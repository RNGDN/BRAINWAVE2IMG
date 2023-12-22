import pygame
import sys
from PIL import Image, ImageFilter

# Initialize Pygame
pygame.init()

# Set window size
width, height = 1800, 500 # Adjust window size
screen = pygame.display.set_mode((width, height))

# Load and process the image to create the feathering effect
def load_feathered_image(path):
     pil_image = Image.open(path)
     mask = Image.new("L", pil_image.size, 0)
     mask_data = []

     # Create feathering effect
     for y in range(pil_image.height):
         for x in range(pil_image.width):
             mask_data.append(min(x, y, pil_image.width - x, pil_image.height - y))
     mask.putdata(mask_data)
     pil_image.putalpha(mask)

     return pygame.image.fromstring(pil_image.tobytes(), pil_image.size, pil_image.mode).convert_alpha()

#Load image
images = [load_feathered_image(f'image_{i}.png') for i in range(1, 6)]

# Image position and transparency
# Consider the image width and set an appropriate initial position
positions = [(-500 * i, 0) for i in range(5)]
alphas = [0 for _ in range(5)] #Initially completely transparent

# Main game loop
running=True
while running:
     for event in pygame.event.get():
         if event.type == pygame.QUIT:
             running=False

     # draw image
     for i, image in enumerate(images):
         x, y = positions[i]
         x = (x + 1) % 900 # Let the image scroll in a loop
         positions[i] = (x, y)

         if x < (width - 900): # Increase transparency when the image is within the screen
             alphas[i] = min(alphas[i] + 1, 255)
         image.set_alpha(alphas[i])
         screen.blit(image, (x, y))

     pygame.display.flip() # Update screen display
     pygame.time.delay(10)

pygame.quit()
sys.exit()