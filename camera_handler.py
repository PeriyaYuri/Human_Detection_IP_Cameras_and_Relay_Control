import cv2
import time
from datetime import datetime

class CameraHandler:
    def __init__(self, url):
        self.url = url
        self.camera = None
        
    def connect(self):
        """Connect to the camera"""
        try:
            self.camera = cv2.VideoCapture(self.url)
            if not self.camera.isOpened():
                raise Exception("Failed to open camera")
            return True
        except Exception as e:
            print(f"Camera connection error: {str(e)}")
            if self.camera is not None:
                self.camera.release()
                self.camera = None
            return False
            
    def read_frame(self):
        """Read frame from camera"""
        if self.camera is None:
            return None
            
        ret, frame = self.camera.read()
        if not ret:
            return None
        return frame
        
    def add_timestamp(self, frame):
        """Add timestamp to frame"""
        cv2.putText(
            frame,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            (10, frame.shape[0] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1
        )
        
    def release(self):
        """Release camera resources"""
        if self.camera is not None:
            self.camera.release()
            self.camera = None