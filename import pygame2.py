import pygame
import sys
from PIL import Image, ImageFilter

# 初始化 Pygame
pygame.init()

# 设置窗口大小
width, height = 1024, 512  # 调整窗口尺寸
screen = pygame.display.set_mode((width, height))

# 加载并处理图像以创建羽化效果
def load_feathered_image(path):
    pil_image = Image.open(path)
    mask = Image.new("L", pil_image.size, 0)
    mask_data = []

    # 创建羽化效果
    for y in range(pil_image.height):
        for x in range(pil_image.width):
            mask_data.append(min(x, y, pil_image.width - x, pil_image.height - y))
    mask.putdata(mask_data)
    pil_image.putalpha(mask)

    return pygame.image.fromstring(pil_image.tobytes(), pil_image.size, pil_image.mode).convert_alpha()

# 加载图像
images = [load_feathered_image(f'image_{i}.png') for i in range(1, 6)]

# 图像位置和透明度
# 考虑图像宽度，设置合适的初始位置
positions = [(-1365 * i, 0) for i in range(5)]
alphas = [0 for _ in range(5)]  # 初始完全透明

# 主游戏循环
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 绘制图像
    for i, image in enumerate(images):
        x, y = positions[i]
        x = (x + 2) % (2048 + 1365)  # 让图像循环滚动，确保展示至少三分之二
        positions[i] = (x, y)

        if x < width:  # 当图像在屏幕内时增加透明度
            alphas[i] = min(alphas[i] + 1, 255)
        image.set_alpha(alphas[i])
        screen.blit(image, (x, y))

    pygame.display.flip()  # 更新屏幕显示
    pygame.time.delay(10)

pygame.quit()
sys.exit()

