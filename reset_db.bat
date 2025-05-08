@echo off
REM Set environment variables for production
SET FLASK_ENV=production
SET DATABASE_URL=postgresql://postgres:0218441816a@localhost:5433/korg_news_new

echo Resetting database tables with updated schema...
python drop_and_recreate_tables.py

echo Done! Now you can run start_production.bat again. 