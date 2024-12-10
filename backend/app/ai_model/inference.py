from ultralytics import YOLO
import numpy as np

class PalletDetector:
    def __init__(self, model_path="best.pt"):
        self.model = YOLO(model_path)
        # Map YOLO class indices to pallet types
        self.class_mapping = {
            0: 'euro',
            1: 'wood',
            2: 'plastic'
        }
        
    def detect(self, image):
        results = self.model(image)
        return self._process_results(results[0])
    
    def _process_results(self, result):
        if len(result.boxes) == 0:
            return "No pallet detected"
            
        confidence = result.boxes.conf.cpu().numpy()
        class_ids = result.boxes.cls.cpu().numpy()
        
        max_conf_idx = np.argmax(confidence)
        class_id = int(class_ids[max_conf_idx])
        pallet_class = self.class_mapping.get(class_id, 'unknown')
        conf_score = confidence[max_conf_idx]
        
        return f"{pallet_class} ({conf_score:.2f})"

# Initialize detector as a singleton
detector = PalletDetector()

def infer_pallet_type(preprocessed_image):
    return detector.detect(preprocessed_image)