from flask import Blueprint, jsonify, current_app
from ..resource_blueprint import ResourceBlueprint
from .services import (
    create_lobby_service,
    update_lobby_service,
    delete_lobby_service,
    join_lobby_service,
    quit_lobby_service,
)
from ..status_library import status_success, status_error

lobbies_resource = ResourceBlueprint('lobbies')
lobbies_bp = lobbies_resource.blueprint

@lobbies_resource.override_route('create_resource')
def create_lobby():
    return create_lobby_service()

@lobbies_resource.override_route('update_resource')
def update_lobby(lobby_id):
    return update_lobby_service(lobby_id)

@lobbies_resource.override_route('delete_resource')
def delete_lobby(lobby_id):
    return delete_lobby_service(lobby_id)

@lobbies_resource.register_additional_route('/api/v0/collections/lobbies/join', methods=['POST'])
def join_lobby_route():
    return join_lobby_service()

@lobbies_resource.register_additional_route('/api/v0/collections/lobbies/quit', methods=['POST'])
def quit_lobby_route():
    return quit_lobby_service()

# Register scheduler refresh route
@lobbies_resource.register_additional_route('/api/v0/collections/lobbies/scheduler/refresh', methods=['POST'])
def refresh_scheduler_route():
    """Manually refresh the scheduler to fetch and schedule existing lobbies"""
    logger = current_app.logger
    scheduler = current_app.config.get('SCHEDULER')

    if not scheduler:
        logger.error("Scheduler not available")
        return jsonify(status_error("Scheduler not available")), 500

    try:
        logger.info("Manually refreshing scheduler")
        scheduler.fetch_and_schedule_existing_lobbies()
        status = scheduler.get_scheduler_status()
        return jsonify(status_success("Scheduler refreshed successfully", data=status)), 200
    except Exception as e:
        logger.error(f"Error refreshing scheduler: {str(e)}")
        return jsonify(status_error(f"Error refreshing scheduler: {str(e)}")), 500

# Register refresh individual lobby schedule route
@lobbies_resource.register_additional_route('/api/v0/collections/lobbies/<lobby_id>/scheduler/refresh', methods=['POST'])
def refresh_lobby_schedule_route(lobby_id):
    """Refresh the schedule for a specific lobby"""
    logger = current_app.logger
    scheduler = current_app.config.get('SCHEDULER')

    if not scheduler:
        logger.error("Scheduler not available")
        return jsonify(status_error("Scheduler not available")), 500

    try:
        success = scheduler.refresh_lobby_schedule(lobby_id)
        if success:
            return jsonify(status_success(f"Refreshed schedule for lobby {lobby_id}")), 200
        else:
            return jsonify(status_error(f"Failed to refresh schedule for lobby {lobby_id} (lobby may not exist or preEventDate passed)")), 404
    except Exception as e:
        logger.error(f"Error refreshing schedule for lobby {lobby_id}: {str(e)}")
        return jsonify(status_error(f"Error refreshing schedule: {str(e)}")), 500

# TEMPORARY TESTING ENDPOINT - Remove in production
@lobbies_resource.register_additional_route('/api/v0/collections/lobbies/<lobby_id>/test-matching', methods=['POST'])
def test_matching_algorithm_route(lobby_id):
    """TEMPORARY: Test the matching algorithm for a specific lobby"""
    logger = current_app.logger
    scheduler = current_app.config.get('SCHEDULER')

    if not scheduler:
        logger.error("Scheduler not available")
        return jsonify(status_error("Scheduler not available")), 500

    try:
        logger.info(f"🧪 TESTING: Manually executing matching algorithm for lobby {lobby_id}")

        # Call the scheduler's matching algorithm directly
        scheduler._execute_matching_algorithm(lobby_id)

        # Fetch the results to show what was created
        matches_response = scheduler.manager.make_api_request(
            requests.get,
            f"api/collections/matches?lobby.id_eq={lobby_id}"
        )

        if matches_response.status_code == 200:
            matches_data = matches_response.json().get('data', [])
            result_data = {
                "lobby_id": lobby_id,
                "matches_created": len(matches_data),
                "matches": matches_data
            }

            return jsonify(status_success(f"Successfully executed matching algorithm for lobby {lobby_id}", data=result_data)), 200
        else:
            return jsonify(status_success(f"Matching algorithm executed for lobby {lobby_id} (no matches data retrieved)")), 200

    except Exception as e:
        logger.error(f"Error testing matching algorithm for lobby {lobby_id}: {str(e)}")
        return jsonify(status_error(f"Error testing matching algorithm: {str(e)}")), 500

# TEMPORARY TESTING ENDPOINT - Test questions data fetch
@lobbies_resource.register_additional_route('/api/v0/collections/test-questions-data', methods=['GET'])
def test_questions_data_route():
    """TEMPORARY: Test fetching questions with match data"""
    logger = current_app.logger
    scheduler = current_app.config.get('SCHEDULER')

    if not scheduler:
        logger.error("Scheduler not available")
        return jsonify(status_error("Scheduler not available")), 500

    try:
        logger.info("🧪 TESTING: Fetching questions with match data")

        # Call the scheduler's questions fetch method
        questions_data = scheduler._fetch_questions_with_match()

        if questions_data:
            return jsonify(status_success("Successfully fetched questions data", data=questions_data)), 200
        else:
            return jsonify(status_error("Failed to fetch questions data")), 500

    except Exception as e:
        logger.error(f"Error testing questions data fetch: {str(e)}")
        return jsonify(status_error(f"Error testing questions data fetch: {str(e)}")), 500

# Register cancel schedule route
@lobbies_resource.register_additional_route('/api/v0/collections/lobbies/<lobby_id>/scheduler/cancel', methods=['DELETE'])
def cancel_lobby_schedule_route(lobby_id):
    """Cancel the scheduled job for a specific lobby"""
    logger = current_app.logger
    scheduler = current_app.config.get('SCHEDULER')

    if not scheduler:
        logger.error("Scheduler not available")
        return jsonify(status_error("Scheduler not available")), 500

    try:
        success = scheduler.cancel_lobby_schedule(lobby_id)
        if success:
            return jsonify(status_success(f"Cancelled schedule for lobby {lobby_id}")), 200
        else:
            return jsonify(status_error(f"No scheduled job found for lobby {lobby_id}")), 404
    except Exception as e:
        logger.error(f"Error cancelling schedule for lobby {lobby_id}: {str(e)}")
        return jsonify(status_error(f"Error cancelling schedule: {str(e)}")), 500
