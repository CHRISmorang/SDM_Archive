import cv2
import io
import os
import numpy as np
from google.cloud import vision
from google.cloud.vision_v1 import types
from time import sleep

# Set up Google Cloud Vision API credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "sdm-ai-449411-3c3407f9fc88.json"

# Initialize Google Cloud Vision API client
client = vision.ImageAnnotatorClient()


def detect_objects(frame):
    """Detect objects in a single video frame using Google Cloud Vision API."""
    try:
        # Convert frame to JPEG format
        _, encoded_image = cv2.imencode(".jpg", frame)
        image_content = encoded_image.tobytes()

        # Send image to Google Cloud Vision API
        image = vision.Image(content=image_content)
        response = client.object_localization(image=image)
        objects = response.localized_object_annotations

        return objects
    except Exception as e:
        print(f"Error in object detection: {e}")
        return []


def draw_objects(frame, objects):
    """Draw bounding boxes around detected objects on the frame."""
    height, width, _ = frame.shape
    for obj in objects:
        # Get bounding box coordinates
        vertices = [(int(vertex.x * width), int(vertex.y * height))
                    for vertex in obj.bounding_poly.normalized_vertices]

        # Draw bounding box
        if len(vertices) == 4:
            cv2.rectangle(frame, vertices[0], vertices[2], (0, 255, 0), 2)

        # Put label text
        label = f"{obj.name} ({obj.score * 100:.1f}%)"
        cv2.putText(
            frame, label, vertices[0], cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    return frame


def main():
    """Capture live video and detect objects in real-time."""
    cap = cv2.VideoCapture(0)  # Use external webcam (try index 2 if needed)

    # Force resolution to 640x480
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # ✅ Force FPS to 30
    cap.set(cv2.CAP_PROP_FPS, 30)

    # Verify settings
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"Camera Resolution: {int(width)}x{int(height)} at {fps} FPS")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Error: Unable to capture frame")
            break

        # Detect objects in the frame
        objects = detect_objects(frame)

        # Draw bounding boxes on the frame
        frame = draw_objects(frame, objects)

        # Show the output
        cv2.imshow("Live Object Detection", frame)

        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # sleep(2)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
