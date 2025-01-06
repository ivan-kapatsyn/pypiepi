import os
import unittest
from src.utils.data_base_util import DataBaseUtil
from src.utils.env_variable_util import EnvVariableUtil


class DataBaseUtilTestCase(unittest.TestCase):

    def setUp(self):
        self.db_util = DataBaseUtil()

    def test_if_exist(self):
        table_name = 'users'
        self.assertEqual(self.db_util._check_if_table_exists(
                table_name), True)

    def test_load_data(self):
        table_name = 'users'
        id_value = 202345673

        expected_result = [202345673, 'arthur_morgan', 'password123', 'student', True]
        self.assertEqual(self.db_util.load_one(table_name, id_value), expected_result)


    def test_delete_data(self):
        table_name = 'users'
        id_value = 202345673
        self.assertEqual(self.db_util.delete_one(table_name, id_value), None)


    def test_insert_data(self):
        obj1 = {
            "user_id": 202345671,
            "username": "arthur_morgan",
            "password": "password123",
            "user_typ": "student",
            "remember_me": "TRUE"}

        self.db_util.insert_one("users", obj1, column="user_id", dublicate=True)
        loaded_data = self.db_util.load_one("users",  202345671)
        self.assertEqual(loaded_data['user_id'], 202345671)
        self.assertEqual(loaded_data['username'], "arthur_morgan")
        self.assertEqual(loaded_data['password'], "password123")
        self.assertEqual(loaded_data['user_typ'], "student")
        self.assertEqual(loaded_data['remember_me'], True)


    def test_insert_many_data(self):
        objects = [
            {
                "user_id": 202345672,
                "username": "john_doe",
                "password": "newpassword",
                "user_typ": "admin",
                "remember_me": True
            },
            {
                "user_id": 202345671,
                "username": "arthur_morgan",
                "password": "password123",
                "user_typ": "student",
                "remember_me": True
             }
        ]
        self.db_util.insert_many("users", objects, column="user_id", dublicate=True)

        for obj in objects:
            loaded_data = self.db_util.load_one("users", obj["user_id"])
            self.assertEqual(loaded_data['user_id'], obj['user_id'])
            self.assertEqual(loaded_data['username'], obj['username'])
            self.assertEqual(loaded_data['password'], obj['password'])
            self.assertEqual(loaded_data['user_typ'], obj['user_typ'])
            self.assertEqual(loaded_data['remember_me'], obj['remember_me'])


    def test_build_query_select(self):
        table_name = "tmuser"
        conditions = [("user_typ", "admin"), ("remember_me", "TRUE")]
        operator = "AND"
        query_type = "SELECT"

        expected_query = "SELECT * FROM users WHERE user_typ = %s AND remember_me = %s;"
        expected_params = ["admin", "TRUE"]

        query, params = self.db_util._build_query(table_name, conditions, operator, query_type)

        self.assertEqual(query, expected_query)
        self.assertEqual(params, expected_params)


    def test_delete_many(self):
        # Test deleting multiple records
        table_name = 'users'
        column = "user_id"
        user_ids = [202345671, 202345672]

        # Überprüfen, ob die Benutzer vor dem Löschen existieren
        for user_id in user_ids:
            exists_before = self.db_util.exists_user_by_id(table_name, user_id)
            print(f"User {user_id} exists before deletion: {exists_before}")  # Debugging-Ausgabe

        # Führen Sie die Löschoperation durch
        self.db_util.delete_many(table_name, column, user_ids)

        # Überprüfen Sie die Existenz der Benutzer nach dem Löschen
        for user_id in user_ids:
            exists_after = self.db_util.exists_user_by_id(table_name, user_id)
            print(f"User {user_id} exists after deletion: {exists_after}")  # Debugging-Ausgabe
            self.assertFalse(exists_after, f"User {user_id} should have been deleted")

    def test_exist_user_id(self):
        user_id_to_test = 202345671
        expected_exists = False  # Setzen Sie dies auf True, wenn der Benutzer existieren soll

        # Überprüfen Sie, ob der Benutzer existiert
        exists = self.db_util.exists_user_by_id("users", user_id_to_test)
        print(f"User {user_id_to_test} exists: {exists}")  # Debug-Ausgabe

        # Assert, dass der Benutzer wie erwartet existiert oder nicht existiert
        self.assertEqual(exists, expected_exists, f"User {user_id_to_test} existence check failed")


    def test_update_one(self):
        table_name = 'users'
        column = "user_id"
        id_value = 202345676
        new_values = {"username": "arthur_updated", "remember_me": False}

        self.db_util.update_one(table_name, column, id_value, new_values)

    def test_initialise(self):
        data_path = EnvVariableUtil.get_env_variable('JSON_FILE_PATH')
        #print(f"JSON_FILE_PATH: {data_path}")  # Debug-Ausgabe
        self.db_util.initialise(json_file=data_path)


    def test_insert_with_duplicate_true(self):
        obj = {
                "user_id": 202345671,
                "username": "arthur_morgan",
                "password": "password123",
                "user_typ": "student",
                "remember_me": True
             }
        self.db_util.insert_one('users', obj, 'user_id', dublicate=True)
        # Verify the insertion logic, including checking for incremented keys.

    def test_insert_with_duplicate_false(self):
        obj = {
                "user_id": 202345671,
                "username": "arthur_morgan",
                "password": "password123",
                "user_typ": "student",
                "remember_me": True
             }
        self.db_util.insert_one('users', obj, 'user_id', dublicate=False)
        # Verify that the entry is present.

    def test_save_data_to_csv(self):
        data_users = [
            {"username": "arthur.morgan", "password": "password123", "first_name": "arthur", "last_name": "morgan",
             "bio": "", "remember_me": "TRUE"},
            {"username": "john.doe", "password": "newpassword", "first_name": "john", "last_name": "doe", "bio": "Shrek is love. Shrek is live",
             "remember_me": "TRUE"},
            {"username": "jane.doe", "password": "mypassword", "first_name": "jane", "last_name": "doe", "bio": "Professional construction enthusiast",
             "remember_me": "FALSE"},
            {"username": "john.marston", "password": "mypasswordisbetter", "first_name": "john", "last_name": "marston",
             "bio": "","remember_me": "FALSE"},
            {"username": "mary.stuart", "password": "stupidpassword", "first_name": "mary", "last_name": "stuart", "bio": "Am I a pretty girl?",
             "remember_me": "TRUE"},
        ]
        for entry in data_users:
            entry["user_id"] = self.db_util.generate_unique_id()
        table_name = "users"
        csv_directory = EnvVariableUtil.get_env_variable('CSV_FILE_PATH')

        try:
            column_types = self.db_util._get_column_types(table_name)
            file_path = self.db_util.save_data_to_csv(table_name=table_name, data=data_users, csv_directory=csv_directory, column_types=column_types)
            assert os.path.exists(file_path), f"CSV file not created at {file_path}"
            print("CSV file saved successfully and test passed.")
        except Exception as e:
            self.fail(f"Test failed: {e}")


if __name__ == '__main__':
    unittest.main()
