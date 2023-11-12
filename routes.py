from functools import wraps
from flask import Flask, request, render_template, url_for, flash, redirect, session

from models import db, User, Songs, Playlist, Album, lyrics
from app import app

def auth_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if "user_id" not in session:
            flash("You need to login first.")
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return inner

@app.route('/')
@auth_required
def index():
    user = User.query.get(session["user_id"])
    if user.is_admin:
        flash("You are an admin, continue as admin")
        return redirect(url_for('admin'))
    else:
        return render_template('index.html', user = User.query.get(session["user_id"]))

@app.route('/profile')
@auth_required
def profile():
    return render_template("profile.html", user = User.query.get(session["user_id"]))

@app.route('/profile', methods=["POST"])
@auth_required
def profile_post():
    username =request.form.get("username")
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    cpassword = request.form.get("cpassword")
    print(username, name, email, password, role, cpassword)
    if username =="" or password =="" or cpassword=="":
        flash("Username or Password cannot be empty.")
        return redirect(url_for('profile'))
    if not check_password(cpassword):
        flash("Incorrect Password, Try again.")
        return redirect(url_for('profile'))
    # if len(password)<7:
    #     flash("Password Strength is low")
    #     return redirect(url_for('profile'))
    if user.query.filter_by(username =username).first() and username !=user.username:
        flash("User with same username already exist, try with newer one")
    user.username, user.name, user.email, user.password = username, name, email, password
    db.session.commit()
    flash("Profile Update successfully")
    return redirect(url_for('profile'))

@app.route('/admin')
def admin():
    return render_template("adminLogin.html")

@app.route('/admin', methods=['POST'])
def admin_post():
    username = request.form.get('username')
    password = request.form.get('password')
    if username =="" or password =="":
        flash("Username or Password cannot be empty.")
        return redirect(url_for('admin'))
    user = User.query.filter_by(username = username).first()
    if not user.is_admin:
        flash("You are not authorized to view this page, please login to continue")
        return redirect(url_for('login'))
    if not user:
        flash("User doesnot exist. Please register and try again.")
        return redirect(url_for('admin'))
    if not user.check_password(password):
        flash("Incorrect Password")
        return redirect(url_for('admin'))
    session["user_id"] = user.id
    return render_template("admin.html")

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    if username =="" or password =="":
        flash("Username or Password cannot be empty.")
        return redirect(url_for('login'))
    user = User.query.filter_by(username = username).first()
    if not user:
        flash("User doesnot exist. Please register and try again.")
        return redirect(url_for('login'))
    if not user.check_password(password):
        flash("Incorrect Password")
        return redirect(url_for('login'))
    session["user_id"] = user.id
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for("login"))

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_post():
    username =request.form.get("username")
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    print(username, name, email, password)
    if username =="" or password =="":
        flash("Username or Password cannot be empty.")
        return redirect(url_for('register'))
    if len(password)<7:
        flash("Length of password cannot be smaller than 6 characters.")
        return redirect(url_for('register'))
    if User.query.filter_by(username = username).first():
        flash("This username is already in use. Please choose another")
        return redirect(url_for('register'))
    user = User(username=username, name = name, email=email, password=password)
    db.session.add(user)
    db.session.commit()
    flash("User added Succesfully")
    return redirect(url_for("login"))

@app.route('/registerAsCreator')
def registerCreator():
    return render_template("registerCreator.html")
    

@app.route('/registerAsCreator', methods=["POST"])
def registerCreator_post():
    username =request.form.get("username")
    password = request.form.get("password")
    confirmPassword = request.form.get("confirmPassword")
    if username=="" or password=="" or confirmPassword=="":
        flash("Kindly fill all the details")
        return redirect(url_for('registerCreator'))
    user = User.query.filter_by(username = username).first()
    if password!=confirmPassword:
        flash("Password should be same")
        return redirect(url_for('registerCreator'))
    if not user:
        flash("User doesnot exist. Please register and try again.")
        return redirect(url_for('registerCreator'))
    if not user.check_password(password):
        flash("Incorrect Password")
        return redirect(url_for('registerCreator'))
    user.role = "creator"
    db.session.commit()
    flash("Registered as Creator")
    return redirect(url_for('index'))


@app.route('/playlist')
@auth_required
def playlist():
    return "Welcome to my Music Application"

@app.route('/album/<int:creator_id>/warn')
@auth_required
def warn_creator(creator_id):
    return "Edit"

@app.route('/album/<int:creator_id>/remove')
@auth_required
def remove_creator(creator_id):
    return "Delete"
