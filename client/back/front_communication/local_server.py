import threading
import requests

from werkzeug.serving import make_server
from flask import Flask, request, jsonify

from client.back.config import BACK_SERV_PORT, CLIENT_TCP_PORT
from client.back.front_communication.front_msg_sender import send_message_to_front, message_queue
from client.back.gcs_communication.tailscale_connect import connect
from client.back.state import client_state
from client.back.task_manager.exits import disconnect, local_close_sess
from client.back.task_manager.start_sess import start_session

from tech_utils.logger import init_logger
logger = init_logger("Back_LocServ")


# === Flask App Initialization ===
back_app = Flask(__name__)
back_server = None


# === Server Startup / Shutdown ===
def run_back_server():
    """
    Start local Flask server to communicate with the frontend.
    """
    global back_server
    logger.info("Starting back local server")
    back_server = make_server("127.0.0.1", BACK_SERV_PORT, back_app)

    thread = threading.Thread(target=back_server.serve_forever)
    thread.start()
    logger.info(f"Back local server started on port {BACK_SERV_PORT}")


# === Routes ===
@back_app.route("/shutdown", methods=["POST"])
def shutdown():
    """
    Route to shut down the Flask server and GCS client server.
    """
    from tech_utils.flask_server_utils import shutdown_server
    if not shutdown_server("127.0.0.1", CLIENT_TCP_PORT, None, logger=logger):
        send_message_to_front("Could not finish Client's server correctly.")
    
    global back_server
    if back_server is None:
        return jsonify({"status": "error", "reason": "Server not running"}), 400

    logger.info("Shutdown requested via /shutdown")
    threading.Thread(target=back_server.shutdown).start()
    client_state.stop_back_event.set()
    return jsonify({"status": "ok", "message": "Server shutting down..."})


@back_app.route("/front-connect", methods=["POST"])
def front_connect():
    """
    Initiates connection to Tailnet using mission_id from the frontend.
    """
    data = request.get_json()
    if "mission_id" not in data:
        return jsonify({"status": "error", "reason": "Missing mission_id"}), 400
    
    threading.Thread(target=connect, args=(data.get("mission_id"),), daemon=True).start()
    return jsonify({"status": "ok"}), 200


@back_app.route("/front-disconnect", methods=["POST"])
def front_disconnect():
    """
    Triggers Tailscale disconnect and session cleanup.
    """
    threading.Thread(target=disconnect, daemon=True).start()
    return jsonify({"status": "ok"}), 200


@back_app.route("/front-launch-session", methods=["POST"])
def front_launch_session():
    """
    Starts a new session if session ID is present in client state.
    """
    logger.info("start-session command on Back server")
    if not client_state.session_id:
        return jsonify({"status": "error", "reason": "No session to start"}), 400 
    
    threading.Thread(target=start_session, daemon=True).start()
    return jsonify({"status": "ok"}), 200


@back_app.route("/front-close-session", methods=["POST"])
def front_close_session():
    """
    Gracefully closes the current session and clears state based on frontend's command.
    """
    data = request.get_json()
    result = data.get("result")

    if result not in ['abort', 'finish']:
        return jsonify({"status": "error", "reason": "Invalid or missing result"}), 400
    
    if not client_state.session_id:
        return jsonify({"status": "error", "reason": "No session to close"}), 400 

    threading.Thread(target=local_close_sess, args=(result=='finish',), daemon=True).start()
    return jsonify({"status": "ok"}), 200


@back_app.route("/get-message", methods=["POST"])
def get_message():
    """
    Sends queued status/message from backend to frontend.
    """
    if message_queue:
        msg = message_queue.pop(0)
        return jsonify({"status": "ok", "message": msg}), 200
    return jsonify({"status": "error", "reason": "No messages yet"}), 400


# === Entry Point ===
if __name__ == '__main__':
    run_back_server()
