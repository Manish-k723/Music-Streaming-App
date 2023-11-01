from flask_sqlalchemy import SQLAlchemy
from app import app

db = SQLAlchemy(app)
# db.init_app(app)

class User(db.Model):
    __tablename__ = 'User'
    user_id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(32), unique = True, nullable=False)
    password = db.Column(db.String(120), nullable = False)
    name = db.Column(db.String(32), nullable=True)
    user_type = db.Column(db.String(26), nullable = False, default='General User')

class Songs(db.Model):
    __tablename__ = 'Songs'
    song_id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(120), nullable=False)
    singer = db.Column(db.String(32))
    # views = db.Column(db.Integer)
    rel_date = db.Column(db.Date, nullable=False)

class Category(db.Model):
    __tablename__='Category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)

    playlist = db.Relationship('Songs', backref='Playlist', lazy=True)

class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('song_id'), nullable=False)




