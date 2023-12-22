import os
import shutil
import tkinter as tk
from PIL import Image, ImageTk
from collections import deque
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ImageCarousel:
    def __init__(self, root, source_image_folder, carousel_image_folder, image_width=2048, image_height=512, overlap=200, max_images=5):
        self.root = root
        self.source_image_folder = source_image_folder
        self.carousel_image_folder = carousel_image_folder
        self.image_width = image_width
        self.image_height = image_height
        self.overlap = overlap
        self.max_images = max_images
        self.canvas = tk.Canvas(root, width=image_width, height=image_height)
        self.canvas.pack(fill="both", expand=True)
        self.scroll_speed = -3  # Negative value for leftward movement
        self.image_queue = deque()  # Queue to hold up to 3 cycles of images
        self.load_and_queue_images()
        self.scroll_images()

    def load_and_queue_images(self):
        new_image_files = self.get_latest_image_files()
        new_tk_images = self.load_images(new_image_files)

        if new_tk_images:
            # Add new images to the queue
            self.image_queue.append(new_tk_images)

            if len(self.image_queue) > 3:
                # Keep only the last 3 cycles if new images are added
                self.image_queue.popleft()

        if not self.canvas.find_all():  # If canvas is empty, display images
            self.display_next_cycle()

    def get_latest_image_files(self):
        # Get the latest 5 images from the source folder
        source_files = [f for f in os.listdir(self.source_image_folder) if f.endswith('.png')]
        source_files.sort(reverse=True)
        latest_files = source_files[:self.max_images]

        # Copy these images to the carousel folder
        for file in latest_files:
            source_path = os.path.join(self.source_image_folder, file)
            destination_path = os.path.join(self.carousel_image_folder, file)
            if not os.path.exists(destination_path):
                shutil.copy2(source_path, destination_path)

        # Remove older images if there are more than 15 in the carousel folder
        carousel_files = os.listdir(self.carousel_image_folder)
        if len(carousel_files) > 15:
            carousel_files.sort()
            for file in carousel_files[:-15]:
                os.remove(os.path.join(self.carousel_image_folder, file))

        # Return the latest 5 images from the carousel folder
        return latest_files

    def load_images(self, image_files):
        tk_images = []
        for img_file in reversed(image_files):
            img_path = os.path.join(self.carousel_image_folder, img_file)
            try:
                img = Image.open(img_path).resize((self.image_width, self.image_height))
                img_with_fade = self.apply_edge_fade(img)
                tk_images.append(ImageTk.PhotoImage(img_with_fade))
            except IOError as e:
                print(f"Error loading image {img_path}: {e}")
        return tk_images

    def apply_edge_fade(self, image):
        fade_size = 100
        alpha_mask = Image.new('L', (image.width, image.height), 255)
        for x in range(fade_size):
            opacity = int(255 * (x / fade_size))
            for y in range(image.height):
                alpha_mask.putpixel((x, y), opacity)
                alpha_mask.putpixel((image.width - x - 1, y), opacity)
        image.putalpha(alpha_mask)
        return image

    def display_next_cycle(self):
        if self.image_queue:
            self.tk_images = self.image_queue[0]  # Peek at the first set of images without removing it
            self.image_positions = self.initialize_image_positions(self.tk_images)

    def initialize_image_positions(self, tk_images):
        positions = []
        x = 0
        for img in tk_images:
            positions.append(self.canvas.create_image(x, 0, image=img, anchor='nw'))
            x += self.image_width - self.overlap  # Adjust image placement to avoid white space at the end
        return positions

    def scroll_images(self):
        canvas_empty = True
        for i, pos in enumerate(self.image_positions):
            self.canvas.move(pos, self.scroll_speed, 0)
            position = self.canvas.coords(pos)
            if position[0] > -self.image_width:
                canvas_empty = False

            # Instantly transition to the new cycle when the 4th image is fully displayed
            if i == len(self.image_positions) - 2 and position[0] <= 0 and len(self.image_queue) > 1:
                self.canvas.delete("all")  # Clear all images from the canvas
                self.display_next_cycle()  # Display the next cycle immediately
                return  # Exit the function to avoid further scrolling

        if canvas_empty and self.image_queue:
            self.display_next_cycle()

        self.canvas.after(1, self.scroll_images)


class EventHandler(FileSystemEventHandler):
    def __init__(self, carousel):
        self.carousel = carousel

    def on_created(self, event):
        if event.src_path.endswith('.png'):
            self.carousel.load_and_queue_images()

def main():
    root = tk.Tk()
    root.geometry("2048x512")
    source_image_folder = 'C:/Users/harry/OneDrive/Desktop/Code/API_IMG'
    carousel_image_folder = 'C:/Users/harry/OneDrive/Desktop/Code/Carousel_IMG'
    carousel = ImageCarousel(root, source_image_folder, carousel_image_folder)

    event_handler = EventHandler(carousel)
    observer = Observer()
    observer.schedule(event_handler, path=source_image_folder, recursive=False)
    observer.start()

    root.mainloop()
    observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
