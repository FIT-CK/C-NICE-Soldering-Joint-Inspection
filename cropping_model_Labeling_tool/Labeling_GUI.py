import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import numpy as np

class ImageAnnotationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Annotation Tool")
        self.image_folder = None
        self.output_folder = None
        self.image_files = []
        self.current_image_index = -1
        self.image = None
        self.img_canvas = None
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.bboxes = []
        self.current_class = 0

        self.canvas = tk.Canvas(root, cursor="cross")
        self.canvas.pack(expand=True, fill=tk.BOTH)
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        self.create_menu()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open Image Folder", command=self.open_image_folder)
        file_menu.add_command(label="Set Output Folder", command=self.set_output_folder)
        file_menu.add_command(label="Next Image", command=self.load_next_image)
        file_menu.add_command(label="Save Annotations", command=self.save_annotations)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        class_menu = tk.Menu(menubar, tearoff=0)
        class_menu.add_command(label="Class 0", command=lambda: self.set_class(0))
        class_menu.add_command(label="Class 1", command=lambda: self.set_class(1))
        menubar.add_cascade(label="Class", menu=class_menu)

        self.root.config(menu=menubar)

    def set_class(self, class_id):
        self.current_class = class_id

    def open_image_folder(self):
        self.image_folder = filedialog.askdirectory()
        if self.image_folder:
            self.image_files = [f for f in os.listdir(self.image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            self.current_image_index = -1
            self.load_next_image()

    def set_output_folder(self):
        self.output_folder = filedialog.askdirectory()

    def load_next_image(self):
        self.current_image_index += 1
        if self.current_image_index < len(self.image_files):
            image_path = os.path.join(self.image_folder, self.image_files[self.current_image_index])
            self.image = Image.open(image_path)
            self.bboxes = []
            self.display_image()

    def display_image(self):
        self.img_canvas = ImageTk.PhotoImage(self.image)
        self.canvas.config(width=self.img_canvas.width(), height=self.img_canvas.height())
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.img_canvas)

    def on_button_press(self, event):
        self.start_x, self.start_y = event.x, event.y
        color = "red" if self.current_class == 0 else "blue"
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline=color)

    def on_mouse_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_button_release(self, event):
        end_x, end_y = event.x, event.y
        color = "red" if self.current_class == 0 else "blue"
        self.canvas.itemconfig(self.rect, outline=color)
        self.bboxes.append((self.start_x, self.start_y, end_x, end_y, self.current_class))

    def save_annotations(self):
        if self.output_folder and self.image:
            img_array = np.array(self.image)
            base_filename = os.path.splitext(self.image_files[self.current_image_index])[0]
            txt_path = os.path.join(self.output_folder, f"{base_filename}.txt")
            with open(txt_path, 'w') as txt_file:
                for (start_x, start_y, end_x, end_y, cls) in self.bboxes:
                    x_center = (start_x + end_x) / 2 / img_array.shape[1]
                    y_center = (start_y + end_y) / 2 / img_array.shape[0]
                    width = (end_x - start_x) / img_array.shape[1]
                    height = (end_y - start_y) / img_array.shape[0]
                    txt_file.write(f"{cls} {x_center} {y_center} {width} {height}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageAnnotationApp(root)
    root.mainloop()
