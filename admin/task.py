from flask_jwt_extended import jwt_required, JWTManager, get_jwt_identity
from flask import Flask, request, Blueprint, jsonify
from dotenv import load_dotenv, find_dotenv
from flasgger import swag_from
import json
import sys
import os

sys.path.append('../')
from dal.task_query import DbQuery
from logs.loguru_conf import get_logger

load_dotenv(find_dotenv())

task_blueprint = Blueprint('boards/tasks', __name__)

@task_blueprint.route('', methods=['GET'])
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
                    "user_id": {"type": "integer"}
                },
                "required": ["board_id", "user_id"]
            }
        }
    ],
    "responses": {
        "200": {
            "description": "Успешное получение задач",
            "examples": {
                "application/json": {
                    "example": {
                        "message": [
                            {
                                "task_id": 1,
                                "title": "Task 1",
                                "description": "Task description",
                                "deadline": "2023-12-31",
                                "status_name": "In progress",
                                "responsible_name": "John Doe"
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
def get_tasks():
    logger = get_logger("to_do.log")
    data = request.get_json()

    if not data or 'board_id' not in data or 'user_id' not in data:
        return jsonify({
            "message": "Missing required fields",
            "success": False
        }), 400

    board_id = data['board_id']
    user_id = data['user_id']

    correct = get_jwt_identity()

    if correct:
        logger.info(f"id = {correct}, operation = get_tasks, status = succes, user_id = {user_id}, board_id = {board_id}")
        return jsonify({
            "message": DbQuery.get_user_tasks(board_id, user_id),
            "success": True
        }), 200
    else:
        logger.warning(f"id = {correct}, operation = get_tasks, status = the token is incorrect, user_id = {user_id}, board_id = {board_id}")
        return jsonify({
            "message": "The token is incorrect",
            "success": False
        }), 401

@task_blueprint.route('', methods=['POST'])
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
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "deadline": {"type": "string", "format": "date"},
                    "board_id": {"type": "integer"},
                    "status_id": {"type": "integer"},
                    "curr_user_id": {"type": "integer"}
                },
                "required": ["title", "description", "deadline", "board_id", "status_id", "curr_user_id"]
            }
        }
    ],
    "responses": {
        "200": {
            "description": "Задача успешно создана",
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
def create_task():
    logger = get_logger("to_do.log")
    data = request.get_json()

    if (not data or 'title' not in data
            or 'description' not in data or 'deadline' not in data
            or 'board_id' not in data or 'status_id' not in data or 'curr_user_id' not in data):
        return jsonify({
            "message": "Missing required fields",
            "success": False
        }), 400

    title = data['title']
    description = data['description']
    deadline = data['deadline']
    board_id = data['board_id']
    status_id = data['status_id']
    curr_user_id = data['curr_user_id']

    user_id = get_jwt_identity()
    if user_id:
        role = DbQuery.get_role_in_board(user_id, board_id)[0]
        global_role = DbQuery.get_role(user_id)[0]
        if(role == "admin" or global_role == "super admin"):
            task_id = DbQuery.create_task(title, description, deadline, board_id, status_id)
            success = DbQuery.assign_responsible(task_id, curr_user_id)
            logger.info(f"id = {user_id}, operation = create_task, status = {success}, user = {curr_user_id}, board_id = {board_id}, title = {title}, description = {description}, deadline = {deadline}, status_id = {status_id}")
            return jsonify({
                "success": success
            }), 200
        logger.error(f"id = {user_id}, operation = create_task, status = You are not admin, user = {curr_user_id}, board_id = {board_id}, title = {title}, description = {description}, deadline = {deadline}, status_id = {status_id}")
        return jsonify({
            "message": "You are not admin",
            "success": False
    }), 401
    logger.warning(f"id = {user_id}, operation = create_task, status = The token is incorrect, user = {curr_user_id}, board_id = {board_id}, title = {title}, description = {description}, deadline = {deadline}, status_id = {status_id}")
    return jsonify({
        "message": "The token is incorrect",
        "success": False
    }), 401


@task_blueprint.route('', methods=['DELETE'])
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
                    "task_id": {"type": "integer"}
                },
                "required": ["task_id", "integer"]
            }
        }
    ],
    "responses": {
        "200": {
            "description": "Задача успешно удалена",
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
def delete_task():
    logger = get_logger("to_do.log")
    data = request.get_json()

    if (not data or 'task_id' not in data):
        return jsonify({
            "message": "Missing required fields",
            "success": False
        }), 400

    task_id = data['task_id']
    print(task_id)
    user_id = get_jwt_identity()

    if user_id:
        role = DbQuery.get_role(user_id)[0]
        if (role == "admin" or role == "super admin"):
            result = DbQuery.delete_tasks(task_id)
            logger.info(
                f"id = {user_id}, operation = delete_tasks, status = {result}, task_id = {task_id}")
            return jsonify({
                "success": result
            }), 200
        logger.error(
            f"id = {user_id}, operation = delete_tasks, status = You are not admin, task_id = {task_id}")
        return jsonify({
            "message": "You are not admin",
            "success": False
        }), 401
    logger.warning(
        f"id = {user_id}, operation = delete_tasks, status = The token is incorrect, task_id = {task_id}")
    return jsonify({
        "message": "The token is incorrect",
        "success": False
    }), 401


@task_blueprint.route('', methods=['PATCH'])
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
                    "task_id": {"type": "integer"}
                },
                "required": ["task_id", "integer"]
            }
        }
    ],
    "responses": {
        "200": {
            "description": "Задача успешно востановлена",
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
def recover_task():
    logger = get_logger("to_do.log")
    data = request.get_json()
    print(data)
    if (not data or 'tasks_id' not in data):
        return jsonify({
            "message": "Missing required fields",
            "success": False
        }), 400

    task_id = data['tasks_id']
    user_id = get_jwt_identity()

    if user_id:
        role = DbQuery.get_role(user_id)[0]
        if (role == "admin" or role == "super admin"):
            result = DbQuery.recover_tasks(task_id)
            logger.info(
                f"id = {user_id}, operation = recovery_task, status = {result}, task_id = {task_id}")
            return jsonify({
                "success": result
            }), 200
        logger.error(
            f"id = {user_id}, operation = recovery_task, status = You are not admin, task_id = {task_id}")
        return jsonify({
            "message": "You are not admin",
            "success": False
        }), 401
    logger.warning(
        f"id = {user_id}, operation = delete_tasks, status = The token is incorrect, task_id = {task_id}")
    return jsonify({
        "message": "The token is incorrect",
        "success": False
    }), 401

