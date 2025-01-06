from flask import Flask, request, Blueprint, jsonify
from dotenv import load_dotenv, find_dotenv
from flasgger import swag_from
import json
import sys
import os

sys.path.append('../')
from bl.bl import AdminBl
from dal.budget_query import DbQuery

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
    data = request.get_json()

    if (not data or 'token' not in data):
        return jsonify({
            "message": "Missing required fields",
            "success": False
        }), 400

    token = data['token']

    user_id = AdminBl.decode_jwt(token, os.getenv('SECRET_KEY'))

    if user_id:
        payments = DbQuery.get_payments()
        expenses = DbQuery.get_expenses()
        return jsonify({
            "payments": payments,
            "expenses": expenses,
            "success": True
        }), 200
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
    data = request.get_json()

    if (not data or 'token' not in data or 'for_user_id' not in data
        or 'value' not in data or 'date_for_period' not in data):
        return jsonify({
            "message": "Missing required fields",
            "success": False
        }), 400

    token = data['token']
    for_user_id = data['for_user_id']
    value = data['value']
    date_for_period = data['date_for_period']

    user_id = AdminBl.decode_jwt(token, os.getenv('SECRET_KEY'))

    if user_id:
        if DbQuery.get_role(user_id)[0] == 'super admin':
            last_sum = DbQuery.get_last_sum()[0]
            result = DbQuery.add_payment(user_id, for_user_id, value, date_for_period, last_sum)
            return jsonify({
                "success": result
            }), 200
        return jsonify({
            "message": "You are not super admin",
            "success": False
        }), 401
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
    data = request.get_json()

    if (not data or 'token' not in data or 'for_user_id' not in data
        or 'value' not in data or 'purpose' not in data):
        return jsonify({
            "message": "Missing required fields",
            "success": False
        }), 400

    token = data['token']
    for_user_id = data['for_user_id']
    value = data['value']
    purpose = data['purpose']

    user_id = AdminBl.decode_jwt(token, os.getenv('SECRET_KEY'))

    if user_id:
        if DbQuery.get_role(user_id)[0] == 'super admin':
            last_exp_sum = DbQuery.get_last_exp_sum()[0]
            print(last_exp_sum)
            result = DbQuery.add_expens(user_id, for_user_id, value, last_exp_sum, purpose)
            return jsonify({
                "success": result
            }), 200
        return jsonify({
            "message": "You are not super admin",
            "success": False
        }), 401
    return jsonify({
        "message": "The token is incorrect",
        "success": False
    }), 401