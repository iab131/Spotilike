import sys
import os
import cv2
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import threading
import time
import numpy as np
from deepface import DeepFace

class FacialRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DeepFace Facial Recognition")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f0f0f0")
        
        # Application state
        self.cap = None
        self.is_webcam_active = False
        self.webcam_thread = None
        self.stop_webcam_thread = False
        self.reference_image = None
        self.current_image = None
        self.db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "face_db")
        
        if not os.path.exists(self.db_path):
            os.makedirs(self.db_path)
        
        # Create main frames
        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()
        
        # Set initial status
        self.update_status("Ready")
    
    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        
        # File Menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open Image", command=self.open_image)
        file_menu.add_command(label="Save Current Image", command=self.save_image)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        # Tools Menu
        tools_menu = tk.Menu(menu_bar, tearoff=0)
        tools_menu.add_command(label="Start Webcam", command=self.toggle_webcam)
        tools_menu.add_command(label="Capture Reference Face", command=self.capture_reference)
        tools_menu.add_command(label="Add Face to Database", command=self.add_to_database)
        tools_menu.add_separator()
        tools_menu.add_command(label="Batch Process Directory", command=self.batch_process)
        menu_bar.add_cascade(label="Tools", menu=tools_menu)
        
        # Analysis Menu
        analyze_menu = tk.Menu(menu_bar, tearoff=0)
        analyze_menu.add_command(label="Detect Faces", command=lambda: self.process_current_image("detect"))
        analyze_menu.add_command(label="Analyze Face", command=lambda: self.process_current_image("analyze"))
        analyze_menu.add_command(label="Verify Against Reference", command=lambda: self.process_current_image("verify"))
        analyze_menu.add_command(label="Find in Database", command=lambda: self.process_current_image("find"))
        menu_bar.add_cascade(label="Analysis", menu=analyze_menu)
        
        # Help Menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menu_bar)
    
    def create_main_frame(self):
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left frame - Image display area
        self.left_frame = tk.Frame(main_frame, bg="#f0f0f0", width=500)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Image display canvas
        self.canvas = tk.Canvas(self.left_frame, bg="black", width=640, height=480)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Right frame - Controls and results
        right_frame = tk.Frame(main_frame, bg="#f0f0f0", width=300)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5, pady=5)
        
        # Reference image
        ref_frame = tk.LabelFrame(right_frame, text="Reference Face", bg="#f0f0f0")
        ref_frame.pack(fill=tk.X, pady=5)
        
        self.ref_canvas = tk.Canvas(ref_frame, bg="black", width=200, height=200)
        self.ref_canvas.pack(padx=5, pady=5)
        
        # Results area
        results_frame = tk.LabelFrame(right_frame, text="Results", bg="#f0f0f0")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.results_text = tk.Text(results_frame, wrap=tk.WORD, height=15)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Quick action buttons
        buttons_frame = tk.Frame(right_frame, bg="#f0f0f0")
        buttons_frame.pack(fill=tk.X, pady=5)
        
        style = ttk.Style()
        style.configure('TButton', font=('Arial', 10))
        
        self.webcam_btn = ttk.Button(buttons_frame, text="Start Webcam", command=self.toggle_webcam)
        self.webcam_btn.pack(fill=tk.X, pady=2)
        
        ttk.Button(buttons_frame, text="Detect Faces", command=lambda: self.process_current_image("detect")).pack(fill=tk.X, pady=2)
        ttk.Button(buttons_frame, text="Analyze Face", command=lambda: self.process_current_image("analyze")).pack(fill=tk.X, pady=2)
        ttk.Button(buttons_frame, text="Verify Against Reference", command=lambda: self.process_current_image("verify")).pack(fill=tk.X, pady=2)
        ttk.Button(buttons_frame, text="Find in Database", command=lambda: self.process_current_image("find")).pack(fill=tk.X, pady=2)
    
    def create_status_bar(self):
        self.status_bar = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def update_status(self, message):
        self.status_bar.config(text=message)
        self.root.update_idletasks()
    
    def open_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        
        if file_path:
            try:
                self.stop_webcam()
                self.current_image = cv2.imread(file_path)
                self.display_image(self.current_image)
                self.update_status(f"Opened image: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open image: {e}")
    
    def save_image(self):
        if self.current_image is None:
            messagebox.showinfo("Info", "No image to save.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save Image",
            defaultextension=".jpg",
            filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png")]
        )
        
        if file_path:
            try:
                cv2.imwrite(file_path, self.current_image)
                self.update_status(f"Image saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image: {e}")
    
    def toggle_webcam(self):
        if self.is_webcam_active:
            self.stop_webcam()
            self.webcam_btn.config(text="Start Webcam")
        else:
            self.start_webcam()
            self.webcam_btn.config(text="Stop Webcam")
    
    def start_webcam(self):
        if self.is_webcam_active:
            return
        
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                messagebox.showerror("Error", "Cannot open webcam")
                return
            
            self.is_webcam_active = True
            self.stop_webcam_thread = False
            self.webcam_thread = threading.Thread(target=self.webcam_loop)
            self.webcam_thread.daemon = True
            self.webcam_thread.start()
            self.update_status("Webcam active")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start webcam: {e}")
    
    def stop_webcam(self):
        if not self.is_webcam_active:
            return
        
        self.stop_webcam_thread = True
        if self.webcam_thread:
            self.webcam_thread.join(timeout=1.0)
        
        if self.cap and self.cap.isOpened():
            self.cap.release()
        
        self.is_webcam_active = False
        self.update_status("Webcam stopped")
    
    def webcam_loop(self):
        last_process_time = time.time()
        process_interval = 1.0  # Process every 1 second
        
        while not self.stop_webcam_thread:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            self.current_image = frame.copy()
            current_time = time.time()
            
            display_frame = frame.copy()
            
            # Process frame at intervals to detect faces
            if current_time - last_process_time > process_interval:
                try:
                    faces = DeepFace.extract_faces(frame, detector_backend='opencv')
                    
                    # Draw rectangles around faces
                    for face in faces:
                        x, y, w, h = face['facial_area']['x'], face['facial_area']['y'], face['facial_area']['w'], face['facial_area']['h']
                        cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                except:
                    pass
                
                last_process_time = current_time
            
            self.display_image(display_frame)
            time.sleep(0.03)  # ~30 FPS
    
    def display_image(self, image):
        if image is None:
            return
        
        # Resize image to fit the canvas while maintaining aspect ratio
        height, width = image.shape[:2]
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Make sure we have valid dimensions
        if canvas_width <= 1:
            canvas_width = 640
        if canvas_height <= 1:
            canvas_height = 480
        
        # Calculate resize ratio
        ratio_w = canvas_width / width
        ratio_h = canvas_height / height
        ratio = min(ratio_w, ratio_h)
        
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        
        resized = cv2.resize(image, (new_width, new_height))
        
        # Convert to RGB for PIL
        image_rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)
        
        # Display on canvas
        self.photo = ImageTk.PhotoImage(image=pil_image)
        self.canvas.config(width=new_width, height=new_height)
        self.canvas.create_image(new_width//2, new_height//2, image=self.photo, anchor=tk.CENTER)
    
    def display_reference(self, image):
        if image is None:
            return
        
        # Resize for reference display
        resized = cv2.resize(image, (200, 200))
        image_rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)
        
        self.ref_photo = ImageTk.PhotoImage(image=pil_image)
        self.ref_canvas.create_image(100, 100, image=self.ref_photo, anchor=tk.CENTER)
    
    def capture_reference(self):
        if self.current_image is None:
            messagebox.showinfo("Info", "No image to capture as reference.")
            return
        
        self.reference_image = self.current_image.copy()
        self.display_reference(self.reference_image)
        self.update_status("Reference face captured")
    
    def add_to_database(self):
        if self.current_image is None:
            messagebox.showinfo("Info", "No image to add to database.")
            return
        
        name = tk.simpledialog.askstring("Face Name", "Enter a name for this face:")
        if not name:
            return
        
        # Ensure db_path exists
        if not os.path.exists(self.db_path):
            os.makedirs(self.db_path)
        
        # Save image to database
        filename = f"{name}_{int(time.time())}.jpg"
        file_path = os.path.join(self.db_path, filename)
        
        try:
            cv2.imwrite(file_path, self.current_image)
            self.update_status(f"Face saved to database as {filename}")
            self.log_result(f"Face saved to database:\nName: {name}\nFile: {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save to database: {e}")
    
    def process_current_image(self, action_type):
        if self.current_image is None:
            messagebox.showinfo("Info", "No image to process.")
            return
        
        try:
            self.update_status(f"Processing image: {action_type}")
            
            if action_type == "detect":
                # Face detection
                faces = DeepFace.extract_faces(self.current_image, detector_backend='opencv')
                
                result_img = self.current_image.copy()
                for i, face in enumerate(faces):
                    x, y, w, h = face['facial_area']['x'], face['facial_area']['y'], face['facial_area']['w'], face['facial_area']['h']
                    cv2.rectangle(result_img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(result_img, f"Face {i+1}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                self.display_image(result_img)
                self.log_result(f"Detected {len(faces)} faces")
                  elif action_type == "analyze":
                # Face analysis - enforce_detection=False helps with difficult images
                analysis = DeepFace.analyze(self.current_image, actions=['emotion', 'age', 'gender', 'race'], enforce_detection=False)
                
                result_img = self.current_image.copy()
                
                # Handle the analysis results properly based on DeepFace's return format
                # DeepFace.analyze returns a list, where each element corresponds to a face
                if isinstance(analysis, list):
                    for i, face_data in enumerate(analysis):
                        emotion = face_data.get('dominant_emotion', 'unknown')
                        age = face_data.get('age', 'unknown')
                        gender = face_data.get('dominant_gender', 'unknown')
                        race = face_data.get('dominant_race', 'unknown')
                        
                        # Get face location
                        if 'region' in face_data:
                            x = face_data['region'].get('x', 0)
                            y = face_data['region'].get('y', 0)
                            w = face_data['region'].get('w', 100)
                            h = face_data['region'].get('h', 100)
                        else:
                            # Try to get from face detection
                            try:
                                faces = DeepFace.extract_faces(self.current_image, detector_backend='opencv')
                                if i < len(faces):
                                    x = faces[i]['facial_area'].get('x', 0)
                                    y = faces[i]['facial_area'].get('y', 0)
                                    w = faces[i]['facial_area'].get('w', 100)
                                    h = faces[i]['facial_area'].get('h', 100)
                                else:
                                    # Default position if face index is out of range
                                    h, w = self.current_image.shape[:2]
                                    x, y = 10, 10
                            except:
                                # Default to upper left if detection fails
                                h, w = self.current_image.shape[:2]
                                x, y = 10, 10
                        
                        # Draw rectangle and info (with guards for coordinate validity)
                        try:
                            cv2.rectangle(result_img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                            y_text = max(y-20, 30)  # Ensure text doesn't go off the top of the image
                            cv2.putText(result_img, f"Age: {age}", (x, y_text-40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                            cv2.putText(result_img, f"Gender: {gender}", (x, y_text-20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                            cv2.putText(result_img, f"Emotion: {emotion}", (x, y_text), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        except:
                            pass  # Skip drawing if there's any issue with coordinates
                        
                        self.log_result(f"Face {i+1} Analysis:\nAge: {age}\nGender: {gender}\nEmotion: {emotion}\nEthnicity: {race}")
                else:
                    # Handle case where only one face is returned (not as a list)
                    face_data = analysis  # Treat it as a single face data
                    emotion = face_data.get('dominant_emotion', 'unknown')
                    age = face_data.get('age', 'unknown')
                    gender = face_data.get('dominant_gender', 'unknown')
                    race = face_data.get('dominant_race', 'unknown')
                    
                    # Try to get face location from face detection
                    try:
                        faces = DeepFace.extract_faces(self.current_image, detector_backend='opencv')
                        if faces:
                            x = faces[0]['facial_area'].get('x', 0)
                            y = faces[0]['facial_area'].get('y', 0)
                            w = faces[0]['facial_area'].get('w', 100)
                            h = faces[0]['facial_area'].get('h', 100)
                            
                            cv2.rectangle(result_img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                            y_text = max(y-20, 30)
                            cv2.putText(result_img, f"Age: {age}", (x, y_text-40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                            cv2.putText(result_img, f"Gender: {gender}", (x, y_text-20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                            cv2.putText(result_img, f"Emotion: {emotion}", (x, y_text), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        else:
                            # If no face is detected, just display the results as text
                            cv2.putText(result_img, f"Age: {age}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                            cv2.putText(result_img, f"Gender: {gender}", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                            cv2.putText(result_img, f"Emotion: {emotion}", (20, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    except:
                        # If face detection fails, just show the results as text
                        cv2.putText(result_img, f"Age: {age}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                        cv2.putText(result_img, f"Gender: {gender}", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                        cv2.putText(result_img, f"Emotion: {emotion}", (20, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    
                    self.log_result(f"Face Analysis:\nAge: {age}\nGender: {gender}\nEmotion: {emotion}\nEthnicity: {race}")
                
                self.display_image(result_img)
                
            elif action_type == "verify":
                if self.reference_image is None:
                    messagebox.showinfo("Info", "No reference face set. Please capture a reference first.")
                    return
                
                # Face verification
                result = DeepFace.verify(self.reference_image, self.current_image)
                verified = result['verified']
                distance = result['distance']
                threshold = result['threshold']
                
                # Display result
                result_img = self.current_image.copy()
                color = (0, 255, 0) if verified else (0, 0, 255)
                text = "MATCH" if verified else "NOT MATCH"
                
                cv2.putText(result_img, text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 3)
                cv2.putText(result_img, f"Distance: {distance:.4f}", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                cv2.putText(result_img, f"Threshold: {threshold:.4f}", (20, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                
                self.display_image(result_img)
                self.log_result(f"Verification Result: {text}\nDistance: {distance:.4f}\nThreshold: {threshold:.4f}")
                
            elif action_type == "find":
                # Check if database exists and has images
                if not os.path.exists(self.db_path) or not os.listdir(self.db_path):
                    messagebox.showinfo("Info", "No faces in database. Please add faces first.")
                    return
                
                # Face recognition
                result = DeepFace.find(img_path=self.current_image, db_path=self.db_path, enforce_detection=False)
                
                result_img = self.current_image.copy()
                
                if result and len(result) > 0 and not result[0].empty:
                    self.log_result("Matching faces found in database:")
                    
                    for i, df in enumerate(result):
                        if not df.empty:
                            # Get top match
                            top_match = df.iloc[0]
                            identity_path = top_match['identity']
                            distance = top_match['distance']
                            
                            # Extract name from filename
                            name = os.path.basename(identity_path).split('_')[0]
                            
                            # Get face location
                            faces = DeepFace.extract_faces(self.current_image, detector_backend='opencv')
                            if i < len(faces):
                                face = faces[i]
                                x, y, w, h = face['facial_area']['x'], face['facial_area']['y'], face['facial_area']['w'], face['facial_area']['h']
                                
                                # Draw rectangle and info
                                cv2.rectangle(result_img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                                cv2.putText(result_img, name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                                
                                self.log_result(f"Face {i+1}: {name}\nDistance: {distance:.4f}")
                else:
                    self.log_result("No matching faces found in database.")
                
                self.display_image(result_img)
            
            self.update_status(f"Completed: {action_type}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process image: {e}")
            self.update_status(f"Error: {action_type} failed")
    
    def batch_process(self):
        input_dir = filedialog.askdirectory(title="Select directory with images to process")
        if not input_dir:
            return
        
        output_dir = filedialog.askdirectory(title="Select output directory for processed images")
        if not output_dir:
            return
        
        try:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            image_extensions = ['.jpg', '.jpeg', '.png']
            image_files = [f for f in os.listdir(input_dir) if any(f.lower().endswith(ext) for ext in image_extensions)]
            
            if not image_files:
                messagebox.showinfo("Info", "No image files found in the selected directory.")
                return
            
            progress_window = tk.Toplevel(self.root)
            progress_window.title("Processing Images")
            progress_window.geometry("400x150")
            
            progress_label = tk.Label(progress_window, text="Processing images...")
            progress_label.pack(pady=10)
            
            progress_bar = ttk.Progressbar(progress_window, orient='horizontal', length=300, mode='determinate')
            progress_bar.pack(pady=10)
            
            progress_text = tk.Label(progress_window, text="")
            progress_text.pack(pady=5)
            
            total_files = len(image_files)
            progress_bar['maximum'] = total_files
            
            def process_files():
                for i, filename in enumerate(image_files):
                    input_path = os.path.join(input_dir, filename)
                    output_path = os.path.join(output_dir, f"processed_{filename}")
                    
                    try:
                        # Update progress
                        progress_text.config(text=f"Processing {i+1}/{total_files}: {filename}")
                        progress_bar['value'] = i + 1
                        self.root.update_idletasks()
                        
                        # Process image
                        img = cv2.imread(input_path)
                        
                        # Detect faces
                        faces = DeepFace.extract_faces(input_path, detector_backend='opencv')
                        
                        # Analyze faces
                        for face in faces:
                            x, y, w, h = face['facial_area']['x'], face['facial_area']['y'], face['facial_area']['w'], face['facial_area']['h']
                            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                              try:
                                analysis = DeepFace.analyze(input_path, actions=['emotion', 'age', 'gender'], enforce_detection=False)
                                
                                # Handle both list and single result formats
                                if isinstance(analysis, list) and len(analysis) > 0:
                                    face_data = analysis[0]
                                else:
                                    face_data = analysis
                                
                                # Use .get() to safely access dictionary values
                                emotion = face_data.get('dominant_emotion', 'unknown')
                                age = face_data.get('age', 'unknown')
                                gender = face_data.get('dominant_gender', 'unknown')
                                
                                # Ensure y position is not too close to the top of the image
                                y_text = max(y-20, 30)
                                cv2.putText(img, f"Age: {age}", (x, y_text-40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)                                cv2.putText(img, f"Gender: {gender}", (x, y_text-20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                                cv2.putText(img, f"Emotion: {emotion}", (x, y_text), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                            except Exception as e:
                                print(f"Error analyzing face: {e}")
                        
                        # Save processed image
                        cv2.imwrite(output_path, img)
                    
                    except Exception as e:
                        print(f"Error processing {filename}: {e}")
                
                progress_window.destroy()
                messagebox.showinfo("Complete", f"Processed {total_files} images. Results saved to {output_dir}")
            
            # Run processing in a separate thread to keep UI responsive
            threading.Thread(target=process_files, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Batch processing failed: {e}")
    
    def log_result(self, text):
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, text)
    
    def show_about(self):
        messagebox.showinfo(
            "About",
            "DeepFace Facial Recognition\n\n"
            "A GUI application for facial analysis using the DeepFace library.\n\n"
            "Features:\n"
            "- Face Detection\n"
            "- Facial Analysis (Age, Gender, Emotion)\n"
            "- Face Verification\n"
            "- Face Recognition\n\n"
            "© 2025"
        )

if __name__ == "__main__":
    # Check if deepface is installed
    try:
        import deepface
    except ImportError:
        print("DeepFace library not found. Please install it with 'pip install deepface'")
        sys.exit(1)
    
    root = tk.Tk()
    app = FacialRecognitionApp(root)
    root.mainloop()
