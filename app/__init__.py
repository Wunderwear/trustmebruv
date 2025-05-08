from flask import Flask
from config import DevelopmentConfig, ProductionConfig
from .models import db
import datetime
import os

def create_app():
    app = Flask(__name__)
    
    # Print environment variables for debugging
    print(f"FLASK_ENV: {os.environ.get('FLASK_ENV')}")
    print(f"DATABASE_URL: {os.environ.get('DATABASE_URL')}")
    
    # Use different configurations based on environment
    if os.environ.get('FLASK_ENV') == 'production':
        app.config.from_object(ProductionConfig)
        print("Running in production mode with PostgreSQL")
        print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    else:
        app.config.from_object(DevelopmentConfig)
        print("Running in development mode with SQLite")
        print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    # Initialize extensions
    db.init_app(app)
    
    # Import and register blueprints
    from .routes import main_bp
    
    app.register_blueprint(main_bp)
    
    # Add template context processor for 'now' variable
    @app.context_processor
    def inject_now():
        return {'now': datetime.datetime.now()}
    
    with app.app_context():
        # Print the actual database engine being used
        print(f"Using database engine: {db.engine.name}")
        
        # Only create tables if they don't exist
        db.create_all()
    
    return app