import os
from ultralytics import YOLO
from PIL import Image, ImageDraw


class YoloInference:
    def __init__(self, weights_path, output_dir="inferenced"):
        if not os.path.isfile(weights_path):
            raise FileNotFoundError(f"Model weights not found at {weights_path}")
        self.model = YOLO(weights_path)
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)

    def run_inference(self, image_path):
        if not os.path.isfile(image_path):
            return {"error": "Image not found"}, 404

        # Run inference using the new API
        results = self.model(image_path)
        
        # Process the first result (since we're only processing one image)
        result = results[0]
        
        # Open the original image for drawing
        pil_img = Image.open(image_path).convert("RGB")
        draw = ImageDraw.Draw(pil_img)

        detections = []
        if result.boxes:  # Check if there are any detections
            for box in result.boxes:
                # Get confidence
                conf = float(box.conf[0])
                # Get coordinates
                x1, y1, x2, y2 = box.xyxy[0].tolist()

                # Draw bounding box
                draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
                
                # Create simplified confidence label
                label = f"{conf:.2%}"
                
                # Measure text size
                text_bbox = draw.textbbox((0, 0), label)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]

                # Draw label background and text
                draw.rectangle([x1, y1 - text_height - 2, x1 + text_width, y1], fill="red")
                draw.text((x1, y1 - text_height - 2), label, fill="white")

                detections.append({
                    "confidence": conf,
                    "box": [x1, y1, x2, y2]
                })

        # Save output image
        output_filename = f"inferenced_{os.path.basename(image_path)}"
        output_path = os.path.join(self.output_dir, output_filename)
        pil_img.save(output_path)

        if not detections:
            return {"error": "No pallet detected", "output_path": output_path}, 404

        return {
            "inferenced_image_path": output_path,
            "detections": detections
        }, 200