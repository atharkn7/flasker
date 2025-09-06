from flask import Flask, render_template


# Initializing the app
app = Flask(__name__)


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
@app.route("/user")
def user():
    return render_template("user.html")