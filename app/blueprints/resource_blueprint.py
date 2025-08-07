from flask import Blueprint, current_app, jsonify, request
import requests
from .status_library import status_success, status_error
from functools import wraps
from ..utilities.constants import Constants
from ..utilities.log import Logger


class ResourceBlueprint:
    """
    A common blueprint class for creating RESTful endpoints for different resource types.
    This class provides standard CRUD operations that follow the API endpoints pattern.
    """
    
    def __init__(self, resource_type, url_prefix=None, manager_attr=None):
        """
        Initialize a new ResourceBlueprint.
        
        :param resource_type: The type of resource (e.g., 'lobbies', 'questions', etc.)
        :param url_prefix: Optional URL prefix (defaults to '/api/collections/{resource_type}')
        :param manager_attr: Optional attribute name in Manager class for specific operations
                           (defaults to resource_type)
        """
        self.resource_type = resource_type
        self.url_prefix = url_prefix or Constants.endpoint_url(resource_type)
        self.manager_attr = manager_attr or resource_type
        self.logger = Logger.get_logger(f"{resource_type}_resource_blueprint")
        
        # Create a Flask Blueprint for this resource
        self.blueprint = Blueprint(f'{resource_type}_bp', __name__)
        
        # Dictionary to store overridden handlers
        self.overrides = {}
        
        # Register the standard routes
        self._register_routes()

    
    def _register_routes(self):
        """Register all standard RESTful routes for this resource."""
        
        # GET /api/collections/{resource_type} - List resources
        @self.blueprint.route(self.url_prefix, methods=['GET'])
        def list_resources():
            logger = self.logger
            logger.info(f"Handling GET request to list all {self.resource_type}")
            
            if 'list_resources' in self.overrides:
                logger.debug(f"Using overridden handler for list_resources")
                return self.overrides['list_resources']()
                
            manager = current_app.config["MANAGER"]
            try:
                logger.debug(f"Making API request to get {self.resource_type} list")
                
                # Extract all query parameters from the request
                params = {}
                for key, value in request.args.items():
                    params[key] = value
                    
                logger.debug(f"Query parameters: {params}")
                
                response = manager.make_api_request(
                    requests.get,
                    f"api/collections/{self.resource_type}",
                    params=params
                )
                
                if response.status_code == 200:
                    logger.info(f"Successfully retrieved {self.resource_type} list")
                    return jsonify(status_success(f"Retrieved {self.resource_type}", response.json())), 200
                else:
                    error_msg = f"Failed to retrieve {self.resource_type}"
                    logger.error(f"{error_msg}: {response.text}")
                    return jsonify(status_error(error_msg)), response.status_code
            except Exception as e:
                error_msg = f"Error retrieving {self.resource_type}"
                logger.exception(f"{error_msg}: {str(e)}")
                return jsonify(status_error(Logger.format_error_for_response(e))), 500
        
        # POST /api/collections/{resource_type} - Create a new resource
        @self.blueprint.route(self.url_prefix, methods=['POST'])
        def create_resource():
            logger = self.logger
            logger.info(f"Handling POST request to create new {self.resource_type}")
            
            if 'create_resource' in self.overrides:
                logger.debug(f"Using overridden handler for create_resource")
                return self.overrides['create_resource']()
                
            manager = current_app.config["MANAGER"]
            try:
                logger.debug(f"Making API request to create {self.resource_type}")
                response = manager.make_api_request(
                    requests.post,
                    f"api/collections/{self.resource_type}",
                    json=request.json
                )
                
                if response.status_code in [200, 201]:
                    # If there's a specific handler for this resource type in the manager, use it
                    if hasattr(manager, f"create_{self.manager_attr}"):
                        logger.debug(f"Using specific handler for {self.manager_attr}")
                        create_method = getattr(manager, f"create_{self.manager_attr}")
                        status, id = create_method(request.json)
                        if status:
                            logger.info(f"Successfully created {self.resource_type} with ID: {id}")
                            return jsonify(status_success(f"{self.resource_type} created with id: {id}", response.json())), 201
                    
                    # Default response if no specific handler
                    logger.info(f"Successfully created new {self.resource_type}")
                    return jsonify(status_success(f"Created new {self.resource_type}", response.json())), 201
                else:
                    error_msg = f"Failed to create {self.resource_type}"
                    logger.error(f"{error_msg}: {response.text}")
                    return jsonify(status_error(error_msg)), response.status_code
            except Exception as e:
                error_msg = f"Error creating {self.resource_type}"
                logger.exception(f"{error_msg}: {str(e)}")
                return jsonify(status_error(Logger.format_error_for_response(e))), 500
        
        # GET /api/collections/{resource_type}/select-options - List resources for select options
        @self.blueprint.route(f"{self.url_prefix}/select-options", methods=['GET'])
        def select_options():
            logger = self.logger
            logger.info(f"Handling GET request for {self.resource_type} select options")
            
            if 'select_options' in self.overrides:
                logger.debug(f"Using overridden handler for select_options")
                return self.overrides['select_options']()
                
            manager = current_app.config["MANAGER"]
            try:
                logger.debug(f"Making API request to get {self.resource_type} select options")
                
                # Extract all query parameters from the request
                params = {}
                for key, value in request.args.items():
                    params[key] = value
                    
                logger.debug(f"Query parameters: {params}")
                
                response = manager.make_api_request(
                    requests.get,
                    f"api/collections/{self.resource_type}/select-options",
                    params=params
                )
                
                if response.status_code == 200:
                    logger.info(f"Successfully retrieved {self.resource_type} select options")
                    return jsonify(status_success(f"Retrieved {self.resource_type} select options", response.json())), 200
                else:
                    error_msg = f"Failed to retrieve {self.resource_type} select options"
                    logger.error(f"{error_msg}: {response.text}")
                    return jsonify(status_error(error_msg)), response.status_code
            except Exception as e:
                error_msg = f"Error retrieving {self.resource_type} select options"
                logger.exception(f"{error_msg}: {str(e)}")
                return jsonify(status_error(Logger.format_error_for_response(e))), 500
        
        # GET /api/collections/{resource_type}/{id} - Get a single resource
        @self.blueprint.route(f"{self.url_prefix}/<id>", methods=['GET'])
        def get_resource(id):
            logger = self.logger
            logger.info(f"Handling GET request for {self.resource_type} with ID: {id}")
            
            if 'get_resource' in self.overrides:
                logger.debug(f"Using overridden handler for get_resource")
                return self.overrides['get_resource'](id)
                
            manager = current_app.config["MANAGER"]
            try:
                logger.debug(f"Making API request to get {self.resource_type} {id}")
                
                # Extract all query parameters from the request
                params = {}
                for key, value in request.args.items():
                    params[key] = value
                    
                logger.debug(f"Query parameters: {params}")
                
                response = manager.make_api_request(
                    requests.get,
                    f"api/collections/{self.resource_type}/{id}",
                    params=params
                )
                
                if response.status_code == 200:
                    logger.info(f"Successfully retrieved {self.resource_type} {id}")
                    return jsonify(status_success(f"Retrieved {self.resource_type} {id}", response.json())), 200
                else:
                    error_msg = f"Failed to retrieve {self.resource_type} {id}"
                    logger.error(f"{error_msg}: {response.text}")
                    return jsonify(status_error(error_msg)), response.status_code
            except Exception as e:
                error_msg = f"Error retrieving {self.resource_type} {id}"
                logger.exception(f"{error_msg}: {str(e)}")
                return jsonify(status_error(Logger.format_error_for_response(e))), 500
        
        # PUT /api/collections/{resource_type}/{id} - Update an existing resource (full replace)
        @self.blueprint.route(f"{self.url_prefix}/<id>", methods=['PUT'])
        def update_resource_full(id):
            logger = self.logger
            logger.info(f"Handling PUT request to update {self.resource_type} with ID: {id}")
            
            if 'update_resource_full' in self.overrides:
                logger.debug(f"Using overridden handler for update_resource_full")
                return self.overrides['update_resource_full'](id)
                
            manager = current_app.config["MANAGER"]
            try:
                logger.debug(f"Making API request to update {self.resource_type} {id}")
                
                # Extract all query parameters from the request
                params = {}
                for key, value in request.args.items():
                    params[key] = value
                    
                logger.debug(f"Query parameters: {params}")
                
                response = manager.make_api_request(
                    requests.put,
                    f"api/collections/{self.resource_type}/{id}",
                    json=request.json,
                    params=params
                )
                
                if response.status_code == 200:
                    logger.info(f"Successfully updated {self.resource_type} {id}")
                    return jsonify(status_success(f"Updated {self.resource_type} {id}", response.json())), 200
                else:
                    error_msg = f"Failed to update {self.resource_type} {id}"
                    logger.error(f"{error_msg}: {response.text}")
                    return jsonify(status_error(error_msg)), response.status_code
            except Exception as e:
                error_msg = f"Error updating {self.resource_type} {id}"
                logger.exception(f"{error_msg}: {str(e)}")
                return jsonify(status_error(Logger.format_error_for_response(e))), 500
        
        # PATCH /api/collections/{resource_type}/{id} - Update an existing resource (partial update)
        @self.blueprint.route(f"{self.url_prefix}/<id>", methods=['PATCH'])
        def update_resource_partial(id):
            logger = self.logger
            logger.info(f"Handling PATCH request for {self.resource_type} with ID: {id}")
            
            if 'update_resource_partial' in self.overrides:
                logger.debug(f"Using overridden handler for update_resource_partial")
                return self.overrides['update_resource_partial'](id)
                
            manager = current_app.config["MANAGER"]
            try:
                logger.debug(f"Making API request to partially update {self.resource_type} {id}")
                
                # Extract all query parameters from the request
                params = {}
                for key, value in request.args.items():
                    params[key] = value
                    
                logger.debug(f"Query parameters: {params}")
                
                response = manager.make_api_request(
                    requests.patch,
                    f"api/collections/{self.resource_type}/{id}",
                    json=request.json,
                    params=params
                )
                
                if response.status_code == 200:
                    logger.info(f"Successfully partially updated {self.resource_type} {id}")
                    return jsonify(status_success(f"Partially updated {self.resource_type} {id}", response.json())), 200
                else:
                    error_msg = f"Failed to update {self.resource_type} {id}"
                    logger.error(f"{error_msg}: {response.text}")
                    return jsonify(status_error(error_msg)), response.status_code
            except Exception as e:
                error_msg = f"Error updating {self.resource_type} {id}"
                logger.exception(f"{error_msg}: {str(e)}")
                return jsonify(status_error(Logger.format_error_for_response(e))), 500
        
        # DELETE /api/collections/{resource_type}/{id} - Delete an existing resource
        @self.blueprint.route(f"{self.url_prefix}/<id>", methods=['DELETE'])
        def delete_resource(id):
            logger = self.logger
            logger.info(f"Handling DELETE request for {self.resource_type} with ID: {id}")
            
            if 'delete_resource' in self.overrides:
                logger.debug(f"Using overridden handler for delete_resource")
                return self.overrides['delete_resource'](id)
                
            manager = current_app.config["MANAGER"]
            try:
                logger.debug(f"Making API request to delete {self.resource_type} {id}")
                
                # Extract all query parameters from the request
                params = {}
                for key, value in request.args.items():
                    params[key] = value
                    
                logger.debug(f"Query parameters: {params}")
                
                response = manager.make_api_request(
                    requests.delete,
                    f"api/collections/{self.resource_type}/{id}",
                    params=params
                )
                
                if response.status_code in [200, 204]:
                    logger.info(f"Successfully deleted {self.resource_type} {id}")
                    return jsonify(status_success(f"Deleted {self.resource_type} {id}")), 200
                else:
                    error_msg = f"Failed to delete {self.resource_type} {id}"
                    logger.error(f"{error_msg}: {response.text}")
                    return jsonify(status_error(error_msg)), response.status_code
            except Exception as e:
                error_msg = f"Error deleting {self.resource_type} {id}"
                logger.exception(f"{error_msg}: {str(e)}")
                return jsonify(status_error(Logger.format_error_for_response(e))), 500
                
    def override_route(self, route_name, handler):
        """Override a route handler with a custom implementation
        
        :param route_name: The name of the route to override (e.g., 'create_resource')
        :param handler: The custom handler function
        """
        self.logger.info(f"Overriding route handler for {route_name} in {self.resource_type}")
        self.overrides[route_name] = handler
        
    def register_additional_route(self, rule, endpoint=None, **options):
        """Register an additional route on this blueprint
        
        :param rule: URL rule for the endpoint
        :param endpoint: Name of the endpoint (defaults to the function name)
        :param options: Options to be forwarded to the route
        """
        self.logger.info(f"Registering additional route {rule} for {self.resource_type}")
        return self.blueprint.route(rule, endpoint=endpoint, **options)