import logging
import os
from flask import abort, jsonify, make_response, send_file, send_from_directory

from api.v1.views import app_views
from models import cache
from models.engine.receipt import Receipt

# Set up a logger for this module
logger = logging.getLogger(__name__)


@app_views.route('/', methods=['GET'], strict_slashes=False)
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
        'redis': cache.ping()
    }), 200


@app_views.route('/qr_code/<filename>')
async def get_qr_code(filename):
    """
    Retrieve and serve a QR code receipt PDF asynchronously.

    This endpoint generates and serves a QR code receipt PDF file directly from memory.
    If the filename corresponds to a valid ticket in the cache, it will generate a PDF
    receipt for download or display. 

    Parameters:
        filename (str): Unique identifier for the ticket data, used to generate the receipt.

    Returns:
        200 OK: Returns the QR code receipt as a downloadable PDF file.
        404 Not Found: The requested ticket data does not exist.

    Example Usage:
        GET /qr_code/sample_qr_code.pdf
    """
    try:
        # Generate the receipt using the Receipt class
        print(filename)
        receipt = Receipt(cache.hget_all(filename))
        receipt_stream = await receipt.create_receipt()

        # Return the PDF as a downloadable file
        return send_file(
            receipt_stream,
            download_name=f"{filename}_receipt.pdf",
            mimetype='application/pdf'
        )

        # return jsonify(f"Hello World, {filename}"), 200

    except KeyError as e:
        # Handle case where ticket data doesn't exist in the cache
        abort(404, description=f"The requested ticket data was not found. {e}")
    except Exception as e:
        # General exception handling
        abort(500, description=f"An error occurred while generating the receipt: {str(e)}")
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
