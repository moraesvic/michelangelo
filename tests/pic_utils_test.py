import unittest, subprocess, shutil

from lib.pic_utils import *
import lib.file_utils as file_utils
from tests.test_common import *

class FileUploadTest(unittest.TestCase):

    # Let's say we overwrite a file. We need to backup the original version to
    # restore to disk later. Format is Tuple[path_to_restore, path_of_backup]

    files_to_revert = []

    def bkp_file(self, path):
        bkp_name = file_utils.get_new_name()
        bkp_path = os.path.join(os.path.dirname(path), bkp_name)
        shutil.copyfile(path, bkp_path)
        self.files_to_revert.append( (path, bkp_path) )

    def tearDown(self):
        if VERBOSE:
            print("Printing contents of test directory before cleaning up")
            print("***")

            test_files_path = rel_path("test_files")
            print(subprocess.check_output(
                f"find {test_files_path} -maxdepth 1 -type f -exec md5sum {{}} +",
                shell = True,
                text = True
                ))

            print("***")

        printv("Restoring overwritten files")
        for file in self.files_to_revert:
            os.rename(file[1], file[0])

        self.files_to_revert.clear()

    # Now, we have a problem. Compression and resizing algorithms are NOT
    # deterministic. This means that every time we run the command, the output
    # could vary slightly. Besides that, metadata could be changed while image
    # data remains identical. Last but not least, somebody could be running
    # a different version of ImageMagick, or a different dependency for 
    # ImageMagick, who knows.
    # 
    # A MD5 hash is NOT appropriate for checking if the conversion was 
    # correctly done.
    #
    # We will need to use ImageMagick's compare. As a metric, we will use "NCC"
    # (Normalized Cross Correlation), and define that two images are identical
    # if they have NCC > 99% (this is actually very forgiving, probably any
    # human would be able to tell they are different at this point — maybe
    # 99.9% would be better).
    #
    # It is not really obvious what these metrics mean and what kind of
    # tolerance should be expected, so I had to run some tests:
    # https://github.com/moraesvic/img_compare
    #
    # https://stackoverflow.com/questions/6380818/imagemagick-making-different-images-on-windows-and-linux
    # https://askubuntu.com/questions/209517/does-diff-exist-for-images

    def test_convert(self):
        file_path = rel_path("test_files/bears_png.png")

        # First we need to guarantee that we are indeed opening the correct file
        orig_size = os.path.getsize(file_path)
        orig_md5 = file_utils.get_md5_hash(file_path)
        expected_orig_size = 3247071
        expected_orig_md5 = "aa213b5bcce4b945c600968d37129d78"
        if orig_size != expected_orig_size or orig_md5 != expected_orig_md5:
            raise Exception("Wrong file was supplied!")

        self.bkp_file(file_path)
        convert(file_path, print_stats = VERBOSE)

        reference_file = rel_path("test_files/converted.jpg")
        self.assertTrue(
            is_identical(file_path, reference_file, print_stat = VERBOSE)
        )

    def test_convert_not_a_pic(self):
        file_path = rel_path("test_files/normal_file.txt")
        with self.assertRaisesRegex(Exception, "Cannot convert file, it is not a picture"):
            convert(file_path, print_stats = VERBOSE)

    def test_convert_nothing_to_do(self):
        file_path = rel_path("test_files/bears.jpg")
        orig_md5 = file_utils.get_md5_hash(file_path)
        convert(file_path, print_stats = VERBOSE)
        new_md5 = file_utils.get_md5_hash(file_path)
        self.assertEqual(orig_md5, new_md5)

    def test_calculate_proportion(self):
        # Normal resizing
        proportion_1 = calculate_proportion( (100, 200) , 100)
        expected_1 = 50
        self.assertEqual(proportion_1, expected_1)

        # Nothing to do, max_size is equal to desired
        proportion_2 = calculate_proportion( (100, 200) , 200)
        expected_2 = 100
        self.assertEqual(proportion_2, expected_2)

        # Nothing to do, max_size is greater than desired
        proportion_3 = calculate_proportion( (100, 200) , 400)
        expected_3 = 100
        self.assertEqual(proportion_3, expected_3)

        # One test with floating numbers
        proportion_4 = calculate_proportion( (1698, 1131) , 800)
        expected_4 = 47
        self.assertEqual(proportion_4, expected_4)

        # Bad input
        with self.assertRaisesRegex(Exception, "Maximum size cannot be zero!"):
            calculate_proportion( (100, 200) , 0)

    def test_get_pic_resolution(self):
        path_1 = rel_path("test_files/bears.jpg")
        resolution_1 = get_pic_resolution(path_1)
        expected_resolution_1 = (1698, 1131)
        self.assertTupleEqual(resolution_1, expected_resolution_1)

        path_2 = rel_path("test_files/logo.png")
        resolution_2 = get_pic_resolution(path_2)
        expected_resolution_2 = (120, 90)
        self.assertTupleEqual(resolution_2, expected_resolution_2)

    def test_strip_pic_metadata(self):
        file_path = rel_path("test_files/bears.jpg")
        # Check that we are opening correct file
        expected_orig_md5 = "569a1c98696050439b5b2a1ecfa52d19"
        if file_utils.get_md5_hash(file_path) != expected_orig_md5:
            raise Exception("Wrong file was supplied!")

        self.bkp_file(file_path)
        strip_pic_metadata(file_path)

        stripped_md5 = file_utils.get_md5_hash(file_path)
        expected_stripped_md5 = "62767fb1f702c10b6dfdac672416dddd"
        self.assertEqual(stripped_md5, expected_stripped_md5)

    def test_resize(self):
        path_jpg = rel_path("test_files/bears.jpg")
        path_png = rel_path("test_files/bears_png.png")

        # Check if we have the right files
        md5_jpg = file_utils.get_md5_hash(path_jpg)
        md5_png = file_utils.get_md5_hash(path_png)
        expected_orig_md5_jpg = "569a1c98696050439b5b2a1ecfa52d19"
        expected_orig_md5_png = "aa213b5bcce4b945c600968d37129d78"

        if md5_jpg != expected_orig_md5_jpg or md5_png != expected_orig_md5_png:
            raise Exception("Wrong file was supplied!")

        self.bkp_file(path_jpg)
        self.bkp_file(path_png)
        resize(path_jpg, 800, print_stats = VERBOSE)
        resize(path_png, 800, print_stats = VERBOSE)

        # These files resulted from the command:
        # "convert -resize 47% ORIGINAL RESIZED"
        # Value of 47% was calculated above (test_calculate_proportion)
        # and has as goal resizing to less or equal than 800 pixels
        
        reference_file_jpg = rel_path("test_files/jpg_resize.jpg")
        reference_file_png = rel_path("test_files/png_resize.png")
        self.assertTrue(
            is_identical(path_jpg, reference_file_jpg, print_stat = VERBOSE)
        )
        self.assertTrue(
            is_identical(path_png, reference_file_png, print_stat = VERBOSE)
        )
        

if __name__ == "__main__":
    unittest.main()