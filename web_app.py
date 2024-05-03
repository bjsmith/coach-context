from flask import Flask, render_template, request, jsonify

wapp = Flask(__name__)

@wapp.route('/')
def index():
    return render_template('chat.html')

@wapp.route("/get", methods=["GET","POST"])
def chat():
    msg= request.form["msg"]
    identity = request.form["identity"]
    input = msg
    return get_Chat_response(input)

def get_Chat_response(text):
    #just reverse the input
    return text[::-1] + " is the reverse of the input"
    #return text +" is the reverse of the input"

# if __name__=="__main__":
#     wapp.run()