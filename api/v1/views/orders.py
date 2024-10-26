#!/usr/bin/env python3

import logging
from flask import abort, jsonify, request

from api.v1.views import app_views
from models.engine.qr_code_engine import QrCodeEngine
from models.order import Order
from models.tickets import Ticket
from models.user import User
from utils.util import protected

# Set up a logger for this module
logger = logging.getLogger(__name__)


@app_views.route('/orders', methods=['GET'], strict_slashes=False)
@protected()
def get_orders():
    """
    Retrieve paginated orders from the database.

    This route fetches orders from the database with optional pagination parameters,
    allowing clients to retrieve data in smaller, manageable chunks. If `page` and
    `page_size` are not provided, the default pagination values are applied.

    Query Parameters:
        - page (int, optional): The page number to retrieve. Default is 1.
        - page_size (int, optional): The number of orders per page. Default is 10.

    Returns:
        JSON: A JSON object containing:
            - success (bool): Status of the request.
            - data (list): A list of order objects in dictionary format for the specified page.
            - page (int): The current page number.
            - page_size (int): The number of orders per page.
            - total_orders (int): The total number of orders available in the database.
            - total_pages (int): The calculated total number of pages based on `page_size`.
            - message (str): Informational message indicating the retrieval status.

    Responses:
        200 OK:
            Successfully retrieved orders with pagination applied.
        400 Bad Request:
            Invalid pagination parameters. Occurs if `page` or `page_size` is not an integer.
        500 Internal Server Error:
            An error occurred while retrieving orders.

    Example Usage:
        GET /orders?page=2&page_size=5
        Retrieves the second page of orders with 5 orders per page.

    Logs:
        Logs any exceptions raised during the process with relevant error messages.

    """
    try:
        # Extract pagination parameters from query string with default values
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))

        # Validate pagination parameters
        if page < 1 or page_size < 1:
            raise ValueError("Page and page_size must be positive integers.")

        # Calculate starting and ending indices for pagination
        start = (page - 1) * page_size
        end = start + page_size

        # Fetch all orders and apply slicing for pagination
        all_orders = Order.all(page=page,
                               page_size=page_size)  # Retrieve all orders (assuming Order.all() returns a list)
        # Calculate total pages
        total_orders = Order.count()
        total_pages = (total_orders + page_size - 1) // page_size

        # Build the response JSON
        response = {
            'success': True,
            'data': all_orders,
            'page': page,
            'page_size': page_size,
            'total_orders': total_orders,
            'total_pages': total_pages,
            'message': 'Orders retrieved successfully'
        }

        return jsonify(response), 200

    except ValueError as ve:
        # Log and return error response for invalid pagination parameters
        logger.error(f"Invalid pagination parameters: {ve}")
        return jsonify({
            'success': False,
            'message': 'Invalid pagination parameters. Page and page_size should be positive integers.'
        }), 400

    except Exception as e:
        # Log and return error response for general exceptions
        logger.error(f"Failed to retrieve orders: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to retrieve orders',
            'error': str(e)
        }), 500


@app_views.route('/order', methods=['POST'], strict_slashes=False)
@protected()
def create_order():
    """
    Create a new order, generate a QR code, and associate a ticket with the order.
    
    This route handles creating an order and associating it with a generated QR code and ticket.
    It accepts a JSON payload with the order details and performs necessary validations, 
    including checking if the user exists or creating a new user as needed.
    
    JSON Payload:
        - event_name (str): Name of the event (required).
        - user_name (str): Name of the user placing the order (required).
        - price (float): Price of the ticket (required).
        - phone (str): User's phone number, used for reference and QR code generation (required).
        - ticket_type (str): Type of ticket being ordered (required).
        - reference (str): Payment reference number (optional, for tracking purposes).
    
    Returns:
        JSON: A JSON object containing:
            - success (bool): Status of the request.
            - qr_code_url (str): The URL of the generated QR code.
            - message (str): Informational message indicating the order creation status.
    
    Responses:
        201 Created:
            Successfully created the order and generated a QR code.
        400 Bad Request:
            Missing required fields in the request payload.
        500 Internal Server Error:
            An error occurred while creating the order.
    
    Example Usage:
        POST /order
        {
            "event_name": "Concert 2024",
            "user_name": "John Doe",
            "price": 50.0,
            "phone": "1234567890",
            "ticket_type": "VIP",
            "reference": "ABC12345"
        }
        This example creates an order for a VIP ticket to "Concert 2024" for the user "John Doe".

    Logs:
        Logs any exceptions raised during the order creation process with relevant error messages.
    """
    try:
        # Parse JSON payload from the request
        data = request.get_json()

        # Extract and validate required fields
        event_name = data.get('event_name')
        user_name = data.get('user_name')
        price = data.get('price')
        phone = data.get('phone')
        ticket_type = data.get('ticket_type')
        reference = data.get('reference')

        # Check if all required fields are provided
        if not all([event_name, user_name, price, phone, ticket_type]):
            abort(400, description="Missing required fields in the request.")

        # Check if the user exists; if not, create a new user
        user = User.get(phone)
        if not user:
            user = User(id=phone, phone=phone, password=phone, country_id=1, name=user_name, email=str(phone))
            user.save()

        # Create and save a ticket associated with the order
        ticket = Ticket(title=ticket_type, price=price, entries_allowed_per_ticket=1, quantity=1)
        ticket.save()  # Save ticket to generate ticket.id

        # Generate the QR code for the order
        qr_code_engine = QrCodeEngine(phone)
        qr_code_url, qr_code_name = qr_code_engine.generate_code()

        # Create and save the order with the generated ticket_id and QR code
        order = Order(
            user_id=phone,
            ticket_id=ticket.id,
            quantity=1,
            ticket_type=ticket_type,
            price=price,
            qr_code=qr_code_name,
            currency='GHS',
            payment_status='COMPLETED',
            reference=reference
        )
        order.save()

        # Return success response with QR code URL
        return jsonify({
            'success': True,
            'qr_code_url': qr_code_url,
            'message': 'Order created successfully'
        }), 201

    except Exception as e:
        # Log the exception and return error response
        logger.error(f"Error creating order: {e}")
        abort(500, description="Error creating an order.")
