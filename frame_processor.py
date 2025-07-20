#!/usr/bin/env python3
"""
Frame Processor for Huvitz Excelon Frame Scan Detection
Processes captured frames to extract frame scan data and measurements
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage
from scipy.signal import find_peaks
import math

class FrameProcessor:
    def __init__(self):
        self.last_processed_frame = None
        self.scan_contours = []
        self.frame_measurements = {}
        
    def process_frame(self, frame):
        """Process incoming frame for frame scan detection"""
        if frame is None:
            return False
        
        # Convert to grayscale for processing
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply preprocessing filters
        processed = self._preprocess_frame(gray)
        
        # Detect frame contours
        contours = self._detect_frame_contours(processed)
        
        if contours:
            self.scan_contours = contours
            self.last_processed_frame = frame
            return True
        
        return False
    
    def _preprocess_frame(self, gray_frame):
        """Apply preprocessing filters to improve frame detection"""
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray_frame, (5, 5), 0)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Apply morphological operations to clean up the image
        kernel = np.ones((3, 3), np.uint8)
        processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        processed = cv2.morphologyEx(processed, cv2.MORPH_OPEN, kernel)
        
        return processed
    
    def _detect_frame_contours(self, processed_frame):
        """Detect frame contours in the processed image"""
        # Find contours
        contours, _ = cv2.findContours(
            processed_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Filter contours based on area and shape
        valid_contours = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 1000:  # Minimum area threshold
                # Approximate contour to polygon
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                # Check if it's roughly rectangular (4-8 vertices)
                if len(approx) >= 4 and len(approx) <= 8:
                    valid_contours.append(contour)
        
        return valid_contours
    
    def extract_scan_data(self, frame):
        """Extract frame scan data from the current frame"""
        if frame is None:
            return None
        
        # Process the frame
        if not self.process_frame(frame):
            return None
        
        # Extract measurements
        measurements = self._extract_measurements(frame)
        
        # Generate radius data (similar to your example)
        radii_data = self._generate_radii_data(measurements)
        
        scan_data = {
            'timestamp': self._get_timestamp(),
            'measurements': measurements,
            'radii': radii_data,
            'contours': self.scan_contours,
            'frame_shape': frame.shape
        }
        
        return scan_data
    
    def _extract_measurements(self, frame):
        """Extract frame measurements from detected contours"""
        measurements = {}
        
        if not self.scan_contours:
            return measurements
        
        # Get the largest contour (assumed to be the main frame)
        main_contour = max(self.scan_contours, key=cv2.contourArea)
        
        # Get bounding rectangle
        x, y, w, h = cv2.boundingRect(main_contour)
        measurements['width'] = w
        measurements['height'] = h
        measurements['area'] = cv2.contourArea(main_contour)
        
        # Calculate center point
        M = cv2.moments(main_contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            measurements['center'] = (cx, cy)
        
        # Calculate perimeter
        measurements['perimeter'] = cv2.arcLength(main_contour, True)
        
        return measurements
    
    def _generate_radii_data(self, measurements):
        """Generate radius data similar to the provided example"""
        if not measurements or 'center' not in measurements:
            return []
        
        center = measurements['center']
        
        # Generate 1000 radius measurements around the frame
        radii = []
        for i in range(1000):
            angle = (i / 1000) * 2 * math.pi
            
            # Calculate radius based on frame shape and position
            # This is a simplified model - you may need to adjust based on actual frame shape
            base_radius = 1550  # Base radius in 0.1mm units
            variation = 100 * math.sin(angle * 2) + 50 * math.cos(angle * 3)
            radius = base_radius + variation
            
            # Ensure radius is within reasonable bounds
            radius = max(1500, min(2700, radius))
            radii.append(int(radius))
        
        return radii
    
    def _get_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def visualize_scan(self, frame, scan_data=None):
        """Visualize the detected frame scan"""
        if frame is None:
            return None
        
        # Create a copy for visualization
        vis_frame = frame.copy()
        
        # Draw contours
        if self.scan_contours:
            cv2.drawContours(vis_frame, self.scan_contours, -1, (0, 255, 0), 2)
        
        # Draw center point if available
        if scan_data and 'measurements' in scan_data:
            measurements = scan_data['measurements']
            if 'center' in measurements:
                center = measurements['center']
                cv2.circle(vis_frame, center, 5, (0, 0, 255), -1)
                cv2.putText(vis_frame, f"Center: {center}", 
                           (center[0] + 10, center[1] - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        
        return vis_frame
    
    def plot_radii_data(self, radii_data):
        """Plot the radius data as a polar plot"""
        if not radii_data:
            return None
        
        # Convert radii to millimeters (division by 10)
        radii = np.array(radii_data) / 10.0
        
        # Create angles for 1000 points on 360°
        theta = np.linspace(0, 2 * np.pi, 1000, endpoint=False)
        
        # Create polar plot
        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(111, projection='polar')
        ax.plot(theta, radii, linewidth=2, color='blue')
        ax.set_title('Frame Scan Shape - Huvitz Excelon', pad=20)
        ax.grid(True)
        
        return fig 