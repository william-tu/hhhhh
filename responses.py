# -*- coding:utf-8 -*-
from flask import jsonify


def not_found(message):
    response = jsonify({'error': 'not found', 'message': message})
    response.status_code = 404
    return response


def bad_request(message):
    response = jsonify({'error':'bad request','message':message})
    response.status_code = 400
    return response