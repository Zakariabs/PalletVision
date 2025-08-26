import json
import os
from datetime import datetime, timedelta, timezone
from threading import Thread
import logging

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import create_engine, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker, joinedload
from dotenv import load_dotenv

# Import our simplified modules
from database_operations import add_initial_values, seed_database
from models import Base, PalletType, Station, User, InferenceRequest, LogEntry
from ai_inference import PalletInference, CameraMock

load_dotenv()

# Flask app setup
app = Flask(__name__)
CORS(app)

# Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'R2xj$f0dz8ow')
jwt = JWTManager(app)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://pallet:pallet@localhost:5432/warehouse")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)
app.session = session

# AI Inference setup
WEIGHTS_PATH = os.getenv("WEIGHTS_PATH", "/app/ai_service/model/best.pt")
IMAGES_DIR = os.getenv("IMAGES_DIR", "/app/ai_service/images/")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/app/ai_service/inferenced/")

# Initialize AI components if weights exist
inference_engine = None
camera_mock = None
background_thread = None

if os.path.exists(WEIGHTS_PATH):
    try:
        inference_engine = PalletInference(WEIGHTS_PATH, OUTPUT_DIR)
        camera_mock = CameraMock(IMAGES_DIR, interval=10)
        print("AI inference initialized successfully")
    except Exception as e:
        print(f"Failed to initialize AI inference: {e}")
else:
    print(f"Model weights not found at {WEIGHTS_PATH}, running without AI inference")

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
try:
    add_initial_values(session)
    seed_database(session)
    session.commit()
    print("Database initialized successfully")
except Exception as e:
    session.rollback()
    print(f"Database initialization warning: {e}")

# ============= API ENDPOINTS =============

@app.route('/health', methods=['GET'])
def health():
    return 'OK', 200

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    
    user = session.query(User).filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"msg": "Bad username or password"}), 401
    
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)

@app.route('/api/stations', methods=['GET'])
@jwt_required()
def get_stations():
    stations = session.query(Station).all()
    return jsonify([
        {
            "station_id": station.id,
            "station_name": station.name,
            "station_status": station.status,
            "status_class": (
                "text-success" if station.status == "Ready"
                else "text-warning" if station.status == "Processing"
                else "text-danger"
            )
        }
        for station in stations
    ])

@app.route('/api/stations/<int:station_id>', methods=['GET'])
@jwt_required()
def get_station_by_id(station_id):
    station = session.query(Station).filter_by(id=station_id).first()
    if not station:
        return jsonify({'error': 'Station not found'}), 404
    
    return jsonify({
        "station_id": station.id,
        "station_name": station.name,
        "station_status": station.status,
        "status_class": (
            "text-success" if station.status == "Ready"
            else "text-warning" if station.status == "Processing"
            else "text-danger"
        )
    })

@app.route('/api/stations/<int:station_id>/current_image', methods=['GET'])
@jwt_required()
def get_current_image(station_id):
    station = session.query(Station).filter_by(id=station_id).first()
    if not station:
        return jsonify({'error': 'Station not found'}), 404
    
    if station.status == "Offline":
        return jsonify({'image': None})
    
    # Get latest inference request for this station
    request_query = (
        session.query(InferenceRequest)
        .filter_by(station_id=station_id)
        .order_by(InferenceRequest.request_creation.desc())
        .first()
    )
    
    if request_query and request_query.inferred_image_path:
        image_url = f"/images/{os.path.basename(request_query.inferred_image_path)}"
        return jsonify({'image': image_url})
    
    return jsonify({'image': None})

@app.route('/api/stations/<int:station_id>/inference_requests', methods=['GET'])
@jwt_required()
def get_inference_requests_by_station(station_id):
    requests = (
        session.query(InferenceRequest)
        .filter_by(station_id=station_id)
        .order_by(InferenceRequest.request_creation.desc())
        .limit(50)  # Limit for performance
        .all()
    )
    return jsonify([req.to_dict() for req in requests])

@app.route('/api/inference_requests', methods=['GET'])
@jwt_required()
def get_inference_requests():
    requests = session.query(InferenceRequest).order_by(InferenceRequest.request_creation.desc()).limit(100).all()
    return jsonify([req.to_dict() for req in requests])

@app.route('/api/inference_requests', methods=['POST'])
@jwt_required()
def create_inference_request():
    data = request.json
    
    try:
        # Get pallet type
        pallet_type = session.query(PalletType).filter_by(name=data.get('pallet_type', 'EPAL')).first()
        if not pallet_type:
            pallet_type = PalletType(name=data.get('pallet_type', 'Other'))
            session.add(pallet_type)
            session.flush()
        
        # Check for duplicates
        existing_request = session.query(InferenceRequest).filter_by(
            initial_image_path=data['initial_image_path']
        ).first()
        
        if existing_request:
            return jsonify({'error': 'Inference request already exists'}), 400
        
        # Create new request
        new_request = InferenceRequest(
            station_id=data.get('station_id', 1),
            initial_image_path=data['initial_image_path'],
            inferred_image_path=data.get('inferred_image_path'),
            request_creation=datetime.fromisoformat(data['request_creation'].replace('Z', '+00:00')),
            answer_time=datetime.fromisoformat(data['answer_time'].replace('Z', '+00:00')) if data.get('answer_time') else None,
            status=data.get('status', 'Done'),
            confidence_level=data.get('confidence_level', 0.0),
            pallet_type_id=pallet_type.id
        )
        
        session.add(new_request)
        session.commit()
        return jsonify(new_request.to_dict()), 201
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating inference request: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/pallet_count', methods=['GET'])
@jwt_required()
def pallet_count():
    now = datetime.now(timezone.utc)
    seven_days_ago = now - timedelta(days=7)
    thirty_days_ago = now - timedelta(days=30)
    
    last_7_days = (
        session.query(PalletType.name, func.count(InferenceRequest.request_id))
        .join(InferenceRequest, InferenceRequest.pallet_type_id == PalletType.id)
        .filter(InferenceRequest.request_creation >= seven_days_ago)
        .group_by(PalletType.name)
        .all()
    )
    
    last_30_days = (
        session.query(PalletType.name, func.count(InferenceRequest.request_id))
        .join(InferenceRequest, InferenceRequest.pallet_type_id == PalletType.id)
        .filter(InferenceRequest.request_creation >= thirty_days_ago)
        .group_by(PalletType.name)
        .all()
    )
    
    def format_data(data):
        return [{"pallet_type": pallet_type, "count": count} for pallet_type, count in data]
    
    return jsonify({
        "last_7_days": format_data(last_7_days),
        "last_30_days": format_data(last_30_days),
    })

@app.route('/images/<path:filepath>')
def serve_image(filepath):
    """Serve images from the output directory"""
    return send_from_directory(OUTPUT_DIR, filepath)

@app.route('/api/logs', methods=['POST'])
def create_log_entry():
    data = request.json
    log_entry = LogEntry(
        category=data['category'],
        detections=json.dumps(data.get('detections', 'No detections')),
        initial_image=data['initial_image'],
        message=data['message']
    )
    session.add(log_entry)
    session.commit()
    return jsonify({'message': 'Log entry created successfully'}), 201

@app.route('/api/logs', methods=['GET'])
@jwt_required()
def get_all_logs():
    logs = session.query(LogEntry).order_by(LogEntry.timestamp.desc()).limit(100).all()
    return jsonify([log.to_dict() for log in logs])

# ============= AI INFERENCE PROCESSING =============

def process_image(image_path):
    """Process single image with AI inference"""
    if not inference_engine:
        logger.warning("Inference engine not available")
        return
    
    try:
        # Run inference
        result, status_code = inference_engine.run_inference(image_path)
        
        if status_code == 200:
            # Successful detection
            detections = result.get('detections', [])
            if detections:
                detection = detections[0]  # Use first detection
                
                # Create inference request
                inference_request_data = {
                    "station_id": 1,  # Default station
                    "initial_image_path": f"http://localhost:5000/images/{os.path.basename(image_path)}",
                    "inferred_image_path": f"http://localhost:5000/images/{os.path.basename(result['inferenced_image_path'])}",
                    "request_creation": datetime.now(timezone.utc).isoformat(),
                    "answer_time": datetime.now(timezone.utc).isoformat(),
                    "status_id": 1,  # "Done"
                    "confidence_level": detection['confidence'],
                    "pallet_type": detection['class']
                }
                
                # Save to database
                try:
                    with app.app_context():
                        pallet_type = session.query(PalletType).filter_by(name=detection['class']).first()
                        if not pallet_type:
                            pallet_type = PalletType(name=detection['class'])
                            session.add(pallet_type)
                            session.flush()
                        
                        new_request = InferenceRequest(
                            station_id=1,
                            initial_image_path=inference_request_data["initial_image_path"],
                            inferred_image_path=inference_request_data["inferred_image_path"],
                            request_creation=datetime.now(timezone.utc),
                            answer_time=datetime.now(timezone.utc),
                            status="Done",
                            confidence_level=detection['confidence'],
                            pallet_type_id=pallet_type.id
                        )
                        
                        session.add(new_request)
                        session.commit()
                        logger.info(f"Successfully processed image: {image_path}")
                
                except Exception as e:
                    session.rollback()
                    logger.error(f"Database error: {e}")
        else:
            logger.warning(f"No detections in image: {image_path}")
            
    except Exception as e:
        logger.error(f"Error processing image {image_path}: {e}")

def start_inference_worker():
    """Start background inference worker"""
    if camera_mock and inference_engine:
        logger.info("Starting AI inference worker...")
        camera_mock.run_continuous_capture(process_image)
    else:
        logger.warning("AI inference worker not started - missing components")

# Start background processing if available
if inference_engine and camera_mock:
    background_thread = Thread(target=start_inference_worker, daemon=True)
    background_thread.start()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)