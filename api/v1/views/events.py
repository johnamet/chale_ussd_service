#!/usr/bin/env python3

"""
Event Management Module
=======================

This module handles event-related operations with the ticketing paltform, specifically providing
endpoint to create and retrieve events with pagination. Key features include:

- Retrieving paginated valid events from the database
- Retrieving an event based on the id of the event
- Logging errors for ease of debugging and system monitoring.

Routes:
- `/events` [GET]: Retrieve paginated  events.
- `/valid-events` [GET]: Retrieve paginated valid events
- `/event/<event_id>`  [GET]: Retrieve a single event


Exception Handling:
    All exceptions are logged, and appropriate HTTP error responses are returned to clients.

Usage:
    These routes are part of a Flask blueprint and can be integrated with other parts of the
    application for a complete order management solution.
"""

from flask import abort, jsonify, request
from api.v1.views import app_views
from models.event import Event
import logging

from models.tour import Tour

logger = logging.getLogger(__name__)

@app_views.route('/events', methods=['GET'], strict_slashes=False)
def get_events():
    """
    Retrieve paginated events from the database.

    This route fetches events with optional pagination parameters, allowing 
    clients to retrieve data in manageable chunks. Defaults are used if `page` and `page_size` are not specified.

    Query Parameters:
        - page (int, optional): Page number to retrieve (default: 10)
        - page_size (int, optional): Number of orders per page (default: 10).

    Returns:
        JSON: A JSON object containing:
            - success (bool): Status of the request.
            - data (list): A list of order objects in dictionary format for the specified page.
            - page (int): Current page number.
            - page_size (int): Number of events per page.
            - total_events (int): Total number of orders.
            - total_pages (int): Calculated total number of pages based on `page_size`.
            - message (str): Informational message.
     Responses:
        200 OK: Successfully retrieved events.
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

        all_events = Event.all(page=page, page_size=page_size)
        total_events = Event.count()
        total_pages = (total_events + page_size - 1) // page_size

        response = {
            'success': True,
            'data': all_events,
            'page': page,
            'page_size': page_size,
            'total_events': total_events,
            'total_pages': total_pages,
            'message': 'Events retrieved successfully'
        }

        return jsonify(response), 200
    except Exception as e:
        logger.error(f'Failed to retrieve events {e}')
        abort(500, description=f'Failed to retrieve events, {e}')
    
@app_views.route('/valid-events', methods=['GET'], strict_slashes=False)
def get_valid_events():
    """
    Retrieve paginated events from the database.

    This route fetches events with optional pagination parameters, allowing 
    clients to retrieve data in manageable chunks. Defaults are used if `page` and `page_size` are not specified.

    Query Parameters:
        - page (int, optional): Page number to retireve (default: 10)
        - page_size (int, optional): Number of orders per page (default: 10).

    Returns:
        JSON: A JSON object containing:
            - success (bool): Status of the request.
            - data (list): A list of order objects in dictionary format for the specified page.
            - page (int): Current page number.
            - page_size (int): Number of events per page.
            - total_events (int): Total number of orders.
            - total_pages (int): Calculated total number of pages based on `page_size`.
            - message (str): Informational message.
     Responses:
        200 OK: Successfully retrieved events.
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

        all_events = Event.all_valid(page=page, page_size=page_size)
        total_events = Event.count()
        total_pages = (total_events + page_size - 1) // page_size

        response = {
            'success': True,
            'data': all_events,
            'page': page,
            'page_size': page_size,
            'total_events': total_events,
            'total_pages': total_pages,
            'message': 'Valid Events retrieved successfully'
        }

        return jsonify(response), 200
    except Exception as e:
        logger.error(f'Failed to retrieve events {e}')
        abort(500, description=f'Failed to valid retrieve events, {e}')



@app_views.route('/event/<event_id>', methods=['GET'], strict_slashes=False)
def get_event(event_id):

    try:
        event = Event.get(event_id)
        if not event:
            event = Tour.get(event_id)
        
        if not event:
            abort(400, description='No event was found')
        response = {
            'success': True,
            'data': event.to_dict(),
            'message': 'Event retrieved successfully'
        }

        return jsonify(response), 200
    
    except Exception as e:
        logger.error(f'Something happenned. {e}')
        abort(500, description='Failed to fetch event')
    



