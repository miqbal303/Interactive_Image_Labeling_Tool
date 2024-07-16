import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import cv2
import numpy as np
from PIL import Image, ImageTk
import logging
import os

class LabelingTool:
    def __init__(self, master):
        self.master = master
        self.master.title("Interactive Image Labeling Tool")
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        
        self.label_map = {
            0: 'Background',
            1: 'French manicure',
            2: 'Acrylic',
            3: 'Bare nail'
        }

        self.label_colors = {
            0: (0, 0, 0),        # Black for Background
            1: (255, 0, 0),      # Blue for French manicure
            2: (0, 255, 0),      # Green for Acrylic
            3: (0, 0, 255)       # Red for Bare nail
        }

        self.current_label = tk.IntVar(value=1)  # Default label

        self.canvas = tk.Canvas(self.master, width=800, height=600, bg='white')
        self.canvas.pack()

        # Create a frame for buttons and dropdown
        self.button_frame = tk.Frame(self.master)
        self.button_frame.pack(pady=10)

        self.load_button = tk.Button(self.button_frame, text="Load Image", command=self.load_image)
        self.load_button.grid(row=0, column=0, padx=5)

        self.load_label_button = tk.Button(self.button_frame, text="Load Label Image", command=self.load_label_image)
        self.load_label_button.grid(row=0, column=1, padx=5)

        self.grayscale_button = tk.Button(self.button_frame, text="Toggle Grayscale", command=self.toggle_grayscale)
        self.grayscale_button.grid(row=0, column=2, padx=5)

        self.label_dropdown = ttk.Combobox(self.button_frame, textvariable=self.current_label, values=list(self.label_map.keys()))
        self.label_dropdown.grid(row=0, column=3, padx=5)
        self.label_dropdown.bind("<<ComboboxSelected>>", self.update_label)

        self.back_button = tk.Button(self.button_frame, text="Back", command=self.back)
        self.back_button.grid(row=0, column=4, padx=5)

        self.save_button = tk.Button(self.button_frame, text="Save Annotation", command=self.save_annotation)
        self.save_button.grid(row=0, column=5, padx=5)

        self.quit_button = tk.Button(self.button_frame, text="Quit", command=self.quit)
        self.quit_button.grid(row=0, column=6, padx=5)

        self.image = None
        self.label_image = None
        self.image_path = None
        self.image_loaded = False
        self.grayscale = False

        self.history = []
        self.polygon_points = []

        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Button-3>", self.on_right_click)

    def load_image(self):
        try:
            self.image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp")])
            if self.image_path:
                logging.info(f"Selected image path: {self.image_path}")
                self.image = cv2.imread(self.image_path)
                if self.image is not None:
                    self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
                    self.image = cv2.resize(self.image, (687, 687))  # Resize to match the example dimensions
                    self.label_image = np.zeros((self.image.shape[0], self.image.shape[1]), dtype=np.uint8)
                    self.image_loaded = True
                    self.show_image()
                    logging.info("Image loaded successfully.")
                else:
                    logging.error("Failed to load image.")
                    messagebox.showerror("Error", "Failed to load image.")
        except Exception as e:
            logging.exception("Exception occurred while loading image:")
            messagebox.showerror("Error", f"An error occurred while loading the image: {e}")

    def load_label_image(self):
        try:
            label_image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png")])
            if label_image_path:
                logging.info(f"Selected label image path: {label_image_path}")
                label_image = cv2.imread(label_image_path, cv2.IMREAD_GRAYSCALE)
                if label_image is not None:
                    self.label_image = cv2.resize(label_image, (687, 687))  # Resize to match the example dimensions
                    self.image_loaded = True
                    self.show_image()
                    logging.info("Label image loaded successfully.")
                else:
                    logging.error("Failed to load label image.")
                    messagebox.showerror("Error", "Failed to load label image.")
        except Exception as e:
            logging.exception("Exception occurred while loading label image:")
            messagebox.showerror("Error", f"An error occurred while loading the label image: {e}")

    def show_image(self):
        try:
            if self.image_loaded:
                display_img = cv2.cvtColor(self.image, cv2.COLOR_RGB2GRAY) if self.grayscale else self.image
                if self.grayscale and len(display_img.shape) == 2:
                    display_img = cv2.cvtColor(display_img, cv2.COLOR_GRAY2RGB)

                annotation_overlay = self.create_annotation_overlay()
                combined_img = cv2.addWeighted(display_img, 0.7, annotation_overlay, 0.3, 0)
                self.canvas_img = cv2.resize(combined_img, (800, 600))
                img = Image.fromarray(self.canvas_img)
                img = ImageTk.PhotoImage(image=img)
                self.canvas.create_image(0, 0, anchor=tk.NW, image=img)
                self.canvas.image = img
                logging.info("Image displayed on canvas.")
        except Exception as e:
            logging.exception("Exception occurred while displaying image:")
            messagebox.showerror("Error", f"An error occurred while displaying the image: {e}")

    def create_annotation_overlay(self):
        if self.label_image is None or self.image is None:
            logging.error("Label image or main image is not loaded.")
            return np.zeros_like(self.image, dtype=np.uint8)

        overlay = np.zeros_like(self.image, dtype=np.uint8)
        for label, color in self.label_colors.items():
            mask = self.label_image == label
            overlay[mask] = color
        return overlay

    def on_click(self, event):
        if self.image_loaded:
            self.polygon_points.append((event.x, event.y))
            self.canvas.create_oval(event.x - 2, event.y - 2, event.x + 2, event.y + 2, fill="red")
            if len(self.polygon_points) > 1:
                self.canvas.create_line(self.polygon_points[-2], self.polygon_points[-1], fill="red")
                if self.is_close_to_start(event.x, event.y):
                    self.on_right_click(event)

    def is_close_to_start(self, x, y, threshold=10):
        start_x, start_y = self.polygon_points[0]
        return ((x - start_x) ** 2 + (y - start_y) ** 2) ** 0.5 < threshold

    def on_right_click(self, event):
        if self.image_loaded and len(self.polygon_points) > 2:
            self.canvas.create_line(self.polygon_points[-1], self.polygon_points[0], fill="red")
            self.label_polygon()
            self.polygon_points = []

    def label_polygon(self):
        try:
            if self.image_loaded and len(self.polygon_points) > 2:
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()
                image_height, image_width = self.label_image.shape

                polygon_points_img = [(int(x * image_width / canvas_width), int(y * image_height / canvas_height)) for x, y in self.polygon_points]

                mask = np.zeros_like(self.label_image, dtype=np.uint8)
                cv2.fillPoly(mask, [np.array(polygon_points_img)], self.current_label.get())

                self.history.append(self.label_image.copy())  # Save history for undo
                self.label_image[mask == self.current_label.get()] = self.current_label.get()
                self.show_image()
                logging.info(f"Label {self.current_label.get()} assigned to polygon with points {self.polygon_points}.")
        except Exception as e:
            logging.exception("Exception occurred while labeling polygon:")
            messagebox.showerror("Error", f"An error occurred while labeling the polygon: {e}")

    def update_label(self, event):
        try:
            self.current_label.set(int(self.label_dropdown.get()))
            logging.info(f"Switched to label {self.current_label.get()}: {self.label_map[self.current_label.get()]}")
        except Exception as e:
            logging.exception("Exception occurred while updating label:")
            messagebox.showerror("Error", f"An error occurred while updating the label: {e}")

    def back(self):
        try:
            if self.history:
                self.label_image = self.history.pop()
                self.show_image()
                logging.info("Reverted to previous label state.")
            else:
                logging.warning("No history to revert to.")
                messagebox.showwarning("Warning", "No history to revert to.")
        except Exception as e:
            logging.exception("Exception occurred while reverting to previous state:")
            messagebox.showerror("Error", f"An error occurred while reverting to the previous state: {e}")

    def toggle_grayscale(self):
        try:
            self.grayscale = not self.grayscale
            self.show_image()
            logging.info(f"Grayscale mode {'enabled' if self.grayscale else 'disabled'}.")
        except Exception as e:
            logging.exception("Exception occurred while toggling grayscale:")
            messagebox.showerror("Error", f"An error occurred while toggling grayscale: {e}")

    def save_annotation(self):
        try:
            if self.label_image is not None:
                save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
                if save_path:
                    cv2.imwrite(save_path, self.label_image)
                    logging.info(f"Annotation saved successfully at {save_path}.")
                    messagebox.showinfo("Success", f"Annotation saved successfully at {save_path}.")
                else:
                    logging.warning("Annotation save canceled.")
                    messagebox.showwarning("Warning", "Annotation save canceled.")
        except Exception as e:
            logging.exception("Exception occurred while saving annotation:")
            messagebox.showerror("Error", f"An error occurred while saving the annotation: {e}")

    def quit(self):
        try:
            logging.info("Quitting the application.")
            self.master.quit()
        except Exception as e:
            logging.exception("Exception occurred while quitting the application:")
            messagebox.showerror("Error", f"An error occurred while quitting the application: {e}")

def main():
    root = tk.Tk()
    labeling_tool = LabelingTool(root)
    root.mainloop()

if __name__ == "__main__":
    main()
