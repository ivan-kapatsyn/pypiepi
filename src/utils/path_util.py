import os
from pathlib import Path

from src.utils.env_variable_util import EnvVariableUtil


class PathUtil:
    @staticmethod
    def get_project_path():
        project_path = EnvVariableUtil.get_env_variable('PROJECT_PATH')
        return project_path

    @staticmethod
    def get_template_path():
        project_path = PathUtil.get_project_path()
        template_path = EnvVariableUtil.get_env_variable('TEMPLATE_RELATIVE_PATH')
        return Path(project_path, template_path)

    @staticmethod
    def get_static_path():
        project_path = PathUtil.get_project_path()
        static_path = EnvVariableUtil.get_env_variable('STATIC_RELATIVE_PATH')
        return Path(project_path, static_path)

    @staticmethod
    def get_data_path():
        project_path = PathUtil.get_project_path()
        static_path = EnvVariableUtil.get_env_variable('DATA_RELATIVE_PATH')
        return Path(project_path, static_path)

    @staticmethod
    def get_json_path():
        project_path = PathUtil.get_project_path()
        static_path = EnvVariableUtil.get_env_variable('DATA_RELATIVE_PATH')
        return Path(project_path, static_path) / r'database_structure.json'

