import psycopg2
import psycopg2.extras
import json
from pathlib import Path
from psycopg2._psycopg import cursor
from typing import Any, Dict, List, Tuple, Callable

from psycopg2.extras import DictRow

from src.utils.env_variable_util import EnvVariableUtil
from src.utils.path_util import PathUtil


# -----------------------------------
class DataBaseUtil:
    def __init__(self):
        self.__connection = None
        self.cursor = None

#------CONNECTION TO THE DATABASE----------
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
            print(f"Error to connect with the database: {error}")

#---EXECUTE COMMAND----
    def __execute_command(self, sql_query: str = None, params: tuple = None, fetch_one: bool = False, log_message: str =None):
        try:
            self.cursor.execute(sql_query, params)
            if log_message:
                print(log_message)
            if fetch_one:
                return self.cursor.fetchone()

            self.connection.commit()
            return True
        except Exception as error:
            print(f"Error by execute command: {error}")
            self.connection.rollback()
            return None

# -------CREATING A USER----------------
    def __create_user(self, username, password):
        create_user_query = f"CREATE USER {username} WITH PASSWORD '{password}';"
        return self.__execute_command(
            sql_query=create_user_query,
            params=(username, password),
            log_message=f"User '{username}' was created.")

#-------GIVING THE USER ALL PRIVILEGES--------
    def __grant_all_privileges(self, username, dbname):
        grant_privileges_query = f"GRANT ALL PRIVILEGES ON DATABASE {dbname} TO {username};"
        return self.__execute_command(
            sql_query=grant_privileges_query,
            params=(username, dbname),
            log_message=f"Grant all privileges on database '{dbname}' to '{username}'."
        )

#------CHECK IF TABLE EXIST---------
    def _check_if_table_exists(self, table_name) -> bool:
        query = f'''SELECT EXISTS (
                        SELECT 1
                        FROM information_schema.tables
                        WHERE table_schema = 'public'
                        AND table_name = '{table_name}'
                    );
                '''
        result_exist = self.__execute_command(
                sql_query=query,
                params=(table_name,),
                fetch_one=True,
                log_message=f"Table '{table_name}' exists."
            )
        return result_exist[0] if result_exist else False

# -------DROP ALL TABLES----------
    def _drop_all_the_tables(self):
            query = f'''DROP SCHEMA public CASCADE;
                                    CREATE SCHEMA public;    
                                    GRANT ALL ON SCHEMA public TO public;
                                    '''
            result_dropping = self.__execute_command(
                sql_query=query,
                log_message="All tables were dropped."
            )
            return result_dropping is None

#-------CREATES THE SCHEMES FOR THE DATABASE--------
    def __create_schemes(self, json_file):
        try:
            with open(json_file) as file:
                data = json.load(file)
            tables = data.get("tables", [])
            for table in tables:
                table_name = table.get("table_name")
                if not table_name:
                    raise ValueError("Mising table name in the JSON file.")

                columns = table.get("columns", [])
                if not columns:
                    raise ValueError(f"No rows defined at the table {table_name}.")

                column_definitions = []
                foreign_keys = []

                for column in columns:
                    column_name = column.get("column_name")
                    data_type = column.get("data_type")
                    constraints = column.get("constraints", "")

                    if not column_name or not data_type:
                        raise ValueError(f"Missing column definition in the table {table_name}: {column}")

                    column_name = str(column_name).strip()
                    data_type = str(data_type).strip()
                    constraints = str(constraints).strip()

                    # If it is a FOREIGN KEY, add it to a separate list
                    if "FOREIGN KEY" in constraints:
                        foreign_keys.append(
                            f"FOREIGN KEY ({column_name}) {constraints.split('FOREIGN KEY')[1].strip()}")
                        constraints = ""

                    # Create the column definition
                    column_definition = f"{column_name} {data_type} {constraints}".strip()
                    column_definitions.append(column_definition)

                # Creating the script for creating a table
                create_table_script = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_definitions)}"

                # add the FOREIGN KEYS if it's available
                if foreign_keys:
                    create_table_script += f", {', '.join(foreign_keys)}"

                create_table_script += ");"  # Schließe die CREATE TABLE-Anweisung ab

                print(f"Create Table {table_name}")
                print(create_table_script)

                self.cursor.execute(create_table_script)

            self.cursor.connection.commit()
            print("All tables were created successfully.")

        except Exception as error:
            print(f"Error by creating the database scheme: {error}")
            return False

#------INSERT ONE TO THE DATABASE--------
    def insert_one(self, table_name: str, obj: Dict[str, any], column: str, dublicate: bool = False) -> None:
        print(f"Inserting in table {table_name}")

        initial_key_value = obj[column]

        if dublicate:
            while True:
                query_check = f'SELECT EXISTS(SELECT 1 FROM {table_name} WHERE {column} = %s);'
                self.__execute_command(query_check, (initial_key_value,))
                exists = self.cursor.fetchone()[0]

                if not exists:
                    break

                initial_key_value += 1

                # Update the object with the new key value
                obj[column] = initial_key_value
                print(f"Updated object key: {obj[column]}")  # Debug output

                # Prepare the insert statement
            columns = ', '.join(obj.keys())
            values_placeholder = ', '.join(['%s'] * len(obj))
            query = f'INSERT INTO {table_name} ({columns}) VALUES ({values_placeholder});'

            # Execute the insert command
            self.__execute_command(
                sql_query=query,
                params=tuple(obj.values()),
            )
            print(f"Inserted {obj} into {table_name}")  # Debug output


# ------INSERT MANY TO THE DATABASE--------
    def _insert_many(self, table_name: str, objects: List[Dict[str, any]], column: str, dublicate: bool = False) -> None:
        print(f"Inserting into {table_name}...")  # Debug output
        errors = []

        for obj in objects:
            initial_key_value = obj[column]

            if dublicate:
                while True:
                    query_check = f'SELECT EXISTS(SELECT 1 FROM {table_name} WHERE {column} = %s);'
                    self.__execute_command(query_check, (initial_key_value,))
                    exists = self.cursor.fetchone()[0]

                    if not exists:
                        break  # Exit loop if the value does not exist

                    # Increment the key value by 1
                    initial_key_value += 1

                # Update the object with the new key value
                obj[column] = initial_key_value
                print(f"Updated object key: {obj[column]}")  # Debug output

            # Prepare the insert statement
            columns = ', '.join(obj.keys())
            values_placeholder = ', '.join(['%s'] * len(obj))
            query = f'INSERT INTO {table_name} ({columns}) VALUES ({values_placeholder});'

            # Execute the insert command
            self.__execute_command(
                sql_query=query,
                params=tuple(obj.values()),
                )
            print(f"Inserted {obj} into {table_name}")  # Debug output

        if errors:
            print("Errors encountered during insertion:")
            for obj, err in errors:
                print(f"Error inserting into {table_name}: {err}")

#------FETCH ONE--------
    def __fetch_one(self, query: str, params: Tuple[Any, ...] = ()) -> DictRow | None:
        result_fetch_one = self.__execute_command(
            sql_query=query,
            params=params,
            fetch_one=True,
            log_message=None
        )
        if result_fetch_one is True:
            return None
        return result_fetch_one

#------FETCH MANY-------
    def __fetch_all(self, query: str, params: Tuple[Any, ...] = ()) -> List[Dict[str, Any]]:
        self.__execute_command(sql_query=query, params=params)  # Execute the command without fetch_one
        if self.cursor.rowcount == 0:  # Check if no rows were returned
            return []

        columns = [desc[0] for desc in self.cursor.description]  # Get column names
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]  # Fetch all rows

#------LOAD ONE DATA------
    def load_data(self, table_name: str, column: str, value:any ) -> DictRow:
        query = f'SELECT * FROM {table_name} WHERE {column} = %s;'
        result_load = self.__fetch_one(query, (value,))

        if result_load is None:
            raise Exception(f"No entry found where {column} = {value}.")
        else:
            return result_load

# ------LOAD MANY DATA-------
    def load_many(self, table_name: str, filter_function: Callable[[Dict[str, Any]], bool]) -> List[Dict[str, Any]]:
        query = f'SELECT * FROM {table_name};'
        results = self.__fetch_all(query)
        print(f"Fetched results from {table_name}: {results}")  # Debug output
        return [result for result in results if filter_function(result)]

# -----FILTER FUNCTION FOR LOADING MANY DATA-------
    @staticmethod
    def filter_function(obj):
        return obj['username'].startswith('A')

# ------LOAD/DELETE DATA WITH CONDITIONS------
    def _build_query(
            self,
            table_name: str,
            conditions: List[Tuple[str, Any]],
            operator: str,
            query_type: str = "SELECT"
    ) -> Tuple[str, List[Any]]:

        if operator not in ("AND", "OR"):
            raise ValueError("Operator muss 'AND' oder 'OR' sein.")

        if query_type not in ("SELECT", "DELETE"):
            raise ValueError("Nur 'SELECT' und 'DELETE' werden unterstützt.")

        condition_string = f" {operator} ".join([f"{col} = %s" for col, _ in conditions])

        if query_type == "SELECT":
            query = f"SELECT * FROM {table_name} WHERE {condition_string};"
        elif query_type == "DELETE":
            query = f"DELETE FROM {table_name} WHERE {condition_string};"

        params = [value for _, value in conditions]

        return query, params


#-----DELETING DATA---------
    def delete_data(self, table_name: str, condition: str, value: Any) -> None:
        query = f'DELETE FROM {table_name} WHERE {condition} = %s;'
        affected_rows = self.__execute_command(
            sql_query=query,
            params=(value,),
            fetch_one=False,
            log_message=f"Attempting to delete entry where {condition} = {value}"
        )
        if affected_rows == 0:
            print(f"No entry found where {condition} = {value}.")

        print(f"Successfully deleted entry where {condition} = {value}.")

#-----INITIALISE DATABASE--------
    def _initialise(self, json_file: str) -> None:
        print("Initializing the database...")
        # Drop existing tables
        self._drop_all_the_tables()

        # Create new schema
        self.__create_schemes(json_file)

        # Optionally, insert initial data or perform any other setup here
        print("Database initialized successfully.")

#-----CLOSE CONNECTION--------
    def __del__(self):
        if self.cursor is not None:
            self.cursor.close()
        if self.__connection is not None:
            self.__connection.close()