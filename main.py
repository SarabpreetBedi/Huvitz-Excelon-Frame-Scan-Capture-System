#!/usr/bin/env python3
"""
Huvitz Excelon Frame Scan Capture System
Captures frame scan data via VGA/USB adapter and generates OMa files
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import os
import json
from datetime import datetime
from frame_processor import FrameProcessor
from oma_generator import OMAGenerator
from gui import HuvitzGUI

class HuvitzExcelonCapture:
    def __init__(self):
        self.capture = None
        self.is_capturing = False
        self.frame_processor = FrameProcessor()
        self.oma_generator = OMAGenerator()
        self.current_frame = None
        self.scan_data = None
        
    def initialize_camera(self, camera_index=0):
        """Initialize the camera capture device"""
        try:
            self.capture = cv2.VideoCapture(camera_index)
            if not self.capture.isOpened():
                raise Exception(f"Cannot open camera at index {camera_index}")
            
            # Set camera properties for better frame capture
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            self.capture.set(cv2.CAP_PROP_FPS, 30)
            
            return True
        except Exception as e:
            print(f"Error initializing camera: {e}")
            return False
    
    def start_capture(self):
        """Start continuous frame capture"""
        self.is_capturing = True
        self.capture_thread = threading.Thread(target=self._capture_loop)
        self.capture_thread.daemon = True
        self.capture_thread.start()
    
    def stop_capture(self):
        """Stop frame capture"""
        self.is_capturing = False
        if self.capture:
            self.capture.release()
    
    def _capture_loop(self):
        """Main capture loop"""
        while self.is_capturing:
            if self.capture and self.capture.isOpened():
                ret, frame = self.capture.read()
                if ret:
                    self.current_frame = frame
                    # Process frame for frame scan detection
                    self.frame_processor.process_frame(frame)
                else:
                    print("Failed to capture frame")
            time.sleep(0.033)  # ~30 FPS
    
    def capture_scan(self):
        """Capture a single frame scan"""
        if not self.current_frame is not None:
            return None
        
        # Process the current frame for frame scan data
        scan_data = self.frame_processor.extract_scan_data(self.current_frame)
        if scan_data:
            self.scan_data = scan_data
            return scan_data
        return None
    
    def generate_oma_file(self, filename=None):
        """Generate OMa file from captured scan data"""
        if not self.scan_data:
            return None
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scan_{timestamp}.oma"
        
        return self.oma_generator.create_oma_file(self.scan_data, filename)
    
    def get_available_cameras(self):
        """Get list of available camera devices"""
        cameras = []
        for i in range(10):  # Check first 10 camera indices
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                cameras.append(i)
                cap.release()
        return cameras

def main():
    """Main application entry point"""
    app = HuvitzExcelonCapture()
    gui = HuvitzGUI(app)
    gui.run()

if __name__ == "__main__":
    main() 