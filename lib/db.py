import psycopg2, os
from dotenv import load_dotenv
import datetime as dt

from .singleton import Singleton

class QueryResult:
    """Basically a struct for fitting the relevant parts of the result"""
    def __init__(self, status_msg: str, descr: tuple, row_count: int, rows: list):
        # This middleware generates output which is a little more compact than
        # Node.js's PG. Here, we receive a description of the columns (descr),
        # and every row is given without labels. Example:

        # What we have:
        # [(1, 'foo'), (2, 'bar')]

        # What we wanted
        # [{'id': 1, 'name': 'foo'}, {'id': 2, 'name': 'bar'}]

        # So, if we want to have them labeled (for use in JSON and others),
        # we have to do it ourselves.

        # I did not want to do this by default because we would be running into
        # some overhead which might not be needed every time. So, to get labeled
        # rows, call instance method json()

        # Typically, the API will call the DB as db.query(...).json()

        self.datetime = dt.datetime.now()
        self.status_msg = status_msg
        self.descr = descr
        self.row_count = row_count
        self.rows = rows
        self.labeled_rows = None

    def json(self):
        if self.labeled_rows:
            return self.labeled_rows
        
        self.labeled_rows = []
        number_of_cols = len(self.descr)
        for r in self.rows:
            row_dict = {}
            for i in range(number_of_cols):
                col = self.descr[i]
                row_dict[col.name] = r[i]
            self.labeled_rows.append(row_dict)

        return self.labeled_rows

    def __str__(self):
        return ( "\n"
            + "-----\n"
            + f"{ self.datetime }\n"
            + f"{ self.status_msg }\n"
            + f"{ self.descr }\n"
            + f"{ self.row_count } rows affected\n"
            + "-----" )

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
        