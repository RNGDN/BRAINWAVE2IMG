import os
import tkinter as tk
from PIL import Image, ImageTk, ImageOps
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ImageCarousel:
    def __init__(self, root, image_folder, image_width=960, image_height=540, overlap=50):
        self.root = root
        self.image_folder = image_folder
        self.image_width = image_width
        self.image_height = image_height
        self.overlap = overlap
        self.canvas = tk.Canvas(root, width=image_width, height=image_height, bg='black')
        self.canvas.pack(fill="both", expand=True)
        self.image_files = self.get_image_files()
        self.tk_images = self.load_images(self.image_files)
        self.image_positions = self.initialize_image_positions(self.tk_images)
        self.scroll_images()


    def get_image_files(self):
        def extract_number(f):
            num_part = f.split('-')[0]  # Splitting based on the hyphen and taking the first part
            try:
                return int(num_part)  # Converting that part to an integer
            except ValueError:
                return 0  # In case the conversion fails, return 0

        png_files = [f for f in os.listdir(self.image_folder) if f.endswith('.png')]
        png_files.sort(key=extract_number)  # Sorting based on the extracted number
        return png_files

    def load_images(self, image_files):
        tk_images = []
        for img_file in image_files:
            img_path = os.path.join(self.image_folder, img_file)
            if self.is_valid_image(img_path):
                try:
                    img = Image.open(img_path).resize((self.image_width, self.image_height))
                    img_with_fade = self.apply_edge_fade(img)
                    tk_images.append(ImageTk.PhotoImage(img_with_fade))
                except IOError:
                    print(f"Unable to load image: {img_path}")
        return tk_images

    def is_valid_image(self, file_path):
        try:
            with open(file_path, 'rb') as file:
                file.seek(0, os.SEEK_END)
                return file.tell() > 0
        except IOError:
            return False

    def apply_edge_fade(self, image):
        fade_size = 30  # Width of the fade effect on each side
        alpha_mask = Image.new('L', (image.width, image.height), 255)  # Create an alpha mask

        # Apply fade effect on the edges
        for x in range(fade_size):
            opacity = int(255 * (x / fade_size))
            for y in range(image.height):
                alpha_mask.putpixel((x, y), opacity)
                alpha_mask.putpixel((image.width - x - 1, y), opacity)

        image.putalpha(alpha_mask)
        return image

    def initialize_image_positions(self, tk_images):
        positions = []
        x = 0
        for img in tk_images:
            positions.append(self.canvas.create_image(x, 135, image=img, anchor='nw'))
            x += self.image_width - self.overlap
        return positions

    def scroll_images(self):
        for pos in self.image_positions:
            self.canvas.move(pos, -2, 0)  # Move images to the left
        self.canvas.after(15, self.scroll_images)  # Adjust speed here

    def add_new_image(self, img_path):
        if self.is_valid_image(img_path):
            try:
                img = Image.open(img_path).resize((self.image_width, self.image_height))
                img_with_fade = self.apply_edge_fade(img)
                tk_img = ImageTk.PhotoImage(img_with_fade)
                x = self.image_positions[-1] + self.image_width - self.overlap
                pos = self.canvas.create_image(x, 0, image=tk_img, anchor='nw')
                self.image_positions.append(pos)
                self.tk_images.append(tk_img)
            except IOError:
                print(f"Unable to load image: {img_path}")

class EventHandler(FileSystemEventHandler):
    def __init__(self, carousel):
        self.carousel = carousel

    def on_created(self, event):
        if event.src_path.endswith('.png'):
            self.carousel.add_new_image(event.src_path)

def main():
    root = tk.Tk()
    root.geometry("1000x500")
    image_folder = 'C:\\Users\\harry\\OneDrive\\Desktop\\Code\\Carousel_IMG'
    carousel = ImageCarousel(root, image_folder)

    event_handler = EventHandler(carousel)
    observer = Observer()
    observer.schedule(event_handler, path=image_folder, recursive=False)
    observer.start()

    root.mainloop()
    observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
