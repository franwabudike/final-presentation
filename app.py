from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'your_secret_key_here' # Needed for sessions

# A simple user dictionary for this example
users = {
    'trent': 'password123'
}

# The navigation bar is now in the layout.
# This context processor makes the 'current_user' available to all templates.
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if users.get(username) == password:
            session['user_info'] = {'username': username}
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_info', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)