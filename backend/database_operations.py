import json
import os
import random
from datetime import datetime, timezone, timedelta
from sqlalchemy.exc import IntegrityError


def add_initial_values(session):
    """Add initial required data to database"""
    from models import PalletType, Station, User
    
    # Add pallet types
    pallet_types = ['EPAL', 'Other']
    for pallet_type in pallet_types:
        if not session.query(PalletType).filter_by(name=pallet_type).first():
            session.add(PalletType(name=pallet_type))
    
    # Add default station
    if not session.query(Station).filter_by(name="Warehouse Gold").first():
        session.add(Station(name="Warehouse Gold", location="Leipzig", status="Offline"))
    
    # Add default admin user
    if not session.query(User).filter_by(username="admin").first():
        new_user = User(username="admin")
        new_user.set_password("admin123")
        session.add(new_user)
    
    session.commit()


def seed_database(session):
    """Seed database with sample data"""
    from models import PalletType, Station, User, InferenceRequest
    
    try:
        # Add more stations
        stations = [
            {"name": "Station A", "location": "Location A", "status": "Offline"},
            {"name": "Station B", "location": "Location B", "status": "Ready"},
            {"name": "Station C", "location": "Location C", "status": "Processing"},
        ]
        
        for station_data in stations:
            if not session.query(Station).filter_by(name=station_data["name"]).first():
                session.add(Station(**station_data))
        
        # Add more users
        user_data = [
            {"username": "manager", "password": "manager123"},
            {"username": "operator", "password": "operator123"},
        ]
        
        for user in user_data:
            if not session.query(User).filter_by(username=user["username"]).first():
                new_user = User(username=user["username"])
                new_user.set_password(user["password"])
                session.add(new_user)
        
        session.commit()
        
        # Generate sample inference requests if inference results exist
        inference_dir = "backend/app/ai_model/dataset/test_images/inferenced"
        if os.path.exists(inference_dir):
            json_files = [f for f in os.listdir(inference_dir) if f.endswith(".json")]
            station_ids = [station.id for station in session.query(Station).all()]
            
            if json_files and station_ids:
                # Generate timestamps over last 30 days
                start_date = datetime.now(timezone.utc) - timedelta(days=30)
                end_date = datetime.now(timezone.utc)
                
                for i, json_file in enumerate(json_files[:50]):  # Limit to 50 samples
                    try:
                        with open(os.path.join(inference_dir, json_file)) as f:
                            data = json.load(f)
                        
                        # Generate random timestamp
                        time_diff = end_date - start_date
                        random_seconds = random.uniform(0, time_diff.total_seconds())
                        request_time = start_date + timedelta(seconds=random_seconds)
                        answer_time = request_time + timedelta(seconds=random.uniform(0.5, 3))
                        
                        # Determine pallet type and confidence
                        if data.get("predictions"):
                            prediction = data["predictions"][0]
                            pallet_class = prediction.get("class", "Other")
                            confidence = prediction.get("confidence", 0.0)
                            status = "Done"
                        else:
                            pallet_class = "Other"
                            confidence = 0.0
                            status = "Error"
                        
                        # Get or create pallet type
                        pallet_type = session.query(PalletType).filter_by(name=pallet_class).first()
                        if not pallet_type:
                            pallet_type = PalletType(name=pallet_class)
                            session.add(pallet_type)
                            session.flush()
                        
                        # Create inference request
                        image_name = json_file.replace('.json', '.png')
                        inference_request = InferenceRequest(
                            station_id=random.choice(station_ids),
                            initial_image_path=f"http://localhost:5000/images/{image_name}",
                            inferred_image_path=f"http://localhost:5000/images/inferenced_{image_name}",
                            request_creation=request_time,
                            answer_time=answer_time,
                            status=status,
                            confidence_level=confidence,
                            pallet_type_id=pallet_type.id
                        )
                        session.add(inference_request)
                    
                    except Exception as e:
                        print(f"Error processing {json_file}: {e}")
                        continue
        
        session.commit()
        print("Database seeded successfully!")
        
    except IntegrityError:
        session.rollback()
        print("Database already seeded or duplicate entry detected.")
    except Exception as e:
        session.rollback()
        print(f"Error seeding database: {e}")