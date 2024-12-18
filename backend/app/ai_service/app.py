from flask import Flask, jsonify
from threading import Thread
import os

from camera_mock import CameraMock
from inference import YoloInference

app = Flask(__name__)

# Configuration
IMAGES_DIR = "images"       # directory with image_1.png, image_2.png, etc.
WEIGHTS_PATH = "model/best.pt"
OUTPUT_DIR = "inferenced"   # directory to store inferenced images
INTERVAL = 5                # seconds between captures

# Global variable to hold the latest inference result
latest_inference_result = {"info": "No inference done yet"}

# Initialize inference and camera
inference_engine = YoloInference(weights_path=WEIGHTS_PATH, output_dir=OUTPUT_DIR)
camera = CameraMock(images_dir=IMAGES_DIR, interval=INTERVAL)

def process_image(image_path):
    global latest_inference_result
    result, status = inference_engine.run_inference(image_path)
    latest_inference_result = result

def start_camera_loop():
    camera.run_continuous_capture(process_image)

# Start the camera & inference loop in a separate thread
background_thread = Thread(target=start_camera_loop, daemon=True)
background_thread.start()

@app.route('/latest_inferenced', methods=['GET'])
def get_latest_inferenced():
    return jsonify(latest_inference_result), 200

if __name__ == '__main__':
    # Ensure directories exist
    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR, exist_ok=True)
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    app.run(host='0.0.0.0', port=5000, debug=True)
