from flask import Blueprint, request, jsonify, current_app
from .resource_blueprint import ResourceBlueprint
from ..utilities.log import Logger
from .status_library import status_success, status_error
import requests

# Create a ResourceBlueprint for member-answers
member_answers_resource = ResourceBlueprint('member-answers')

# Define a custom implementation for create_member_answer
def _custom_create_member_answer():
    logger = Logger.get_logger("member_answers_blueprint")
    manager = current_app.config["MANAGER"]
    logger.info("Attempting to create or update a member answer")
    
    try:
        # Get the payload from the request
        payload = request.json
        logger.info("Processing member answer")
        logger.debug(f"Member answer payload: {payload}")
        
        # Check if required fields exist in the payload
        required_fields = ['memberId', 'questionId', 'answerId']
        for field in required_fields:
            if field not in payload:
                logger.warning(f"{field} is required but not provided in the request")
                return jsonify(status_error(f"{field} is required")), 400
        
        member_id = payload['memberId']
        question_id = payload['questionId']
        answer_id = payload['answerId']
        
        # Check if a member answer already exists for this member and question
        logger.info(f"Checking if member answer already exists for member {member_id} and question {question_id}")
        
        existing_answers_response = manager.make_api_request(
            requests.get,
            f"api/collections/member-answers?member.id_eq={member_id}&question.id_eq={question_id}"
        )
        
        if existing_answers_response.status_code == 200:
            existing_answers = existing_answers_response.json()
            
            if existing_answers['total'] > 0:
                # Update existing answer instead of creating a new one
                existing_answer_id = existing_answers['data'][0]['id']
                logger.info(f"Found existing member answer with ID {existing_answer_id}, updating it")
                
                update_response = manager.make_api_request(
                    requests.patch,
                    f"api/collections/member-answers/{existing_answer_id}",
                    json={'answer': answer_id}
                )
                
                if update_response.status_code == 200:
                    logger.info("Member answer updated successfully")
                    return jsonify(status_success(f"Member answer updated with id: {existing_answer_id}")), 200
                else:
                    logger.error(f"Failed to update member answer. Status code: {update_response.status_code}, Response: {update_response.text}")
                    return jsonify(status_error("Couldn't update member answer")), 500
        
        # If no existing answer found, proceed with creating a new one
        logger.info("No existing member answer found, creating a new one")
        response = manager.make_api_request(
            requests.post,
            "api/collections/member-answers",
            json=payload
        )
        
        if response.status_code == 201:
            logger.info("Member answer created successfully")
            answer_id = response.json().get('id')
            
            logger.info(f"Successfully created member answer with ID: {answer_id}")
            return jsonify(status_success(f"Member answer created with id: {answer_id}")), 201
        else:
            logger.error(f"Failed to create member answer. Status code: {response.status_code}, Response: {response.text}")
            return jsonify(status_error("Couldn't create member answer")), 500
            
    except Exception as e:
        logger.exception(f"Exception occurred while creating/updating member answer: {str(e)}")
        return jsonify(status_error(f"Error processing member answer: {str(e)}")), 500

# Override the default create_resource with our custom implementation
member_answers_resource.override_route('create_resource', _custom_create_member_answer)

# Use the blueprint from the ResourceBlueprint without any overrides
member_answers_bp = member_answers_resource.blueprint