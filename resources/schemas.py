#!/usr/bin/python
# -*- coding: utf-8 -*-

SchemaUserToken = {
    "type": "object",
    "properties": {
        "token": {"type": "string"},
    },
    "required": ["token"]
}

SchemaRegisterUser = {
    "type": "object",
    "properties": {
        "username": {"type": "string"},
        "password": {"type": "string"},
        "email": {"type": "string"},
        "name": {"type": "string"},
        "surname": {"type": "string"}
    },
    "required": ["username", "password", "email", "name", "surname"]
}
SchemaGameEnd = {
    "type": "object",
    "properties": {
        "user1_id": {"type": "integer"},
        "user1_score": {"type": "integer"},
        "user2_id": {"type": "integer"},
        "user2_score": {"type": "integer"}
    },
    "required": ["user1_id", "user1_score", "user2_id", "user2_score"]
}
