#!/usr/bin/env python3
# Load the API key from the environment
import os
from datetime import datetime
from functools import wraps

from dotenv import load_dotenv
from flask import abort, request

load_dotenv()

API_KEY = os.getenv("API_KEY")


def require_api_key(func):
    def wrapper(*args, **kwargs):
        # Get API key from request headers
        api_key = request.headers.get("X-API-Key")

        # Check if the API key is valid
        if api_key != API_KEY:
            abort(401, description="Unauthorized: Invalid API Key")

        # Proceed if the key is valid
        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


def protected():
    def admin_decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Get API key from request headers
            api_key = request.headers.get("X-API-Key")

            # Check if the API key is valid
            if api_key != API_KEY:
                abort(401, description="Unauthorized: Invalid API Key")
            else:
                return fn(*args, **kwargs)

        return wrapper

    return admin_decorator


import secrets
import string


def generate_api_key(length=32):
    """
    Generates a secure random API key.

    Args:
        length (int): The length of the API key to generate.

    Returns:
        str: A random API key of the specified length.
    """
    # Create a set of characters to choose from (digits, uppercase, lowercase)
    characters = string.ascii_letters + string.digits
    api_key = ''.join(secrets.choice(characters) for _ in range(length))
    return api_key


def generate_token(length=6):
    characters = string.ascii_letters + string.digits
    token = ''.join(secrets.choice(characters) for _ in range(length))
    return token


def format_date_time(date_str, time_str):
    # Combine date and time into a single string
    combined_str = f"{date_str} {time_str}"

    # Parse the combined string to a datetime object
    dt = datetime.strptime(combined_str, "%Y-%m-%d %H:%M:%S")

    # Format to the desired output
    formatted_date_time = dt.strftime("%B %d, %Y %I:%M%p GMT")
    return formatted_date_time
