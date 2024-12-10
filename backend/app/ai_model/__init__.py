import time
from threading import Thread
import os
from itertools import cycle
import cv2
from .preprocessing import preprocess_image
from .inference import infer_pallet_type

class CameraSimulator:
    def __init__(self, images_dir="test_images"):
        self.images_dir = images_dir
        self.image_files = [os.path.join(images_dir, f) for f in os.listdir(images_dir) 
                           if f.endswith(('.jpg', '.jpeg', '.png'))]
        self.image_cycle = cycle(self.image_files)
        
    def capture_image(self):
        image_path = next(self.image_cycle)
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to load image: {image_path}")
        return image, image_path

def process_and_infer():
    camera = CameraSimulator()
    while True:
        try:
            image, image_path = camera.capture_image()
            preprocessed_image = preprocess_image(image)
            pallet_type = infer_pallet_type(preprocessed_image)
            print(f"Image: {image_path} - Detected pallet type: {pallet_type}")
            time.sleep(10)
        except Exception as e:
            print(f"Error processing image: {str(e)}")

def start_camera_simulation():
    camera_thread = Thread(target=process_and_infer)
    camera_thread.daemon = True
    camera_thread.start()

# Start the camera simulation when the module is imported
if __name__ == "__main__":
    start_camera_simulation()
