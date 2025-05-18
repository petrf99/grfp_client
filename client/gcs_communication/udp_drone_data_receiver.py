import socket
import time

from tech_utils.logger import init_logger
logger = init_logger("RCClient_UDPReceiver")


from client.config import UDP_SEND_LOG_DELAY

def telemetry_receiver(sock: socket.socket):
    print("📡 Starting telemetry receiver...")
    logger.info("Starting udp receiver")
    sock.settimeout(1.0)
    
    last_inp_log_time = 0
    while True:
        try:
            data, addr = sock.recvfrom(65536)
            message = data.decode(errors="ignore")
            print(f"📥 Received from {addr}: {message}")
            cur_time = time.time()
            if cur_time - last_inp_log_time >= UDP_SEND_LOG_DELAY:
                logger.info(f"Received from {addr}: {message}")
        except socket.timeout:
            continue
        except OSError:
            print("🛑 Telemetry socket closed.")
            logger.error("Telemetry socker closed")
            break
        except Exception as e:
            print(f"⚠️ Telemetry error: {e}")
            logger.error(f"Telemetry error: {e}")

