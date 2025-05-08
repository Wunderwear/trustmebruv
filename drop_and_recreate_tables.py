from app import create_app, db

# Create the Flask app with PostgreSQL configuration
app = create_app()

with app.app_context():
    print("Dropping all tables...")
    db.drop_all()
    
    print("Creating tables with updated schema...")
    db.create_all()
    
    print("Tables successfully recreated!") 