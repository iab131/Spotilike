import cv2
import os
import time
from deepface import DeepFace
import numpy as np

def real_time_facial_recognition():
    """
    Real-time facial recognition using webcam
    Press 'q' to quit, 'c' to capture reference face, 's' to save current face to database
    """
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera")
        return
    
    # Create database directory if it doesn't exist
    db_path = "face_db"
    if not os.path.exists(db_path):
        os.makedirs(db_path)
    
    reference_face = None
    reference_name = None
    face_count = 0
    
    print("Controls:")
    print("- Press 'q' to quit")
    print("- Press 'c' to capture current face as reference")
    print("- Press 's' to save current face to database")
    print("- Press 'a' to analyze facial attributes")
    
    analyze_mode = False
    last_detection_time = time.time()
    detection_interval = 1.0  # Seconds between detection attempts
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        
        # Display the frame
        display_frame = frame.copy()
        current_time = time.time()
        
        try:
            # Run face detection/recognition at intervals to avoid overloading CPU
            if current_time - last_detection_time > detection_interval:
                faces = DeepFace.extract_faces(frame, detector_backend='opencv')
                last_detection_time = current_time
                
                if len(faces) > 0:
                    # Draw rectangle around the face
                    face = faces[0]
                    x, y, w, h = face['facial_area']['x'], face['facial_area']['y'], face['facial_area']['w'], face['facial_area']['h']
                    cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    
                    # If we have a reference face, try to match
                    if reference_face is not None:
                        try:
                            result = DeepFace.verify(frame, reference_face)
                            text = f"{reference_name if reference_name else 'Match'}: {'Yes' if result['verified'] else 'No'}"
                            cv2.putText(display_frame, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                        except:
                            pass
                    
                    # If in analyze mode, show facial attributes
                    if analyze_mode:
                        try:
                            analysis = DeepFace.analyze(frame, actions=['emotion', 'age', 'gender'], enforce_detection=False)
                            if analysis:
                                emotion = analysis[0]['dominant_emotion']
                                age = analysis[0]['age']
                                gender = analysis[0]['dominant_gender']
                                
                                cv2.putText(display_frame, f"Age: {age}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                                cv2.putText(display_frame, f"Gender: {gender}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                                cv2.putText(display_frame, f"Emotion: {emotion}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        except Exception as e:
                            print(f"Analysis error: {e}")
                            analyze_mode = False
        except Exception as e:
            print(f"Detection error: {e}")
        
        # Show the frame with or without detection results
        cv2.imshow('DeepFace Facial Recognition', display_frame)
        
        # Process key presses
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        elif key == ord('c'):
            # Capture current frame as reference face
            reference_face = frame.copy()
            reference_name = input("Enter name for reference face: ")
            print(f"Reference face captured: {reference_name}")
        elif key == ord('s'):
            # Save current frame to database
            if not os.path.exists(db_path):
                os.makedirs(db_path)
            face_name = input("Enter name for this face: ")
            face_filename = f"{face_name}_{face_count}.jpg"
            face_path = os.path.join(db_path, face_filename)
            cv2.imwrite(face_path, frame)
            face_count += 1
            print(f"Face saved to {face_path}")
        elif key == ord('a'):
            # Toggle analysis mode
            analyze_mode = not analyze_mode
            print(f"Analysis mode {'on' if analyze_mode else 'off'}")
    
    cap.release()
    cv2.destroyAllWindows()

def batch_process_images(input_dir, output_dir=None):
    """
    Process all images in a directory for facial recognition
    """
    if output_dir is None:
        output_dir = os.path.join(input_dir, "processed")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    image_extensions = ['.jpg', '.jpeg', '.png']
    processed_count = 0
    
    for filename in os.listdir(input_dir):
        if any(filename.lower().endswith(ext) for ext in image_extensions):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, f"processed_{filename}")
            
            try:
                # Read image
                img = cv2.imread(input_path)
                
                # Extract faces
                faces = DeepFace.extract_faces(input_path, detector_backend='opencv')
                
                # If faces found, mark them
                for face in faces:
                    x, y, w, h = face['facial_area']['x'], face['facial_area']['y'], face['facial_area']['w'], face['facial_area']['h']
                    cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    
                    # Analyze face
                    analysis = DeepFace.analyze(input_path, actions=['emotion', 'age', 'gender'], region=(x, y, w, h), enforce_detection=False)
                    if analysis:
                        emotion = analysis[0]['dominant_emotion']
                        age = analysis[0]['age']
                        gender = analysis[0]['dominant_gender']
                        
                        # Add text with analysis results
                        cv2.putText(img, f"Age: {age}", (x, y-40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        cv2.putText(img, f"Gender: {gender}", (x, y-20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        cv2.putText(img, f"Emotion: {emotion}", (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                # Save processed image
                cv2.imwrite(output_path, img)
                processed_count += 1
                print(f"Processed {filename} - Found {len(faces)} faces")
            
            except Exception as e:
                print(f"Error processing {filename}: {e}")
    
    print(f"Batch processing complete. Processed {processed_count} images.")

if __name__ == "__main__":
    print("DeepFace Realtime Demo")
    print("1. Real-time facial recognition with webcam")
    print("2. Batch process images for facial recognition")
    
    choice = input("Enter your choice (1/2): ")
    
    if choice == '1':
        real_time_facial_recognition()
    elif choice == '2':
        input_dir = input("Enter the path to the directory with images: ")
        output_dir = input("Enter the path for processed images (leave empty for default): ")
        if not output_dir:
            output_dir = None
        batch_process_images(input_dir, output_dir)
    else:
        print("Invalid choice")
