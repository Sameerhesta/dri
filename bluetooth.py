import subprocess
import threading
import time

def enable_and_discoverable():
    try:
        # Use hciconfig to set Bluetooth device to discoverable mode
        subprocess.run(["sudo", "hciconfig", "hci0", "piscan"])

        print("Bluetooth set to discoverable mode.")
    except Exception as e:
        print(f"Error: {e}")

def accept_all_connections():
    try:
        # Use bluetoothctl to set up auto-acceptance of all incoming connections
        subprocess.run(["sudo", "bluetoothctl", "discoverable", "on"])
        subprocess.run(["sudo", "bluetoothctl", "pairable", "on"])
        subprocess.run(["sudo", "hciconfig", "hci0", "class", "0x002580"])

        # Set the Bluetooth device as default (controller alias)
        subprocess.run(["sudo", "bluetoothctl", "default-agent"])
        subprocess.run(["sudo", "hciconfig", "hci0", "name", "MyBluetoothDevice"])

        print("Auto-accepting all incoming connection requests.")
    except Exception as e:
        print(f"Error: {e}")

def main():
    enable_and_discoverable()

    # Start a separate thread for auto-accepting connections
    accept_thread = threading.Thread(target=accept_all_connections)
    accept_thread.start()

    # Run a loop to keep the script alive
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
