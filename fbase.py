import os
import json
import time
import pyrebase
from dotenv import load_dotenv

load_dotenv()

config = {
    "apiKey": os.environ.get("FB_apiKey"),
    "authDomain": os.environ.get("FB_authDomain"),
    "projectId": os.environ.get("FB_projectId"),
    "storageBucket": os.environ.get("FB_storageBucket"),
    "messagingSenderId": os.environ.get("FB_messagingSenderId"),
    "appId": os.environ.get("FB_appId"),
    "measurementId": os.environ.get("FB_measurementId"),
    "databaseURL": os.environ.get("FB_databaseURL"),
}
# print(config)

firebase = pyrebase.initialize_app(config)
db = firebase.database()
auth = firebase.auth()


def login_to_firebase(email_id: str, password: str, save_to_json=False) -> dict[bool, str]:
    """ ### Function to log in to Firebase and return the status and message

    Args:
        email_id (str): Email ID of the user
        password (str): Password of the user
        save_to_json (bool): Flag to save the response to a JSON file (for development)

    Returns:
        dict: A dictionary containing:
        - "status" (bool): True if login is successful, False otherwise.
        - "message" (str): "Login successful" on success, or an error message on failure.
    """

    try:
        resp = auth.sign_in_with_email_and_password(
            email=email_id,
            password=password
        )
        uid = resp["localId"]
        token = resp["idToken"]

        # Save the uid, token and timestamp to env:
        os.environ["FB_LOGIN_UID"] = uid
        os.environ["FB_LOGIN_TOKEN"] = token
        os.environ["FB_LOGIN_TIMESTAMP"] = str(time.time())

        # To avoid repeated logins (in development)...:
        if save_to_json:
            t = {
                "status": True, "uid": uid,
                "token": token, "timestamp": str(time.time())
            }
            with open("./temp_resp_login.json", "w") as f:
                f.write(json.dumps(t, indent=4))

        # return {"status": True, "uid": uid, "token": token}
        return {"status": True, "message": "Login successful"}

    except Exception as e:
        try:
            error_msg = str(e.args)
            err_st = error_msg.find('{')
            err_en = error_msg.rfind("}")
            error_msg = error_msg[err_st:err_en+1].replace("\\n", "")
            error_msg = json.loads(error_msg)["error"]["message"]
        except:
            error_msg = "An error occurred"
        return {"status": False, "message": error_msg}


def is_login_expired():
    """ ### Function to check if the login is expired

    Returns:
        bool: True if login is expired, False otherwise.
    """

    try:
        timestamp = float(os.environ.get("FB_LOGIN_TIMESTAMP"))
        current_time = float(str(time.time()))

        if current_time - timestamp > 3600:
            return True
        else:
            return False

    except:
        return True


def read_node(node: str, uid: str, token: str) -> dict[bool, any]:
    """ ### Function to read a node from Firebase

    Args:
        node (str): Node to read from
        uid (str): User ID (used in building node path)
        token (str): Token (for authentication)

    Returns:
        dict: A dictionary containing:
        - "status" (bool): True if read is successful, False otherwise.
        - "message" (any): The data read from the node, or an error message on failure.
    """

    try:
        resp = db.child(f"users/{uid}/{node}").get(token).val()
        return {"status": True, "message": resp}

    except Exception as e:
        try:
            err_msg = str(e.args)
            err_st = err_msg.find("{")
            err_en = err_msg.find("}")
            err_msg = err_msg[err_st:err_en+1].replace("\\n", "")
            err_msg = json.loads(err_msg)["error"]
        except:
            err_msg = "An error occurred"

        return {"status": False, "message": err_msg}


if __name__ == "__main__":
    # To avoid repeated logins, load json, (daily login limit)...
    try:
        with open("./temp_resp_login.json", "r") as f:
            resp = json.load(f)
            os.environ["FB_LOGIN_UID"] = resp["uid"]
            os.environ["FB_LOGIN_TOKEN"] = resp["token"]
            os.environ["FB_LOGIN_TIMESTAMP"] = resp["timestamp"]
    except:
        None

    # Login to Firebase:
    if is_login_expired():
        resp = login_to_firebase(
            email_id=os.environ.get("TEST_ID"),
            password=os.environ.get("TEST_PW"),
            save_to_json=True
        )
        print("New Login attempted...")
    else:
        print("Using existing login...")

    if not resp["status"]:
        print(f'Failed to login: `{resp["message"]}`')
    else:
        uid = os.environ.get("FB_LOGIN_UID")
        token = os.environ.get("FB_LOGIN_TOKEN")

        # resp = read_node(uid=uid, token=token, node="full_day_data")
        resp = read_node(uid=uid, token=token, node="test")
        if resp["status"]:
            print(f'Node Data: `{resp["message"]}`')
        else:
            print(f'Failed to read node: `{resp["message"]}`')
