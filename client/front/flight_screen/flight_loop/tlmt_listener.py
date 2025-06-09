import time
from tech_utils.udp_listener import UDPListener

from client.front.config import CLIENT_TLMT_RECV_PORT, FREQUENCY

from tech_utils.logger import init_logger
logger = init_logger("Front_TLMT_Listener")

# 📡 Global telemetry data storage
telemetry_data = {}

# 📡 Listening for telemetry data on the given socket and update telemetry state
def get_telemetry():
    listener = UDPListener(CLIENT_TLMT_RECV_PORT)
    from client.front.state import front_state
    global telemetry_data

    try:
        while front_state.running_event.is_set():
            data = listener.get_latest()
            if not data:
                time.sleep(0.001)  # avoid busy-loop
                continue

            try:
                telemetry_data.clear()
                telemetry_data.update(data)

                # Calculate round-trip time (RTT) for RC channel timestamps if available
                cur_time = time.time()
                init_timestamp = telemetry_data.get("rc_channels", {}).get("init_timestamp")
                if init_timestamp is not None:
                    telemetry_data["round_trip_time_ms"] = int(1000 * (cur_time - init_timestamp))
            except Exception as e:
                logger.warning(f"Telemetry parse/update error: {e}")

    except OSError as e:
        logger.warning(f"Telemetry receiver socket closed: {e}")
    except Exception as e:
        logger.error(f"Telemetry receiver error: {e}")
    finally:
        listener.stop()
