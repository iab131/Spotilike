import os
from deepface import DeepFace
import matplotlib.pyplot as plt
import cv2
import numpy as np

def display_image(img):
    """Display image using matplotlib"""
    plt.figure(figsize=(10, 8))
    if isinstance(img, str):
        img = cv2.imread(img)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    plt.imshow(img)
    plt.axis('off')
    plt.show()

def face_verification(img1_path, img2_path):
    """Verify if two faces belong to the same person"""
    try:
        result = DeepFace.verify(img1_path, img2_path)
        print(f"Face verification result: {result}")
        
        # Display images side by side
        img1 = cv2.imread(img1_path)
        img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
        
        img2 = cv2.imread(img2_path)
        img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
        
        plt.figure(figsize=(15, 8))
        plt.subplot(1, 2, 1)
        plt.imshow(img1)
        plt.title('Image 1')
        plt.axis('off')
        
        plt.subplot(1, 2, 2)
        plt.imshow(img2)
        plt.title('Image 2')
        plt.axis('off')
        
        plt.suptitle(f"Verified: {result['verified']}, Distance: {result['distance']:.2f}")
        plt.show()
        
        return result
    except Exception as e:
        print(f"Error in face verification: {e}")
        return None

def face_analysis(img_path):
    """Analyze facial attributes"""
    try:
        result = DeepFace.analyze(img_path, actions=['emotion', 'age', 'gender', 'race'])
        print("\nFace Analysis:")
        print(f"Emotion: {result[0]['dominant_emotion']}")
        print(f"Age: {result[0]['age']}")
        print(f"Gender: {result[0]['dominant_gender']}")
        print(f"Ethnicity: {result[0]['dominant_race']}")
        
        # Display image with analysis results
        img = cv2.imread(img_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Add text with analysis results
        plt.figure(figsize=(10, 8))
        plt.imshow(img)
        plt.title(f"Age: {result[0]['age']}, Gender: {result[0]['dominant_gender']}\n"
                 f"Emotion: {result[0]['dominant_emotion']}, Race: {result[0]['dominant_race']}")
        plt.axis('off')
        plt.show()
        
        return result
    except Exception as e:
        print(f"Error in face analysis: {e}")
        return None

def find_faces(img_path):
    """Detect and highlight faces in an image"""
    try:
        faces = DeepFace.extract_faces(img_path, detector_backend='opencv')
        
        # Show original image
        img = cv2.imread(img_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        plt.figure(figsize=(12, 8))
        plt.imshow(img)
        plt.title("Original image")
        plt.axis('off')
        plt.show()
        
        # Display each detected face
        print(f"Found {len(faces)} faces")
        for i, face in enumerate(faces):
            plt.figure(figsize=(5, 5))
            plt.imshow(face['face'])
            plt.title(f"Face {i+1}")
            plt.axis('off')
            plt.show()
        
        return faces
    except Exception as e:
        print(f"Error in face detection: {e}")
        return None

def face_recognition_demo(img_path, db_path):
    """Identify faces in an image by matching against a database"""
    try:
        result = DeepFace.find(img_path=img_path, db_path=db_path)
        print(f"\nFace Recognition Results:")
        
        # Show query image
        img = cv2.imread(img_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        plt.figure(figsize=(10, 8))
        plt.imshow(img)
        plt.title("Query image")
        plt.axis('off')
        plt.show()
        
        # If identities were found
        if len(result) > 0 and not result[0].empty:
            print(f"Found {len(result)} matching faces")
            for i, df in enumerate(result):
                if not df.empty:
                    for _, row in df.iterrows():
                        identity_path = row['identity']
                        distance = row['distance']
                        
                        matched_img = cv2.imread(identity_path)
                        matched_img = cv2.cvtColor(matched_img, cv2.COLOR_BGR2RGB)
                        
                        plt.figure(figsize=(8, 8))
                        plt.imshow(matched_img)
                        plt.title(f"Match: {os.path.basename(identity_path)}\nDistance: {distance:.2f}")
                        plt.axis('off')
                        plt.show()
        else:
            print("No matching identities found")
        
        return result
    except Exception as e:
        print(f"Error in face recognition: {e}")
        return None

def create_database(images_dir, db_name="face_db"):
    """Create a face database from a directory of images"""
    try:
        # Create database directory if it doesn't exist
        if not os.path.exists(db_name):
            os.makedirs(db_name)
        
        # Process each image in the directory
        for filename in os.listdir(images_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                src = os.path.join(images_dir, filename)
                dst = os.path.join(db_name, filename)
                
                # Copy the image to the database
                if not os.path.exists(dst):
                    import shutil
                    shutil.copy2(src, dst)
        
        # Build the representation for face matching
        DeepFace.build_model("VGG-Face")  # Pre-load the model
        representations = DeepFace.represent(db_path=db_name, model_name="VGG-Face", enforce_detection=False)
        print(f"Created database with {len(os.listdir(db_name))} images")
        
        return db_name
    except Exception as e:
        print(f"Error creating database: {e}")
        return None

# Usage example (commented out)
if __name__ == "__main__":
    print("DeepFace Facial Recognition Demo")
    print("To use this script, you need to have some images with faces.")
    print("Example usage:")
    print("1. For face verification:")
    print("   face_verification('path_to_image1.jpg', 'path_to_image2.jpg')")
    print("2. For face analysis:")
    print("   face_analysis('path_to_image.jpg')")
    print("3. For face detection:")
    print("   find_faces('path_to_image_with_faces.jpg')")
    print("4. For face recognition:")
    print("   create_database('path_to_folder_with_known_faces', 'my_face_db')")
    print("   face_recognition_demo('path_to_query_image.jpg', 'my_face_db')")
