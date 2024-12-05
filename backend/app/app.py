from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, InferenceRequest

app = Flask(__name__)
CORS(app)

DATABASE_URL = "postgresql+psycopg2://pallet:pallet@timescaledb:5432/warehouse"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)
app.session = session

# Register routes
@app.route('/api/inference_requests', methods=['GET'])
def get_inference_requests():
    requests = app.session.query(InferenceRequest).all()
    return jsonify([request.__dict__ for request in requests])

@app.route('/api/inference_requests', methods=['POST'])
def create_inference_request():
    data = request.json
    new_request = InferenceRequest(
        station_id=data['station_id'],
        initial_image_id=data['initial_image_id'],
        inferred_image_id=data.get('inferred_image_id'),
        request_creation=data['request_creation'],
        answer_time=data['answer_time'],
        status_id=data['status_id'],
        confidence_level=data.get('confidence_level'),
        pallet_type=data.get('pallet_type')
    )
    app.session.add(new_request)
    app.session.commit()
    return jsonify(new_request.__dict__), 201

# Swagger UI setup
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Your Flask API"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
