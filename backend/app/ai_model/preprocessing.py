# DEPRECATED — used by the legacy local YOLO pipeline. Roboflow handles preprocessing
# server-side now. Kept alongside train_model.py for offline retraining.
import cv2
import numpy as np

def preprocess_image(image):
    """
    Preprocess image for YOLOv8 inference
    Args:
        image: numpy array from cv2.imread
    Returns:
        preprocessed image
    """
    # Resize image to YOLOv8 input size
    image = cv2.resize(image, (640, 640))
    
    # Convert BGR to RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Normalize pixel values
    image = image.astype(np.float32) / 255.0
    
    return image