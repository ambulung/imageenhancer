import tkinter as tk
from tkinter import filedialog, Scale, HORIZONTAL, ttk, messagebox
from PIL import Image, ImageTk, ImageEnhance, ImageFilter

class ImageEnhancer:
    """
    Core logic for image enhancement using Pillow.
    Handles loading, applying enhancements, and resetting.
    """
    def __init__(self):
        self.original_image = None
        self.current_image = None
        self.display_image_tk = None # To hold the PhotoImage object for Tkinter
        self.image_path = None

    def load_image(self, path):
        try:
            self.original_image = Image.open(path).convert("RGB") # Ensure RGB for consistent processing
            self.current_image = self.original_image.copy()
            self.image_path = path
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")
            self.original_image = None
            self.current_image = None
            self.image_path = None
            return False

    def reset_image(self):
        if self.original_image:
            self.current_image = self.original_image.copy()
        return self.current_image

    def apply_enhancements(self, brightness_factor, contrast_factor,
                           sharpness_factor, color_factor, grayscale, blur):
        if not self.original_image:
            return None

        # Start from a clean copy of the original image for each update
        temp_image = self.original_image.copy()

        # Apply Grayscale if selected
        if grayscale:
            temp_image = temp_image.convert("L") # Convert to grayscale
            temp_image = temp_image.convert("RGB") # Convert back to RGB for other enhancements

        # Apply Brightness
        enhancer = ImageEnhance.Brightness(temp_image)
        temp_image = enhancer.enhance(brightness_factor)

        # Apply Contrast
        enhancer = ImageEnhance.Contrast(temp_image)
        temp_image = enhancer.enhance(contrast_factor)

        # Apply Sharpness
        enhancer = ImageEnhance.Sharpness(temp_image)
        temp_image = enhancer.enhance(sharpness_factor)

        # Apply Color
        enhancer = ImageEnhance.Color(temp_image)
        temp_image = enhancer.enhance(color_factor)
        
        # Apply Blur if selected
        if blur:
            temp_image = temp_image.filter(ImageFilter.GaussianBlur(radius=2)) # Adjust radius as needed

        self.current_image = temp_image
        return self.current_image

    def get_image_for_display(self, max_size=(800, 600)):
        if not self.current_image:
            return None

        img = self.current_image.copy()
        img.thumbnail(max_size, Image.Resampling.LANCZOS) # Resize for display, maintaining aspect ratio
        self.display_image_tk = ImageTk.PhotoImage(img) # Store as instance variable
        return self.display_image_tk

    def save_image(self, path):
        if self.current_image:
            try:
                self.current_image.save(path)
                messagebox.showinfo("Success", f"Image saved successfully to {path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image: {e}")
        else:
            messagebox.showwarning("Warning", "")


class ImageEnhancerApp:
    """
    Tkinter GUI for the Image Enhancer.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Python Image Enhancer")
        self.root.geometry("1200x800")

        self.enhancer = ImageEnhancer()

        self._create_widgets()
        self._setup_layout()
        self._reset_sliders() # Initialize slider values

    def _create_widgets(self):
        # --- Control Frame ---
        self.control_frame = ttk.Frame(self.root, padding="10")
        self.control_frame.grid(row=0, column=0, sticky="nsew")
        
        ttk.Label(self.control_frame, text="Controls", font=("Arial", 14, "bold")).pack(pady=10)

        # Open/Save/Reset Buttons
        ttk.Button(self.control_frame, text="Open Image", command=self._open_image).pack(pady=5, fill="x")
        ttk.Button(self.control_frame, text="Save Image", command=self._save_image).pack(pady=5, fill="x")
        ttk.Button(self.control_frame, text="Reset Image", command=self._reset_image_and_sliders).pack(pady=5, fill="x")

        # Separator
        ttk.Separator(self.control_frame, orient="horizontal").pack(fill="x", pady=10)

        # Sliders
        self._create_slider(self.control_frame, "Brightness", 0.1, 3.0, 1.0, self._update_image, "brightness_scale")
        self._create_slider(self.control_frame, "Contrast", 0.1, 3.0, 1.0, self._update_image, "contrast_scale")
        self._create_slider(self.control_frame, "Sharpness", 0.0, 3.0, 1.0, self._update_image, "sharpness_scale")
        self._create_slider(self.control_frame, "Color", 0.0, 3.0, 1.0, self._update_image, "color_scale")

        # Toggles
        self.grayscale_var = tk.BooleanVar(value=False)
        self.blur_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.control_frame, text="Grayscale", variable=self.grayscale_var, command=self._update_image).pack(pady=5, fill="x")
        ttk.Checkbutton(self.control_frame, text="Blur", variable=self.blur_var, command=self._update_image).pack(pady=5, fill="x")

        # --- Image Display Frame ---
        self.image_frame = ttk.Frame(self.root, relief="sunken", borderwidth=2)
        self.image_frame.grid(row=0, column=1, sticky="nsew")

        self.image_label = ttk.Label(self.image_frame)
        self.image_label.pack(expand=True, fill="both")

        # Initial placeholder text
        ttk.Label(self.image_frame, text="Open an image to start enhancing!", font=("Arial", 16)).place(relx=0.5, rely=0.5, anchor="center")

    def _create_slider(self, parent, text, from_, to, default, command, attr_name):
        ttk.Label(parent, text=text).pack(pady=(5, 0))
        scale = Scale(parent, from_=from_, to=to, resolution=0.01,
                      orient=HORIZONTAL, command=command,
                      length=200) # Fixed length for consistency
        scale.set(default)
        scale.pack(pady=(0, 10), fill="x")
        setattr(self, attr_name, scale) # Store scale object as an attribute

    def _setup_layout(self):
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=0) # Control column fixed width
        self.root.grid_columnconfigure(1, weight=1) # Image display column expands

        self.control_frame.grid_columnconfigure(0, weight=1) # Make controls expand horizontally within their frame

    def _open_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif"), ("All Files", "*.*")]
        )
        if file_path:
            if self.enhancer.load_image(file_path):
                self._reset_sliders() # Reset sliders upon loading new image
                self._update_image()
                self.image_label.config(text="") # Clear placeholder text

    def _save_image(self):
        if not self.enhancer.current_image:
            messagebox.showwarning("Warning", "No image to save. Please open an image first.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        if file_path:
            self.enhancer.save_image(file_path)

    def _update_image(self, event=None):
        if not self.enhancer.original_image:
            return

        brightness = self.brightness_scale.get()
        contrast = self.contrast_scale.get()
        sharpness = self.sharpness_scale.get()
        color = self.color_scale.get()
        grayscale = self.grayscale_var.get()
        blur = self.blur_var.get()

        self.enhancer.apply_enhancements(brightness, contrast, sharpness, color, grayscale, blur)
        
        display_img_tk = self.enhancer.get_image_for_display()
        if display_img_tk:
            self.image_label.config(image=display_img_tk)
            self.image_label.image = display_img_tk # Keep a reference!

    def _reset_sliders(self):
        self.brightness_scale.set(1.0)
        self.contrast_scale.set(1.0)
        self.sharpness_scale.set(1.0)
        self.color_scale.set(1.0)
        self.grayscale_var.set(False)
        self.blur_var.set(False)

    def _reset_image_and_sliders(self):
        if self.enhancer.original_image:
            self.enhancer.reset_image()
            self._reset_sliders()
            self._update_image()
        else:
            messagebox.showwarning("Warning", "No image to reset.")

if __name__ == "__main__":
    root = tk.Tk()
    # Apply a modern theme if available (for ttk widgets)
    try:
        root.tk.call("source", "azure.tcl") # Example: Azure theme (requires the .tcl file)
        root.tk.call("set_theme", "light")
    except tk.TclError:
        pass # Fallback to default if theme not found
        # You can also use other built-in themes like 'clam', 'alt', 'default', 'classic'
        # root.tk_set_theme("clam") 

    app = ImageEnhancerApp(root)
    root.mainloop()