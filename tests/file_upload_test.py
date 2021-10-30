import sys, time, re, random, math, unittest, subprocess
from werkzeug.datastructures import FileStorage

from api.lib.file_upload import *
from api.lib.file_utils import NEW_NAME_MAX_RND

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

# if __name__ == "__main__":
unittest.main()