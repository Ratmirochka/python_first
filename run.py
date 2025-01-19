from dotenv import load_dotenv, find_dotenv
from flask_jwt_extended import JWTManager
from datetime import timedelta
from flasgger import Swagger, swag_from
from flask import Flask
import os

from admin.to_do import to_do_blueprint
from admin.auth import auth_blueprint
from admin.budget import budget_blueprint
from admin.admin_page import admin_page_blueprint
from admin.board import board_blueprint
from admin.task import task_blueprint

load_dotenv(find_dotenv())

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=8)

jwt = JWTManager(app)

swagger_config = {
    "headers": [
    ],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "swagger_ui_bundle_js": "https://rawcdn.githack.com/swagger-api/swagger-ui/v3.23.1/dist/swagger-ui-bundle.js",
    "swagger_ui_standalone_preset_js": "https://rawcdn.githack.com/swagger-api/swagger-ui/v3.23.1/dist/swagger-ui-standalone-preset.js",
    "swagger_ui_css": "https://rawcdn.githack.com/swagger-api/swagger-ui/v3.23.1/dist/swagger-ui.css",
    "swagger_ui_js": "https://rawcdn.githack.com/swagger-api/swagger-ui/v3.23.1/dist/swagger-ui.js",
}


swagger = Swagger(app, config=swagger_config)

app.register_blueprint(to_do_blueprint, url_prefix='/to_do')
app.register_blueprint(auth_blueprint, url_prefix='/auth')
app.register_blueprint(budget_blueprint, url_prefix='/budgets')
app.register_blueprint(admin_page_blueprint, url_prefix='/admin_page')
app.register_blueprint(board_blueprint, url_prefix='/boards')
app.register_blueprint(task_blueprint, url_prefix='/boards/tasks')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)