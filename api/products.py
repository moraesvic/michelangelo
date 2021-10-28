
class Products:
    def __init__(self, app):
        @app.get("/list-products")
        def get_list_products():
            return "list-products"

        @app.get("/products/count")
        def get_products_count():
            return "products/count"

        @app.get("/products/<int:id>")
        def get_product_by_id(id):
            return str(id)

        @app.post("/products")
        def post_product():
            pass

        @app.delete("/products/all")
        def delete_products_all():
            pass

