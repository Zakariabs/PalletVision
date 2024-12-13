import os
import json
import random
from datetime import datetime, timedelta, timezone

from app.models import (
    Base, StationStatus, Status, PalletType, Station, User, Image, InferenceRequest
)

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError



# Database Configuration
DATABASE_URL = "postgresql+psycopg2://pallet:pallet@timescaledb:5432/warehouse"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()


# Seed data
def seed_database():
    try:
        # 1. StationStatus
            # station_statuses = ['Offline', 'Ready', 'Processing']
            # for status in station_statuses:
                # if not session.query(StationStatus).filter_by(name=status).first():
                    # session.add(StationStatus(name=status))

        # 2. Status
            # statuses = ['Done', 'Processing', 'Error']
            # for status in statuses:
                # if not session.query(Status).filter_by(name=status).first():
                    # session.add(Status(name=status))

        # 3. PalletType
        pallet_types = ['EPAL', 'Other']
        for pallet_type in pallet_types:
            if not session.query(PalletType).filter_by(name=pallet_type).first():
                session.add(PalletType(name=pallet_type))

        session.commit()

        # 4. Stations (default to Offline)
        offline_status = session.query(StationStatus).filter_by(name="Offline").first()
        stations = [
            {"name": "Station A", "location": "Location A", "station_status_id": offline_status.id},
            {"name": "Station B", "location": "Location B", "station_status_id": offline_status.id},
            {"name": "Station C", "location": "Location C", "station_status_id": offline_status.id},
        ]
        for station_data in stations:
            if not session.query(Station).filter_by(name=station_data["name"]).first():
                session.add(Station(**station_data))


        # 5. Users
        user_data = [
            {"username": "admin", "password": "admin123"},
            {"username": "manager", "password": "manager123"},
        ]
        for user in user_data:
            if not session.query(User).filter_by(username=user["username"]).first():
                new_user = User(username=user["username"])
                new_user.set_password(user["password"])  # Hash the password
                session.add(new_user)

        session.commit()

        # 6. Images
        initial_image_dir = "app/ai_model/dataset/test_images"
        
        inferred_image_dir = "app/ai_model/dataset/test_images/inferenced"
        image_map = {}

        # Add initial images
        for file in os.listdir(initial_image_dir):
            if file.endswith(".png"):
                path = os.path.join(initial_image_dir, file)
                image = Image(path=path)
                session.add(image)
                session.commit()
                image_map[file] = image.id

        # Add inferred images
        for file in os.listdir(inferred_image_dir):
            if file.endswith(".png"):
                path = os.path.join(inferred_image_dir, file)
                image = Image(path=path)
                session.add(image)
                session.commit()
                image_map[file] = image.id

        # 7. InferenceRequests
        json_dir = "app/ai_model/dataset/test_images/inferenced"
        station_ids = [station.id for station in session.query(Station).all()]  # Fetch all station IDs

        for file in os.listdir(json_dir):
            if file.endswith(".json"): #select data from json file only
                with open(os.path.join(json_dir, file)) as f:
                    data = json.load(f)

                    # Get image names
                    initial_image_name = f'image_{file.split("_")[-1].split(".")[0]}.png'
                    inferred_image_name = f'inferenced_image_{file.split("_")[-1].split(".")[0]}.png'

                    # Ensure images exist
                    initial_image_id = image_map.get(initial_image_name)
                    inferred_image_id = image_map.get(inferred_image_name)

                    if initial_image_id is None or inferred_image_id is None:
                        print(f"Skipping request {file} due to missing image: {initial_image_name} or {inferred_image_name}")
                        continue

                    # Generate a random creation time within the last 75 days
                    start_date = datetime.now(timezone.utc) - timedelta(days=75) #not earlier than 75 days ago
                    end_date = datetime.now(timezone.utc) #end date now

                    request_creation = start_date + timedelta(
                        seconds=random.randint(0, int((end_date - start_date).total_seconds()))
                    )
                    # Calculate the answer time
                    answer_time = request_creation + timedelta(seconds=round(data["time"]))

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
                        initial_image_id=image_map.get(initial_image_name),
                        inferred_image_id=image_map.get(inferred_image_name),
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

if __name__ == "__main__":
    seed_database()
