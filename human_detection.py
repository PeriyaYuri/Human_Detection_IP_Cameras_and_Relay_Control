import cv2
import numpy as np
from threading import Thread
import time

from detector import HumanDetector
from gpio_controller import RelayController
from camera_handler import CameraHandler

class CameraSystem:
    def __init__(self):
        # Initialize components
        self.detector = HumanDetector()
        self.relay_controller = RelayController(
            pin1=17,
            pin2=18,
            duration=5
        )
        
        # Camera URLs
        self.camera_urls = [
            "rtsp://username:password@camera1_ip:554/stream1",
            "rtsp://username:password@camera2_ip:554/stream2"
        ]
        
        # Detection zones
        self.detection_zones = [
            [(100, 100), (500, 400)],  # Zone for camera 1
            [(100, 100), (500, 400)]   # Zone for camera 2
        ]
        
        # Initialize cameras
        self.cameras = [
            CameraHandler(url) for url in self.camera_urls
        ]
        self.frames = [None, None]
        self.running = True
        
    def setup_camera(self, camera_index):
        """Setup and maintain camera connection"""
        while self.running:
            if not self.cameras[camera_index].connect():
                time.sleep(5)  # Wait before retry
                
    def process_camera(self, camera_index):
        """Process camera feed and detect humans"""
        camera = self.cameras[camera_index]
        zone = self.detection_zones[camera_index]
        
        while self.running:
            try:
                frame = camera.read_frame()
                if frame is None:
                    time.sleep(1)
                    continue
                
                # Draw detection zone
                cv2.rectangle(frame, zone[0], zone[1], (0, 255, 0), 2)
                
                # Detect humans
                boxes = self.detector.detect_humans(frame, zone)
                
                if boxes:
                    # Person detected
                    cv2.putText(
                        frame,
                        f"Person Detected - Camera {camera_index + 1}",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 0, 255),
                        2
                    )
                    
                    # Activate relay
                    self.relay_controller.activate_relay(camera_index)
                    
                    # Draw detection boxes
                    self.detector.draw_detections(frame, boxes, zone)
                
                # Add timestamp
                camera.add_timestamp(frame)
                self.frames[camera_index] = frame
                
            except Exception as e:
                print(f"Error processing camera {camera_index + 1}: {str(e)}")
                time.sleep(1)
                
    def display_frames(self):
        """Display camera feeds"""
        while self.running:
            try:
                if all(frame is not None for frame in self.frames):
                    combined_frame = np.hstack((self.frames[0], self.frames[1]))
                    cv2.imshow('Camera Feeds', combined_frame)
                    
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.running = False
                    
            except Exception as e:
                print(f"Error displaying frames: {str(e)}")
                time.sleep(1)
                
    def run(self):
        """Run the camera system"""
        try:
            # Start camera setup threads
            camera_setup_threads = [
                Thread(target=self.setup_camera, args=(i,))
                for i in range(2)
            ]
            
            # Start camera processing threads
            camera_process_threads = [
                Thread(target=self.process_camera, args=(i,))
                for i in range(2)
            ]
            
            # Start display thread
            display_thread = Thread(target=self.display_frames)
            
            # Start all threads
            for thread in camera_setup_threads + camera_process_threads + [display_thread]:
                thread.start()
            
            # Wait for threads to finish
            for thread in camera_setup_threads + camera_process_threads + [display_thread]:
                thread.join()
                
        except KeyboardInterrupt:
            print("Shutting down...")
        finally:
            self.cleanup()
            
    def cleanup(self):
        """Cleanup system resources"""
        self.running = False
        # Release cameras
        for camera in self.cameras:
            camera.release()
        # Cleanup GPIO
        self.relay_controller.cleanup()
        # Close all windows
        cv2.destroyAllWindows()

if __name__ == "__main__":
    system = CameraSystem()
    system.run()