import io
import os
from google.cloud import vision
from google.cloud.vision_v1 import types
from PIL import Image, ImageDraw

# Set up authentication
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "sdm-ai-449411-3c3407f9fc88.json"


def detect_objects(image_path):
    """Detects objects in an image using Google Cloud Vision API."""
    client = vision.ImageAnnotatorClient()

    # Read image
    with io.open(image_path, "rb") as image_file:
        content = image_file.read()
    image = vision.Image(content=content)

    # Perform object detection
    response = client.object_localization(image=image)
    objects = response.localized_object_annotations

    print("Objects detected:")
    for obj in objects:
        print(f"{obj.name} ({obj.score * 100:.2f}% confidence)")

    return objects


def draw_objects(image_path, objects):
    """Draw bounding boxes around detected objects."""
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    for obj in objects:
        vertices = [(vertex.x * image.width, vertex.y * image.height)
                    for vertex in obj.bounding_poly.normalized_vertices]
        draw.polygon(vertices, outline="red", width=3)

    image.show()  # Show image with bounding boxes


def test_api():
    client = vision.ImageAnnotatorClient()

    image = vision.Image()
    image.source.image_uri = "https://upload.wikimedia.org/wikipedia/commons/6/60/Toy_train_2.JPG"

    response = client.object_localization(image=image)

    if response.localized_object_annotations:
        print("API is working. Objects detected:")
        for obj in response.localized_object_annotations:
            print(f"{obj.name} ({obj.score * 100:.2f}% confidence)")
    else:
        print("No objects detected.")


if __name__ == "__main__":
    img_path = "input.png"
    detected_objects = detect_objects(img_path)
    draw_objects(img_path, detected_objects)
    test_api()
