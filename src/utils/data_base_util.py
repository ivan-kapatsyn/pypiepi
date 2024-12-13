from multiprocessing import connection

import psycopg2
import psycopg2.extras
import json
import csv

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


# -----------------------------------
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


# --------------------------------------------------


class Initialise(DataBaseUtil):
    def __init__(self):
        super().__init__(self, 'postgres', 'postgres', 'melisahu', 'localhost', 5432, )

    @staticmethod
    def drop_table(cursor):
        try:
            query = f'''DROP SCHEMA public CASCADE;
                        CREATE SCHEMA public;    
                        GRANT ALL ON SCHEMA public TO public;
                        '''
            cursor.execute(query)
            cursor.connection.commit()
            return True

        except Exception as error:
            print(f"Fehler ist aufgetreten: {error}")
            return False


# -------------------------------------------------------

class CreateTableFromJSON(DataBaseUtil):
    def __init__(self):
        super().__init__('postgres', 'postgres', 'melisahu', 'localhost', 5432)

    def create_table(self, json_file):
        try:
            with open(json_file) as file:
                data = json.load(file)

            tables = data.get("tables", [])
            for table in tables:
                table_name = table.get("table_name")
                if not table_name:
                    raise ValueError("Fehlender Tabellenname in der JSON-Datei.")

                columns = table.get("columns", [])
                if not columns:
                    raise ValueError(f"Keine Spalten für die Tabelle {table_name} definiert.")

                column_definitions = []
                foreign_keys = []

                for column in columns:
                    column_name = column.get("column_name")
                    data_type = column.get("data_type")
                    constraints = column.get("constraints", "")

                    if not column_name or not data_type:
                        raise ValueError(f"Fehlende Spaltendefinition in der Tabelle {table_name}: {column}")

                    column_name = str(column_name).strip()
                    data_type = str(data_type).strip()
                    constraints = str(constraints).strip()

                    # Wenn es sich um einen FOREIGN KEY handelt, füge ihn zu einer separaten Liste hinzu
                    if "FOREIGN KEY" in constraints:
                        foreign_keys.append(
                            f"FOREIGN KEY ({column_name}) {constraints.split('FOREIGN KEY')[1].strip()}")
                        constraints = ""  # Foreign key constraint sollte nicht in der Spaltendefinition stehen

                    # Erstelle die Spaltendefinition
                    column_definition = f"{column_name} {data_type} {constraints}".strip()
                    column_definitions.append(column_definition)

                # Baue die CREATE TABLE-Anweisung zusammen
                create_table_script = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_definitions)}"

                # Füge die FOREIGN KEYS hinzu, falls vorhanden
                if foreign_keys:
                    create_table_script += f", {', '.join(foreign_keys)}"

                create_table_script += ");"  # Schließe die CREATE TABLE-Anweisung ab

                print(f"Create Table {table_name}")
                print(create_table_script)

                # Führe die SQL-Anweisung aus
                self.cursor.execute(create_table_script)

            self.cursor.connection.commit()
            print("Alle Tabellen wurden erfolgreich erstellt.")

        except Exception as error:
            print(f"Fehler ist aufgetreten: {error}")
            return False


# ----CHECK IF TABLE EXIST
if __name__ == "__main__":
    table_name = 'user'
    if DataBaseUtil(table_name, 'postgres', 'postgres', 'melisahu', 'localhost', 5432).check_if_table_exists(
            table_name):
        print("Table exists")
    else:
        print("Table doesn't exist")

# ----DROP TABLE
#initialiser = Initialise()
#result = initialiser.drop_table(initialiser.cursor)
#if result:
#    print("Table was dropped")
#else:
#    print("There was a problem. The Table was not dropped")

# ---------
if __name__ == '__main__':
    db_creator = CreateTableFromJSON()
    db_creator.create_table("database_structure.json")
