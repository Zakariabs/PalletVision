from ultralytics import YOLO

# Load a model
model = YOLO("model\\best.pt")  # pretrained YOLO11n model

# Run batched inference on a list of images
results = model(["images/image_1.png", "images/image_2.png"], stream=True)  # return a generator of Results objects

# Process results generator
for result in results:
    boxes = result.boxes  # Boxes object for bounding box output
    # result.show()  # display to screen
    filename = result.path.rsplit("\\",1)[1]
    result.save(filename="inferenced_"+filename)  # save to diskaq