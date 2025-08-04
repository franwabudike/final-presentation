from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import requests

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Mock user database
users = {
    'testuser': 'password123'
}

# Example playlist data
playlists_data = [
    {"title": "Chill Vibes", "mood": "chill", "platform": "youtube", "url": "#"},
    {"title": "Workout Music", "mood": "energized", "platform": "youtube", "url": "#"},
    {"title": "Lofi Focus Beats", "mood": "focus", "platform": "youtube", "url": "#"},
]

# Inject user into all templates
@app.context_processor
def inject_user():
    return dict(user=session.get('user'))

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
    error = None
    return render_template('auth.html', error=error)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    if username in users and users[username] == password:
        session['user'] = username
        flash(f'Welcome back, {username}!')
        return redirect(url_for('home'))
    else:
        flash('❌ Invalid login credentials')
        return redirect(url_for('auth'))

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')

    if username in users:
        flash('❌ Username already exists. Try a different one.')
        return redirect(url_for('auth'))

    users[username] = password
    session['user'] = username
    flash('✅ Registration successful. Welcome!')
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('👋 You’ve been logged out.')
    return redirect(url_for('home'))

@app.route('/playlists')
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
