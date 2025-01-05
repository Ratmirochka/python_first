from flask import Flask
from admin.admin import admin

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kjh92JHGkj023Kfewi43KJKfgew'

app.register_blueprint(admin, url_prefix='/admin')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)