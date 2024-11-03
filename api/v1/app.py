#!/usr/bin/env python3
"""
Flask Application for Service.

This script sets up a Flask web application that provides RESTful APIs for an event service,
with integrated Swagger documentation using Flasgger.
"""

import asyncio
import logging
import os
from typing import Any
from celery import Celery
from flask import Flask, jsonify, make_response
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
import flask_celery

from api.v1.views import app_views
from models.engine.mail_service import init_app as init_email_service

# Set up basic logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.propagate = False
# File logging setup for detailed logs
file_handler = logging.FileHandler('event_service.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    return celery


            
# Create the Flask application
app = Flask(__name__)
app.config['QR_CODE_DIR'] = os.getenv('QR_CODE_DIR', './qrcodes')



app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379/0',
    CELERY_RESULT_BACKEND='redis://localhost:6379/0'
)

celery = flask_celery.Celery(app)


# @celery.task
# def generate_bulk_pdf(data_list):
#     receipt = BulkQRcodePDF(data_list)

#     # Run the asynchronous method synchronously
#     receipt_stream = asyncio.run(receipt.create_receipt())
    # return receipt_stream

app.config['MAIL_SERVER'] = 'live.smtp.mailtrap.io'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'api'
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

init_email_service(app)

# Enable Cross-Origin Resource Sharing (CORS) for all routes
CORS(app, resources={r"/*": {"origins": "*"}})
SWAGGER_URL = '/v1/docs'
API_URL = "http://app.chaleapp.org/api-service/docs"

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'chale services'
    }
)

# Register Swagger UI blueprint
app.register_blueprint(swaggerui_blueprint)

# Register the blueprint for API routes
app.register_blueprint(app_views)


# Error Handlers for the Flask Application
@app.errorhandler(400)
def bad_request(error: Exception) -> Any:
    """
    Handles 400 Bad Request errors.
    ---
    responses:
      400:
        description: The server could not understand the request due to invalid syntax.
    """
    logger.error('400 Bad Request: %s', error)
    return make_response(
        jsonify({
            'success': False,
            'status': 'Error',
            'message': str(error),
            'details': 'Bad Request - The server could not understand the request due to invalid syntax.'
        }), 400
    )


@app.errorhandler(401)
def unauthorized(error: Exception) -> Any:
    """
    Handles 401 Unauthorized errors.
    ---
    responses:
      401:
        description: The client must authenticate itself to get the requested response.
    """
    logger.error('401 Unauthorized: %s', error)
    return make_response(
        jsonify({
            'success': False,
            'status': 'Error',
            'message': str(error),
            'status': 'Error',
            'details': f'Unauthorized - The client must authenticate itself to get the requested response. {error}'
        }), 401
    )


@app.errorhandler(403)
def forbidden(error: Exception) -> Any:
    """
    Handles 403 Forbidden errors.
    ---
    responses:
      403:
        description: The client does not have access rights to the requested content.
    """
    logger.error('403 Forbidden: %s', error)
    return make_response(
        jsonify({
            'success': False,
            'status': 'Error',
            'message': str(error),
            'status': 'Error',
            'details': 'Forbidden - The client does not have access rights to the requested content.'
        }), 403
    )


@app.errorhandler(404)
def not_found(error: Exception) -> Any:
    """
    Handles 404 Not Found errors.
    ---
    responses:
      404:
        description: The server cannot find the requested resource.
    """
    logger.error('404 Not Found: %s', error)
    return make_response(
        jsonify({
            'success': False,
            'status': 'Error',
            'message': str(error),
            'status': 'Error',
            'details': 'Not Found - The server cannot find the requested resource.'
        }), 404
    )


@app.errorhandler(405)
def method_not_allowed(error: Exception) -> Any:
    """
    Handles 405 Method Not Allowed errors.
    ---
    responses:
      405:
        description: The request method is known but has been disabled and cannot be used.
    """
    logger.error('405 Method Not Allowed: %s', error)
    return make_response(
        jsonify({
            'success': False,
            'status': 'Error',
            'message': str(error),
            'status': 'Error',
            'details': 'Method Not Allowed - The request method is known but has been disabled and cannot be used.'
        }), 405
    )


@app.errorhandler(500)
def internal_error(error: Exception) -> Any:
    """
    Handles 500 Internal Server Error errors.
    ---
    responses:
      500:
        description: The server has encountered a situation it doesn't know how to handle.
    """
    logger.error('500 Internal Server Error: %s', error)
    return make_response(
        jsonify({
            'success': False,
            'status': 'Error',
            'message': str(error),
            'status': 'Error',
            'details': 'Internal Server Error - The server has encountered a situation it doesn\'t know how to handle.'
        }), 500
    )


# Entry point for the Flask application
if __name__ == '__main__':
    # Get the host and port from environment variables, or use defaults
    host = os.environ.get('CHALE_SERVER_HOST', '0.0.0.0')
    port = int(os.environ.get('CHALE_SERVER_PORT', 7000))

    # Start the Flask application
    app.run(host=host, port=port,debug=True)
