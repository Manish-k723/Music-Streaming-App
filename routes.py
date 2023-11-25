import os
from functools import wraps
from flask import Flask, request, render_template, url_for, flash, redirect, session
from sqlalchemy import func

from models import db, User, Songs, Playlist, Album
from app import app

def auth_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if "user_id" not in session:
            flash("Login required.", 'danger')
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return inner

@app.route('/')
def index():
    try:
        user = User.query.get(session["user_id"])
        if user:
            return redirect(url_for("home"))
    except:
        return redirect(url_for("login"))

@app.route('/admin', methods=['GET','POST'])
def admin():
    if request.method == "GET":
        return render_template("adminLogin.html")
    username = request.form.get('username')
    password = request.form.get('password')
    if username =="" or password =="":
        flash("Username or Password cannot be empty.", "danger")
        return redirect(url_for('admin'))
    user = User.query.filter_by(username = username).first()
    if not user.is_admin:
        flash("You are not authorized to view this page, please login to continue", "danger")
        return redirect(url_for('login'))
    if not user:
        flash("User doesnot exist. Please register and try again.", "danger")
        return redirect(url_for('admin'))
    if not user.check_password(password):
        flash("Incorrect Password", "danger")
        return redirect(url_for('admin'))
    session["user_id"] = user.id  
    return redirect(url_for("adminHome"))

@app.route('/login', methods=["GET",'POST'])
def login():
    if request.method == "GET":
        return render_template('login.html')
    username = request.form.get('username')
    password = request.form.get('password')
    if username =="" or password =="":
        flash("Username or Password cannot be empty.", "danger")
        return redirect(url_for('login'))
    user = User.query.filter_by(username = username).first()
    if not user:
        flash("User doesnot exist. Please register and try again.", "danger")
        return redirect(url_for('login'))
    if not user.check_password(password):
        flash("Incorrect Password", "danger")
        return redirect(url_for('login'))
    session["user_id"] = user.id
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for("login"))

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == "GET":
        return render_template('register.html')
    username =request.form.get("username")
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    print(username, name, email, password)
    if username =="" or password =="":
        flash("Username or Password cannot be empty.", "danger")
        return redirect(url_for('register'))
    if len(password)<7:
        flash("Length of password cannot be smaller than 6 characters.", "danger")
        return redirect(url_for('register'))
    if User.query.filter_by(username = username).first():
        flash("This username is already in use. Please choose another", "danger")
        return redirect(url_for('register'))
    user = User(username=username, name = name, email=email, password=password)
    db.session.add(user)
    db.session.commit()
    flash("User added Succesfully", "success")
    return redirect(url_for("login"))

@app.route('/home')
@auth_required
def home():
    user = User.query.get(session["user_id"])
    if user.is_admin:
        flash("You are an admin, continue as admin", "info")
        return redirect(url_for('admin'))
    else:
        songs = Songs.query.order_by(Songs.rating.desc()).all()
        return render_template('home.html', songs = songs, user = User.query.get(session["user_id"]))
    
@app.route('/adminHome')
@auth_required
def adminHome():
    total_songs =  Songs.query.count()
    total_albums =  Album.query.count()
    normal_user_count = User.query.filter_by(role = 'User').count()
    creator_count = User.query.filter_by(role = 'creator').count()
    unique_genres = db.session.query(Songs.genre).distinct().all()
    unique_genres_list = [genre[0] for genre in unique_genres]
    genreCount = len(unique_genres_list)
    return render_template("admin.html", total_songs = total_songs, normal_user_count = normal_user_count, creator_count = creator_count, genreCount= genreCount, total_albums = total_albums, user = User.query.get(session["user_id"])) 

@app.route('/profile', methods=["GET","POST"])
@auth_required
def profile():
    if request.method == "GET":
        return render_template("profile.html", user = User.query.get(session["user_id"]))
    username =request.form.get("username")
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    cpassword = request.form.get("cpassword")
    if username =="" or password =="" or cpassword=="":
        flash("Username or Password cannot be empty.", "danger")
        return redirect(url_for('profile'))
    if not check_password(cpassword):
        flash("Incorrect Password, Try again.", "danger")
        return redirect(url_for('profile'))
    if len(password)<7:
        flash("Password Strength is low", "danger")
        return redirect(url_for('profile'))
    if user.query.filter_by(username =username).first() and username !=user.username:
        flash("User with same username already exist, try with other one", "danger")
    user.username, user.name, user.email, user.password = username, name, email, password
    db.session.commit()
    flash("Profile Update successfully", "success")
    return redirect(url_for('profile'))
    
@app.route('/registerAsCreator', methods=["POST", "GET"])
@auth_required
def registerCreator():
    if request.method == "GET":
        return render_template("registerCreator.html")
    username =request.form.get("username")
    password = request.form.get("password")
    if username=="" or password=="":
        flash("Kindly fill all the details", "danger")
        return redirect(url_for('registerCreator'))
    user = User.query.filter_by(username = username).first()
    if not user:
        flash("User doesnot exist. Please register and try again.", "danger")
        return redirect(url_for('registerCreator'))
    if not user.check_password(password):
        flash("Incorrect Password", "danger")
        return redirect(url_for('registerCreator'))
    user.role = "creator"
    db.session.commit()
    flash("Registered as Creator", "success")
    return redirect(url_for('creatorAccount'))

@app.route('/creatorAccount', methods=["POST", "GET"])
@auth_required
def creatorAccount():
    user = User.query.get(session["user_id"])
    current_creator = user.id
    if request.method == "GET":
        total_songs = db.session.query(func.count(Songs.id)).filter(Songs.CreatorId == current_creator).scalar()
        average_rating = db.session.query(func.avg(Songs.rating)).filter(Songs.CreatorId == current_creator).scalar()
        total_albums = db.session.query(func.count(Album.id)).filter(Album.CreatorId == current_creator).scalar()
        albums = Album.query.filter_by(CreatorId=current_creator).all()
        return render_template("creatorAccount.html", total_songs= total_songs, average_rating= average_rating, total_albums= total_albums, creator= user.username, albums=albums, user = user, need = True)
    albumTitle = request.form.get('albumTitle')
    artistName = request.form.get('artistName')
    album = Album(name=albumTitle, artist = artistName, CreatorId = current_creator) # genre=albumGenre
    db.session.add(album)
    db.session.commit()
    flash("Album added Succesfully", "success")
    return redirect(url_for("creatorAccount"))
      
@app.route("/creatorAccount/<int:album_id>/update", methods = ["POST","GET"])
@auth_required
def updateAlbum(album_id):
    user = User.query.get(session["user_id"])
    album = db.session.query(Album).filter_by(id = album_id).one()
    if request.method == "GET":
        return render_template('updateAlbum.html', user = user, need = True, albumName = album.name, artistName = album.artist)
    elif request.method=="POST":
        albumTitle, artistName = request.form.get('albumTitle'), request.form.get('artistName')
        album.name, album.artist = albumTitle, artistName
        db.session.commit()
        return redirect(url_for("creatorAccount"))

@app.route("/creatorAccount/<int:album_id>/delete")
@auth_required
def deleteAlbum(album_id):
    songs_in_album = db.session.query(Songs).filter_by(album_id=album_id).first()
    if songs_in_album:
        flash("Cannot delete album. Remove all songs from the album first.", "danger")
    else:
        remove_album = db.session.query(Album).filter_by(id=album_id).first()

        if remove_album:
            db.session.delete(remove_album)
            db.session.commit()
            flash("Album deleted successfully", "success")
        else:
            flash("Album not found", "danger")

    return redirect(url_for("creatorAccount"))

@app.route("/creatorAccount/<int:album_id>/addSongs", methods = ["GET", "POST"])
@auth_required
def addSongs(album_id):
    user = User.query.get(session["user_id"])
    current_creator = user.id
    album = db.session.query(Album).filter_by(id = album_id).one()
    if request.method == "GET":
        total_songs = db.session.query(func.count(Songs.id)).filter(Songs.CreatorId == current_creator).scalar()
        average_rating = db.session.query(func.avg(Songs.rating)).filter(Songs.CreatorId == current_creator).scalar()
        total_albums = db.session.query(func.count(Album.id)).filter(Album.CreatorId == current_creator).scalar()
        songs = Songs.query.filter_by(album_id=album_id).all()
        return render_template("addSongs.html", total_songs= total_songs, average_rating= average_rating, total_albums= total_albums, creator= user.username, songs=songs, user = user, need = True, album_id = album_id)
    SongTitle = request.form.get('SongTitle')
    SingerName = request.form.get('SingerName')
    Genre = request.form.get('Genre')
    lyrics = request.form.get('lyrics')
    file = request.files['mp3File']
    if file:
      filename = file.filename
      file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    new_song = Songs(name = SongTitle, artist = SingerName, lyrics = lyrics, genre = Genre, filename = filename, album_id = album_id, CreatorId =  current_creator)
    db.session.add(new_song)
    db.session.commit()
    flash("Song added Succesfully", "success")
    return redirect(url_for("addSongs", album_id=album_id))

@app.route("/creatorAccount/<int:album_id>/addSongs/<int:song_id>/update", methods= ["GET", "POST"])
@auth_required
def updateSong(album_id, song_id):
    user = User.query.get(session["user_id"])
    song = db.session.query(Songs).filter_by(id = song_id).one()
    if request.method == "GET":
        return render_template("updateSong.html", user = user, need = True, SongTitle = song.name, singerName = song.artist, songGenre = song.genre, lyrics = song.lyrics)
    SongTitle, singerName, songGenre, lyrics = request.form.get('SongTitle'), request.form.get('singerName'), request.form.get('genre'), request.form.get('lyrics')
    song.name, song.artist, song.genre, song.lyrics = SongTitle, singerName, songGenre, lyrics
    db.session.commit()
    return redirect(url_for("addSongs", album_id = album_id))

@app.route("/creatorAccount/<int:album_id>/addSongs/<int:song_id>/delete")
@auth_required
def deleteSong(album_id, song_id):
    remove_song = db.session.query(Songs).filter_by(id=song_id).first()
    filename = remove_song.filename
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    db.session.delete(remove_song)
    flash("Song deleted Successfully", "success")
    db.session.commit()
    return redirect(url_for("addSongs", album_id = album_id))

@app.route('/adminHome/manageCreators')
@auth_required
def manageCreators():
    creators = User.query.filter_by(role="creator").all()
    creators_data = (
        db.session.query(
            User.id,
            User.name,
            User.username,
            User.status,
            db.func.count(db.func.distinct(Songs.id)).label('totalSongs'),
            db.func.count(db.func.distinct(Album.id)).label('totalAlbums')
        ).filter(User.role == 'creator').outerjoin(Songs, User.id == Songs.CreatorId).outerjoin(Album, User.id == Album.CreatorId).group_by(User.id, User.name, User.username).all()
    )
    return render_template("manageCreator.html", user = User.query.get(session["user_id"]), creators = creators_data,  need = True)

@app.route("/adminHome/manageCreators/<int:creatorID>/<string:newStatus>")
@auth_required
def updateStatus(creatorID, newStatus):
    creator = db.session.query(User).filter_by(id = creatorID).one()
    creator.status = newStatus
    db.session.commit()
    return redirect(url_for('manageCreators'))

@app.route('/adminHome/manageSongs')
@auth_required
def manageSongs():
    songs = db.session.query(Songs).all()
    return render_template("manageSongs.html", songs = songs, user = User.query.get(session["user_id"]), need = True)

@app.route('/adminHome/manageSongs/<string:action>/<int:song_id>')
@auth_required
def adminManageSongs(song_id, action):
    song = db.session.query(Songs).filter_by(id = song_id).one()
    if action == "lyrics":
        print(song.lyrics)
        return render_template("lyrics.html", song=song)
    elif action == "flag":
        filename = song.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        db.session.delete(song)
        db.session.commit()
        flash("Song removed", "success")
    return redirect(url_for('manageSongs'))

@app.route('/playSong/<int:song_id>')
@auth_required
def playSong(song_id):
    song = db.session.query(Songs).filter_by(id = song_id).one()
    filename = song.filename
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return render_template("playSong.html", song = song, user = User.query.get(session['user_id']), path = file_path)

@app.route('/playlist')
@auth_required
def playlist():
    return "Welcome to my Music Application"
