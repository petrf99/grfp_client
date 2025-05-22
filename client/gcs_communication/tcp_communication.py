import requests
import time
import threading

from tech_utils.logger import init_logger
logger = init_logger("RCClient_GCS_Connect")


from client.config import CLIENT_TCP_PORT, GCS_TCP_PORT, NUM_START_SESS_ATTEMPTS, START_SESS_POLL_INTERVAL,TCP_KEEP_CONNECTION_RETRIES, PING_INTERVAL


# client_flask_server.py
from flask import Flask, request, jsonify

app = Flask(__name__)

from client.session_manager.events import finish_event, abort_event, external_stop_event

@app.route("/send-message", methods=["POST"])
def receive_message():
    data = request.get_json()
    logger.info(f"Message received on TCP Flask server: {data}")
    message = data.get("message", "")
    if message == 'abort-session':
        abort_event.set()
        external_stop_event.set()
    if message == 'finish-session':
        finish_event.set()
        external_stop_event.set()
    if 'session' in message:
        return jsonify({"status": "ok"})
    else:
        return jsonify({"status": "error", "reason": "What?"}), 400

server = None  # ссылка на сервер
from werkzeug.serving import make_server

@app.route("/shutdown", methods=["POST"])
def shutdown():
    global server
    if server is None:
        return jsonify({"status": "error", "reason": "Server not running"}), 400

    logger.info("Shutdown requested via /shutdown")
    shutdown_thread = threading.Thread(target=server.shutdown)
    shutdown_thread.start()
    return jsonify({"status": "ok", "message": "Server shutting down..."})

def run_client_server():
    global server
    server = make_server("0.0.0.0", CLIENT_TCP_PORT, app)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    logger.info("Flask server started")

def shutdown_client_server():
    print("Stopping TCP server...")
    try:
        res = requests.post(f"http://localhost:{CLIENT_TCP_PORT}/shutdown", timeout=3)
        if res.ok:
            logger.info("TCP server stopped")
            print("🔌 TCP server stopped.")
        return True
    except requests.exceptions.ConnectionError:
        logger.error("TCP server not running (already stopped)")
        print("⚠️ TCP server not running (already stopped).")
    except Exception as e:
        logger.error(f"Failed to shutdown TCP server: {e}")
        print(f"⚠️ Failed to shutdown TCP server: {e}")
    return False

from client.session_manager.basic_commands import close
def send_start_message_to_gcs(gcs_ip: str, session_id: str):
    url = f"http://{gcs_ip}:{GCS_TCP_PORT}/send-message"
    payload = {
        "session_id": session_id,
        "message": "start-session"
    }
    print(f"📡 Sending start-session to GCS at {gcs_ip}...")
    try:
        for _ in range(NUM_START_SESS_ATTEMPTS):
            try:
                res = requests.post(url, json=payload, timeout=5)
                if res.status_code == 200:
                    print("✅ Handshake with GCS successful.")
                    logger.info(f"{session_id} Handshake with GCS successfull")
                    return True
                else:
                    logger.warning(f"{session_id} Handshake to GCS went wrong. Status_code: {res.status_code}")
            except Exception as e:
                logger.error(f"{session_id} Unsuccessfull handshake attempt with GCS. Exception: {e}. Retrying...")

            print(f"Attempt {_+1}/{NUM_START_SESS_ATTEMPTS}: No reach. Retrying...")
            time.sleep(START_SESS_POLL_INTERVAL)
    except KeyboardInterrupt:
        abort_event.set()
        logger.warning(f"{session_id} aborted by keyboard interrupt while sending handshake to GCS")
        close(gcs_ip, session_id)

    print("❌ Could not confirm handshake with GCS.")
    logger.info(f"{session_id} Could not confirm handshake with GCS")
    return False


def keep_connection(gcs_ip, session_id):
    logger.info(f"Started keep-connection thread for session {session_id}")
    url = f"http://{gcs_ip}:{CLIENT_TCP_PORT}/send-message"
    payload = {
        "session_id": session_id,
        "message": "ping-session"
    }

    fails = 0
    while not finish_event.is_set() and not abort_event.is_set():
        try:
            res = requests.post(url, json=payload, timeout=5)
            if res.status_code == 200:
                logger.info(f"{session_id} Ping to GCS successfull")
                fails = 0
            else:
                fails += 1
                print("⚠️ Connection with GCS went wrong, retrying...")
                logger.warning(f"{session_id} Ping to GCS went wrong. Status_code: {res.status_code}")
        except Exception as e:
            fails += 1
            print("❌ Connection with GCS failed, retrying...")
            logger.error(f"{session_id} Unsuccessfull handshake attempt with GCS. Exception: {e}. Retrying...")

        if fails >= TCP_KEEP_CONNECTION_RETRIES:
            abort_event.set()
            print("❌ GCS has disconnected. Please contact administrator.\nClosing the session...")
            logger.error(f"{session_id} No TCP connection with GCS")
            break

        time.sleep(PING_INTERVAL)
    
    logger.info(f"Finished keep-connection thread for session {session_id}")


if __name__ == '__main__':
    run_client_server()