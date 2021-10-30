import subprocess, re, math, os, secrets
from typing import Tuple

from .file_utils import get_mime_type, test_mime_type

def strip_pic_metadata(path: str) -> None:
    arg = f"exiftool -overwrite_original -all= \"{path}\""
    try:
        subprocess.check_output(
            arg,
            shell = True,
            stderr = subprocess.DEVNULL
        )
    except:
        raise Exception("exiftool emitted an error!")

def get_pic_resolution(path: str) -> Tuple[int, int]:
    arg = f"""
    exiftool "{path}" | \
	sed -rn "s/^Image Size[^0-9]*([0-9]+x[0-9]+)$/\\1/p"
    """
    resolution = subprocess.check_output(
            arg,
            shell = True,
            text = True,
            stderr = subprocess.DEVNULL
        )
    regex = re.compile(r"([0-9]+)x([0-9]+)")
    match = regex.search(resolution)

    if not match:
        raise Exception("Could not get resolution from exiftool's output")
    
    return int(match.groups()[0]), int(match.groups()[1])

def calculate_proportion(resolution: Tuple[int, int], max_size: int) -> int:
    """
    Receives tuple with picture resolution and outputs what factor
    (as a percentage) must be used in order to make maximal dimension
    equal to max_size
    """

    biggest = max(resolution[0], resolution[1])
    factor = 1.0 if biggest <= max_size else max_size / biggest

    return math.floor(factor * 100.0)

def resize(path: str, max_size: int) -> None:
    resolution = get_pic_resolution(path)
    proportion = calculate_proportion(resolution, max_size)
    
    if not test_mime_type(path, ["image"]):
        raise Exception("Cannot resize file, it is not a picture")
    
    #
    # ...
    #

def compare_size_apply_changes(old_path: str, new_path: str) -> str:
    pass

def convert(path: str, new_type: str = "jpeg") -> None:
    """
    Picture is overwritten!
    """
    file_type, file_subtype = get_mime_type(path)

    if file_type != "image":
        raise Exception("Cannot convert file, it is not a picture")
    
    if file_subtype == new_type:
        # Nothing to do, file is already in the desired format
        return
    
    # We need to save original size, to be able to compare later
    # and see if the operation in fact reduced picture size
    old_size = os.path.get_size(path)

    # Name is only temporary, picture will be overwritten
    # Let's add a random suffix, we do not want to overwrite another
    # file on the same directory by mistake
    random_suffix = secrets.token_hex(4)
    new_path = f"{path}-{random_suffix}.{new_type}"
    arg = f"convert \"{path}\" \"{new_path}\""

    try:
        subprocess.check_output(
            arg,
            shell = True,
            stderr = subprocess.DEVNULL
        )
    except:
        raise Exception("An error occurred while converting file")

    new_size = os.path.getsize(new_path)

    if new_size < old_size:
        # Good, let's overwrite original
        # ...
        pass
    else:
        # The intention was to reduce file size... we need to revert
        # what we did
        # ...
        pass



print(
    calculate_proportion(
        get_pic_resolution("../../tests/test_files/logo.png"),
        1999
    )
)

