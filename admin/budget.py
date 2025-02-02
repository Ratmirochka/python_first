import flask_jwt_extended
from flask import Flask, request, Blueprint, jsonify
from dotenv import load_dotenv, find_dotenv
from flasgger import swag_from
from flask_jwt_extended import jwt_required, JWTManager, get_jwt_identity
import json
import sys
import os

sys.path.append('../')
from bl.bl import AdminBl
from dal.budget_query import DbQuery
from logs.loguru_conf import get_logger

load_dotenv(find_dotenv())

budget_blueprint = Blueprint('budget', __name__)


@budget_blueprint.route('', methods=['GET'])
@swag_from({
    "parameters": [
        {
            "name": "Authorization",
            "in": "header",
            "type": "string",
            "required": True,
            "description": "Example:\"Bearer <JWT>\""
        }
    ],
    "responses": {
        "200": {
            "description": "Успешное получение бюджета",
            "examples": {
                "application/json": {
                    "example": {
                        "payments": [
                            {"pay_id": 1, "name_for_make": "Hairulin Bulat", "name_who_make": "Akhmedshin Ratmir",
                             "values": 10000, "date_for_period": "2024-01-30", "date_of_pay": "2024-01-30", "summ": 150}
                        ],
                        "expenses": [
                            {"expens_id": 1, "who_expens": "ratmir", "who_write": "ratmir", "values": 5000,
                             "purpose": "Зарплата", "date_of_exp": "2023-01-15", "summ": 2000}
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
def get_budget():
    logger = get_logger("budget.log")
    user_id = get_jwt_identity()

    if user_id:
        try:
            payments = DbQuery.get_payments()
            expenses = DbQuery.get_expenses()
            logger.info(f"id = {user_id}, operation = get_budget, status = succes")
            return jsonify({
                "payments": payments,
                "expenses": expenses,
                "success": True
            }), 200
        except Exception as e:
            logger.error(f"id = {user_id}, operation = get_budget, status = Server error - {e}")
            return jsonify({
                "message": "Server error",
                "success": False
            }), 500
    else:
        logger.warning(f"id = {user_id}, operation = get_budget, status = The token is incorrect")
        return jsonify({
            "message": "The token is incorrect",
            "success": False
        }), 401


@budget_blueprint.route('/payments', methods=['POST'])
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
                    "for_user_id": {"type": "integer"},
                    "value": {"type": "number"},
                    "date_for_period": {"type": "string", "format": "date"}
                },
                "required": ["for_user_id", "value", "date_for_period"]
            }
        }
    ],
    "responses": {
        "200": {
            "description": "Оплата успешно добавлена",
            "examples": {
                "application/json": {
                    "example": {
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
@jwt_required()
def add_payment():
    logger = get_logger("budget.log")

    data = request.get_json()

    if not data or 'for_user_id' not in data or 'value' not in data or 'date_for_period' not in data:
        return jsonify({
            "message": "Missing required fields",
            "success": False
        }), 400

    user_id = get_jwt_identity()

    if user_id:
        role = DbQuery.get_role(user_id)[0]
        if role == 'super admin':
            try:
                result = DbQuery.add_payment(user_id, data['for_user_id'], data['value'], data['date_for_period'])
                logger.info(
                    f"id = {user_id}, operation = add_payment, status = {result}, for_user_id = {data['for_user_id']}, value = {data['value']}, period = {data['date_for_period']}")
                return jsonify({
                    "success": result
                }), 200
            except Exception as e:
                logger.error(
                    f"id = {user_id}, operation = add_payment, status = Server error - {e}, for_user_id = {data['for_user_id']}, value = {data['value']}, period = {data['date_for_period']}")
                return jsonify({
                    "message": "Server error",
                    "success": False
                }), 500
        else:
            logger.error(
                f"id = {user_id}, operation = add_payment, status = You are not super admin, for_user_id = {data['for_user_id']}, value = {data['value']}, period = {data['date_for_period']}")
            return jsonify({
                "message": "You are not super admin",
                "success": False
            }), 401
    else:
        logger.error(
            f"id = {user_id}, operation = add_payment, status = The token is incorrect, for_user_id = {data['for_user_id']}, value = {data['value']}, period = {data['date_for_period']}")
        return jsonify({
            "message": "The token is incorrect",
            "success": False
        }), 401


@budget_blueprint.route('/expenses', methods=['POST'])
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
                    "token": {"type": "string"},
                    "for_user_id": {"type": "integer"},
                    "value": {"type": "number"},
                    "purpose": {"type": "string"}
                },
                "required": ["token", "for_user_id", "value", "purpose"]
            }
        }
    ],
    "responses": {
        "200": {
            "description": "Расход успешно добавлен",
            "examples": {
                "application/json": {
                    "example": {
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
@jwt_required()
def add_expens():
    logger = get_logger("budget.log")

    data = request.get_json()

    if not data or 'for_user_id' not in data or 'value' not in data or 'purpose' not in data:
        return jsonify({
            "message": "Missing required fields",
            "success": False
        }), 400

    usert_id = get_jwt_identity()

    if user_id:
        role = DbQuery.get_role(user_id)[0]
        if role == 'super admin':
            try:
                result = DbQuery.add_expens(user_id, data['for_user_id'], data['value'], data['purpose'])
                logger.info(
                    f"id = {user_id}, operation = add_expens, status = {result}, for_user_id = {data['for_user_id']}, value = {data['value']}, pepose = {data['purpose']}")
                return jsonify({
                    "success": result
                }), 200
            except Exception as e:
                logger.error(
                    f"id = {user_id}, operation = add_expens, status = Server error - {e}, for_user_id = {data['for_user_id']}, value = {data['value']}, pepose = {data['purpose']}")
                return jsonify({
                    "message": "Server error",
                    "success": False
                }), 500
        else:
            logger.warning(
                f"id = {user_id}, operation = add_expens, status = You are not super admin, for_user_id = {data['for_user_id']}, value = {data['value']}, pepose = {data['purpose']}")
            return jsonify({
                "message": "You are not super admin",
                "success": False
            }), 401
    else:
        logger.error(
            f"id = {user_id}, operation = add_expens, status = The token is incorrect, for_user_id = {data['for_user_id']}, value = {data['value']}, pepose = {data['purpose']}")
        return jsonify({
            "message": "The token is incorrect",
            "success": False
        }), 401

@budget_blueprint.route('/version_id', methods=['GET'])
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
                    "token": {"type": "string"}
                },
                "required": ["token"]
            }
        }
    ],
    "responses": {
        "200": {
            "description": "Успешное получение номеров версий",
            "examples": {
                "application/json": {
                    "example": {
                        "payments": [
                            {"pay_id": 1, "name_for_make": "Hairulin Bulat", "name_who_make": "Akhmedshin Ratmir",
                             "values": 10000, "date_for_period": "2024-01-30", "date_of_pay": "2024-01-30", "summ": 150, "version_id": 23}
                        ],
                        "expenses": [
                            {"expens_id": 1, "who_expens": "ratmir", "who_write": "ratmir", "values": 5000,
                             "purpose": "Зарплата", "date_of_exp": "2023-01-15", "summ": 2000, "version_id": 23}
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
def get_version_id():
    logger = get_logger("budget.log")

    user_id = get_jwt_identity()

    if user_id:
        role = DbQuery.get_role(user_id)[0]
        if role == 'super admin':
            try:
                result = DbQuery.get_version_id()
                logger.info(f"id = {user_id}, operation = get_version_id, status = {result}")
                return jsonify({
                    "success": result
                }), 200
            except Exception as e:
                logger.error(f"id = {user_id}, operation = get_version_id, status = server error - {e}")
                return jsonify({
                    "message": "Server error",
                    "success": False
                }), 500
        else:
            logger.warning(f"id = {user_id}, operation = get_version_id, status = You are not super admin")
            return jsonify({
                "message": "You are not super admin",
                "success": False
            }), 401
    else:
        logger.error(f"id = {user_id}, operation = get_version_id, status = The token is incorrect")
        return jsonify({
            "message": "The token is incorrect",
            "success": False
        }), 401


@budget_blueprint.route('/for_admins', methods=['GET'])
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
                    "token": {"type": "string"},
                    "version_id": {"type": "integer"}
                },
                "required": ["token", "version_id"]
            }
        }
    ],
    "responses": {
        "200": {
            "description": "Успешное получение бюджета",
            "examples": {
                "application/json": {
                    "example": {
                        "payments": [
                            {"pay_id": 1, "name_for_make": "Hairulin Bulat", "name_who_make": "Akhmedshin Ratmir",
                             "values": 10000, "date_for_period": "2024-01-30", "date_of_pay": "2024-01-30", "summ": 150, "version_id": 23}
                        ],
                        "expenses": [
                            {"expens_id": 1, "who_expens": "ratmir", "who_write": "ratmir", "values": 5000,
                             "purpose": "Зарплата", "date_of_exp": "2023-01-15", "summ": 2000, "version_id": 23}
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
def get_budget_for_admin():
    logger = get_logger("budget.log")

    data = request.get_json()

    if not data or 'version_id' not in data:
        return jsonify({
            "message": "Missing required fields",
            "success": False
        }), 400

    version_id = int(data['version_id'])

    user_id = get_jwt_identity()

    if user_id:
        role = DbQuery.get_role(user_id)[0]
        if role == 'super admin':
            try:
                payments = DbQuery.get_payments(version_id)
                expenses = DbQuery.get_expenses(version_id)
                logger.info(f"id = {user_id}, operation = get_budget, status = succes")
                return jsonify({
                    "payments": payments,
                    "expenses": expenses,
                    "success": True
                }), 200
            except Exception as e:
                logger.error(f"id = {user_id}, operation = get_budget, status = Server error - {e}")
                return jsonify({
                    "message": "Server error",
                    "success": False
                }), 500
        else:
            logger.warning(f"id = {user_id}, operation = get_version_id, status = You are not super admin")
            return jsonify({
                "message": "You are not super admin",
                "success": False
            }), 401
    else:
        logger.warning(f"id = {user_id}, operation = get_budget, status = The token is incorrect")
        return jsonify({
            "message": "The token is incorrect",
            "success": False
        }), 401