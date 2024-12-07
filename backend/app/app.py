from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.status import HTTP_201_CREATED
from flasgger import Swagger


from models import Base, InferenceRequest, PalletType, Status, StationStatus, Station, User, Image

app = Flask(__name__)
CORS(app)
swagger = Swagger(app, template={
    "swagger": "2.0",
    "info": {
        "title": "PalletVision Service",
        "version": "0.0.1"
    }
})

DATABASE_URL = "postgresql+psycopg2://pallet:pallet@timescaledb:5432/warehouse"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)
app.session = session

def add_initial_values(session):
    if not session.query(PalletType).filter_by(name='EPAL').first():
        epal = PalletType(name='EPAL')
        session.add(epal)

    statuses = ['Done', 'Processing', 'Error']
    for status in statuses:
        if not session.query(Status).filter_by(name=status).first():
            session.add(Status(name=status))

    station_statuses = ['Ready', 'Offline', 'Processing']
    for status in station_statuses:
        if not session.query(StationStatus).filter_by(name=status).first():
            session.add(StationStatus(name=status))
    session.commit()

add_initial_values(session)


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
            - initial_image_id
            - request_creation
            - answer_time
            - status_id
          properties:
            station_id:
              type: integer
            initial_image_id:
              type: integer
            inferred_image_id:
              type: integer
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
    new_request = InferenceRequest(
        station_id=data['station_id'],
        initial_image_id=data['initial_image_id'],
        inferred_image_id=data['inferred_image_id'],
        request_creation=data['request_creation'],
        answer_time=data['answer_time'],
        status_id=data['status_id'],
        confidence_level=data['confidence_level'],
        pallet_type=pallet_type.id
    )
    app.session.add(new_request)
    app.session.commit()
    return jsonify(new_request), 201



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



@app.route('/api/upload_image',methods=['POST'])
def upload_image():
    """
    Upload image
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            path:
              type: string
    responses:
      201:
        description: Uploaded image
    """
    data = request.json
    uploaded_image = Image(path=data['path'])
    session.add(uploaded_image)
    session.commit()
    return jsonify({'message': 'Image Uploaded', 'id': uploaded_image.id,'path':uploaded_image.path}), HTTP_201_CREATED


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')

