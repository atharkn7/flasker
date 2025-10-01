from datetime import datetime
from flask import Flask, render_template, flash, redirect, url_for, request
from flask_ckeditor import CKEditor
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from webforms import UserForm, PostForm, NamerForm, LoginForm, SearchForm
from werkzeug.security import generate_password_hash, check_password_hash

# Imports for saving file to folder and filename to db
from werkzeug.utils import secure_filename  # Securing against injection attacks
import uuid as uuid # Creates unique user id
import os   # to save the file


""" CONFIG """
# Initializing the app
app = Flask(__name__)
# App Configurations
app.config['SECRET_KEY'] = 'pass'   # Secret Key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db' # Database

# Rich Text Editor
ckeditor = CKEditor(app)

# Image upload folder
UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Initializing the DB
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Flask Logic Configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Loading users from Users model
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


""" MODELS """
# Users Model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    fav_color = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.now)
    password_hash = db.Column(db.String(128), nullable=False)
    # Users can have multiple posts (One to Many)
    posts = db.relationship('Posts', backref='poster')
    about_author = db.Column(db.Text(500), nullable=True)
    profile_pic = db.Column(db.String(), nullable=True)

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
    # author = db.Column(db.String(255), nullable=False)    # Removed
    slug = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.now)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))


""" ROUTES """
# Main page
@app.route("/")
def index():
    title = "Flasker"
    toppings = ['paneer', 'chicken', 'oregano', 'garlic']
    return render_template("home.html", 
                           title = title, 
                           toppings = toppings)


""" CONTEXT PROCESSOR """
@app.context_processor
def base():
    # Global variable for all templates
    form = SearchForm()
    return dict(form=form)


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
# Admin User
@app.route("/admin")
def admin():
    # Logic to say user ID 1 is admin ()
        # Not the best way to do this but a hacky way
    if current_user.id == 1:
        return render_template("admin.html")
    else:
        flash("You are not authorized to access this page...")
        return redirect(url_for("dashboard"))


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
                         username=form.username.data,
                         fav_color=form.fav_color.data,
                         about_author=form.about_author.data,
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
@login_required
def update(id):
    form = UserForm()
    user_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        # Updating from values from the template
        user_to_update.name = request.form["name"]
        user_to_update.email = request.form["email"]
        user_to_update.username = request.form["username"]
        user_to_update.fav_color = request.form["fav_color"]
        user_to_update.about_author = request.form["about_author"]
        try:
            db.session.commit()
            flash("User Updated Successfully!!!")
            return redirect(url_for("dashboard"))
        except:
            flash("User Update Failed!!! Try Again...")
            return redirect(url_for("dashboard"))
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


""" LOGIN MANAGEMENT """
# Login Route
@app.route("/login", methods=["GET", "POST"])
def login():
    form=LoginForm()
    # Validating form submission
    if form.validate_on_submit():
        # Querying db
        user = Users.query.filter_by(username=form.username.data).first()
        # Validating username
        if user:
            # Validating password
            if check_password_hash(user.password_hash, form.password.data):
                
                # Logging in USER
                login_user(user)
                flash("Logged in successfully!")
                return redirect(url_for("dashboard"))
            else:
                # redirect not needed for errors as user is staying on the same page
                flash("Incorrect password! Try again...")
        
        # Logic for no username found 
        else: 
            flash("Username not found! Try again...")

    # GET workflow
    return render_template("login.html", form=form)

# Dashboard/login page
@app.route("/dashboard", methods=["GET", "POST"])
@login_required 
def dashboard():
    # Don't need to send model to template current_user() has it 
    form = UserForm()
    user_to_update = Users.query.get_or_404(current_user.id)

    # POST Workflow
    if request.method == "POST":
        # Updating values 
        user_to_update.username = form.username.data
        user_to_update.email = form.email.data
        user_to_update.name = form.name.data
        user_to_update.fav_color = form.fav_color.data
        user_to_update.about_author = form.about_author.data
        
        if request.files["profile_pic"]:     # Checking for NULL profile pic
            # Saving User uploaded Profile pic
            user_to_update.profile_pic = request.files["profile_pic"]
            # Can use (request.files["profile_pic"]) form.profile_pic.data as well 
            
            # Grab Image Name securely
            pic_filename = secure_filename(user_to_update.profile_pic.filename)
            # Set UUID
            pic_name = str(uuid.uuid1()) + "_" + pic_filename
            # Saving image
            saver = request.files['profile_pic']
            
            # Change it to a string to save to db
            user_to_update.profile_pic = pic_name

        try:
            # DB commit
            saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
            db.session.commit()
            flash("Updated Successfully!")
            return redirect(url_for("dashboard"))
        except Exception as e:
            flash(f"Update failed! Try again... | Error: {e}")
            return redirect(url_for("dashboard"))
            
    # GET workflow
    # form.fav_color.data = user_to_update.fav_color

    return render_template("dashboard.html", form=form, user_to_update=user_to_update)

# Logout route
@app.route("/logout")
@login_required
def logout():
    logout_user()   # Logs out current user
    flash("Logged out successfully!")
    return redirect(url_for("login"))


""" TEST/TRY PAGES """
# Test Password Page
@app.route("/test_pw", methods=["GET", "POST"])
def test_pw():
    form = LoginForm()
    username = None 
    password = None
    user_to_check = None
    passed = None

    # Will validate only if data entered and submitted
    if form.validate_on_submit():
        # Assigning values
        username = form.username.data
        password = form.password.data

        """ Another form of logic where form submission is checked through a value being NULL
        # form.email.data = ''
        # form.password.data = ''
        """
        
        # Querying db to check if email exists
        user_to_check = Users.query.filter_by(username=username).first()

        if user_to_check:
            
            # Checking if entered pass matches existing pass
            passed = check_password_hash(user_to_check.password_hash, password)
            
            # Message and render
            flash("User Found!")
            return render_template("test_pw.html", form=form, username=username, user_to_check=user_to_check, passed=passed)
        else:
            flash("No user found!")
            return redirect(url_for("test_pw"))
    
    return render_template("test_pw.html", form=form, username=username)

# JSON Page
@app.route("/test_date")
def test_date():
    return {"Date: ": datetime.now()}


""" BLOG CRUD OPERATIONS """
# CREATE Blog Post
@app.route("/add-post", methods=["GET", "POST"])
@login_required
def add_post():
    form = PostForm()
    poster = current_user.id    # To get who is posting

    if form.validate_on_submit():
        # Creating a new post
        post = Posts(title=form.title.data,  
                     slug=form.slug.data, 
                     content=form.content.data, 
                     poster_id=poster)
        
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
@login_required
def edit_posts(id):
    # Getting form and model
    post_to_update = Posts.query.get_or_404(id)
    form = PostForm()
    # form = PostForm(obj=post_to_update)   # Pre-fills form with existing values

    if post_to_update.poster_id == current_user.id:
        # POST workflow
        if form.validate_on_submit():
            # Updating Post (can be automated with populate_obj line below)
            post_to_update.title = form.title.data
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
        form.slug.data = post_to_update.slug
        form.content.data = post_to_update.content

        return render_template("edit_post.html", form=form, id=id)
    
    else:
        flash("You are not authorized to edit this post! ")
        return redirect(url_for("posts"))

# DELETE - Blog Post 
""" Changed to POST as GET should only be used in read-only ops"""
@app.route("/posts/delete/<int:id>", methods=["POST"])
@login_required
def delete_posts(id):
    post_to_delete = Posts.query.get_or_404(id)
    poster_id = current_user.id

    # Checking if current user is the same as poster
    if poster_id == post_to_delete.poster_id:    
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
    else:
        flash("You are not authorized to delete this post!")
        return redirect(url_for("posts"))
    

""" BLOG ACTIONS """
# Search blog posts
@app.route("/search", methods=["GET", "POST"])
def search():
    form = SearchForm()
    post = Posts.query  # Getting all posts

    if form.validate_on_submit():
        
        searched = form.searched.data
        # Searching content field in DB
        posts = post.filter(Posts.content.like('%'+searched+'%'))
        posts = posts.order_by(Posts.title).all()

        return render_template("search.html", form=form, posts=posts, searched=searched)

    return render_template("search.html", form=form, searched=searched)


""" Best practice in production:
    1. Wrap all commits in 
        1a. try/except 
        1b. SQLAlchemyError).
    2. Rollback on failure.
    3. Log the exact error for debugging, but show a clean flash to the user
        3a. DELETE is most likely to fail, maybe a post is referenced by another table
"""