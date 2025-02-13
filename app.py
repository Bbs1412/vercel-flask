import os
from flask import Flask, jsonify, request, send_from_directory, render_template

from fbase import login_to_firebase, read_node

# Config:
# get this code files absolute path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(BASE_DIR, 'Templates')
static_dir = os.path.join(BASE_DIR, 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)


# Test route:
@app.route('/test')
def test():
    return jsonify(status=True, message="Server is live")


# Main route:
@app.route('/')
def index():
    return render_template('index.html')

# Serve the static files:
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory(static_dir, path)
# ex. http://localhost:5454/static/css/style.css



# Route for login:
@app.route('/login')
def login():
    resp = login_to_firebase(
        email_id=os.environ.get("TEST_ID"),
        password=os.environ.get("TEST_PW")
    )
    return jsonify(resp)


# Route to get data, has parameter ideal_mode(bool):
@app.route('/get_data')
def get_data():
    ideal_mode = request.args.get('ideal_mode', False) == "true"

    node = "full_day_data" if ideal_mode else "live_data"

    resp = read_node(
        node=node,
        uid=os.environ.get("FB_LOGIN_UID"),
        token=os.environ.get("FB_LOGIN_TOKEN")
    )

    return jsonify(resp)


# Entry point:
if __name__ == '__main__':
    app.run(
        port=5454,
        debug=True,
        load_dotenv=True,
    )
