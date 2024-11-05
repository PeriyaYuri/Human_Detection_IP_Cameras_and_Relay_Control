from ultralytics import YOLO
import cv2
import numpy as np

class HumanDetector:
    def __init__(self):
        # Initialize YOLO model
        self.model = YOLO('yolov8n.pt')
        
    def detect_humans(self, frame, zone):
        """
        Detect humans in the specified zone of the frame
        Returns: List of detected boxes
        """
        # Extract region of interest
        roi = frame[zone[0][1]:zone[1][1], zone[0][0]:zone[1][0]]
        
        # Run detection
        results = self.model(roi, classes=[0])  # class 0 is person in COCO dataset
        
        # Process results
        detected_boxes = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                if box.conf[0] > 0.5:  # Confidence threshold
                    x1, y1, x2, y2 = box.xyxy[0]
                    detected_boxes.append((
                        int(x1), int(y1),
                        int(x2 - x1), int(y2 - y1)
                    ))
        
        return detected_boxes

    def draw_detections(self, frame, boxes, zone):
        """Draw detection boxes and labels on frame"""
        for (x, y, w, h) in boxes:
            cv2.rectangle(
                frame,
                (zone[0][0] + x, zone[0][1] + y),
                (zone[0][0] + x + w, zone[0][1] + y + h),
                (0, 0, 255),
                2
            )