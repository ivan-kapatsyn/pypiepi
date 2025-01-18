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
        id_value = "f63b0b2f7c48c85f"

        expected_result = ["f63b0b2f7c48c85f", "arthur.morgan",
                           "JDJiJDEyJGx6RjZMbnZqTEdJcEtlY3pWZENqNmVWQkpKcnVSSGNSaU54S085TWQvc2tYQ29FQWF6d2wy",
                           "arthur", "morgan", "NaN",True]
        self.assertEqual(self.db_util.load_one(table_name, column,id_value), expected_result)

#WORK
    def test_load_many(self):
        table_name = 'users'
        filter_function = "first_name = %s"
        user_first_name = ["john"]

        expected_result = [
            [
                "f67d38dee48d641f",
                "john.doe",
                "JDJiJDEyJHB6L3o4ZnR3SE1uQkpzS09UUUpSaS5pLzRvYks1OTVSL0s3NXVnOVVmRlFVcXp3YTkzUzNP",
                "john",
                "doe",
                "Shrek is love. Shrek is live",
                True
            ],
            [
                "59d1dcf2a970a9fd",
                "john.marston",
                "JDJiJDEyJDgxaXUuZmdNZXVPcHJCYXQveEwyRS51UVZKZ1UwLnBXVDdIVnBBQVRPdVNQWXluSm45SENT",  # password
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
                    "username": "dutch.vanderlinde",
                    "password": "tahiti",
                    "first_name": "dutch",
                    "last_name": "van der linde",
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
        table_name = 'student'
        column_d = "user_id"
        value_d = "16f9cbf0d5f0e513"
        self.assertEqual(self.db_util.delete_one(table_name, column_d, value_d), None)

# WORK
    def test_delete_many(self):
        table_name = 'student'
        column = "user_id"
        user_ids = ["f67d38dee48d641f", "f63b0b2f7c48c85f"]

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
        expected_exists = False  # Setzen Sie dies auf True, wenn der Benutzer existieren soll

        # Überprüfen Sie, ob der Benutzer existiert
        exists = self.db_util.exists_user_by_id("users", user_id_to_test)
        print(f"User {user_id_to_test} exists: {exists}")  # Debug-Ausgabe

        # Assert, dass der Benutzer wie erwartet existiert oder nicht existiert
        self.assertEqual(exists, expected_exists, f"User {user_id_to_test} existence check failed")


'''
    def test_save_data_to_csv(self):
        data_user = [
            {"username": "arthur.morgan", "password": "password123", "first_name": "arthur", "last_name": "morgan",
             "bio": "", "remember_me": "TRUE"},
            {"username": "john.doe", "password": "newpassword", "first_name": "john", "last_name": "doe",
             "bio": "Shrek is love. Shrek is live", "remember_me": "TRUE"},
            {"username": "jane.doe", "password": "mypassword", "first_name": "jane", "last_name": "doe",
             "bio": "Professional construction enthusiast", "remember_me": "FALSE"},
            {"username": "john.marston", "password": "mypasswordisbetter", "first_name": "john", "last_name": "marston",
             "bio": "", "remember_me": "FALSE"},
            {"username": "mary.stuart", "password": "stupidpassword", "first_name": "mary", "last_name": "stuart",
             "bio": "Am I a pretty girl?", "remember_me": "TRUE"},
            {"username": "walter.white", "password": "heisenberg", "first_name": "walter", "last_name": "white",
             "bio": "Say my name.", "remember_me": "TRUE"},
            {"username": "luke.skywalker", "password": "jedi123", "first_name": "luke", "last_name": "skywalker",
             "bio": "May the force be with you.", "remember_me": "TRUE"},
            {"username": "rick.grimes", "password": "coral123", "first_name": "rick", "last_name": "grimes",
             "bio": "We are the walking dead.", "remember_me": "TRUE"},
            {"username": "jesse.pinkman", "password": "yo1234", "first_name": "jesse", "last_name": "pinkman",
             "bio": "Yeah science!", "remember_me": "FALSE"},
            {"username": "tony.stark", "password": "ironman", "first_name": "tony", "last_name": "stark",
             "bio": "Genius, billionaire, playboy, philanthropist.", "remember_me": "TRUE"},
            {"username": "barney.stinson", "password": "legenwaitforitdary", "first_name": "barney",
             "last_name": "stinson", "bio": "Suit up!", "remember_me": "TRUE"},
            {"username": "ted.mosby", "password": "architect4life", "first_name": "ted", "last_name": "mosby",
             "bio": "", "remember_me": "TRUE"},
            {"username": "patrick.star", "password": "isthiskrustykrab", "first_name": "patrick", "last_name": "star",
             "bio": "No, this is Patrick!", "remember_me": "FALSE"},
            {"username": "spongebob.squarepants", "password": "ilovekrabbypatties", "first_name": "spongebob",
             "last_name": "squarepants", "bio": "", "remember_me": "TRUE"},
            {"username": "luffy.monkey", "password": "pirateking", "first_name": "monkey", "last_name": "d. luffy",
             "bio": "I’m gonna be the Pirate King!", "remember_me": "TRUE"},
            {"username": "sheldon.cooper", "password": "bazinga", "first_name": "sheldon", "last_name": "cooper",
             "bio": "I'm not crazy. My mother had me tested.", "remember_me": "TRUE"},
            {"username": "leonard.hofstadter", "password": "physics123", "first_name": "leonard",
             "last_name": "hofstadter", "bio": "", "remember_me": "FALSE"},
            {"username": "patrick.star", "password": "mayonnaise", "first_name": "patrick", "last_name": "star",
             "bio": "Is mayonnaise an instrument?", "remember_me": "TRUE"},
            {"username": "sandy.cheeks", "password": "karate123", "first_name": "sandy", "last_name": "cheeks",
             "bio": "A squirrel in the sea!", "remember_me": "TRUE"},
            {"username": "max.mustermann", "password": "musterpasswort", "first_name": "max", "last_name": "mustermann",
             "bio": "", "remember_me": "TRUE"},
        ]

        # Jede user_id generieren
        for user in data_user:
            user["user_id"] = self.db_util.generate_unique_id()

        column_types = {
            "user_id": "VARCHAR(16)",
            "username": "VARCHAR(200)",
            "password": "VARCHAR(80)",
            "first_name": "VARCHAR(20)",
            "last_name": "VARCHAR(200)",
            "bio": "VARCHAR(200)",
            "remember_me": "BOOLEAN"
        }

        table_name = "users"

        self.db_util.save_data_to_csv(table_name, data_user, column_types)

'''



if __name__ == '__main__':
    unittest.main()
