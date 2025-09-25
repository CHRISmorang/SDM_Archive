import time
from datetime import datetime
import cv2
import os
from openai import OpenAI
import base64

# Replace with your OpenAI API key
os.environ['OPENAI_API_KEY'] = 'your-openai-api-key'

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


def encode_image_to_base64(image_path):
    """Convert image to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def find_camera():
    """
    Find available camera ports
    Returns the first working camera port number
    """
    max_ports = 20  # Maximum number of ports to check

    for port in range(max_ports):
        try:
            cap = cv2.VideoCapture(port)
            if cap.isOpened():
                success = cap.read()[0]  # Only get the return status
                if success:
                    print(f"Found working camera at port {port}")
                    cap.release()
                    return port
            cap.release()
        except:
            continue

    raise RuntimeError("No working camera found!")


def capture_image():
    """Capture image from USB camera and downscale to 720p"""
    try:
        # Find camera port
        camera_port = find_camera()

        # Initialize camera with found port
        cap = cv2.VideoCapture(camera_port)

        if not cap.isOpened():
            raise RuntimeError("Could not open camera")

        # Wait for camera to initialize
        time.sleep(2)

        # Capture frame
        ret, frame = cap.read()
        if not ret:
            raise RuntimeError("Could not capture frame")

        # Downscale image to 640x360
        frame_resized = cv2.resize(frame, (640, 360))

        # Ensure 'images' folder exists
        if not os.path.exists('images'):
            os.makedirs('images')

        # Save two copies of the image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        analysis_filename = os.path.join("images", f"capture_{timestamp}.jpg")
        cv2.imwrite(analysis_filename, frame_resized)

        base_folder_file = os.path.join(os.getcwd(), 'last_item.png')
        cv2.imwrite(base_folder_file, frame_resized)

        return analysis_filename

    except Exception as e:
        print(f"Camera error: {e}")
        return None

    finally:
        if 'cap' in locals():
            cap.release()


def analyze_waste(image_path):
    """Analyze waste image using OpenAI Vision API"""
    try:
        # Convert image to base64
        base64_image = encode_image_to_base64(image_path)

        # Prepare the messages for the API
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """Analyze this image and provide a JSON response in exactly this format:
                        {
                            "Category": "one of: ['Bio Degradable and Recyclable', 'Bio Degradable and Non Recyclable', 'Non Bio Degradable and Recyclable', 'Non Bio Degradable and Non Recyclable']",
                            "Item": "name of the object",
                            "Recyclable tips": "how it can be recycled (if recyclable, else null)",
                            "Bio degradable facts": "how it is biodegradable (if biodegradable, else explain how harmful it is for environment)"
                        }
                        """
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=messages,
            max_tokens=1000
        )

        # Clean up captured image
        os.remove(image_path)

        return response.choices[0].message.content

    except Exception as e:
        print(f"Error analyzing image: {e}")
        if os.path.exists(image_path):
            os.remove(image_path)
        return None


def get_trash_classification():
    """Main function to capture and analyze waste"""
    try:
        # Capture image from camera
        image_path = capture_image()

        # Analyze the captured image
        result = analyze_waste(image_path)

        if result:
            return result
        else:
            return "Error: Could not analyze waste"

    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    # Test the system
    result = get_trash_classification()
    print(result)
