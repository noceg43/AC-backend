from app import create_app
import os
from dotenv import load_dotenv

load_dotenv()

app = create_app()

if __name__ == '__main__':
    is_dev = os.environ.get("FLASK_ENV", "development") == "development"
    app.run(debug=is_dev, host='0.0.0.0')
