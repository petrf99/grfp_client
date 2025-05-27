import requests
import time

from tech_utils.logger import init_logger
logger = init_logger("TechUtils_SafePOST")

def post_request(url, payload, description: str, retries = 3, timeout=1, event_to_set=None, print_func = lambda x: x, message=None):
    logger.info(f"Post request {description} to {url}: {payload}")
    try:
        for k in range(retries):
            try:
                response = requests.post(url, json=payload, timeout=20)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "ok":
                        logger.info(f"{description} — success")
                        return data
                else:
                    data = response.json()
                    reason = data.get("reason", "Unknown error")
                    logger.warning(f"{description} failed: {reason}")
                time.sleep(timeout)
            except Exception as e:
                logger.error(f"{description} — could not reach url: {e}")
            
            print_func(message)
    except KeyboardInterrupt:
        if event_to_set:
            event_to_set.set()
        logger.warning(f"Aborted by keyboard interrupt while {description}")
    return None