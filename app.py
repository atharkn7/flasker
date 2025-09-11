from flask import Flask, render_template, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField    # EmailField, PasswordField
from wtforms.validators import DataRequired     # Length
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


# Initializing the app
app = Flask(__name__)
# App Configurations
app.config['SECRET_KEY'] = 'pass'   # Secret Key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db' # Database

# Initializing the DB
db = SQLAlchemy(app)

# DB Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<Name %r>' % self.name


# Add User Form
class UserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    # password = PasswordField('Password', validators=[Length(min=6, max=16), DataRequired()]) # 6 - 12 digit pass
    submit = SubmitField('Submit')


# User login Form
class NamerForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Main page
@app.route("/")
def index():
    title = "Flasker"
    toppings = ['paneer', 'chicken', 'oregano', 'garlic']
    return render_template("home.html", 
                           title = title, 
                           toppings = toppings)

# Error Pages
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html")

# Name Page
@app.route("/user", methods=["GET", "POST"])
def user():
    form = NamerForm()
    name = None # Assigning None to show form when value none and when name entered by user then it would show the greet message

    # Validating form
    if form.validate_on_submit():
        name = form.name.data
        flash("Form Submitted Successfully!")
        return render_template("user.html", form=form, name=name)
    
    else:
        return render_template("user.html", form=form, name=name)
    
# Add User Page (Shows how to add to DB)
@app.route("/user/add", methods=["GET", "POST"])
def add_user():
    form = UserForm()
    our_users = Users.query.order_by(Users.date_added)

    # Validating form
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first() # Checking if current email exists

        if user is None:    # if no existing users
            user = Users(name=form.name.data, 
                         email=form.email.data)
            db.session.add(user)
            db.session.commit()
            flash("User Added Successfully!")
            return redirect(url_for("add_user"))
        
        else:
            flash("Already Registered!")
            return redirect(url_for("add_user"))

    
    return render_template("add.html", form=form, our_users=our_users)