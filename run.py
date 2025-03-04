import os
from dotenv import load_dotenv
from app import create_app

# Load environment variables
load_dotenv()

# Get the environment
env = os.getenv('FLASK_ENV', 'development')
print(f"Starting application in {env} mode")

# Create the application
app = create_app()

if __name__ == '__main__':
    if env == 'production':
        # In production, use gunicorn
        print("Please use gunicorn for production:")
        print("gunicorn -c gunicorn_config.py wsgi:app")
    else:
        # In development, use Flask's development server
        app.run(host='0.0.0.0', port=5000) 