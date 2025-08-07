from flask import Blueprint, request, jsonify, current_app
from .resource_blueprint import ResourceBlueprint
from .status_library import status_success, status_error
from ..utilities.log import Logger
import requests

# Create a ResourceBlueprint for questions
questions_resource = ResourceBlueprint('questions')



def questions_with_match_handler():
    logger = Logger.get_logger("questions_blueprint")
    manager = current_app.config["MANAGER"]
    logger.info("Attempting to fetch all questions with their member answers")

    try:
        # First, fetch all questions
        logger.info("Fetching all questions")
        questions_response = manager.make_api_request(
            requests.get,
            "api/collections/questions"
        )

        if questions_response.status_code != 200:
            logger.error(f"Failed to fetch questions. Status code: {questions_response.status_code}, Response: {questions_response.text}")
            return jsonify(status_error("Couldn't fetch questions")), 500

        questions_data = questions_response.json()['data']
        if not questions_data:
            logger.warning("No questions found")
            return jsonify(status_error("No questions found")), 404

        # Combine questions with their member answers
        questions_with_answers = []
        for question in questions_data:
            question_id = question['id']
            
            # Fetch member answers for this specific question
            logger.info(f"Fetching member answers for question ID: {question_id}")
            member_answers_response = manager.make_api_request(
                requests.get,
                f"api/collections/member-answers?relations=question&question.id_eq={question_id}"
            )

            member_answers = []
            if member_answers_response.status_code == 200:
                member_answers = member_answers_response.json()['data']
            else:
                logger.warning(f"Failed to fetch member answers for question {question_id}. Status code: {member_answers_response.status_code}")

            question_with_answers = {
                "question": question,
                "member_answers": member_answers
            }
            questions_with_answers.append(question_with_answers)

        logger.info(f"Successfully retrieved {len(questions_with_answers)} questions with their member answers")
        return jsonify(status_success("Retrieved questions with member answers", questions_with_answers)), 200

    except Exception as e:
        logger.exception(f"Exception occurred while fetching questions with answers: {str(e)}")
        return jsonify(status_error(f"Error fetching questions with answers: {str(e)}")), 500


# Lobby details with Match for user
@questions_resource.register_additional_route('/api/v0/collections/questions-with-match', methods=['GET'])
def questions_with_match():
        return questions_with_match_handler()


# Use the blueprint from the ResourceBlueprint without any overrides
questions_bp = questions_resource.blueprint