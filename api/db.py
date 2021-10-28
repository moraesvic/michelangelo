import os

class DB:
    def __init__(self):
        pass

    def get_sql_env(self):
        return os.getenv("PG_PASSWORD")