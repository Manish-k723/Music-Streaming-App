from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import app

db = SQLAlchemy(app)
# db.init_app(app)

class User(UserMixin, db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(32), unique = True, nullable=False)
    passhash = db.Column(db.String(512), nullable = False)
    name = db.Column(db.String(32), nullable=True)
    email = db.Column(db.String(120), unique =True, nullable = False)
    role = db.Column(db.String(26), nullable = False, default='User')
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    status = db.Column(db.String(16), nullable=False, default="white")

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.passhash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.passhash, password)


class Songs(db.Model):
    __tablename__ = 'Songs'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(120), nullable=False)
    artist = db.Column(db.String(32))
    lyrics = db.Column(db.String(1024), nullable = False)
    rating = db.Column(db.Integer, nullable = False, default=0)
    genre = db.Column(db.String(26), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    imagepath = db.Column(db.String(255), nullable=False)
    album_id = db.Column(db.Integer, db.ForeignKey('Album.id'), nullable = False)
    CreatorId = db.Column(db.Integer, db.ForeignKey('User.id'), nullable = False)


class Album(db.Model):
    __tablename__='Album'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    artist = db.Column(db.String, nullable = False)
    CreatorId = db.Column(db.Integer, db.ForeignKey('User.id'), nullable = False)

playlist_songs = db.Table('playlist_songs',
                db.Column('playlist_id', db.Integer, db.ForeignKey('Playlist.id')),
                db.Column('song_id', db.Integer, db.ForeignKey('Songs.id')))

class Playlist(db.Model):
    __tablename__='Playlist'
    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    playlist_name = db.Column(db.String(255), nullable=False)
    songs = db.Relationship('Songs', secondary="playlist_songs", backref='Playlist') # lazy = True

with app.app_context():
    db.create_all()
    admin = User.query.filter_by(is_admin=True).first()
    if not admin:
        admin = User(username="admin", name = "admin", password="admin133", email="admin@musicly.in", role="admin", is_admin=True)
        db.session.add(admin)
        db.session.commit()


