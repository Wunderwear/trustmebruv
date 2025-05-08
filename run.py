from app import create_app
import os

# Force environment to production if it's set in the environment or command line
if os.environ.get('FLASK_ENV') == 'production':
    print("ENFORCING PRODUCTION MODE")
    os.environ['FLASK_ENV'] = 'production'

app = create_app()

if __name__ == '__main__':
    # Use environment variable to control debug mode
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    # In development, only listen on localhost
    # In production, this should be run behind a proper web server
    app.run(host='127.0.0.1', port=5000, debug=debug_mode) 