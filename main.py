import tkinter as tk
import cv2
import os
import face_recognition  # Import the face_recognition library
from PIL import Image, ImageTk
import datetime
from tkinter import messagebox
import numpy as np

class App:
    def __init__(self):
        # Create the main window
        self.main_window = tk.Tk()

        # Set the geometry of the window (widthxheight+x_offset+y_offset)
        self.main_window.geometry("1200x520+350+100")

        # Define button size
        self.button_width = 20
        self.button_height = 2

        # Create a "Login" button with consistent size and command
        self.login_button_main_window = tk.Button(self.main_window, text='Login', bg='green', fg='white',
                                                  width=self.button_width, height=self.button_height, command=self.login)
        self.login_button_main_window.place(x=750, y=300)

        # Create a "Register" button with consistent size and command
        self.register_button_main_window = tk.Button(self.main_window, text='Register', bg='gray', fg='black',
                                                     width=self.button_width, height=self.button_height, command=self.register_new_user)
        self.register_button_main_window.place(x=750, y=350)

        # Create a label for showing the webcam feed
        self.webcam_label = tk.Label(self.main_window)
        self.webcam_label.place(x=10, y=0, width=700, height=500)

        # Initialize webcam feed
        self.add_webcam(self.webcam_label)

        # Define the directory for storing images
        self.db_dir = './db'
        if not os.path.exists(self.db_dir):
            os.mkdir(self.db_dir)
        
        # Define log file path
        self.log_path = './log.txt'

    def add_webcam(self, label):
        # Initialize video capture if not already done
        if 'cap' not in self.__dict__:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("Error: Could not access the webcam.")
                return
        
        self._label = label
        self.process_webcam()

    def process_webcam(self):
        ret, frame = self.cap.read()
        if not ret:
            print("Error: Failed to capture image.")
            return
        
        # Convert the frame to RGB
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img)
        
        # Convert to ImageTk
        img_tk = ImageTk.PhotoImage(image=img_pil)
        
        # Update the label with the new image
        self._label.image = img_tk
        self._label.configure(image=img_tk)
        
        # Store the most recent capture
        self.most_recent_capture_arr = frame
        self.most_recent_capture_pil = img_pil
        
        # Schedule the next frame update
        self._label.after(20, self.process_webcam)

    def start(self):
        # Start the main loop to run the Tkinter application
        self.main_window.mainloop()

    def login(self):
        unknown_img_path = './.tmp.jpg'
        cv2.imwrite(unknown_img_path, self.most_recent_capture_arr)

        # Load the unknown image and the known images from the database
        unknown_image = face_recognition.load_image_file(unknown_img_path)
        unknown_encoding = face_recognition.face_encodings(unknown_image)

        if not unknown_encoding:
            messagebox.showinfo('Error', 'No face detected in the image.')
            os.remove(unknown_img_path)
            return

        unknown_encoding = unknown_encoding[0]

        known_encodings = []
        known_names = []

        for filename in os.listdir(self.db_dir):
            if filename.endswith('.jpg'):
                name = os.path.splitext(filename)[0]
                image = face_recognition.load_image_file(os.path.join(self.db_dir, filename))
                encoding = face_recognition.face_encodings(image)
                if encoding:
                    known_encodings.append(encoding[0])
                    known_names.append(name)

        # Compare the unknown face to known faces
        results = face_recognition.compare_faces(known_encodings, unknown_encoding)
        if any(results):
            matched_name = known_names[results.index(True)]
            messagebox.showinfo('Welcome back!', f'Welcome, {matched_name}')
            with open(self.log_path, 'a') as f:
                f.write(f'{matched_name} {datetime.datetime.now()}\n')
        else:
            messagebox.showinfo('Oops...', 'Unknown user. Please register or try again.')

        os.remove(unknown_img_path)

    def register_new_user(self):
        # Create a new window for registration
        self.register_new_user_window = tk.Toplevel(self.main_window)
        self.register_new_user_window.geometry("1200x520+370+120")

        # Create "Accept" button
        self.accept_button_register_new_user_window = tk.Button(self.register_new_user_window, text='Accept', bg='green', fg='black',
                                                     width=self.button_width, height=self.button_height, command=self.accept_register_new_user)
        self.accept_button_register_new_user_window.place(x=750, y=350)
        
        # Create "Try Again" button
        self.try_again_button_register_new_user_window = tk.Button(self.register_new_user_window, text='Try again', bg='red', fg='black',
                                                     width=self.button_width, height=self.button_height, command=self.try_again_register_new_user)
        self.try_again_button_register_new_user_window.place(x=750, y=400)
        
        # Create a label for capturing image
        self.capture_label = tk.Label(self.register_new_user_window)
        self.capture_label.place(x=10, y=0, width=700, height=500)
        self.add_img_to_label(self.capture_label)
        
        # Create an entry for username with increased height
        self.entry_text_register_new_user = tk.Entry(self.register_new_user_window, font=('Arial', 16))
        self.entry_text_register_new_user.place(x=750, y=150, width=200, height=30)
        
        # Create a text label for username
        self.text_label_register_new_user = tk.Label(self.register_new_user_window, text='Please input username:')
        self.text_label_register_new_user.place(x=750, y=100)
        
        print("Register button clicked")
        
    def try_again_register_new_user(self):
        self.register_new_user_window.destroy()
    
    def add_img_to_label(self, label):
        if hasattr(self, 'most_recent_capture_pil'):
            imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
            label.imgtk = imgtk
            label.configure(image=imgtk)
            
            # Store the captured image for use
            self.register_new_user_capture = self.most_recent_capture_arr.copy()
        
    def accept_register_new_user(self):
        name = self.entry_text_register_new_user.get().strip()
        if name:
            filename = os.path.join(self.db_dir, f'{name}.jpg')
            cv2.imwrite(filename, self.register_new_user_capture)
            print("Accept button clicked")
            messagebox.showinfo('Success', 'User registered successfully!')
            self.register_new_user_window.destroy()
        else:
            print("Error: No username provided")
            messagebox.showerror('Error', 'Please provide a username.')

if __name__ == "__main__":
    app = App()
    app.start()
