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
    def insert_one(self, table_name: str, obj: Dict[str, any], column: str, dublicate: bool = False, create_id: bool = True) -> None:
        """
        Inserts a single record into the specified table.

        Parameters:
        - table_name (str): The name of the table where the record will be inserted.
        - obj (Dict[str, any]): A dictionary representing the record to be inserted, where keys are column names.
        - column (str): The name of the column used to check for duplicates.
        - dublicate (bool): Indicates whether to allow duplicate entries. Defaults to False.

        Returns:
        - None: This method does not return a value.
        """
        print(f"Inserting in table {table_name}")

        obj = {
            key: json.dumps(value) if isinstance(value, (list, dict)) else value
            for key, value in obj.items()
        }

        if "password" in obj:
            obj["password"] = PasswordUtils.hash_password(obj["password"])

        columns = ', '.join(obj.keys())
        values_placeholder = ', '.join(['%s'] * len(obj))
        query = f'INSERT INTO {table_name} ({columns}) VALUES ({values_placeholder});'

        if dublicate:
            initial_key_value = obj[column]
            while True:
                query_check = f'SELECT EXISTS(SELECT * FROM {table_name} WHERE {column} = %s);'
                self.__execute_command(query_check, (initial_key_value,))
                exists = self.cursor.fetchone()[0]

                if not exists:
                    break

                if create_id:
                    initial_key_value = self.generate_unique_id()
                    obj[column] = initial_key_value
                    print(f"Updated object key: {obj[column]}")

        else:
            query_check = f'SELECT EXISTS(SELECT * FROM {table_name} WHERE {column} = %s);'
            self.__execute_command(query_check, (obj[column],))
            exists = self.cursor.fetchone()[0]

            if exists:
                raise Exception(f"Duplicate entry for {column}: {obj[column]}")

        self.__execute_command(sql_query=query, params=tuple(obj.values()))
        print(f"Inserted {obj} into {table_name}")


# ------INSERT MANY TO THE DATABASE--------
    def insert_many(self, table_name: str, objects: List[Dict[str, any]], column: str,
                    dublicate: bool = False, create_id: bool = True, create_password: bool = True) -> None:
        """
        Inserts multiple records into the specified table.

        Parameters:
        - table_name (str): The name of the table where multiple records will be inserted.
        - objects (List[Dict[str, any]]): A list of dictionaries, each representing a record to be inserted.
        - column (str): The name of the column used to check for duplicates.
        - dublicate (bool): Indicates whether to allow duplicate entries during insertion. Defaults to False.

        Returns:
        - None: This method does not return a value.
        """
        if not objects:
            print("No objects to insert.")
            return

        print(f"Inserting into {table_name}...")

        for obj in objects:
            if "password" in obj:
                if create_password:
                    obj["password"] = PasswordUtils.hash_password(obj["password"])
            for key, value in obj.items():
                if isinstance(value, (list, dict)):
                    obj[key] = json.dumps(value)

        if dublicate:
            existing_keys_query = f"SELECT {column} FROM {table_name} WHERE {column} IN %s;"
            existing_keys = set()

            keys_to_check = [obj[column] for obj in objects]
            self.__execute_command(existing_keys_query, (tuple(keys_to_check),))
            for row in self.cursor.fetchall():
                existing_keys.add(row[0])

            for obj in objects:
                while obj.get(column) in existing_keys:
                    if create_id:
                        obj[column] = self.generate_unique_id()
                existing_keys.add(obj[column])

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
        query = f"SELECT EXISTS(SELECT * FROM {table_name} WHERE user_id = %s);"
        result = self.__fetch_one(query, (user_id,))
        print(f"Checking existence for user_id {user_id}: result = {result}")
        return result[0] if result else False


# -------LOAD ONE------
    def load_one(self, table_name: str, column: str, value:any) -> DictRow | None:
        """
            Loads a single record from the specified table based on a given column and value.

            Parameters:
            - table_name (str): The name of the table from which to load the record.
            - column (str): The name of the column used to filter the records. Must be a valid identifier.
            - value (any): The value to match in the specified column. The type should correspond to the column's data type.

            Returns:
            - DictRow | None: A dictionary representing the record if found, or None if no record matches the criteria.

            Raises:
            - ValueError: If the provided column name is not a valid identifier.
            - TypeError: If the qualification field in the result has an unexpected type.
        """
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
        """
        Loads multiple records from the specified table, optionally filtered by a condition.

        Parameters:
        - table_name (str): The name of the table from which to load records.
        - filter_function (str, optional): An optional SQL filter string to apply to the query. If provided, must be a valid SQL condition.
        - values (List[Any], optional): A list of values to bind to the filter function placeholders, if any.

        Returns:
        - List[Dict[str, Any]]: A list of dictionaries representing the records loaded from the table.
                                 Each dictionary corresponds to a record, or an empty list if no records are found.

        Raises:
        - Exception: If an error occurs during the query execution.
        """
        if values and filter_function or filter_function:
            query = f'SELECT * FROM {table_name} WHERE {filter_function};'
            params = tuple(values)
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

        if results:
            print(f"Successfully loaded {len(results)} records from {table_name}.")
            return results
        else:
            print(f"Error during batch load in {table_name}.")
            return []


# -----DELETE ONE WITH ID---------
    def delete_one_with_id(self, table_name: str, id_value: Any) -> None:
        """
        Deletes a single record from the specified table using its primary key.

        Parameters:
        - table_name (str): The name of the table from which to delete the record.
        - id_value (any): The value of the primary key to identify the record to be deleted.
                          The type should correspond to the primary key's data type.

        Returns:
        - None: This method does not return a value.

        Raises:
        - Exception: If an error occurs during the deletion process.
        """
        id_column = self.get_primary_key_column(table_name)

        query = f"DELETE FROM {table_name} WHERE {id_column} = %s;"
        self.__execute_command(query, (id_value, ))
        print(f"Deleted record from {table_name} where {id_column} = {id_value}.")


# -----DELETE ONE---------
    def delete_one(self, table_name: str, column: str, value: Any) -> None:
        """
        Deletes a single record from the specified table based on a given column and value.

        Parameters:
        - table_name (str): The name of the table from which to delete the record.
        - column (str): The name of the column used to filter the records. Must be a valid identifier.
        - value (any): The value to match in the specified column. The type should correspond to the column's data type.

        Returns:
        - None: This method does not return a value.

        Raises:
        - ValueError: If the provided column name is not a valid identifier.
        """
        if not column.isidentifier():
            raise ValueError(f"Invalid column name: {column}")

        query = f"DELETE FROM {table_name} WHERE {column} = %s;"
        self.__execute_command(query, (value,))
        print(f"Deleted record from {table_name} where {column} = {value}.")


# ------DELETE MANY DATA--------
    def delete_many(self, table_name: str, column: str, values: List[Any]) -> None:
        """
        Deletes multiple records from the specified table based on the given column and a list of values.

        Parameters:
        - table_name (str): The name of the table from which to delete records.
        - column (str): The name of the column used as the filter criterion for deletion.
        - values (List[Any]): A list of values to match against the specified column.
                              Only records with a column value that matches any value in this list will be deleted.

        Returns:
        - None: This method does not return a value.

        Raises:
        - Exception: If an error occurs during the deletion process.
        """
        if not values:
            print("No values to delete.")
            return

        placeholders = ', '.join(['%s'] * len(values))
        query = f"DELETE FROM {table_name} WHERE {column} IN ({placeholders});"

        print(f"Deleting {len(values)} records from {table_name} where {column} matches.")
        self.__execute_command(sql_query=query, params=tuple(values))
        print(f"Successfully deleted {len(values)} records from {table_name}.")


#-------UPDATE ONE-----
    def update_one(self, table_name: str, id_column: str, id_value: Any, new_values: Dict[str, Any]) -> None:
        """
        Updates a single record in the specified table based on the primary key.

        Parameters:
        - table_name (str): The name of the table in which the record will be updated.
        - id_column (str): The name of the column used as the primary key to identify the record.
        - id_value (any): The value of the primary key to match the record that needs to be updated.
        - new_values (Dict[str, Any]): A dictionary of new values to be set for the record.
                                        Keys represent column names and values represent the new data.

        Returns:
        - None: This method does not return a value.

        Raises:
        - Exception: If an error occurs during the update process.
        """
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
        """
        Updates multiple records in the specified table based on a list of conditions and corresponding new values.

        Parameters:
        - table_name (str): The name of the table in which the records will be updated.
        - conditions (List[Dict[str, Any]]): A list of dictionaries where each dictionary represents the conditions
                                               to match for each record. Each key corresponds to a column name.
        - new_values (List[Dict[str, Any]]): A list of dictionaries containing new values for each record.
                                              Each dictionary's keys represent the column names to be updated.

        Returns:
        - None: This method does not return a value.

        Raises:
        - Exception: If an error occurs during the update process.
        """
        if not new_values:
            print("No updates provided.")
            return

        for condition, new_value in zip(conditions, new_values):
            where_clause = ' AND '.join([f"{key} = %s" for key in condition.keys()])
            set_clause = ', '.join([f"{key} = %s" for key in new_value.keys()])
            query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause};"

            params = tuple(new_value.values()) + tuple(condition.values())
            print(f"Executing update query: {query} with params: {params}")

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
    def save_data_to_csv(self, table_name: str, data: List[Dict[str, Any]], column_types: Dict[str, str]) -> str:
        """
        Saves data from the specified table into a CSV file.

        Parameters:
        - table_name (str): The name of the table from which the data is extracted. This will also be used as the CSV file name.
        - data (List[Dict[str, Any]]): A list of dictionaries where each dictionary represents a row of data.
                                        Keys correspond to column names.
        - column_types (Dict[str, str]): A dictionary specifying the data types of the columns. Keys are column names
                                           and values are the data types (e.g., 'jsonb', 'password').
        - csv_directory (str, optional): The directory where the CSV file will be saved. If not provided, it retrieves
                                          the directory from environment variables.

        Returns:
        - str: The path to the created CSV file.

        Raises:
        - Exception: If an error occurs during the saving process or if the data is not provided.
        """
        #EnvVariableUtil.get_env_variable('CSV_FILE_PATH') csv_directory or
        csv_directory = PathUtil.get_data_path()
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
    def initialise(self) -> None:
        """
        Initializes the database by dropping existing tables, creating new schemas,
        and populating them with initial values.

        Parameters:
        - json_file (str): The path to the JSON file used for creating schemas and populating initial values.

        Returns:
        - None: This method does not return a value.

        Raises:
        - Exception: If an error occurs during the initialization process.
        """
        print("Initializing the database...")
        self._drop_all_the_tables()
        self.__create_schemes(json_file=PathUtil.get_json_path())
        self.__populate_with_values()

        print("Database initialized successfully.")

# ------CHECK IF TABLE EXIST---------
    def _check_if_table_exists(self, table_name) -> bool:
        """
        Checks whether a specified table exists in the database.

        Parameters:
        - table_name (str): The name of the table to check for existence.

        Returns:
        - bool: True if the table exists, False otherwise.

        Raises:
        - Exception: If an error occurs while executing the existence check query.
        """
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
        """
        Drops all tables in the public schema of the database and recreates the schema.

        Returns:
        - bool: True if the operation was successful, False otherwise.

        Raises:
        - Exception: If an error occurs while dropping the tables.
        """
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
    def _build_query(self, table_name: str, conditions: List[Tuple[str, Any]], operator: str, query_type: str = "SELECT") -> Tuple[str, List[Any]]:
        """
        Constructs a SQL query based on specified conditions and the desired query type (SELECT or DELETE).

        Parameters:
        - table_name (str): The name of the table on which the query will be executed.
        - conditions (List[Tuple[str, Any]]): A list of tuples where each tuple contains a column name and its corresponding value to filter the records.
        - operator (str): The logical operator ('AND' or 'OR') used to combine conditions in the query.
        - query_type (str): The type of query to construct ('SELECT' or 'DELETE'). Defaults to 'SELECT'.

        Returns:
        - Tuple[str, List[Any]]: A tuple containing the constructed SQL query string and a list of parameter values.

        Raises:
        - ValueError: If the operator is not 'AND' or 'OR'.
        - ValueError: If the query type is not 'SELECT' or 'DELETE'.
        """
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
        """
        Retrieves the data types of columns for a specified table.

        Parameters:
        - table_name (str): The name of the table for which to fetch column types.

        Returns:
        - Dict[str, str]: A dictionary where keys are column names and values are their corresponding data types.

        Raises:
        - Exception: If no columns are found for the specified table.
        """
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
    def __execute_command(self, sql_query: str = None, params: tuple = None, fetch_one: bool = False, fetch_all: bool = False, log_message: str = None):
        """
        Executes a given SQL command with optional parameters and fetch options.

        Parameters:
        - sql_query (str, optional): The SQL query to be executed. Defaults to None.
        - params (tuple, optional): A tuple of parameters to be used in the SQL query. Defaults to None.
        - fetch_one (bool, optional): If True, fetches a single result. Defaults to False.
        - fetch_all (bool, optional): If True, fetches all results. Defaults to False.
        - log_message (str, optional): An optional message to log during execution.

        Returns:
        - Any: The fetched result if fetch_one or fetch_all is True, otherwise returns True upon successful execution.

        Raises:
        - Exception: If an error occurs during the execution of the command.
        """
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
        """
        Creates a new database user with the specified username and password.

        Parameters:
        - username (str): The username for the new database user.
        - password (str): The password for the new database user.

        Returns:
        - bool: True if the user was created successfully, otherwise False.
        """
        create_user_query = f"CREATE USER {username} WITH PASSWORD '{password}';"
        return self.__execute_command(
            sql_query=create_user_query,
            params=(username, password),
            log_message=f"User '{username}' was created.")


#-------GIVING THE USER ALL PRIVILEGES--------
    def __grant_all_privileges(self, username, dbname):
        """
        Grants all privileges on a specified database to a given user.

        Parameters:
        - username (str): The username of the user to whom the privileges will be granted.
        - dbname (str): The name of the database on which privileges are to be granted.

        Returns:
        - bool: True if privileges were granted successfully, otherwise False.
        """
        grant_privileges_query = f"GRANT ALL PRIVILEGES ON DATABASE {dbname} TO {username};"
        return self.__execute_command(
            sql_query=grant_privileges_query,
            params=(username, dbname),
            log_message=f"Grant all privileges on database '{dbname}' to '{username}'."
        )


#-------CREATES THE SCHEMES FOR THE DATABASE--------
    def __create_schemes(self, json_file):
        """
        Creates database schemas and tables based on the definitions provided in a JSON file.

        Parameters:
        - json_file (str): The path to the JSON file containing table and column definitions.

        Returns:
        - bool: True if all tables were created successfully, otherwise False.

        Raises:
        - ValueError: If any required fields (such as table name or column definitions) are missing in the JSON file.
        - Exception: If there is an error during the creation of the database schema.
        """
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

                    if "FOREIGN KEY" in constraints:
                        foreign_keys.append(
                            f"FOREIGN KEY ({column_name}) {constraints.split('FOREIGN KEY')[1].strip()}")
                        constraints = ""

                    column_definition = f"{column_name} {data_type} {constraints}".strip()
                    column_definitions.append(column_definition)

                create_table_script = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_definitions)}"

                if foreign_keys:
                    create_table_script += f", {', '.join(foreign_keys)}"

                create_table_script += ");"

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
        """
        Executes a query and fetches a single record from the database.

        Parameters:
        - query (str): The SQL query to be executed.
        - params (Tuple[Any, ...], optional): A tuple of parameters to be used in the SQL query. Defaults to an empty tuple.

        Returns:
        - Union[DictRow, None]: A dictionary representing the record if found, or None if no record matches the criteria.
        """
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
        """
        Executes a query and fetches all matching records from the database.

        Parameters:
        - query (str): The SQL query to be executed.
        - params (Tuple[Any, ...], optional): A tuple of parameters to be used in the SQL query. Defaults to an empty tuple.

        Returns:
        - List[Dict[str, Any]]: A list of dictionaries, where each dictionary represents a record retrieved from the database.
        """
        self.__execute_command(sql_query=query, params=params)
        columns = [desc[0] for desc in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]


# -------POPULATE WITH VALUES
    def __populate_with_values(self) -> None:
        """
        Populates database tables with values from CSV files located in the specified directory.

        Parameters:
        - csv_directory (str, optional): The path to the directory containing CSV files. If not provided, the path will be retrieved from an environment variable.

        Returns:
        - None

        Raises:
        - FileNotFoundError: If the specified CSV directory does not exist.
        - Exception: If there is an error while processing any CSV file.

        Notes:
        The method processes predefined tables in a specific order and attempts to insert data into them. If a table does not have a corresponding CSV file, it is skipped.
        """
        csv_directory = PathUtil.get_data_path()
        print("Populating tables with values from CSV files...")

        if not os.path.exists(csv_directory):
            raise FileNotFoundError(f"The directory '{csv_directory}' does not exist.")

        table_order = ["tokens", "users", "student", "tutor", "room", "course", "announcement", "studentincourse"]

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
                        self.insert_many(table_name, rows, column='id', dublicate=False, create_id=False, create_password=False)
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