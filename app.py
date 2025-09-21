from datetime import datetime
from flask import Flask, render_template, flash, redirect, url_for, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField, BooleanField, ValidationError
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired, Length, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash


# Initializing the app
app = Flask(__name__)
# App Configurations
app.config['SECRET_KEY'] = 'pass'   # Secret Key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db' # Database

# Initializing the DB
db = SQLAlchemy(app)
migrate = Migrate(app, db)

""" MODELS """
# Users Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    fav_color = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.now)
    password_hash = db.Column(db.String(128), nullable=False)

    # A way to add a constraint at the db level would need - 
        # from sqlalchemy import CheckConstraint
    """__table_args__ = (
        CheckConstraint("length(name) <= 200", name="check_name_length"),
    )
    """

    # Password hashing
    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute!")
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # Repr
    def __repr__(self):
        return '<Name %r>' % self.name

# Post Model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.now)

""" FORMS """
# Add User Form
class UserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=200)])
    email = EmailField('Email', validators=[DataRequired(), Length(max=120)])
    fav_color = StringField('Favorite Color', validators=[Length(max=120)])
    password = PasswordField('Password', validators=[Length(min=6, max=16), DataRequired(), EqualTo('password2', message='Passwords must match!')])
    password2 = PasswordField('Confirm Password', validators=[Length(min=6, max=16), DataRequired()]) 
    submit = SubmitField('Submit')

# User login Form
class TestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Naming Form
class NamerForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Posts Form
class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    author = StringField("Author", validators=[DataRequired()])
    slug = StringField("Slug", validators=[DataRequired()])
    content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    submit = SubmitField("Submit")


""" ROUTES """
# Main page
@app.route("/")
def index():
    title = "Flasker"
    toppings = ['paneer', 'chicken', 'oregano', 'garlic']
    return render_template("home.html", 
                           title = title, 
                           toppings = toppings)


""" ERROR PAGES """
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
    

""" USER MANAGEMENT """
# Add User Page (Shows how to add to DB)
@app.route("/user/add", methods=["GET", "POST"])
def add_user():
    form = UserForm()
    our_users = Users.query.order_by(Users.date_added)

    # Validating form
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first() # Checking if current email exists

        if user is None:    # if no existing users
            # Hashing Pass
            hashed_pw = generate_password_hash(form.password.data)

            # Updating user with values from form
            user = Users(name=form.name.data, 
                         email=form.email.data,
                         fav_color=form.fav_color.data,
                         password_hash=hashed_pw)
            
            # Commiting to DB
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

""" TEST/TRY PAGES """
# Test Password Page
@app.route("/test_pw", methods=["GET", "POST"])
def test_pw():
    form = TestForm()
    email = None 
    password = None
    user_to_check = None
    passed = None

    # Will validate only if data entered and submitted
    if form.validate_on_submit():
        # Assigning values
        email = form.email.data
        password = form.password.data

        """ Another form of logic where form submission is checked through a value being NULL
        # form.email.data = ''
        # form.password.data = ''
        """
        
        # Querying db to check if email exists
        user_to_check = Users.query.filter_by(email=email).first()

        # Checking if entered pass matches existing pass
        passed = check_password_hash(user_to_check.password_hash, password)

        if user_to_check:
            return render_template("test_pw.html", form=form, email=email, user_to_check=user_to_check, passed=passed)
    
    return render_template("test_pw.html", form=form, email=email)

# JSON Page
@app.route("/test_date")
def test_date():
    return {"Date: ": datetime.now()}

""" BLOG CRUD OPERATIONS """
# CREATE Blog Post
@app.route("/add-post", methods=["GET", "POST"])
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        # Creating a new post
        post = Posts(title=form.title.data, 
                     author=form.author.data, 
                     slug=form.slug.data, 
                     content=form.content.data)
        
        # Adding to db
        db.session.add(post)
        db.session.commit()

        # Confirming user added & redirecting
        flash("Blog posted successfully!")
        # Good practice to use url_for() instead of hardcoding
        return redirect(url_for("posts"))   
    
    return render_template("add_post.html", form=form)

# READ - All Blogs
@app.route("/posts")
def posts():
    # Adding form to allow deletion 
        # Ideally this should be a seperate delete form to handle this
    form = PostForm()
    
    # Getting all posts
    posts = Posts.query.order_by(Posts.date_posted.desc()).all()
    return render_template("posts.html", posts=posts, form=form)

# READ - Individual blog
@app.route("/posts/<int:id>")
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template("post.html", post=post)

# UPDATE - Blog Post
@app.route("/posts/edit/<int:id>", methods=["GET", "POST"])
def edit_posts(id):
    # Getting form and model
    post_to_update = Posts.query.get_or_404(id)
    form = PostForm()
    # form = PostForm(obj=post_to_update)   # Pre-fills form with existing values
        
    
    # POST workflow
    if form.validate_on_submit():
        # Updating Post (can be automated with populate_obj line below)
        post_to_update.title = form.title.data
        post_to_update.author = form.author.data
        post_to_update.slug = form.slug.data
        post_to_update.content = form.content.data
        # form.populate_obj(post_to_update)     # Automatically assigns form data to model fields 

        # Updating db
        db.session.commit()

        # Confirming and redirecting
        flash("Blog post edited successfully!")
        return redirect(url_for("posts"))
    
    # Adding values to form (can be automated with pre-fills line)
    form.title.data = post_to_update.title
    form.author.data = post_to_update.author
    form.slug.data = post_to_update.slug
    form.content.data = post_to_update.content

    return render_template("edit_post.html", form=form, id=id)

# DELETE - Blog Post 
""" Changed to POST as GET should only be used in read-only ops"""
@app.route("/posts/delete/<int:id>", methods=["POST"])
def delete_posts(id):
    post_to_delete = Posts.query.get_or_404(id)
    try:
        # Deleting selected user
        db.session.delete(post_to_delete)
        db.session.commit()

        # Confirm & redirect
        flash("Blog post deleted successfully!")
        return redirect(url_for("posts"))
    except:
        flash("Failed post deletion! Try again...")
        # db.session.rollback()     # Clear failed transaction and resets the session
        return redirect(url_for("posts"))
    
"""
Best practice in production:
    1. Wrap all commits in 
        1a. try/except 
        1b. SQLAlchemyError).
    2. Rollback on failure.
    3. Log the exact error for debugging, but show a clean flash to the user
        3a. DELETE is most likely to fail, maybe a post is referenced by another table
"""