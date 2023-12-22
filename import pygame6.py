import os
import time
import pygame
import sys

# 初始化 Pygame
pygame.init()

# 設置窗口大小
window_size = (1024, 256)  # 根據需要調整窗口大小
screen = pygame.display.set_mode(window_size)

# 控制更新速率
clock = pygame.time.Clock()
fps = 10  # 可以根據需要調整每秒幀數

def get_image_files(folder_path):
    """從指定資料夾獲取所有 PNG 圖片檔案"""
    for file in os.listdir(folder_path):
        if file.endswith(".png"):
            yield os.path.join(folder_path, file)

def is_file_stable(file_path, wait_seconds=1):
    """檢查檔案在一段時間內大小是否沒有變化"""
    initial_size = os.path.getsize(file_path)
    time.sleep(wait_seconds)
    return os.path.getsize(file_path) == initial_size

images = []  # 用來存儲圖片路徑的列表

folder_path = r"C:\Users\harry\OneDrive\Desktop\Code\API_IMG"

while True:
    # 更新圖片列表
    for img_file in get_image_files(folder_path):
        if img_file not in images and is_file_stable(img_file):
            images.append(img_file)

    # 從舊到新播放圖片
    for img_path in images:
        try:
            img = pygame.image.load(img_path)
            img = pygame.transform.scale(img, window_size)  # 縮放圖片以適應窗口
            screen.blit(img, (0, 0))
            pygame.display.flip()
            clock.tick(fps)  # 控制更新率
        except Exception as e:
            print(f"Error loading image {img_path}: {e}")

    # 從新到舊播放圖片
    for img_path in reversed(images):
        try:
            img = pygame.image.load(img_path)
            img = pygame.transform.scale(img, window_size)  # 縮放圖片以適應窗口
            screen.blit(img, (0, 0))
            pygame.display.flip()
            clock.tick(fps)  # 控制更新率
        except Exception as e:
            print(f"Error loading image {img_path}: {e}")
