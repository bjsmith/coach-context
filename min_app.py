#front-end
import eventlet
eventlet.monkey_patch()
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit

#other
import time
wapp = Flask(__name__)
wapp.config['SECRET KEY'] = 'abc123thatshoweasylovecanbe'
socketio = SocketIO(wapp)

@wapp.route('/')
def index():
    print("loading app initially.")
    return render_template('chat.html')

@socketio.on('connection')
def handle_open(data):
    print("connection from user opened")
    emit('response', "connection opened",to=request.sid)

@socketio.on('message')
def handle_msg(data):
        message = data
        user_id = request.sid
        server_ts = time.time()
        print("call to handle_msg URL occured")

        print("receiving message from user " + str(user_id) + " (" + str(server_ts) + ")")

        send_message(user_id, f"received your message {message}")
        print(f' received a message from a user ({user_id}) {message}')

def send_message(channel_id,text):
    try:
        # Send a message using the Slack WebClient
        #context.bot.send_message(chat_id=update.effective_chat.id, text="alt-echo: " + update.message.text)
        #print(f"Message sent: {response['ts']} - {text}")
        #await self.app.bot.send_message(chat_id=channel_id, text=text)
        emit('response', text,to=channel_id)
        #print(f"Message sent: {text}")
    except Exception as e:
        # In case of errors, print the error message
        print(f"Error sending message: {e}")

if __name__ == '__main__':
    #wapp.run(debug=True)
    socketio.run(wapp,debug=True)