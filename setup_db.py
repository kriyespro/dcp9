import os
from dotenv import load_dotenv
from app import create_app, db
from flask_migrate import upgrade

def setup_database():
    # Load environment variables
    load_dotenv()
    
    # Get the environment
    env = os.getenv('FLASK_ENV', 'development')
    print(f"Setting up database for {env} environment")
    
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        # Run database migrations
        upgrade()
        
        print("Database setup completed successfully!")
        print(f"Using database: {app.config['SQLALCHEMY_DATABASE_URI']}")

if __name__ == '__main__':
    setup_database() 