import json  # Import json for handling JSON data
import os # Import os for operating system functionalities
import secrets  # import for generating secure random numbers
from typing import Any, Dict, List, Tuple
import pandas as pd  # Import pandas for data manipulation and analysis
import psycopg2  # Import psycopg2 for PostgreSQL database interaction
import psycopg2.extras  # Import extras for additional features in psycopg2
from psycopg2.extras import DictRow
from src.utils.env_variable_util import EnvVariableUtil # Import EnvVariableUtil for environment variable management
from src.utils.password_utils import PasswordUtils  # Import PasswordUtils for password hashing utilities
from src.utils.path_util import PathUtil  # Import PathUtil for path utilities


# -----------------------------------
class DataBaseUtil:
    """
    Utility class for interacting with a PostgreSQL database.
    It provides methods for inserting, retrieving, and deleting records.
    """
    def __init__(self):
        """
        Initializes the database connection.

        Parameters:
        - connection parameters (database name, user, password, host, and port): retrieved from environment variables using EnvVariableUtil.

        Attributes:
        - connection (psycopg2.extensions.connection or None): Stores the database connection object.
        - cursor (psycopg2.extras.DictCursor or None): Stores the database cursor object.

        Raises:
        - Exception: if the connection fails, an error message is printed.
        """
        self.__connection = None
        self.cursor = None

        # ------CONNECTION TO THE DATABASE----------
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
        """
        Closes the database connection and cursor when the object is deleted.
        """
        # Check if the cursor is not None
        if self.cursor is not None:
            self.cursor.close()
        # Check if the connection is not None
        if self.__connection is not None:
            self.__connection.close()

    # --------GENERATE UNIQUE ID-------
    def generate_unique_id(self) -> str:
        """
        Generates a secure random unique ID.

        Returns:
        - str: A 16-character hexadecimal string.
        """

        return secrets.token_hex(8)  # Return a secure random hexadecimal string of length 16

    # ------INSERT ONE TO THE DATABASE--------
    def insert_one(self, table_name: str, obj: Dict[str, any], column: str, dublicate: bool = False,
                   create_id: bool = True) -> None:
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

        columns = ', '.join(obj.keys())  # Create a comma-separated string of column names
        values_placeholder = ', '.join(['%s'] * len(obj))  # Create a placeholder string for values
        query = f'INSERT INTO {table_name} ({columns}) VALUES ({values_placeholder});'

        if dublicate:  # Check if duplicates are allowed
            initial_key_value = obj[column]  # Store the initial value of the column to check for duplicates
            while True:
                query_check = f'SELECT EXISTS(SELECT * FROM {table_name} WHERE {column} = %s);'
                self.__execute_command(query_check, (initial_key_value,))
                exists = self.cursor.fetchone()[0]  # Fetch the result to see if the entry exists

                if not exists:
                    break

                if create_id:  # If new IDs should be created
                    initial_key_value = self.generate_unique_id()
                    obj[column] = initial_key_value  # Update the object with the new ID
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
        if not objects:  # Check if the list of objects is empty
            print("No objects to insert.")
            return

        print(f"Inserting into {table_name}...")

        for obj in objects:  # Iterate over each object in the list
            if "password" in obj:  # Check if the password key is in the object
                if create_password:
                    obj["password"] = PasswordUtils.hash_password(obj["password"])
            for key, value in obj.items():  # Iterate over each key-value pair in the object
                if isinstance(value, (list, dict)):  # Check if the value is a list or dictionary
                    obj[key] = json.dumps(value)  # Convert the value to a JSON string

        if dublicate:  # Check if duplicates are allowed
            existing_keys_query = f"SELECT {column} FROM {table_name} WHERE {column} IN %s;"
            existing_keys = set()  # Initialize a set to store existing keys

            keys_to_check = [obj[column] for obj in objects]  # Create a list of keys to check for duplicates
            self.__execute_command(existing_keys_query, (tuple(keys_to_check),))
            for row in self.cursor.fetchall():
                existing_keys.add(row[0])

            for obj in objects:
                while obj.get(column) in existing_keys:  # Check if the object's key is in the existing keys
                    if create_id:
                        obj[column] = self.generate_unique_id()
                existing_keys.add(obj[column])

        columns = ', '.join(objects[0].keys())  # Create a comma-separated string of column names from the first object
        values_placeholder = ', '.join(['%s'] * len(objects[0]))  # Create a placeholder string for values
        query = f"INSERT INTO {table_name} ({columns}) VALUES {', '.join(['(' + values_placeholder + ')' for _ in objects])};"
        values = tuple(value for obj in objects for value in
                       obj.values())  # Flatten the list of values from all objects into a single tuple

        try:
            self.__execute_command(sql_query=query, params=values)
            print(f"Inserted {len(objects)} records into {table_name}.")
        except Exception as e:
            print(f"Error during batch insert into {table_name}: {e}")

    # -------GET PRIMARY KEY-----------
    def get_primary_key_column(self, table_name: str) -> str:
        """
        Retrieves the primary key column of a given table.

        Parameters:
        - table_name (str): The name of the table.

        Returns:
        - str: The name of the primary key column.

        Raises:
        - Exception: If no primary key column is found.
        """
        query = f"SELECT a.attname FROM pg_index i JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey) WHERE i.indrelid = %s::regclass AND i.indisprimary;"  # Create a query to find the primary key column
        primary_key_column = self.__execute_command(query, (table_name,), fetch_one=True)
        if primary_key_column is None:
            raise Exception(f"No primary key column for {table_name}")
        return primary_key_column[0]

    # --------EXIST USER BY ID---------
    def exists_user_by_id(self, table_name: str, user_id: Any) -> bool:
        """
        Checks if a user exists in the specified table by user ID.

        Parameters:
        - table_name (str): The name of the table.
        - user_id (Any): The user ID to check.

        Returns:
        - bool: True if the user exists, False otherwise.
        """
        query = f"SELECT EXISTS(SELECT * FROM {table_name} WHERE user_id = %s);"  # Create a query to check for the existence of a user
        result = self.__fetch_one(query, (user_id,))
        print(f"Checking existence for user_id {user_id}: result = {result}")
        return result[0] if result else False  # Return True if the user exists, otherwise return False

    # -------LOAD ONE------
    def load_one(self, table_name: str, column: str, value: any) -> DictRow | None:
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
        if not column.isidentifier():  # Check if the column name is a valid identifier
            raise ValueError(f"Invalid column name: {column}")

        query = f'SELECT * FROM {table_name} WHERE {column} = %s;'
        result_load = self.__fetch_one(query, (value,))  # Execute the query and fetch the result

        if result_load is None:  # Check if no record was found
            print(f"No entry found where {column} = {value}.")
            return None

        if "qualification" in result_load and result_load["qualification"] is not None:  # Check if the qualification field exists and is not None
            if isinstance(result_load["qualification"], str):  # If qualification is a string
                result_load["qualification"] = json.loads(result_load["qualification"])
            elif isinstance(result_load["qualification"], list):  # If qualification is already a list
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
        if values and filter_function or filter_function:  # Check if filter_function is provided and has values
            query = f'SELECT * FROM {table_name} WHERE {filter_function};'
            params = tuple(values)  # Create a tuple of values for the query parameters
        else:  # If no filter is provided
            query = f'SELECT * FROM {table_name};'
            params = ()

        print(f"Executing query: {query} with values: {values}")

        results = self.__execute_command(  # Execute the command to fetch records
            sql_query=query,
            params=params,
            fetch_one=False,
            fetch_all=True,  # Indicate that we want to fetch all matching records
            log_message=f"Loading records from {table_name} with filter {filter_function}."
        )

        if results:  # Check if any results were returned
            print(f"Successfully loaded {len(results)} records from {table_name}.")
        else:  # If no results were found
            print(f"No records could be found in {table_name}.")
            return []

        return results

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
        id_column = self.get_primary_key_column(table_name)  # Get the primary key column for the specified table

        query = f"DELETE FROM {table_name} WHERE {id_column} = %s;"
        self.__execute_command(query, (id_value,))
        print(f"Deleted record from {table_name} where {id_column} = {id_value}.")

    # -----DELETE ONE---------
    def delete_one(self, table_name: str, column: str, value: Any) -> None:
        """
        Deletes a single record from the specified table based on a given column and value.

        Parameters:
        - table_name (str): The name of the table from which to delete the record.
        - column (str): The name of the column used to filter the records. Must be a valid identifier.
        - value (any): The value to match in the specified column. The type should correspond to the column's data type.

        Raises:
        - ValueError: If the provided column name is not a valid identifier.
        """
        if not column.isidentifier():  # Check if the column name is a valid identifier
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

        Raises:
        - Exception: If an error occurs during the deletion process.
        """
        if not values:  # Check if the list of values is empty
            print("No values to delete.")
            return

        placeholders = ', '.join(['%s'] * len(values))  # Create a placeholder string for the values
        query = f"DELETE FROM {table_name} WHERE {column} IN ({placeholders});"

        print(f"Deleting {len(values)} records from {table_name} where {column} matches.")
        self.__execute_command(sql_query=query, params=tuple(values))
        print(f"Successfully deleted {len(values)} records from {table_name}.")

    # -------UPDATE ONE DATA-----
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
        if not new_values:  # Check if there are no new values to update
            print("No new values to update.")
            return

        set_clause = ', '.join(
            f"{key} = %s" for key in new_values.keys())  # Create a SET clause for the SQL update query
        query = f"UPDATE {table_name} SET {set_clause} WHERE {id_column} = %s;"

        params = tuple(new_values.values()) + (id_value,)  # Create a tuple of new values and the primary key value
        print(f"Executing update query: {query} with params: {new_values}")

        affected_rows = self.__execute_command(
            sql_query=query,
            params=params,
            fetch_one=False,
            fetch_all=False,
            log_message=f"Updating row in {table_name} where {id_column} = {id_value}."
        )
        if affected_rows == 0:  # Check if no rows were affected by the update
            print(f"No entry found where {id_column} = {id_value}.")

        print(f"Succesfully updated where {id_column} = {id_value} from {table_name}.")

    # -------UPDATE MANY DATA--------
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
        if not new_values:  # Check if there are no new values to update
            print("No updates provided.")
            return

        for condition, new_value in zip(conditions, new_values):  # Iterate over pairs of conditions and new values
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

            if affected_rows == 0:  # Check if no rows were affected by the update
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
        csv_directory = PathUtil.get_data_path()  # Get the directory path for saving CSV files
        if not os.path.exists(csv_directory):  # Check if the directory does not exist
            os.makedirs(csv_directory)  # Create the directory if it does not exist
        csv_file = os.path.join(csv_directory, f"{table_name}.csv")  # Create the full path for the CSV file

        try:
            if data:  # Check if there is data to save
                df = pd.DataFrame(data)  # Convert the list of dictionaries
                for col, col_type in column_types.items():
                    if col in df.columns:  # Check if the column exists in the DataFrame
                        if col_type.lower() == 'jsonb':  # If the column type is 'jsonb'
                            df[col] = df[col].apply(
                                lambda x: json.dumps(x) if isinstance(x, (list, dict)) else json.dumps(
                                    [x]))  # Convert lists and dicts to JSON strings
                        elif col.lower() == "password":  # If the column type is 'password'
                            df[col] = df[col].apply(PasswordUtils.hash_password)

                df.to_csv(csv_file, index=False,
                          encoding="utf-8")  # Save the DataFrame to a CSV file without the index, index=False indicates to not write the index in the CSV-File
                print(f"Data written successfully to {csv_file}")
            else:  # If no data is provided
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
        return result_dropping is None  # Return True if the operation was successful (result_dropping is None)

    # ------LOAD/DELETE DATA WITH CONDITIONS------
    def _build_query(self, table_name: str, conditions: List[Tuple[str, Any]], operator: str,
                     query_type: str = "SELECT") -> Tuple[str, List[Any]]:
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
        if operator not in ("AND", "OR"):  # Check if the operator is valid
            raise ValueError("Operator must be 'AND' oder 'OR'.")

        if query_type not in ("SELECT", "DELETE"):  # Check if the operator is valid
            raise ValueError("Just 'SELECT' und 'DELETE' are being used.")

        condition_string = f" {operator} ".join(
            [f"{col} = %s" for col, _ in conditions])  # Construct the condition string for the query

        if query_type == "SELECT":
            query = f"SELECT * FROM {table_name} WHERE {condition_string};"
        elif query_type == "DELETE":
            query = f"DELETE FROM {table_name} WHERE {condition_string};"

        params = [value for _, value in conditions]

        return query, params  # Return the constructed query and the list of parameters

    # -----GET COLUMN TYPES--------
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
            fetch_all=True,  # Fetch all results
            log_message=f"Fetching column types for table {table_name}."
        )

        if not result:  # Check if no results were returned
            raise Exception(f"No columns found for table {table_name}")

        column_types = {row['column_name']: row['data_type'] for row in result}
        return column_types

    # ---EXECUTE COMMAND----
    def __execute_command(self, sql_query: str = None, params: tuple = None, fetch_one: bool = False,
                          fetch_all: bool = False, log_message: str = None):
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

            self.connection.commit()  # Commit the transaction if no results are being fetched
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

    # -------GIVING THE USER ALL PRIVILEGES--------
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

    # -------CREATES THE SCHEMES FOR THE DATABASE--------
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
            data = pd.read_json(json_file)  # Read the JSON file
            tables = data.get("tables", [])  # Get the list of tables
            for table in tables:
                table_name = table.get("table_name")  # Get the table name
                if not table_name:  # Check if the table name is missing
                    raise ValueError("Mising table name in the JSON file.")

                columns = table.get("columns", [])  # Get the list of columns for the table
                if not columns:  # Check if no columns are defined
                    raise ValueError(f"No rows defined at the table {table_name}.")

                column_definitions = []  # Initialize a list to hold column definitions
                foreign_keys = []  # Initialize a list to hold foreign key definitions

                for column in columns:
                    column_name = column.get("column_name")  # Get the column name
                    data_type = column.get("data_type")  # Get the data type of the column
                    constraints = column.get("constraints", "")  # Get any constraints for the column

                    if not column_name or not data_type:  # Check if the column name or data type is missing
                        raise ValueError(f"Missing column definition in the table {table_name}: {column}")

                    column_name = str(column_name).strip()  # Strip whitespace from the column name
                    data_type = str(data_type).strip()  # Strip whitespace from the data type
                    constraints = str(constraints).strip()  # Strip whitespace from the constraints

                    if "FOREIGN KEY" in constraints:  # Check if the constraints include a foreign key
                        foreign_keys.append(  # Add the foreign key definition to the list
                            f"FOREIGN KEY ({column_name}) {constraints.split('FOREIGN KEY')[1].strip()}")
                        constraints = ""

                    column_definition = f"{column_name} {data_type} {constraints}".strip()
                    column_definitions.append(column_definition)

                create_table_script = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_definitions)}"  # Start creating the SQL script for the table

                if foreign_keys:  # If there are foreign keys defined
                    create_table_script += f", {', '.join(foreign_keys)}"  # Add the foreign key definitions to the script

                create_table_script += ");"  # Close the CREATE TABLE statement

                print(f"Create Table {table_name}")
                print(create_table_script)

                self.cursor.execute(create_table_script)  # Execute the SQL script to create the table

            self.cursor.connection.commit()  # Commit the transaction to save the changes
            print("All tables were created successfully.")

        except Exception as error:
            print(f"Error by creating the database scheme: {error}")
            return False

    # ------FETCH ONE--------
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
        if result_fetch_one is True:  # Check if the result indicates no record was found
            return None  # Return None if no record matches
        return result_fetch_one  # Return the fetched record

    # ------FETCH MANY-------
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
        columns = [desc[0] for desc in self.cursor.description]  # Get the column names from the cursor description
        return [dict(zip(columns, row)) for row in
                self.cursor.fetchall()]  # Fetch all rows and return them as a list of dictionaries

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
        csv_directory = PathUtil.get_data_path()  # Get the path to the directory containing CSV files
        print("Populating tables with values from CSV files...")

        if not os.path.exists(csv_directory):  # Check if the specified directory exists
            raise FileNotFoundError(f"The directory '{csv_directory}' does not exist.")

        table_order = ["tokens", "room", "users", "student", "tutor", "admin", "course", "student_in_course",
                       "announcement", "evaluation"]  # Define the order in which tables will be populated

        file_to_table_map = {  # Create a mapping of table names to their corresponding CSV file paths
            os.path.splitext(file_name)[0]: os.path.join(csv_directory, file_name)
            # Map the table name (without extension) to the full file path
            for file_name in os.listdir(csv_directory)
            if file_name.lower().endswith('.csv')  # Filter for files that end with .csv
        }

        for table_name in table_order:
            if table_name in file_to_table_map:  # Check if a CSV file exists for the current table
                file_path = file_to_table_map[table_name]  # Get the file path for the current table

                try:
                    reader = pd.read_csv(file_path)  # Read the CSV file
                    rows = reader.to_dict(orient='records')  # Convert the DataFrame to a list of dictionaries

                    if rows:  # Check if there are any rows to insert
                        print(f"Inserting data into {table_name} from {os.path.basename(file_path)}...")
                        self.insert_many(table_name, rows, column='id', dublicate=False, create_id=False,
                                         create_password=False)
                    else:
                        print(f"No data found in {os.path.basename(file_path)}, skipping...")
                except Exception as e:
                    print(f"Error processing {os.path.basename(file_path)}: {e}")
            else:
                print(f"No data file found for table '{table_name}', skipping...")

    def __enter__(self):  # Method to support context management (entering the context)
        return self

    def __exit__(self):  # Method to support context management (exiting the context)
        self.connection.close()
