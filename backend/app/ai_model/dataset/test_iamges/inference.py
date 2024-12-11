import os
import base64
import requests
import json
from PIL import Image, ImageDraw
import io

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def send_to_roboflow(base64_image):
    url = "https://detect.roboflow.com/pallet-detection-bpx8m-vz3n2/1"
    params = {"api_key": "ltNnn4L5T3cwHjssyn3z"}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    response = requests.post(url, params=params, data=base64_image, headers=headers)
    return response.json()

def draw_boxes(image_path, predictions):
    # Open the image
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    
    # Draw each prediction box
    for prediction in predictions:
        x1 = prediction['x'] - prediction['width'] / 2
        y1 = prediction['y'] - prediction['height'] / 2
        x2 = prediction['x'] + prediction['width'] / 2
        y2 = prediction['y'] + prediction['height'] / 2
        
        # Draw rectangle
        draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
        
        # Draw label
        label = f"{prediction['class']} ({prediction['confidence']:.2f})"
        draw.text((x1, y1-15), label, fill="red")
    
    return image

def process_directory(input_dir=".", output_dir="inferenced"):
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    # Process each image in the directory
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, f"inferenced_{filename}")
            
            try:
                # Encode and send image
                base64_image = encode_image_to_base64(input_path)
                result = send_to_roboflow(base64_image)
                
                # Save the prediction results as JSON
                with open(output_path.replace('.jpg', '.json').replace('.png', '.json'), 'w') as f:
                    json.dump(result, f, indent=2)
                
                # Draw boxes and save image
                if 'predictions' in result:
                    image_with_boxes = draw_boxes(input_path, result['predictions'])
                    image_with_boxes.save(output_path)
                
                print(f"Processed: {filename}")
            except Exception as e:
                print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    process_directory()