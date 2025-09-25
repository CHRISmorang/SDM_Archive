import serial
import time
import serial.tools.list_ports
import json
import os

CONFIG_FILE = 'arduino_ports.json'


def list_all_ports():
    """List all available COM ports"""
    # First try the standard way
    ports = list(serial.tools.list_ports.comports())

    # If no ports found and on Unix-like system, try direct device listing
    if not ports and os.name != 'nt':  # not Windows
        try:
            import glob
            # Only check tty.* devices
            usb_ports = sorted(glob.glob('/dev/tty.*'), reverse=True)
            print("\nFound USB ports through direct search:")
            for port in usb_ports:
                print(f"Port: {port}")
            # Convert to list_ports format
            ports = [serial.tools.list_ports_common.ListPortInfo(
                port) for port in usb_ports]
        except Exception as e:
            print(f"Error searching USB ports: {e}")

    # Reverse the port list to check from last to first
    ports = list(reversed(ports))

    print("\nAvailable ports:")
    for port in ports:
        print(f"Port: {port.device}, Description: {
              port.description}, Hardware ID: {port.hwid}")

    return ports


def save_port_config(stepper_port, mechanism_port):
    """Save port configuration to file"""
    config = {
        'stepper_port': stepper_port,
        'mechanism_port': mechanism_port
    }
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)
    print(f"Configuration saved to {CONFIG_FILE}")


def load_port_config():
    """Load port configuration from file"""
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            return config['stepper_port'], config['mechanism_port']
    except (FileNotFoundError, json.JSONDecodeError):
        return None, None


def verify_port(port, expected_response, baudrate=9600, timeout=1):
    """Verify if a port responds with expected handshake"""
    print(f"\nTrying port {port}...")
    try:
        with serial.Serial(port=port, baudrate=baudrate, timeout=timeout) as ser:
            time.sleep(1.5)  # Reduced delay for Arduino reset
            ser.flushInput()
            print("Sending HANDSHAKE command...")
            ser.write(b'HANDSHAKE\n')
            response = ser.readline().decode('utf-8').strip()
            print(f"Response from {port}: {response}")
            return response == expected_response
    except Exception as e:
        print(f"Error on port {port}: {e}")
        return False


def get_arduino_ports():
    """
    Get Arduino ports by checking all available ports.
    Returns:
        tuple: (stepper_port, mechanism_port)
    """
    print("\nDetecting Arduino ports...")
    arduino_ports = {
        'ARDUINO1': None,  # Stepper
        'ARDUINO2': None   # Mechanism
    }

    # List all available ports in reverse order
    available_ports = list_all_ports()

    if not available_ports:
        print("No COM ports found! Please check Arduino connections.")
        return None, None

    # Try each port
    for port in available_ports:
        if 'Bluetooth' in port.device:  # Skip Bluetooth ports
            print(f"\nSkipping Bluetooth port: {port.device}")
            continue

        try:
            print(f"\nTesting port: {port.device}")
            ser = serial.Serial(port=port.device, baudrate=9600, timeout=1)

            # Wait for Arduino to reset
            time.sleep(1.5)

            # Clear input buffer
            ser.reset_input_buffer()

            # Send handshake
            print("Sending HANDSHAKE command...")
            ser.write(b'HANDSHAKE\n')
            ser.flush()  # Ensure command is sent

            # Read response
            response = ser.readline().decode('utf-8').strip()
            print(f"Raw response received: '{response}'")

            if response == "ARDUINO1" and not arduino_ports['ARDUINO1']:
                arduino_ports['ARDUINO1'] = port.device
                print(f"Found ARDUINO1 (Stepper) at {port.device}")
            elif response == "ARDUINO2" and not arduino_ports['ARDUINO2']:
                arduino_ports['ARDUINO2'] = port.device
                print(f"Found ARDUINO2 (Mechanism) at {port.device}")

            # Close the connection
            ser.close()

        except Exception as e:
            print(f"Error testing port {port.device}: {e}")
            if 'ser' in locals():
                ser.close()
            continue

        # Print current status after each port
        print("\nCurrent status:")
        print(f"ARDUINO1: {arduino_ports['ARDUINO1']}")
        print(f"ARDUINO2: {arduino_ports['ARDUINO2']}")

        # Exit if both found
        if arduino_ports['ARDUINO1'] and arduino_ports['ARDUINO2']:
            print("Both Arduinos found! Stopping search.")
            break

    stepper_port = arduino_ports['ARDUINO1']
    mechanism_port = arduino_ports['ARDUINO2']

    # Print final results
    print("\nFinal Port Detection Results:")
    print(f"Stepper Arduino (ARDUINO1): {stepper_port or 'Not Found'}")
    print(f"Mechanism Arduino (ARDUINO2): {mechanism_port or 'Not Found'}")

    if stepper_port and mechanism_port:
        save_port_config(stepper_port, mechanism_port)
        print("Port configuration saved")
    else:
        print("\nWarning: Could not find one or both Arduinos")
        print("Please check:")
        print("1. Arduino connections")
        print("2. Arduino power")
        print("3. Correct firmware upload")
        print("4. USB ports")

    return stepper_port, mechanism_port


if __name__ == "__main__":
    print("Arduino Port Finder")
    print("==================")

    # Try to load existing configuration
    saved_stepper, saved_mechanism = load_port_config()
    if saved_stepper and saved_mechanism:
        print("\nFound saved configuration:")
        print(f"Stepper Port: {saved_stepper}")
        print(f"Mechanism Port: {saved_mechanism}")
        print("\nVerifying saved ports...")

        # Verify saved ports still work
        if verify_port(saved_stepper, "ARDUINO1") and verify_port(saved_mechanism, "ARDUINO2"):
            print("\nSaved ports verified successfully!")
            exit(0)
        else:
            print("\nSaved ports not responding, searching for new ports...")

    # Search for new ports
    stepper_port, mechanism_port = get_arduino_ports()
