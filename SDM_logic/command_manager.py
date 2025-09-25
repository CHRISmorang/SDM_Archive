from arduino_port_finder import get_arduino_ports
import serial
import time
import json
import subprocess


class CommandManager:
    def __init__(self):
        """Initialize serial connections to both Arduinos"""
        try:
            # Run arduino_port_finder.py and wait for completion
            print("Running port finder...")
            subprocess.run(['python3', 'arduino_port_finder.py'], check=True)
            print("Port finder completed")

            # Read the saved port configuration
            with open('arduino_ports.json', 'r') as f:
                data = json.load(f)
                self.stepper_port = data['stepper_port']
                self.mechanism_port = data['mechanism_port']

            if not self.stepper_port or not self.mechanism_port:
                raise ConnectionError("Could not find one or both Arduinos")

            # Initialize serial connections
            self.arduino1 = serial.Serial(self.stepper_port, 9600, timeout=1)
            self.arduino2 = serial.Serial(self.mechanism_port, 9600, timeout=1)

            # Wait for connections to establish
            time.sleep(2)

            print(f"Connected to stepper at {self.stepper_port}")
            print(f"Connected to mechanism at {self.mechanism_port}")

        except Exception as e:
            print(f"Error during initialization: {e}")
            self.close()  # Close any open connections
            raise

    def send_command(self, arduino, command):
        """Send a command to the specified Arduino"""
        try:
            arduino.write(f"{command}\n".encode())
            arduino.flush()  # Ensure command is sent
            response = arduino.readline().decode().strip()
            return response
        except serial.SerialException as e:
            print(f"Error sending command: {e}")
            return None

    # Mechanism Commands (Handled by arduino2)
    def open_br(self):
        """Open Biodegradable & Recyclable bin"""
        print("Opening BR bin command sent")
        return self.send_command(self.arduino2, "BR")

    def open_bnr(self):
        """Open Biodegradable & Non-Recyclable bin"""
        print("Opening BNR bin command sent")
        return self.send_command(self.arduino2, "BNR")

    def open_nbr(self):
        """Open Non-Biodegradable & Recyclable bin"""
        print("Opening NBR bin command sent")
        return self.send_command(self.arduino2, "NBR")

    def open_nbnr(self):
        """Open Non-Biodegradable & Non-Recyclable bin"""
        print("Opening NBNR bin command sent")
        return self.send_command(self.arduino2, "NBNR")

    def get_sensor_data(self):
        """Send request once and wait for valid sensor data before proceeding."""
        print("Sending sensor data request...")
        try:
            # Set a shorter timeout for the request
            self.arduino2.timeout = 1
            self.send_command(self.arduino2, "GETD")  # Send request only once

            print("Waiting for sensor data...")
            start_time = time.time()
            timeout = 5  # 5 second timeout

            while (time.time() - start_time) < timeout:
                if self.arduino2.in_waiting > 0:  # Check if data is available
                    response = self.arduino2.readline().decode().strip()  # Read available data
                    if response:
                        try:
                            # Convert to integers
                            values = [int(x) for x in response.split(',')]
                            print("Received sensor data:", values)
                            return values  # Return list of integers
                        except ValueError:
                            print("Invalid sensor data received, retrying...")
                time.sleep(0.1)  # Small delay to prevent excessive CPU usage

            # If we get here, we timed out
            print("Timeout waiting for sensor data")
            return None

        except Exception as e:
            print(f"Error getting sensor data: {e}")
            return None
        finally:
            # Reset timeout to default
            self.arduino2.timeout = 1

    def reset_disk(self):
        """Reset disk position"""
        print("Reset disk command sent")
        return self.send_command(self.arduino2, "disk_reset")

    def flush_bins(self):
        """Flush all bins"""
        print("Flush bins command sent")
        return self.send_command(self.arduino2, "FLUSH")

    def restart_mechanism(self):
        """Restart mechanism"""
        print("Restart mechanism command sent")
        return self.send_command(self.arduino2, "RESTART")

    # Stepper Commands (Handled by arduino1)
    def run_stepper(self):
        """Run stepper motor"""
        print("Run stepper command sent")
        return self.send_command(self.arduino1, "COMPRESS")

    def close(self):
        """Close serial connections"""
        try:
            if hasattr(self, 'arduino1'):
                self.arduino1.close()
            if hasattr(self, 'arduino2'):
                self.arduino2.close()
        except serial.SerialException as e:
            print(f"Error closing connections: {e}")


def test_all_functions():
    """Test all commands in sequence"""
    try:
        # Create command manager instance
        cmd = CommandManager()

        print("\nTesting serial connection restart...")
        try:
            # Close connections
            print("Closing serial connections...")
            cmd.close()
            time.sleep(1)

            # Reinitialize connections
            print("Restarting serial connections...")
            cmd = CommandManager()
            print("Serial connections restarted successfully")

        except Exception as e:
            print(f"Error during serial restart: {e}")
            return

        # Test mechanism commands
        print("\nTesting mechanism...")
        print("Sensor data:", cmd.get_sensor_data())

        print("\nTesting bins:")
        print("Directed to BR bin", cmd.open_br())
        time.sleep(2)
        print("Directed to BNR bin", cmd.open_bnr())
        time.sleep(2)
        print("Directed to NBR bin", cmd.open_nbr())
        time.sleep(2)
        print("Directed to NBNR bin", cmd.open_nbnr())
        time.sleep(2)

        print("\nTesting system commands:")
        print("Reset disk:", cmd.reset_disk())
        time.sleep(1)
        print("Flush bins:", cmd.flush_bins())
        time.sleep(2)
        print("Restart mechanism:", cmd.restart_mechanism())

    except Exception as e:
        print(f"Error during testing: {e}")

    finally:
        # Ensure connections are closed
        if 'cmd' in locals():
            cmd.close()


if __name__ == "__main__":
    test_all_functions()
