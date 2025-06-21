# DeepFace Facial Recognition Project

This project implements facial recognition features using the DeepFace library, which is a lightweight facial recognition and facial attribute analysis framework for Python.

## Files in this Project

1. `facial_recognition.py` - Contains utility functions for various facial recognition tasks
2. `realtime_recognition.py` - Implements real-time facial recognition using webcam
3. `facial_recognition_gui.py` - A graphical user interface for easy usage of facial recognition features

## Features

- **Face Detection**: Detect and locate faces in images
- **Face Recognition**: Identify people by comparing faces against a database
- **Face Verification**: Verify if two faces belong to the same person
- **Facial Analysis**: Determine age, gender, emotion, and ethnicity from a face
- **Real-time Processing**: Process webcam images in real-time
- **Batch Processing**: Process multiple images in a directory

## Requirements

- Python 3.6+
- OpenCV
- DeepFace
- NumPy
- Matplotlib
- TensorFlow (installed automatically with DeepFace)
- Tkinter (for GUI application)
- PIL (for GUI application)

## Getting Started

1. Make sure DeepFace is installed:
   ```
   pip install deepface
   ```

2. Run one of the applications:
   
   - For GUI application:
     ```
     python facial_recognition_gui.py
     ```
   
   - For real-time recognition using webcam:
     ```
     python realtime_recognition.py
     ```

   - For using utility functions in your own code:
     ```python
     from facial_recognition import face_verification, face_analysis, find_faces
     ```

## Usage Examples

### Using the GUI Application

The GUI application provides an easy-to-use interface for facial recognition tasks:

1. Start the application: `python facial_recognition_gui.py`
2. Click "Start Webcam" or open an image file from the File menu
3. Use the tools to perform various facial recognition operations:
   - Detect Faces
   - Analyze Face (age, gender, emotion)
   - Capture a face as reference
   - Compare against reference face
   - Add faces to the database
   - Find matches in the database

### Using the Real-time Recognition

1. Start the application: `python realtime_recognition.py`
2. Choose option 1 for webcam-based recognition
3. Use keyboard controls:
   - Press 'q' to quit
   - Press 'c' to capture reference face
   - Press 's' to save current face to database
   - Press 'a' to toggle facial attribute analysis mode

### Using the Utility Functions

```python
from facial_recognition import face_verification, face_analysis, find_faces, face_recognition_demo

# Verify if two faces match
result = face_verification("person1.jpg", "person2.jpg")

# Analyze facial attributes
analysis = face_analysis("face.jpg")

# Detect faces in an image
faces = find_faces("group_photo.jpg")

# Create a face database
create_database("known_faces_folder", "my_face_db")

# Find a face in the database
matches = face_recognition_demo("unknown_person.jpg", "my_face_db")
```

## Notes

- For first-time use, DeepFace will download required models which may take some time
- Face database is stored in the "face_db" folder in the project directory
- Real-time processing may be slow on systems with limited computing resources

## Troubleshooting

- If you encounter "No module named 'deepface'" error, install it with `pip install deepface`
- If face detection fails, try different lighting conditions or adjust your position
- For performance issues, consider:
  - Reducing the frame size for webcam input
  - Increasing the detection interval
  - Using a more powerful computer

## License

This project is meant for educational and personal use.
