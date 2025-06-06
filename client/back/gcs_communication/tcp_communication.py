import requests
import time
import threading

from client.back.front_communication.front_msg_sender import send_message_to_front
from tech_utils.safe_post_req import post_request
from client.back.config import CLIENT_TCP_PORT, GCS_TCP_PORT, NUM_START_SESS_ATTEMPTS, START_SESS_POLL_INTERVAL, PING_INTERVAL, TCP_KEEP_CONNECTION_RETRIES
from client.back.state import client_state

# === Flask server setup ===
from flask import Flask, request, jsonify
app = Flask(__name__)

server = None  # server reference for controlled shutdown
from werkzeug.serving import make_server

from tech_utils.logger import init_logger
logger = init_logger("Client_GCS_Connect")

# Starts the local Flask TCP server on the client
def run_client_server():
    global server
    server = make_server("0.0.0.0", CLIENT_TCP_PORT, app)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    logger.info(f"Flask server started on port {CLIENT_TCP_PORT}")

# Graceful shutdown endpoint for the TCP server
@app.route("/shutdown", methods=["POST"])
def shutdown():
    global server
    if server is None:
        return jsonify({"status": "error", "reason": "Server not running"}), 400

    logger.info("Shutdown requested via /shutdown")
    shutdown_thread = threading.Thread(target=server.shutdown)
    shutdown_thread.start()
    return jsonify({"status": "ok", "message": "Server shutting down..."})


# === Main GCS <-> Client communication endpoint ===

@app.route("/send-message", methods=["POST"])
def receive_message():
    data = request.get_json()
    logger.info(f"Message received on TCP Flask server: {data}")
    message = data.get("message", "")

    # GCS requests to abort session
    if message == 'abort-session':
        client_state.abort_event.set()
        client_state.external_stop_event.set()
        send_message_to_front('abort')
        return jsonify({"status": "ok"})

    # GCS requests to finish session normally
    elif message == 'finish-session':
        client_state.finish_event.set()
        client_state.external_stop_event.set()
        send_message_to_front('finish')
        return jsonify({"status": "ok"})

    # GCS initiates a session
    elif message == "start-session":
        client_state.session_id = data.get("session_id")
        client_state.gcs_rc_port = data.get("gcs_rc_port")
        client_state.gcs_ip = request.remote_addr
        send_message_to_front(f"session-request GCS IP: {client_state.gcs_ip}. Session_id: {client_state.session_id}")
        return jsonify({
            "status": "ok",
            "client_vid_port": client_state.client_vid_port,
            "client_tlmt_port": client_state.client_tlmt_port
        })

    # GCS pings or sends status update
    elif 'session' in message:
        return jsonify({"status": "ok"})

    # Unknown message type
    else:
        return jsonify({"status": "error", "reason": "What?"}), 400


# === Initiates handshake with GCS ===
def send_start_message_to_gcs():
    logger.info(f"Starting handshake with GCS. {client_state}")
    url = f"http://{client_state.gcs_ip}:{GCS_TCP_PORT}/send-message"
    payload = {
        "session_id": client_state.session_id,
        "message": "start-session"
    }
    send_message_to_front(f"📡 Sending start_session to GCS at {client_state.gcs_ip}:{GCS_TCP_PORT}...")
    
    res = post_request(
        url=url,
        payload=payload,
        description="GCS Handshake",
        retries=NUM_START_SESS_ATTEMPTS,
        timeout=START_SESS_POLL_INTERVAL,
        event_to_set=client_state.abort_event,
        print_func=send_message_to_front,
        message="📡 Waiting for a Handshake with GCS"
    )

    if res:
        send_message_to_front("✅ Handshake with GCS for successful.")
        logger.info(f"Handshake with GCS successfull {client_state}")
        return True

    send_message_to_front("❌ Could not confirm handshake with GCS.")
    logger.error(f"Could not confirm handshake with GCS {client_state}")
    return False


# === Keeps the TCP session alive with GCS ===
def keep_connection():
    logger.info(f"Started keep-connection thread for session {client_state}")
    url = f"http://{client_state.gcs_ip}:{GCS_TCP_PORT}/send-message"
    payload = {
        "session_id": client_state.session_id,
        "message": "ping-session"
    }

    fails = 0
    while not client_state.finish_event.is_set() and not client_state.abort_event.is_set():
        print(client_state.abort_event.is_set(), client_state.finish_event.is_set())
        try:
            res = requests.post(url, json=payload, timeout=5)
            if res.status_code == 200:
                logger.info(f"{client_state} Ping to GCS successful")
                fails = 0
            else:
                fails += 1
                send_message_to_front("⚠️ Connection with GCS went wrong, retrying...")
                logger.warning(f"{client_state} Ping to GCS failed. Status_code: {res.status_code}")
        except Exception as e:
            fails += 1
            send_message_to_front("❌ Connection with GCS failed, retrying...")
            logger.error(f"{client_state} Unsuccessful ping to GCS. Exception: {e}")

        # Too many failed attempts, consider connection lost
        if fails >= TCP_KEEP_CONNECTION_RETRIES:
            client_state.abort_event.set()
            send_message_to_front("❌ GCS has disconnected. Please contact administrator.\nClosing the session...")
            send_message_to_front("abort")
            logger.error(f"{client_state} No TCP connection with GCS")
            break

        time.sleep(PING_INTERVAL)
    
    logger.info(f"Finished keep-connection thread for session {client_state}")


if __name__ == '__main__':
    run_client_server()
