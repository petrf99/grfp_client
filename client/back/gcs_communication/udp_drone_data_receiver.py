import socket
import time
import json

from tech_utils.logger import init_logger
logger = init_logger("Client_UDPReceiver")


from client.front.config import UDP_SEND_LOG_DELAY, LOCAL_VIDEO_PORT

from client.session_manager.events import finish_event, abort_event

telemetry_data = {}
def telemetry_receiver(sock: socket.socket):
    global telemetry_data
    print("📡 Starting Telemetry receiver...")
    logger.info("Starting Telemetry receiver")
    sock.settimeout(1.0)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    last_inp_log_time = 0
    with open("logs/telemetry_log.jsonl.txt", "a") as tlmt_log:
        try:
            while not finish_event.is_set() and not abort_event.is_set():
                try:
                    data, addr = sock.recvfrom(65536)
                    telemetry_data.clear()
                    telemetry_data.update(json.loads(data))
                    cur_time = time.time()
                    telemetry_data["network_ping_ms"] = int(1000*(cur_time - telemetry_data.get("timestamp", cur_time)))
                    if cur_time - last_inp_log_time >= UDP_SEND_LOG_DELAY:
                        tlmt_log.write(json.dumps(telemetry_data) + "\n")
                        tlmt_log.flush()
                        logger.info(f"Telemetry received from {addr}: {len(data)} bytes")
                        last_inp_log_time = cur_time
                except socket.timeout:
                    continue
                except OSError as e:
                    print("🛑 Telemetry receiver socket closed.")
                    logger.warning(f"Telemetry receiver socker closed {e}")
                    break
                except Exception as e:
                    print(f"⚠️ Telemetry receiver error: {e}")
                    logger.error(f"Telemetry receiver error: {e}")
        except KeyboardInterrupt:
            print("🛑 Telemetry receiver interrupted by user.")
            logger.warning("Telemetry receiver interrupted by user.")
        finally:
            sock.close()

def video_receiver(sock: socket.socket):
    print("📡 Starting Video receiver...")
    logger.info("Starting Video receiver")
    sock.settimeout(1.0)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    last_inp_log_time = 0
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as self_sock:
        try:
            while not finish_event.is_set() and not abort_event.is_set():
                try:
                    data, addr = sock.recvfrom(65536)
                    self_sock.sendto(data, ("127.0.0.1", LOCAL_VIDEO_PORT))
                    cur_time = time.time()

                    if cur_time - last_inp_log_time >= UDP_SEND_LOG_DELAY:
                        logger.info(f"Video received from {addr}: {len(data)} bytes and re-streamed on local port {LOCAL_VIDEO_PORT}")
                        last_inp_log_time = cur_time

                except socket.timeout:
                    continue
                except OSError as e:
                    print("🛑 Video receiver socket closed.")
                    logger.warning(f"Video receiver socket closed {e}")
                    break
                except Exception as e:
                    print(f"⚠️ Video receiver error: {e}")
                    logger.error(f"Video receiver error: {e}")
                    break
        except KeyboardInterrupt:
            print("🛑 Video receiver interrupted by user.")
            logger.warning("Video receiver interrupted by user.")
        finally:
            sock.close()
