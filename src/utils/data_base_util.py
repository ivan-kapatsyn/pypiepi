from pathlib import Path
from typing import Dict, List
import psycopg2
import psycopg2.extras
import json
from psycopg2._psycopg import cursor
from typing import Any, Dict, List, Tuple
from src.utils.env_variable_util import EnvVariableUtil
from src.utils.path_util import PathUtil


# -----------------------------------
class DataBaseUtil:
    def __init__(self):
        self.__connection = None
        self.cursor = None

        try:
            self.connection = psycopg2.connect(
                dbname=EnvVariableUtil.get_env_variable("DBNAME"),
                user=EnvVariableUtil.get_env_variable("USER"),
                password=EnvVariableUtil.get_env_variable("PASSWORD"),
                host=EnvVariableUtil.get_env_variable("HOST"),
                port=EnvVariableUtil.get_env_variable("PORT")
            )
            self.cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

        except Exception as error:
            print(f"Fehler beim Herstellen der Verbindung: {error}")


    def create_user(self, username, password):
        try:
            create_user_query = f"CREATE USER {username} WITH PASSWORD '{password}';"
            self.cursor.execute(create_user_query)
            self.connection.commit()
            print(f"Benutzer '{username}' wurde erstellt.")
        except Exception as error:
            print(f"Fehler beim Erstellen des Benutzers: {error}")

    def grant_all_privileges(self, username, dbname):
        try:
            grant_privileges_query = f"GRANT ALL PRIVILEGES ON DATABASE {dbname} TO {username};"
            self.cursor.execute(grant_privileges_query)
            self.connection.commit()
            print(f"Alle Berechtigungen auf die Datenbank '{dbname}' wurden an '{username}' gewährt.")
        except Exception as error:
            print(f"Fehler beim Gewähren der Berechtigungen: {error}")

    def check_if_table_exists(self, table_name) -> bool:
        try:
            query = f'''SELECT EXISTS (
                        SELECT 1
                        FROM information_schema.tables
                        WHERE table_schema = 'public'
                        AND table_name = '{table_name}'
                    );'''
            self.cursor.execute(query, (table_name,))
            result = self.cursor.fetchone()
            return result[0]
        except Exception as error:
            print(f"Fehler ist aufgetreten: {error}")
            return False

    def close_connection(self):
        if self.cursor is not None:
            self.cursor.close()
        if self.connection is not None:
            self.connection.close()


    def drop_all_the_tables(self):
        try:
            query = f'''DROP SCHEMA public CASCADE;
                                CREATE SCHEMA public;    
                                GRANT ALL ON SCHEMA public TO public;
                                '''
            self.cursor.execute(query)
            self.connection.commit()
            return True
        except Exception as error:
            print(f"Fehler ist aufgetreten: {error}")
            return False

    def create_schemes(self,json_file):
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
            #self.connection.close()

        except Exception as error:
            print(f"Fehler ist aufgetreten: {error}")
            return False


    def insert_one(self, table_name: str, obj: Dict[str, any], condition: str, dublicate: bool = False) -> None:
        try:
            query = f"SELECT 1 FROM {table_name} WHERE {condition} = %s;"
            self.cursor.execute(query, (obj[condition],))
            exists = self.cursor.fetchone()

            if exists and not dublicate:
                print(f"Duplicate entry already exists for {condition}: {obj[condition]}")
                return

            columns = obj.keys()
            values = tuple(obj.values())
            placeholders = ", ".join(["%s"] * len(columns))
            insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders});"
            self.cursor.execute(insert_query, values)
            self.connection.commit()
            print(f"Object inserted successfully into {table_name}: {obj[condition]}")

        except Exception as e:
            self.connection.rollback()
            raise Exception(f"Error inserting {table_name}: {e}")

    def insert_many(self, table_name: str, objects: List[Dict[str, any]], condition: str,
                    dublicate: bool = False) -> None:
        errors = []
        for obj in objects:
            try:
                self.insert_one(table_name, obj, condition, dublicate)
            except Exception as e:
                errors.append((obj, str(e)))

        if errors:
            print(errors)
            for obj, err in errors:
                print(f"Error inserting {table_name}: {err}")



if __name__ == "__main__":
    db_util = DataBaseUtil()
    try:
        table_name = 'tmuser'
        if db_util.check_if_table_exists(
                table_name):
            print("Table exists")
        else:
            print("Table doesn't exist")


        result = db_util.drop_all_the_tables()
        if result:
            print("Table was dropped")
        else:
            print("There was a problem. The Table was not dropped")

        # Benutzer erstellen
        #db_util.create_user(username="new_user", password="password")

        # Berechtigungen gewähren
        #db_util.grant_all_privileges(username="new_user", dbname=EnvVariableUtil.get_env_variable("DBNAME"))

        from pathlib import Path

        # Absoluter Pfad zum Hauptverzeichnis
        base_path = Path(__file__).resolve().parents[2]  # Zwei Ebenen über 'utils'
        json_file_path = base_path / "data_folder" / "database_structure.json"

        # Nutze den Pfad für die JSON-Datei
        if not json_file_path.exists():
            raise FileNotFoundError(f"Die Datei {json_file_path} wurde nicht gefunden.")
        db_util.create_schemes(json_file_path)

        #inserts into the database
        obj1 = {
                "user_id": 202345671,
                "username": "arthur_morgan",
                "password": "password123",
                "user_typ": "student",
                "remember_me": "TRUE"}

        objects = [
            {
                "user_id": 202345672,
                "username": "john_doe",
                "password": "newpassword",
                "user_typ": "admin",
                "remember_me": "TRUE"
            },
            {   "user_id": 202345673,
                "username": "jane_doe",
                "password": "mypassword",
                "user_typ": "admin",
                "remember_me": "TRUE"
            },
            {   "user_id": 202345671,
                "username": "arthur_morgan",
                "password": "password123",
                "user_typ": "student",
                "remember_me": "TRUE"
                }
                ]

        try:
            db_util.insert_one("tmuser", obj1, condition="user_id", dublicate=True)
            db_util.insert_many("tmuser", objects, condition="user_id", dublicate=False)

        except Exception as e:
            print(e)

    except Exception as error:
        print(f"Ein Fehler ist aufgetreten: {error}")

    finally:
        # Verbindung schließen
        if db_util:
            print("Schließe die Datenbank-Verbindung...")
            db_util.close_connection()

