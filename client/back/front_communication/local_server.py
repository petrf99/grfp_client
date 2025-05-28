from werkzeug.serving import make_server
import threading
import requests
import uuid

from client.back.config import BACK_SERV_PORT
from client.back.front_communication.front_msg_sender import send_message_to_front
from client.back.gcs_communication.tailscale_connect import connect
from client.back.state import client_state

from tech_utils.logger import init_logger
logger = init_logger("Back_LocServ")

### === Server set up ===

from flask import Flask, request, jsonify
back_app = Flask(__name__)

back_server = None

def run_back_server():
    logger.info("Starting back local server")
    global back_server
    back_server = make_server("127.0.0.1", BACK_SERV_PORT, back_app)
    
    thread = threading.Thread(target=back_server.serve_forever)
    thread.start()
    logger.info("Back local server started")


def shutdown_back_server():
    send_message_to_front("Stopping TCP server...")
    try:
        res = requests.post(f"http://127.0.0.1:{BACK_SERV_PORT}/shutdown", timeout=3)
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
    from client.back.gcs_communication.tcp_communication import shutdown_client_server
    if not shutdown_client_server():
        send_message_to_front("Could not finish TCP server correctly.")
    global back_server
    if back_server is None:
        return jsonify({"status": "error", "reason": "Server not running"}), 400

    logger.info("Shutdown requested via /shutdown")
    shutdown_thread = threading.Thread(target=back_server.shutdown)
    shutdown_thread.start()
    client_state.stop_back_event.set()
    return jsonify({"status": "ok", "message": "Server shutting down..."})


from client.back.config import RFD_IP, RFD_SM_PORT

import hashlib
def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest().upper()

RFD_URL = f"http://{RFD_IP}:{RFD_SM_PORT}/validate-token"

@back_app.route("/front-connect", methods=["POST"])
def front_connect():
    data = request.get_json()
    if "mission_id" not in data:
        return jsonify({"status": "error", "reason": "Missing mission_id"}), 400
    threading.Thread(target=connect, args=(data.get("mission_id"), ), daemon=True).start()
    return jsonify({"status": "ok"}), 200

from client.back.task_manager.exits import disconnect

@back_app.route("/front-disconnect", methods=["POST"])
def front_disconnect():
    threading.Thread(target=disconnect, args=(), daemon=True).start()
    return jsonify({"status": "ok"}), 200

from client.back.task_manager.start_sess import start_session
@back_app.route("/front-launch-session", methods=["POST"])
def front_launch_session():
    logger.info(f"start-session command on Back server")
    if not client_state.session_id:
        return jsonify({"status": "error", "reason": "No session to start"}), 400 
    
    threading.Thread(target=start_session, daemon=True).start()
    return jsonify({"status": "ok"}), 200


from client.back.task_manager.exits import local_close_sess

@back_app.route("/front-close-session", methods=["POST"])
def front_close_session():
    data = request.get_json()
    if not "result" in data:
        return jsonify({"status": "error", "reason": "Missing result"}), 400
    
    if not client_state.session_id:
        return jsonify({"status": "error", "reason": "No session to close"}), 400 

    if data.get('result') == 'abort':
        client_state.abort_event.set()
    elif data.get('result') == 'finish':
        client_state.finish_event.set()
    else:
        return jsonify({"status": "error", "reason": "Invalid result"}), 400 
    
    threading.Thread(target=local_close_sess, args=(client_state.finish_event.is_set(), ), daemon=True).start()

    return jsonify({"status": "ok"}), 200
    

from client.back.front_communication.front_msg_sender import message_queue

@back_app.route("/get-message", methods=["POST"])
def get_message():
    if message_queue:
        msg = message_queue.pop(0)  # достаём и удаляем первое сообщение
        return jsonify({"status": "ok", "message": msg}), 200
    else:
        return jsonify({"status": "error", "reason": "No messages yet"}), 400
    

if __name__ == '__main__':
    run_back_server()