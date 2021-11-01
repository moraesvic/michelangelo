from flask import request as req, jsonify, send_file
import os

import lib.file_upload as file_upload
import lib.exceptions as exceptions

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
        path = db.query("""
            SELECT pic_path
            FROM pics
            WHERE pic_id = %s::bigint 
            LIMIT 1;
        """, args = (id,) ).single()

        return send_file(path)

    @app.delete("/pictures/all")
    def delete_pictures_all():
        pass

    @app.post("/pictures")
    def post_picture():
        # It is a bit tricky to handle files and multipart encoding
        # If in doubt, check documentation:
        # https://flask.palletsprojects.com/en/2.0.x/patterns/fileuploads/

        pic_file = req.files.get("picture")
        if pic_file and len(pic_file.filename):
        
            try:
                pic_path, md5 = file_upload.save_pic(
                    pic_file,
                    upload_path = app.config["UPLOAD_FOLDER"],
                    max_size = app.config["MAX_CONTENT_LENGTH"]
                )
                print(f"pic_path is {pic_path}")
                print(f"md5 is {md5}")
                json = jsonify({
                    "picName": os.path.basename(pic_path),
                    "md5": md5
                })
                print(json)
                return json, 200

            except exceptions.BadRequest as err:
                return err.response()
            except Exception as err:
                exceptions.printerr(err)
                return exceptions.InternalServerError.response()
        
        else:
            # Accessing the route without the required fields / encoding
            return exceptions.BadRequest.response()