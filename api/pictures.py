def Pictures(app, db):
    @app.get("/pictures/<int:id>")
    def get_picture_by_id(id):
        pass

    @app.delete("/pictures/all")
    def delete_pictures_all():
        pass

    @app.post("/pictures")
    def post_picture():
        pass