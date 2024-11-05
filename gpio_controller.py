import RPi.GPIO as GPIO
import time
from threading import Thread

class RelayController:
    def __init__(self, pin1, pin2, duration):
        self.RELAY_PIN_1 = pin1
        self.RELAY_PIN_2 = pin2
        self.relay_duration = duration
        
        # Initialize GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.RELAY_PIN_1, GPIO.OUT)
        GPIO.setup(self.RELAY_PIN_2, GPIO.OUT)
        
    def control_relay(self, relay_pin):
        """Control relay with specified duration"""
        GPIO.output(relay_pin, GPIO.HIGH)
        time.sleep(self.relay_duration)
        GPIO.output(relay_pin, GPIO.LOW)
        
    def activate_relay(self, camera_index):
        """Activate relay for specified camera in a separate thread"""
        relay_pin = self.RELAY_PIN_1 if camera_index == 0 else self.RELAY_PIN_2
        Thread(target=self.control_relay, args=(relay_pin,)).start()
        
    def cleanup(self):
        """Cleanup GPIO resources"""
        GPIO.cleanup()