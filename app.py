from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'a_very_secret_and_long_random_string'

users = {
    'trent': 'password123'
}

@app.context_processor
def inject_user():
    return dict(current_user=session.get('user_info'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/playlists')
def playlists():
    return render_template('playlists.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/about')
def about():
    return render_template('about.html')

# New route for the combined login/register page
@app.route('/auth')
def auth():
    return render_template('auth.html')

# Handles the login form submission
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    if users.get(username) == password:
        session['user_info'] = {'username': username}
        return redirect(url_for('index'))
    return redirect(url_for('auth'))

# Handles the registration form submission
@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    # Check if the username already exists
    if username in users:
        # You might want to show a flash message here
        return 'Username already exists!', 409
    
    # Register the new user
    users[username] = password
    
    # Log the new user in automatically and redirect to the home page
    session['user_info'] = {'username': username}
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user_info', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)