from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField    # EmailField, PasswordField
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


# User login Form
class UserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    # email = EmailField('Email', validators=[DataRequired()])
    # password = PasswordField('Password', validators=[Length(min=6, max=16), DataRequired()]) # 6 - 12 digit pass
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

# User Info Page
@app.route("/user", methods=["GET", "POST"])
def user():
    form = UserForm()
    name = None # Assigning None to show form when value none and when name entered by user then it would show the greet message

    # Validating form
    if form.validate_on_submit():
        name = form.name.data
        # email = form.email.data
        # password = form.password.data
        flash("Form Submitted Successfully!")
        return render_template("user.html", form=form, name=name)
    
    else:
        return render_template("user.html", form=form, name=name)