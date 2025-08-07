from flask import Blueprint, request, jsonify, current_app
from .resource_blueprint import ResourceBlueprint
from ..utilities.log import Logger
from .status_library import status_success, status_error
import requests

# Create a ResourceBlueprint for members
members_resource = ResourceBlueprint('members')

# Define a custom implementation for create_member
def _custom_create_member():
    logger = Logger.get_logger("members_blueprint")
    manager = current_app.config["MANAGER"]
    logger.info("Attempting to create a new member")
    
    try:
        # Get the payload from the request
        payload = request.json
        logger.info("Creating new member")
        logger.debug(f"Member payload: {payload}")
        
        # Check if userId exists in the payload
        if 'userId' not in payload:
            logger.warning("userId is required but not provided in the request")
            return jsonify(status_error("userId is required")), 400
            
        user_id = payload['userId']
        
        # Check if a member with this userId already exists using the _eq filter suffix
        logger.info(f"Checking if a member with userId {user_id} already exists")
        
        existing_members_response = manager.make_api_request(
            requests.get,
            f"api/collections/members?userId_eq={user_id}"
        )
        
        if existing_members_response.status_code == 200:
            existing_members = existing_members_response.json()
            if existing_members['total'] > 0:
                memberName = existing_members['data'][0]['name']
                logger.warning(f"A member with userId {user_id} already exists")
                return jsonify(status_error(f"A member with userId {user_id} already exists",memberName )), 409
        
        # If no existing member found, proceed with creating a new one
        response = manager.make_api_request(
            requests.post,
            "api/collections/members",
            json=payload
        )
        
        if response.status_code == 201:
            logger.info("Member created successfully")
            member_id = response.json().get('id')
            
            logger.info(f"Successfully created member with ID: {member_id}")
            return jsonify(status_success(f"Member created with id: {member_id}")), 201
        else:
            logger.error(f"Failed to create member. Status code: {response.status_code}, Response: {response.text}")
            return jsonify(status_error("Couldn't create member")), 500
    except Exception as e:
        logger.exception(f"Exception occurred while creating member: {str(e)}")
        return jsonify(status_error(f"Error creating member: {str(e)}")), 500

# Override the default create_resource with our custom implementation
members_resource.override_route('create_resource', _custom_create_member)

# Define a custom implementation for delete_member
def _custom_delete_member(member_id):
    logger = Logger.get_logger("members_blueprint")
    manager = current_app.config["MANAGER"]
    logger.info("Attempting to delete a member")
    
    try:
        if not member_id:
            logger.warning("Member ID is required but not provided in the request")
            return jsonify(status_error("Member ID is required")), 400
        
        logger.info(f"Deleting member with ID: {member_id}")
        
        # First, fetch and delete all member answers for this member
        logger.info(f"Fetching member answers for member ID: {member_id}")
        member_answers_response = manager.make_api_request(
            requests.get,
            f"api/collections/member-answers?member.id_eq={member_id}"
        )
        
        if member_answers_response.status_code == 200:
            member_answers_data = member_answers_response.json()
            member_answers = member_answers_data.get('data', [])
            
            if member_answers:
                logger.info(f"Found {len(member_answers)} member answers to delete")
                
                # Delete each member answer
                for answer in member_answers:
                    answer_id = answer['id']
                    logger.info(f"Deleting member answer with ID: {answer_id}")
                    
                    delete_answer_response = manager.make_api_request(
                        requests.delete,
                        f"api/collections/member-answers/{answer_id}"
                    )
                    
                    if delete_answer_response.status_code != 200:
                        logger.error(f"Failed to delete member answer {answer_id}. Status code: {delete_answer_response.status_code}")
                        return jsonify(status_error(f"Failed to delete member answer {answer_id}")), 500
                
                logger.info(f"Successfully deleted all {len(member_answers)} member answers")
            else:
                logger.info("No member answers found for this member")
        else:
            logger.error(f"Failed to fetch member answers. Status code: {member_answers_response.status_code}")
            return jsonify(status_error("Failed to fetch member answers")), 500
        
        # Now delete the member
        logger.info(f"Proceeding to delete member with ID: {member_id}")
        response = manager.make_api_request(
            requests.delete,
            f"api/collections/members/{member_id}"
        )
        
        if response.status_code == 200:
            logger.info(f"Successfully deleted member with ID: {member_id}")
            return jsonify(status_success(f"Member and associated answers deleted successfully")), 200
        else:
            logger.error(f"Failed to delete member. Status code: {response.status_code}, Response: {response.text}")
            return jsonify(status_error("Couldn't delete member")), 500
            
    except Exception as e:
        logger.exception(f"Exception occurred while deleting member: {str(e)}")
        return jsonify(status_error(f"Error deleting member: {str(e)}")), 500

# Override the default delete_resource with our custom implementation
members_resource.override_route('delete_resource', _custom_delete_member)

def lobby_match_details(member_id=None):
    logger = Logger.get_logger("members_blueprint")
    manager = current_app.config["MANAGER"]
    logger.info("Attempting to fetch lobby details for a member")

    try:
        # Get the member_id from the parameter or URL parameter
        if not member_id:
            member_id = request.view_args.get('memberId')
        if not member_id:
            logger.warning("memberId is required but not provided in the request")
            return jsonify(status_error("memberId is required")), 400
        
        logger.info(f"Fetching lobby details for member with ID: {member_id}")        
        # Fetch member with related lobbies and matches
        response = manager.make_api_request(
            requests.get,
            f"api/collections/members?relations=lobbies,matches&userId_eq={member_id}"
        )

        if response.status_code != 200:
            logger.error(f"Failed to fetch member data. Status code: {response.status_code}, Response: {response.text}")
            return jsonify(status_error("Couldn't fetch member data")), 500

        member_data = response.json()['data']
        if not member_data:
            logger.warning(f"No member found with userId {member_id}")
            return jsonify(status_error("Member not found")), 404

        member = member_data[0]

        # Only check the first lobby (if any) for matches
        matches = member['matches']
        match = matches[0] if matches else None
        if match:
            logger.info(f"Found match with ID: {match['id']} for member with userId {member_id}")
            response = manager.make_api_request(
                requests.get,
                f"api/collections/matches/{match['id']}?relations=members"
            )
            if response.status_code == 200:
                match_data = response.json()
                # lobby with match details
                output = {
                    "lobby": member['lobbies'][0] if member['lobbies'] else None,
                    "match": match_data
                }      
                logger.info(f"Returning lobby and match details for member with userId {member_id}")
                return jsonify(status_success(output)), 200
            

        logger.info(f"No lobbies found for member with userId {member_id}")
        return jsonify(status_error("No lobbies or match found for this member")), 404

        
    except Exception as e:
        logger.exception(f"Exception occurred while fetching lobby details: {str(e)}")
        return jsonify(status_error(f"Error fetching lobby details: {str(e)}")), 500

# Lobby details with Match for user
@members_resource.register_additional_route('/api/v0/collections/members/<memberId>/lobbyMatch', methods=['GET'])
def lobby_match_details_route(memberId):
        return lobby_match_details(memberId)



# Use the blueprint from the ResourceBlueprint
members_bp = members_resource.blueprint