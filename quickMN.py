import customtkinter as ctk
import cv2
import numpy as np
import pandas as pd
import os
from tkinter import filedialog
from PIL import Image, ImageTk

class MicroneedleMeasurementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Microneedle Measurement")
        
        # UI Elements
        self.canvas = ctk.CTkCanvas(root)
        self.canvas.grid(row=0, column=0, columnspan=4, sticky="nsew")
        
        self.scale_label = ctk.CTkLabel(root, text="Scale (px per unit):")
        self.scale_label.grid(row=1, column=0)
        
        self.scale_entry = ctk.CTkEntry(root)
        self.scale_entry.grid(row=1, column=1)
        
        self.comment_label = ctk.CTkLabel(root, text="Comment:")
        self.comment_label.grid(row=1, column=2)
        
        self.comment_entry = ctk.CTkEntry(root)
        self.comment_entry.grid(row=1, column=3)
        
        self.load_button = ctk.CTkButton(root, text="Load Images", command=self.load_images)
        self.load_button.grid(row=2, column=0)
        
        self.reset_button = ctk.CTkButton(root, text="Reset Points", command=self.reset_points)
        self.reset_button.grid(row=2, column=1)
        
        self.save_button = ctk.CTkButton(root, text="Save & Next", command=self.save_measurements)
        self.save_button.grid(row=2, column=2)
        
        self.mark_flawed_button = ctk.CTkButton(root, text="Mark as Flawed", command=self.mark_flawed)
        self.mark_flawed_button.grid(row=3, column=1)
        
        self.points = []
        self.image_list = []
        self.current_image_index = 0
        self.image_path = None
        self.image = None
        self.tk_image = None
        self.data = []
        self.original_image_size = None
        
        self.canvas.bind("<Button-1>", self.capture_point)
        
        # Configure window resizing
        root.columnconfigure(0, weight=1)
        root.columnconfigure(1, weight=1)
        root.columnconfigure(2, weight=1)
        root.columnconfigure(3, weight=1)
        root.rowconfigure(0, weight=1)

    def load_images(self):
        folder = filedialog.askdirectory()
        if folder:
            self.image_list = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(('png', 'jpg', 'jpeg', 'bmp'))]
            self.current_image_index = 0
            self.load_next_image()

    def load_next_image(self):
        if self.current_image_index < len(self.image_list):
            self.image_path = self.image_list[self.current_image_index]
            self.image = cv2.imread(self.image_path)
            self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            self.original_image_size = self.image.shape[:2]
            self.display_image()
            self.points = []
        else:
            self.save_to_excel()
            print("No more images.")

    def display_image(self):
        img = Image.fromarray(self.image)
        img_ratio = img.width / img.height
        win_width = self.root.winfo_width()
        win_height = self.root.winfo_height()
        
        if win_width / win_height > img_ratio:
            new_height = win_height - 50
            new_width = int(new_height * img_ratio)
        else:
            new_width = win_width - 50
            new_height = int(new_width / img_ratio)
        
        old_width = img.width
        img = img.resize((new_width, new_height), Image.LANCZOS)
        self.new_img_scale = img.width / old_width
        print(self.new_img_scale)
        self.tk_image = ImageTk.PhotoImage(img)
        self.canvas.config(width=new_width, height=new_height)
        self.canvas.create_image(0, 0, anchor='nw', image=self.tk_image)

    def capture_point(self, event):
        if len(self.points) < 5:
            x, y = event.x, event.y
            self.points.append((x, y))
            self.canvas.create_oval(x-3, y-3, x+3, y+3, fill="red")

    def reset_points(self):
        self.points = []
        self.display_image()

    def save_measurements(self):
        if len(self.points) == 5 and self.scale_entry.get():
            scale = float(self.scale_entry.get()) * self.new_img_scale
            base_width = np.linalg.norm(np.array(self.points[1]) - np.array(self.points[0])) / scale
            
            # Compute normal vector height
            p0, p1, p4 = np.array(self.points[0]), np.array(self.points[1]), np.array(self.points[4])
            base_vector = p1 - p0
            normal_vector = np.array([-base_vector[1], base_vector[0]])  # Rotate 90 degrees
            normal_vector = normal_vector / np.linalg.norm(normal_vector)  # Normalize
            height_vector = p4 - p0
            needle_height = np.abs(np.dot(height_vector, normal_vector)) / scale
            
            # Check offset of normal foot
            midpoint = (p0 + p1) / 2
            foot_projection = p0 + np.dot(height_vector, base_vector) / np.dot(base_vector, base_vector) * base_vector
            offset_note = "" if np.linalg.norm(foot_projection - midpoint) < (base_width / 8) else "Tip offset from midpoint"
            
            # Compute tip sharpness (angle between tip points)
            p2, p3 = np.array(self.points[2]), np.array(self.points[3])
            tip_vector1 = p2 - p4
            tip_vector2 = p3 - p4
            angle_radians = np.arccos(np.dot(tip_vector1, tip_vector2) / (np.linalg.norm(tip_vector1) * np.linalg.norm(tip_vector2)))
            tip_sharpness = np.degrees(angle_radians)
            
            comment = self.comment_entry.get() + (". " + offset_note if offset_note else "")
            
            self.data.append([self.image_path, base_width, needle_height, tip_sharpness, comment])
            self.current_image_index += 1
            self.load_next_image()
        else:
            print("Please mark 5 points and enter a scale.")

    def mark_flawed(self):
        comment = self.comment_entry.get()
        self.data.append([self.image_path, "Flawed", "", "", comment])
        self.current_image_index += 1
        self.load_next_image()

    def save_to_excel(self):
        df = pd.DataFrame(self.data, columns=["Image", "Base Width", "Needle Height", "Tip Sharpness", "Comment"])
        df.to_excel("microneedle_measurements.xlsx", index=False)
        print("Data saved to microneedle_measurements.xlsx")

if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("1000x800")
    app = MicroneedleMeasurementApp(root)
    root.mainloop()
