import threading
import webbrowser

from flask import Flask
from src.ui.routes import Routes
from src.utils.path_util import PathUtil


def create_app():
    app = Flask(__name__,
                template_folder=PathUtil.get_template_path(),
                static_folder=PathUtil.get_static_path())
    app.config.from_object('src.ui.configs.configs.Config')


    app.register_blueprint(Routes.main_bp)

    return app

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/login")


if __name__ == '__main__':
    app = create_app()
    threading.Timer(1, open_browser).start()

    # TODO debug=True make the browser load the page twice. Solve it
    app.run(debug=False)
