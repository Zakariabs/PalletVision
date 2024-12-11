from ultralytics import YOLO
import torch

# Verify CUDA is available
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"Current device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")

# Load model
model = YOLO("yolo11n.yaml")  

# Train model with GPU
results = model.train(
    data="/home/zakaria/PalletVision/backend/app/ai_model/Pallet Detection.v1i.yolov11/data.yaml", 
    epochs=300, 
    imgsz=640,
    device=0  # Use GPU. Use device='cpu' for CPU
)