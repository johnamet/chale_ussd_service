#!/usr/bin/env python3
import pandas as pd

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

from flask import abort, jsonify, request, render_template

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
@protected()
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
                social = Social.dynamic_query({'user_id':user.id})

                if not social:
                    social = Social(platform="instagram", user_id=user.id,
                                    handle=instagram)
                    social.save()
        if not user:

            user = User(id=phone, phone=phone,
                        password=phone,
                        country_id=1, name=user_name,
                        email=email if email else str(phone))

            if instagram:
                social = Social.dynamic_query({'user_id':user.id})
                if not social:
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
            reference=reference,
            other_details=event_id
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

           body = render_template(
                "ticket_email_template.html",
                event_name=event_name,
                password=password,
                mail_code_url=mail_code_url,
                user_name=user_name.split(" ")[0]
            )
           send_email(subject=f"You Dey Inside! {event_name} is Waiting for You 🎉", recipients=[email],
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
    
@app_views.route('/orders/<event_id>', methods=['GET'], strict_slashes=False)
@protected()
def get_event_orders(event_id):
    try:
        event = Event.get(event_id)

        if not event:
            abort(400, f"Event with id: {event_id} not found")
        
        event_orders = Order.dynamic_query({'other_details':int(event_id)})

        if event_orders:
            return jsonify({
                'success': True,
                'data': event_orders,
                'message': f'Orders for {event.name} retrieved successfully'
            }), 200
        else:
            orders = Order.all()
            event_orders = [order for order in orders if Ticket.get(order['ticket_id']).event_id == int(event_id)]
            return jsonify({
                'success': True,
                'data': event_orders,
                'message': f'Orders for {event.name} retrieved successfully'
            }), 200
    except Exception as e:
        print(e)
        abort(500, 'Error retrieving orders for event')



@app_views.route('/bulk-orders/<event_id>', methods=['POST'], strict_slashes=False)
def create_bulk_order(event_id):
    """
    Create bulk orders
    """

    try:
        if 'file' not in request.files:
            abort(400, description='No file provided in the request')
        

        
        event = Event.get(event_id)

        excel_file = request.files['file']

        df = pd.read_excel(excel_file)

        required_fields = {'First Name', 'Last Name', 'Tel', 'Email', 'Ticket Type', 'Assigned Table'}

        if not required_fields.issubset(df.columns):
            abort(400, description=f'Missing required columns. Expected columns: {required_fields}')

        success_count = 0

        failure_details = []

        for _, row in df.iterrows():
            email = row['Email']
            name = f"{row['First Name']} {row['Last Name']}"
            phone = row['Tel']
            ticket_type = row['Ticket Type']
            assigned_table = row['Assigned Table']
            quantity = row['Quantity'] or  1
            price = row['Price'] or 0

            users = []
            tickets = []
            orders = []

            code_data = []

            try:
                user = User.dynamic_query({'name': name,'email': email})

                if not user:
                    user = User(id=phone, phone=phone,
                        password=phone,
                        country_id=1, name=name,
                        email=email if email else str(phone))
                    users.append(user)

                else:
                    user = user[0]


                ticket = Ticket.dynamic_query({'title': ticket_type, "event_id": event_id})[0]
                


                file_name = f'qrcode_{phone}-{datetime.now().timestamp()}'

                order = Order(user_id=user.id, ticket_id=ticket['id'],
                              quantity=quantity,
                              ticket_type=ticket_type,
                              price=price,
                              qr_code=file_name,
                              currency='GHS',
                              payment_status='COMPLETED',
                              reference=f'REF{generate_token()}')
                orders.append(order)

                code_data.append({
                    'ticket_id': ticket['id'],
                    'user_id': user.id,
                    'event_id': event.id,
                    'assigned_table': assigned_table,
                    'valid': util.format_date_time(event.end_date, event.end_time)
                })
                success_count =+ 1
            
            except Exception as e:
                logger.error(f"Failed to process row {row}: {e}")
                failure_details.append({
                    'row': row.to_dict(),
                    'error': str(e)
                })

        return jsonify({
            'success': True,
            'message': 'Bulk order processing completed',
            'processed': success_count,
            'processed_percentage': (success_count * 100)/ len(df),
            'failures': failure_details,
            'data': code_data
        }), 200
    except Exception as e:
        logger.error(f"Failed to process bulk order file: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to process bulk order file',
            'error': str(e)
        }), 500
    

@app_views.route('/user/<id>', methods=['GET'], strict_slashes=False)
def get_user(id):
    try:
        user = User.get(id)

        if user:
            return jsonify({
                'success': True,
                'data': user.to_dict(),
                'message': 'User retrieved Successfully',
            })
        else:
            abort(404, f'User with ID: {id} not found')
    except Exception as e:
        logger.error(e)
        abort(500, f'Internal Error: {e}')







                



                

                    
                




