import socket
import time

from tech_utils.logger import init_logger
logger = init_logger("RCClient_UDPReceiver")


from client.config import UDP_SEND_LOG_DELAY

from client.session_manager.events import finish_event, abort_event
def telemetry_receiver(sock: socket.socket):
    print("📡 Starting Telemetry receiver...")
    logger.info("Starting Video receiver")
    sock.settimeout(1.0)
    
    last_inp_log_time = 0
    while not finish_event.is_set() and not abort_event.is_set():
        try:
            data, addr = sock.recvfrom(65536)
            message = data.decode(errors="ignore")
            cur_time = time.time()
            if cur_time - last_inp_log_time >= UDP_SEND_LOG_DELAY:
                print(f"📥 Received telemetry packet: {len(data)} bytes")
                with open("telemetry_dump.txt", "a") as f:
                    f.write(message + '\n\n\n')

                logger.info(f"Telemetry received from {addr}: {len(data)} bytes")
                last_inp_log_time = cur_time
        except socket.timeout:
            continue
        except OSError as e:
            print("🛑 Telemetry receiver socket closed.")
            logger.warning(f"Telemetry receiver socker closed {e}")
            break
        except KeyboardInterrupt:
            print("🛑 Telemetry receiver interrupted by user.")
            logger.warning("Telemetry receiver interrupted by user.")
            break
        except Exception as e:
            print(f"⚠️ Telemetry receiver error: {e}")
            logger.error(f"Telemetry receiver error: {e}")

    sock.close()

def video_receiver(sock: socket.socket):
    print("📡 Starting Video receiver...")
    logger.info("Starting Video receiver")
    sock.settimeout(1.0)
    
    last_inp_log_time = 0
    while not finish_event.is_set() and not abort_event.is_set():
        try:
            data, addr = sock.recvfrom(65536)
            message = data.decode(errors="ignore")
            cur_time = time.time()
            if cur_time - last_inp_log_time >= UDP_SEND_LOG_DELAY:
                print(f"📦 Received video packet: {len(data)} bytes")
                with open("video_dump.ts", "ab") as f:
                    f.write(data)

                logger.info(f"Video received from {addr}: {len(data)} bytes")
                last_inp_log_time = cur_time
        except socket.timeout:
            continue
        except OSError as e:
            print("🛑 Video receiver socket closed.")
            logger.warning(f"Video receiver socker closed {e}")
            break
        except KeyboardInterrupt:
            print("🛑 Video receiver interrupted by user.")
            logger.warning("Video receiver interrupted by user.")
            break
        except Exception as e:
            print(f"⚠️ Video receiver error: {e}")
            logger.error(f"Video receiver error: {e}")
    
    sock.close()



