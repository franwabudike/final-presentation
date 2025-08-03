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
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if users.get(username) == password:
            session['user_info'] = {'username': username}
            return redirect(url_for('index'))
        return redirect(url_for('auth'))  # or return an error message
    # This will show the login page when accessed via GET
    return render_template('login.html')


# Handles the registration form submission
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in users:
            return 'Username already exists!', 409
        users[username] = password
        session['user_info'] = {'username': username}
        return redirect(url_for('index'))
    return render_template('register.html')  # if you have a register.html


@app.route('/logout')
def logout():
    session.pop('user_info', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)