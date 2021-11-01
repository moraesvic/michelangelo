from flask import Response
import traceback, sys, datetime

# Just to make the code more readable when throwing an unknown exception
def printerr(err):
    LINE_LENGTH = 60
    date_string = " " + str(datetime.datetime.now()) + " "

    # Print date in a centered format
    margin = int((LINE_LENGTH - len(date_string)) / 2)
    print(f"{'-' * margin}{date_string}{'-' * margin}", file = sys.stderr)
    traceback.print_tb(err.__traceback__)
    print(err)
    print("-" * LINE_LENGTH, file = sys.stderr)

# Abstract class, not to be used directly
class CustomException(Exception):
    def log(self):
        # Default is printing to stderr
        # https://docs.python.org/3/library/traceback.html
        printerr(self)

    @classmethod
    def response(self):
        return Response(self.name, self.code)

class BadRequest(CustomException):
    name = "Bad request"
    code = 400

class NotFound(CustomException):
    name = "Not found"
    code = 404

class InternalServerError(CustomException):
    name = "Internal server error"
    code = 500

class AssertionFailed(InternalServerError):
    """Use this if an assertion fails due to bad coding
    (code that should not have been reached was executed, etc)"""