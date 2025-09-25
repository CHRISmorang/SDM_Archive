from command_manager import CommandManager
from change_detection import detect_new_object, capture_reference_frame
from vision import get_trash_classification
import json
import time
import sys
import os


def restart_program():
    """Restart the entire program"""
    print("\nRestarting system...")
    time.sleep(2)  # Wait before restart
    python = sys.executable
    os.execl(python, python, *sys.argv)


def update_database(result_data):
    """Update data_base.txt with latest detection at the top"""
    try:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

        # Get current sensor values from command manager
        cmd = CommandManager()
        sensor_data = cmd.get_sensor_data()

        # Use sensor data if available, otherwise use defaults
        if sensor_data and len(sensor_data) == 4:
            br_value = str(sensor_data[0])
            bnr_value = str(sensor_data[1])
            nbr_value = str(sensor_data[2])
            nbnr_value = str(sensor_data[3])
        else:
            br_value = '00'
            bnr_value = '00'
            nbr_value = '00'
            nbnr_value = '00'

        # Read existing content
        existing_lines = []
        if os.path.exists('data_base.txt') and os.path.getsize('data_base.txt') > 0:
            with open('data_base.txt', 'r') as f:
                existing_lines = f.readlines()

        # Create new data entry with updated sensor values
        new_data = (
            f"Dustbin Code: BIN001, "
            f"Dustbin Location: New Student Activity Center (New SAC), "
            f"BR: {br_value}, "
            f"BNR: {bnr_value}, "
            f"NBR: {nbr_value}, "
            f"NBNR: {nbnr_value}, "
            f"Last used: {timestamp}, "
            f"Recyclable tips: {result_data.get(
                'Recyclable tips', 'No recycling information available')}, "
            f"Bio degradable facts: {result_data.get(
                'Bio degradable facts', 'No biodegradable information available')}, "
            f"Item: {result_data.get('Item', 'Unknown')}, "
            f"Category: {result_data.get('Category', 'Unknown')}\n"
        )

        # Write new data at the top, followed by existing content
        with open('data_base.txt', 'w') as f:
            f.write(new_data)
            f.writelines(existing_lines)

        print(f"Database updated - Item: {result_data.get('Item', 'Unknown')}, Type: {
              result_data.get('Category', 'Unknown')}")

    except Exception as e:
        print(f"Error updating database: {e}")
        print(f"Current data: {result_data}")


def get_bin_code(category):
    """Convert category text to bin code"""
    category_mapping = {
        "Bio Degradable and Recyclable": "BR",
        "Bio Degradable and Non Recyclable": "BNR",
        "Non Bio Degradable and Recyclable": "NBR",
        "Non Bio Degradable and Non Recyclable": "NBNR"
    }

    # Exact string matching
    return category_mapping.get(category.strip(), None)


def clean_json_string(raw_string):
    """Remove markdown code block and clean the JSON string"""
    # Remove ```json and ``` markers
    cleaned = raw_string.replace('```json', '').replace('```', '').strip()
    return cleaned


def main():
    max_retries = 3
    retry_count = 0

    while True:
        try:
            print("Initializing system...")
            cmd = CommandManager()
            print("Arduino connections established")
            capture_reference_frame()
            retry_count = 0

            while True:
                try:
                    while True:
                        # 0.01 is the threshold for detection
                        if detect_new_object(0.01):
                            print("🔴 Object detected, camera released!")
                            break  # Stop loop after detection
                        else:
                            print("✅ No new object detected")
                        time.sleep(3)  # Check every 1 second

                    print("\nWaiting for trash...")
                    result = get_trash_classification()

                    print("Raw result:", result)
                    print("Result type:", type(result))

                    try:
                        # Clean the JSON string before parsing
                        cleaned_result = clean_json_string(result)
                        result_data = json.loads(cleaned_result)
                        print("Parsed data:", result_data)

                        # Continue with the rest of your code...

                    except json.JSONDecodeError as e:
                        print(f"JSON parsing error: {e}")
                        print(f"Failed to parse: {result}")
                        continue

                    print(f"\nDetected: {result_data['Item']}")
                    print(f"Classification: {result_data['Category']}")

                    # Update database
                    update_database(result_data)

                    # Get bin code from category
                    bin_code = get_bin_code(result_data['Category'])

                    print("Starting compression...")
                    cmd.run_stepper()

                    # Open appropriate bin
                    if bin_code == "BR":
                        print("Directing trash to BR bin")
                        cmd.open_br()
                    elif bin_code == "BNR":
                        print("Directing trash to BNR bin")
                        cmd.open_bnr()
                    elif bin_code == "NBR":
                        print("Directing trash to NBR bin")
                        cmd.open_nbr()
                    elif bin_code == "NBNR":
                        print("Directing trash to NBNR bin")
                        cmd.open_nbnr()

                    # Get bin levels
                    sensor_data = cmd.get_sensor_data()
                    if sensor_data:
                        print(f"Current bin levels: {sensor_data}")

                        # Check if any bin is full (threshold can be adjusted)
                        if max(sensor_data) > 10:  # 10 cm i guess
                            print("Warning: One or more bins need emptying")
                            cmd.flush_bins()

                    # Send RESTART command to reset mechanism
                    print("Resetting mechanism...")
                    cmd.restart_mechanism()

                    # Wait before next detection
                    time.sleep(3)
                    print("\nReady for next item...")

                except Exception as e:
                    print(f"Error in main loop: {e}")
                    retry_count += 1
                    if retry_count >= max_retries:
                        print("Max retries reached. Restarting system...")
                        break
                    time.sleep(2)

        except KeyboardInterrupt:
            print("\nSystem stopped by user")
            break
        except Exception as e:
            print(f"System error: {e}")
            time.sleep(5)
        finally:
            # Clean shutdown
            if 'cmd' in locals():
                cmd.close()
            print("System shutdown complete")


if __name__ == "__main__":
    main()
