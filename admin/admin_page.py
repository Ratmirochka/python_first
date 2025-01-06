from flask import Flask, request, Blueprint, jsonify
from dotenv import load_dotenv, find_dotenv
from flasgger import swag_from
import json
import sys
import os

sys.path.append('../')
from bl.bl import AdminBl
from dal.admin_page_query import DbQuery
from logs.loguru_conf import get_logger

load_dotenv(find_dotenv())

admin_page_blueprint = Blueprint('admin_page', __name__)

@admin_page_blueprint.route('/get_user_for_admin', methods=['POST'])
@swag_from({
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "token": {"type": "string"},
                    "filter": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "integer"},
                            "post": {"type": "integer"},
                            "role": {"type": "integer"},
                            "project": {"type": "integer"}
                        }
                    }
                },
                "required": ["token", "filter"]
            }
        }
    ],
    "responses": {
        "200": {
            "description": "Успешный ответ",
            "examples": {
                "application/json": {
                    "message": [
                        {
                          "post": "Backend developer",
                          "projects": "еще одна тестовая доска, Сайт для клиники, To-do list",
                          "role": "super admin",
                          "username": "Akhmedshin Ratmir"
                        },
                        {
                          "post": "devops",
                          "projects": "null",
                          "role": "user",
                          "username": "anton"
                        }
                    ],
                    "success": True
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
            "description": "Неверный токен или недостаточно прав",
            "examples": {
                "application/json": {
                    "example": {
                        "message": "You are not admin",
                        "success": False
                    }
                }
            }
        }
    }
})
def get_user_for_admin():
    logger = get_logger("admin_page.log")
    logger.debug("Запрос на получение пользователей для администратора")
    data = request.get_json()

    if not data or 'token' not in data or 'filter' not in data:
        logger.debug("Некорректный запрос: отсутствуют обязательные поля")
        return jsonify({
            "message": "Missing required fields",
            "success": False
        }), 400

    token = data['token']
    filter = data['filter']

    user_id = AdminBl.decode_jwt(token, os.getenv('SECRET_KEY'))
    if user_id:
        logger.debug(f"user_id = {user_id}")
        role = DbQuery.get_role(user_id)[0]
        logger.debug(f"Роль пользователя: {role}")
        if role == 'admin' or role == 'super admin':
            users = DbQuery.get_user_for_admin(filter)
            logger.debug(f"Пользователи успешно получены: {users}")
            return jsonify({
                "message": users,
                "success": True
            }), 200
        else:
            logger.debug("Пользователь не имеет прав администратора")
            return jsonify({
                "message": "You are not admin",
                "success": True
            }), 401
    else:
        logger.debug("Неверный токен")
        return jsonify({
            "message": "The token is incorrect",
            "success": False
        }), 401


@admin_page_blueprint.route('/create_user', methods=['POST'])
@swag_from({
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "token": {"type": "string"},
                    "name": {"type": "string"},
                    "mail": {"type": "string"},
                    "passw": {"type": "string"},
                    "post": {"type": "string"},
                    "role": {"type": "string"}
                },
                "required": ["token", "name", "mail", "passw", "post", "role"]
            }
        }
    ],
    "responses": {
        "200": {
            "description": "Пользователь успешно создан",
            "examples": {
                "application/json": {
                    "example": {
                        "message": "User is added",
                        "success": True
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
            "description": "Неверный токен или недостаточно прав",
            "examples": {
                "application/json": {
                    "example": {
                        "message": "You are not super admin",
                        "success": False
                    }
                }
            }
        }
    }
})
def create_user():
    logger = get_logger("admin_page.log")
    logger.debug("Запрос на создание нового пользователя")
    data = request.get_json()

    if not data or 'token' not in data or 'name' not in data or 'mail' not in data or 'passw' not in data or 'post' not in data or 'role' not in data:
        logger.debug("Некорректный запрос: отсутствуют обязательные поля")
        return jsonify({
            "message": "Missing required fields",
            "success": False
        }), 400

    token = data['token']
    name = data['name']
    mail = data['mail']
    passw = data['passw']
    post = data['post']
    role = data['role']

    user_id = AdminBl.decode_jwt(token, os.getenv('SECRET_KEY'))
    if user_id:
        user_role = DbQuery.get_role(user_id)[0]
        logger.debug(f"Роль пользователя: {user_role}")
        if user_role == 'super admin':
            role_id = 1
            if role == 'user': role_id = 1
            if role == 'admin': role_id = 2
            if role == 'super admin': role_id = 3
            DbQuery.insert_new_user(name, post, mail, passw, role_id)
            logger.debug(f"Пользователь {name} успешно добавлен")
            return jsonify({
                "message": "User is added",
                "success": True
            }), 200
        logger.debug("Пользователь не имеет прав супер-администратора")
        return jsonify({
            "message": "You are not super admin",
            "success": False
        }), 401
    logger.debug("Неверный токен")
    return jsonify({
        "message": "The token is incorrect",
        "success": False
    }), 401