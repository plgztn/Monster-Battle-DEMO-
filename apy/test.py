import pygame
import os
import tkinter as tk
from tkinter import simpledialog, filedialog
import random

# Hàm khởi tạo màn hình nhập liệu với tkinter
def get_monster_attributes():
    root = tk.Tk()
    root.withdraw()  # Ẩn cửa sổ chính của tkinter

    # Hiển thị hộp thoại nhập liệu
    monster1_health = simpledialog.askinteger("Input", "Nhập lượng máu cho quái vật 1:", minvalue=1, maxvalue=100000)
    monster1_damage = simpledialog.askinteger("Input", "Nhập lượng sát thương cho quái vật 1:", minvalue=1, maxvalue=20000)
    monster1_ultimate_multiplier = simpledialog.askinteger("Input", "Nhập hệ số sát thương tuyệt chiêu cho quái vật 1:", minvalue=1, maxvalue=100)

    monster2_health = simpledialog.askinteger("Input", "Nhập lượng máu cho quái vật 2:", minvalue=1, maxvalue=100000)
    monster2_damage = simpledialog.askinteger("Input", "Nhập lượng sát thương cho quái vật 2:", minvalue=1, maxvalue=20000)
    monster2_ultimate_multiplier = simpledialog.askinteger("Input", "Nhập hệ số sát thương tuyệt chiêu cho quái vật 2:", minvalue=1, maxvalue=100)

    # Lựa chọn hình ảnh cho quái vật 1
    monster1_image = filedialog.askopenfilename(initialdir="images", title="Chọn hình ảnh cho quái vật 1", filetypes=(("Image files", ".jpg *.png"), ("all files", ".*")))
    # Lựa chọn hình ảnh cho quái vật 2
    monster2_image = filedialog.askopenfilename(initialdir="images", title="Chọn hình ảnh cho quái vật 2", filetypes=(("Image files", ".jpg *.png"), ("all files", ".*")))

    return monster1_health, monster1_damage, monster1_ultimate_multiplier, monster1_image, monster2_health, monster2_damage, monster2_ultimate_multiplier, monster2_image

# Khởi tạo Pygame
pygame.init()
pygame.mixer.init()  # Khởi tạo âm thanh

# Kích thước màn hình
SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 900

# Màu sắc
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

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
attack_sound.set_volume(0.5)
ultimate_attack_sound.set_volume(0.5)

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

def draw_health_bar(x, y, health, max_health):
    bar_length = 250
    bar_height = 30
    fill = (health / max_health) * bar_length
    outline_rect = pygame.Rect(x, y, bar_length, bar_height)
    fill_rect = pygame.Rect(x, y, fill, bar_height)
    pygame.draw.rect(screen, RED, fill_rect)
    pygame.draw.rect(screen, BLACK, outline_rect, 2)

    # Vẽ số máu bị trừ
    if health < max_health:
        damage_taken = max_health - health
        damage_text = f"-{damage_taken} HP"
        draw_text(damage_text, health_font, RED, screen, x + bar_length + 10, y)

class Monster:
    def __init__(self, name, image_path, x, y, health, damage, ultimate_multiplier):
        self.name = name
        self.image = pygame.image.load(image_path)  # Load hình ảnh từ tệp
        self.image = pygame.transform.scale(self.image, (250, 250))
        self.x = x
        self.y = y
        self.health = health
        self.max_health = health
        self.damage = damage
        self.ultimate_multiplier = ultimate_multiplier
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.damage_text = ""
        self.attack_count = 0  # Bộ đếm số lần tấn công
        self.ultimate_count = 0  # Bộ đếm số lần dùng tuyệt chiêu
        self.start_time = pygame.time.get_ticks()  # Thời điểm bắt đầu game
        self.is_ultimate_attacking = False
        self.ultimate_effect_start_time = 0

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))
        draw_health_bar(self.rect.x, self.rect.y - 30, self.health, self.max_health)
        # Vẽ số máu--------
        draw_text(f"{self.health}/{self.max_health}", health_font, BLACK, surface, self.rect.x, self.rect.y - 50)
        # Vẽ sát thương-----
        draw_text(f"Damaged: {self.damage}", damage_font, BLACK, surface, self.rect.x, self.rect.y + self.rect.height + 10)
        # Vẽ tên
        draw_text(self.name, health_font, BLACK, surface, self.rect.x, self.rect.y - 70)
        # Vẽ bộ đếm số lần tấn công
        draw_text(f"Attacks: {self.attack_count}", health_font, BLACK, surface, self.rect.x, self.rect.y + self.rect.height + 30)
        # Vẽ bộ đếm số lần dùng tuyệt chiêu
        draw_text(f"Ultimates: {self.ultimate_count}", health_font, BLACK, surface, self.rect.x, self.rect.y + self.rect.height + 50)
        # Vẽ thông báo sát thương
        if self.damage_text:
            if self.name == "Monster 1":
                draw_text(self.damage_text, health_font, BLACK, surface, 20, SCREEN_HEIGHT - 40)
            else:  # Quái vật 2, hiển thị thông báo sát thương bên phải
                draw_text(self.damage_text, health_font, BLACK, surface, SCREEN_WIDTH - 450, SCREEN_HEIGHT - 40)

        # Vẽ bộ đếm thời gian trên màn hình
        elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000
        timer_text = f"Time: {elapsed_time} s"
        draw_text(timer_text, health_font, BLACK, surface, SCREEN_WIDTH // 2 - 50, 20)

        # Vẽ hiệu ứng tấn công khi dùng Tuyệt Kĩ
        if self.is_ultimate_attacking:
            current_time = pygame.time.get_ticks()
            if current_time - self.ultimate_effect_start_time < 500:  # Hiệu ứng kéo dài 500ms
                effect_radius = 200 + (current_time - self.ultimate_effect_start_time) // 5
                pygame.draw.circle(surface, YELLOW, (self.rect.centerx, self.rect.centery), effect_radius, 5)
            else:
                self.is_ultimate_attacking = False

    def attack(self, other):
        damage_dealt = self.damage
        other.health -= damage_dealt
        if other.health < 0:
            other.health = 0
        # Phát âm thanh tấn công
        attack_sound.play()
        # Hiển thị sát thương và tự động xóa sau 2 giây
        self.damage_text = f"{self.name} attacked {other.name} dealt {damage_dealt} damage!"
        pygame.time.set_timer(pygame.USEREVENT, 2500)  # Tạo sự kiện đếm thời gian
        self.attack_count += 1  # Tăng bộ đếm số lần tấn công

    def ultimate_attack(self, other):
        # Tính toán sát thương ngẫu nhiên từ 1 đến hệ số người dùng nhập
        damage_multiplier = random.randint(1, self.ultimate_multiplier)
        damage_dealt = self.damage * damage_multiplier
        # Áp dụng sát thương lên quái vật khác
        other.health -= damage_dealt
        if other.health < 0:
            other.health = 0
        # Phát âm thanh tuyệt chiêu
        ultimate_attack_sound.play()
        # Hiển thị sát thương và tự động xóa sau 2 giây
        self.damage_text = f"{self.name} Use Ultimate {damage_dealt} Damaged (x{damage_multiplier}) On {other.name}!"
        pygame.time.set_timer(pygame.USEREVENT, 2000)  # Tạo sự kiện đếm thời gian
        self.ultimate_count += 1  # Tăng bộ đếm số lần dùng tuyệt chiêu
        # Kích hoạt hiệu ứng tấn công Tuyệt Kĩ
        self.is_ultimate_attacking = True
        self.ultimate_effect_start_time = pygame.time.get_ticks()
        self.attack_count = 0

    def heal(self, amount):
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health

def main():
    show_buttons = False  # Ẩn nút "Chơi lại" và "Kết thúc" khi game bắt đầu
    game_over = False  # Trạng thái game over
    # Nhập lượng máu và sát thương từ người chơi
    monster1_health, monster1_damage, monster1_ultimate_multiplier, monster1_image, monster2_health, monster2_damage, monster2_ultimate_multiplier, monster2_image = get_monster_attributes()

    # Khởi tạo quái vật với lượng máu và sát thương người chơi nhập
    monster1 = Monster("Monster 1", monster1_image, 150, SCREEN_HEIGHT // 2, monster1_health, monster1_damage, monster1_ultimate_multiplier)
    monster2 = Monster("Monster 2", monster2_image, SCREEN_WIDTH - 200, SCREEN_HEIGHT // 2, monster2_health, monster2_damage, monster2_ultimate_multiplier)

    # Phát nhạc nền và giảm âm lượng xuống 50%
    pygame.mixer.music.load('byte-blast-8-bit-arcade-music-background-music-for-video-208780.mp3')
    pygame.mixer.music.set_volume(0.2)  # Giảm âm lượng xuống 50%
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
                if event.key == pygame.K_s:  # Hồi máu cho quái vật 1
                    heal_amount = simpledialog.askinteger("Input", "Nhập lượng máu hồi phục cho quái vật 1:", minvalue=1, maxvalue=100000)
                    if heal_amount:
                        monster1.heal(heal_amount)
                if event.key == pygame.K_k:  # Hồi máu cho quái vật 2
                    heal_amount = simpledialog.askinteger("Input", "Nhập lượng máu hồi phục cho quái vật 2:", minvalue=1, maxvalue=100000)
                    if heal_amount:
                        monster2.heal(heal_amount)
            if event.type == pygame.USEREVENT:  # Xóa thông báo sát thương sau 2 giây
                monster1.damage_text = ""
                monster2.damage_text = ""

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a or event.key == pygame.K_l or event.key == pygame.K_SPACE or event.key == pygame.K_RETURN or event.key == pygame.K_s or event.key == pygame.K_k:
                    if monster1.health <= 0 or monster2.health <= 0:
                        show_buttons = True
            # Xử lý sự kiện khi click chuột
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if show_buttons:
                    mouse_pos = pygame.mouse.get_pos()
                    # Nếu người chơi nhấp vào nút "Chơi lại"
                    if play_again_button_rect.collidepoint(mouse_pos):
                        game_over = False
                        show_buttons = False
                        main()
                    # Nếu người chơi nhấp vào nút "Kết thúc"
                    elif quit_button_rect.collidepoint(mouse_pos):
                        running = False
        monster1.draw(screen)
        monster2.draw(screen)
        # Vẽ chữ "VS" ở giữa hai quái vật
        draw_text("VS", font, RED, screen, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2)

        if monster1.health <= 0 or monster2.health <= 0:
            game_over = True

        if game_over and show_buttons:
            # Vẽ nút "Chơi lại"
            play_again_button_rect = pygame.draw.rect(screen, RED, (SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 50, 200, 50))
            draw_text("Play Again", font, WHITE, screen, SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 60)

            # Vẽ nút "Kết thúc"
            quit_button_rect = pygame.draw.rect(screen, RED, (SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 120, 200, 50))
            draw_text("End.", font, WHITE, screen, SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 130)
        pygame.display.flip()
        clock.tick(30)  # Giới hạn frame rate

    pygame.quit()
if __name__ == "__main__":
    main()