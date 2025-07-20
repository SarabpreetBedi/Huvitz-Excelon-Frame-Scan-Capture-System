#!/usr/bin/env python3
"""
Camera Test Script for Huvitz Excelon System
Helps diagnose camera connection issues
"""

import cv2
import numpy as np
import time

def test_cameras():
    """Test all available cameras"""
    print("Testing Camera Connections...")
    print("=" * 40)
    
    working_cameras = []
    
    # Test first 5 camera indices
    for i in range(5):
        print(f"\nTesting camera index {i}...")
        try:
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                print(f"  ✓ Camera {i} opened successfully")
                
                # Try to read a frame
                ret, frame = cap.read()
                if ret:
                    print(f"  ✓ Camera {i} can read frames")
                    print(f"  ✓ Frame size: {frame.shape}")
                    working_cameras.append(i)
                    
                    # Try to get camera properties
                    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    print(f"  ✓ Resolution: {width}x{height}, FPS: {fps}")
                else:
                    print(f"  ✗ Camera {i} opened but cannot read frames")
                
                cap.release()
            else:
                print(f"  ✗ Camera {i} failed to open")
                
        except Exception as e:
            print(f"  ✗ Error testing camera {i}: {e}")
    
    print(f"\n{'='*40}")
    print(f"Summary: {len(working_cameras)} working camera(s) found")
    if working_cameras:
        print(f"Working cameras: {working_cameras}")
    else:
        print("No working cameras found!")
        print("\nTroubleshooting tips:")
        print("1. Check if USB video capture device is connected")
        print("2. Verify device drivers are installed")
        print("3. Try different USB ports")
        print("4. Check Windows Device Manager for camera devices")
    
    return working_cameras

def test_specific_camera(camera_index):
    """Test a specific camera with live preview"""
    print(f"\nTesting camera {camera_index} with live preview...")
    print("Press 'q' to quit, 's' to save a test image")
    
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"Failed to open camera {camera_index}")
        return
    
    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    frame_count = 0
    start_time = time.time()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame")
            break
        
        frame_count += 1
        
        # Calculate FPS
        elapsed_time = time.time() - start_time
        fps = frame_count / elapsed_time if elapsed_time > 0 else 0
        
        # Add text to frame
        cv2.putText(frame, f"Camera {camera_index} - FPS: {fps:.1f}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, "Press 'q' to quit, 's' to save", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        cv2.imshow(f'Camera {camera_index} Test', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            filename = f"camera_{camera_index}_test.jpg"
            cv2.imwrite(filename, frame)
            print(f"Saved test image: {filename}")
    
    cap.release()
    cv2.destroyAllWindows()

def main():
    """Main test function"""
    print("Huvitz Excelon Camera Test Utility")
    print("=" * 40)
    
    # Test all cameras
    working_cameras = test_cameras()
    
    if working_cameras:
        print(f"\nWould you like to test a specific camera?")
        print(f"Available cameras: {working_cameras}")
        
        try:
            choice = input("Enter camera index (or press Enter to skip): ").strip()
            if choice and choice.isdigit():
                camera_index = int(choice)
                if camera_index in working_cameras:
                    test_specific_camera(camera_index)
                else:
                    print(f"Camera {camera_index} is not available")
            else:
                print("Skipping live camera test")
        except KeyboardInterrupt:
            print("\nTest cancelled by user")
    else:
        print("\nNo cameras available for live testing")

if __name__ == "__main__":
    main() 