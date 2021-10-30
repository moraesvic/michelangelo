import time, os, re, subprocess, math, random
from typing import Tuple, List


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

    # In the future, it might be interesting to replace this with
    # secrets.token_hex(4)
    # 4 bytes already generate a bit over 4 billion possibilities,
    # with a shorter filename, and more secure entropy source
    # https://docs.python.org/3/library/secrets.html

    random_number_length = round(math.log10(NEW_NAME_MAX_RND))
    random_number = str(
        random.randint(0, NEW_NAME_MAX_RND - 1)).zfill(random_number_length)

    return f"{seconds}-{random_number}"


def get_mime_type(path: str) -> Tuple[str, str]:
    """
    Returns (type, subtype)
    """

    # Python has libraries for checking mimetype, but this solution was already
    # tested and proven in another project I did using Node.js
    #
    # Besides, "file" is a utility that comes with every Linux installation, so
    # we can have one less dependency for our project
    #
    # For future reference:
    # https://stackoverflow.com/questions/43580/how-to-find-the-mime-type-of-a-file-in-python

    arg = f"file --mime-type \"{path}\""
    output = subprocess.check_output(
        arg,
        shell = True,
        text = True,
        stderr = subprocess.DEVNULL
    )
    groups = re.search(r"^.+?: (\w+)/(\w+)", output).groups()
    return groups[0], groups[1]

def test_mime_type(path: str, accepted_types: List[str]) -> bool:
    """
    Tests whether the given file's mimetype is in the accepted_types
    """
    try:
        file_type, _ = get_mime_type(path)
        return file_type in accepted_types
    except:
        return False

def rename_mime_type(path: str, subtype: str = None) -> str:
    """
    Renames the file according to its mime subtype
    """
    # Please note that text files will not be renamed as file.txt, but as
    # file.plain . This makes this function limited, in this case, but
    # for image files it works perfectly

    if subtype:
        file_subtype = subtype
    else:
        _, file_subtype = get_mime_type(path)

    # We do not want something like file.png.png, so we have to check if
    # file already has the extension
    regex = re.compile(rf"^.+?\.({file_subtype})$", re.IGNORECASE)
    basename = os.path.basename(path)

    if not regex.search(basename):
        new_path = f"{path}.{file_subtype}"
        os.rename(path, new_path)
    else:
        new_path = path

    return new_path
    
def test_and_rename_mime_type(path: str, accepted_types: List[str]) -> str:
    """
    If file's mimetype is among the accepted_types, then we renamed it.
    If it is not, raises an exception
    """
    file_type, file_subtype = get_mime_type(path)
    if file_type not in accepted_types:
        raise Exception("File is not in the accepted types!")

    new_path = rename_mime_type(path, subtype = file_subtype)
    return new_path

def get_md5_hash(path: str) -> str:
    """
    Returns MD5 hash for file.
    """
    # See note on "get_meme_type" on why we are doing this from command line
    # instead of a library
    arg = f"md5sum \"{path}\""

    try:
        output = subprocess.check_output(
            arg,
            shell = True,
            text = True,
            stderr = subprocess.DEVNULL
        )
    except subprocess.CalledProcessError:
        raise Exception("Failed to calculate MD5 hash for file!")

    regex = re.compile(r"^([0-9a-f]{32}).*$")
    match = regex.search(output)

    if not match:
        raise Exception("Failed to calculate MD5 hash for file!")

    return match.groups()[0]
