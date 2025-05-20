import socket
import time

from tech_utils.logger import init_logger
logger = init_logger("RCClient_UDPReceiver")


from client.config import UDP_SEND_LOG_DELAY

from client.session_manager.events import finish_event, abort_event
def telemetry_receiver(sock: socket.socket):
    print("📡 Starting telemetry receiver...")
    logger.info("Starting udp receiver")
    sock.settimeout(1.0)
    
    last_inp_log_time = 0
    while not finish_event.is_set() and not abort_event.is_set():
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
            print("🛑 Drone data receiver socket closed.")
            logger.error("Drone data receiver socker closed")
            break
        except KeyboardInterrupt:
            print("🛑 Drone data receiver interrupted by user.")
            logger.warning("Drone data receiver interrupted by user.")
            break
        except Exception as e:
            print(f"⚠️ Drone data receiver error: {e}")
            logger.error(f"Drone data receiver error: {e}")


