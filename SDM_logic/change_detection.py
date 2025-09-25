import cv2
import numpy as np
import time

# Global variables
reference_frame = None
cap = None  # Global camera instance


def find_camera():
    """Find the first available camera."""
    max_ports = 20  # Maximum number of ports to check

    for port in range(max_ports):  # ✅ Fixed iteration issue
        try:
            test_cap = cv2.VideoCapture(port)
            if test_cap.isOpened():
                success = test_cap.read()[0]  # Check if the camera works
                if success:
                    test_cap.release()
                    return port
            test_cap.release()
        except:
            continue

    raise RuntimeError("❌ No working camera found!")


def init_camera():
    """Initialize the camera only once and keep it open globally."""
    global cap
    if cap is None:
        camera_port = find_camera()
        cap = cv2.VideoCapture(camera_port)
        time.sleep(2)  # Allow camera to stabilize


def capture_reference_frame():
    """Capture a reference frame and preprocess it."""
    global reference_frame, cap

    if cap is None:
        init_camera()  # Ensure the camera is initialized

    ret, frame = cap.read()
    if not ret:
        raise RuntimeError("❌ Could not capture reference frame")

    # Convert to grayscale and apply Gaussian blur
    reference_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    reference_frame = cv2.GaussianBlur(reference_frame, (21, 21), 0)

    print("📸 Reference frame captured!")


def detect_new_object(change_threshold=0.01):
    """
    Detect if a new object has appeared in the frame.

    change_threshold: Determines how much of the frame must change to trigger detection.
                      Example: 0.01 means 1% of the frame must change.
    """
    global reference_frame, cap

    if reference_frame is None:
        raise ValueError(
            "❌ Reference frame not set. Call capture_reference_frame() first.")

    if cap is None:
        init_camera()  # Ensure camera is initialized

    ret, frame = cap.read()
    if not ret:
        return False  # Could not capture a new frame

    # Convert new frame to grayscale and apply Gaussian blur
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_frame = cv2.GaussianBlur(gray_frame, (21, 21), 0)

    # Compute absolute difference between reference frame and new frame
    frame_diff = cv2.absdiff(reference_frame, gray_frame)

    # Apply threshold to highlight differences
    _, thresh = cv2.threshold(
        frame_diff, 25, 255, cv2.THRESH_BINARY)  # Adjusted threshold

    # Compute the change factor (percentage of changed pixels)
    change_factor = np.count_nonzero(
        thresh) / (thresh.shape[0] * thresh.shape[1])

    # Find contours (objects that changed)
    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Debugging: Show processed frames
    cv2.imshow("Frame Difference", frame_diff)
    cv2.imshow("Threshold", thresh)

    # Print debug values
    print(f"Change Factor: {change_factor:.4f}")

    # If change factor is above threshold, check for significant contour area
    if change_factor > change_threshold:
        for contour in contours:
            # Lowered area threshold for better detection
            if cv2.contourArea(contour) > 500:
                print(f"🚨 New object detected! Change Factor: {
                      change_factor:.4f}")
                release_camera()  # Automatically release camera
                return True  # New object detected

    return False  # No new object detected


def release_camera():
    """Gracefully release the camera when done."""
    global cap
    if cap is not None:
        cap.release()
        cap = None
        cv2.destroyAllWindows()
        print("📷 Camera released for other programs.")
