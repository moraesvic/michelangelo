import time, os, re, subprocess, math, random, secrets
from typing import Tuple, List

# Range of random values to name a file
N_RANDOM_BYTES = 4

def get_new_name() -> str:
    # Unix allows up to 255 characters in file names.
    # We will use 24 digits for a unique name and allow
    # a large margin

    # Get milliseconds since Unix epoch
    seconds = str(int(time.time() * 1000))

    # What if two files are uploaded in the same millisecond ?
    # Now seems unlikely, but if there are many requests, it will
    # probably happen at some point. So we generate a random number
    # and append it to the name

    # 4 bytes already generate a bit over 4 billion possibilities,
    # with a shorter filename, and more secure entropy source
    # https://docs.python.org/3/library/secrets.html

    random_token = secrets.token_hex(N_RANDOM_BYTES)

    return f"{seconds}-{random_token}"


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

    return append_extension(path, file_subtype)
    
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

    print(f"output was {output}")

    if not match:
        raise Exception("Failed to calculate MD5 hash for file!")

    return match.groups()[0]


def append_extension(path: str, extension: str) -> str:
    """
    Renames file, appending extension to it, but only if it hasn't already
    got the extension
    """

    # We do not want something like file.png.png, so we have to check if
    # file already has the extension

    regex = re.compile(rf"^.+?\.({extension})$", re.IGNORECASE)
    basename = os.path.basename(path)

    if not regex.search(basename):
        new_path = f"{path}.{extension}"
        os.rename(path, new_path)
    else:
        new_path = path

    return new_path

def compare_size_apply_changes(
        old_path: str,
        new_path: str,
        print_stats: bool = False,
        operation_name: str = ""):
    """
    Receives two paths, old_path represents the original file and
    new_path the file after an operation (converting, resizing, 
    compressing, etc.)

    Checks if such operation indeed reduced file size, and apply changes
    or reverts operation (leaves original file)

    operation_name is an optional argument, which can be used for
    debugging and benchmarking
    """
    old_size = os.path.getsize(old_path)
    new_size = os.path.getsize(new_path)

    if print_stats:
        diff = old_size - new_size
        percentage = diff / old_size * 100.0
        verb = "reduced" if diff > 0 else "increased"
        if len(operation_name):
            print(f"operation {operation_name}")
        print(f"old_path = {old_path}")
        print(f"new_path = {new_path}")
        print(f"File {verb} in {abs(diff)} bytes ({percentage:.2f}%)")

    if old_size <= new_size:
        if print_stats:
            print("Operation was not effective. Reverting.")
        os.remove(new_path)
    else:
        if print_stats:
            print("Operation was successful. Applying changes.")
        os.rename(new_path, old_path)