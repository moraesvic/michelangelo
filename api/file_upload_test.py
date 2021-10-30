import sys, time, re, random, math, unittest, subprocess
from typing import List, Tuple, Dict, Callable
from werkzeug.datastructures import FileStorage

from file_upload import *

NUMBER_OF_TESTS = 50
VERBOSE = any([re.search(r"-v", arg) for arg in sys.argv])

def printv(s: str):
    """Prints string s if running in verbosity mode"""
    if VERBOSE:
        print(s)

def rel_path(path):
    this_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(this_dir, path)

class FileUploadTest(unittest.TestCase):

    # When we are done with tests, we need to close files and remove
    # all files saved to disk

    open_files = []
    tmp_files = []

    # Let's say we rename a file A to the name B. We need to keep track
    # of this and then revert these changes in the end

    revert_name = []

    def open_file(self, path):
        # A wrapper to open files safely into a Werkzeug object
        filename = rel_path(path)
        fd = open(filename, 'rb')
        self.open_files.append(fd)
        return FileStorage(fd)

    def get_valid_file(self):
        # This refers to a normal tiny text file
        return self.open_file("test_files/normal_file.txt")

    def get_large_file(self):
        # This refers to a 10MB file with random binary data, generated with
        # "dd if=/dev/urandom of=large_file.bin bs=1024 count=$((10 * 1024))"

        # As the default FILE_MAX_SIZE is 5MB, this should give an error
        return self.open_file("test_files/large_file.bin")

    @classmethod
    def tearDownClass(cls):
        printv("Closing files")
        for file in cls.open_files:
            file.close()

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
        random_number_length = round(math.log10(NEW_NAME_MAX_RND))
        return re.compile(r"[0-9]{%d}-[0-9]{%d}" % (
            milliseconds_length, random_number_length))

    def test_get_new_name(self):
        regex = self.get_filename_regex()

        for _ in range(NUMBER_OF_TESTS):
            with self.subTest():
                time.sleep(random.random() * 0.05)
                new_name = get_new_name()
                if self.assertRegex(new_name, regex):
                    printv(f"{new_name} : ok!")

    def test_save_file_no_dir(self):
        file = self.get_valid_file()
        with self.assertRaisesRegex(Exception, "Given upload path does not exist!"):
            save_file(file, "nonexistent/path")

    def test_save_file_large_file_case_1(self):
        # This is a large file, and should raise an exception
        file = self.get_large_file()
        with self.assertRaisesRegex(Exception, "File is too large!"):
            save_file(
                file,
                rel_path("test_files"),
                max_size = FILE_MAX_SIZE,
                check_size_before_saving = False)

    def test_save_file_large_file_case_2(self):
        # The difference to the test above is that this will read the file
        # in-place, as a stream, and not save to disk, when checking size
        file = self.get_large_file()
        with self.assertRaisesRegex(Exception, "File is too large!"):
            save_file(
                file,
                rel_path("test_files"),
                max_size = FILE_MAX_SIZE,
                check_size_before_saving = True)

    def test_save_file_large_file_case_3(self):
        # This time, it is still a large file, but, as max_size is zero,
        # it should be saved to a path and match the standard name format
        file = self.get_large_file()
        file_path = save_file(
                file,
                rel_path("test_files"),
                max_size = 0)

        printv(f"File saved to {file_path}")
        file_basename = os.path.basename(file_path)
        
        self.assertRegex(file_basename, self.get_filename_regex())
        self.tmp_files.append(file_path)

    def test_save_file_ok(self):
        # This should run successfully
        file = self.get_valid_file()
        file_path = save_file(
                file,
                rel_path("test_files"),
                max_size = 0)

        printv(f"File saved to {file_path}")
        file_basename = os.path.basename(file_path)
        
        self.assertRegex(file_basename, self.get_filename_regex())
        self.tmp_files.append(file_path)

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