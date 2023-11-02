from flask import Flask, request, render_template, url_for, flash, redirect

from models import User, Songs, Playlist, Album, lyrics
from app import app

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username = username).first()
    if not user:
        flash("User doesnot exist. Please register and try again")
        return redirect(url_for('login'))
    if not user.check_password(password):
        flash("Incorrect Password")
        return redirect(url_for('login'))
    return redirect(url_for('index'))
    
@app.route('/register')
def register():
    return render_template('register.html')

# @app.route('/register', methods=['POST'])
# def register_post():
#     username 