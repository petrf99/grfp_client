import requests
import time

from tech_utils.logger import init_logger
logger = init_logger("RCClient_GCS_Connect")

from client.config import CLIENT_TCP_PORT, GCS_TCP_PORT, NUM_START_SESS_ATTEMPTS, START_SESS_POLL_INTERVAL

def send_start_message_to_gcs(gcs_ip: str, session_id: str):
    url = f"http://{gcs_ip}:{GCS_TCP_PORT}/send-message"
    payload = {
        "session_id": session_id,
        "message": "start_session"
    }
    print(f"📡 Sending start_session to GCS at {gcs_ip}...")
    for _ in range(NUM_START_SESS_ATTEMPTS):
        try:
            res = requests.post(url, json=payload, timeout=5)
            if res.status_code == 200:
                print("✅ Handshake with GCS successful.")
                logger.info(f"{session_id} Handshake with GCS successfull")
                return True
        except Exception as e:
            print(f"No reach. Retrying...")
            logger.error(f"{session_id} Unsuccessfull handshake attempt with GCS. Exception: {e}. Retrying...")

        time.sleep(START_SESS_POLL_INTERVAL)

    print("❌ Could not confirm handshake with GCS.")
    logger.info(f"{session_id} Could not confirm handshake with GCS")
    return False


# client_flask_server.py
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/send-message", methods=["POST"])
def receive_message():
    data = request.get_json()
    print(f"📩 Message received from GCS: {data}")
    logger.info(f"Message received from GCS: {data}")
    return jsonify({"status": "ok"})

@app.route("/shutdown", methods=["POST"])
def shutdown():
    shutdown_func = request.environ.get('werkzeug.server.shutdown')
    if shutdown_func is None:
        logger.error("Error while shuttiing down flask server")
        raise RuntimeError("Not running with Werkzeug")
    shutdown_func()
    logger.info("Shutting down Flask server")
    return "🔌 Client Flask server shutting down..."

def run_client_server():
    app.run(host="0.0.0.0", port=CLIENT_TCP_PORT)

def shutdown_client_server():
    try:
        requests.post(f"http://localhost:{CLIENT_TCP_PORT}/shutdown")
        print("🔌 Client Flask server stopped.")
    except Exception as e:
        print(f"⚠️ Failed to shutdown Flask server: {e}")
