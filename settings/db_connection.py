import pymysql

class DBMS:
    def __init__(self, host, port, user, password, name):
        self.conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=name,
            cursorclass=pymysql.cursors.DictCursor,
        )
        self.conn.autocommit(False)
        self.cursor = self.conn.cursor()
