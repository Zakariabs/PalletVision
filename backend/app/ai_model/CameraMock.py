import os
import time
import random

class CameraMock:
    def __init__(self, images_dir, interval=5):
        """
        images_dir: Directory containing images to simulate camera captures.
        interval: Time in seconds between each "capture".
        """
        self.images_dir = images_dir
        self.interval = interval
        self.image_files = [
            f for f in os.listdir(images_dir) 
            if os.path.isfile(os.path.join(images_dir, f))
        ]

    def start_stream(self):
        """
        Simulate a continuous stream of images from the camera.
        This generator yields a path to a random image every 'interval' seconds.
        """
        while True:
            if not self.image_files:
                yield None
            else:
                img = random.choice(self.image_files)
                yield os.path.join(self.images_dir, img)
            time.sleep(self.interval)

### Usage
# from camera_mock import CameraMock

# cam = CameraMock(images_dir="backend/app/ai_model/dataset/test_images")
# for image_path in cam.start_stream():
#     # Integrate image_path with inference or other logic
#     print("New image captured:", image_path)
