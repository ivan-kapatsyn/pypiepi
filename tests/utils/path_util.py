import unittest
from pathlib import Path

from src.utils.path_util import PathUtil


class PathUtilTestCase(unittest.TestCase):
    def test_template_path(self):
        file = 'login.html'
        path_to_html = Path(PathUtil.get_template_path(), file)
        self.assertEqual(path_to_html.exists(), True)

    def test_static_path(self):
        file = 'favicon.ico'
        path_to_ico = Path(PathUtil.get_static_path(), file)
        self.assertEqual(path_to_ico.exists(), True)


if __name__ == '__main__':
    unittest.main()
