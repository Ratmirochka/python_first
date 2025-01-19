import sys
import jwt
from jinja2.compiler import generate
from werkzeug.security import check_password_hash
import datetime

sys.path.append('../')
from dal.auth_query import DbQuery

class AdminBl():
    @staticmethod
    def is_correct(login, password):
        passw = DbQuery.get_passw(login)
        if passw is None:
            return False
        return check_password_hash(passw[0], password)

    # @staticmethod
    # def generate_jwt(user_id, SECRET_KEY):
    #     payload = {
    #         "user_id": user_id,
    #         "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    #     }
    #     return jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    #
    # @staticmethod
    # def decode_jwt(token, SECRET_KEY):
    #     try:
    #         payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    #         return payload.get("sub")
    #     except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
    #         return False


