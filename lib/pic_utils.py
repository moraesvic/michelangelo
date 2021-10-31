import subprocess, re, math, os
from typing import Tuple

from .file_utils import get_mime_type, test_mime_type, \
    compare_size_apply_changes, get_new_name

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

    # Name is only temporary, picture will be overwritten
    # Let's use a random name, we do not want to overwrite another
    # file on the same directory by mistake
    new_basename = f"{get_new_name()}.{new_type}"
    new_path = os.path.join(os.path.dirname(path), new_basename)
    arg = f"convert \"{path}\" \"{new_path}\""

    try:
        subprocess.check_output(
            arg,
            shell = True,
            stderr = subprocess.DEVNULL
        )
    except:
        raise Exception("An error occurred while converting file")

    compare_size_apply_changes(
        path,
        new_path,
        True,
        "converting"
    )


realpath = os.path.realpath("tests/test_files/bears_alt.png")
print(realpath)
convert(realpath)

