from flask import jsonify
from utilities.log import Logger
import requests
import time
from datetime import datetime, timezone

def check_member_exists(manager, member_id):
    url = f"api/collections/members/{member_id}"
    response = manager.make_api_request(
        requests.get,
        url
    )
    if response.status_code == 200:
        return True
    else:
        raise Exception(f"Member {member_id} not found")

def check_lobby_exists(manager, lobby_id):
    url = f"api/collections/lobbies/{lobby_id}?relations=members"
    response = manager.make_api_request(
        requests.get,
        url
    )
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Lobby {lobby_id} not found")

def is_lobby_available(manager, lobby_data, member_id):
    # Check if lobby is not full
    # Check if lobby accepts new users (lobby full & invite time expired)
    # Check if member is not in the lobby
    # Check if member has answered to the question of the question set
    maxMembers = lobby_data.get('maxMembers', 0)
    members = lobby_data.get('members', [])
    if len(members) >= maxMembers:
        raise Exception("Lobby is full")

    # example  "2024-03-20T18:00:00.000Z"
    if 'preEventDate' in lobby_data:
        pre_event_date = datetime.fromisoformat(lobby_data['preEventDate'].replace("Z", "+00:00"))
        if pre_event_date < datetime.now(timezone.utc):
            raise Exception("Lobby invite time has expired")

    # check if member is not in the lobby
    if any(member['id'] == member_id for member in members):
        raise Exception("Member is already in the lobby")
    
    # Check if the member has answered to the question of the question set
    question_set = lobby_data.get('questionSet', {})
    if not question_set:
        return True  # No question set, lobby is available
    questions = question_set.get('questions', [])

    if _has_member_answered_to_question_set(manager, question_set, member_id):
        return True
    else:
        raise Exception("Member has not answered the question set")
    # If all checks passed, the lobby is available

    return False


def _has_member_answered_to_question_set(manager, question_set, member_id):
    # Check if the user has answered to the question inside the question set
    questionSetId = question_set.get('id')
    
    questions = question_set.get('questions', [])
    if not questions or len(questions) == 0:
        return False

    questionIds = [question['id'] for question in questions]

    data = manager.make_api_request(
        requests.get,
        f"api/collections/member-answers?member.id_eq={member_id}&question.id_in={','.join(questionIds)}"
    )

    if data.status_code == 200:
        answers = data.json().get('data', [])
        if len(answers) == len(questions):
            return True

    return False


def first_available_lobby(manager, member_id):
    # Get all lobbies and check if any are available
    # use _is_lobby_available to check if the lobby is available
    allLobbies_response = manager.make_api_request(
        requests.get,
        "api/collections/lobbies?orderBy=creationDate"
    )
    if allLobbies_response.status_code == 200:
        all_lobbies = allLobbies_response.json().get('data', [])
        for lobby in all_lobbies:
            if is_lobby_available(manager, lobby, member_id):
                return lobby
    else:
        raise Exception(f"Failed to fetch lobbies: {allLobbies_response.text}")
    
    raise Exception("No available lobbies found")


def add_member_to_lobby(manager, lobby_id, member_id):
    # Add a member to the lobby and return the updated lobby data
    lobby = manager.make_api_request(
        requests.get,
        f"api/collections/lobbies/{lobby_id}?relations=members"
    )
    if lobby.status_code != 200:
        raise Exception(f"Lobby {lobby_id} not found")
    
    lobby_data = lobby.json()
    currentMembers = lobby_data.get('members', {})
    
    currentMembersIds = [member['id'] for member in currentMembers]

    if member_id in currentMembersIds:
        Logger.get_logger("lobby_utilities").info(f"Member {member_id} is already in the lobby {lobby_id}")
        return lobby_data
    # Add the member to the lobby
    add_member_response = manager.make_api_request(
        requests.patch,
        f"api/collections/lobbies/{lobby_id}",
        json=
         {
             "members" : [{"id": member_id} for member_id in currentMembersIds + [member_id]]
         }
    )

    if add_member_response.status_code != 200:
        raise Exception(f"Failed to add member {member_id} to lobby {lobby_id}: {add_member_response.text}")

    updated_lobby = manager.make_api_request(
        requests.get,
        f"api/collections/lobbies/{lobby_id}?relations=members"
    )
    if updated_lobby.status_code == 200:
        return updated_lobby.json()
    else:
        raise Exception(f"Failed to retrieve updated lobby: {updated_lobby.text}")


def quit_lobby(manager, lobby_id, member_id):
    # Remove a member from the lobby
    lobby = manager.make_api_request(
        requests.get,
        f"api/collections/lobbies/{lobby_id}?relations=members"
    )
    if lobby.status_code != 200:
        raise Exception(f"Lobby {lobby_id} not found")
    
    lobby_data = lobby.json()
    currentMembers = lobby_data.get('members', {})
    
    currentMembersIds = [member['id'] for member in currentMembers]

    if member_id not in currentMembersIds:
        raise Exception(f"Member {member_id} is not in the lobby {lobby_id}")
    # Remove the member from the lobby
    updated_members = [member for member in currentMembers if member['id'] != member_id]
    remove_member_response = manager.make_api_request(
        requests.patch,
        f"api/collections/lobbies/{lobby_id}",
        json={
            "members": updated_members
        }
    )
    if remove_member_response.status_code != 200:
        raise Exception(f"Failed to remove member {member_id} from lobby {lobby_id}: {remove_member_response.text}")
    updated_lobby = manager.make_api_request(
        requests.get,
        f"api/collections/lobbies/{lobby_id}?relations=members"
    )
    if updated_lobby.status_code == 200:
        return updated_lobby.json()
    else:
        raise Exception(f"Failed to retrieve updated lobby: {updated_lobby.text}")