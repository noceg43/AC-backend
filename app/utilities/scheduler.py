import schedule
import time
import threading
from datetime import datetime, timezone
from ..utilities.log import Logger
import requests
from ..ml.MatchingAlgorithm import AlphaConnectMatcher


class LobbyScheduler:
    def __init__(self, manager):
        self.manager = manager
        self.logger = Logger.get_logger("LobbyScheduler")
        self.scheduler_thread = None
        self.running = False
        self.scheduled_jobs = {}  # Track scheduled jobs by lobby_id
        
    def start(self):
        """Start the scheduler in a background thread"""
        if self.running:
            self.logger.warning("Scheduler is already running")
            return
            
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        self.logger.info("Scheduler started successfully")
        
        # Fetch existing lobbies and schedule them
        self.fetch_and_schedule_existing_lobbies()
        
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        self.scheduled_jobs.clear()
        self.logger.info("Scheduler stopped")
        
    def _run_scheduler(self):
        """Run the scheduler loop in background thread"""
        while self.running:
            current_time = datetime.now(timezone.utc)
            
            # Check for scheduled jobs that need to be executed
            jobs_to_execute = []
            for lobby_id, job_info in list(self.scheduled_jobs.items()):
                if not job_info.get('executed', False) and current_time >= job_info['scheduled_date']:
                    jobs_to_execute.append((lobby_id, job_info))
            
            # Execute due jobs
            for lobby_id, job_info in jobs_to_execute:
                self._execute_pre_event_function(lobby_id, job_info['lobby_data'])
                # Mark as executed and remove from scheduled jobs
                del self.scheduled_jobs[lobby_id]
            
            # Also run any other pending schedule jobs (if any)
            schedule.run_pending()
            time.sleep(1)
            
    def fetch_and_schedule_existing_lobbies(self):
        """Fetch existing lobbies from API and schedule pre-event functions"""
        try:
            self.logger.info("Fetching existing lobbies to schedule")
            
            # Make API request to get all lobbies with relations
            response = self.manager.make_api_request(
                requests.get,
                "api/collections/lobbies?relations=questionSet.questions.answers"
            )
            
            if response.status_code != 200:
                self.logger.error(f"Failed to fetch lobbies: {response.status_code} - {response.text}")
                return
                
            lobbies_data = response.json()
            self.logger.debug(f"Received lobbies data: {lobbies_data}")
            
            if 'data' not in lobbies_data:
                self.logger.warning("No data field in lobbies response")
                return
                
            lobbies = lobbies_data['data']
            self.logger.info(f"Found {len(lobbies)} existing lobbies")
            
            current_time = datetime.now(timezone.utc)
            scheduled_count = 0
            
            for lobby in lobbies:
                try:
                    lobby_id = lobby.get('id')
                    pre_event_date_str = lobby.get('preEventDate')
                    
                    if not lobby_id or not pre_event_date_str:
                        self.logger.warning(f"Lobby missing required fields: id={lobby_id}, preEventDate={pre_event_date_str}")
                        continue
                        
                    # Parse the preEventDate
                    pre_event_date = datetime.fromisoformat(pre_event_date_str.replace("Z", "+00:00"))
                    
                    # Only schedule if the preEventDate is in the future
                    if pre_event_date > current_time:
                        self.schedule_pre_event_function(lobby_id, pre_event_date, lobby)
                        scheduled_count += 1
                        self.logger.info(f"Scheduled pre-event function for lobby {lobby_id} at {pre_event_date}")
                    else:
                        self.logger.info(f"Lobby {lobby_id} preEventDate {pre_event_date} has already passed, skipping")
                        
                except Exception as e:
                    self.logger.error(f"Error processing lobby {lobby.get('id', 'unknown')}: {str(e)}")
                    continue
                    
            self.logger.info(f"Successfully scheduled {scheduled_count} lobbies")
            
        except Exception as e:
            self.logger.exception(f"Error fetching and scheduling existing lobbies: {str(e)}")
            
    def schedule_pre_event_function(self, lobby_id, pre_event_date, lobby_data=None):
        """Schedule a function to run at the lobby's preEventDate"""
        try:
            # Store the scheduled job info with target datetime
            self.scheduled_jobs[lobby_id] = {
                'scheduled_date': pre_event_date,
                'lobby_data': lobby_data,
                'executed': False
            }
            
            self.logger.info(f"Scheduled pre-event function for lobby {lobby_id} at {pre_event_date}")
            
        except Exception as e:
            self.logger.error(f"Error scheduling pre-event function for lobby {lobby_id}: {str(e)}")
            
    def _execute_pre_event_function(self, lobby_id, lobby_data=None):
        """Execute the pre-event function for a specific lobby"""
        try:
            self.logger.info(f"🎉 PRE-EVENT TRIGGERED for lobby {lobby_id}")
            
            if lobby_data:
                lobby_name = lobby_data.get('name', 'Unknown')
                event_date = lobby_data.get('eventDate', 'Unknown')
                max_members = lobby_data.get('maxMembers', 'Unknown')
                
                self.logger.info(f"Lobby Details:")
                self.logger.info(f"  - Name: {lobby_name}")
                self.logger.info(f"  - Event Date: {event_date}")
                self.logger.info(f"  - Max Members: {max_members}")
                
                # Print to console as requested
                print(f"🚀 PRE-EVENT FUNCTION EXECUTED!")
                print(f"📍 Lobby: {lobby_name} (ID: {lobby_id})")
                print(f"📅 Event Date: {event_date}")
                print(f"👥 Max Members: {max_members}")
                print(f"⏰ Triggered at: {datetime.now(timezone.utc)}")
                print("-" * 50)
            else:
                print(f"🚀 PRE-EVENT FUNCTION EXECUTED for lobby {lobby_id}")
                print(f"⏰ Triggered at: {datetime.now(timezone.utc)}")
                print("-" * 50)
            
            # Execute matching algorithm
            self._execute_matching_algorithm(lobby_id)
                
            self.logger.info(f"Successfully executed pre-event function for lobby {lobby_id}")
                
        except Exception as e:
            self.logger.error(f"Error executing pre-event function for lobby {lobby_id}: {str(e)}")

    def _execute_matching_algorithm(self, lobby_id):
        """Execute the matching algorithm for a specific lobby"""
        try:
            self.logger.info(f"🔥 Starting matching algorithm for lobby {lobby_id}")
            
            # Check if matching algorithm is available
            if AlphaConnectMatcher is None:
                self.logger.error("MatchingAlgorithm not available - import failed")
                return
            
            # Step 1: Fetch questions with match data
            questions_data = self._fetch_questions_with_match()
            if not questions_data:
                self.logger.warning(f"No questions data found for matching in lobby {lobby_id}")
                return
            
            # Step 2: Initialize and run the matching algorithm
            matcher = AlphaConnectMatcher(questions_data)
            matches = matcher.create_matching()
            
            if not matches:
                self.logger.warning(f"No matches generated for lobby {lobby_id}")
                return
            
            self.logger.info(f"Generated {len(matches)} matches for lobby {lobby_id}")
            
            # Step 3: Only delete existing matches if new matches were generated
            self._delete_existing_matches(lobby_id)
            
            # Step 4: Create new matches
            self._create_new_matches(lobby_id, matches)
            
            self.logger.info(f"Successfully completed matching algorithm for lobby {lobby_id}")
            
        except Exception as e:
            self.logger.error(f"Error executing matching algorithm for lobby {lobby_id}: {str(e)}")

    def _fetch_questions_with_match(self):
        """Fetch questions with match data by calling the questions logic directly"""
        try:
            self.logger.info("Fetching questions with match data using direct function logic")
            
            # Replicate the logic from questions_with_match_handler directly
            # First, fetch all questions
            self.logger.info("Fetching all questions")
            questions_response = self.manager.make_api_request(
                requests.get,
                "api/collections/questions"
            )

            if questions_response.status_code != 200:
                self.logger.error(f"Failed to fetch questions. Status code: {questions_response.status_code}")
                return None

            questions_data = questions_response.json()['data']
            if not questions_data:
                self.logger.warning("No questions found")
                return None

            # Combine questions with their member answers
            questions_with_answers = []
            for question in questions_data:
                question_id = question['id']
                
                # Fetch member answers for this specific question
                self.logger.info(f"Fetching member answers for question ID: {question_id}")
                member_answers_response = self.manager.make_api_request(
                    requests.get,
                    f"api/collections/member-answers?relations=question&question.id_eq={question_id}"
                )

                member_answers = []
                if member_answers_response.status_code == 200:
                    member_answers = member_answers_response.json()['data']
                else:
                    self.logger.warning(f"Failed to fetch member answers for question {question_id}. Status code: {member_answers_response.status_code}")

                question_with_answers = {
                    "question": question,
                    "member_answers": member_answers
                }
                questions_with_answers.append(question_with_answers)

            self.logger.info(f"Successfully retrieved {len(questions_with_answers)} questions with their member answers")
            return {"data": questions_with_answers}
                
        except Exception as e:
            self.logger.error(f"Error fetching questions with match data: {str(e)}")
            return None

    def _delete_existing_matches(self, lobby_id):
        """Delete all existing matches for a specific lobby"""
        try:
            self.logger.info(f"Deleting existing matches for lobby {lobby_id}")
            
            # Query for existing matches
            matches_response = self.manager.make_api_request(
                requests.get,
                f"api/collections/matches?relations=lobby&lobby.id_eq={lobby_id}"
            )
            
            if matches_response.status_code == 200:
                matches_data = matches_response.json().get('data', [])
                self.logger.info(f"Found {len(matches_data)} existing matches to delete")
                
                # Delete each match
                for match in matches_data:
                    match_id = match['id']
                    delete_response = self.manager.make_api_request(
                        requests.delete,
                        f"api/collections/matches/{match_id}"
                    )
                    
                    if delete_response.status_code in [200, 204]:
                        self.logger.info(f"Successfully deleted match {match_id}")
                    else:
                        self.logger.error(f"Failed to delete match {match_id}. Status code: {delete_response.status_code}")
                        
            elif matches_response.status_code == 404:
                self.logger.info(f"No existing matches found for lobby {lobby_id}")
            else:
                self.logger.error(f"Failed to fetch existing matches. Status code: {matches_response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Error deleting existing matches for lobby {lobby_id}: {str(e)}")

    def _create_new_matches(self, lobby_id, matches):
        """Create new matches in the database"""
        try:
            self.logger.info(f"Creating {len(matches)} new matches for lobby {lobby_id}")
            
            for i, (member1_id, member2_id, score) in enumerate(matches):
                match_data = {
                    "memberIds": [member1_id, member2_id],
                    "lobbyId": lobby_id,
                    "score": score
                }
                
                create_response = self.manager.make_api_request(
                    requests.post,
                    "api/collections/matches",
                    json=match_data
                )
                
                if create_response.status_code == 201:
                    match_result = create_response.json()
                    match_id = match_result.get('id', 'unknown')
                    self.logger.info(f"Successfully created match {i+1}/{len(matches)} (ID: {match_id}) between members {member1_id} and {member2_id}")
                else:
                    self.logger.error(f"Failed to create match between {member1_id} and {member2_id}. Status code: {create_response.status_code}")
                    
            self.logger.info(f"Successfully created all {len(matches)} matches for lobby {lobby_id}")
            
        except Exception as e:
            self.logger.error(f"Error creating new matches for lobby {lobby_id}: {str(e)}")
            
    def schedule_new_lobby(self, lobby_data):
        """Schedule a newly created lobby"""
        try:
            lobby_id = lobby_data.get('id')
            pre_event_date_str = lobby_data.get('preEventDate')
            
            if not lobby_id or not pre_event_date_str:
                self.logger.warning(f"Cannot schedule lobby - missing required fields: id={lobby_id}, preEventDate={pre_event_date_str}")
                return False
                
            pre_event_date = datetime.fromisoformat(pre_event_date_str.replace("Z", "+00:00"))
            current_time = datetime.now(timezone.utc)
            
            if pre_event_date > current_time:
                self.schedule_pre_event_function(lobby_id, pre_event_date, lobby_data)
                return True
            else:
                self.logger.info(f"New lobby {lobby_id} preEventDate has already passed, not scheduling")
                return False
                
        except Exception as e:
            self.logger.error(f"Error scheduling new lobby {lobby_data.get('id', 'unknown')}: {str(e)}")
            return False

    def refresh_lobby_schedule(self, lobby_id):
        """Refresh the schedule for a specific lobby (fetch latest data and reschedule)"""
        try:
            self.logger.info(f"Refreshing schedule for lobby {lobby_id}")
            
            # First, cancel any existing schedule for this lobby
            self.cancel_lobby_schedule(lobby_id)
            
            # Fetch the latest lobby data
            response = self.manager.make_api_request(
                requests.get,
                f"api/collections/lobbies/{lobby_id}?relations=questionSet.questions.answers"
            )
            
            if response.status_code == 200:
                lobby_data = response.json()
                
                # Schedule the lobby with updated data
                success = self.schedule_new_lobby(lobby_data)
                if success:
                    self.logger.info(f"Successfully refreshed schedule for lobby {lobby_id}")
                else:
                    self.logger.info(f"Lobby {lobby_id} not scheduled (preEventDate may have passed)")
                    
                return success
            elif response.status_code == 404:
                self.logger.info(f"Lobby {lobby_id} not found - removing any existing schedule")
                return False
            else:
                self.logger.error(f"Failed to fetch lobby {lobby_id} for refresh. Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error refreshing schedule for lobby {lobby_id}: {str(e)}")
            return False

    def update_lobby_schedule(self, lobby_data):
        """Update the schedule for a lobby when it's edited"""
        try:
            lobby_id = lobby_data.get('id')
            if not lobby_id:
                self.logger.warning("Cannot update lobby schedule - no lobby ID provided")
                return False
                
            self.logger.info(f"Updating schedule for edited lobby {lobby_id}")
            
            # Cancel existing schedule
            self.cancel_lobby_schedule(lobby_id)
            
            # Schedule with new data
            return self.schedule_new_lobby(lobby_data)
            
        except Exception as e:
            self.logger.error(f"Error updating schedule for lobby {lobby_data.get('id', 'unknown')}: {str(e)}")
            return False
            
    def cancel_lobby_schedule(self, lobby_id):
        """Cancel scheduled job for a specific lobby"""
        try:
            if lobby_id in self.scheduled_jobs:
                del self.scheduled_jobs[lobby_id]
                self.logger.info(f"Cancelled scheduled job for lobby {lobby_id}")
                return True
            else:
                self.logger.warning(f"No scheduled job found for lobby {lobby_id}")
                return False
        except Exception as e:
            self.logger.error(f"Error cancelling schedule for lobby {lobby_id}: {str(e)}")
            return False
            
    def get_scheduled_lobbies(self):
        """Get list of currently scheduled lobbies"""
        return list(self.scheduled_jobs.keys())
        
    def get_scheduler_status(self):
        """Get current scheduler status"""
        return {
            'running': self.running,
            'scheduled_lobbies_count': len(self.scheduled_jobs),
            'scheduled_lobbies': [
                {
                    'lobby_id': lobby_id,
                    'scheduled_date': job_info['scheduled_date'].isoformat(),
                    'lobby_name': job_info['lobby_data'].get('name', 'Unknown') if job_info['lobby_data'] else 'Unknown'
                }
                for lobby_id, job_info in self.scheduled_jobs.items()
            ]
        }
