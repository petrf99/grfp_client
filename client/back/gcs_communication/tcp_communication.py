import requests
import time
import threading

from client.back.front_communication.front_msg_sender import send_message_to_front
from tech_utils.safe_post_req import post_request
from client.back.config import CLIENT_TCP_PORT, GCS_TCP_PORT, NUM_START_SESS_ATTEMPTS, START_SESS_POLL_INTERVAL, PING_INTERVAL, TCP_KEEP_CONNECTION_RETRIES
from client.back.state import client_state

# === Client's Server Set-up
from flask import Flask, request, jsonify
app = Flask(__name__)

server = None  # ссылка на сервер
from werkzeug.serving import make_server

from tech_utils.logger import init_logger
logger = init_logger("Client_GCS_Connect")

def run_client_server():
    global server
    server = make_server("0.0.0.0", CLIENT_TCP_PORT, app)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    logger.info("Flask server started")

@app.route("/shutdown", methods=["POST"])
def shutdown():
    global server
    if server is None:
        return jsonify({"status": "error", "reason": "Server not running"}), 400

    logger.info("Shutdown requested via /shutdown")
    shutdown_thread = threading.Thread(target=server.shutdown)
    shutdown_thread.start()
    return jsonify({"status": "ok", "message": "Server shutting down..."})


def shutdown_client_server():
    send_message_to_front("Stopping TCP server...")
    try:
        res = requests.post(f"http://localhost:{CLIENT_TCP_PORT}/shutdown", timeout=3)
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




# === Actual GCS Communication methods ===

@app.route("/send-message", methods=["POST"])
def receive_message():
    data = request.get_json()
    logger.info(f"Message received on TCP Flask server: {data}")
    message = data.get("message", "")
    if message == 'abort-session':
        client_state.abort_event.set()
        client_state.external_stop_event.set()
        send_message_to_front('abort')
        return jsonify({"status": "ok"})
    elif message == 'finish-session':
        client_state.finish_event.set()
        client_state.external_stop_event.set()
        send_message_to_front('finish')
        return jsonify({"status": "ok"})
    elif message == "start-session":
        client_state.session_id = data.get("session_id")
        client_state.gcs_rc_port = data.get("gcs_rc_port")
        client_state.gcs_ip = request.remote_addr
        send_message_to_front(f"session-request. GCS IP: {client_state.gcs_ip}")
        return jsonify({"status": "ok", "client_vid_port": client_state.client_vid_port, "client_tlmt_port": client_state.client_tlmt_port})
    elif 'session' in message:
        return jsonify({"status": "ok"})
    else:
        return jsonify({"status": "error", "reason": "What?"}), 400



def send_start_message_to_gcs():
    logger.info(f"Starting handshake with GCS. {client_state}")
    url = f"http://{client_state.gcs_ip}:{GCS_TCP_PORT}/send-message"
    payload = {
        "session_id": client_state.session_id,
        "message": "start-session"
    }
    send_message_to_front(f"📡 Sending start_session to GCS at {client_state.gcs_ip}...")
    res = post_request(url=url, payload=payload, 
                       description=f"GCS Handshake", 
                       retries=NUM_START_SESS_ATTEMPTS, timeout=START_SESS_POLL_INTERVAL, 
                       event_to_set=client_state.abort_event, 
                       print_func=send_message_to_front, 
                       message=f"📡 Waiting for a Handshake with GCS")
    if res:
        send_message_to_front(f"✅ Handshake with GCS for successful.")
        logger.info(f"Handshake with GCS successfull {client_state}")
        return True

    send_message_to_front(f"❌ Could not confirm handshake with GCS.")
    logger.error(f"Could not confirm handshake with GCS {client_state}")
    return False


def keep_connection():
    logger.info(f"Started keep-connection thread for session {client_state}")
    url = f"http://{client_state.gcs_ip}:{GCS_TCP_PORT}/send-message"
    payload = {
        "session_id": client_state.session_id,
        "message": "ping-session"
    }

    fails = 0
    while not client_state.finish_event.is_set() and not client_state.abort_event.is_set():
        try:
            res = requests.post(url, json=payload, timeout=5)
            if res.status_code == 200:
                logger.info(f"{client_state} Ping to GCS successfull")
                fails = 0
            else:
                fails += 1
                send_message_to_front("⚠️ Connection with GCS went wrong, retrying...")
                logger.warning(f"{client_state} Ping to GCS went wrong. Status_code: {res.status_code}")
        except Exception as e:
            fails += 1
            send_message_to_front("❌ Connection with GCS failed, retrying...")
            logger.error(f"{client_state} Unsuccessfull handshake attempt with GCS. Exception: {e}. Retrying...")

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