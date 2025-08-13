from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_socketio import SocketIO, join_room, emit
import requests
import re
import uuid

app = Flask(__name__)
app.secret_key = 'supersecretkey'
socketio = SocketIO(app)

# USERS
users = {'testuser': 'password123'}

# PLAYLISTS DATA (YouTube embed/watch/short URLs are fine)
playlists_data = [
    {"id": "1", "title": "Chill Vibes", "mood": "chill", "platform": "youtube", "url": "https://www.youtube.com/watch?v=5qap5aO4i9A"},
    {"id": "2", "title": "Workout Music", "mood": "energized", "platform": "youtube", "url": "https://www.youtube.com/watch?v=XI_gjW3r5dA"},
    {"id": "3", "title": "Lofi Focus Beats", "mood": "focus", "platform": "youtube", "url": "https://www.youtube.com/watch?v=jfKfPfyJRdk"},
    {"id": "4", "title": "Upbeat Hits", "mood": "upbeat", "platform": "youtube", "url": "https://www.youtube.com/watch?v=2Vv-BfVoq4g"},
    {"id": "5", "title": "Lo-Fi Dreams", "mood": "lofi", "platform": "youtube", "url": "https://www.youtube.com/watch?v=hHW1oY26kxQ"},
    {"id": "6", "title": "Stress Relief", "mood": "stressed", "platform": "youtube", "url": "https://www.youtube.com/watch?v=1ZYbU82GVz4"},
    {"id": "7", "title": "Nature Sounds", "mood": "nature", "platform": "youtube", "url": "https://www.youtube.com/watch?v=odrJZ9QccuQ"},
    {"id": "8", "title": "Smooth Jazz", "mood": "jazz", "platform": "youtube", "url": "https://www.youtube.com/watch?v=DXSnwq4lmu8"},
    {"id": "9", "title": "Classical Mornings", "mood": "classical", "platform": "youtube", "url": "https://www.youtube.com/watch?v=MJpUAWnbhPQ"},
    {"id": "10", "title": "Ambient Waves", "mood": "ambient", "platform": "youtube", "url": "https://www.youtube.com/watch?v=2OEL4P1Rz04"}
]

rooms = {}  # {room_id: {"name": str, "users": []}}

# --- Helpers -----------------------------------------------------------------
YOUTUBE_ID_RE = re.compile(
    r"""(?ix)
    (?:v=|\/)([0-9A-Za-z_-]{11})              # watch?v=ID or /ID
    |youtu\.be\/([0-9A-Za-z_-]{11})           # youtu.be/ID
    |embed\/([0-9A-Za-z_-]{11})               # /embed/ID
    """,
)

def extract_youtube_id(url: str) -> str | None:
    if not url:
        return None
    m = YOUTUBE_ID_RE.search(url)
    if not m:
        return None
    # find the first group that matched
    for g in m.groups():
        if g:
            return g
    return None

# WEATHER FUNCTION
def get_weather_by_coords(lat, lon):
    api_key = "213472c9a0bda2052a29f3cf29d1af3d"
    url = f"http://api.weatherstack.com/current?access_key={api_key}&query={lat},{lon}"
    try:
        response = requests.get(url, timeout=10)
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

# ROUTES
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

@app.route('/viberoom/<playlist_id>')
def viberoom(playlist_id):
    playlist = next((p for p in playlists_data if p['id'] == playlist_id), None)
    if not playlist:
        flash("❌ Playlist not found.")
        return redirect(url_for('playlists'))

    video_id = extract_youtube_id(playlist.get('url', ''))
    if not video_id:
        flash("❌ Could not resolve video for this playlist.")
        return redirect(url_for('playlists'))

    # Suggestions queue: same mood, exclude current
    queue = []
    for p in playlists_data:
        if p['mood'] == playlist['mood'] and p['id'] != playlist_id:
            vid = extract_youtube_id(p.get('url', ''))
            if vid:
                queue.append({"title": p['title'], "id": vid})

    return render_template('viberoom.html', playlist=playlist, video_id=video_id, queue=queue)

@app.route('/weather', methods=['POST'])
def weather_by_location():
    data = request.get_json()
    lat = data.get('lat')
    lon = data.get('lon')
    result = get_weather_by_coords(lat, lon)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)

# ROOMS
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

# SOCKET.IO EVENTS
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



