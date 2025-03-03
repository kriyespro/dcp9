from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from flask_principal import Principal
from flask_wtf.csrf import CSRFProtect
from datetime import datetime

from config import Config, DevelopmentConfig

# Initialize Flask extensions
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
migrate = Migrate()
mail = Mail()
principal = Principal()
csrf = CSRFProtect()

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    principal.init_app(app)
    csrf.init_app(app)

    # Register blueprints
    from app.routes.main import main as main_bp
    app.register_blueprint(main_bp)

    from app.routes.auth import auth as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.routes.api import api as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # Register error handlers
    from app.utils.error_handlers import register_error_handlers
    register_error_handlers(app)

    # Register CLI commands
    from app.commands import init_db_command
    app.cli.add_command(init_db_command)

    # Add template context processors
    @app.context_processor
    def utility_processor():
        return {'now': datetime.utcnow()}

    return app

from app.models import User

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id)) 