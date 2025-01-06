from flask import Flask, request, Blueprint, jsonify
from dotenv import load_dotenv, find_dotenv
from flasgger import swag_from
import json
import sys
import os

sys.path.append('../')
from bl.bl import AdminBl
from dal.budget_query import DbQuery
from logs.loguru_conf import get_logger

load_dotenv(find_dotenv())

budget_blueprint = Blueprint('budget', __name__)



@budget_blueprint.route('/get_budget', methods=['POST'])
@swag_from({
    "parameters": [
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
            "description": "Успешное получение бюджета",
            "examples": {
                "application/json": {
                    "example": {
                        "payments": [
                            {"pay_id": 1, "name_for_make": "Hairulin Bulat", "name_who_make": "Akhmedshin Ratmir", "values": 10000, "date_for_period": "2024-01-30", "date_of_pay": "2024-01-30", "summ": 150}
                        ],
                        "expenses": [
                            {"expens_id": 1, "who_expens": "ratmir", "who_write": "ratmir", "values": 5000, "purpose": "Зарплата", "date_of_exp": "2023-01-15", "summ": 2000}
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
def get_budget():

    logger = get_logger("budget.log")

    logger.info("Запрос на получение бюджета")

    data = request.get_json()

    if not data or 'token' not in data:
        logger.warning("Неверный формат запроса: отсутствует токен")
        return jsonify({
            "message": "Missing required fields",
            "success": False
        }), 400

    token = data['token']
    logger.debug(f"Получен токен: {token}")

    user_id = AdminBl.decode_jwt(token, os.getenv('SECRET_KEY'))

    if user_id:
        logger.info(f"Пользователь с ID {user_id} прошел аутентификацию")
        try:
            print("before")
            payments = DbQuery.get_payments()
            expenses = DbQuery.get_expenses()
            return jsonify({
                "payments": payments,
                "expenses": expenses,
                "success": True
            }), 200
        except Exception as e:
            logger.error(f"Ошибка получения бюджета: {e}")
            return jsonify({
                "message": "Server error",
                "success": False
            }), 500
    else:
        logger.warning("Неверный токен")
        return jsonify({
            "message": "The token is incorrect",
            "success": False
        }), 401

@budget_blueprint.route('/add_payment', methods=['POST'])
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
                    "for_user_id": {"type": "integer"},
                    "value": {"type": "number"},
                    "date_for_period": {"type": "string", "format": "date"}
                },
                "required": ["token", "for_user_id", "value", "date_for_period"]
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
def add_payment():
    logger = get_logger("budget.log")
    logger.info("Запрос на добавление платежа")

    data = request.get_json()

    if not data or 'token' not in data or 'for_user_id' not in data or 'value' not in data or 'date_for_period' not in data:
        logger.warning("Неверный формат запроса: отсутствуют обязательные поля")
        return jsonify({
            "message": "Missing required fields",
            "success": False
        }), 400

    token = data['token']
    logger.debug(f"Получен токен: {token}")

    user_id = AdminBl.decode_jwt(token, os.getenv('SECRET_KEY'))

    if user_id:
        logger.info(f"Пользователь с ID {user_id} прошел аутентификацию")
        role = DbQuery.get_role(user_id)[0]
        if role == 'super admin':
            logger.debug(f"Пользователь {user_id} имеет роль: {role}")
            try:
                last_sum = DbQuery.get_last_sum()[0]
                logger.debug(f"Последняя сумма платежа: {last_sum}")
                result = DbQuery.add_payment(user_id, data['for_user_id'], data['value'], data['date_for_period'],
                                             last_sum)
                logger.info(f"Платеж успешно добавлен: {result}")
                return jsonify({
                    "success": result
                }), 200
            except Exception as e:
                logger.error(f"Ошибка добавления платежа: {e}")
                return jsonify({
                    "message": "Server error",
                    "success": False
                }), 500
        else:
            logger.warning(f"Пользователь {user_id} не является супер-админом")
            return jsonify({
                "message": "You are not super admin",
                "success": False
            }), 401
    else:
        logger.warning("Неверный токен")
        return jsonify({
            "message": "The token is incorrect",
            "success": False
        }), 401



@budget_blueprint.route('/add_expens', methods=['POST'])
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
def add_expens():
    logger = get_logger("budget.log")
    logger.info("Запрос на добавление расхода")

    data = request.get_json()

    if not data or 'token' not in data or 'for_user_id' not in data or 'value' not in data or 'purpose' not in data:
        logger.warning("Неверный формат запроса: отсутствуют обязательные поля")
        return jsonify({
            "message": "Missing required fields",
            "success": False
        }), 400

    token = data['token']
    logger.debug(f"Получен токен: {token}")

    user_id = AdminBl.decode_jwt(token, os.getenv('SECRET_KEY'))

    if user_id:
        logger.info(f"Пользователь с ID {user_id} прошел аутентификацию")
        role = DbQuery.get_role(user_id)[0]
        if role == 'super admin':
            logger.debug(f"Пользователь {user_id} имеет роль: {role}")
            try:
                last_exp_sum = DbQuery.get_last_exp_sum()[0]
                logger.debug(f"Последняя сумма расходов: {last_exp_sum}")
                result = DbQuery.add_expens(user_id, data['for_user_id'], data['value'], last_exp_sum, data['purpose'])
                logger.info(f"Расход успешно добавлен: {result}")
                return jsonify({
                    "success": result
                }), 200
            except Exception as e:
                logger.error(f"Ошибка добавления расхода: {e}")
                return jsonify({
                    "message": "Server error",
                    "success": False
                }), 500
        else:
            logger.warning(f"Пользователь {user_id} не является супер-админом")
            return jsonify({
                "message": "You are not super admin",
                "success": False
            }), 401
    else:
        logger.warning("Неверный токен")
        return jsonify({
            "message": "The token is incorrect",
            "success": False
        }), 401
