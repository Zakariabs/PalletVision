import json
import os
import random
from datetime import datetime, timezone, timedelta

from flask import jsonify
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError



def add_initial_values(session):
    from models.models import PalletType, StationStatus, Station, User, Status

    if not session.query(PalletType).filter_by(name='euro').first():
        epal = PalletType(name='euro')
        other = PalletType(name='Other')
        session.add(epal)
        session.add(other)

    statuses = ['Done', 'Processing', 'Error']
    for status in statuses:
        if not session.query(Status).filter_by(name=status).first():
            session.add(Status(name=status))

    station_statuses = ['Ready', 'Offline', 'Processing']
    for status in station_statuses:
        if not session.query(StationStatus).filter_by(name=status).first():
            session.add(StationStatus(name=status))


    offline_status = session.query(StationStatus).filter_by(name="Offline").first()
    if not offline_status:
        return jsonify({'message': 'Invalid status name'}), 400

    if not session.query(Station).filter_by(name="Warehouse Gold").first():
        session.add(Station(name="Warehouse Gold",location="Leipzig",station_status_id=offline_status.id))

    if not session.query(User).filter_by(username="admin").first():
        new_user = User(username="admin")
        new_user.set_password("admin123")
        session.add(new_user)
    session.commit()


def seed_database(session):
    from models.models import PalletType, StationStatus, Station, User, Status, InferenceRequest
    try:
        # Initial statuses and types
        station_statuses = ['Offline', 'Ready', 'Processing']
        statuses = ['Done', 'Processing', 'Error']
        pallet_types = ['EPAL', 'Other']

        for status in station_statuses:
            if not session.query(StationStatus).filter_by(name=status).first():
                session.add(StationStatus(name=status))

        for status in statuses:
            if not session.query(Status).filter_by(name=status).first():
                session.add(Status(name=status))

        for pallet_type in pallet_types:
            if not session.query(PalletType).filter_by(name=pallet_type).first():
                session.add(PalletType(name=pallet_type))

        session.commit()

        # Add stations
        offline_status = session.query(StationStatus).filter_by(name="Offline").first()
        stations = [
            {"name": "Station A", "location": "Location A", "station_status_id": offline_status.id},
            {"name": "Station B", "location": "Location B", "station_status_id": offline_status.id},
            {"name": "Station C", "location": "Location C", "station_status_id": offline_status.id},
        ]
        for station_data in stations:
            if not session.query(Station).filter_by(name=station_data["name"]).first():
                session.add(Station(**station_data))


        # Add users
        user_data = [
            {"username": "admin", "password": "admin123"},
            {"username": "manager", "password": "manager123"},
        ]
        for user in user_data:
            if not session.query(User).filter_by(username=user["username"]).first():
                new_user = User(username=user["username"])
                new_user.set_password(user["password"])
                session.add(new_user)

        session.commit()

        # Images for inference requests
        initial_image_dir = "app/ai_model/dataset/test_images"
        inferred_image_dir = "app/ai_model/dataset/test_images/inferenced"

        # Filter `.json` files
        json_files = [f for f in os.listdir(inferred_image_dir) if f.endswith(".json")]

       
        # Fetch all station IDs for inference request
        station_ids = [station.id for station in session.query(Station).all()]  # Fetch all station IDs

        # Generate request creation and answer times
        start_date = datetime.now(timezone.utc) - timedelta(days=45) #not earlier than 45 days ago
        end_date = datetime.now(timezone.utc) #end date now
              
        total_requests = len(json_files)  # Number of requests to seed

        # Generate ordered timestamps
        if total_requests > 0:
            time_interval = (end_date - start_date) / total_requests  # Evenly spaced intervals
            ordered_timestamps = [start_date + i * time_interval for i in range(total_requests)]

            for i in range(len(ordered_timestamps)): #add random noise to timestamps
                ordered_timestamps[i] += timedelta(seconds=random.randint(-3600, 3600))  # +/- 1 hour
            ordered_timestamps.sort()  # Ensure timestamps are still ordered

            # Assign these timestamps during seeding
            for idx, file in enumerate(json_files):
                with open(os.path.join(inferred_image_dir, file)) as f:
                    data = json.load(f)
            
                # Assign ordered timestamp
                request_creation = ordered_timestamps[idx]
                answer_time = request_creation + timedelta(seconds=random.uniform(0.5, 3)) 
        
                #add image to requets
                initial_image_name = f'image_{file.split("_")[-1].split(".")[0]}.png'
                inferred_image_name = f'inferenced_image_{file.split("_")[-1].split(".")[0]}.png'   

                # Ensure images exist
                if not os.path.exists(os.path.join(initial_image_dir, initial_image_name)) or \
                        not os.path.exists(os.path.join(inferred_image_dir, inferred_image_name)):
                    print(f"Skipping request {file} due to missing image: {initial_image_name} or {inferred_image_name}")
                    continue

                # Determine the pallet type and request status
                if data["predictions"]:
                    pallet_class = data["predictions"][0]["class"]
                    pallet_type = session.query(PalletType).filter(func.lower(PalletType.name) == pallet_class.lower()).first() # Compare normalized names
                    # If the pallet type does not exist, add it to the database
                    if not pallet_type:
                        pallet_type = PalletType(name=pallet_class.capitalize()) # Normalize the name
                        session.add(pallet_type)
                        session.commit()
                    status_id = session.query(Status).filter_by(name="Done").first().id
                else: # If no predictions are made assume type = "Other" and status = "Failed"
                    pallet_type = session.query(PalletType).filter_by(name="Other").first()
                    status_id = session.query(Status).filter_by(name="Error").first().id

                # Randomly assign a station ID from available stations
                random_station_id = random.choice(station_ids)


                inference_request = InferenceRequest(
                    station_id=random_station_id,  # Randomly assign a station
                    initial_image_path = f"http://localhost:5000/images/{initial_image_name}",
                    inferred_image_path = f"http://localhost:5000/images/inferenced/{inferred_image_name}",

                    request_creation=request_creation,
                    answer_time=answer_time,
                    status_id=status_id,
                    confidence_level=data["predictions"][0]["confidence"] if data["predictions"] else 0.0,
                    pallet_type_id=pallet_type.id,
                )
                session.add(inference_request)

        session.commit()
        print("Database seeded successfully!")

    except IntegrityError: # Catch IntegrityError exceptions if data already exists
        session.rollback()
        print("Database already seeded or duplicate entry detected. Skipping this step...")
