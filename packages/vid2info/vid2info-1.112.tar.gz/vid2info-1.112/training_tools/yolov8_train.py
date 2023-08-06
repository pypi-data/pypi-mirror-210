from ultralytics import YOLO

# Load a pretrained YOLO model (recommended for training)
model = YOLO('C:\\Code\\vid2info\\vid2info\\inference\\models\\segmentation\\yolov8n-seg.pt')


# Train the model using the 'coco128.yaml' dataset for 3 epochs
results = model.train(data='C:\\Code\\vid2info\\training_tools\\datasets\\instance-cooking-segmentation\\images\\val', epochs=3)

print(results)