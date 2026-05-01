import logging
import os
import shutil
from datetime import datetime, timezone
from threading import Thread

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from camera_mock import CameraMock
from models import Status
from roboflow_classifier import RoboflowClassifier

load_dotenv()

app = Flask(__name__)
CORS(app)
app.config['JWT_SECRET_KEY'] = 'R2xj$f0dz8ow'
jwt = JWTManager(app)
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
app.session = session

# Filesystem layout (shared volume — see docker-compose.yml)
SEED_DIR = "/app/seed_images/"           # read-only, where users drop test inputs
INITIAL_DIR = "/app/images/initial/"     # served by backend at /images/initial/...
OUTPUT_DIR = "/app/images/inferenced/"   # served by backend at /images/inferenced/...
INTERVAL = 5

# Roboflow config
ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY")
ROBOFLOW_PROJECT_ID = os.getenv("ROBOFLOW_PROJECT_ID")
ROBOFLOW_MODEL_VERSION = os.getenv("ROBOFLOW_MODEL_VERSION")
ROBOFLOW_CONFIDENCE_THRESHOLD = float(os.getenv("ROBOFLOW_CONFIDENCE_THRESHOLD", "0.6"))
ROBOFLOW_UPLOAD_ON_LOW_CONF = os.getenv("ROBOFLOW_UPLOAD_ON_LOW_CONF", "true").lower() == "true"

os.makedirs(INITIAL_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

latest_inference_result = {"info": "No inference done yet"}

inference_engine = RoboflowClassifier(
    api_key=ROBOFLOW_API_KEY,
    project_id=ROBOFLOW_PROJECT_ID,
    version=ROBOFLOW_MODEL_VERSION,
    threshold=ROBOFLOW_CONFIDENCE_THRESHOLD,
    output_dir=OUTPUT_DIR,
    upload_low_conf=ROBOFLOW_UPLOAD_ON_LOW_CONF,
)
camera = CameraMock(images_dir=SEED_DIR, interval=INTERVAL)

with app.app_context():
    worker_token = create_access_token(identity='worker_identity')

logger = logging.getLogger(__name__)


class EndpointHandler(logging.Handler):
    def __init__(self, url):
        super().__init__()
        self.url = url

    def emit(self, record):
        log_entry = {
            'category': getattr(record, 'category', 'default_category'),
            'timestamp': getattr(record, 'timestamp', datetime.now(timezone.utc).isoformat()),
            'detections': getattr(record, 'detections', 'No detections'),
            'initial_image': getattr(record, 'initial_image', 'No image path'),
            'message': record.getMessage(),
        }
        try:
            requests.post(self.url, json=log_entry, timeout=5)
        except Exception as exc:
            print(f"Failed to send log entry: {exc}")


logger.setLevel(logging.DEBUG)
endpoint_handler = EndpointHandler('http://backend_container:5000/api/logs')
endpoint_handler.setLevel(logging.INFO)
logger.addHandler(endpoint_handler)


def process_image(seed_path):
    """Copy a seed frame into the shared volume, classify it via Roboflow, then
    persist the result through the backend API."""
    global latest_inference_result
    start_req = datetime.now(timezone.utc).isoformat()

    initial_path = os.path.join(INITIAL_DIR, os.path.basename(seed_path))
    if not os.path.exists(initial_path):
        shutil.copy(seed_path, initial_path)

    result, status = inference_engine.run_inference(initial_path)
    if status != 200:
        logger.log(
            logging.ERROR,
            f"Roboflow inference failed for {initial_path}: {result.get('error')}",
            extra={
                "category": "inference_error",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "detections": result.get('error', 'unknown'),
                "initial_image": initial_path,
            },
        )
        return

    status_id = session.query(Status).filter_by(name="Done").first().id

    inference_request = {
        "answer_time": datetime.now(timezone.utc).isoformat(),
        "confidence_level": result['confidence'],
        "inferred_image_path": result['annotated_image_path'],
        "initial_image_path": initial_path,
        "pallet_type": result['label'],
        "request_creation": start_req,
        "station_id": 1,
        "status_id": status_id,
        "model_version": result['model_version'],
        "flagged_for_review": result['flagged_for_review'],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    headers = {'Authorization': f'Bearer {worker_token}'}
    res = requests.post(
        'http://backend_container:5000/api/inference_requests',
        json=inference_request,
        headers=headers,
        timeout=10,
    )

    if res.status_code == 201:
        logger.log(
            logging.INFO,
            f"Image has been written at {result['annotated_image_path']}",
            extra={
                "category": "inference",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "detections": f"{result['label']} ({result['confidence']:.2%})",
                "initial_image": initial_path,
            },
        )
    elif res.status_code == 400:
        logger.log(
            logging.INFO,
            f"{result['annotated_image_path']} already exists in the db.",
            extra={
                "category": "duplicate_error",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "detections": f"{result['label']} ({result['confidence']:.2%})",
                "initial_image": initial_path,
            },
        )

    latest_inference_result = result


def start_camera_loop():
    camera.run_continuous_capture(process_image)


background_thread = Thread(target=start_camera_loop, daemon=True)
background_thread.start()


@app.route('/latest_inferenced', methods=['GET'])
def get_latest_inferenced():
    return jsonify(latest_inference_result), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)
