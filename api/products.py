from flask import jsonify, request as req, Response
import math
from werkzeug.utils import secure_filename

def Products(
        app,
        db):

    @app.get("/list-products")
    def get_list_products():
        # This number is defined here and in the front-end
        # Perhaps in the future I will create some environment variable
        # to merge both
        PRODUCTS_PER_PAGE = 8

        # If the query parameter is not defined, then req.args.get returns 
        # None and trying to cast into integer gives TypeError. We will use
        # 0 as a default value
        # 
        # If it is a random string not corresponding to a number,
        # it will yield ValueError and return status 400
        try:
            offset = PRODUCTS_PER_PAGE * int(req.args.get("page"))
        except TypeError:
            offset = 0
        except ValueError:
            return Response("Bad request", status = 400)

        try:
            result = db.query("""
                SELECT * FROM products
                OFFSET %s
                LIMIT %s ;""",
                (offset, PRODUCTS_PER_PAGE))
            return jsonify(result.json())
        except:
            return Response("Internal server error", status = 500)
        

    @app.get("/products/count")
    def get_products_count():
        try:
            result = db.query("SELECT COUNT(*) FROM products;")
            return jsonify(result.json()[0]["count"])
        except:
            return Response("Internal server error", status = 500)

    @app.get("/products/<int:id>")
    def get_product_by_id(id):
        try:
            result = db.query("""
            SELECT * FROM products
            WHERE prod_id = %s
            LIMIT 1 ; """, (id,) )
            if len(result.rows):
                return jsonify(result.json()[0])
            else:
                return Response("Not found", status = 404)
        except:
            return Response("Internal server error", status = 500)

    @app.post("/products")
    def post_product():
        # It is a bit tricky to handle files and multipart encoding
        # If in doubt, check documentation:
        # https://flask.palletsprojects.com/en/2.0.x/patterns/fileuploads/
        
        pic_id = None
        pic_file = req.files.get("picture")
        if pic_file and len(pic_file.filename):
            print(pic_file)
            print(type(pic_file))
            upload_folder = app.config["UPLOAD_FOLDER"]
            filename = secure_filename(pic_file.filename)
            # pic_file.save(os.path.join(upload_folder, filename))
            # ... process picture and attribute pic_id ...

        # Picture was already saved in database and in filesystem
        # If anything goes wrong below, we will need to remove it

        form_data = dict(req.form)
        # We will do some casts and assert values are within what we expect,
        # but the DB also enforces these constraints. So it is just an extra
        # layer of security
        try:
            prod_name = form_data["prodName"]
            if len(prod_name) == 0:
                raise ValueError("Name must be non-empty string")
            prod_descr = form_data["prodDescr"]
            prod_price = math.floor(float(form_data["prodPrice"]) * 100)
            prod_instock = int(form_data["prodInStock"])

        except (KeyError, ValueError):
            # ... remove picture ... #
            return Response("Bad request", status = 400)

        # We already asserted above that values were plausible. If we have an
        # exception now, it is now user's fault, it is an unforeseen error in
        # the server side
        try:
            db.query("""
                INSERT INTO products
                (
                    prod_name,
                    prod_descr,
                    pic_id,
                    prod_price,
                    prod_instock
                )
                VALUES
                (
                    %s::text,
                    %s::text,
                    %s::bigint,
                    %s::bigint,
                    %s::bigint
                ) RETURNING * ; """,
                ( prod_name, prod_descr, pic_id, prod_price, prod_instock )
            )

            return jsonify({"success": True, "picId": pic_id})
        
        except Exception as e:
            # ... remove picture ... #
            print(f"An unexpected error happened when inserting product in database: {str(e)}")
            return Response("Internal server error", status = 500)           

    @app.delete("/products/all")
    def delete_products_all():
        try:
            result = db.query("""
                SELECT prod_id, prod_img
                FROM products; """).json()

            pics_set = set()
            for row in result:
                pic_id = row["prod_img"]
                if pic_id:
                    pics_set.add(pic_id)

            for pic in pics_set:
                # delete picture
                pass

            result_del_pics = db.query("""
                DELETE FROM pics
                RETURNING pic_id ; """)

            deleted_pics = len(pics_set) + len(result_del_pics.rows)
            deleted_prods = len(result)

            return f"Success. We deleted {deleted_pics} pics and {deleted_prods} products"

        except:
            return Response("Internal server error", status = 500)

        

