import unittest

from src.utils.data_base_util import DataBaseUtil


class DataBaseUtilTestCase(unittest.TestCase):

    def setUp(self):
        self.db_util = DataBaseUtil()

    def test_if_exist(self):
        table_name = 'tmuser'
        self.assertEqual(self.db_util.check_if_table_exists(
                table_name), True)

    def test_load_data(self):
        table_name = 'tmuser'
        condition = 'user_id'
        value = 202345671

        expected_result = [202345671, 'arthur_morgan', 'password123', 'student', True]
        self.assertEqual(self.db_util.load_data(table_name, condition, value),expected_result)


    def test_delete_data(self):
        table_name = 'tmuser'
        condition = 'user_id'
        value = '202345671'
        self.assertEqual(self.db_util.delete_data(table_name, condition, value),None)


    def test_insert_data(self):
        obj1 = {
            "user_id": 202345671,
            "username": "arthur_morgan",
            "password": "password123",
            "user_typ": "student",
            "remember_me": "TRUE"}

        self.db_util.insert_one("tmuser", obj1, column="user_id", dublicate=True)
        loaded_data = self.db_util.load_data("tmuser", "user_id", 202345671)
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
        self.db_util.insert_many("tmuser", objects, column="user_id", dublicate=True)

        for obj in objects:
            loaded_data = self.db_util.load_data("tmuser", "user_id", obj["user_id"])
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

        expected_query = "SELECT * FROM tmuser WHERE user_typ = %s AND remember_me = %s;"
        expected_params = ["admin", "TRUE"]

        query, params = self.db_util.build_query(table_name, conditions, operator, query_type)

        self.assertEqual(query, expected_query)
        self.assertEqual(params, expected_params)


if __name__ == '__main__':
    unittest.main()
