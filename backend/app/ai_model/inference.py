import os
import base64
from io import BytesIO
from ultralytics import YOLO
from PIL import Image, ImageDraw, ImageFont

class YoloInference:
    def __init__(self, weights_path):
        """
        weights_path: Path to the YOLOv8 model weights.
        """
        if not os.path.isfile(weights_path):
            raise FileNotFoundError(f"Model weights not found at {weights_path}")
        self.model = YOLO(weights_path)
        
        # Optional: if you have class names, define them here. 
        # Otherwise, it will just say Type_<class_index>.
        # Example: self.class_names = ["TypeA", "TypeB", "TypeC"]
        # Adjust this to match your training labels if available.
        self.class_names = None

    def run_inference(self, image_path):
        """
        Runs inference on the specified image.
        Returns a JSON-friendly dictionary with:
          - base64-encoded image (with bounding boxes)
          - detections list
        """
        if not os.path.isfile(image_path):
            return {"error": "Image not found"}, 404

        # Run inference
        results = self.model.predict(image_path)
        # Get the PIL image
        pil_img = Image.open(image_path).convert("RGB")
        draw = ImageDraw.Draw(pil_img)

        detections = []
        if len(results) > 0 and hasattr(results[0], 'boxes'):
            for box in results[0].boxes:
                c = int(box.cls[0]) if hasattr(box, 'cls') else -1
                # If you have class names, use them, otherwise fallback:
                class_name = self.class_names[c] if (self.class_names and c < len(self.class_names)) else f"Type_{c}"
                conf = float(box.conf[0])
                
                # Box coordinates: xyxy format: [x1, y1, x2, y2]
                coords = box.xyxy[0].tolist() if hasattr(box, 'xyxy') else []
                if len(coords) == 4:
                    x1, y1, x2, y2 = coords
                    # Draw bounding box
                    draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
                    
                    # Optional: draw label above the box
                    label = f"{class_name} {conf:.2f}"
                    # Draw text background
                    text_width, text_height = draw.textsize(label)
                    draw.rectangle([x1, y1 - text_height, x1 + text_width, y1], fill="red")
                    draw.text((x1, y1 - text_height), label, fill="white")
                    
                    detections.append({
                        "class": class_name,
                        "confidence": conf,
                        "box": [x1, y1, x2, y2]
                    })

        if not detections:
            return {"error": "No pallet detected"}, 404

        # Convert PIL image to base64
        buffered = BytesIO()
        pil_img.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

        # Return JSON response with image and detections
        return {
            "inferenced_image": f"data:image/jpeg;base64,{img_str}",
            "detections": detections
        }, 200
