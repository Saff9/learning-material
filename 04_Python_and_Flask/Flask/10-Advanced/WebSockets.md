---
title: WebSockets
description: Real-time bidirectional communication in Flask with Flask-SocketIO
chapter: 10-Advanced
tags:
  - websockets
  - socketio
  - real-time
  - flask-socketio
  - async
difficulty: Advanced
prerequisites:
  - [[10-Advanced/REST-API-Development]]
  - [[00-Foundations/TCP-UDP]]
---

# WebSockets

> HTTP is request-response — the client asks, the server answers. WebSockets enable full-duplex, real-time communication where either side can send data at any time. This is essential for chat applications, live notifications, collaborative editing, and real-time dashboards.

## Learning Objectives

After completing this chapter, you will be able to:

- Explain how WebSockets differ from HTTP and when to use them
- Implement WebSocket communication using Flask-SocketIO
- Handle connection events, messaging, and broadcasting
- Integrate WebSockets with Flask's authentication system
- Scale WebSocket applications with message queues
- Understand WebSocket security considerations

## HTTP vs. WebSockets

| Feature | HTTP | WebSockets |
|---------|------|------------|
| Communication | Request-response | Full-duplex bidirectional |
| Connection | Short-lived (per request) | Long-lived persistent |
| Overhead | Headers on every request | Minimal after handshake |
| Real-time | Polling/long-polling required | Native real-time |
| Use case | Document transfer, REST APIs | Chat, notifications, live data |

### WebSocket Handshake

WebSockets begin as an HTTP request that upgrades the connection:

```http
GET /chat HTTP/1.1
Host: example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
```

```http
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

After the handshake, the connection switches to the WebSocket protocol.

## Flask-SocketIO

Flask-SocketIO gives Flask applications access to WebSocket functionality.

### Installation

```bash
pip install flask-socketio
```

### Basic Setup

```python
from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins='*')

@app.route('/')
def index():
    return render_template('chat.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('message', {'data': 'Welcome!'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('message')
def handle_message(data):
    print(f'Received: {data}')
    emit('message', {'data': data}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)
```

### Client (JavaScript)

```html
<script src="https://cdn.socket.io/4.5.0/socket.io.min.js"></script>
<script>
    const socket = io();
    
    socket.on('connect', function() {
        console.log('Connected to server');
    });
    
    socket.on('message', function(data) {
        console.log('Received:', data);
        document.getElementById('messages').innerHTML += 
            '<p>' + data.data + '</p>';
    });
    
    function sendMessage() {
        const message = document.getElementById('message').value;
        socket.emit('message', message);
    }
</script>
```

## Rooms and Namespaces

### Rooms

Rooms allow sending messages to specific groups of clients:

```python
@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    emit('message', {'data': f'User joined {room}'}, to=room)

@socketio.on('leave')
def on_leave(data):
    room = data['room']
    leave_room(room)
    emit('message', {'data': f'User left {room}'}, to=room)

@socketio.on('room_message')
def handle_room_message(data):
    room = data['room']
    emit('message', {'data': data['message']}, to=room)
```

### Namespaces

Namespaces separate different communication channels:

```python
@socketio.on('connect', namespace='/chat')
def chat_connect():
    print('Connected to /chat namespace')

@socketio.on('message', namespace='/chat')
def chat_message(data):
    emit('response', {'data': data}, namespace='/chat')
```

```javascript
const chatSocket = io('/chat');
chatSocket.emit('message', 'Hello chat!');
```

## Authentication with WebSockets

```python
from flask_socketio import disconnect

@socketio.on('connect')
def handle_connect(auth):
    token = auth.get('token') if auth else None
    
    if not token:
        disconnect()
        return
    
    try:
        user_id = verify_token(token)  # Your token verification
        request.user_id = user_id
        join_room(f'user_{user_id}')
    except:
        disconnect()

@socketio.on('private_message')
def handle_private_message(data):
    recipient_id = data['to']
    emit('message', {'from': request.user_id, 'text': data['text']},
         to=f'user_{recipient_id}')
```

## Broadcasting Patterns

### Chat Room

```python
@socketio.on('send_message')
def handle_chat_message(data):
    message = Message(
        room=data['room'],
        user_id=request.user_id,
        content=data['content']
    )
    db.session.add(message)
    db.session.commit()
    
    emit('new_message', {
        'id': message.id,
        'user': message.user.username,
        'content': message.content,
        'timestamp': message.created_at.isoformat()
    }, to=data['room'])
```

### Live Notifications

```python
@socketio.on('post_created')
def notify_followers(data):
    post = Post.query.get(data['post_id'])
    for follower in post.author.followers:
        emit('notification', {
            'type': 'new_post',
            'message': f'{post.author.username} posted: {post.title}',
            'link': f'/posts/{post.id}'
        }, to=f'user_{follower.id}')
```

## Scaling WebSockets

For multiple server instances, use a message queue:

```python
# Using Redis as message broker
socketio = SocketIO(app, message_queue='redis://localhost:6379/0')
```

With this configuration, messages are broadcast across all server instances via Redis.

## Security Considerations

### 1. Authenticate Connections

Always verify the client's identity before allowing WebSocket connections.

### 2. Validate All Input

```python
@socketio.on('message')
def handle_message(data):
    if not isinstance(data, str) or len(data) > 1000:
        return  # Reject invalid input
    # Process message
```

### 3. Rate Limit

```python
from flask_limiter import Limiter

limiter = Limiter(app)

@socketio.on('message')
@limiter.limit("30 per minute")
def handle_message(data):
    pass
```

### 4. Use HTTPS/WSS

Always use WSS (WebSocket Secure) in production:
```javascript
const socket = io('wss://example.com');
```

## Common Mistakes

**Mistake: No authentication on WebSocket connections**
Anyone can connect if you don't authenticate.

**Mistake: Trusting client-sent data**
Always validate data from WebSocket clients.

**Mistake: Broadcasting to all clients**
Use rooms to limit message scope.

**Mistake: Not handling disconnections**
Clean up resources when clients disconnect.

## Exercises

1. **Chat Room**: Build a multi-room chat application.

2. **Notifications**: Add real-time notifications to a blog application.

3. **Typing Indicators**: Show "user is typing" indicators.

4. **Online Status**: Track and display user online/offline status.

## Quiz

**Question 1**: What is the main advantage of WebSockets over HTTP polling?

**Question 2**: Describe the WebSocket handshake process.

**Question 3**: What are rooms in Flask-SocketIO?

**Question 4**: How do you authenticate WebSocket connections?

**Question 5**: How do you scale WebSockets across multiple servers?

## Interview Questions

1. "When would you use WebSockets instead of HTTP?"

2. "How does Flask-SocketIO work? What transport does it use?"

3. "How would you implement authentication for WebSocket connections?"

4. "How do you scale real-time applications across multiple servers?"

5. "What security considerations apply to WebSocket applications?"

## Related Chapters

- [[10-Advanced/REST-API-Development]] — API design
- [[10-Advanced/JWT-Authentication]] — Token authentication
- [[08-Security/Security-Overview]] — Security fundamentals

## Official Documentation References

- [Flask-SocketIO Documentation](https://flask-socketio.readthedocs.io/)
- [Socket.IO Documentation](https://socket.io/docs/)
- [RFC 6455 - WebSocket Protocol](https://datatracker.ietf.org/doc/html/rfc6455)

---

*Previous: [[10-Advanced/JWT-Authentication]]*