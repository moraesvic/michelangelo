import time, re, random, unittest, subprocess

from lib.file_utils import *
from tests.test_common import *

class FileUploadTest(unittest.TestCase):

    # When we are done with tests, we need to close files and remove
    # all files saved to disk

    tmp_files = []

    # Let's say we rename a file A to the name B. We need to keep track
    # of this and then revert these changes in the end

    revert_name = []

    @classmethod
    def tearDownClass(cls):
        if VERBOSE:
            print("Printing contents of test directory before cleaning up")
            print("***")

            test_files_path = rel_path("test_files")
            print(subprocess.check_output(
                f"ls {test_files_path}",
                shell = True,
                text = True
                ))

            print("***")

        printv("Removing temporary files")
        for file in cls.tmp_files:
            os.remove(file)

        printv("Reverting file names")
        for name_pair in cls.revert_name:
            printv(f"renaming {name_pair[0]} to {name_pair[1]}")
            os.rename(name_pair[0], name_pair[1])

    def get_filename_regex(self):
        milliseconds_length = len(str(int(time.time() * 1000)))
        random_number_length = N_RANDOM_BYTES * 2
        return re.compile(r"[0-9]{%d}-[0-9a-f]{%d}" % (
            milliseconds_length, random_number_length))

    def test_get_new_name(self):
        regex = self.get_filename_regex()

        for _ in range(NUMBER_OF_TESTS):
            with self.subTest():
                time.sleep(random.random() * 0.05)
                new_name = get_new_name()
                if self.assertRegex(new_name, regex):
                    printv(f"{new_name} : ok!")

    def test_get_mime_type_img(self):
        return_value = get_mime_type(rel_path("test_files/logo.png"))
        expected = ("image", "png")
        self.assertTupleEqual(return_value, expected)

    def test_get_mime_type_txt(self):
        return_value = get_mime_type(rel_path("test_files/normal_file.txt"))
        expected = ("text", "plain")
        self.assertTupleEqual(return_value, expected)

    def test_get_mime_type_img(self):
        # Here we try to fool the method, by passing an image file
        # with text extension. Doesn't really matter, since Unix does not
        # care about extensions, and "file" util does not take it into
        # consideration

        return_value = get_mime_type(rel_path("test_files/logo.txt"))
        expected = ("image", "png")
        self.assertTupleEqual(return_value, expected)

    def test_test_mime_type_true(self):
        self.assertTrue(test_mime_type(
            rel_path("test_files/logo.txt"),
            ["image"]
        ))

    def test_test_mime_type_false(self):
        self.assertFalse(test_mime_type(
            rel_path("test_files/normal_file.txt"),
            ["image"]
        ))

    def test_rename_mime_type(self):
        old_path = rel_path("test_files/file_without_extension")
        new_path = rename_mime_type(old_path)
        basename = os.path.basename(new_path)
        self.assertEqual(basename, "file_without_extension.png")

        # Necessary to keep track of renaming to rollback later
        self.revert_name.append((new_path, old_path))

    def test_test_and_rename_mime_type(self):
        accepted_types = ["image"]

        # This is a PNG file without the extension
        old_path_1 = rel_path("test_files/other_file_wo_ext")
        new_path_1 = test_and_rename_mime_type(old_path_1, accepted_types)
        self.assertRegex(os.path.basename(new_path_1), "other_file_wo_ext.png")
        self.revert_name.append((new_path_1, old_path_1))

        # This is a text file (should raise exception)
        old_path_2 = rel_path("test_files/normal_file.txt")
        with self.assertRaisesRegex(Exception, "File is not in the accepted types!"):
            test_and_rename_mime_type(old_path_2, accepted_types)

        # This is a PNG file that already has the extension .png
        old_path_3 = rel_path("test_files/logo.png")
        new_path_3 = test_and_rename_mime_type(old_path_3, accepted_types)
        self.assertRegex(os.path.basename(new_path_3), "logo.png")
        
        # No need to revert name, as there was no renaming

    def test_get_md5_hash(self):
        path_1 = rel_path("test_files/logo.png")
        hash_1 = get_md5_hash(path_1)
        expected = "367794bc62a0b8ea08d6e982d3db0827"
        self.assertRegex(hash_1, expected)

        path_2 = rel_path("nonexistent/path")
        with self.assertRaisesRegex(Exception, "Failed to calculate MD5 hash for file!"):
            get_md5_hash(path_2)

if __name__ == "__main__":
    unittest.main()