# AC-backend

AC backend is a Flask-based API service that acts as a proxy to another API service. It provides a RESTful interface for managing lobbies, members, questions, and other resources.

## Features

*   **RESTful API:** A comprehensive API for managing the application's resources.
*   **Authentication:** Authenticated access to the underlying API service.
*   **Background Jobs:** A scheduler for running background tasks, such as lobby management.
*   **Machine Learning:** A matching algorithm for finding suitable matches between members.
*   **Dockerized:** The application is fully containerized for easy deployment.

## Architecture

The application is built using the Flask web framework and follows the application factory pattern. The main components are:

*   **Application Factory (`app/__init__.py`):** Creates and configures the Flask application instance.
*   **Blueprints (`app/blueprints`):** Organizes the application into smaller, reusable components. Each resource has its own blueprint.
*   **ResourceBlueprint (`app/blueprints/resource_blueprint.py`):** A custom class for creating RESTful blueprints with standard CRUD operations.
*   **Manager (`app/utilities/manager.py`):** A class for managing the interaction with the external API service.
*   **Scheduler (`app/utilities/scheduler.py`):** A class for managing background jobs.
*   **Configuration (`config.py`):** A file for managing the application's configuration for different environments.

## Getting Started

### Prerequisites

*   Python 3.8+
*   Docker (optional)

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-username/ac-backend.git
    cd ac-backend
    ```

2.  Create a virtual environment:
    ```bash
    python -m venv env
    source env/bin/activate
    ```

3.  Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Configuration

Create a `.env` file in the root directory with the following variables:

```
URL=http://your-api-url/
EMAIL=your-email@example.com
PASSWORD=your-password
FLASK_ENV=[production|development]
```

### Running the Application

#### Without Docker

```bash
flask run
```

#### With Docker

1.  Build the Docker image:
    ```bash
    docker build -t ac-backend .
    ```

2.  Run the Docker container:
    ```bash
    docker run -p 5000:5000 --env-file .env ac-backend
    ```

## API Documentation

The API documentation is available at the `/api/docs` endpoint after starting the application.

### Endpoints

Here is a summary of the available endpoints:

*   **Lobbies:** `/api/v0/collections/lobbies`
*   **Members:** `/api/v0/collections/members`
*   **Questions:** `/api/v0/collections/questions`
*   **Answers:** `/api/v0/collections/answers`
*   **Question Sets:** `/api/v0/collections/question-sets`
*   **Matches:** `/api/v0/collections/matches`
*   **Feedback:** `/api/v0/collections/feedbacks`
*   **Member Answers:** `/api/v0/collections/member-answers`

For more details on the available endpoints and their usage, please refer to the API documentation at `/api/docs`.

## Running Tests

To run the tests, use the following command:

```bash
pytest
```

*(Note: No tests are currently implemented.)*
