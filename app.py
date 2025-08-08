from flask import Flask, render_template, url_for, flash, redirect, request, jsonify
from reg_form import RegistrationForm
from flask_behind_proxy import FlaskBehindProxy
from flask_sqlalchemy import SQLAlchemy
from db_model import User, db
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import requests


app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///VibeRoom.db' #creating database
app.config['UPLOAD_FOLDER'] = 'static/profile_pics' #photo for profile photo uploads to go
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit for images

# Create folder for uploads if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize extensions
db.init_app(app)
# Create tables
with app.app_context():
    db.create_all()
#create login manager
login_manager = LoginManager()
login_manager.login_view = '/login' #redirects to this page when trying to enter a login required page
login_manager.init_app(app)

#load user
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

"""
# Mock user database
users = {
    'testuser': 'password123'
}
"""

# Example playlist data
playlists_data = [
    {"title": "Chill Vibes", "mood": "chill", "platform": "youtube", "url": "#"},
    {"title": "Workout Music", "mood": "energized", "platform": "youtube", "url": "#"},
    {"title": "Lofi Focus Beats", "mood": "focus", "platform": "youtube", "url": "#"},
]
"""
# Inject user into all templates
@app.context_processor
def inject_user():
    return dict(user=session.get('user'))
"""

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        print(f"[Contact] From: {name} <{email}> | Subject: {subject}\n{message}")
        flash('✅ Your message has been sent! Thank you for reaching out.')
        return redirect(url_for('contact'))

    return render_template('contact.html')

@app.route('/auth', methods=['GET', 'POST'])
def auth():
    form = RegistrationForm()  # Create the form instance
    error = None
    return render_template('auth.html', error=error, form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first() #find user using username

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid Creditials')
            return redirect(url_for('auth'))  # Redirect back to auth page    
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == 'POST' and form.validate_on_submit():

        # Check if username already exists
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'error')
            return redirect(url_for('register'))
        
        # Check if email already exists
        existing_email = User.query.filter_by(email=form.email.data).first()
        if existing_email:
            flash('Email already registered. Please use a different email.', 'error')
            return redirect(url_for('register'))

        # Handle profile picture upload
        picture_file = request.files['picture']
        if picture_file and picture_file.filename != '':
            filename = secure_filename(picture_file.filename)
            picture_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            picture_file.save(picture_path)
        else:
            filename = "default_pfp.jpeg"

        hashed_password = generate_password_hash(form.password.data, method='sha256')

        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
            picture=filename
        )

        try:
            db.session.add(user)
            db.session.commit()
            flash(f'Account created for {form.username.data}!', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            db.session.rollback()
            flash('An error occured while creating your account. Please try again.', 'error')
            return redirect(url_for('register')) #render_template('auth.htm', title='Register', form=form)
    # in case form fails or GET request
    return render_template('auth.html', title='Register', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('👋 You’ve been logged out.')
    return redirect(url_for('home'))

@app.route('/playlists')
@login_required
def playlists():
    mood = request.args.get('mood', 'all')
    platform = request.args.get('platform', 'all')

    filtered = [
        p for p in playlists_data
        if (mood == 'all' or p['mood'] == mood) and (platform == 'all' or p['platform'] == platform)
    ]

    return render_template('playlists.html', playlists=filtered, mood=mood, platform=platform)

@app.route('/weather', methods=['POST'])
def weather_by_location():
    data = request.get_json()
    lat = data.get('lat')
    lon = data.get('lon')

    api_key = "213472c9a0bda2052a29f3cf29d1af3d"  # so this is the api key for weatherstack, frances'
    url = f"http://api.weatherstack.com/current?access_key={api_key}&query={lat},{lon}"

    try:
        response = requests.get(url)
        weather_data = response.json()

        if "current" in weather_data:
            condition = weather_data["current"]["weather_descriptions"][0].lower()
            temperature = weather_data["current"]["temperature"]
            city_name = weather_data["location"]["name"]

            if "rain" in condition or "storm" in condition:
                mood = "chill"
            elif "sun" in condition or "clear" in condition:
                mood = "energized"
            elif "cloud" in condition:
                mood = "focus"
            else:
                mood = "focus"

            return jsonify({
                "location": city_name,
                "temperature": temperature,
                "description": condition,
                "suggested_mood": mood
            })
        else:
            return jsonify({"error": "Weather data not found"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
