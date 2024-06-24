import pygame
import os
import tkinter as tk
from tkinter import simpledialog
import random

# Hàm khởi tạo màn hình nhập liệu với tkinter
def get_monster_attributes():
    root = tk.Tk()
    root.withdraw()  # Ẩn cửa sổ chính của tkinter

    # Hiển thị hộp thoại nhập liệu
    monster1_health = simpledialog.askinteger("Input", "Nhập lượng máu cho quái vật 1:", minvalue=1, maxvalue=500)
    monster1_damage = simpledialog.askinteger("Input", "Nhập lượng sát thương cho quái vật 1:", minvalue=1, maxvalue=100)
    monster2_health = simpledialog.askinteger("Input", "Nhập lượng máu cho quái vật 2:", minvalue=1, maxvalue=500)
    monster2_damage = simpledialog.askinteger("Input", "Nhập lượng sát thương cho quái vật 2:", minvalue=1, maxvalue=100)

    return monster1_health, monster1_damage, monster2_health, monster2_damage

# Khởi tạo Pygame
pygame.init()
pygame.mixer.init()  # Khởi tạo âm thanh

# Kích thước màn hình
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

# Màu sắc
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Tạo màn hình game
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Quái vật đánh nhau")

# Font chữ
font = pygame.font.SysFont(None, 48)
health_font = pygame.font.SysFont(None, 24)
damage_font = pygame.font.SysFont(None, 24)

# Tải âm thanh cho tấn công và tuyệt chiêu
attack_sound = pygame.mixer.Sound('slash-21834.mp3')
ultimate_attack_sound = pygame.mixer.Sound('sword-slash-and-swing-185432.mp3')
attack_sound.set_volume(0.2)
ultimate_attack_sound.set_volume(0.2)


def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

def draw_health_bar(x, y, health, max_health):
    bar_length = 200
    bar_height = 20
    fill = (health / max_health) * bar_length
    outline_rect = pygame.Rect(x, y, bar_length, bar_height)
    fill_rect = pygame.Rect(x, y, fill, bar_height)
    pygame.draw.rect(screen, GREEN, fill_rect)
    pygame.draw.rect(screen, BLACK, outline_rect, 2)

class Monster:
    def __init__(self, name, image_path, x, y, health, damage):
        self.name = name
        self.image = pygame.image.load(image_path)  # Load hình ảnh từ tệp
        self.x = x
        self.y = y
        self.health = health
        self.max_health = health
        self.damage = damage
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.damage_text = ""

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))
        draw_health_bar(self.rect.x, self.rect.y - 30, self.health, self.max_health)
        # Vẽ số máu
        draw_text(f"{self.health}/{self.max_health}", health_font, BLACK, surface, self.rect.x, self.rect.y - 50)
        # Vẽ sát thương
        draw_text(f"Sát thương: {self.damage}", damage_font, BLACK, surface, self.rect.x, self.rect.y + self.rect.height + 10)
        # Vẽ tên
        draw_text(self.name, health_font, BLACK, surface, self.rect.x, self.rect.y - 70)
        # Vẽ thông báo sát thương
        if self.damage_text:
            draw_text(self.damage_text, health_font, BLACK, surface, 20, SCREEN_HEIGHT - 40)

    def attack(self, other):
        damage_dealt = self.damage
        other.health -= damage_dealt
        if other.health < 0:
            other.health = 0
        # Phát âm thanh tấn công
        attack_sound.play()
        # Hiển thị sát thương và tự động xóa sau 2 giây
        self.damage_text = f"{self.name} attacked {other.name} dealt {damage_dealt} damge!"
        pygame.time.set_timer(pygame.USEREVENT, 2000)  # Tạo sự kiện đếm thời gian

    def ultimate_attack(self, other):
        # Tính toán sát thương ngẫu nhiên từ 1 đến 3
        damage_multiplier = random.randint(1, 3)
        damage_dealt = self.damage * damage_multiplier
        # Áp dụng sát thương lên quái vật khác
        other.health -= damage_dealt
        if other.health < 0:
            other.health = 0
        # Phát âm thanh tuyệt chiêu
        ultimate_attack_sound.play()
        # Hiển thị sát thương và tự động xóa sau 2 giây
        self.damage_text = f"{self.name} Use Ultimate {damage_dealt} Damged (x{damage_multiplier}) On {other.name}!"
        pygame.time.set_timer(pygame.USEREVENT, 600)  # Tạo sự kiện đếm thời gian

def main():
    # Nhận lượng máu và sát thương từ người chơi
    monster1_health, monster1_damage, monster2_health, monster2_damage = get_monster_attributes()

    # Khởi tạo quái vật với lượng máu và sát thương người chơi nhập
    monster1 = Monster("Monter 1", "img/Tacke.jpg", 150, SCREEN_HEIGHT // 2, monster1_health, monster1_damage)
    monster2 = Monster("Monter 2", "img/DRa.jpg", SCREEN_WIDTH - 200, SCREEN_HEIGHT // 2, monster2_health, monster2_damage)

    # Phát nhạc nền và giảm âm lượng xuống 50%
    pygame.mixer.music.load('byte-blast-8-bit-arcade-music-background-music-for-video-208780.mp3')
    pygame.mixer.music.set_volume(0.03)  # Giảm âm lượng xuống 50%
    pygame.mixer.music.play(-1)  # Phát lặp lại vô hạn

    running = True
    clock = pygame.time.Clock()

    while running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    monster1.attack(monster2)
                if event.key == pygame.K_l:
                    monster2.attack(monster1)
                if event.key == pygame.K_SPACE:  # Kích hoạt Tuyệt chiêu cho quái vật 1
                    monster1.ultimate_attack(monster2)
                if event.key == pygame.K_RETURN:  # Kích hoạt Tuyệt chiêu cho quái vật 2
                    monster2.ultimate_attack(monster1)
            if event.type == pygame.USEREVENT:  # Xóa thông báo sát thương sau 2 giây
                monster1.damage_text = ""
                monster2.damage_text = ""

        monster1.draw(screen)
        monster2.draw(screen)
        if monster1.health <= 0:
            draw_text("Monster 2 Wins!", font, BLACK, screen, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2)
            running = False
        elif monster2.health <= 0:
            draw_text("Monster 1 Wins!", font, BLACK, screen, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2)
            running = False
            



        pygame.display.flip()
        clock.tick(30)  # Giới hạn frame rate

    pygame.quit()

if __name__ == "__main__":
    main()
