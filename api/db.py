import psycopg2
from dotenv import load_dotenv

# Necessary in order to import from parent directory
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.singleton import Singleton

class QueryResult:
    """Basically a struct for fitting the relevant parts of the result"""
    def __init__(self, status_msg: str, descr: tuple, row_count: int, rows: list):
        self.status_msg = status_msg
        self.descr = descr
        self.row_count = row_count
        self.rows = rows

class DB (metaclass = Singleton):
    conn = None

    def __init__(self):
        # When running development, flask will automatically import ".env"
        # into the environment variables. However, for production, we need this.
        load_dotenv()

        self.user = os.getenv("POSTGRES_USER")
        self.password = os.getenv("POSTGRES_PASSWORD")
        self.host = os.getenv("POSTGRES_HOST")
        self.dbname = os.getenv("POSTGRES_DATABASE")
        self.port = os.getenv("POSTGRES_PORT")

        try:
            self.conn = self.connect()
            self.cur = self.get_cursor()
        except Exception as e:
            print(f"Connection to database could not be established!\n{str(e)}")

    def get_sql_env(self):
        return {
            "user": self.user,
            "password": self.password,
            "host": self.host,
            "dbname": self.dbname,
            "port": self.port
            }

    def connect(self):
        return psycopg2.connect(**self.get_sql_env())

    def get_cursor(self):
        return self.conn.cursor()

    def query(self, fmtstr: str, args: tuple = tuple() ):
        # Strip formated string of whitespace
        stripped = fmtstr.strip()
        if stripped[-1] != ";":
            print("Warning: SQL command was not terminated with semi-colon")

        try:
            self.cur.execute(stripped, args)
            return QueryResult(
                self.cur.statusmessage,
                self.cur.description,
                self.cur.rowcount,
                self.cur.fetchall()
            )
        except Exception as e:
            print(f"Error! SQL command <{stripped}> raised an error: {str(e)}")
            return None
        
