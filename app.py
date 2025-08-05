from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_socketio import SocketIO, join_room, emit
import requests
import uuid

app = Flask(__name__)
app.secret_key = 'supersecretkey'
socketio = SocketIO(app)

# -------------------------------
# In-Memory User + Playlist + Room Storage (for demo purposes)
# -------------------------------
users = {'testuser': 'password123'}
playlists_data = [
    {"title": "Chill Vibes", "mood": "chill", "platform": "youtube", "url": "#"},
    {"title": "Workout Music", "mood": "energized", "platform": "youtube", "url": "#"},
    {"title": "Lofi Focus Beats", "mood": "focus", "platform": "youtube", "url": "#"},
]
rooms = {}  # {room_id: {"name": str, "users": []}}

def get_weather_by_coords(lat, lon):
    api_key = "213472c9a0bda2052a29f3cf29d1af3d"
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
            return {
                "location": city_name,
                "temperature": temperature,
                "description": condition,
                "suggested_mood": mood
            }
        else:
            return {"error": "Weather data not found"}
    except Exception as e:
        return {"error": str(e)}

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
    return render_template('auth.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    if username in users and users[username] == password:
        session['user'] = username
        flash(f'✅ Welcome back, {username}!')
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
    result = get_weather_by_coords(lat, lon)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)

@app.route('/rooms')
def rooms_page():
    return render_template('rooms.html', rooms=rooms)

@app.route('/create_room', methods=['POST'])
def create_room():
    room_name = request.form.get('room_name')
    username = session.get('user', 'guest')
    room_id = str(uuid.uuid4())[:8]
    rooms[room_id] = {"name": room_name, "users": [username]}
    return redirect(url_for('room_page', room_id=room_id))

@app.route('/join_room/<room_id>')
def room_page(room_id):
    room = rooms.get(room_id)
    if not room:
        flash("❌ Room not found.")
        return redirect(url_for('rooms_page'))
    username = session.get('user', 'guest')
    if username not in room["users"]:
        room["users"].append(username)
    return render_template('room.html', room=room, room_id=room_id)

# -------------------------------
# SocketIO Events
# -------------------------------
@socketio.on('join')
def handle_join(data):
    room = data['room']
    user = session.get('user', 'guest')
    join_room(room)
    emit('user_joined', {'user': user}, room=room)

@socketio.on('new_video')
def handle_new_video(data):
    emit('new_video', data, room=data['room'])

@socketio.on('video_event')
def handle_video_event(data):
    emit('video_event', data, room=data['room'])

@socketio.on('chat_message')
def handle_chat(data):
    emit('chat_message', data, room=data['room'])

if __name__ == '__main__':
    socketio.run(app, debug=True)
