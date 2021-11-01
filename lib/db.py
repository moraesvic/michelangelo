import psycopg2, os
from dotenv import load_dotenv
import datetime as dt

from lib.singleton import Singleton
import lib.exceptions as exceptions

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
        # This is not even JSON, it is a dictionary, but the name stuck
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
            self.conn.autocommit = True
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

    def query(
                self,
                fmtstr: str,
                args: tuple = tuple(),
                verbose: bool = False ):
        # In case user accidentally uses sole argument without making it into
        # a tuple, we can help them and prevent an error
        if type(args) != tuple:
            print("Warning: argument should be given as tuple")
            args = (args,)
        
        # Strip formated string of whitespace
        stripped = fmtstr.strip()
        if stripped[-1] != ";":
            print("Warning: SQL command was not terminated with semi-colon")

        # We need to get the cursor here. For the same connection, many
        # cursors can be active, and we need one per query, if we don't
        # want to run into race conditions

        try:
            cur = self.conn.cursor()
        except:
            print("Could not get a cursor!")
            raise exceptions.InternalServerError("Could not get cursor.")

        try:
            cur.execute(stripped, args)
            query_result = QueryResult(
                cur.statusmessage,
                cur.description,
                cur.rowcount,
                cur.fetchall()
            )
            cur.close()
            return query_result
            
        except psycopg2.IntegrityError as err:
            # If this error is raised, a constraint was violated
            # (e.g. trying to insert string for integer field, foreign key
            # is invalid, non-nullable field was left empty, etc.)

            # It could be bad user input, but application logic should have
            # filtered this. Better to examine with care.
            
            if verbose:
                cmd = cur.mogrify(stripped, args).decode("utf-8")
                print(f"Integrity error! SQL command <{cmd}> raised an error")
                print(err)
                print("Are you trying to insert non-sanitized or non-validated data?")
            cur.close()
            raise exceptions.BadRequest("Integrity error occurred interacting with database")

        except psycopg2.Error as err:
            # Another kind of error occurred. Could be anything, from a disconnect
            # to a programming mistake. This is considered more serious than the
            # above.
            print(err)
            cmd = cur.mogrify(stripped, args).decode("utf-8")
            cur.close()
            print(f"Error! SQL command <{cmd}> raised an error")
            exceptions.printerr(err)
            raise exceptions.InternalServerError("An unknown error happened.")
        