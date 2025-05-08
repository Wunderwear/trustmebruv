import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    basedir = os.path.abspath(os.path.dirname(__file__))
    
    # Add a secret key for Flask sessions
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-super-secret-key-here'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API Keys
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
    STABILITY_KEY = os.environ.get('STABILITY_KEY')
    
    # Twitter API credentials
    TWITTER_API_KEY = os.environ.get('TWITTER_API_KEY')
    TWITTER_API_SECRET = os.environ.get('TWITTER_API_SECRET')
    TWITTER_ACCESS_TOKEN = os.environ.get('TWITTER_ACCESS_TOKEN')
    TWITTER_ACCESS_TOKEN_SECRET = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')
    BASE_URL = os.getenv('BASE_URL', 'http://sourcetrustmebro.ai')
    
    # xAI API Key
    XAI_API_KEY = os.environ.get('XAI_API_KEY')
    # Grok API Key
    GROK_API_KEY = os.environ.get('GROK_API_KEY')
    
    LEONARDO_KEY = os.environ.get('LEONARDO_KEY')
    
    DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
    DISCORD_CHANNEL_ID = os.environ.get('DISCORD_CHANNEL_ID')
    MIDJOURNEY_SERVER_ID = os.environ.get('MIDJOURNEY_SERVER_ID')
    
    REPLICATE_API_TOKEN = os.environ.get('REPLICATE_API_TOKEN')


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(Config.basedir, 'app.db')


class ProductionConfig(Config):
    DEBUG = False
    # PostgreSQL database URI format: postgresql://username:password@hostname:port/database_name
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:0218441816a@localhost:5433/korg_news_new'
    
    # Set to True in production for better security
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True