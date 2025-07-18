# AC-backend

AC backend is a Flask-based API service that acts as a proxy to [another API service](https://github.com/noceg43/aConnect).

## Docker Quick Start Guide

### Build the Docker Image
```bash
docker build -t ac-backend .
```

### Environment Selection

The application can run in two modes:
- **Development** (default): More verbose logging and detailed error messages
- **Production**: Minimal logging and user-friendly error messages without sensitive details

You can select the environment by setting the `FLASK_ENV` environment variable in the `.env` file.

### Set Up Environment Variables
Create a `.env` file with your credentials and the environment mode:
```
URL=http://your-api-url/
EMAIL=your-email@example.com
PASSWORD=your-password
FLASK_ENV=[production|development]
```

### Run the Container


**Option 1: Using environment variables directly**
```bash
docker run -p 5000:5000 \
  -e URL=http://your-api-url/ \
  -e EMAIL=your-email@example.com \
  -e PASSWORD=your-password \
  -e FLASK_ENV=[production|development] \
  ac-backend
```

**Option 2: Using a .env file (recommended)**

If your .env file is in the current directory:
```bash
# Linux/macOS
docker run -p 5000:5000 --env-file .env ac-backend

# Windows Command Prompt
docker run -p 5000:5000 --env-file .env ac-backend

# Windows PowerShell
docker run -p 5000:5000 --env-file .env ac-backend
```

If your .env file is in a specific path:
```bash
# Linux/macOS
docker run -p 5000:5000 --env-file /absolute/path/to/.env ac-backend

# Windows
docker run -p 5000:5000 --env-file /absolute/path/to/.env ac-backend
```

**For connecting to host services:**
```bash
docker run -p 5000:5000 \
  -e URL=http://host.docker.internal:1111/ \
  -e EMAIL=your-email@example.com \
  -e PASSWORD=your-password \
  --add-host=host.docker.internal:host-gateway \
  ac-backend
```

### Quick Examples

If your .env file is at `C:\Users\username\configs\.env`:
```bash
docker run -p 5000:5000 --env-file C:\Users\username\configs\.env ac-backend
```

To run the container in detached mode (background):
```bash
docker run -d -p 5000:5000 --env-file C:\Users\username\configs\.env ac-backend
```

To give the container a name (useful for management):
```bash
docker run -d -p 5000:5000 --name my-ac-backend --env-file C:\Users\username\configs\.env ac-backend
```

To run the container in production mode:
```bash
docker run -d -p 5000:5000 --name ac-backend-prod -e FLASK_ENV=production ---env-file C:\Users\username\configs\.env ac-backend
```

### Container Management

View running containers:
```bash
docker ps
```

Stop the container:
```bash
docker stop container_id
# or if named
docker stop my-ac-backend
```

### Access the API
Once running, access the API at `http://localhost:5000/`

## Development Setup (without Docker)

If you prefer to run the application directly without Docker:

1. Create a virtual environment:
   ```bash
   python -m venv env
   ```

2. Activate the environment:
   - Windows: `env\Scripts\activate`
   - Unix/MacOS: `source env/bin/activate`

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with the following content:
   ```
   URL=http://your-api-url/
   EMAIL=your-email@example.com
   PASSWORD=your-password
   FLASK_ENV=[production|development]
   ```


5. Run the application:
   ```bash
   flask run
   ```

   
> [!WARNING]  
> If the variable FLASK_ENV is set on production, the server will not run on windows due to missing dependencies

## API Documentation

For API documentation, visit `/api` after starting the application.

For a comprehensive guide to the project, please see the [documentation](doc/project_overview.md).