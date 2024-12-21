import unittest

from src.utils.data_base_util import DataBaseUtil


class DataBaseUtilTestCase(unittest.TestCase):
    def test_if_exist(self):
        table_name = 'tmuser'
        self.assertEqual(DataBaseUtil().check_if_table_exists(
                table_name), True)

    def test_some_values_initialised(self):
        DataBaseUtil.initialise_db
        #

        raise NotImplementedError





if __name__ == '__main__':
    unittest.main()
