from flask import Flask, request, render_template, url_for, flash

from models import User, Songs, Category, Playlist
from app import app

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')