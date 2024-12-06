import unittest

from src.utils.env_variable_util import EnvVariableUtil


class EnvVariableUtilTestCase(unittest.TestCase):
    def test_check_right_env_variable(self):
        result = EnvVariableUtil.get_env_variable('STATIC_RELATIVE_PATH')

        expected_result = "html\\css"
        self.assertEqual(result, expected_result)

    def test_check_wrong_env_variable(self):
        try:
            result = EnvVariableUtil.get_env_variable('DUMMY_VARIABLE_USED_FOR_UNITTEST')
        except Exception as e:
            self.assertEqual(type(e), KeyError)
            self.assertEqual(str(e),
                             "\"The variable 'DUMMY_VARIABLE_USED_FOR_UNITTEST' has invalid value '...'. Please update the variable.\"")

    def test_check_wrong_env_variable_name(self):
        try:
            result = EnvVariableUtil.get_env_variable('BAKA')
        except Exception as e:
            self.assertEqual(type(e), KeyError)
            self.assertEqual(str(e),
                             "\"The variable 'BAKA' does not exist. Please go to .env file to set it.\"")


if __name__ == '__main__':
    unittest.main()
