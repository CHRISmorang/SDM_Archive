import serial
import time

def send_command(command):
    """
    Sends a command to Arduino and prints the response.
    
    :param command: Command string entered by the user
    """
    ser.write(f"{command}\n".encode())  # Send command
    ser.flush()  # Ensure command is sent

    while True:
        response = ser.readline().decode('utf-8').strip()  # Read Arduino response
        if response:
            print("Arduino:", response)
        if "completed" in response or "opened" in response or "updated" in response or "emptied" in response:  # Exit on expected response
            break


try:
    # Open Serial Connection
    ser = serial.Serial('COM8', 9600, timeout=1)  # Adjust port if needed
    time.sleep(2)  # Wait for Arduino to initialize

    print("Enter commands to send to Arduino (type 'exit' to quit).")
    
    while True:
        user_input = input("Enter command: ").strip()  # Get user input
        if user_input.lower() == "exit":
            break  # Exit the loop if user types "exit"
        send_command(user_input)

except serial.SerialException as e:
    print(f"Serial Error: {e}")

finally:
    ser.close()  # Close the Serial connection properly

