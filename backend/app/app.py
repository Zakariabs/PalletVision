import json
import os

import requests
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from sqlalchemy import create_engine, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker, joinedload
from starlette.status import HTTP_201_CREATED
from flasgger import Swagger
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging


from database_operations import add_initial_values
from models.models import Base, PalletType, Station, User, StationStatus,InferenceRequest,LogEntry

load_dotenv()
app = Flask(__name__)
CORS(app)
swagger = Swagger(app, template={
    "swagger": "2.0",
    "info": {
        "title": "PalletVision Service",
        "version": "0.0.1"
    }
})

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)
app.session = session

logger = logging.getLogger(__name__)


class EndpointHandler(logging.Handler):
    def __init__(self, url):
        super().__init__()
        self.url = url

    def emit(self, record):
        log_entry = {
            'category': getattr(record, 'category', 'default_category'),
            'timestamp': getattr(record, 'timestamp', datetime.now()).isoformat(),
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
endpoint_handler = EndpointHandler('http://localhost:5000/api/logs')
endpoint_handler.setLevel(logging.INFO)

# Add the handler to the logger
logger.addHandler(endpoint_handler)
# Helper Function: Add Initial Values
add_initial_values(session)

# seed_database(session)

# Backend API Endpoints
@app.route('/api/inference_requests', methods=['GET'])
def get_inference_requests():
    """
    Get all inference requests
    ---
    responses:
      200:
        description: Returns a list of all inference requests
    """
    requests = app.session.query(InferenceRequest).all()
    return jsonify([request.to_dict() for request in requests])



@app.route('/api/inference_requests', methods=['POST'])
def create_inference_request():
    """
    Create a new inference request
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          id: InferenceRequest
          required:
            - station_id
            - initial_image_path
            - inferred_image_path
            - request_creation
            - answer_time
            - status_id
          properties:
            station_id:
              type: integer
            initial_image_path:
              type: string
            inferred_image_path:
              type: string
            request_creation:
              type: string
              format: date-time
            answer_time:
              type: string
              format: date-time
            status_id:
              type: integer
            confidence_level:
              type: number
              format: float
            pallet_type:
              type: string
    responses:
      201:
        description: The created inference request
    """
    data = request.json
    pallet_type = session.query(PalletType).filter_by(name=data['pallet_type']).first()

    if not pallet_type:
        return jsonify({'message': 'Invalid pallet type name'}), 400
    try:

        existing_request = app.session.query(InferenceRequest).filter_by(
            initial_image_path=data['initial_image_path']).first()
        if existing_request:
            return jsonify({'error': 'Inference request already exists.'}), 400

        # Create a new inference request
        new_request = InferenceRequest(
            station_id=data['station_id'],
            initial_image_path=data['initial_image_path'],
            inferred_image_path=data['inferred_image_path'],
            request_creation=data['request_creation'],
            answer_time=data['answer_time'],
            status_id=data['status_id'],
            confidence_level=data['confidence_level'],
            pallet_type=pallet_type
        )
        app.session.add(new_request)
        app.session.commit()
        return jsonify(new_request.to_dict()), 201
    except IntegrityError as e:
        app.session.rollback()
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        app.session.rollback()
        return jsonify({'error': str(e)}), 500



@app.route('/api/new_installation',methods=['POST'])
def create_new_install():
    """
    Create a new installation
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          required:
            - station_name
            - station_location
            - username
            - password
          properties:
            station_name:
              type: string
            station_location:
              type: string
            username:
              type: string
            password:
              type: string

    responses:
      201:
        description: The created installation
    """
    data = request.json
    offline_status = session.query(StationStatus).filter_by(name="Offline").first()
    if not offline_status:
        return jsonify({'message': 'Invalid status name'}), 400
    new_station = Station(name=data['station_name'],location=data['station_location'],station_status_id=offline_status.id)
    new_user = User(username=data['username'])
    new_user.set_password(data['password'])
    session.add(new_station)
    session.add(new_user)
    session.commit()
    return jsonify({'message': 'New Installation Created', 'id': new_station.id}), HTTP_201_CREATED

@app.route('/api/stations', methods=['GET'])
def get_stations():
    """
    Get all stations
    ---
    responses:
      200:
        description: Returns a list of all stations
    """
    stations = app.session.query(Station).options(joinedload(Station.station_status)).all()

    return jsonify([
        {
          "station_id": station.id, 
          "station_name": station.name,
          "station_status": station.station_status.name,
          "status_class": (
              "text-success" if station.station_status.name == "Ready"
              else "text-warning" if station.station_status.name == "Processing"
              else "text-danger"
          )
        }
        for station in stations
    ])

@app.route('/api/stations/<int:station_id>', methods=['GET'])
def get_station_by_id(station_id):
    """
    Get a specific station by its ID
    ---
    parameters:
      - name: station_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Returns details of a specific station
    """
    station = app.session.query(Station).options(joinedload(Station.station_status)).filter_by(id=station_id).first()
    if not station:
        return jsonify({'error': 'Station not found'}), 404

    return jsonify({
        "station_id": station.id,
        "station_name": station.name,
        "station_status": station.station_status.name if station.station_status else "Unknown",
        "status_class": (
            "text-success" if station.station_status and station.station_status.name == "Ready"
            else "text-warning" if station.station_status and station.station_status.name == "Processing"
            else "text-danger"
        )
    })

@app.route('/api/stations/<int:station_id>/current_image', methods=['GET'])
def get_current_image(station_id):
    """
    Get the current image for a station based on its status
    """
    station = app.session.query(Station).options(joinedload(Station.station_status)).filter_by(id=station_id).first()
    if not station:
        return jsonify({'error': 'Station not found'}), 404

    station_status = station.station_status.name if station.station_status else None

    if station_status == "Offline":
        return jsonify({'image': None})  # No image if offline

    if station_status == "Processing":
        request = (
            app.session.query(InferenceRequest)
            .filter_by(station_id=station_id, answer_time=None)
            .order_by(InferenceRequest.request_creation.desc())
            .first()
        )
        if request and request.initial_image_path:
            return jsonify({'image': f"/images/{os.path.basename(request.initial_image_path)}"})

    request = (
        app.session.query(InferenceRequest)
        .filter(InferenceRequest.station_id == station_id, InferenceRequest.answer_time.isnot(None))
        .order_by(InferenceRequest.answer_time.desc())
        .first()
    )
    if request and request.inferred_image_path:
        return jsonify({'image': f"/images/{os.path.basename(request.inferred_image_path)}"})

    return jsonify({'image': None})


@app.route('/api/stations/<int:station_id>/inference_requests', methods=['GET'])
def get_inference_requests_by_station(station_id):
    """
    Get inference requests for a specific station
    ---
    parameters:
      - name: station_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Returns a list of inference requests for a specific station
    """
    requests = (
        app.session.query(InferenceRequest)
        .filter_by(station_id=station_id)
        .all()
    )
    return jsonify([request.to_dict() for request in requests])

@app.route('/api/pallet_count', methods=['GET'])
def pallet_count():
    """
    Get all list of inference requests from the last 7 and 30 days
    ---
    responses:
      200:
        description: Returns a list of all inference requests over the past 7 and 30 days.
    """
    now = datetime.utcnow()
    seven_days_ago = now - timedelta(days=7)
    thirty_days_ago = now - timedelta(days=30)

    last_7_days = (
        app.session.query(InferenceRequest.pallet_type, func.count(InferenceRequest.request_id))
        .filter(InferenceRequest.request_creation >= seven_days_ago)
        .group_by(InferenceRequest.pallet_type)
        .all()
    )
    last_30_days = (
        app.session.query(InferenceRequest.pallet_type, func.count(InferenceRequest.request_id))
        .filter(InferenceRequest.request_creation >= thirty_days_ago)
        .group_by(InferenceRequest.pallet_type)
        .all()
    )

    def format_data(data):
        pallet_types = {p.id: p.name for p in session.query(PalletType).all()}
        formatted = []
        for pallet_type, count in data:
            pallet_type_name = pallet_types.get(pallet_type)
            formatted.append({"pallet_type": pallet_type_name, "count": count})
        return formatted

    return jsonify({
        "last_7_days": format_data(last_7_days),
        "last_30_days": format_data(last_30_days),
    })

@app.route('/images/<path:filepath>')
def serve_image(filepath):
    """Serve images from the /app/images directory, including subdirectories."""
    return send_from_directory('/app/images', filepath)

@app.route('/api/logs', methods=['POST'])
def create_log_entry():
    """
    Create a new log entry
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          id: LogEntry
          required:
            - category
            - timestamp
            - detections
            - initial_image
            - message
          properties:
            category:
              type: string
              description: The category of the log entry
              example: inference
            timestamp:
              type: string
              format: date-time
              description: The timestamp of the log entry
              example: 2024-12-18T17:45:00Z
            detections:
              type: string
              description: The detections related to the log entry
              example: "Object detected"
            initial_image:
              type: string
              description: The path to the initial image
              example: /path/to/image.jpg
            message:
              type: string
              description: The log message
              example: "Model weights not found"
    responses:
      201:
        description: The created log entry
        schema:
          id: LogEntry
          properties:
            id:
              type: integer
              description: The ID of the log entry
            category:
              type: string
              description: The category of the log entry
            timestamp:
              type: string
              format: date-time
              description: The timestamp of the log entry
            detections:
              type: string
              description: The detections related to the log entry
            initial_image:
              type: string
              description: The path to the initial image
            message:
              type: string
              description: The log message
    """

    data = request.json
    log_entry = LogEntry(
        category=data['category'],
        timestamp=datetime.fromisoformat(data['timestamp']),
        detections=json.dumps(getattr(data, 'detections', 'No detections')),
        initial_image=data['initial_image'],
        message=data['message']
    )
    session.add(log_entry)
    session.commit()
    return jsonify({'message': 'Log entry created successfully'}), 201

@app.route('/api/logs',methods=['GET'])
def get_all_logs():
    """
    Get all logs entries
    ---
    responses:
      200:
        description: Returns a list of all log entries
    """
    logs = app.session.query(LogEntry).all()
    return jsonify([log.to_dict() for log in logs])

@app.route('/health', methods=['GET'])
def health():
    return 'OK', 200

# Run Flask App
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')

