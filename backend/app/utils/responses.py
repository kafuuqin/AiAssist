from flask import jsonify


def ok(data=None, status=200):
    payload = {"data": data}
    return jsonify(payload), status


def error(message, status=400):
    return jsonify({"message": message, "status": status}), status
