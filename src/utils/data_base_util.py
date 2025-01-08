import secrets
import uuid
from src.utils.password_utils import PasswordUtils
import psycopg2
import psycopg2.extras
import json
import pandas as pd
from pathlib import Path
from pandas.core.interchange import column
from psycopg2._psycopg import cursor
from typing import Any, Dict, List, Tuple, Callable
from psycopg2.extras import DictRow
from src.utils.env_variable_util import EnvVariableUtil
from src.utils.path_util import PathUtil
import os
import csv


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


# -----CLOSE CONNECTION--------
    def __del__(self):
        if self.cursor is not None:
            self.cursor.close()
        if self.__connection is not None:
            self.__connection.close()


#--------GENERATE UNIQUE ID-------
    def generate_unique_id(self) -> str:
        return secrets.token_hex(8)


# ------INSERT ONE TO THE DATABASE--------
    def insert_one(self, table_name: str, obj: Dict[str, any], column: str, dublicate: bool = False) -> None:
        print(f"Inserting in table {table_name}")

        obj = {
            key: json.dumps(value) if isinstance(value, (list, dict)) else value
            for key, value in obj.items()
        }

        if "password" in obj:
            obj["password"] = PasswordUtils.hash_password(obj["password"])

        # Prepare the insert statement
        columns = ', '.join(obj.keys())
        values_placeholder = ', '.join(['%s'] * len(obj))
        query = f'INSERT INTO {table_name} ({columns}) VALUES ({values_placeholder});'

        if dublicate:
            initial_key_value = obj[column]
            while True:
                # Check if the current key value exists
                query_check = f'SELECT EXISTS(SELECT 1 FROM {table_name} WHERE {column} = %s);'
                self.__execute_command(query_check, (initial_key_value,))
                exists = self.cursor.fetchone()[0]

                if not exists:
                    break  # Exit the loop if the key is unique

                # generates a new unique_id to find a new unique key
                initial_key_value = self.generate_unique_id()
                obj[column] = initial_key_value
                print(f"Updated object key: {obj[column]}")  # Debug output

        else:
            # Check for duplicates before inserting if not allowing duplicates
            query_check = f'SELECT EXISTS(SELECT 1 FROM {table_name} WHERE {column} = %s);'
            self.__execute_command(query_check, (obj[column],))
            exists = self.cursor.fetchone()[0]

            if exists:
                raise Exception(f"Duplicate entry for {column}: {obj[column]}")

        self.__execute_command(sql_query=query, params=tuple(obj.values()))
        print(f"Inserted {obj} into {table_name}")  # Debug output


# ------INSERT MANY TO THE DATABASE--------
    def insert_many(self, table_name: str, objects: List[Dict[str, any]], column: str,
                    dublicate: bool = False) -> None:
        if not objects:
            print("No objects to insert.")  # Debug output
            return

        print(f"Inserting into {table_name}...")  # Debug output

        for obj in objects:
            if "password" in obj:
                obj["password"] = PasswordUtils.hash_password(obj["password"])
            for key, value in obj.items():
                if isinstance(value, (list, dict)):
                    obj[key] = json.dumps(value)

        if dublicate:
            # Collect existing keys in one query for efficiency
            existing_keys_query = f"SELECT {column} FROM {table_name} WHERE {column} IN %s;"
            existing_keys = set()

            keys_to_check = [obj[column] for obj in objects]
            self.__execute_command(existing_keys_query, (tuple(keys_to_check),))
            for row in self.cursor.fetchall():
                existing_keys.add(row[0])

            # Update objects with unique keys
            for obj in objects:
                while obj.get(column) in existing_keys:
                    obj[column] = self.generate_unique_id()
                existing_keys.add(obj[column])

                # Prepare and execute batch insert
        columns = ', '.join(objects[0].keys())
        values_placeholder = ', '.join(['%s'] * len(objects[0]))
        query = f"INSERT INTO {table_name} ({columns}) VALUES {', '.join(['(' + values_placeholder + ')' for _ in objects])};"
        values = tuple(value for obj in objects for value in obj.values())

        try:
            self.__execute_command(sql_query=query, params=values)
            print(f"Inserted {len(objects)} records into {table_name}.")
        except Exception as e:
            print(f"Error during batch insert into {table_name}: {e}")


#-------GET PRIMARY KEY-----------
    def get_primary_key_column(self, table_name: str) -> str:
        query = f"SELECT a.attname FROM pg_index i JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey) WHERE i.indrelid = %s::regclass AND i.indisprimary;"
        primary_key_column = self.__execute_command(query, (table_name,), fetch_one=True)
        if primary_key_column is None:
            raise Exception(f"No primary key column for {table_name}")
        return primary_key_column[0]


#--------EXIST USER BY ID---------
    def exists_user_by_id(self, table_name: str, user_id: Any) -> bool:
        query = f"SELECT EXISTS(SELECT 1 FROM {table_name} WHERE user_id = %s);"
        result = self.__fetch_one(query, (user_id,))
        print(f"Checking existence for user_id {user_id}: result = {result}")  # Debug-Ausgabe
        return result[0] if result else False


# -------LOAD ONE------
    def load_one(self, table_name: str, column: str, value:any) -> DictRow | None:
        if not column.isidentifier():
            raise ValueError(f"Invalid column name: {column}")

        query = f'SELECT * FROM {table_name} WHERE {column} = %s;'
        result_load = self.__fetch_one(query, (value,))

        if result_load is None:
            print(f"No entry found where {column} = {value}.")
            return None

        if "qualification" in result_load and result_load["qualification"] is not None:
            if isinstance(result_load["qualification"], str):
                result_load["qualification"] = json.loads(
                    result_load["qualification"])
            elif isinstance(result_load["qualification"], list):
                pass
            else:
                raise TypeError(f"Unexpected type for qualification: {type(result_load['qualification'])}")

        return result_load


# ------LOAD MANY DATA-------
    def load_many(self, table_name: str, filter_function: str = None, values: List[Any] = None) -> List[Dict[str, Any]]:
        if values:
            placeholders = ', '.join(['%s'] * len(values))
            query = f'SELECT * FROM {table_name} WHERE {filter_function.replace('%s', placeholders)};'
            params = tuple(values)
        elif filter_function:
            query = f'SELECT * FROM {table_name} WHERE {filter_function};'
            params = ()
        else:
            query = f'SELECT * FROM {table_name};'
            params = ()

        print(f"Executing query: {query} with values: {values}")

        results = self.__execute_command(
            sql_query=query,
            params=params,
            fetch_one=False,
            fetch_all=True,
            log_message=f"Loading records from {table_name} with filter {filter_function}."
            )

        if results is not None:  # Check if results are not None (indicating no error occurred)
            print(f"Successfully loaded {len(results)} records from {table_name}.")  # Debug output
            return results
        else:
            print(f"Error during batch load in {table_name}.")
            return []


# -----DELETING ONE---------
    def delete_one(self, table_name: str, id_value: Any) -> None:
        id_column = self.get_primary_key_column(table_name)

        query = f"DELETE FROM {table_name} WHERE {id_column} = %s;"
        self.__execute_command(query, (id_value, ))
        print(f"Deleted record from {table_name} where {id_column} = {id_value}.")


# ------DELETE MANY DATA--------
    def delete_many(self, table_name: str, column: str, values: List[Any]) -> None:
        if not values:
            print("No values to delete.")
            return

        placeholders = ', '.join(['%s'] * len(values))
        query = f"DELETE FROM {table_name} WHERE {column} IN ({placeholders});"

        print(f"Deleting {len(values)} records from {table_name} where {column} matches.")  # Debug output
        self.__execute_command(sql_query=query, params=tuple(values))
        print(f"Successfully deleted {len(values)} records from {table_name}.")  # Debug output


#-------UPDATE ONE-----
    def update_one(self, table_name: str, id_column: str, id_value: Any, new_values: Dict[str, Any]) -> None:
        if not new_values:
            print("No new values to update.")
            return

        set_clause = ', '.join(f"{key} = %s" for key in new_values.keys())
        query = f"UPDATE {table_name} SET {set_clause} WHERE {id_column} = %s;"

        params = tuple(new_values.values()) + (id_value, )
        print(f"Executing update query: {query} with params: {new_values}")

        affected_rows = self.__execute_command(
            sql_query=query,
            params=params,
            fetch_one=False,
            fetch_all=False,
            log_message=f"Updating row in {table_name} where {id_column} = {id_value}."
        )
        if affected_rows == 0:
            print(f"No entry found where {id_column} = {id_value}.")

        print(f"Succesfully updated where {id_column} = {id_value} from {table_name}.")


# -------UPDATE DATA--------
    def update_many(self, table_name: str, conditions: List[Dict[str, Any]], new_values: List[Dict[str, Any]]) -> None:
        if not new_values:
            print("No updates provided.")  # Debug output
            return

        for condition, new_value in zip(conditions, new_values):
            where_clause = ' AND '.join([f"{key} = %s" for key in condition.keys()])
            set_clause = ', '.join([f"{key} = %s" for key in new_value.keys()])
            query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause};"

            params = tuple(new_value.values()) + tuple(condition.values())
            print(f"Executing update query: {query} with params: {params}")  # Debug output

            affected_rows = self.__execute_command(
                sql_query=query,
                params=params,
                fetch_one=False,
                fetch_all=False,
                log_message=f"Updating rows in {table_name} with conditions: {condition}."
            )

            if affected_rows == 0:
                print(f"No entries matched the conditions: {condition}.")
            else:
                print(f"Successfully updated rows in {table_name} with conditions: {condition}.")


# ------SAVE DATA TO CSV FILE-------
    def save_data_to_csv(self, table_name: str, data: List[Dict[str, Any]], column_types: Dict[str, str], csv_directory: str = None) -> str:
        csv_directory = csv_directory or EnvVariableUtil.get_env_variable('CSV_FILE_PATH')
        if not os.path.exists(csv_directory):
            os.makedirs(csv_directory)
        csv_file = os.path.join(csv_directory, f"{table_name}.csv")

        try:
            if data:
                df = pd.DataFrame(data)
                for col, col_type in column_types.items():
                    if col in df.columns:
                        if col_type.lower() == 'jsonb':
                            df[col] = df[col].apply(lambda x: json.dumps(x) if isinstance(x, (list, dict)) else json.dumps([x]))
                        elif col.lower() == "password":
                            df[col] = df[col].apply(PasswordUtils.hash_password)

                df.to_csv(csv_file, index=False, encoding="utf-8")
                print(f"Data written successfully to {csv_file}")
            else:
                print("No data provided. CSV file not created.")
            return csv_file
        except Exception as error:
            raise Exception(f"Error while saving data to {csv_file}: {error}")


# -----INITIALISE DATABASE--------
    def initialise(self, json_file: str) -> None:
        print("Initializing the database...")
        self._drop_all_the_tables()
        self.__create_schemes(json_file=EnvVariableUtil.get_env_variable('JSON_FILE_PATH'))
        self.__populate_with_values()

        print("Database initialized successfully.")

# ------CHECK IF TABLE EXIST---------
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


# ------LOAD/DELETE DATA WITH CONDITIONS------
    def _build_query(
            self,
            table_name: str,
            conditions: List[Tuple[str, Any]],
            operator: str,
            query_type: str = "SELECT"
    ) -> Tuple[str, List[Any]]:

        if operator not in ("AND", "OR"):
            raise ValueError("Operator must be 'AND' oder 'OR'.")

        if query_type not in ("SELECT", "DELETE"):
            raise ValueError("Just 'SELECT' und 'DELETE' are being used.")

        condition_string = f" {operator} ".join([f"{col} = %s" for col, _ in conditions])

        if query_type == "SELECT":
            query = f"SELECT * FROM {table_name} WHERE {condition_string};"
        elif query_type == "DELETE":
            query = f"DELETE FROM {table_name} WHERE {condition_string};"

        params = [value for _, value in conditions]

        return query, params


#-----GET COLUMN TYPES--------
    def _get_column_types(self, table_name: str) -> Dict[str, str]:
        query = f"""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = %s;
        """
        result = self.__execute_command(
            sql_query=query,
            params=(table_name,),
            fetch_one=False,
            fetch_all=True,
            log_message=f"Fetching column types for table {table_name}."
        )

        if not result:
            raise Exception(f"No columns found for table {table_name}")

        column_types = {row['column_name']: row['data_type'] for row in result}
        return column_types


#---EXECUTE COMMAND----
    def __execute_command(self, sql_query: str = None, params: tuple = None, fetch_one: bool = False, fetch_all: bool = False, log_message: str =None):
        try:
            self.cursor.execute(sql_query, params)
            if log_message:
                print(log_message)
            if fetch_one:
                return self.cursor.fetchone()
            if fetch_all:
                return self.cursor.fetchall()

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


#-------CREATES THE SCHEMES FOR THE DATABASE--------
    def __create_schemes(self, json_file):
        try:
            data = pd.read_json(json_file)
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
        columns = [desc[0] for desc in self.cursor.description]  # Get column names
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]  # Fetch all rows


# -------POPULATE WITH VALUES
    def __populate_with_values(self, csv_directory: str = None) -> None:
        csv_directory = csv_directory or EnvVariableUtil.get_env_variable('CSV_FILE_PATH')
        print("Populating tables with values from CSV files...")

        if not os.path.exists(csv_directory):
            raise FileNotFoundError(f"The directory '{csv_directory}' does not exist.")

        table_order = ["tokens", "users", "student", "tutor", "course", "studentincourse"]

        file_to_table_map = {
            os.path.splitext(file_name)[0]: os.path.join(csv_directory, file_name)
            for file_name in os.listdir(csv_directory)
            if file_name.lower().endswith('.csv')
        }

        for table_name in table_order:
            if table_name in file_to_table_map:
                file_path = file_to_table_map[table_name]

                try:
                    reader = pd.read_csv(file_path)
                    rows = reader.to_dict(orient='records')

                    if rows:
                        print(f"Inserting data into {table_name} from {os.path.basename(file_path)}...")
                        self.insert_many(table_name, rows, column='id', dublicate=False)
                    else:
                        print(f"No data found in {os.path.basename(file_path)}, skipping...")
                except Exception as e:
                    print(f"Error processing {os.path.basename(file_path)}: {e}")
            else:
                print(f"No data file found for table '{table_name}', skipping...")


    def __enter__(self):
        return self

    def __exit__(self):
        self.connection.close()