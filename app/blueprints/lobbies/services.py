from flask import current_app, jsonify, request
import requests
from ..status_library import status_success, status_error
from ...utilities.log import Logger
from ...utilities.lobby import Lobby
from ..utilities.lobby_utilities import check_member_exists, check_lobby_exists, first_available_lobby, is_lobby_available, add_member_to_lobby, quit_lobby

def create_lobby_service():
    logger = Logger.get_logger("lobbies_service")
    manager = current_app.config["MANAGER"]
    logger.info("Attempting to create a new lobby")
    
    try:
        # Check if a lobby already exists
        logger.info("Checking if a lobby already exists")
        existing_lobbies_response = manager.make_api_request(
            requests.get,
            "api/collections/lobbies"
        )
        
        if existing_lobbies_response.status_code == 200:
            existing_lobbies = existing_lobbies_response.json()
            if existing_lobbies['total'] > 0:
                logger.warning("A lobby already exists, cannot create another one")
                return jsonify(status_error("A lobby already exists, cannot create another one")), 400
        
        # Get the payload from the request
        payload = request.json
        logger.info("Creating new lobby")
        logger.debug(f"Lobby payload: {payload}")
        
        # Make the API request directly
        response = manager.make_api_request(
            requests.post,
            "api/collections/lobbies",
            json=payload
        )
        
        if response.status_code == 201:
            logger.info("Lobby created successfully")
            # Create a new Lobby object and store it in the manager
            manager.lobby = Lobby(manager.url, response.json())
            lobby_id = manager.lobby.id
            
            # Schedule the new lobby with the scheduler
            scheduler = current_app.config.get('SCHEDULER')
            if scheduler:
                try:
                    scheduler.schedule_new_lobby(response.json())
                    logger.info(f"Successfully scheduled new lobby {lobby_id}")
                except Exception as e:
                    logger.error(f"Failed to schedule new lobby {lobby_id}: {str(e)}")
            else:
                logger.warning("Scheduler not available, lobby not scheduled")
            
            logger.info(f"Successfully created lobby with ID: {lobby_id}")
            return jsonify(status_success(f"lobby created with id: {lobby_id}")), 201
        else:
            logger.error(f"Failed to create lobby. Status code: {response.status_code}, Response: {response.text}")
            return jsonify(status_error("couldn't create lobby")), 500
    except Exception as e:
        logger.exception(f"Exception occurred while creating lobby: {str(e)}")
        return jsonify(status_error(f"Error creating lobby: {str(e)}")), 500

def update_lobby_service(lobby_id):
    logger = Logger.get_logger("lobbies_service")
    manager = current_app.config["MANAGER"]
    logger.info(f"Attempting to update lobby with ID: {lobby_id}")
    
    try:
        if not lobby_id:
            logger.warning("Lobby ID is required but not provided in the request")
            return jsonify(status_error("Lobby ID is required")), 400
            
        # Get the payload from the request
        payload = request.json
        logger.info("Updating lobby")
        logger.debug(f"Update lobby payload: {payload}")
        
        # Make the API request to update the lobby
        response = manager.make_api_request(
            requests.patch,
            f"api/collections/lobbies/{lobby_id}",
            json=payload
        )
        
        if response.status_code == 200:
            updated_lobby_data = response.json()
            logger.info(f"Successfully updated lobby {lobby_id}")
            
            # Update the scheduler with the new lobby data
            scheduler = current_app.config.get('SCHEDULER')
            if scheduler:
                try:
                    scheduler.update_lobby_schedule(updated_lobby_data)
                    logger.info(f"Successfully updated schedule for lobby {lobby_id}")
                except Exception as e:
                    logger.error(f"Failed to update schedule for lobby {lobby_id}: {str(e)}")
            else:
                logger.warning("Scheduler not available, schedule not updated")
            
            return jsonify(status_success(f"Updated lobby {lobby_id}", data=updated_lobby_data)), 200
        else:
            logger.error(f"Failed to update lobby {lobby_id}. Status code: {response.status_code}, Response: {response.text}")
            return jsonify(status_error(f"Failed to update lobby {lobby_id}")), response.status_code
            
    except Exception as e:
        logger.exception(f"Exception occurred while updating lobby {lobby_id}: {str(e)}")
        return jsonify(status_error(f"Error updating lobby: {str(e)}")), 500

def delete_lobby_service(lobby_id):
    logger = Logger.get_logger("lobbies_service")
    manager = current_app.config["MANAGER"]
    logger.info(f"Attempting to delete lobby with ID: {lobby_id}")
    
    try:
        if not lobby_id:
            logger.warning("Lobby ID is required but not provided in the request")
            return jsonify(status_error("Lobby ID is required")), 400
        
        # First, check if the lobby exists
        logger.info(f"Checking if lobby {lobby_id} exists")
        lobby_data = check_lobby_exists(manager, lobby_id)
        if not lobby_data:
            logger.warning(f"Lobby with ID {lobby_id} does not exist")
            return jsonify(status_error("Lobby does not exist")), 404
        
        # Get all members in the lobby
        members = lobby_data.get('members', [])
        logger.info(f"Found {len(members)} members in lobby {lobby_id}")
        
        # Step 1: Delete all matches associated with this lobby
        _delete_lobby_matches(manager, lobby_id)
        
        # Step 2: Remove lobby from all members' lobby arrays
        if members:
            _remove_lobby_from_members(manager, lobby_id, members)
        
        # Cancel any scheduled jobs for this lobby
        scheduler = current_app.config.get('SCHEDULER')
        if scheduler:
            try:
                scheduler.cancel_lobby_schedule(lobby_id)
                logger.info(f"Cancelled scheduled job for lobby {lobby_id}")
            except Exception as e:
                logger.warning(f"Failed to cancel scheduled job for lobby {lobby_id}: {str(e)}")
        
        # Finally, delete the lobby itself
        logger.info(f"Proceeding to delete lobby with ID: {lobby_id}")
        response = manager.make_api_request(
            requests.delete,
            f"api/collections/lobbies/{lobby_id}"
        )
        
        if response.status_code in [200, 204]:
            logger.info(f"Successfully deleted lobby {lobby_id}")
            return jsonify(status_success(f"Deleted lobby {lobby_id}")), 200
        else:
            logger.error(f"Failed to delete lobby {lobby_id}. Status code: {response.status_code}, Response: {response.text}")
            return jsonify(status_error(f"Failed to delete lobby {lobby_id}")), response.status_code
            
    except Exception as e:
        logger.exception(f"Exception occurred while deleting lobby {lobby_id}: {str(e)}")
        return jsonify(status_error(f"Error deleting lobby: {str(e)}")), 500

def join_lobby_service():
    logger = Logger.get_logger("lobbies_service")
    manager = current_app.config["MANAGER"]
    logger.info("Handling request to join a lobby")

    try:
        payload = request.json
        logger.debug(f"Join lobby payload: {payload}")

        # Validate the memberId in the payload
        member_id = payload.get('memberId')
        if not member_id:
            logger.warning("memberId is required but not provided in the request")
            return jsonify(status_error("memberId is required")), 400
        
        exists = check_member_exists(manager, member_id)
        if not exists:
            logger.warning(f"Member with ID {member_id} does not exist")
            return jsonify(status_error("Member does not exist")), 404

        # Validate the lobbyId in the payload
        # If lobbyId is not provided, find the first available lobby, else check if the lobby provided exists and is available
        lobby_id = payload.get('lobbyId')
        lobby_data = None
        if lobby_id:
            lobby_data= check_lobby_exists(manager, lobby_id)
            lobby_available = is_lobby_available(manager, lobby_data, member_id)
            lobby_data = lobby_data if lobby_available else None
        else:
            lobby_data = first_available_lobby(manager, member_id)
            lobby_id = lobby_data['id']
            if not lobby_data:
                logger.info("No available lobby found, creating a new one")
                return jsonify(status_error("No available lobby found")), 404
            logger.info(f"Found active lobby with ID: {lobby_id}")
        
        if lobby_data:
            updated_lobby = add_member_to_lobby(manager, lobby_data['id'], member_id)
            return jsonify(status_success(f"Joined lobby with ID: {updated_lobby['id']}", data= updated_lobby)), 200
        else:
            logger.warning(f"Lobby with ID {lobby_id} does not exist or is not available")
            return jsonify(status_error("Lobby does not exist or is not available")), 404

    except Exception as e:
        logger.exception(f"Exception occurred while joining lobby: {str(e)}")
        return jsonify(status_error(f"An unexpected error occurred: {str(e)}")), 500

def quit_lobby_service():
    logger = Logger.get_logger("lobbies_service")
    manager = current_app.config["MANAGER"]
    logger.info("Handling request to quit a lobby")

    try:
        payload = request.json
        logger.debug(f"Quit lobby payload: {payload}")

        # Validate the memberId in the payload
        member_id = payload.get('memberId')
        if not member_id:
            logger.warning("memberId is required but not provided in the request")
            return jsonify(status_error("memberId is required")), 400
        
        exists = check_member_exists(manager, member_id)
        if not exists:
            logger.warning(f"Member with ID {member_id} does not exist")
            return jsonify(status_error("Member does not exist")), 404

        # Validate the lobbyId in the payload
        lobby_id = payload.get('lobbyId')
        if not lobby_id:
            logger.warning("lobbyId is required but not provided in the request")
            return jsonify(status_error("lobbyId is required")), 400
        lobby_data = check_lobby_exists(manager, lobby_id)
        if not lobby_data:
            logger.warning(f"Lobby with ID {lobby_id} does not exist")
            return jsonify(status_error("Lobby does not exist")), 404
        # Check if the member is in the lobby
        current_members = lobby_data.get('members', [])
        if not any(member['id'] == member_id for member in current_members):
            logger.warning(f"Member with ID {member_id} is not in the lobby {lobby_id}")
            return jsonify(status_error("Member is not in the lobby")), 404
        # Remove the member from the lobby
        updated_lobby = quit_lobby(manager, lobby_id, member_id)
        if updated_lobby:
            logger.info(f"Member {member_id} has quit the lobby {lobby_id}")
            return jsonify(status_success(f"Member {member_id} has quit the lobby {lobby_id}", data=updated_lobby)), 200
        else:
            logger.error(f"Failed to remove member {member_id} from lobby {lobby_id}")
            return jsonify(status_error("Failed to remove member from lobby")), 500
    except Exception as e:
        logger.exception(f"Exception occurred while quitting lobby: {str(e)}")
        return jsonify(status_error(f"An unexpected error occurred: {str(e)}")), 500

def _delete_lobby_matches(manager, lobby_id):
    """Delete all matches associated with a specific lobby"""
    logger = Logger.get_logger("lobbies_service")
    logger.info(f"Searching for matches associated with lobby {lobby_id}")
    
    # Query directly for matches filtering by lobby ID
    matches_response = manager.make_api_request(
        requests.get,
        f"api/collections/matches?relations=lobby&lobby.id_eq={lobby_id}"
    )
    
    if matches_response.status_code == 200:
        matches_data = matches_response.json().get('data', [])
        logger.info(f"Found {len(matches_data)} matches associated with lobby {lobby_id}")

        # Delete each match associated with this lobby
        for match in matches_data:
            match_id = match['id']
            logger.info(f"Deleting match with ID: {match_id} for lobby {lobby_id}")

            delete_match_response = manager.make_api_request(
                requests.delete,
                f"api/collections/matches/{match_id}"
            )

            if delete_match_response.status_code in [200, 204]:
                logger.info(f"Successfully deleted match {match_id}")
            else:
                logger.error(f"Failed to delete match {match_id}. Status code: {delete_match_response.status_code}")
                raise Exception(f"Failed to delete match {match_id}")
    elif matches_response.status_code == 404:
        # No matches found for this lobby, which is fine
        logger.info(f"No matches found for lobby {lobby_id}")
    else:
        logger.error(f"Failed to fetch matches for lobby {lobby_id}. Status code: {matches_response.status_code}")
        raise Exception(f"Failed to fetch matches for lobby {lobby_id}")

def _remove_lobby_from_members(manager, lobby_id, members):
    """Remove the lobby from all members' lobby arrays"""
    logger = Logger.get_logger("lobbies_service")
    logger.info(f"Removing lobby {lobby_id} from {len(members)} members")
    
    for member in members:
        member_id = member['id']
        logger.info(f"Removing lobby {lobby_id} from member {member_id}")
        
        # Fetch the member with their current lobbies
        member_response = manager.make_api_request(
            requests.get,
            f"api/collections/members/{member_id}?relations=lobbies"
        )
        
        if member_response.status_code == 200:
            member_data = member_response.json()
            current_lobbies = member_data.get('lobbies', [])
            
            # Remove the lobby from the member's lobbies array
            updated_lobbies = [lobby for lobby in current_lobbies if lobby['id'] != lobby_id]
            
            # Update the member with the new lobbies array using PATCH
            update_response = manager.make_api_request(
                requests.patch,
                f"api/collections/members/{member_id}",
                json={
                    "lobbies": updated_lobbies
                }
            )
            
            if update_response.status_code == 200:
                logger.info(f"Successfully removed lobby {lobby_id} from member {member_id}")
            else:
                logger.error(f"Failed to update member {member_id}. Status code: {update_response.status_code}")
                raise Exception(f"Failed to update member {member_id}")
        else:
            logger.error(f"Failed to fetch member {member_id}. Status code: {member_response.status_code}")
            raise Exception(f"Failed to fetch member {member_id}")
