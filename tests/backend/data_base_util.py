import os
import unittest
from pandas.core.interchange import column
from src.utils.data_base_util import DataBaseUtil
from src.utils.env_variable_util import EnvVariableUtil
from src.utils.path_util import PathUtil


class DataBaseUtilTestCase(unittest.TestCase):

    def setUp(self):
        self.db_util = DataBaseUtil()

#WORK
    def test_initialise(self):
        self.db_util.initialise()

#WORKS
    def test_if_exist(self):
        table_name = 'users'
        self.assertEqual(self.db_util._check_if_table_exists(
                table_name), True)

#WORK
    def test_load_one(self):
        table_name = 'users'
        column = "user_id"
        id_value = "a70030991cfada5a"

        expected_result = ["a70030991cfada5a", "arthur.morgan",
                           "JDJiJDEyJHBmbnhZcFdYa1JlTWNjalUyUFFVTC41YzhhYnBmSEdPbFlDS0JUOWdLeUxtdE1XWXJIZTFL",
                           "arthur", "morgan", "NaN",True]
        self.assertEqual(self.db_util.load_one(table_name, column,id_value), expected_result)

#WORK
    def test_load_many(self):
        table_name = 'users'
        filter_function = "first_name = %s"
        user_first_name = ["john"]

        expected_result = [
            [
                "299edbe2695a53ed",
                "john.doe",
                "JDJiJDEyJHN2VTNhcUhDbXBzZkExenhvakNFdnVhcjZsOHJXdkJLNjFNSWx0cnJtR3IuakU1MWlXZERD",
                "john",
                "doe",
                "Shrek is love. Shrek is live",
                True
            ],
            [
                "b365cd8f07cd0520",
                "john.marston",
                "JDJiJDEyJFMudTBhZHVUbGNXRjB1em8yTWo5Q2U3SlJGWkIvTHYvVjZnR2pITjhxckVjUk1zeHNvNTZD",  # password
                "john",
                "marston",
                "NaN",
                False
            ]
        ]

        result = self.db_util.load_many(table_name, filter_function, user_first_name)
        self.assertEqual(result, expected_result)


#WORK
    def test_insert_one(self):
        new_user_id = self.db_util.generate_unique_id()
        obj1 = {
            "user_id": new_user_id,
            "username": "eren.jaeger",
            "password": "thisismypassword",
            "first_name": "eren",
            "last_name": "jaeger",
            "bio": "tatakai! tatakai!",
            "remember_me": True
        }

        self.db_util.insert_one("users", obj1, column="user_id", dublicate=True)

        loaded_data = self.db_util.load_one("users",  "user_id", value=new_user_id)

        self.assertEqual(loaded_data['user_id'], new_user_id)
        self.assertEqual(loaded_data['username'], obj1['username'])
        self.assertEqual(loaded_data['bio'], obj1['bio'])


#WORK
    def test_insert_user(self):
        new_user_id = self.db_util.generate_unique_id()
        obj_user = {
            "user_id": new_user_id,
            "username": "johnny.silverhand",
            "password": "thisismypassword",
            "first_name": "johnny",
            "last_name": "silverhand",
            "bio": "fuck arasaka",
            "remember_me": False
        }

        self.db_util.insert_one("users", obj_user, column="user_id", dublicate=True)
        loaded_data = self.db_util.load_one("users",  "user_id", new_user_id)
        self.assertEqual(loaded_data['user_id'], new_user_id)
        self.assertEqual(loaded_data['username'], "johnny.silverhand")
        self.assertEqual(loaded_data['first_name'], "johnny")
        self.assertEqual(loaded_data['last_name'], "silverhand")
        self.assertEqual(loaded_data['bio'], "fuck arasaka")
        self.assertEqual(loaded_data['remember_me'], False)

#WORK
    def test_insert_many(self):
        new_user_id = self.db_util.generate_unique_id()
        objects = [
            {
                "user_id": new_user_id,
                "username": "mr.bean",
                "password": "thisismypassword",
                "first_name": "mr",
                "last_name": "bean",
                "bio": "teddy",
                "remember_me": True
            },
            {
                "user_id": new_user_id,
                "username": "bird.eren",
                "password": "thisismypassword",
                "first_name": "eren",
                "last_name": "jaeger",
                "bio": "krah! krah!",
                "remember_me": False
            }
        ]
        self.db_util.insert_many("users", objects, column="user_id", dublicate=True)

        for obj in objects:
            loaded_data = self.db_util.load_one("users", "user_id", obj["user_id"])
            self.assertEqual(loaded_data['username'], obj['username'])
            self.assertEqual(loaded_data['remember_me'], obj['remember_me'])

# WORK
    def test_insert_with_duplicate_true(self):
        new_user_id = self.db_util.generate_unique_id()
        obj = {
                    "user_id": new_user_id,
                    "username": "charles.smith",
                    "password": "thisismypassword",
                    "first_name": "charles",
                    "last_name": "smith",
                    "bio": "",
                    "remember_me": True
                }
        self.db_util.insert_one('users', obj, 'user_id', dublicate=True)

# WORK
    def test_insert_with_duplicate_false(self):
        new_user_id = self.db_util.generate_unique_id()
        obj = {
                    "user_id": new_user_id,
                    "username": "charles.smith",
                    "password": "thisismypassword",
                    "first_name": "charles",
                    "last_name": "smith",
                    "bio": "",
                    "remember_me": True
                }
        self.db_util.insert_one('users', obj, 'user_id', dublicate=False)

# WORK
    def test_delete_one_with_id(self):
        table_name = 'student'
        id_value = "299edbe2695a53ed"
        self.assertEqual(self.db_util.delete_one_with_id(table_name, id_value), None)

# WORK
    def test_delete_one(self):
        table_name = 'student'
        column_d = "user_id"
        value_d = "6a780ff0e0bdbb97"
        self.assertEqual(self.db_util.delete_one(table_name, column_d, value_d), None)

# WORK
    def test_delete_many(self):
        table_name = 'student'
        column = "user_id"
        user_ids = ["b365cd8f07cd0520", "6a780ff0e0bdbb97"]

        for user_id in user_ids:
            exists_before = self.db_util.exists_user_by_id(table_name, user_id)
            print(f"User {user_id} exists before deletion: {exists_before}")

        self.db_util.delete_many(table_name, column, user_ids)

        for user_id in user_ids:
            exists_after = self.db_util.exists_user_by_id(table_name, user_id)
            print(f"User {user_id} exists after deletion: {exists_after}")
            self.assertFalse(exists_after, f"User {user_id} should have been deleted")

#WORK
    def test_update_one(self):
        table_name = 'users'
        column = "user_id"
        id_value = "a70030991cfada5a"
        new_values = {"username": "arthur.morgan_updated", "remember_me": False}
        self.db_util.update_one(table_name, column, id_value, new_values)

#WORK
    def test_update_many(self):
        table_name = 'users'
        conditions = [
            {"user_id": "a70030991cfada5a"},
            {"user_id": "430112d4d154a44f"}
            ]
        new_values = [
            {"remember_me": False},
            {"remember_me": False}
            ]
        self.db_util.update_many(table_name, conditions, new_values)
        result = self.db_util.load_many(
            table_name,
            "user_id = %s",
            ["a70030991cfada5a"]
            )
        self.assertEqual(result[0]["remember_me"], False)

        result = self.db_util.load_many(
            table_name,
            "user_id = %s",
            ["430112d4d154a44f"]
            )
        self.assertEqual(result[0]["remember_me"], False)

#WORK
    def test_build_query_select(self):
        table_name = "users"
        conditions = [("first_name", "john"), ("remember_me", "TRUE")]
        operator = "AND"
        query_type = "SELECT"

        expected_query = "SELECT * FROM users WHERE first_name = %s AND remember_me = %s;"
        expected_params = ["john", "TRUE"]

        query, params = self.db_util._build_query(table_name, conditions, operator, query_type)

        self.assertEqual(query, expected_query)
        self.assertEqual(params, expected_params)


#WORK
    def test_exist_user_id(self):
        user_id_to_test = 202345671
        expected_exists = False  # Setzen Sie dies auf True, wenn der Benutzer existieren soll

        # Überprüfen Sie, ob der Benutzer existiert
        exists = self.db_util.exists_user_by_id("users", user_id_to_test)
        print(f"User {user_id_to_test} exists: {exists}")  # Debug-Ausgabe

        # Assert, dass der Benutzer wie erwartet existiert oder nicht existiert
        self.assertEqual(exists, expected_exists, f"User {user_id_to_test} existence check failed")



if __name__ == '__main__':
    unittest.main()
