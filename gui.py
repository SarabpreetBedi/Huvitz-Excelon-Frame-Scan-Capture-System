#!/usr/bin/env python3
"""
GUI for Huvitz Excelon Frame Scan Capture System
Provides a user-friendly interface for capturing and processing frame scans
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import cv2
from PIL import Image, ImageTk
import threading
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class HuvitzGUI:
    def __init__(self, app):
        self.app = app
        self.root = tk.Tk()
        self.root.title("Huvitz Excelon Frame Scan Capture System")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.camera_index = tk.IntVar(value=0)
        self.is_capturing = False
        self.current_frame = None
        self.scan_data = None
        
        # Setup GUI
        self.setup_gui()
        
        # Start camera detection
        self.detect_cameras()
    
    def setup_gui(self):
        """Setup the main GUI layout"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="Huvitz Excelon Frame Scan Capture", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Capture tab
        self.setup_capture_tab(notebook)
        
        # Analysis tab
        self.setup_analysis_tab(notebook)
        
        # Settings tab
        self.setup_settings_tab(notebook)
    
    def setup_capture_tab(self, notebook):
        """Setup the capture tab"""
        capture_frame = ttk.Frame(notebook)
        notebook.add(capture_frame, text="Capture")
        
        # Left panel - Controls
        left_panel = ttk.Frame(capture_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Camera selection
        camera_frame = ttk.LabelFrame(left_panel, text="Camera Settings", padding=10)
        camera_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(camera_frame, text="Camera Index:").pack(anchor=tk.W)
        self.camera_combo = ttk.Combobox(camera_frame, textvariable=self.camera_index, 
                                        state="readonly", width=10)
        self.camera_combo.pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Button(camera_frame, text="Refresh Cameras", 
                  command=self.detect_cameras).pack(anchor=tk.W)
        
        # Capture controls
        capture_frame = ttk.LabelFrame(left_panel, text="Capture Controls", padding=10)
        capture_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.capture_btn = ttk.Button(capture_frame, text="Start Capture", 
                                     command=self.toggle_capture)
        self.capture_btn.pack(fill=tk.X, pady=(0, 5))
        
        self.scan_btn = ttk.Button(capture_frame, text="Capture Scan", 
                                  command=self.capture_scan, state=tk.DISABLED)
        self.scan_btn.pack(fill=tk.X, pady=(0, 5))
        
        self.save_btn = ttk.Button(capture_frame, text="Save OMa File", 
                                  command=self.save_oma_file, state=tk.DISABLED)
        self.save_btn.pack(fill=tk.X, pady=(0, 5))
        
        # Status
        status_frame = ttk.LabelFrame(left_panel, text="Status", padding=10)
        status_frame.pack(fill=tk.X)
        
        self.status_label = ttk.Label(status_frame, text="Ready")
        self.status_label.pack(anchor=tk.W)
        
        # Right panel - Video display
        right_panel = ttk.Frame(capture_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Video display
        video_frame = ttk.LabelFrame(right_panel, text="Live Feed", padding=10)
        video_frame.pack(fill=tk.BOTH, expand=True)
        
        self.video_label = ttk.Label(video_frame, text="No camera feed")
        self.video_label.pack(expand=True)
    
    def setup_analysis_tab(self, notebook):
        """Setup the analysis tab"""
        analysis_frame = ttk.Frame(notebook)
        notebook.add(analysis_frame, text="Analysis")
        
        # Analysis controls
        controls_frame = ttk.Frame(analysis_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(controls_frame, text="Load OMa File", 
                  command=self.load_oma_file).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(controls_frame, text="Plot Scan Data", 
                  command=self.plot_scan_data).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(controls_frame, text="Export to JSON", 
                  command=self.export_to_json).pack(side=tk.LEFT)
        
        # Analysis display
        self.analysis_frame = ttk.Frame(analysis_frame)
        self.analysis_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Create matplotlib figure for analysis
        self.analysis_fig, self.analysis_ax = plt.subplots(figsize=(8, 6))
        self.analysis_canvas = FigureCanvasTkAgg(self.analysis_fig, self.analysis_frame)
        self.analysis_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def setup_settings_tab(self, notebook):
        """Setup the settings tab"""
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="Settings")
        
        # Settings content
        settings_content = ttk.Frame(settings_frame)
        settings_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Frame detection settings
        detection_frame = ttk.LabelFrame(settings_content, text="Frame Detection Settings", padding=10)
        detection_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(detection_frame, text="Minimum contour area:").pack(anchor=tk.W)
        self.min_area_var = tk.IntVar(value=1000)
        ttk.Entry(detection_frame, textvariable=self.min_area_var).pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Label(detection_frame, text="Gaussian blur kernel size:").pack(anchor=tk.W)
        self.blur_kernel_var = tk.IntVar(value=5)
        ttk.Entry(detection_frame, textvariable=self.blur_kernel_var).pack(anchor=tk.W, pady=(0, 10))
        
        # OMa file settings
        oma_frame = ttk.LabelFrame(settings_content, text="OMa File Settings", padding=10)
        oma_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(oma_frame, text="Default save directory:").pack(anchor=tk.W)
        self.save_dir_var = tk.StringVar(value="./scans")
        ttk.Entry(oma_frame, textvariable=self.save_dir_var).pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Button(oma_frame, text="Browse Directory", 
                  command=self.browse_save_directory).pack(anchor=tk.W)
    
    def detect_cameras(self):
        """Detect available cameras"""
        cameras = self.app.get_available_cameras()
        self.camera_combo['values'] = cameras
        if cameras:
            self.camera_combo.set(cameras[0])
            self.status_label.config(text=f"Found {len(cameras)} camera(s)")
        else:
            self.status_label.config(text="No cameras found")
    
    def toggle_capture(self):
        """Toggle camera capture on/off"""
        if not self.is_capturing:
            # Start capture
            camera_index = self.camera_index.get()
            if self.app.initialize_camera(camera_index):
                self.app.start_capture()
                self.is_capturing = True
                self.capture_btn.config(text="Stop Capture")
                self.scan_btn.config(state=tk.NORMAL)
                self.status_label.config(text="Capturing...")
                
                # Start video update thread
                self.video_thread = threading.Thread(target=self.update_video)
                self.video_thread.daemon = True
                self.video_thread.start()
            else:
                messagebox.showerror("Error", "Failed to initialize camera")
        else:
            # Stop capture
            self.app.stop_capture()
            self.is_capturing = False
            self.capture_btn.config(text="Start Capture")
            self.scan_btn.config(state=tk.DISABLED)
            self.status_label.config(text="Ready")
    
    def update_video(self):
        """Update video display"""
        while self.is_capturing:
            if self.app.current_frame is not None:
                # Resize frame for display
                frame = cv2.resize(self.app.current_frame, (640, 480))
                
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Convert to PIL Image
                pil_image = Image.fromarray(frame_rgb)
                photo = ImageTk.PhotoImage(pil_image)
                
                # Update label
                self.video_label.config(image=photo)
                self.video_label.image = photo  # Keep a reference
                
                self.current_frame = self.app.current_frame
            
            time.sleep(0.033)  # ~30 FPS
    
    def capture_scan(self):
        """Capture a frame scan"""
        if self.current_frame is not None:
            self.scan_data = self.app.capture_scan()
            if self.scan_data:
                self.save_btn.config(state=tk.NORMAL)
                self.status_label.config(text="Scan captured successfully")
                messagebox.showinfo("Success", "Frame scan captured successfully!")
            else:
                self.status_label.config(text="Failed to capture scan")
                messagebox.showerror("Error", "Failed to capture frame scan")
        else:
            messagebox.showerror("Error", "No frame available")
    
    def save_oma_file(self):
        """Save OMa file"""
        if not self.scan_data:
            messagebox.showerror("Error", "No scan data to save")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".oma",
            filetypes=[("OMA files", "*.oma"), ("All files", "*.*")]
        )
        
        if filename:
            result = self.app.generate_oma_file(filename)
            if result:
                self.status_label.config(text=f"OMa file saved: {filename}")
                messagebox.showinfo("Success", f"OMa file saved successfully!\n{filename}")
            else:
                messagebox.showerror("Error", "Failed to save OMa file")
    
    def load_oma_file(self):
        """Load OMa file for analysis"""
        filename = filedialog.askopenfilename(
            filetypes=[("OMA files", "*.oma"), ("All files", "*.*")]
        )
        
        if filename:
            self.scan_data = self.app.oma_generator.read_oma_file(filename)
            if self.scan_data:
                self.status_label.config(text=f"Loaded: {filename}")
                messagebox.showinfo("Success", "OMa file loaded successfully!")
            else:
                messagebox.showerror("Error", "Failed to load OMa file")
    
    def plot_scan_data(self):
        """Plot scan data"""
        if not self.scan_data:
            messagebox.showerror("Error", "No scan data to plot")
            return
        
        # Clear previous plot
        self.analysis_ax.clear()
        
        # Plot radius data
        radii = self.scan_data.get('radii', [])
        if radii:
            # Convert to polar plot
            theta = np.linspace(0, 2 * np.pi, len(radii), endpoint=False)
            radii_mm = np.array(radii) / 10.0  # Convert to mm
            
            self.analysis_ax = plt.subplot(111, projection='polar')
            self.analysis_ax.plot(theta, radii_mm, linewidth=2, color='blue')
            self.analysis_ax.set_title('Frame Scan Shape', pad=20)
            self.analysis_ax.grid(True)
        
        self.analysis_canvas.draw()
    
    def export_to_json(self):
        """Export scan data to JSON"""
        if not self.scan_data:
            messagebox.showerror("Error", "No scan data to export")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            result = self.app.oma_generator.export_to_json(self.scan_data, filename)
            if result:
                messagebox.showinfo("Success", f"JSON export saved: {filename}")
            else:
                messagebox.showerror("Error", "Failed to export JSON")
    
    def browse_save_directory(self):
        """Browse for save directory"""
        directory = filedialog.askdirectory()
        if directory:
            self.save_dir_var.set(directory)
    
    def run(self):
        """Run the GUI application"""
        # Create sample OMa file for testing
        self.app.oma_generator.create_sample_oma()
        
        self.root.mainloop() 