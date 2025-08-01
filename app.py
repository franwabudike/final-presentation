# app.py
# This is the main Python file for the VibeRoom Flask web application.
# It handles routing and serves the HTML pages.

# Import the necessary Flask components.
from flask import Flask, render_template

# Create a Flask web application instance.
app = Flask(__name__)

# Define the route for the home page.
# The '@app.route' decorator maps the URL '/' to the 'index' function.
@app.route('/')
def index():
    # Render the 'index.html' template.
    return render_template('index.html')

# Define the route for the about page.
@app.route('/about')
def about():
    # Render the 'about.html' template.
    return render_template('about.html')

# Define the route for the playlists page.
@app.route('/playlists')
def playlists():
    # Render the 'playlists.html' template.
    return render_template('playlists.html')

# Define the route for the contact page.
@app.route('/contact')
def contact():
    # Render the 'contact.html' template.
    return render_template('contact.html')