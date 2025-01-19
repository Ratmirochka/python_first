from flask_jwt_extended import jwt_required, JWTManager, get_jwt_identity
from flask import Flask, request, Blueprint, jsonify
from dotenv import load_dotenv, find_dotenv
from flasgger import swag_from
import json
import sys
import os

sys.path.append('../')
from dal.board_query import DbQuery
from logs.loguru_conf import get_logger

load_dotenv(find_dotenv())

board_blueprint = Blueprint('boards', __name__)

@board_blueprint.route('', methods=['GET'])
@swag_from({
    "parameters": [
        {
            "name": "Authorization",
            "in": "header",
            "type": "string",
            "required": True,
            "description": "Example:\"Bearer <JWT>\""
        },
        {
            "name": "deleted_boards",
            "in": "header",
            "type": "boolean",
            "required": True,
            "description": "true or false"
        }
    ],
    "responses": {
        "200": {
            "description": "Успешное получение досок",
            "examples": {
                "application/json": {
                    "example": {
                        "message": [
                            {"board_id": 1, "name": "Work", "description": "Work tasks", "role_name": "admin"}
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
            "description": "Неверный токен",
            "examples": {
                "application/json": {
                    "example": {
                        "message": "The token is incorrect",
                        "success": False
                    }
                }
            }
        }
    }
})
@jwt_required()
def get_boards(delete_boards=False):
    logger = get_logger("to_do.log")

    user_id = get_jwt_identity()
    header_value = request.headers.get('deleted_boards')

    if header_value is not None:
        delete_boards = header_value.lower() == 'true'
    print(header_value)
    print(delete_boards)
    print(f"user_id = {user_id}")
    if user_id:
        result = DbQuery.get_user_boards(user_id, delete_boards)
        logger.info(f"id = {user_id}, operation = get_boards, status = {result}")
        return jsonify({
            "message": result,
            "success": True
        }), 200
    else:
        logger.warning(f"id = {user_id}, operation = get_boards, status = The token is incorrect")
        return jsonify({
            "message": "The token is incorrect",
            "success": False
        }), 401

@board_blueprint.route('', methods=['POST'])
@swag_from({
    "parameters": [
        {
            "name": "Authorization",
            "in": "header",
            "type": "string",
            "required": True,
            "description": "Example:\"Bearer <JWT>\""
        },
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "users": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "integer"},
                                "role": {"type": "string"}
                            }
                        }
                    }
                },
                "required": ["description", "users"]
            }
        }
    ],
    "responses": {
        "200": {
            "description": "Доска успешно создана",
            "content": {
                "application/json": {
                    "example": {
                        "success": True
                    }
                }
            }
        },
        "400": {
            "description": "Неверный формат запроса",
            "content": {
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
            "content": {
                "application/json": {
                    "example": {
                        "message": "The token is incorrect",
                        "success": False
                    }
                }
            }
        }
    }
})
@jwt_required()
def create_desk():
    logger = get_logger("to_do.log")
    data = request.get_json()

    if not data or 'name' not in data or 'description' not in data or 'users' not in data:
        return jsonify({
            "message": "Missing required fields",
            "success": False
        }), 400

    name = data['name']
    description = data['description']
    users = data['users']

    user_id = get_jwt_identity()
    role = DbQuery.get_role(user_id)[0]

    if user_id and (role == 'admin' or role == 'super admin'):
        board_id = DbQuery.add_board(name, description)
        for user in users:
            role_id = 1
            if user['role'] == 'admin':
                role_id = 2
            else:
                role_id = 1
            if not DbQuery.add_user_to_board(board_id, user['user_id'], role_id):
                logger.error(f"id = {user_id}, operation = create_desk, status = Can't add user to board, user_id = {user['user_id']}, board_name = {name}, description = {description}")
                return jsonify({
                    "message": "Can't add user to board",
                    "success": False
                }), 503
        logger.info(f"id = {user_id}, operation = create_desk, status = succes, users = {users}, board_name = {name}, description = {description}")
        return jsonify({
            "success": True
        }), 200
    else:
        logger.warning(f"id = {correct}, operation = create_desk, status = The token is incorrect, user_id = {user_id}, board_id = {board_id}")
        return jsonify({
            "message": "The token is incorrect",
            "success": False
        }), 401


@board_blueprint.route('/users', methods=['POST'])
@swag_from({
    "parameters": [
        {
            "name": "Authorization",
            "in": "header",
            "type": "string",
            "required": True,
            "description": "Example:\"Bearer <JWT>\""
        },
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "board_id": {"type": "integer"},
                    "users": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "integer"},
                                "role": {"type": "string"}
                            }
                        }
                    }
                },
                "required": ["board_id", "users"]
            }
        }
    ],
    "responses": {
        "200": {
            "description": "Пользователи успешно добавлены на доску",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Users successfully added",
                        "success": True
                    }
                }
            }
        },
        "400": {
            "description": "Неверный формат запроса",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Missing required fields",
                        "success": False
                    }
                }
            }
        },
        "401": {
            "description": "Неверный токен",
            "content": {
                "application/json": {
                    "example": {
                        "message": "The token is incorrect",
                        "success": False
                    }
                }
            }
        }
    }
})
@jwt_required()
def add_to_desk():
    logger = get_logger("to_do.log")
    data = request.get_json()

    if not data or 'users' not in data or 'board_id' not in data:
        return jsonify({
            "message": "Missing required fields",
            "success": False
        }), 400

    users = data['users']
    board_id = data['board_id']

    user_id = get_jwt_identity()

    if user_id:
        for user in users:
            role_id = ''
            if user['role'] == 'admin':
                role_id = 2
            else:
                role_id = 1
            if not DbQuery.add_user_to_board(board_id, user['user_id'], role_id):
                return jsonify({
                    "message": "Can't add user to board",
                    "success": False
                }), 503
        logger.info(f"id = {user_id}, operation = add_to_desk, status = succes, users = {users}, board_id = {board_id}")
        return jsonify({
            "message": "Users succesfuly added",
            "success": True
        }), 200
    else:
        logger.warning(f"id = {user_id}, operation = add_to_desk, status = The token is incorrect, users = {users}, board_id = {board_id}")
        return jsonify({
            "message": "The token is incorrect",
            "success": False
        }), 401

@board_blueprint.route('', methods=['DELETE'])
@swag_from({
    "parameters": [
        {
            "name": "Authorization",
            "in": "header",
            "type": "string",
            "required": True,
            "description": "Example:\"Bearer <JWT>\""
        },
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "board_id": {"type": "integer"}
                },
                "required": ["board_id"]
            }
        }
    ],
    "responses": {
        "200": {
            "description": "Доска успешно удалена",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Доска удалена",
                        "success": True
                    }
                }
            }
        },
        "400": {
            "description": "Неверный формат запроса",
            "content": {
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
            "content": {
                "application/json": {
                    "example": {
                        "message": "The token is incorrect",
                        "success": False
                    }
                }
            }
        }
    }
})
@jwt_required()
def delete_board():
    logger = get_logger("to_do.log")
    data = request.get_json()

    if not data or 'board_id' not in data:
        return jsonify({
            "message": "Missing required fields",
            "success": False
        }), 400

    board_id = int(data['board_id'])
    user_id = get_jwt_identity()
    role = DbQuery.get_role(user_id)[0]

    if user_id and (role == 'admin' or role == 'super admin'):
        result = DbQuery.delete_board(board_id)
        logger.info(f"id = {user_id}, operation = delete_board, status = {result}, board_id = {board_id}")
        return jsonify({
            "message": "Доска удалена",
            "success": result
        }), 200
    else:
        logger.warning(f"id = {user_id}, operation = delete_board, status = You are not admin, board_id = {board_id}")
        return jsonify({
            "message": "You are not admin",
            "success": False
        }), 401

    @board_blueprint.route('', methods=['PATCH'])
    @swag_from({
        "parameters": [
            {
                "name": "Authorization",
                "in": "header",
                "type": "string",
                "required": True,
                "description": "Example:\"Bearer <JWT>\""
            },
            {
                "name": "body",
                "in": "body",
                "required": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "board_id": {"type": "integer"}
                    },
                    "required": ["board_id"]
                }
            }
        ],
        "responses": {
            "200": {
                "description": "Доска успешно восстановлена",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Доска успешно восстановлена",
                            "success": True
                        }
                    }
                }
            },
            "400": {
                "description": "Неверный формат запроса",
                "content": {
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
                "content": {
                    "application/json": {
                        "example": {
                            "message": "The token is incorrect",
                            "success": False
                        }
                    }
                }
            }
        }
    })
    @jwt_required()
    def recover_board():
        logger = get_logger("to_do.log")
        data = request.get_json()

        if not data or 'board_id' not in data:
            return jsonify({
                "message": "Missing required fields",
                "success": False
            }), 400

        board_id = int(data['board_id'])
        user_id = get_jwt_identity()
        role = DbQuery.get_role(user_id)[0]

        if user_id and (role == 'admin' or role == 'super admin'):
            result = DbQuery.recover_board(board_id)
            logger.info(f"id = {user_id}, operation = recover_board, status = {result}, board_id = {board_id}")
            return jsonify({
                "message": "Доска успешно восстановлена",
                "success": result
            }), 200
        else:
            logger.warning(
                f"id = {user_id}, operation = recover_board, status = You are not admin, board_id = {board_id}")
            return jsonify({
                "message": "You are not admin",
                "success": False
            }), 401