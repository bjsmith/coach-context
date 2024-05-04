#front-end
print(__name__)
if __name__ != '__main__':
    print("using eventlet")
    #workaround--I only want to use eventlet on the server
    import eventlet
    eventlet.monkey_patch()
else:
    print("not using eventlet")
from flask import Flask, render_template, make_response, request, jsonify
from flask_socketio import SocketIO, emit
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

#back-end
from chat import ChatConfig, CoachingIOInterface
from session import SessionManager

#other
import time
wapp = Flask(__name__)
wapp.config['SECRET KEY'] = ChatConfig.get_config()['flask_secret']
socketio = SocketIO(wapp)

@wapp.route('/')
def index():
    #this will remember the user based on a cookie
    #thi will be persistent within the browser, hence "browser_id"
    user_browser_id = request.cookies.get('userId')

    if not user_browser_id:
        # Generate a new user ID somehow; here we fabricate a random one
        import uuid
        user_browser_id = str(uuid.uuid4())

    resp = make_response(render_template('chat.html', user_id=user_browser_id))
    resp.set_cookie('userId', user_browser_id, max_age=30*24*60*60, httponly=True)
        #expire one month from now.

    print(f"loading app initially. User ID cookie: {user_browser_id}")



    return resp

# @wapp.route("/get", methods=["GET","POST"])
# def chat():
#     msg= request.form["msg"]
#     identity = request.form["identity"]
#     input = msg
#     return get_Chat_response(input)
@socketio.on('connection')
def handle_open(data):
    print("connection from user opened")
    emit('response', "connection opened",to=request.sid)



@socketio.on('message')
def handle_msg(data):
        #message = update.message
        message = data
        socket_identity = request.sid
        user_browser_id = request.cookies.get('userId')
        #client_ts = request.form["client_timestamp"]
        server_ts = time.time()

        print("call to handle_msg URL occured")

        #current_ts =0
        text = message
        user_id = user_browser_id

        channel_id = socket_identity
        ts = server_ts
        print(f"receiving message from user with cookie id {str(user_id)} and socket id {socket_identity} (" + str(ts) + ")")

        user_info = {
#            'first_name': identity,
            'language_code': 'en-US'
        }

        session_manager.handle_incoming_message(channel_id, user_id, text, user_info = user_info, ts=ts)
        print(f' received a message from a user ({user_id}) {text}')

        #self.send_message(channel_id, f"response")

        #return ("received your message. But I don't know how to respond yet.")


        #return jsonify({'status': 'ok'})



def send_message(channel_id,text):
    try:
        # Send a message using the Slack WebClient
        #context.bot.send_message(chat_id=update.effective_chat.id, text="alt-echo: " + update.message.text)
        #print(f"Message sent: {response['ts']} - {text}")
        print(f"sending message to {channel_id}")
        #await self.app.bot.send_message(chat_id=channel_id, text=text)
        emit('response', text,to=channel_id)
        #print(f"Message sent: {text}")
    except Exception as e:
        # In case of errors, print the error message
        print(f"Error sending message: {e}")
        



def get_Chat_response(text):
    #just reverse the input
    return text[::-1] + " is the reverse of the input"


class WebIO(CoachingIOInterface):
    """
    creates a mode-agnostic pattern for the therapist to use to communicate with the client
    """
    def __init__(self, send_message_callback):
        self.send_message_callback = send_message_callback
        pass

    def send_message(self, message, channel_id):
        self.send_message_callback(channel_id, message)

    def indicate_response_coming(self):
        pass

    def message_admin(self, message):
        pass
        admins = ChatConfig.get_config()['telegram_admin_ids']
        for admin in admins:
            self.send_message_callback(admin, message)


io = WebIO(send_message)
session_manager = SessionManager(io)


if __name__ == '__main__':
    #wapp.run(debug=True,port=5007)
    socketio.run(wapp,debug=False,port=5001)