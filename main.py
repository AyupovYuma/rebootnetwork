#!/usr/bin/env python3

import subprocess
import time
import os
from datetime import datetime

PING_HOST = "8.8.8.8"
PING_COUNT = 2
CHECK_INTERVAL = 60  # секунд
RESTART_THRESHOLD = 3
REBOOT_THRESHOLD = 10
FAIL_FILE = "/var/tmp/net_fail_count.txt"
REBOOT_FILE = "/var/tmp/last_reboot.txt"
REBOOT_TIMEOUT = 3600  # секунд


def ping_ok():
    return subprocess.call(["ping", "-c", str(PING_COUNT), PING_HOST],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0


def get_default_interface():
    try:
        output = subprocess.check_output(["ip", "route"]).decode()
        for line in output.splitlines():
            if line.startswith("default"):
                return line.split()[4]
    except:
        pass
    return None


def restart_services(interface):
    print(f"[INFO] Перезапуск сервисов для интерфейса {interface}...")
    subprocess.call(["systemctl", "restart", "NetworkManager"])

    # Опционально: ручной перезапуск интерфейса
    subprocess.call(["ip", "link", "set", interface, "down"])
    time.sleep(2)
    subprocess.call(["ip", "link", "set", interface, "up"])


def reboot_system():
    print("[CRITICAL] Перезагрузка системы...")
    with open(REBOOT_FILE, "w") as f:
        f.write(str(int(time.time())))
    subprocess.call(["reboot"])


def time_since_last_reboot():
    if not os.path.exists(REBOOT_FILE):
        return REBOOT_TIMEOUT + 1
    try:
        with open(REBOOT_FILE) as f:
            last = int(f.read().strip())
            return time.time() - last
    except:
        return REBOOT_TIMEOUT + 1


def read_fail_count():
    if os.path.exists(FAIL_FILE):
        try:
            with open(FAIL_FILE) as f:
                return int(f.read().strip())
        except:
            pass
    return 0


def write_fail_count(count):
    with open(FAIL_FILE, "w") as f:
        f.write(str(count))


def main():
    while True:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if ping_ok():
            print(f"[{now}] Интернет доступен.")
            write_fail_count(0)
        else:
            print(f"[{now}] Потеря соединения.")
            count = read_fail_count() + 1
            write_fail_count(count)

            interface = get_default_interface()
            print(f"[INFO] Активный интерфейс: {interface or 'не определён'}")

            if count >= REBOOT_THRESHOLD:
                if time_since_last_reboot() > REBOOT_TIMEOUT:
                    reboot_system()
                else:
                    print("[WARN] Пропущена перезагрузка (слишком скоро).")
            elif count >= RESTART_THRESHOLD:
                if interface:
                    restart_services(interface)
                else:
                    print("[ERROR] Не удалось определить интерфейс.")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
