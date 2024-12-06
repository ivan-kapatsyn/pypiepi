import psycopg2
import psycopg2.extras

cur = None
conn = None

try:
    # Korrigierte Verbindungszeichenkette mit UTF-8
    conn_string = "dbname='postgres' user='postgres' password='melisahu' host='localhost' port='5432'"
    conn = psycopg2.connect(conn_string)

    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Tabelle erstellen
    create_script = ''' CREATE TABLE IF NOT EXISTS "user" (
                                userID      int PRIMARY KEY,
                                username    varchar(40) NOT NULL,
                                password    varchar(40) NOT NULL,
                                userTyp    varchar(40) NOT NULL
 ) '''

    conn.commit()


except Exception as error:
    print("Ein Fehler ist aufgetreten:", error)

finally:
    # Überprüfen, ob cur und conn nicht None sind, bevor du sie schließt
    if cur is not None:
        cur.close()
    if conn is not None:
        conn.close()


class DataBaseUtil:
    def __init__(self, table_name, dbname, user, password, host='localhost', port=5432):
        self.__connection = None
        self.cursor = None

        self.conn_string = "dbname='postgres' user='postgres' password='melisahu' host='localhost' port='5432'"
        conn = psycopg2.connect(conn_string)

        self.table_name = table_name

        try:
            self.connection = psycopg2.connect(
                dbname= 'postgres',
                user='postgres',
                password='melisahu',
                host='localhost',
                port='5432'
            )
            self.cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

        except Exception as error:
            print(f"Fehler beim Herstellen der Verbindung: {error}")

    def check_if_table_exists(self, table_name) -> bool:
        cur = None
        try:
            query = f'''SELECT EXISTS(SELECT * FROM {table_name});'''
            self.cursor.execute(query, (table_name,))
            result = self.cursor.fetchone()
            return result[0]

        except Exception as error:
            print(f"Fehler ist aufgetreten: {error}")
            return False

    def close_connection(self):
        if self.connection is not None:
            self.connection.close()

if __name__ == "__main__":


    table_name = 'baka'

    if DataBaseUtil(table_name, 'postgres', 'postgres', 'melisahu','localhost', 5432).check_if_table_exists(table_name):
        print("Table exists")
    else:
        print("Table doesn't exist")


