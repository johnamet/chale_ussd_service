#!/usr/bin/env python3

import re
from api.v1.views import app_views
import logging
from flask import jsonify, request, abort

from models.temp_user import TempUser



def validate_data(data):
    errors = []
    # Basic validation
    if not data.get("first-name"):
        errors.append("First name is required.")
    if not data.get("last-name"):
        errors.append("Last name is required.")
    if not data.get("your-number") or not re.match(r'^[0-9]{10,15}$', data.get("your-number")):
        errors.append("A valid phone number is required.")
    if not data.get("your-email") or not re.match(r"[^@]+@[^@]+\.[^@]+", data.get("your-email")):
        errors.append("A valid email address is required.")
    if not data.get("your-instagram"):
        errors.append("Instagram handle is required.")
    return errors



