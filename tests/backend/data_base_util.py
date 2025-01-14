import os
import unittest

from pandas.core.interchange import column

from src.utils.data_base_util import DataBaseUtil
from src.utils.env_variable_util import EnvVariableUtil


class DataBaseUtilTestCase(unittest.TestCase):

    def setUp(self):
        self.db_util = DataBaseUtil()

#WORKS
    def test_if_exist(self):
        table_name = 'users'
        self.assertEqual(self.db_util._check_if_table_exists(
                table_name), True)

#WORK
    def test_load_one(self):
        table_name = 'users'
        column = "user_id"
        id_value = "9e6fde3566ae0547"

        expected_result = ["9e6fde3566ae0547", "arthur.morgan",
                           "JDJiJDEyJGxyUzIvQTROb2JCeDVpWUJzeVVDTWVPMzlDZklqZmJwZDB6d3NsLkJvLm5WaTJYUWY3N1FL",
                           "arthur", "morgan", "NaN",True]
        self.assertEqual(self.db_util.load_one(table_name, column,id_value), expected_result)

#WORK
    def test_load_many(self):
        table_name = 'users'
        filter_function = "first_name = %s"
        user_first_name = ["john"]

        expected_result = [
            [
                "506c1a851263a9e5",
                "john.doe",
                "JDJiJDEyJHFBdGhDL3RRYks5b2J0UHRpemZqbXVScERjb2c3dzF2MHl4WVNJVmdkWXZvMWtRTFZPejVL",
                "john",
                "doe",
                "Shrek is love. Shrek is live",
                True
            ],
            [
                "19995af5bef504ee",
                "john.marston",
                "JDJiJDEyJEVuSkM0UGRic2FVQzloRWtrQU1sVy5weE1QeHJZQy5wTjRNb1g3Si50R2JGVnlxcjYudFJx",  # password
                "john",
                "marston",
                "NaN",
                False
            ]
        ]

        result = self.db_util.load_many(table_name, filter_function, user_first_name)

        self.assertEqual(result, expected_result)


#WORK
    def test_delete_one_with_id(self):
        table_name = 'users'
        id_value = "2efafa285df19ac9"
        self.assertEqual(self.db_util.delete_one_with_id(table_name, id_value), None)


#WORK
    def test_delete_one(self):
        table_name = 'users'
        column_d = "user_id"
        value_d = "063dfafed02ea11d"
        self.assertEqual(self.db_util.delete_one(table_name, column_d, value_d), None)

#WORK
    def test_delete_many(self):
        table_name = 'users'
        column = "user_id"
        user_ids = ["9b5bdd1016946389", "961ce05a42f05144", "8d66502c89d550c9"]

        for user_id in user_ids:
            exists_before = self.db_util.exists_user_by_id(table_name, user_id)
            print(f"User {user_id} exists before deletion: {exists_before}")

        self.db_util.delete_many(table_name, column, user_ids)

        for user_id in user_ids:
            exists_after = self.db_util.exists_user_by_id(table_name, user_id)
            print(f"User {user_id} exists after deletion: {exists_after}")
            self.assertFalse(exists_after, f"User {user_id} should have been deleted")

#WORK
    def test_insert_one(self):
        obj1 = {
            "user_id": "9e6fde3566ae0547",
            "student_id": "c6ffacc8367b6336",
            "qualification": ["economics"]
        }

        self.db_util.insert_one("student", obj1, column="student_id", dublicate=True)

        loaded_data = self.db_util.load_one("student",  "student_id", value="c6ffacc8367b6336")

        self.assertEqual(loaded_data['user_id'], "9e6fde3566ae0547")
        self.assertEqual(loaded_data['student_id'], "c6ffacc8367b6336")
        self.assertEqual(loaded_data['qualification'], ["economics"])

#WORK
    def test_insert_user(self):
        new_user_id = self.db_util.generate_unique_id()
        obj_user = {
            "user_id": new_user_id,
            "username": "eren.jaeger",
            "password": "thisismypassword",
            "first_name": "eren",
            "last_name": "jaeger",
            "bio": "tatakai! tatakai!",
            "remember_me": True
        }

        self.db_util.insert_one("users", obj_user, column="user_id", dublicate=True)
        loaded_data = self.db_util.load_one("users",  "user_id", new_user_id)
        self.assertEqual(loaded_data['user_id'], new_user_id)
        self.assertEqual(loaded_data['username'], "eren.jaeger")
        self.assertEqual(loaded_data['first_name'], "eren")
        self.assertEqual(loaded_data['last_name'], "jaeger")
        self.assertEqual(loaded_data['bio'], "tatakai! tatakai!")
        self.assertEqual(loaded_data['remember_me'], True)

#WORK
    def test_insert_many(self):
        new_user_id = self.db_util.generate_unique_id()
        objects = [
            {
                "user_id": new_user_id,
                "username": "eren.jaeger",
                "password": "thisismypassword",
                "first_name": "eren",
                "last_name": "jaeger",
                "bio": "tatakai! tatakai!",
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
            self.assertEqual(loaded_data['user_id'], obj['user_id'])
            self.assertEqual(loaded_data['username'], obj['username'])
            self.assertEqual(loaded_data['remember_me'], obj['remember_me'])

#WORK
    def test_update_one(self):
        table_name = 'users'
        column = "user_id"
        id_value = "9e6fde3566ae0547"
        new_values = {"username": "arthur.morgan_updated", "remember_me": False}
        self.db_util.update_one(table_name, column, id_value, new_values)

#WORK
    def test_update_many(self):
        table_name = 'users'
        conditions = [
            {"user_id": "9e6fde3566ae0547"},
            {"user_id": "063dfafed02ea11d"}
            ]
        new_values = [
            {"remember_me": "TRUE"},
            {"remember_me": "TRUE"}
            ]
        self.db_util.update_many(table_name, conditions, new_values)
        result = self.db_util.load_many(
            table_name,
            "user_id = %s",
            ["9e6fde3566ae0547"]
            )
        self.assertEqual(result[0]["remember_me"], True)

        result = self.db_util.load_many(
            table_name,
            "user_id = %s",
            ["063dfafed02ea11d"]
            )
        self.assertEqual(result[0]["remember_me"], True)

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

#WORK
    def test_initialise(self):
        self.db_util.initialise()

#WORK
    def test_insert_with_duplicate_true(self):
        new_user_id = self.db_util.generate_unique_id()
        obj = {
            "user_id": new_user_id,
            "username": "eren.jaeger",
            "password": "thisismypassword",
            "first_name": "eren",
            "last_name": "jaeger",
            "bio": "tatakai! tatakai!",
            "remember_me": True
        }
        self.db_util.insert_one('users', obj, 'user_id', dublicate=True)

#WORK
    def test_insert_with_duplicate_false(self):
        new_user_id = self.db_util.generate_unique_id()
        obj = {
            "user_id": new_user_id,
            "username": "eren.jaeger",
            "password": "thisismypassword",
            "first_name": "eren",
            "last_name": "jaeger",
            "bio": "tatakai! tatakai!",
            "remember_me": True
        }
        self.db_util.insert_one('users', obj, 'user_id', dublicate=False)

#WORKS
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
