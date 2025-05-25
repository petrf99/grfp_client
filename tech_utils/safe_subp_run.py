import subprocess
import time

from tech_utils.logger import init_logger
logger = init_logger("SafeSUBPRun_TechUtils")

def safe_subp_run(
    command,
    retries=3,
    timeout=10,
    delay_between_retries=2,
    **kwargs
):
    """
    Runs a subprocess with a timeout and retries in case of hanging.

    :param command: Command as a list (e.g., ['tailscale', 'up'])
    :param retries: Number of attempts
    :param timeout: Timeout for each attempt (in seconds)
    :param delay_between_retries: Delay between retries (in seconds)
    :param kwargs: Additional arguments passed to subprocess.run
    :return: subprocess.CompletedProcess if successful
    :raises: subprocess.TimeoutExpired or subprocess.CalledProcessError after all retries fail
    """
    last_exception = None

    for attempt in range(1, retries + 1):
        try:
            logger.info(f"[{attempt}/{retries}] Run subprocess: {' '.join(command)}")
            result = subprocess.run(command, timeout=timeout, **kwargs)
            logger.info("Cmd subprocess succeed")
            return result
        except subprocess.TimeoutExpired as e:
            logger.warning(f"Retry {attempt}: timeout ({timeout} sec) while running subprocess.")
            last_exception = e
        except subprocess.CalledProcessError as e:
            logger.warning(f"Retry {attempt}: error run subprocess: {e}")
            return e

        if attempt < retries:
            logger.info(f"Delay {delay_between_retries} sec before next retry...")
            time.sleep(delay_between_retries)

    logger.error("Couldn't run subprocess")
    raise last_exception
