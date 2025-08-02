from flask import Flask, render_template

app = Flask(__name__)

# when a user visits the root URL
@app.route('/')
def index():
    return render_template('index.html')

# will be called when a user visits the /playlists URL
@app.route('/playlists')
def playlists():
    return render_template('playlists.html')

# will be called when a user visits the /contact URL
@app.route('/contact')
def contact():
    return render_template('contact.html')

# placeholder for the About page
@app.route('/about')
def about():
    return render_template('about.html')

# a new route for the login page ("/login")
@app.route('/login')
def login():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)