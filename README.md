# Huvitz Excelon Frame Scan Capture System

A comprehensive Python application for capturing frame scan data from Huvitz Excelon devices via VGA output and generating OMa files.

## Features

- **Real-time Video Capture**: Capture frame scans through VGA/USB adapter
- **Frame Detection**: Advanced image processing to detect frame contours
- **OMa File Generation**: Generate standardized OMa files from scan data
- **Data Visualization**: Plot frame scan shapes using polar plots
- **Modern GUI**: User-friendly interface with multiple tabs
- **Data Export**: Export scan data to JSON format for analysis

## System Requirements

- Windows 10/11
- Python 3.8 or higher
- USB video capture device (for VGA to USB connection)
- Huvitz Excelon device with VGA output

## Installation

1. **Clone or download the project files to your workspace**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Connect your hardware**:
   - Connect Huvitz Excelon VGA output to USB video capture device
   - Connect USB capture device to your computer
   - Ensure the device is recognized by Windows

## Usage

### Running the Application

1. **Start the main application**:
   ```bash
   python main.py

   Or double-click run.bat on Windows
   ```

2. **Using the GUI**:
   - **Capture Tab**: Select camera, start capture, and capture frame scans
   - **Analysis Tab**: Load OMa files and visualize scan data
   - **Settings Tab**: Configure frame detection parameters

### Command Line Testing

Run the test script to verify functionality:
```bash
python test_scan.py
```

Run the script to View the demo::
```bash
python demo_plot.py
```

This will:
- Test radius plotting with sample data
- Test OMa file generation and reading
- Test frame processing functionality

## File Structure

```
HuvitzExcelon/
├── main.py              # Main application entry point
├── frame_processor.py   # Frame detection and processing
├── oma_generator.py     # OMa file generation and parsing
├── gui.py              # GUI interface
├── test_scan.py        # Test script
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## OMa File Format

The application generates OMa files with the following structure:

- **Header**: Magic number, version, timestamp, device info
- **Frame Data**: Width, height, center coordinates, area, perimeter
- **Radius Data**: 1000 radius measurements in 0.1mm units

### Sample OMa File Structure

```
OMAF (Magic number)
Version: 1
Number of radius points: 1000
Timestamp: ISO format
Device info: "Huvitz Excelon Frame Scanner"
Frame measurements: width, height, center_x, center_y, area, perimeter
Radius data: 1000 16-bit integers
```

## Frame Processing

The system uses advanced computer vision techniques:

1. **Preprocessing**: Gaussian blur and adaptive thresholding
2. **Contour Detection**: Find frame boundaries
3. **Shape Analysis**: Extract measurements and center points
4. **Radius Calculation**: Generate 1000 radius measurements

## Configuration

### Camera Settings
- **Camera Index**: Select the correct USB capture device
- **Resolution**: Default 1920x1080, adjustable in settings
- **Frame Rate**: 30 FPS for real-time capture

### Frame Detection Settings
- **Minimum Contour Area**: Filter out small noise (default: 1000)
- **Blur Kernel Size**: Gaussian blur parameter (default: 5)
- **Save Directory**: Default location for OMa files

## Troubleshooting

### Common Issues

1. **No Camera Found**:
   - Check USB connection
   - Verify device drivers are installed
   - Try different camera indices

2. **Frame Not Detected**:
   - Adjust lighting conditions
   - Modify minimum contour area in settings
   - Check frame positioning

3. **OMa File Generation Failed**:
   - Ensure scan data is captured
   - Check file permissions
   - Verify disk space

### Debug Mode

Enable debug output by modifying the logging level in the code.

## Sample Data

The application includes sample radius data based on your provided example:

```python
# Sample radius data (1000 points)
radii = [2354, 2359, 2365, ...]  # 0.1mm units
```

This data is used for testing and demonstration purposes.

## Development

### Adding New Features

1. **Custom Frame Detection**: Modify `frame_processor.py`
2. **New File Formats**: Extend `oma_generator.py`
3. **GUI Enhancements**: Update `gui.py`

### Testing

Run comprehensive tests:
```bash
python test_scan.py
```

## License

This project is designed for Huvitz Excelon frame scan capture and analysis.

## Support

For technical support or feature requests, please refer to the code documentation and test scripts.

---

**Note**: This system is specifically designed for Huvitz Excelon devices and may require calibration for optimal performance with your specific hardware setup. 