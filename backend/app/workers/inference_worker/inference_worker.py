import os

import PIL.Image
from inference_sdk import InferenceHTTPClient
from dotenv import load_dotenv

load_dotenv()
CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key=os.getenv("API_KEY")
)

result = CLIENT.infer("../../../data/incoming/image_1.png", model_id="pallet-detection-bpx8m-vz3n2/1")
print(result)


# Run Flask App
if __name__ == "__main__":

    print(result)
    # CLIENT.infer("../../../ai_model/dataset/test_images/image_1.png", model_id="pallet-detection-bpx8m-vz3n2/1")
# pick up image din data/incoming
# move image to data/output
#insert inference entry in db with empty end timestamp and empty inference image
# inference is done, use result to update db entry, draw the localization on start image to generate inferred image



import os
import time

def process_image(image_path):
    print(f"Processing image: {image_path}")
    # Add your image processing code here

def check_for_new_images(folder_path, processed_files):
    for filename in os.listdir(folder_path):
        if filename.endswith(('.png', '.jpg', '.jpeg')) and filename not in processed_files:
            image_path = os.path.join(folder_path, filename)
            process_image(image_path)
            processed_files.add(filename)

if __name__ == "__main__":
    folder_to_watch = "path/to/your/folder"
    processed_files = set()

    while True:
        check_for_new_images(folder_to_watch, processed_files)
        time.sleep(5)  # Check every 5 seconds
