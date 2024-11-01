#!/usr/bin/env python3
"""
Database Storage Engine for managing MySQL database connections and operations.
Provides methods to add, update, delete, and retrieve models, with support for pagination.
"""

import logging
import os
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import and_, create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlite3 import OperationalError

from models.basemodel import Base

# Load environment variables from .env file
load_dotenv()

# Set up a logger for this module
logger = logging.getLogger(__name__)

# Get database connection details from environment variables
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = int(os.environ.get('DB_PORT'))

# Construct the database URL using MySQL connector
DB_URL = f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'


class DBStorage:
    """
    Manages the connection and CRUD operations for the database, handling models
    and supporting pagination for large datasets.
    """

    def __init__(self):
        """
        Initializes the DBStorage class and sets up the database engine.
        """
        self.__engine = create_engine(DB_URL, echo=False, pool_pre_ping=True)
        self.__session = None
        self.reload()

    def save(self):
        """
        Commits any pending changes to the database.
        """
        try:
            self.__session.commit()
        except SQLAlchemyError as e:
            self.__session.rollback()
            print(f"Error during save operation: {e}")

    def new(self, obj):
        """
        Adds a new object to the current session for future insertion.
        :param obj: The object to be added to the session.
        """
        try:
            self.__session.expire_all()
            self.__session.add(obj)
        except SQLAlchemyError as e:
            print(f"Error during add operation: {e}")

    def update(self, obj):
        """
        Updates the object in the database, modifying its updated_at field.
        :param obj: The object to be updated.
        """
        try:
            obj.updated_at = datetime.now()
            self.save()
        except SQLAlchemyError as e:
            print(f"Error during update operation: {e}")

    def delete(self, obj):
        """
        Marks an object as deleted by updating its deleted_at field and removes it from the session.
        :param obj: The object to be deleted.
        """
        try:
            obj.deleted_at = datetime.now()
            self.save()
            self.__session.delete(obj)
            self.save()
        except SQLAlchemyError as e:
            print(f"Error during delete operation: {e}")

    def reload(self):
        """
        Reloads the connection to the database, creating all tables from metadata
        and establishing a new session.
        """
        Base.metadata.create_all(self.__engine)
        session = sessionmaker(bind=self.__engine)
        Session = scoped_session(session)
        self.__session = Session()

    def get(self, cls, _id):
        """
        Retrieves a single object from the database by its ID.
        :param cls: The class of the object to retrieve.
        :param _id: The ID of the object.
        :return: The object instance or None if not found.
        """
        try:
            return self.__session.query(cls).get(_id)
        except SQLAlchemyError as e:
            print(f"Error retrieving object by ID: {e}")
            return None

    def get_by_name(self, cls, name):
        """
        Retrieves a single object from the database by its name.
        :param cls: The class of the object to retrieve.
        :param name: The name of the object.
        :return: The object instance or None if not found.
        """
        try:
            return self.__session.query(cls).filter_by(name=name).first()
        except SQLAlchemyError as e:
            print(f"Error retrieving object by name: {e}")
            return None
    
    def dynamic_query(self, cls, filters=None, page=None, page_size=10):
        """
        Performs a dynamic query on the given class based on the provided filters.

        :param cls: The class of the objects to query.
        :param filters: A dictionary of field-value pairs to filter by.
        :param page: Optional page number for pagination (1-indexed).
        :param page_size: Number of items per page for pagination.
        :return: A list of matching objects or an empty list if none found.
        """
        try:
            # Start with a base query for the class
            query = self.__session.query(cls)
            
            # Apply filters dynamically
            if filters:
                conditions = [getattr(cls, key) == value for key, value in filters.items()]
                query = query.filter(and_(*conditions))
            
            # Apply pagination
            query = self.__apply_pagination(query, page, page_size)
            
            # Execute the query and return results as dictionaries
            return [obj.to_dict() for obj in query.all()]
        
        except SQLAlchemyError as e:
            print(f"Error during dynamic query: {e}")
            return []

    def count(self, cls):
        """
        Count the number of objects in the database by the class type.
        :param cls: The class of the object to count.
        :return: The number of instances found.
        """

        try:
            return self.__session.query(cls).count()
        except SQLAlchemyError as e:
            print(f"Error counting the object: {e}")
            return 0

    def all(self, cls=None, page=None, page_size=10):
        """
        Retrieves all objects from the database for a given class with optional pagination.
        If no class is provided, returns all objects across all classes.
        :param cls: The class of the objects to retrieve. If None, retrieves all objects.
        :param page: Page number for pagination (1-indexed).
        :param page_size: Number of items per page for pagination.
        :return: A list of objects or a dictionary of lists if cls is None.
        """
        try:
            if cls is None:
                result = {}
                from models import classes
                for clss in classes.values():
                    objs = self.__apply_pagination(self.__session.query(clss), page, page_size).all()
                    result[clss.__name__] = [obj.to_dict() for obj in objs]
                return result
            else:
                query = self.__apply_pagination(self.__session.query(cls), page, page_size)
                return [obj.to_dict() for obj in query.all()]
        except SQLAlchemyError as e:
            print(f"Error retrieving all objects: {e}")
            return []
        
    def all_valid(self, cls=None, page=None, page_size=10):
        """
        Retrieves all objects from the database for a given class with optional pagination.
        If no class is provided, returns all objects across all classes.
        :param cls: The class of the objects to retrieve. If None, retrieves all objects.
        :param page: Page number for pagination (1-indexed).
        :param page_size: Number of items per page for pagination.
        :return: A list of objects or a dictionary of lists if cls is None.
        """
        try:
            if cls is None:
                result = {}
                from models import classes
                for clss in classes.values():
                    objs = self.__apply_pagination(self.__session.query(clss)
                                                   .filter(clss.end_date > datetime.now().date()), 
                                                   page, page_size).all()
                    result[clss.__name__] = [obj.to_dict() for obj in objs]
                return result
            else:
                query = self.__apply_pagination(self.__session.query(cls)
                                                   .filter(cls.end_date > datetime.now().date())
                                                , page, page_size)
                return [obj.to_dict() for obj in query.all()]
        except SQLAlchemyError as e:
            print(f"Error retrieving all objects: {e}")
            return []

    def close(self):
        """
        Closes the current database session and engine, freeing up resources.
        """
        if self.__session is not None:
            self.__session.close()
            self.__engine.dispose()
            self.__session = None

    def __apply_pagination(self, query, page, page_size):
        """
        Applies pagination to a query.
        :param query: The SQLAlchemy query to paginate.
        :param page: Page number for pagination (1-indexed).
        :param page_size: Number of items per page.
        :return: Paginated query.
        """
        if page is not None and page_size > 0:
            return query.offset((page - 1) * page_size).limit(page_size)
        return query

    def is_live(self):
        """
        Tests the connection to the database.

        Returns:
            dict: A dictionary with:
                - success (bool): Whether the connection was successful.
                - message (str): A message indicating the status of the connection.
        """
        try:
            # Attempting a quick connection test by connecting and immediately disconnecting
            with self.__engine.connect() as connection:
                connection.execute("SELECT 1;")
            return {
                'success': True,
                'message': 'Database connection successful.'
            }
        except OperationalError as e:
            logger.error(f"Database connection failed: {e}")
            return {
                'success': False,
                'message': f"Database connection failed: {e}"
            }
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return {
                'success': False,
                'message': f"An unexpected error occurred: {e}"
            }
