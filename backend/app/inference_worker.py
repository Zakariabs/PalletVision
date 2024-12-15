
from datetime import datetime, timezone

import numpy as np
import requests
from PIL import Image, ImageDraw

from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

from sqlalchemy import func, create_engine
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import sessionmaker

from models import *
import os
import time
load_dotenv()


app = Flask(__name__)
CORS(app)
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
app.session = session


def process_image(image_path,session):

    API_KEY = os.getenv("API_KEY")
    url = f"https://detect.roboflow.com/pallet-detection-bpx8m-vz3n2/1?api_key={API_KEY}"
    start_date = datetime.now(timezone.utc)
    print(image_path)
    os.path.relpath("images/")
    inferred_image_path = None
    with open(f"{image_path}","rb") as img_file:
        result = requests.post(url, files={"file": img_file}).json()


        if result["predictions"]:
            pallet_class = result["predictions"][0]["class"]
            pallet_type = session.query(PalletType).filter(
                func.lower(PalletType.name) == pallet_class.lower()).first()

            if not pallet_type:
                pallet_type = PalletType(name=pallet_class.capitalize())
                session.add(pallet_type)
                session.commit()
            status_id = session.query(Status).filter_by(name="Done").first().id

            image = Image.open(f"{image_path}")
            image = image.convert("RGB")
            image = np.array(image)
            if result["predictions"]:
                prediction_image = Image.fromarray(image)
                draw = ImageDraw.Draw(prediction_image)
                for pred in result["predictions"]:
                    x = pred["x"]
                    y = pred["y"]
                    width = pred["width"]
                    height = pred["height"]
                    left = x - width / 2
                    top = y - height / 2
                    right = x + width / 2
                    bottom = y + height / 2
                    draw.rectangle([left, top, right, bottom], outline="red", width=2)
                print("image path pre inferred: ", image_path)
                inferred_image_path = image_path.split("/",1)[0] + "/inferenced/"+image_path.split("/",1)[1]
            else:
                prediction_image = Image.fromarray(image)
        else:
            pallet_type = session.query(PalletType).filter_by(name="Other").first()
            status_id = session.query(Status).filter_by(name="Error").first().id


        try:
            existing_request = session.query(InferenceRequest).filter_by(
                station_id=1,
                initial_image_path='app/ai_model/dataset/test_images/' +image_path.split("/",1)[1],
                inferred_image_path='app/ai_model/dataset/test_images/inferenced/inferenced_' +image_path.split("/",1)[1],
                request_creation=start_date,
                status_id=status_id,
                pallet_type_id=pallet_type.id
            ).one()
            print(f"Entry already exists: {existing_request}")
        except NoResultFound:
            # Insert new entry if it doesn't exist
            inference_request = InferenceRequest(
                station_id=1,
                initial_image_path='app/ai_model/dataset/test_images/' +image_path.split("/",1)[1],
                inferred_image_path='app/ai_model/dataset/test_images/inferenced/inferenced_' +image_path.split("/",1)[1],
                request_creation=start_date,
                answer_time=datetime.now(timezone.utc),
                status_id=status_id,
                confidence_level=result["predictions"][0]["confidence"] if result["predictions"] else 0.0,
                pallet_type_id=pallet_type.id,
            )
            session.add(inference_request)
            session.commit()
            print(f"Processing image: {image_path}")

def check_for_new_images(folder_path, processed_files,session):
    for filename in os.listdir(folder_path):
        if filename.endswith(('.png', '.jpg', '.jpeg')) and filename not in processed_files:
            image_path = os.path.join(folder_path, filename)
            process_image(image_path,session)
            processed_files.add(filename)
def run_inference_worker(session):
    folder_to_watch = os.path.relpath("images/")

    processed_files = set()
    while True:
        check_for_new_images(folder_to_watch, processed_files,session)
        time.sleep(5)  # Check every 5 seconds

if __name__ == "__main__":

    run_inference_worker(session)
