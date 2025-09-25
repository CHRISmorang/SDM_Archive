import serial
import time
import glob
import os


def find_usb_ports():
    """Find all USB ports"""
    if os.name != 'nt':  # Unix-like system
        ports = glob.glob('/dev/tty.usb*') + \
            glob.glob('/dev/ttyUSB*') + glob.glob('/dev/tty.*')
    else:  # Windows
        ports = ['COM%s' % (i + 1) for i in range(256)]
    return ports


def test_port(port, baudrate=9600):
    """Test serial communication with a port"""
    try:
        print(f"\nTesting port: {port}")
        with serial.Serial(port=port, baudrate=baudrate, timeout=2) as ser:
            # Wait for Arduino to reset
            time.sleep(2)

            # Clear any existing data
            ser.flushInput()

            # Send handshake command
            print("Sending HANDSHAKE command...")
            ser.write(b'HANDSHAKE\n')

            # Read response
            response = ser.readline().decode('utf-8').strip()
            print(f"Response: {response}")

    except Exception as e:
        print(f"Error testing port {port}: {e}")


def main():
    """Main function to test all ports"""
    print("USB Port Tester")
    print("==============")

    ports = find_usb_ports()
    print(f"\nFound ports: {ports}")

    for port in ports:
        test_port(port)


if __name__ == "__main__":
    main()
