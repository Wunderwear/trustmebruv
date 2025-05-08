from datetime import datetime
from . import db

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tweet_id = db.Column(db.String(50))  # To store the Twitter post ID
    
    def __repr__(self):
        return f'<Article {self.title}>' 