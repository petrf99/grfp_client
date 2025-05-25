import subprocess
import time
import sys
import os
from pathlib import Path

from client.front.front import main as front_main

def main():
    # Запускаем бэк
    print("[LAUNCHER] Starting backend...")
    back_proc = subprocess.Popen(
        ["python", "-m", "client.back.back"],  # Запуск бэка (можно путь к python указать)
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    try:
        # Запускаем фронт — он останется в терминале
        print("[LAUNCHER] Starting frontend...")
        #front_main() 
        subprocess.run(["python", "-m", "client.front.front"], close_fds=True)  # здесь ты можешь заменить на electron . / npm run start

    except KeyboardInterrupt:
        print("[LAUNCHER] Ctrl+C — exiting frontend...")

    finally:
        print("[LAUNCHER] Frontend finished. Backend should shut down on its own.")
        time.sleep(3)  # даём бэку время завершиться
        if back_proc.poll() is None:
            print("[LAUNCHER] Backend still alive — killing for safety.")
            back_proc.terminate()
            try:
                back_proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                print("[LAUNCHER] Backend did not exit — killing hard.")
                back_proc.kill()

if __name__ == "__main__":
    main()
