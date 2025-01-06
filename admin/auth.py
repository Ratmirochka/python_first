from flask import Flask, request, Blueprint, jsonify
from dotenv import load_dotenv, find_dotenv
from flasgger import swag_from
import os
import sys

sys.path.append('../')
from bl.bl import AdminBl
from dal.auth_query import DbQuery
from logs.loguru_conf import get_logger
load_dotenv(find_dotenv())

auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route('/', methods=['POST'])
@swag_from({
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "login": {"type": "string"},
                    "password": {"type": "string"}
                },
                "required": ["login", "password"]
            }
        }
    ],
    "responses": {
        "200": {
            "description": "Успешная аутентификация",
            "examples": {
                "application/json": {
                    "example": {
                        "message": "Logged in successfully",
                        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "user": {
                            "user_id": 1,
                            "name": "Иван Иванов",
                            "post": "Менеджер",
                            "role": "Администратор"
                        }
                    }
                }
            }
        },
        "400": {
            "description": "Неверный формат запроса",
            "examples": {
                "application/json": {
                    "example": {
                        "message": "Missing required fields",
                        "success": False
                    }
                }
            }
        },
        "401": {
            "description": "Неверные учетные данные",
            "examples": {
                "application/json": {
                    "example": {
                        "message": "Incorrect username/password",
                        "success": False
                    }
                }
            }
        },
        "500": {
            "description": "Ошибка сервера",
            "examples": {
                "application/json": {
                    "example": {
                        "message": "Database connection error",
                        "success": False
                    }
                }
            }
        }
    }
})
def auth():
    logger = get_logger("auth.log")
    data = request.get_json()

    if not data or 'login' not in data or 'password' not in data:
        logger.warning("Неверный формат запроса: отсутствуют обязательные поля")
        return jsonify({
            "message": "Missing required fields",
            "success": False
        }), 400

    login = data['login']
    password = data['password']

    logger.info(f"Попытка аутентификации пользователя: {login}")
    result = AdminBl.is_correct(login, password)

    if result is True:
        user = DbQuery.get_user(login)
        if user:
            token = AdminBl.generate_jwt(user['user_id'], os.getenv('SECRET_KEY'))
            logger.info(f"Пользователь {login} успешно аутентифицирован")
            return jsonify({
                "message": "Logged in successfully",
                "token": token,
                "user": user
            }), 200
        else:
            logger.error(f"Ошибка получения данных пользователя {login}")
            return jsonify({
                "message": "Database connection error",
                "success": False
            }), 500
    elif result is False:
        logger.warning(f"Неверные учетные данные для пользователя {login}")
        return jsonify({
            "message": "Incorrect username/password",
            "success": False
        }), 401
    else:
        logger.error("Ошибка сервера при проверке учетных данных")
        return jsonify({
            "message": "Database connection error",
            "success": False
        }), 500
