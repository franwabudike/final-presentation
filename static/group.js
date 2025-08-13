const socket = io();
let player;

// Render initial users without duplicates
function renderUserList(users) {
    const ul = document.getElementById("user-list");
    ul.innerHTML = "";
    [...new Set(users)].forEach(user => {
        const li = document.createElement("li");
        li.textContent = user;
        ul.appendChild(li);
    });
}

renderUserList(window.INITIAL_USERS);

socket.emit('join', { room: window.ROOM_ID });

// Update when new user joins
socket.on('user_joined', data => {
    window.INITIAL_USERS.push(data.user);
    renderUserList(window.INITIAL_USERS);
});

function onYouTubeIframeAPIReady() {
    player = new YT.Player('player', {
        height: '270',
        width: '100%',
        videoId: '5qap5aO4i9A',
        events: { onStateChange: onPlayerStateChange }
    });
}

function onPlayerStateChange(event) {
    const time = player.getCurrentTime();
    if (event.data === YT.PlayerState.PLAYING) {
        socket.emit('video_event', { room: window.ROOM_ID, action: 'play', time });
    } else if (event.data === YT.PlayerState.PAUSED) {
        socket.emit('video_event', { room: window.ROOM_ID, action: 'pause', time });
    }
}

socket.on('video_event', data => {
    if (!player) return;
    player.seekTo(data.time, true);
    if (data.action === 'play') player.playVideo();
    else if (data.action === 'pause') player.pauseVideo();
});

document.getElementById('video-form').addEventListener('submit', e => {
    e.preventDefault();
    const url = document.getElementById('video-url').value;
    const videoId = extractYouTubeID(url);
    if (videoId) {
        socket.emit('new_video', { room: window.ROOM_ID, videoId });
        document.getElementById('video-url').value = '';
    }
});

socket.on('new_video', data => {
    if (!player) return;
    player.loadVideoById(data.videoId);
    addToQueue(data.videoId);
});

function addToQueue(videoId) {
    const ul = document.getElementById("queue-list");
    const li = document.createElement("li");
    li.textContent = `https://youtu.be/${videoId}`;
    ul.appendChild(li);
}

function extractYouTubeID(url) {
    const regex = /(?:v=|\/)([0-9A-Za-z_-]{11}).*/;
    const match = url.match(regex);
    return match ? match[1] : null;
}

document.getElementById("chat-form").addEventListener("submit", e => {
    e.preventDefault();
    const input = document.getElementById("chat-input");
    const message = input.value;
    socket.emit('chat_message', { room: window.ROOM_ID, message });
    input.value = '';
});

socket.on('chat_message', data => {
    const chat = document.getElementById("chat-messages");
    const p = document.createElement("p");
    p.textContent = data.message;
    chat.appendChild(p);
    chat.scrollTop = chat.scrollHeight;
});

