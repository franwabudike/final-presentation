# This is the main Python file for the VibeRoom Flask web application.

from flask import Flask, render_template

app = Flask(__name__)

# the route for the home page.
# '@app.route' decorator maps the URL '/' to the 'index' function.
@app.route('/')
def index():
    # the 'index.html' template.
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

# the route for the playlists page.
@app.route('/playlists')
def playlists():
    return render_template('playlists.html')

# the route for the contact page.
@app.route('/contact')
def contact():
    return render_template('contact.html')