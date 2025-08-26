import os
import json
from datetime import datetime, timezone
from ultralytics import YOLO
from PIL import Image, ImageDraw


class PalletInference:
    """Unified pallet detection inference service"""
    
    def __init__(self, weights_path, output_dir="inferenced"):
        if not os.path.isfile(weights_path):
            raise FileNotFoundError(f"Model weights not found at {weights_path}")
        
        self.model = YOLO(weights_path)
        self.output_dir = output_dir
        
        # Ensure output directory exists
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
    
    def run_inference(self, image_path):
        """
        Run pallet detection inference on image
        Returns: (result_dict, status_code)
        """
        if not os.path.isfile(image_path):
            return {"error": "Image not found"}, 404
        
        try:
            # Run YOLO inference
            results = self.model(image_path)
            result = results[0]
            
            # Open original image for annotation
            pil_img = Image.open(image_path).convert("RGB")
            draw = ImageDraw.Draw(pil_img)
            
            detections = []
            
            if result.boxes:
                for box in result.boxes:
                    # Extract detection data
                    confidence = float(box.conf[0])
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    class_id = int(box.cls[0]) if hasattr(box, 'cls') else 0
                    
                    # Determine pallet type (simplified)
                    pallet_type = "EPAL" if class_id == 0 else "Other"
                    
                    # Draw bounding box
                    draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
                    
                    # Add confidence label
                    label = f"{pallet_type} {confidence:.2%}"
                    text_bbox = draw.textbbox((0, 0), label)
                    text_width = text_bbox[2] - text_bbox[0]
                    text_height = text_bbox[3] - text_bbox[1]
                    
                    draw.rectangle([x1, y1 - text_height - 2, x1 + text_width, y1], fill="red")
                    draw.text((x1, y1 - text_height - 2), label, fill="white")
                    
                    detections.append({
                        "class": pallet_type,
                        "confidence": confidence,
                        "box": [x1, y1, x2, y2]
                    })
            
            # Save annotated image
            output_filename = f"inferenced_{os.path.basename(image_path)}"
            output_path = os.path.join(self.output_dir, output_filename)
            pil_img.save(output_path)
            
            # Save detection results as JSON
            json_filename = f"inferenced_{os.path.splitext(os.path.basename(image_path))[0]}.json"
            json_path = os.path.join(self.output_dir, json_filename)
            
            result_data = {
                "predictions": detections,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "image_path": image_path,
                "output_path": output_path
            }
            
            with open(json_path, 'w') as f:
                json.dump(result_data, f, indent=2)
            
            if not detections:
                return {
                    "error": "No pallets detected",
                    "inferenced_image_path": output_path,
                    "predictions": []
                }, 404
            
            return {
                "inferenced_image_path": output_path,
                "detections": detections,
                "predictions": detections  # Backward compatibility
            }, 200
            
        except Exception as e:
            return {"error": f"Inference failed: {str(e)}"}, 500


class CameraMock:
    """Simplified camera mock for testing"""
    
    def __init__(self, images_dir, interval=5):
        self.images_dir = images_dir
        self.interval = interval
        self.image_files = [f for f in os.listdir(images_dir) 
                           if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        self.current_index = 0
    
    def get_next_image(self):
        """Get next image path"""
        if not self.image_files:
            return None
        
        image_path = os.path.join(self.images_dir, self.image_files[self.current_index])
        self.current_index = (self.current_index + 1) % len(self.image_files)
        return image_path
    
    def run_continuous_capture(self, callback):
        """Run continuous image processing"""
        import time
        import threading
        
        def process_loop():
            while True:
                image_path = self.get_next_image()
                if image_path:
                    callback(image_path)
                time.sleep(self.interval)
        
        thread = threading.Thread(target=process_loop, daemon=True)
        thread.start()
        return thread