from flask import Flask
from flasgger import Swagger
from admin.to_do import to_do_blueprint
from admin.auth import auth_blueprint
from admin.budget import budget_blueprint
from admin.admin_page import admin_page_blueprint

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kjh92JHGkj023Kfewi43KJKfgew'

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
    "swagger_ui_js": "https://rawcdn.githack.com/swagger-api/swagger-ui/v3.23.1/dist/swagger-ui.js"
}

# Инициализируем Swagger
Swagger(app, config=swagger_config)

app.register_blueprint(to_do_blueprint, url_prefix='/to_do')
app.register_blueprint(auth_blueprint, url_prefix='/auth')
app.register_blueprint(budget_blueprint, url_prefix='/budget')
app.register_blueprint(admin_page_blueprint, url_prefix='/admin_page')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)