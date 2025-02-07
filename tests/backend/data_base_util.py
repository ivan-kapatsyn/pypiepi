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

#WORK
    def test_if_exist(self):
        table_name = 'users'
        self.assertEqual(self.db_util._check_if_table_exists(
                table_name), True)

#WORK
    def test_load_one(self):
        table_name = 'users'
        column = "user_id"
        id_value = "f63b0b2f7c48c85f"

        expected_result = ["f63b0b2f7c48c85f", "arthur.morgan",
                           "JDJiJDEyJGx6RjZMbnZqTEdJcEtlY3pWZENqNmVWQkpKcnVSSGNSaU54S085TWQvc2tYQ29FQWF6d2wy",
                           "Arthur", "Morgan", "NaN",True,'student']
        self.assertEqual(self.db_util.load_one(table_name, column,id_value), expected_result)

#WORK
    def test_load_many(self):
        table_name = 'users'
        filter_function = "first_name = %s"
        user_first_name = ["John"]

        expected_result = [
            [
                "f67d38dee48d641f",
                "john.doe",
                "JDJiJDEyJHB6L3o4ZnR3SE1uQkpzS09UUUpSaS5pLzRvYks1OTVSL0s3NXVnOVVmRlFVcXp3YTkzUzNP",
                "John",
                "Doe",
                "Shrek is love. Shrek is live",
                True,
                'student'
            ],
            [
                "b365cd8f07cd0520",
                "john.marston",
                "JDJiJDEyJDgxaXUuZmdNZXVPcHJCYXQveEwyRS51UVZKZ1UwLnBXVDdIVnBBQVRPdVNQWXluSm45SENT",  # password
                "John",
                "Marston",
                "NaN",
                False,
                'tutor'
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
            "first_name": "Eren",
            "last_name": "Jaeger",
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
            "first_name": "Johnny",
            "last_name": "Silverhand",
            "bio": "fuck arasaka",
            "remember_me": False
        }

        self.db_util.insert_one("users", obj_user, column="user_id", dublicate=True)
        loaded_data = self.db_util.load_one("users",  "user_id", new_user_id)
        self.assertEqual(loaded_data['user_id'], new_user_id)
        self.assertEqual(loaded_data['username'], "johnny.silverhand")
        self.assertEqual(loaded_data['first_name'], "Johnny")
        self.assertEqual(loaded_data['last_name'], "Silverhand")
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
                "first_name": "Mr",
                "last_name": "Bean",
                "bio": "teddy",
                "remember_me": True
            },
            {
                "user_id": new_user_id,
                "username": "bird.eren",
                "password": "thisismypassword",
                "first_name": "Eren",
                "last_name": "Jaeger",
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
                    "first_name": "Charles",
                    "last_name": "Smith",
                    "bio": "",
                    "remember_me": True
                }
        self.db_util.insert_one('users', obj, 'user_id', dublicate=True)

# WORK
    def test_insert_with_duplicate_false(self):
        new_user_id = self.db_util.generate_unique_id()
        obj = {
                    "user_id": new_user_id,
                    "username": "dutch.vanderlinde",
                    "password": "tahiti",
                    "first_name": "Dutch",
                    "last_name": "Van der Linde",
                    "bio": "",
                    "remember_me": True
                }
        self.db_util.insert_one('users', obj, 'user_id', dublicate=False)

# WORK
    def test_delete_one_with_id(self):
        table_name = 'student'
        id_value = "59d1dcf2a970a9fd"
        self.assertEqual(self.db_util.delete_one_with_id(table_name, id_value), None)

# WORK
    def test_delete_one(self):
        table_name = 'student_in_course'
        column_d = "student_id"
        value_d = "16f9cbf0d5f0e513"
        self.assertEqual(self.db_util.delete_one(table_name, column_d, value_d), None)

# WORK
    def test_delete_many(self):
        table_name = 'student_in_course'
        column = "student_id"
        user_ids = ["f67d38dee48d641f", "f63b0b2f7c48c85f"]

        self.db_util.delete_many(table_name, column, user_ids)


#WORK
    def test_update_one(self):
        table_name = 'users'
        column = "user_id"
        id_value = "f63b0b2f7c48c85f"
        new_values = {"username": "arthur.morgan_updated", "remember_me": False}
        self.db_util.update_one(table_name, column, id_value, new_values)

#WORK
    def test_update_many(self):
        table_name = 'users'
        conditions = [
            {"user_id": "14d099c161cf3bea"},
            {"user_id": "928930d566c50b2d"}
            ]
        new_values = [
            {"remember_me": False},
            {"remember_me": False}
            ]
        self.db_util.update_many(table_name, conditions, new_values)
        result = self.db_util.load_many(
            table_name,
            "user_id = %s",
            ["14d099c161cf3bea"]
            )
        self.assertEqual(result[0]["remember_me"], False)

        result = self.db_util.load_many(
            table_name,
            "user_id = %s",
            ["928930d566c50b2d"]
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
        user_id_to_test = "202345671"
        expected_exists = False
        exists = self.db_util.exists_user_by_id("users", user_id_to_test)
        print(f"User {user_id_to_test} exists: {exists}")

        self.assertEqual(exists, expected_exists, f"User {user_id_to_test} existence check failed")


    def test_exist_user_id(self):
        user_id_to_test = "202345671"
        expected_exists = False
        exists = self.db_util.exists_user_by_id("users", user_id_to_test)
        print(f"User {user_id_to_test} exists: {exists}")

        self.assertEqual(exists, expected_exists, f"User {user_id_to_test} existence check failed")


if __name__ == '__main__':
    unittest.main()
