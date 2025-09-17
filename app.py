from datetime import datetime
from flask import Flask, render_template, flash, redirect, url_for, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField    # EmailField, PasswordField
from wtforms.validators import DataRequired, Length


# Initializing the app
app = Flask(__name__)
# App Configurations
app.config['SECRET_KEY'] = 'pass'   # Secret Key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db' # Database

# Initializing the DB
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# DB Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    fav_color = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.now)

    # A way to add a constraint at the db level would need - 
        # from sqlalchemy import CheckConstraint
    """__table_args__ = (
        CheckConstraint("length(name) <= 200", name="check_name_length"),
    )
    """

    def __repr__(self):
        return '<Name %r>' % self.name


# Add User Form
class UserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=200)])
    email = EmailField('Email', validators=[DataRequired(), Length(max=120)])
    # password = PasswordField('Password', validators=[Length(min=6, max=16), DataRequired()]) # 6 - 12 digit pass
    fav_color = StringField('Favorite Color', validators=[Length(max=120)])
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
                         email=form.email.data,
                         fav_color=form.fav_color.data)
            db.session.add(user)
            db.session.commit()
            flash("User Added Successfully!")
            return redirect(url_for("add_user"))
        
        else:
            flash("Already Registered!")
            return redirect(url_for("add_user"))

    
    return render_template("add.html", form=form, our_users=our_users)


# Update user route
@app.route("/update/<int:id>", methods=["GET", "POST"])
def update(id):
    form = UserForm()
    user_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        # Updating from values from the template
        user_to_update.name = request.form["name"]
        user_to_update.email = request.form["email"]
        user_to_update.fav_color = request.form["fav_color"]
        try:
            db.session.commit()
            flash("User Updated Successfully!!!")
            return redirect(url_for("add_user"))
        except:
            flash("User Update Failed!!! Try Again...")
            return redirect(url_for("add_user"))
    else:
        return render_template("update.html", 
                               form=form, 
                               id=id,
                               user_to_update=user_to_update)
    
# Removing a user from db
@app.route("/delete/<int:id>")
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User Deleted Successfully!!!")
        return redirect(url_for("add_user"))
    except:
        flash("Failed to delete user! Try again...")
        return redirect(url_for("add_user"))
