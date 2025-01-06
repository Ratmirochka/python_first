from flask import Flask, request, Blueprint, jsonify
from dotenv import load_dotenv, find_dotenv
from flasgger import swag_from
import json
import sys
import os

sys.path.append('../')
from bl.bl import AdminBl
from dal.admin_page_query import DbQuery

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
                    "example": {
                        "message": [
                            {
                                "username": "Иван Иванов",
                                "post": "Менеджер",
                                "role": "Администратор",
                                "projects": "Проект 1, Проект 2"
                            }
                        ],
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
                        "message": "You are not admin",
                        "success": False
                    }
                }
            }
        }
    }
})
def get_user_for_admin():
    data = request.get_json()

    if not data or 'token' not in data or 'filter' not in data:
        return jsonify({
            "message": "Missing required fields",
            "success": False
        }), 400

    token = data['token']
    filter = data['filter']

    user_id = AdminBl.decode_jwt(token, os.getenv('SECRET_KEY'))
    if user_id:
        print(f"user_id = {user_id}")
        role = DbQuery.get_role(user_id)[0]
        print(f"role = {role}")
        if role == 'admin' or role == 'super admin':
            users = DbQuery.get_user_for_admin(filter)
            return jsonify({
                "message": users,
                "success": True
            }), 200
        else:
            return jsonify({
                "message": "You are not admin",
                "success": True
            }), 401
    else:
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
    data = request.get_json()

    if not data or 'token' not in data or 'name' not in data or 'mail' not in data or 'passw' not in data or 'post' not in data or 'role' not in data:
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
        if user_role == 'super admin':
            role_id = 1
            if role == 'user': role_id = 1
            if role == 'admin': role_id = 2
            if role == 'super admin': role_id = 3
            DbQuery.insert_new_user(name, post, mail, passw, role_id)
            return jsonify({
                "message": "User is added",
                "success": True
            }), 200
        return jsonify({
            "message": "You are not super admin",
            "success": False
        }), 401
    return jsonify({
        "message": "The token is incorrect",
        "success": False
    }), 401