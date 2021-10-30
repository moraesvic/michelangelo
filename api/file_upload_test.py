import time, re, random, math, unittest
from typing import List, Tuple, Dict, Callable
from werkzeug.datastructures import FileStorage

from file_upload import *

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
NUMBER_OF_TESTS = 50
VERBOSE = True

class FileUploadTest(unittest.TestCase):

    open_files = []

    def open_file(self, path):
        # A wrapper to open files safely into a Werkzeug object
        filename = os.path.join(THIS_DIR, path)
        fd = open(filename, 'rb')
        self.open_files.append(fd)
        return FileStorage(fd)

    def get_valid_file(self):
        # This refers to a Python script of normal size ( < 10 KB)
        return self.open_file("file_upload.py")

    def get_large_file(self):
        # This refers to a 10MB file with random binary data, generated with
        # "dd if=/dev/urandom of=large_file.bin bs=1024 count=$((10 * 1024))"

        # As the default FILE_MAX_SIZE is 5MB, this should give an error
        return self.open_file("large_file.bin")

    def tearDown(self):
        for file in self.open_files:
            file.close()

    def test_get_new_name(self):
        milliseconds_length = len(str(int(time.time() * 1000)))
        random_number_length = round(math.log10(NEW_NAME_MAX_RND))
        regex = re.compile(r"[0-9]{%d}-[0-9]{%d}" % (
            milliseconds_length, random_number_length))

        for _ in range(NUMBER_OF_TESTS):
            with self.subTest():
                time.sleep(random.random() * 0.05)
                new_name = get_new_name()
                if self.assertRegex(new_name, regex) and VERBOSE:
                    print(f"{new_name} : ok!")

    def test_save_file_no_dir(self):
        file = self.get_valid_file()
        with self.assertRaisesRegex(Exception, "Given upload path does not exist!"):
            save_file(file, "nonexistent/path")

    def test_save_file_large_file_case_1(self):
        file = self.get_large_file()
        with self.assertRaisesRegex(Exception, "File is too large!"):
            save_file(
                file,
                ".",
                max_size = FILE_MAX_SIZE,
                check_size_before_saving = False)

    def test_save_file_large_file_case_2(self):
        file = self.get_large_file()
        with self.assertRaisesRegex(Exception, "File is too large!"):
            save_file(
                file,
                ".",
                max_size = FILE_MAX_SIZE,
                check_size_before_saving = True)


if __name__ == "__main__":
    unittest.main()