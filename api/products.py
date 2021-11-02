from flask import jsonify, request as req, Response
import math, os, re
from werkzeug.utils import secure_filename

import lib.exceptions as exceptions
import api.pictures as pictures

# Using compiled version of regex for readability and (insignificant)
# performance boost
REGEX_MD5 = re.compile(r"^[0-9a-f]{32}$")

def validate_post_data(form_data, upload_folder):
    pic_path = None
    try:
        prod_name = form_data["prodName"]
        if len(prod_name) == 0:
            raise ValueError("Name must be non-empty string")

        prod_price = math.floor(float(form_data["prodPrice"]) * 100)
        prod_instock = int(form_data["prodInStock"])

        # Not mandatory fields
        prod_descr = form_data.get("prodDescr", None)
        pic_name = form_data.get("picName", None)
        pic_md5 = form_data.get("md5", None)

        # However, if it is given, it must be valid
        # Sanitize to avoid an attack with something like picName = "../../../home"
        if pic_name:
            pic_basename = os.path.basename(pic_name)
            pic_path = os.path.join(
                    upload_folder,
                    pic_basename
            )
            if not os.path.isfile(pic_path):
                raise exceptions.BadRequest("File does not exist.")

        if (pic_name and not pic_md5) or (not pic_name and pic_md5):
            # If one of them is present, the other must be as well
            raise exceptions.BadRequest("File name for picture and MD5 hash must be provided together.")

       
        if pic_md5 and not REGEX_MD5.search(pic_md5):
            raise exceptions.BadRequest("Field 'MD5 hash' has invalid value.")

        return prod_name, prod_descr, prod_price, prod_instock, pic_path, pic_md5

    except (KeyError, ValueError, exceptions.BadRequest) as orig_exc:
        # A required field is not present, cannot be cast into required
        # type, or supplied file name is invalid
        try:
            os.remove(pic_path)

        except (FileNotFoundError, TypeError):
            # picName is None or does not correspond to a file in disk
            # This "except" doesn't do anything, I just thought I should
            # consider this situation
            pass

        # We raise another exception here, to be caught by main function
        exceptions.printerr(orig_exc)
        raise exceptions.BadRequest from orig_exc

def validate_patch_data(form_data):
    # Without a picture, this should be much easier
    try:
        prod_id = form_data["prodId"]
        prod_name = form_data["prodName"]
        if len(prod_name) == 0:
            raise ValueError("Name must be non-empty string")

        prod_price = math.floor(float(form_data["prodPrice"]) * 100)
        prod_instock = int(form_data["prodInStock"])

        # Not mandatory fields
        prod_descr = form_data.get("prodDescr", None)

        return prod_id, prod_name, prod_descr, prod_price, prod_instock

    except (KeyError, ValueError) as orig_exc:
        # A required field is not present, cannot be cast into required type
        exceptions.printerr(orig_exc)
        raise exceptions.BadRequest from orig_exc

def delete_product(db, id):
    # This is a function called by delete_product_single and selete_product_all
    try:
        result = db.query("""
            DELETE
            FROM products
            WHERE prod_id = %s::bigint
            RETURNING pic_id ; """,
            args = (id,) )

        if not result.row_count:
            raise exceptions.BadRequest("Product did not exist")

        pic_id = result.single()

    except Exception as err:
        raise exceptions.InternalServerError

    if pic_id:
        pictures.decrease_picture_count(db, pic_id)

    return pic_id

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
            return exceptions.BadRequest.response()

        try:
            result = db.query("""
                SELECT * FROM products
                OFFSET %s
                LIMIT %s ;""",
                (offset, PRODUCTS_PER_PAGE))
            return jsonify(result.json())
        except Exception as err:
            exceptions.printerr(err)
            return exceptions.InternalServerError.response()
        

    @app.get("/products/count")
    def get_products_count():
        try:
            result = db.query("SELECT COUNT(*) FROM products;")
            return jsonify(result.json()[0]["count"])
        except:
            return exceptions.InternalServerError.response()

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
                return exceptions.NotFound.response()
        except:
            return exceptions.InternalServerError.response()

    @app.post("/products")
    def post_product():
        # Picture was already saved in database and in filesystem
        # If anything goes wrong below, we will need to remove it

        form_data = req.get_json()

        # We will do some casts and assert values are within what we expect,
        # but the DB also enforces these constraints. So it is just an extra
        # layer of security

        try:
            prod_name, prod_descr, prod_price, prod_instock, pic_path, pic_md5 = \
                    validate_post_data(form_data, app.config["UPLOAD_FOLDER"])
        except exceptions.BadRequest as err:
            exceptions.printerr(err)
            return err.response()

        # Save picture to database (thus far, it was only in disk)
        pic_id = None
        if pic_path:
            try:
                pic_id = db.query("""
                    SELECT *
                    FROM fn_pic_upsert
                    (
                        %s::text,
                        %s::text
                    ) ;
                """, (pic_path, pic_md5) ).single()
                
            except Exception as err:
                os.remove(pic_path)
                exceptions.printerr(err)
                return exceptions.InternalServerError.response()

        # We already asserted above that values were plausible. If we have an
        # exception now, it is now user's fault, it is an unforeseen error in
        # the server side

        try:
            result = db.query("""
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
                args = ( prod_name, prod_descr, pic_id, prod_price, prod_instock )
            )

            return jsonify({
                "success": True,
                "picId": pic_id,
                "prodId": result.json()[0]["prod_id"]
                })
        
        except Exception as err:
            exceptions.printerr(err)
            if pic_path:
                print("We will also need to decrease file count")
                try:
                    pictures.decrease_picture_count(db, pic_id)
                except:
                    return exceptions.InternalServerError.response()
            
            return exceptions.InternalServerError.response()         

    @app.delete("/products/all")
    def delete_products_all():
        try:
            result = db.query("""
                SELECT prod_id
                FROM products; """).json()

            deleted_pics = 0
            for row in result:
                prod_id = row["prod_id"]
                deleted_pics += bool(delete_product(db, prod_id))

            return jsonify({ "deletedPics" : deleted_pics })

        except Exception as err:
            exceptions.printerr(err)
            return exceptions.InternalServerError.response()

    @app.delete("/products/<int:id>")
    def delete_product_single(id):
        try:
            pic_id = delete_product(db, id)
            return jsonify({ "picId" : pic_id })
        except exceptions.BadRequest as err:
            return err.response()
        except exceptions.InternalServerError as err:
            exceptions.printerr(err)
            return err.response()
        
    @app.patch("/products/<int:id>")
    def patch_product(id):
        print(req.get_json())
        try:
            prod_id, prod_name, prod_descr, prod_price, prod_instock = \
                validate_patch_data(req.get_json())
        except exceptions.BadRequest as err:
            return err.response()
        
        try:
            db.query("""
                UPDATE products
                SET
                    prod_name = %s::text,
                    prod_descr = %s::text,
                    prod_price = %s::bigint,
                    prod_instock = %s::bigint
                WHERE
                    prod_id = %s::bigint ;
            """,
            args = (prod_name, prod_descr, prod_price, prod_instock, prod_id) )
            return ""
        except Exception as err:
            exceptions.printerr(err)
            return exceptions.InternalServerError.response()
        
