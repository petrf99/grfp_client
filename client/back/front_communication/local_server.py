from werkzeug.serving import make_server
import threading
import requests
import uuid

from client.back.config import CLIENT_BACK_SERV_PORT
from client.back.front_communication.front_msg_sender import send_message_to_front
from client.back.session_manager.state import sess_state

from tech_utils.logger import init_logger
logger = init_logger("Back_LocServ")

### === Server set up ===

running = threading.Event()

from flask import Flask, request, jsonify
back_app = Flask(__name__)

back_server = None

def run_back_server():
    logger.info("Starting back local server")
    global back_server, running
    back_server = make_server("127.0.0.1", CLIENT_BACK_SERV_PORT, back_app)
    thread = threading.Thread(target=back_server.serve_forever)
    thread.start()
    running.set()
    logger.info("Back local server started")


def shutdown_back_server():
    send_message_to_front("Stopping TCP server...")
    try:
        res = requests.post(f"http://127.0.0.1:{CLIENT_BACK_SERV_PORT}/shutdown", timeout=3)
        if res.ok:
            logger.info("TCP server stopped")
            send_message_to_front("🔌 TCP server stopped.")
        return True
    except requests.exceptions.ConnectionError:
        logger.error("TCP server not running (already stopped)")
        send_message_to_front("⚠️ TCP server not running (already stopped).")
    except Exception as e:
        logger.error(f"Failed to shutdown TCP server: {e}")
        send_message_to_front(f"⚠️ Failed to shutdown TCP server: {e}")
    return False

### === Methods ====

@back_app.route("/shutdown", methods=["POST"])
def shutdown():
    global back_server, running
    if back_server is None:
        return jsonify({"status": "error", "reason": "Server not running"}), 400

    logger.info("Shutdown requested via /shutdown")
    shutdown_thread = threading.Thread(target=back_server.shutdown)
    shutdown_thread.start()
    running.clear()
    return jsonify({"status": "ok", "message": "Server shutting down..."})


from client.back.config import RFD_IP, RFD_SM_PORT

import hashlib
def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest().upper()

RFD_URL = f"http://{RFD_IP}:{RFD_SM_PORT}/validate-token"

@back_app.route("/validate-token", methods=["POST"])
def validate_token():
    global sess_state
    data = request.get_json()
    logger.info(f"validate-token command on Back server")
    token = data.get("token", "")
    if token and token != "":
        try:
            response = requests.post(RFD_URL, json={"token": hash_token(token)}, timeout=5)
            data = response.json()
            if response.status_code == 200:
                if data.get("status") == "ok" and "session_id" in data:
                    sess_state.auth_token = token
                    logger.info(f"Token with hash {hash_token(token)} verified successully. Session-id:\n{data['session_id']}\n")
                    return jsonify({"status": "ok", "session_id": data.get("session_id")}), 200
            else:
                logger.info(f"Token with hash {hash_token(token)} verification failed. Reason: {data.get('reason', '')}")
                return jsonify({"status": "error", "reason": f"Token verification failed. Reason: {data.get('reason', '')}"}), 400
        except Exception as e:
            logger.error("Could not reach RFD\n")
            return jsonify({"status": "error", "reason": "Can't reach RFD"}), 500
        
from client.back.session_manager.start_sess import connect

@back_app.route("/start-session", methods=["POST"])
def start_session():
    global sess_state
    data = request.get_json()
    logger.info(f"start-session command on Back server: {data}")
    session_id = data.get("session_id", "")
    sess_state.session_id = session_id
    try:
        uuid.UUID(session_id)
    except Exception as e:
        return jsonify({"status": "error", "reason": "Incorrect session_id"}), 400
    

    if connect(session_id, sess_state.auth_token, 'client'):
        return jsonify({"status": "ok"}), 200
    else:
        return jsonify({"status": "error", "reason": "Can't start up a session on Back-end"}), 400
    
from client.back.session_manager.start_sess import launch_sess

@back_app.route("/launch-streams", methods=["POST"])
def launch_streams():
    global sess_state
    data = request.get_json()
    logger.info(f"start-session command on Back server: {data}")
    session_id = data.get("session_id", "")
    sess_state.controller = data.get("controller", "")
    if sess_state.session_id != session_id:
        return jsonify({"status": "error", "reason": "Session_id on Back server doesn't match with yours"}), 400
    if not launch_sess(session_id):
        return jsonify({"status": "error", "reason": "Error while launching RC-input stream or keeping connection with GCS"}), 500
    return jsonify({"status": "ok"}), 200

from client.back.session_manager.basic_commands import close

@back_app.route("/close-session", methods=["POST"])
def close_session():
    global sess_state
    data = request.get_json()
    logger.info(f"close-session command on Back server: {data}")
    session_id = data.get("session_id", "")
    if session_id == sess_state.session_id:
        close(sess_state.gcs_ip, session_id, data.get("finish_flg"))
        sess_state.clear()
        return jsonify({"status": "ok"}), 200
    else:
        return jsonify({"status": "error", "reason": "Session_id on Back server doesn't match with yours"}), 400
    

from client.back.front_communication.front_msg_sender import message_queue
from flask import Response

@back_app.route("/get-message", methods=["GET"])
def get_message():
    if message_queue:
        msg = message_queue.pop(0)  # достаём и удаляем первое сообщение
        return Response(msg, status=200, mimetype="text/plain")
    else:
        return Response("No msg yet", status=400, mimetype="text/plain")