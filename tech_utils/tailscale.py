import sys
import shutil
import re
import subprocess
import os
import time

from dotenv import load_dotenv
load_dotenv()

from tech_utils.logger import init_logger
logger = init_logger("Tailsale_TechUtils")


# ===== UTILS ====

def find_gui_tailscale_path_macos() -> str | None:
    # 1. Попытка найти через Spotlight (mdfind по bundle id)
    try:
        result = subprocess.run(
            ["mdfind", "kMDItemCFBundleIdentifier == 'com.tailscale.ipn.macsys'"],
            capture_output=True, text=True
        )
        for app_path in result.stdout.strip().splitlines():
            candidate = os.path.join(app_path, "Contents", "MacOS", "Tailscale")
            if os.path.exists(candidate):
                return candidate
    except Exception:
        pass

    # 2. Ручной обход популярных директорий
    possible_dirs = [
        "/Applications",
        os.path.expanduser("~/Applications"),
        os.path.expanduser("~/Downloads"),
        "/Users/Shared",
    ]

    for directory in possible_dirs:
        if not os.path.exists(directory):
            continue

        for item in os.listdir(directory):
            if item.lower().startswith("tailscale") and item.endswith(".app"):
                candidate = os.path.join(directory, item, "Contents", "MacOS", "Tailscale")
                if os.path.exists(candidate):
                    return candidate

    # 3. Жёсткий fallback: стандартный путь
    fallback = "/Applications/Tailscale.app/Contents/MacOS/Tailscale"
    if os.path.exists(fallback):
        return fallback

    return None


    
def get_tailscale_path() -> str:
    os_name = sys.platform

    # 1. Windows: try `where`
    if os_name.startswith("win"):
        try:
            result = subprocess.run(["where", "tailscale"], capture_output=True, text=True)
            if result.returncode == 0:
                path = result.stdout.strip().splitlines()[0]
                if os.path.exists(path):
                    return path
        except Exception:
            pass

    # 2. POSIX (Linux/macOS): try `which`
    found = shutil.which("tailscale")
    if found and os.path.exists(found):
        return found

    # 3. macOS: fallback to GUI
    if os_name == "darwin":
        gui_bin = find_gui_tailscale_path_macos()
        if gui_bin and os.path.exists(gui_bin):
            return gui_bin

    raise RuntimeError("❌ Tailscale binary not found on this system.")



def get_tailscaled_path():
    # Аналогично tailscale, ищем tailscaled
    path = shutil.which("tailscaled")
    if path and os.path.exists(path):
        return path

    # Попробуем GUI-путь macOS или другие редкие пути (по желанию)
    fallback_paths = [
        "/Users/peter/.homebrew/bin/tailscaled",  # для конкретных случаев
    ]
    for alt_path in fallback_paths:
        if os.path.exists(alt_path):
            return alt_path

    return None


def is_tailscaled_running() -> bool:
    # True только если процесс запущен и сокет существует
    try:
        result = subprocess.run(["pgrep", "tailscaled"], capture_output=True, text=True)
        if result.returncode != 0:
            return False
        return True #os.path.exists("/var/run/tailscaled.socket")
    except Exception as e:
        logger.warning(f"Error checking tailscaled status: {e}")
        return False


def is_tailscale_installed() -> bool:
    os_name = sys.platform

    # Windows: try `where tailscale`
    if os_name.startswith("win"):
        try:
            result = subprocess.run(["where", "tailscale"], capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False

    # Unix: try `which`
    cli_path = shutil.which("tailscale")
    if cli_path:
        return True

    # macOS only: try GUI version
    if os_name == "darwin":
        gui_path = find_gui_tailscale_path_macos()
        if gui_path and os.path.exists(gui_path):
            return 'macos-gui'
        
    return False


def needs_sudo_retry(stderr: str, os_name: str) -> bool:
    if not os_name.startswith(("linux", "darwin")):
        return False
    stderr = stderr.lower()
    return any(
        msg in stderr for msg in [
            "failed to connect to local tailscaled",
            "can't connect",
            "permission denied",
            "access denied",
            "connect: permission denied"
        ]
    )


# ============== UP ==================



import shlex
def start_tailscaled_if_needed() -> bool:
    if is_tailscaled_running():
        return True
    
    logger.info("Starting tailscaled")

    path = get_tailscaled_path()
    if not path:
        logger.error("❌ tailscaled binary not found.")
        return False
    

    try:
        print(f"🚀 Starting tailscaled via: {path}")
        # ⛔️ Важно: используем shell=True + nohup + redirect + background
        shell_cmd = f"nohup {shlex.quote(path)} --state=mem: --tun=userspace-networking >/dev/null 2>&1 &"
        sudo_cmd = ["sudo", "sh", "-c", shell_cmd]

        subprocess.run(
            sudo_cmd,
            check=True,
            text=True,
            stdin=sys.stdin  # позволяет ввести пароль
        )
        # Подождём немного и проверим несколько раз
        for i in range(10):
            time.sleep(1.5)
            if is_tailscaled_running():
                print("✅ tailscaled is now running.")
                logger.info("tailscaled is now running")
                return True
        print("❌ tailscaled did not start within timeout.")
        logger.error("tailscaled did not start within timeout.")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to start tailscaled: {e}")
        return False

    


def tailscale_up(hostname: str, auth_token: str):
    print("🔧 Starting Tailscale...")
    is_installed = is_tailscale_installed()
    if not is_installed:
        print("❌ Tailscale is not installed on this system.")
        logger.error(f"{hostname} Tailscale start failed — not installed")
        return False

    os_name = sys.platform
    mac_gui_flg = is_installed == 'macos-gui'

    if os_name.startswith(("linux", "darwin")) and not mac_gui_flg:
        if not start_tailscaled_if_needed():
            print("❌ Could not start tailscaled.")
            return False

    ts_path = get_tailscale_path()
    cmd = [ts_path, "up", f"--authkey={auth_token}", f"--hostname={hostname}"]

    try:
        logger.info(f"Starting tailscale for {hostname}")
        subprocess.run(cmd, check=True, capture_output=True, text=True, shell=os_name.startswith("win"))

        print("✅ Tailscale started.")
        logger.info(f"{hostname} Tailscale start succeeded on {os_name}")
        return True

    except subprocess.CalledProcessError as e:
        stderr = e.stderr or ""
        if needs_sudo_retry(stderr, os_name):
            # 2. Пробуем с sudo (если ошибка похожа на "нужен tailscaled")
            logger.info(f"Retry to start tailscale with sudo for {hostname}")
            try:
                sudo_cmd = ["sudo"] + cmd
                subprocess.run(
                    sudo_cmd,
                    check=True,
                    capture_output=True,
                    text=True,
                    shell=False,
                    stdin=sys.stdin
                )
                print("✅ Tailscale started with sudo.")
                logger.info(f"{hostname} Tailscale sudo-start succeeded on {os_name}")
                return True

            except subprocess.CalledProcessError as sudo_e:
                print("❌ Failed to start Tailscale with sudo:", sudo_e)
                logger.error(
                    f"{hostname} Tailscale sudo start failed. OS: {os_name} "
                    f"STDOUT: {sudo_e.stdout} STDERR: {sudo_e.stderr}",
                    exc_info=True
                )
                return False

        # Если ошибка не связана с tailscaled — не пробуем sudo
        print("❌ Failed to start Tailscale (non-sudo issue):", e)
        logger.error(
            f"{hostname} Tailscale start failed (non-sudo). OS: {os_name} "
            f"STDOUT: {e.stdout} STDERR: {e.stderr}",
            exc_info=True
        )
        return False
    
    except Exception as e:
        print("❌ Unexpected error while starting Tailscale:", e)
        logger.exception("Unexpected error during Tailscale start-up")
        return False



# =================== DOWN ==================


def stop_tailscaled():
    try:
        # Получаем PID
        result = subprocess.run(["pgrep", "tailscaled"], capture_output=True, text=True)
        if result.returncode != 0:
            return False

        pids = result.stdout.strip().split()
        for pid in pids:
            subprocess.run(["sudo", "kill", pid])
        return True
    except Exception as e:
        logger.warning(f"❌ Could not stop tailscaled: {e}")
        return False

def tailscale_down():
    is_installed = is_tailscale_installed()
    if not is_installed:
        print("❌ Tailscale is not installed.")
        logger.warning("Tailscale disconnect skipped — not installed.")
        return

    mac_gui_flg = is_installed == 'macos-gui'

    os_name = sys.platform
    ts_path = get_tailscale_path()
    cmd = [ts_path, "down"]
    shell_flag = os_name.startswith("win")

    print("🔌 Disconnecting from Tailnet...")

    # 1. Попытка без sudo
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, shell=shell_flag)
        print("✅ Tailscale VPN disconnected (no sudo).")
        logger.info("Tailscale VPN stopped without sudo")

    except subprocess.CalledProcessError as e:
        stderr = e.stderr or ""
        needs_sudo = needs_sudo_retry(stderr, os_name)

        if needs_sudo:
            try:
                sudo_cmd = ["sudo"] + cmd
                subprocess.run(sudo_cmd, check=True, capture_output=True, text=True, stdin=sys.stdin)
                print("✅ Tailscale VPN disconnected (with sudo).")
                logger.info("Tailscale VPN stopped with sudo")
            except subprocess.CalledProcessError as sudo_e:
                print("❌ Failed to disconnect Tailscale with sudo:", sudo_e)
                logger.error(
                    f"Tailscale sudo disconnect failed. OS: {os_name} "
                    f"STDOUT: {sudo_e.stdout} STDERR: {sudo_e.stderr}",
                    exc_info=True
                )
        else:
            print("❌ Failed to disconnect Tailscale:", e)
            logger.error(
                f"Tailscale disconnect failed. OS: {os_name} "
                f"STDOUT: {e.stdout} STDERR: {e.stderr}",
                exc_info=True
            )

    except Exception as e:
        print("❌ Unexpected error while disconnecting Tailscale:", e)
        logger.exception("Unexpected error during Tailscale disconnect")


    if (not mac_gui_flg and os_name.startswith("darwin")) or os_name.startswith("linux"):
        if stop_tailscaled():
            print("🛑 tailscaled process stopped.")
            logger.info("tailscaled daemon process stopped.")
        else:
            print("⚠️ tailscaled was not running or could not be stopped.")


if __name__ == '__main__':
    tailscale_up('test-client', os.getenv("TEST_CLIENT_AUTH_KEY"))
    tailscale_down()
