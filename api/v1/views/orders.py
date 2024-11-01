#!/usr/bin/env python3

"""
Order Management Module
=======================

This module handles order-related operations within the ticketing platform, specifically providing
endpoints to create and retrieve orders with pagination. Key features include:

- Creating orders with associated QR codes and tickets.
- Retrieving paginated orders from the database.
- Generating unique tokens for secure PDF unlocks and order references.
- Utilizing caching with Redis for efficient order data storage and quick access.
- Logging errors for ease of debugging and system monitoring.

Dependencies:
    - Flask: For handling web requests and routing.
    - datetime: For timestamping QR codes.
    - os: For accessing environment variables.
    - models: To interact with Order, Ticket, Event, Tour, and User models.
    - utils: For token generation and utility functions.
    - logging: For logging errors.

Routes:
    - `/orders` [GET]: Retrieve paginated orders.
    - `/order` [POST]: Create a new order and associate it with a QR code and ticket.

Exception Handling:
    All exceptions are logged, and appropriate HTTP error responses are returned to clients.

Usage:
    These routes are part of a Flask blueprint and can be integrated with other parts of the
    application for a complete order management solution.

Author: [John Ametepe Agboku]
Date: 2024
"""

import logging
import os
from datetime import datetime

from flask import abort, jsonify, request

from api.v1.views import app_views
from models import cache
from models.engine.mail_service import send_email
from models.event import Event
from models.order import Order
from models.social import Social
from models.temp_user import TempUser
from models.tickets import Ticket
from models.tour import Tour
from models.user import User
from utils import util
from utils.util import generate_token, protected

# Configure logger
logger = logging.getLogger(__name__)


@app_views.route('/orders', methods=['GET'], strict_slashes=False)
@protected()
def get_orders():
    """
    Retrieve paginated orders from the database.

    This route fetches orders with optional pagination parameters, allowing clients to retrieve
    data in manageable chunks. Defaults are used if `page` and `page_size` are not specified.

    Query Parameters:
        - page (int, optional): Page number to retrieve (default: 1).
        - page_size (int, optional): Number of orders per page (default: 10).

    Returns:
        JSON: A JSON object containing:
            - success (bool): Status of the request.
            - data (list): A list of order objects in dictionary format for the specified page.
            - page (int): Current page number.
            - page_size (int): Number of orders per page.
            - total_orders (int): Total number of orders.
            - total_pages (int): Calculated total number of pages based on `page_size`.
            - message (str): Informational message.

    Responses:
        200 OK: Successfully retrieved orders.
        400 Bad Request: Invalid pagination parameters.
        500 Internal Server Error: Error during order retrieval.

    Logs:
        Exceptions raised during the process with relevant error messages.
    """
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))

        if page < 1 or page_size < 1:
            raise ValueError("Page and page_size must be positive integers.")

        start = (page - 1) * page_size
        end = start + page_size

        all_orders = Order.all(page=page, page_size=page_size)
        total_orders = Order.count()
        total_pages = (total_orders + page_size - 1) // page_size

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
        logger.error(f"Invalid pagination parameters: {ve}")
        return jsonify({
            'success': False,
            'message': 'Invalid pagination parameters. Page and page_size should be positive integers.'
        }), 400

    except Exception as e:
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

    This route handles order creation with a generated QR code and ticket, accepting a JSON
    payload with the order details and performing necessary validations. Checks if a user
    exists or creates one as needed.

    JSON Payload:
        - event_name (str): Name of the event.
        - user_name (str): Name of the user.
        - price (float): Ticket price.
        - phone (str): User's phone number for reference and QR code generation.
        - ticket_type (str): Type of ticket.
        - reference (str, optional): Payment reference number.

    Returns:
        JSON: A JSON object with:
            - success (bool): Status of the request.
            - qr_code_url (str): URL of the generated QR code.
            - message (str): Informational message.

    Responses:
        201 Created: Successfully created the order and generated a QR code.
        400 Bad Request: Missing required fields.
        500 Internal Server Error: Error during order creation.

    Logs:
        Exceptions raised during the process with relevant error messages.
    """
    try:
        data = request.get_json()
        required_fields = ['event_name', 'user_name', 'price', 'ticket_type']

        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "message": f"Missing required field: {field}",
                    "error": "Database connection error"
                }), 200

        event_name = data.get('event_name')
        user_name = data.get('user_name')
        price = data.get('price')
        phone = data.get('phone')
        ticket_type = data.get('ticket_type')
        reference = data.get('reference', f'ref-{generate_token()}')

        user = User.get(phone)
        if not user:
            user = User(id=phone, phone=phone, password=phone, country_id=1, name=user_name, email=str(phone))
            user.save()

        event = Event.get_by_name(event_name) or Tour.get_by_name(event_name)
        event_id = event.id if event else None
        ticket = Ticket(title=ticket_type, price=price, entries_allowed_per_ticket=1, quantity=1,
                        event_id=event_id)

        ticket.save()
        file_name = f'qrcode_{phone}-{datetime.now().timestamp()}'

        order = Order(
            user_id=phone,
            ticket_id=ticket.id,
            quantity=1,
            ticket_type=ticket_type,
            price=price,
            qr_code=file_name,
            currency='GHS',
            payment_status='COMPLETED',
            reference=reference
        )
        order.save()

        password = generate_token()
        data = {
            'phone': phone,
            'name': user_name,
            'event_coordinates': event.coordinates if event else 'www.chaleapp.org',
            'event_name': event_name,
            'start_date': util.format_date_time(event.start_date, event.start_time) if event else None,
            'end_date': util.format_date_time(event.end_date, event.end_time) if event else None,
            'description': event.description if event else 'Contact customer service for details.',
            'reference': reference,
            'password': password,
            'ticket_id': ticket.id,
            'ticket_type': ticket_type
        }

        cache_result = cache.hset(key=file_name, data=data)
        if not cache_result:
            abort(500, 'Error writing to Redis')

        code_url = f'{os.getenv("SERVER_ADDRESS")}qr_code/{file_name}'

        return jsonify({
            'success': True,
            'qr_code_url': code_url,
            'pdf_unlock_token': password,
            'message': 'Order created successfully'
        }), 200

    except Exception as e:
        logger.error(f"Error creating order: {e}")
        return jsonify({
            "success": False,
            "message": "Error creating an order",
            "error": "Database connection error"
        }), 200


@app_views.route('/instant-order', methods=['POST'], strict_slashes=False)
def create_instant_order():
    """
    Create a new order, generate a QR code, and associate a ticket with the order.

    This route handles order creation with a generated QR code and ticket, accepting a JSON
    payload with the order details and performing necessary validations. Checks if a user
    exists or creates one as needed.

    JSON Payload:
        - event_name (str): Name of the event.
        - user_name (str): Name of the user.
        - price (float): Ticket price.
        - phone (str): User's phone number for reference and QR code generation.
        - ticket_type (str): Type of ticket.
        - reference (str, optional): Payment reference number.

    Returns:
        JSON: A JSON object with:
            - success (bool): Status of the request.
            - qr_code_url (str): URL of the generated QR code.
            - message (str): Informational message.

    Responses:
        201 Created: Successfully created the order and generated a QR code.
        400 Bad Request: Missing required fields.
        500 Internal Server Error: Error during order creation.

    Logs:
        Exceptions raised during the process with relevant error messages.
    """
    try:
        data = request.get_json()
        required_fields = ['event_name', 'user_name', 'email']

        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "message": f"Missing required field: {field}",
                    "error": "Database connection error"
                }), 200

        event_name = data.get('event_name', 'Private Event')
        user_name = data.get('user_name')
        price = data.get('price', 0)
        phone = data.get('phone')
        ticket_type = data.get('ticket_type', 'regular')
        reference = data.get('reference', f'ref-{generate_token()}')
        instagram = data.get('instagram', )
        email = data.get('email')

        user = User.get(phone)
        if user:
                social = Social(platform="instagram", user_id=user.id,
                                handle=instagram)
                social.save()
        if not user:
            user = User(id=phone, phone=phone,
                        password=phone,
                        country_id=1, name=user_name,
                        email=email if email else str(phone))

            if instagram:
                social = Social(platform="instagram", user_id=user.id,
                                handle=instagram)

                social.save()
            user.save()

        event = Event.get_by_name(event_name) or Tour.get_by_name(event_name)
        event_id = event.id if event else None
        ticket = Ticket(title=ticket_type, price=price, entries_allowed_per_ticket=1, quantity=1,
                        event_id=event_id)

        ticket.save()
        file_name = f'qrcode_{phone}-{datetime.now().timestamp()}'

        order = Order(
            user_id=phone,
            ticket_id=ticket.id,
            quantity=1,
            ticket_type=ticket_type,
            price=price,
            qr_code=file_name,
            currency='GHS',
            payment_status='COMPLETED',
            reference=reference
        )
        order.save()

        password = generate_token()

        data = {
            'phone': phone,
            'name': user_name,
            'event_coordinates': event.coordinates if event else 'www.app.chaleapp.org',
            'event_name': event_name,
            'start_date': util.format_date_time(event.start_date, event.start_time) if event else None,
            'end_date': util.format_date_time(event.end_date, event.end_time) if event else None,
            'description': event.description if event else 'Contact customer service for details.',
            'reference': reference,
            'password': password,
            'ticket_id': ticket.id,
            'ticket_type': ticket_type
        }

        cache_result = cache.hset(key=file_name, data=data)
        if not cache_result:
            abort(500, 'Error writing to Redis')

        mail_code_url = f'{os.getenv("SERVER_ADDRESS")}qr_code/{file_name}'
        pos_code_url = f'{os.getenv("SERVER_ADDRESS")}pos-qrcode/{file_name}'

        if email:
            body = f"""
                <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your Ticket for {event_name}</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
        <h2 style="color: #ff6600; text-align: center;">Hello, {user_name.split(" ")[0]}</h2>
        
        <p style="font-size: 1.1em;">
            Chalé, are you ready? Because we’ve got you all set for <strong>{event_name}!</strong> 🎶🔥
        </p>
        
        <p style="font-size: 1em;">
            Check this – your ticket is in hand, and you’re officially on the list. Here’s what you need to enter like a boss:
        </p>

        <ul style="list-style-type: none; padding: 0;">
            <li style="margin-bottom: 10px;">
                <strong>QR Code:</strong> <a href="{mail_code_url}" style="color: #ff6600;">{mail_code_url}</a>
            </li>
            <li style="margin-bottom: 10px;">
                <strong>Unlock Code for PDF Ticket:</strong> <em>{password}</em>
            </li>
        </ul>
        
        <p style="font-size: 1em;">
            Just show the QR code at the gate, and you're in! If you have any trouble, don't stress – we're just a message away.
        </p>
        
        <p style="font-size: 1.1em;">
            Get ready, stay safe, and come with your vibe! Let’s make this one memorable.
        </p>
        
        <p style="font-size: 1em; text-align: center;">
            See you there!<br>
            <strong>The Chalé Team</strong>
        </p>
    </div>
</body>
</html>
                """

            send_email(subject=f"Eii Chalé! You're All Set for {event_name} 🎉", recipients=[email],
                       body=body,
                       html_body=body)

        return jsonify({
            'success': True,
            'qr_code_url': pos_code_url,
            'message': 'Order created successfully'
        }), 200

    except Exception as e:
        logger.error(f"Error creating order: {e}")
        return jsonify({
            "success": False,
            "message": "Error creating an order",
            "error": "Database connection error"
        }), 200
