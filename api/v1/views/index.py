import logging
import os
from flask import jsonify, make_response, send_from_directory

from api.v1.views import app_views

# Set up a logger for this module
logger = logging.getLogger(__name__)


@app_views.route('/status', methods=['GET'], strict_slashes=False)
def get_status():
    """
    Check the status of the Flask server.

    This endpoint tests the connection to the Flask server, providing a simple
    "Hello World" response to confirm that the server is operational.

    Returns:
        JSON: A JSON object containing:
            - status (str): The status of the server.
            - message (str): A greeting message.

    Responses:
        200 OK:
            The server is operational and responding to requests.

    Example Usage:
        GET /status
        Returns:
        {
            "status": "Ok",
            "message": "Hello World"
        }
    """
    return jsonify({
        'status': 'Ok',
        'message': 'Hello World'
    }), 200


@app_views.route('/health', methods=['GET'], strict_slashes=False)
def get_health():
    """
    Check the health of the database connection.

    This endpoint tests the connection to the database, returning a success status
    indicating whether the database is live.

    Returns:
        JSON: A JSON object containing:
            - success (bool): Status of the database connection.
            - is_live (bool): Indicates whether the database is live.

    Responses:
        200 OK:
            Successfully checked the database connection.

    Example Usage:
        GET /health
        Returns:
        {
            "success": true,
            "is_live": true
        }
    """
    from models import storage

    return jsonify({
        'success': True,
        'is_live': storage.is_live()
    }), 200


@app_views.route('/qr_code/<filename>')
def get_qr_code(filename):
    """
    Retrieve a QR code file.

    This endpoint serves a QR code file from the specified directory. It returns the
    file with the provided filename, allowing clients to download or display the QR code.

    Parameters:
        filename (str): The name of the QR code file to retrieve.

    Responses:
        200 OK:
            Successfully retrieved the QR code file.
        404 Not Found:
            The requested QR code file does not exist.

    Example Usage:
        GET /qr_code/sample_qr_code.png
    """
    return send_from_directory(os.getenv('QR_CODE_DIR'), filename)


@app_views.route('/docs/', methods=['GET'], strict_slashes=False)
def swagger_yaml():
    """
    Serve the Swagger documentation in YAML format.

    This endpoint returns the Swagger YAML documentation for the API, allowing clients
    to understand the available endpoints and their usage.

    Returns:
        Text: The Swagger YAML documentation for the API.

    Responses:
        200 OK:
            Successfully retrieved the Swagger YAML documentation.

    Example Usage:
        GET /docs/
    """
    # Replace with the path to your actual swagger.yaml file
    swagger_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docs', 'swagger.yaml')

    return make_response(open(swagger_file_path).read(), 200, {'Content-Type': 'text/yaml'})
