from change_detection import detect_new_object, capture_reference_frame
from time import sleep

# Capture the reference frame before checking for new objects
capture_reference_frame()

while True:
    if detect_new_object(0.01):
        print("🔴 Object detected, camera released!")
        break  # Stop loop after detection
    else:
        print("✅ No new object detected")

    sleep(5)  # Check every 1 second
