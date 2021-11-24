from flask import request as req, jsonify, send_file
import os

from lib import file_upload, exceptions

# This belongs here (logically) but gets called by products.py
def decrease_picture_count(db, pic_id):
    try:
        # This will path to the picture if and only if calling the function
        # resulted in reference count dropping to zero

        pic_path = db.query("""
            SELECT *
            FROM fn_pic_decrease_ref_count(%s::int) ;
        """, args = (pic_id,) ).single()
        
        if pic_path:
            os.remove(pic_path)

    except Exception as err:
        exceptions.printerr(err)
        raise

def Pictures(
        app,
        db):
    
    @app.get("/pictures/<int:id>")
    def get_picture_by_id(id):
        try:
            result = db.query("""
                SELECT pic_path
                FROM pics
                WHERE pic_id = %s::bigint 
                LIMIT 1;
            """, args = (id,) )
            if result.row_count:
                return send_file(result.single())
            else:
                return exceptions.NotFound.response()
        except Exception as err:
            exceptions.printerr(err)
            return exceptions.InternalServerError.response()

    @app.delete("/pictures/all")
    def delete_pictures_all():
        try:
            result = db.query("""
                DELETE
                FROM pics
                RETURNING pic_path ;
            """)

            json = result.json()
            for row in json:
                os.remove(row["pic_path"])

            return f"Success! {result.row_count} pictures deleted."

        except Exception as err:
            exceptions.printerr(err)
            return exceptions.InternalServerError.response()

    @app.delete("/pictures/<int:id>")
    def delete_picture(id):
        try:
            path = db.query("""
                DELETE
                FROM pics
                WHERE pic_id = %s::bigint
                RETURNING pic_path ;
            """, (id,) ).single()

            os.remove(path)

            return f"Success! Picture {id} deleted."

        except Exception as err:
            exceptions.printerr(err)
            return exceptions.InternalServerError.response()

    @app.post("/pictures")
    def post_picture():
        # It is a bit tricky to handle files and multipart encoding
        # If in doubt, check documentation:
        # https://flask.palletsprojects.com/en/2.0.x/patterns/fileuploads/

        pic_file = req.files.get("picture")
        if pic_file and len(pic_file.filename):
        
            try:
                pic_path, pic_md5 = file_upload.save_pic(
                    pic_file,
                    upload_path = app.config["UPLOAD_FOLDER"],
                    max_size = app.config["MAX_CONTENT_LENGTH"]
                )

                # Will return pic_ref_count and pic_id
                result = db.query("""
                    SELECT *
                    FROM fn_pic_upsert
                    (
                        %s::text,
                        %s::text
                    ) ;
                """, (pic_path, pic_md5) ).json()[0]

                pic_ref_count = result["pic_ref_count"]

                if pic_ref_count == 1:
                    # This means that the picture was first uploaded for this
                    # product, and has to be updated now

                    # The processing should occur asynchronously, but that will have to
                    # be implemented later
                    pic_path = file_upload.process_pic(pic_path)

                    db.query("""
                        UPDATE pics
                        SET pic_path = %s::text
                        WHERE pic_md5 = %s::text ;
                    """, (pic_path, pic_md5) )
                else:
                    # Picture was already in DB.
                    # Let's delete file
                    os.remove(pic_path)

                json = jsonify({
                    "md5": pic_md5
                })
                return json, 200

            except exceptions.BadRequest as err:
                return err.response()
            except Exception as err:
                exceptions.printerr(err)
                return exceptions.InternalServerError.response()
        
        else:
            # Accessing the route without the required fields / encoding
            return exceptions.BadRequest.response()

    @app.delete("/pictures/orphan")
    def delete_pictures_orphan():
        # This will delete all pictures that do not have an associated product.
        # This can be run periodically to clean database.

        # An alternative for the last part of the query is
        # """
        # WHERE pics.pics_id IN (SELECT * FROM cte)
        # """
        # As far as I tested (not much), they are similar regarding performance.
        # According to this post (https://pt.stackoverflow.com/questions/417582/diferen%C3%A7a-entre-exists-e-in-no-postgres)
        # WHERE ... IN should have better performance, because the SELECT statement
        # is just run once, but in practice they have the same performance, because
        # Postgres is smart enough to optimize it (as seen with command EXPLAIN)

        try:
            result = db.query("""
                WITH cte AS
                (
                    SELECT
                        pics.pic_id AS pic_id
                    FROM pics
                    LEFT JOIN products
                    ON pics.pic_id = products.pic_id
                    WHERE products.prod_id IS NULL 
                )
                DELETE
                FROM pics
                WHERE EXISTS
                (
                    SELECT
                    FROM cte
                    WHERE pic_id = pics.pic_id
                )
                RETURNING pics.pic_path;
            """)
            
            for row in result.rows:
                os.remove(row[0])
            
            return f"Success! {result.row_count} orphan pictures removed."

        except Exception as err:
            exceptions.printerr(err)
            return exceptions.InternalServerError.response()