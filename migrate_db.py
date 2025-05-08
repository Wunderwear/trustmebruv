import os
import sqlite3
import psycopg2
from datetime import datetime
from app import create_app, db
from app.models import User, Article

def migrate_from_sqlite_to_postgres():
    # Connect to SQLite
    sqlite_conn = sqlite3.connect('app.db')
    sqlite_cursor = sqlite_conn.cursor()

    # Get the PostgreSQL connection string from environment
    postgres_uri = os.environ.get('DATABASE_URL') or 'postgresql://postgres:0218441816a@localhost:5433/korg_news'

    # Extract username, password, host, and dbname from connection URI
    parts = postgres_uri.replace('postgresql://', '').split('@')
    user_pass = parts[0].split(':')
    host_db = parts[1].split('/')

    username = user_pass[0]
    password = user_pass[1]
    host_port = host_db[0].split(':')
    host = host_port[0]
    dbname = host_db[1]

    # Connect to PostgreSQL
    pg_conn = psycopg2.connect(
        dbname=dbname,
        user=username,
        password=password,
        host=host,
        port=port
    )
    pg_cursor = pg_conn.cursor()

    # Migrate users
    print("Migrating users...^")
    sqlite_cursor.execute("SELECT id, username, password FROM user")
    users = sqlite_cursor.fetchall()

    for user in users:
        user_id, username, password = user
        # Check if user already exists
        pg_cursor.execute("SELECT id FROM \"user\" WHERE username = s", (username,))
        if not pg_cursor.fetchone():
            pg_cursor.execute(
                "INSERT INTO \"user\" ^(id, username, password^) VALUES ^(s, s^)",
                (user_id, username, password)
            )
            print(f"User {username} migrated")

    # Migrate articles
    print("Migrating articles...^")
    sqlite_cursor.execute("SELECT id, title, content, image_url, created_at, tweet_id FROM article")
    articles = sqlite_cursor.fetchall()

    for article in articles:
        article_id, title, content, image_url, created_at, tweet_id = article
        # Check if article already exists
        pg_cursor.execute("SELECT id FROM article WHERE id = s", (article_id,))
        if not pg_cursor.fetchone():
            # Convert created_at if it's not None
            if created_at is not None:
                try:
                    created_date = datetime.fromisoformat(created_at)
                except:
                    created_date = datetime.now()
            else:
                created_date = datetime.now()

            pg_cursor.execute(
                "INSERT INTO article ^(id, title, content, image_url, created_at, tweet_id^) VALUES ^(s, s, s^)",
                (article_id, title, content, image_url, created_date, tweet_id)
            )
            print(f"Article '{title[:30]}...' migrated")

    # Commit changes and close connections
    pg_conn.commit()
    sqlite_conn.close()
    pg_conn.close()
    print("Migration completed successfully!")


if __name__ == '__main__':
    # Set up the Flask app context
    app = create_app()
    with app.app_context():
        # Create tables in PostgreSQL
        db.create_all()
        print("PostgreSQL tables created")
        # Migrate data
        migrate_from_sqlite_to_postgres()
