from ultralytics import YOLO

# Load a model
model = YOLO("backend\app\ai_service\model\best.pt")  # pretrained YOLO11n model

# Run batched inference on a list of images
results = model(["images/image1.jpg", "images/image2.jpg"], stream=True)  # return a generator of Results objects

# Process results generator
for result in results:
    boxes = result.boxes  # Boxes object for bounding box output
    result.show()  # display to screen
    result.save(filename="test_dir/result.jpg")  # save to diskaq