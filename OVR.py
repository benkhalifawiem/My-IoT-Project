import os
import hashlib
import requests
import subprocess
import serial.tools.list_ports

# ------------------------------
# USER CONFIGURATION
# ------------------------------

FIRMWARE_URL =  "https://raw.githubusercontent.com/benkhalifawiem/My-IoT-Project/main/firmware/tasmota.bin"
FIRMWARE_FILE = "tasmota.bin"
HASH_FILE = "firmware.hash"


# ------------------------------
# AUTO-INSTALL ESPTOOL IF NEEDED
# ------------------------------

def install_esptool():
    try:
        subprocess.run(["esptool.exe", "--help"], capture_output=True)
        print("✔ esptool is installed.")
    except Exception:
        print("⚠ esptool missing — installing...")
        subprocess.run(["pip", "install", "esptool"])
        print("✔ esptool installed!")


def get_esptool_path():
    try:
        result = subprocess.run(["where", "esptool.exe"], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ esptool.exe not found!")
            return None
        return result.stdout.splitlines()[0]
    except Exception:
        print("❌ Could not locate esptool.exe")
        return None


# ------------------------------
# DETECT ESP8266 COM PORT
# ------------------------------

def detect_com_port():
    print("🔍 Searching for ESP8266 COM port...")
    ports = serial.tools.list_ports.comports()

    for port in ports:
        if "USB" in port.description or "UART" in port.description:
            print(f"✔ ESP8266 detected on {port.device}")
            return port.device

    print("❌ ESP8266 not found! Plug it in and try again.")
    return None


# ------------------------------
# DOWNLOAD FIRMWARE
# ------------------------------

def download_firmware():
    print("⬇ Downloading firmware from GitHub...")

    r = requests.get(FIRMWARE_URL)

    print(f"HTTP Status: {r.status_code}")

    if r.status_code != 200:
        print("❌ Failed to download firmware!")
        return False

    with open(FIRMWARE_FILE, "wb") as f:
        f.write(r.content)

    print("✔ Firmware downloaded.")
    return True


# ------------------------------
# HASH CHECK
# ------------------------------

def file_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def load_last_hash():
    if not os.path.exists(HASH_FILE):
        return None
    with open(HASH_FILE, "r") as f:
        return f.read().strip()


def save_hash(h):
    with open(HASH_FILE, "w") as f:
        f.write(h)


# ------------------------------
# FLASH FIRMWARE
# ------------------------------

def flash_firmware(esptool_path, com_port):
    print("🚀 Flashing ESP8266...")

    cmd = [
        esptool_path,
        "--chip", "esp8266",
        "--port", com_port,
        "--baud", "460800",
        "write_flash",
        "0x00000", FIRMWARE_FILE
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    print(result.stdout)

    if result.returncode == 0:
        print("✔ Flashing completed successfully!")
        return True
    else:
        print("❌ Flashing failed!")
        print(result.stderr)
        return False


# ------------------------------
# MAIN PROGRAM
# ------------------------------

def main():
    print("🚀 ESP8266 Auto-Updater Started\n")

    install_esptool()
    esptool_path = get_esptool_path()

    if not esptool_path:
        print("❌ Cannot continue without esptool.")
        return

    com_port = detect_com_port()
    if not com_port:
        return

    last_hash = load_last_hash()
    print(f"🔍 Last firmware hash: {last_hash}")

    print("⬇ Downloading firmware metadata...")
    r = requests.get(FIRMWARE_URL)

    print("HTTP Status:", r.status_code)

    if r.status_code != 200:
        print("❌ GitHub firmware not found! Check URL.")
        return

    new_hash = hashlib.sha256(r.content).hexdigest()
    print(f"🔍 New firmware hash: {new_hash}")

    if new_hash == last_hash:
        print("✔ No update needed. Firmware is already up-to-date.")
        return

    print("🔥 New firmware version detected!")

    if not download_firmware():
        return

    if flash_firmware(esptool_path, com_port):
        save_hash(new_hash)
        print("🎉 Update completed successfully!")


# ------------------------------
# RUN
# ------------------------------

if _name_ == "_main_":
    main()
