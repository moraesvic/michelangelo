import requests, unittest, subprocess

import lib.db as db
import lib.file_utils as file_utils
from tests.test_common import *

URL = "http://localhost:7777/michelangelo"

def is_server_connected():
    try:
        r = requests.get(URL)
        check_status_code(r.status_code)
        return True
    except:
        return False

def check_status_code(status_code):
    if not (status_code >= 200 and status_code < 300):
        raise Exception(f"Error: Server responded with code {status_code}")

def post_picture(path, base_dir = ""):
    pic = open(rel_path(path, base_dir),"rb")
    files = {"picture": pic}
    endpoint = "/pictures"
    r = requests.post(URL + endpoint, files=files)
    pic.close()
    check_status_code(r.status_code)
    json = r.json()
    return json["md5"]

def post_product(
        prod_name: str,
        prod_price: float,
        prod_instock: int,
        pic_path: str = "",
        prod_descr: str = "",
        base_dir: str = ""):

    pic_md5 = None, None
    if pic_path:
        pic_md5 = post_picture(pic_path, base_dir = base_dir)

    data = {
        "md5": pic_md5,
        "prodName": prod_name,
        "prodPrice": prod_price,
        "prodInStock": prod_instock,
        "prodDescr": prod_descr
    }
    endpoint= "/products"
    r = requests.post(URL + endpoint, json=data)
    check_status_code(r.status_code)
    json = r.json()
    return json["picId"], json["prodId"]

def delete_products():
    endpoint = "/products/all"
    r = requests.delete(URL + endpoint)
    check_status_code(r.status_code)
    return r.text

def delete_pictures():
    endpoint = "/pictures/all"
    r = requests.delete(URL + endpoint)
    check_status_code(r.status_code)
    return r.text

class FileUploadTest(unittest.TestCase):
    db = db.DB()
    upload_path = rel_path("../uploads")

    @classmethod
    def setUpClass(cls):
        printv("Setting up...")
        if not is_server_connected():
            raise Exception("Server was not connected! Cannot proceed with testing!")
        printv("Deleting existing database...")
        printv(delete_products())
        printv(delete_pictures())

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

    def select_pictures(self):
        # We will order by pic_id to get a deterministic result
        return self.db.query("""
            SELECT *
            FROM pics
            ORDER BY pic_id ;
        """).json()

    def ls_uploaded_pics(self):
        # Returns the number of files in the uploaded directory
        # as a list with every file basename
        n_pics = subprocess.check_output(f"""   \
            cd "{self.upload_path}" || exit 1 ; \
            find .                              \
            -maxdepth 1                         \
            -type f                             \
            -exec basename {{}} \; """,
            shell = True,
            text = True
        )
        ls = n_pics.strip().split("\n")
        if len(ls) == 1 and ls[0] == "":
            return []
        return ls

    def assert_db_filesystem_integrity(self):
        # We are storing files in the filesystem, and storing only path in the
        # DB. So, we need to check if every file in the DB is in the filesystem,
        # and every file in the FS is in the DB
        db_pics = self.select_pictures()
        ls_pics = self.ls_uploaded_pics()

        # If the number of files is not the same, we stop here
        if len(db_pics) != len(ls_pics):
            self.assertTrue(False)
            return
        
        for pic in db_pics:
            basename = os.path.basename(pic["pic_path"])
            self.assertIn(basename, ls_pics)

        # Since we have already fetched everything, might as well return
        # it and maybe save an operation later
        return db_pics, ls_pics

    def select_products(self):
        pass

    def test_post_picture_1(self):
        # Here, we will send a text file and expect it to be rejected
        # as a bad request. We also check to see if number of pictures
        # in upload path remains the same

        # Also, at any given time, number of rows in pictures table
        # should be the same as number of files in the uploads directory
        orig_db_pics, _ = self.assert_db_filesystem_integrity()

        file_path = rel_path("test_files/normal_file.txt")
        with self.assertRaisesRegex(Exception, r"^Error: Server responded with code 400"):
            md5 = post_picture(file_path)

        later_db_pics, _ = self.assert_db_filesystem_integrity()
        self.assertListEqual(orig_db_pics, later_db_pics)

    def test_post_picture_2(self):
        # Here, we will send a picture and expect it to be received with status
        # 200. We also check to see if number of pictures increases by one
        orig_db_pics, _ = self.assert_db_filesystem_integrity()

        file_path = rel_path("test_files/bears.jpg")
        md5 = post_picture(file_path)

        calculated_md5 = file_utils.get_md5_hash(file_path)
        self.assertEqual(md5, calculated_md5)

        later_db_pics, _ = self.assert_db_filesystem_integrity()
        self.assertEqual(len(orig_db_pics) + 1, len(later_db_pics))

    def test_post_picture_3(self):
        # Here, we will try to post a picture that already exists in the
        # system. The returned md5 should be the same, and the number of
        # rows in DB should not change

        # By default, tests run in alphabetical order, so this should be
        # run after test_post_picture_2
        orig_db_pics, _ = self.assert_db_filesystem_integrity()

        file_path = rel_path("test_files/bears.jpg")
        md5 = post_picture(file_path)

        calculated_md5 = file_utils.get_md5_hash(file_path)
        self.assertEqual(md5, calculated_md5)

        later_db_pics, _ = self.assert_db_filesystem_integrity()
        self.assertEqual(len(orig_db_pics), len(later_db_pics))


if __name__ == "__main__":
    unittest.main()