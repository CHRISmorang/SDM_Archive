import time
import random


class CommandManager:
    def __init__(self):
        """Initialize test environment without hardware"""
        print("Test Mode: Simulating Arduino connections")
        print("Connected to stepper at TEST_PORT_1")
        print("Connected to mechanism at TEST_PORT_2")
        time.sleep(1)

    def send_stepper_command(self, command):
        """Simulate sending command to stepper Arduino"""
        time.sleep(0.5)
        return f"Stepper received: {command}"

    def send_mechanism_command(self, command):
        """Simulate sending command to mechanism Arduino"""
        time.sleep(0.5)
        return f"Mechanism received: {command}"

    # Mechanism Commands
    def open_br(self):
        """Simulate opening Biodegradable & Recyclable bin"""
        print("Opening BR bin...")
        return self.send_mechanism_command("BR")

    def open_bnr(self):
        """Simulate opening Biodegradable & Non-Recyclable bin"""
        print("Opening BNR bin...")
        return self.send_mechanism_command("BNR")

    def open_nbr(self):
        """Simulate opening Non-Biodegradable & Recyclable bin"""
        print("Opening NBR bin...")
        return self.send_mechanism_command("NBR")

    def open_nbnr(self):
        """Simulate opening Non-Biodegradable & Non-Recyclable bin"""
        print("Opening NBNR bin...")
        return self.send_mechanism_command("NBNR")

    def get_sensor_data(self):
        """Simulate getting sensor readings"""
        return [
            random.randint(0, 100),  # BR
            random.randint(0, 100),  # BNR
            random.randint(0, 100),  # NBR
            random.randint(0, 100)   # NBNR
        ]

    def reset_disk(self):
        """Simulate resetting disk position"""
        print("Resetting disk position...")
        return self.send_mechanism_command("disk_reset")

    def flush_bins(self):
        """Simulate flushing all bins"""
        print("Flushing all bins...")
        return self.send_mechanism_command("FLUSH")

    def restart_mechanism(self):
        """Simulate restarting mechanism"""
        print("Restarting mechanism...")
        return self.send_mechanism_command("RESTART")

    def run_stepper(self):
        """Simulate running stepper motor"""
        print("Running compression cycle...")
        time.sleep(2)
        return self.send_stepper_command("COMPRESS")

    def close(self):
        """Simulate closing connections"""
        print("Closing test connections...")
        time.sleep(0.5)


def test_all_functions():
    """Test all commands in sequence"""
    try:
        cmd = CommandManager()

        print("\nTesting stepper motor...")
        print("Run:", cmd.run_stepper())
        time.sleep(1)

        print("\nTesting mechanism...")
        print("Sensor data:", cmd.get_sensor_data())

        print("\nTesting bins:")
        print("BR bin:", cmd.open_br())
        time.sleep(1)
        print("BNR bin:", cmd.open_bnr())
        time.sleep(1)
        print("NBR bin:", cmd.open_nbr())
        time.sleep(1)
        print("NBNR bin:", cmd.open_nbnr())
        time.sleep(1)

        print("\nTesting system commands:")
        print("Reset disk:", cmd.reset_disk())
        print("Flush bins:", cmd.flush_bins())
        print("Restart mechanism:", cmd.restart_mechanism())

    except Exception as e:
        print(f"Error during testing: {e}")
    finally:
        if 'cmd' in locals():
            cmd.close()


if __name__ == "__main__":
    test_all_functions()
