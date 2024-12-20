import logging
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify
from threading import Thread
import os

from flask_cors import CORS
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from models import PalletType, Status
from camera_mock import CameraMock
from inference import YoloInference

load_dotenv()

app = Flask(__name__)
CORS(app)
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
app.session = session

# Configuration
IMAGES_DIR = "/app/app/ai_service/images/"       # directory with image_1.png, image_2.png, etc.
WEIGHTS_PATH = "/app/app/ai_service/model/best.pt"
OUTPUT_DIR = "/app/app/ai_service/inferenced/"   # directory to store inferenced images
INTERVAL = 5                # seconds between captures

# Global variable to hold the latest inference result
latest_inference_result = {"info": "No inference done yet"}

# Initialize inference and camera
inference_engine = YoloInference(weights_path=WEIGHTS_PATH, output_dir=OUTPUT_DIR)
camera = CameraMock(images_dir=IMAGES_DIR, interval=INTERVAL)

logger = logging.getLogger(__name__)


class EndpointHandler(logging.Handler):
    def __init__(self, url):
        super().__init__()
        self.url = url

    def emit(self, record):
        log_entry = {
            'category': getattr(record, 'category', 'default_category'),
            'timestamp': getattr(record, 'timestamp', datetime.now().isoformat()),
            'detections': getattr(record, 'detections', 'No detections'),
            'initial_image': getattr(record, 'initial_image', 'No image path'),
            'message': record.getMessage()
        }
        try:
            requests.post(self.url, json=log_entry)
        except Exception as e:
            print(f"Failed to send log entry: {e}")


# Create a logger
logger.setLevel(logging.DEBUG)

# Create an endpoint handler
endpoint_handler = EndpointHandler('http://backend_container:5000/api/logs')
endpoint_handler.setLevel(logging.INFO)

# Add the handler to the logger
logger.addHandler(endpoint_handler)

def process_image(image_path):
    start_req = datetime.now(timezone.utc).isoformat()
    global latest_inference_result
    result, status = inference_engine.run_inference(image_path)

    pallet_type = session.query(PalletType).filter(
        func.lower(PalletType.name) == "euro").first()
    if not pallet_type:
        pallet_type = PalletType(name="euro")
        session.add(pallet_type)
        session.commit()
    status_id = session.query(Status).filter_by(name="Done").first().id

    if status == 200:
        logger.log(logging.INFO, f"Image has been written at {result['inferenced_image_path']}",
                   extra={"category": "inference", "timestamp": datetime.now(timezone.utc).isoformat(),
                          "detections": result['detections'], "initial_image": image_path})
        inference_request = {
                              "answer_time": datetime.now(timezone.utc).isoformat(),
                              "confidence_level": result['detections'][0]['confidence'],
                              "inferred_image_path": result['inferenced_image_path'],
                              "initial_image_path": image_path,
                              "pallet_type": pallet_type.name,
                              "request_creation": start_req,
                              "station_id": 1,
                              "status_id": status_id
}

        requests.post('http://backend_container:5000/api/inference_requests', json=inference_request)
    else:
        logger.log(logging.ERROR, f"No pallets detected in {image_path}",
                   extra={"category": "inference", "timestamp": datetime.now(timezone.utc).isoformat(),
                          "detections": "No pallets detected", "initial_image": image_path})
        inference_request = {
            "answer_time": datetime.now(timezone.utc).isoformat(),
            "confidence_level": 0,
            "inferred_image_path": result['inferenced_image_path'],
            "initial_image_path": image_path,
            "pallet_type": pallet_type.name,
            "request_creation": start_req,
            "station_id": 1,
            "status_id": status_id
        }
        requests.post('http://backend_container:5000/api/inference_requests', json=inference_request)
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

    app.run(host='0.0.0.0', port=5005, debug=True)
