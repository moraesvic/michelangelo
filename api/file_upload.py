import os, random, time

# File max size, given in bytes (5 MB)
# This is just a suggestion, client applications can use their own parameters,
# perhaps by accessing app.config["MAX_CONTENT_LENGTH"]
FILE_MAX_SIZE = 5 * 1024 * 1024

# Check if it is a file:
# os.path.isfile(file)

# Check file size
# os.path.getsize(path)

def get_new_name():
    # Unix allows up to 255 characters in file names.
    # We will use 24 digits for a unique name and allow
    # a large margin

    # Get milliseconds since Unix epoch
    seconds = str(int(time.time() * 1000))

    # What if two files are uploaded in the same millisecond ?
    # Now seems unlikely, but if there are many requests, it will
    # probably happen at some point. So we generate a random number
    # between 0 and 1 billion and append it to the name
    random_number = f"{random.randint(0, 10**9 - 1):09}"

    return f"{seconds}-{random_number}"


def save_file(file_storage, upload_path, max_size = FILE_MAX_SIZE):
    """
    file_storage is a werkzeug.datastructures.FileStorage object

    https://werkzeug.palletsprojects.com/en/2.0.x/datastructures/#werkzeug.datastructures.FileStorage
    """
    new_name = get_new_name()

    if not os.path.isdir(upload_path):
        raise Exception("Given upload path does not exist!")
    
    new_path = os.path.join(upload_path, new_name)

    # Unix paths (with filename and extension) can go up to 4096 characters.
    # As usual, we want to leave a fat margin and not have any problems

    if len(new_path) > 2048:
        raise Exception("File path is too long!")

    file_storage.save(new_path) 

    # Flask will already check if the payload exceeds the maximum size
    # given by app.conf["MAX_CONTENT_LENGTH"] . But, as this module is
    # supposed to serve as an independent piece of software, usable by other
    # frameworks, we will check file size again.

    file_size = os.path.getsize(new_path)
    if file_size > max_size:
        # remove file
        raise Exception("File is too large!")

    # If everything went well, we return path to saved file
    return new_path

def get_mime_type(path):
    pass

def test_mime_type(path):
    pass

def rename_mime_type(path):
    pass
    
def get_md5_hash(path):
    pass
    
    
# pic_file.save(os.path.join(upload_folder, filename))

for i in range(10):
    save_file(None, None)
    time.sleep(random.random() * 0.1)