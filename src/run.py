import threading
import webbrowser

from flask import Flask

from src.ui.route_components.course_routes import CoursesRoutes
from src.ui.route_components.login_routes import LoginRoutes
from src.ui.route_components.register_routes import RegisterRoutes
from src.ui.route_components.tutor_routes import TutorRoutes
from src.ui.route_components.user_routes import UserRoutes
from src.utils.path_util import PathUtil


def create_app():
    app = Flask(__name__,
                template_folder=PathUtil.get_template_path(),
                static_folder=PathUtil.get_static_path())
    app.config.from_object('src.ui.configs.configs.Config')

    routes = [LoginRoutes,RegisterRoutes,TutorRoutes,UserRoutes,CoursesRoutes]
    for route in routes:
        app.register_blueprint(route.main_bp)

    return app

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/login/index")


if __name__ == '__main__':
    app = create_app()
    threading.Timer(1, open_browser).start()

    # TODO debug=True make the browser load the page twice. Solve it
    app.run(debug=False)
