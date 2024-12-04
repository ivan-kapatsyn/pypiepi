from flask import Flask
from src.ui.routes import main_bp

def create_app():
    app = Flask(__name__,
                template_folder=r'C:\Users\Admin\Desktop\programs\Uni\pypiepi\html',)
    app.config.from_object('src.ui.configs.configs.Config')


    app.register_blueprint(main_bp)

    return app



if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
