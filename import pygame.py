import pygame
import sys
from PIL import Image, ImageFilter

# 初始化 Pygame
pygame.init()

# 设置窗口大小
width, height = 1024, 512
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

# 图像位置
positions = [(-2048, 0)]  # 所有图像初始位置设置在屏幕左侧之外
current_image = 0  # 当前滚动的图像索引

# 主游戏循环
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 获取当前要滚动的图像及其位置
    x, y = positions[current_image]
    x += 2  # 向右滚动
    positions[current_image] = (x, y)

    # 清空屏幕
    screen.fill((0, 0, 0))

    # 绘制当前图像
    screen.blit(images[current_image], (x, y))

    # 当前图像滚动到屏幕中间时，准备下一张图像
    if x >= width // 2 and current_image < len(images) - 1:
        current_image += 1
        positions.append((-2048, 0))  # 设置下一张图像的初始位置

    pygame.display.flip()  # 更新屏幕显示
    pygame.time.delay(10)

pygame.quit()
sys.exit()
