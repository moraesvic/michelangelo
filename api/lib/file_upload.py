import os
from werkzeug.datastructures import FileStorage

from .file_utils import get_new_name

# File max size, given in bytes (5 MB)
# This is just a suggestion, client applications can use their own parameters,
# perhaps by accessing app.config["MAX_CONTENT_LENGTH"]
FILE_MAX_SIZE = 5 * 1024 * 1024

def save_file(
            file_storage: FileStorage,
            upload_path: str,
            max_size: int = FILE_MAX_SIZE,
            check_size_before_saving: bool = False) -> str:
    """
    Returns path to saved file or raise an exception.

    If max_size is zero, file will get saved to disk right away, without
    checking how big it is. Use this setting if you are already using middleware
    that prevents the program from receiving a too big file.
    
    If max_size is non-zero and check_size_before_saving is True, we will seek
    file end as a stream before saving it to disk

    https://werkzeug.palletsprojects.com/en/2.0.x/datastructures/#werkzeug.datastructures.FileStorage
    https://stackoverflow.com/questions/15772975/flask-get-the-size-of-request-files-object
    """
    new_name = get_new_name()

    if not os.path.isdir(upload_path):
        raise Exception("Given upload path does not exist!")
    
    new_path = os.path.join(upload_path, new_name)

    # Unix paths (with filename and extension) can go up to 4096 characters.
    # As usual, we want to leave a fat margin and not have any problems

    if len(new_path) > 2048:
        raise Exception("File path is too long!")

    # Flask will already check if the payload exceeds the maximum size
    # given by app.conf["MAX_CONTENT_LENGTH"] . But, as this module is
    # supposed to serve as an independent piece of software, usable by other
    # frameworks, we will check file size again.

    if check_size_before_saving:
        file_storage.seek(0, os.SEEK_END)
        file_size = file_storage.tell()
    else:
        file_storage.save(new_path)
        file_size = os.path.getsize(new_path)
    
    if max_size != 0 and file_size > max_size:
        if not check_size_before_saving:
            os.remove(new_path)
        raise Exception("File is too large!")

    elif check_size_before_saving:
        # Now we need to rewind the file...
        file_storage.seek(0, 0)
        file_storage.save(new_path)

    # If everything went well, we return path to saved file
    return new_path
