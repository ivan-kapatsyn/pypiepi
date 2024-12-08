import os
from dotenv import load_dotenv

class EnvVariableUtil:
    @staticmethod
    def get_env_variable(var_name):
        load_dotenv()
        try:
            result = os.environ[var_name]
        except KeyError:
            raise KeyError(f"The variable '{var_name}' does not exist. Please go to .env file to set it.")

        if EnvVariableUtil.validate(result):
            return result
        else:
            raise KeyError(f"The variable '{var_name}' has invalid value '{result}'. Please update the variable.")

    @staticmethod
    def validate(result):
        if result is None:
            return False
        if result == "":
            return False
        if result == '...':
            return False
        return True