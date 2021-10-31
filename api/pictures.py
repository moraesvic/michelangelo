from flask import request as req, jsonify
import lib.file_upload as file_upload

def Pictures(
        app,
        db,
        prefix):
    
    @app.get(f"{prefix}/pictures/<int:id>")
    def get_picture_by_id(id):
        pass

    @app.delete(f"{prefix}/pictures/all")
    def delete_pictures_all():
        pass

    @app.post(f"{prefix}/pictures")
    def post_picture():
        pic_id = None
        pic_file = req.files.get("picture")
        if pic_file and len(pic_file.filename):
        
            try:
                pic_path = file_upload.save_file(
                    pic_file,
                    upload_path = app.config["UPLOAD_FOLDER"],
                    max_size = app.config["MAX_CONTENT_LENGTH"],
                    check_size_before_saving = True
                )
                return jsonify({"path": pic_path})
            except:
                return jsonify({"error": "error"})
        
        else:
            return jsonify({"error": "you did not send anything :)"})