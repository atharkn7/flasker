from flask import Flask, render_template


# Initializing the app
app = Flask(__name__)


# Main page
@app.route("/")
def index():
    return render_template("index.html")