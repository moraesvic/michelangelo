import subprocess, re, math, os
from typing import Tuple

import lib.file_utils as file_utils

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

    if max_size == 0:
        raise Exception("Maximum size cannot be zero!")

    biggest = max(resolution[0], resolution[1])
    factor = 1.0 if biggest <= max_size else max_size / biggest

    return math.floor(factor * 100.0)

def resize(
            path: str,
            max_size: int,
            print_stats: bool = False) -> None:
    resolution = get_pic_resolution(path)
    proportion = calculate_proportion(resolution, max_size)
    
    if not file_utils.test_mime_type(path, ["image"]):
        raise Exception("Cannot resize file, it is not a picture")

    new_basename = f"{file_utils.get_new_name()}"
    new_path = os.path.join(os.path.dirname(path), new_basename)

    arg = f"convert -resize {proportion}% \"{path}\" \"{new_path}\""

    try:
        subprocess.check_output(
            arg,
            shell = True,
            stderr = subprocess.DEVNULL
        )
    except:
        raise Exception("An error occurred while resizing file")
    
    file_utils.compare_size_apply_changes(
        path,
        new_path,
        print_stats,
        "resizing"
    )



def convert(
        path: str,
        new_type: str = "jpeg",
        print_stats: bool = False) -> None:
    """
    Picture is overwritten!
    """
    file_type, file_subtype = file_utils.get_mime_type(path)

    if file_type != "image":
        raise Exception("Cannot convert file, it is not a picture")
    
    if file_subtype == new_type:
        # Nothing to do, file is already in the desired format
        if print_stats:
            print("File is already in desired format, nothing to do!")
        return

    # Name is only temporary, picture will be overwritten
    # Let's use a random name, we do not want to overwrite another
    # file on the same directory by mistake
    new_basename = f"{file_utils.get_new_name()}.{new_type}"
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

    file_utils.compare_size_apply_changes(
        path,
        new_path,
        print_stats,
        "converting"
    )

def get_ncc(
            path1: str,
            path2: str,
            only_same_resolution: bool = True):
    # NCC, or Normalized Cross Correlation, is a metric to determine to what
    # extent two images are similar

    if not (file_utils.test_mime_type(path1, ["image"])
        and file_utils.test_mime_type(path2, ["image"])):
        raise Exception("Cannot compare file, it is not a picture")

    if only_same_resolution:
        resolution_1 = get_pic_resolution(path1)
        resolution_2 = get_pic_resolution(path2)

        if resolution_1 != resolution_2:
            raise Exception("Images do not have same resolution")

    # Third argument is usually a destination for delta image, but we are
    # not going to use this
    arg = f"compare -metric NCC \"{path1}\" \"{path2}\" /dev/null 2>&1"
    ncc = None

    try:
        # "compare" returns error code if images are not 100% identical, so
        # we cannot use check_output and have to resort to the lower level
        # subprocess.run
        ncc = float(subprocess.run(
            arg,
            shell = True,
            check = False,
            capture_output = True,
            text = True
        ).stdout)
    except subprocess.CalledProcessError as err:
        print(f"error was: {err}")
        print(f"return code: {err.returncode}")
        print(f"output: {err.output}")
        raise Exception("An error occurred while comparing files")

    return ncc

def is_identical(
            path1: str,
            path2: str,
            min_ncc: float = 0.99,
            print_stat: bool = False):
    # Checks if two images are identical by comparing their NCC (Normalized
    # Cross Correlation). Default value for testing is, images must have at
    # least 99% correlation
    try:
        ncc = get_ncc(path1, path2)
        if print_stat:
            print(f"images are {ncc * 100:.4f}% similar")
        return ncc > min_ncc
    except Exception as err:
        print(f"An error occurred: {err}")
        return False