from flask import Flask, jsonify
import os
import logging
from .utilities.manager import Manager
from .utilities.scheduler import LobbyScheduler
from .blueprints.status_library import status_error
from config import config_by_name

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Load configuration
    config_name = os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config_by_name[config_name]())

    # Initialize Manager and Scheduler
    manager = Manager(app.config['URL'], app.config['EMAIL'], app.config['PASSWORD'])
    app.config['MANAGER'] = manager
    scheduler = LobbyScheduler(manager)
    app.config['SCHEDULER'] = scheduler

    with app.app_context():
        # Import and register blueprints
        from .blueprints.lobbies import lobbies_bp
        from .blueprints.answers import answers_bp
        from .blueprints.question_sets import question_sets_bp
        from .blueprints.questions import questions_bp
        from .blueprints.members import members_bp
        from .blueprints.matches import matches_bp
        from .blueprints.feedback import feedbacks_bp
        from .blueprints.member_answers import member_answers_bp

        app.register_blueprint(lobbies_bp)
        app.register_blueprint(answers_bp)
        app.register_blueprint(question_sets_bp)
        app.register_blueprint(questions_bp)
        app.register_blueprint(members_bp)
        app.register_blueprint(matches_bp)
        app.register_blueprint(feedbacks_bp)
        app.register_blueprint(member_answers_bp)

        # Register routes
        @app.route('/', methods=["GET"])
        def api_list():
            """Return API information"""
            return jsonify({
                "message": "AC Backend API",
                "version": "1.0.0",
                "documentation": "/api/docs"
            })

        @app.route('/api/v0/scheduler/status', methods=["GET"])
        def scheduler_status():
            """Return scheduler status information"""
            scheduler = app.config.get('SCHEDULER')
            if scheduler:
                return jsonify(scheduler.get_scheduler_status())
            else:
                return jsonify({
                    "running": False,
                    "error": "Scheduler not initialized"
                }), 500

        # Register error handlers
        @app.errorhandler(404)
        def not_found(error):
            return jsonify(status_error("Resource not found")), 404

        @app.errorhandler(500)
        def internal_error(error):
            return jsonify(status_error("Internal server error")), 500

        # Start the scheduler
        if scheduler:
            scheduler.start()

    return app
