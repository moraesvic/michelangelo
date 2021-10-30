import os, random, time, math

# We will need to import this, as native support to "list of integers" kind
# of type hinting was only added in Python3.9
# https://stackoverflow.com/questions/24853923/type-hinting-a-collection-of-a-specified-type
# https://stackoverflow.com/questions/40181344/how-to-annotate-types-of-multiple-return-values
from typing import List, Tuple

from werkzeug.datastructures import FileStorage

# File max size, given in bytes (5 MB)
# This is just a suggestion, client applications can use their own parameters,
# perhaps by accessing app.config["MAX_CONTENT_LENGTH"]
FILE_MAX_SIZE = 5 * 1024 * 1024

# Range of random values to name a file
NEW_NAME_MAX_RND = 10 ** 9

def get_new_name() -> str:
    # Unix allows up to 255 characters in file names.
    # We will use 24 digits for a unique name and allow
    # a large margin

    # Get milliseconds since Unix epoch
    seconds = str(int(time.time() * 1000))

    # What if two files are uploaded in the same millisecond ?
    # Now seems unlikely, but if there are many requests, it will
    # probably happen at some point. So we generate a random number
    # between 0 and 1 billion and append it to the name

    random_number_length = round(math.log10(NEW_NAME_MAX_RND))
    random_number = str(
        random.randint(0, NEW_NAME_MAX_RND - 1)).zfill(random_number_length)

    return f"{seconds}-{random_number}"

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

    if max_size == 0 or check_size_before_saving:
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

def get_mime_type(path: str) -> Tuple[str, str]:
    """
    Returns (type, subtype)
    """
    pass

def test_mime_type(path: str, accepted_types: List[str]) -> bool:
    pass

def rename_mime_type(path: str) -> str:
    pass
    
def get_md5_hash(path: str) -> str:
    pass
    
