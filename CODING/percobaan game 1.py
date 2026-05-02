import os
import json
from datetime import datetime
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
IMAGE_PATH = os.path.join(PROJECT_DIR, "GAMBAR_CODING")
SOUND_PATH = os.path.join(PROJECT_DIR, "SOUND_CODING")
JSON_PATH = os.path.join(PROJECT_DIR, "json")

import pygame
import sys
import random

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

try:
    pygame.mixer.init()
    pygame.mixer.set_num_channels(8)
    AUDIO_ENABLED = True
except pygame.error as error:
    AUDIO_ENABLED = False
    print(f"Audio tidak aktif: {error}")


class SilentSound:
    is_silent = True

    def set_volume(self, volume):
        pass


class SilentChannel:
    def play(self, *args, **kwargs):
        pass

    def stop(self):
        pass

    def fadeout(self, *args, **kwargs):
        pass


def get_channel(index):
    if AUDIO_ENABLED:
        return pygame.mixer.Channel(index)
    return SilentChannel()


def set_music_volume(value):
    if AUDIO_ENABLED:
        pygame.mixer.music.set_volume(value)

# ==================================================
# LAYAR
# ==================================================
WIDTH, HEIGHT = 1200, 600
layar = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PROTOTYPE THE LAST OF ANCALA")
FPS = 60
clock = pygame.time.Clock()

# ==================================================
# WARNA & FONT
# ==================================================
WHITE = (255, 255, 255)
GREEN = (70, 200, 70)
RED = (200, 60, 60)

font = pygame.font.SysFont(None, 32)
menu_font = pygame.font.SysFont(None, 45)

tutorial_font_big = pygame.font.SysFont("arialblack", 64)
tutorial_font_small = pygame.font.SysFont("arialblack", 38)
cutscene_font_title = pygame.font.SysFont("georgia", 58, bold=True)
cutscene_font_body = pygame.font.SysFont("georgia", 34)
cutscene_font_italic = pygame.font.SysFont("georgia", 34, italic=True)

# ==================================================
# VOLUME
# ==================================================
volume = 0.5
set_music_volume(volume)

# ==================================================
# WORLD
# ==================================================
BASE_WORLD_WIDTH = 8000
WORLD_WIDTH = BASE_WORLD_WIDTH
CAMERA_X = 0
LANTAI = 500
TILE_SIZE = 50
KOTAK = 200
BASE_GRAVITASI = 0.6
GRAVITASI = BASE_GRAVITASI
feedback_start_time = 0  
show_feedback = False
death_fade_alpha = 0

KAYU_WIDTH = 150
KAYU_HEIGHT = 50

RESPAWN_MAX = 3
respawn_left = RESPAWN_MAX

# =========================
# TUTORIAL GLOBAL FLAG
# =========================
tutorial_permanently_disabled = False

# ==================================================
# GAME STATE
# ==================================================
MENU = "menu"
AWAL = "awal"

SAVE_DATA = "save_data"
PROGRESS = "progress"
CREDIT = "credit"
COLLECTION = "collection"
PLAY = "play"
OPTIONS = "options"
PAUSE = "pause"

CUTSCENE = "cutscene"
LOSE_CUTSCENE = "lose_cutscene"
WIN_CUTSCENE = "win_cutscene"

game_state = AWAL
previous_state = MENU

VICTORY = "victory"
GAME_OVER = "game_over"
DYING = "dying"
WINNING = "winning"
DEATH_SLOW_DURATION = 1400
DEATH_FADE_DURATION = 1100

# ==================================================
# PLAYER
# ==================================================
PLAYER_WIDTH = 47
PLAYER_HEIGHT = 90

PLAYER_RUN_WITDH = 80
PLAYER_RUN_HEIGHT = 90

PLAYER_SPEED = 5
PLAYER_VELOCITY_Y = -12
GRAVITASI = 0.6

PLAYER_X = 50
PLAYER_SPAWN_Y = LANTAI - PLAYER_HEIGHT

PLAYER_JUMP_WITDH = 65
PLAYER_JUMP_HEIGHT = 90

# ==================================================
# PLAYER SHOOT
# ==================================================
PLAYER_BULLET_SPEED = 10
PLAYER_BULLET_DAMAGE = 25
PLAYER_SHOOT_COOLDOWN = 2000  
last_player_shoot_time = 0
player_bullets = []
mouse_clicked = False
DEFAULT_PLAYER_SHOOT_COOLDOWN = PLAYER_SHOOT_COOLDOWN

# =========================
# SAVE LAST PLAYER POSITION
# =========================
last_player_x = 0
last_player_y = 0
player_dead_effect = False

# ==================================================
# MUSUH
# ==================================================
MUSUH_WIDTH = 47
MUSUH_HEIGHT = 90
JARAK_MIN_MUSUH = 500
PELURU_SPEED = 8
SHOOT_DELAY = 90
PELURU_DAMAGE = 3
MUSUH_SPEED = 2
MUSUH_BODY_DAMAGE = 1
MELEE_RANGE = 70
MELEE_COOLDOWN = 60
MELEE_DAMAGE = 8
MUSUH_MAX_HEALTH = 75
hit_flash_time = 0

DIFFICULTY_CONFIG = {
    "MUDAH": {
        "enemy_speed": 1.2,
        "shoot_delay": 130,
        "bullet_damage": 1,
        "body_damage": 1,
        "melee_damage": 4,
        "enemy_spawns": [
            (1050, "ranged"), (1550, "melee"), (2250, "ranged"), (3050, "melee")
        ],
        "obstacle_spawns": [900, 1350, 1950, 2650, 3450, 4400]
    },
    "NORMAL": {
        "enemy_speed": 2,
        "shoot_delay": 90,
        "bullet_damage": 3,
        "body_damage": 1,
        "melee_damage": 8,
        "enemy_spawns": [
            (1050, "ranged"), (1450, "melee"), (1900, "ranged"), (2400, "melee"),
            (3150, "ranged"), (3900, "melee"), (4750, "ranged")
        ],
        "obstacle_spawns": [850, 1200, 1600, 2100, 2550, 3000, 3650, 4300, 5000, 5900]
    },
    "SUSAH": {
        "enemy_speed": 3,
        "shoot_delay": 55,
        "bullet_damage": 5,
        "body_damage": 2,
        "melee_damage": 12,
        "enemy_spawns": [
            (980, "ranged"), (1300, "melee"), (1650, "ranged"), (2050, "melee"),
            (2500, "ranged"), (2950, "melee"), (3500, "ranged"), (4150, "melee"),
            (4850, "ranged"), (5600, "melee"), (6500, "ranged")
        ],
        "obstacle_spawns": [
            780, 1050, 1350, 1700, 2050, 2380, 2750, 3150,
            3600, 4050, 4550, 5050, 5600, 6150, 6800, 7300
        ]
    },
}

player_name = ""
name_input_active = False
selected_difficulty = None
save_warning_text = ""
save_warning_start_time = 0

DEVELOPER_NAMES = ["MIRZA", "DHENI"]
collection_message = ""
selected_progress_slot = 1
credit_start_time = 0
cutscene_start_time = 0
lose_cutscene_start_time = 0
win_cutscene_start_time = 0
death_start_time = 0
win_delay_start_time = 0

CREDIT_SCENE_DURATIONS = [2200, 3000, 4000, 3000, 4000, 2200, 3000, 2100]
CUTSCENE_SCENE_DURATIONS = [3300, 3900, 5600, 4200, 3600]
LOSE_CUTSCENE_SCENE_DURATIONS = [3600, 3000, 5000, 5800, 4200, 3600]
WIN_CUTSCENE_SCENE_DURATIONS = [2800, 3600, 3600, 3800, 3600, 3400, 3000, 5200]

IMAGE_ALIASES = {
    "HAL AWAL.png": "awal bg.png",
    "play.png": "mulai.png",
    "HAL KEDUA.png": "mulai bg.png",
    "6.png": "pengaturan bg.png",
    "14.png": "save data bg.png",
    "8.png": "pause bg.png",
    "13.png": "progress bg.png",
    "7.png": "progress bg.png",
    "volume.png": "pengaturan.png",
    "10.png": "mati bg.png",
    "9.png": "menang bg.png",
    "level 1 bg.png": "level 3 bg.png",
    "grasslvl1.png": "grasslvl3.png",
    "level 2 bg.png": "level 3 bg.png",
    "grasslvl2.png": "grasslvl3.png",
    "options.png": "pengaturan.png",
    "exit.png": "keluar.png",
    "resume.png": "lanjut.png",
    "bullets.jpeg": "peluru.png",
    "health.jpeg": "darah.png",
    "gravity.jpeg": "lompat.png",
    "respawn.png": "lanjut.png",
    "next.png": "lanjut.png",
    "restart.png": "ulang.png",
    "quit.png": "keluar.png",
    "2.png": "3.png",
}


def resolve_asset_path(folder, name, aliases=None):
    path = os.path.join(folder, name)
    if os.path.exists(path):
        return path

    alias = aliases.get(name) if aliases else None
    if alias:
        alias_path = os.path.join(folder, alias)
        if os.path.exists(alias_path):
            return alias_path

    raise FileNotFoundError(f"Asset '{name}' tidak ditemukan di folder {folder}")


def load_sound(name, volume=1.0):
    if not AUDIO_ENABLED:
        return SilentSound()
    try:
        sound = pygame.mixer.Sound(resolve_asset_path(SOUND_PATH, name))
        sound.set_volume(volume)
        return sound
    except (FileNotFoundError, pygame.error) as error:
        print(f"Sound gagal dimuat ({name}): {error}")
        return SilentSound()

# ==================================================
# LOAD IMAGE
# ==================================================
def load_image(name, scale=None):
    try:
        path = resolve_asset_path(IMAGE_PATH, name, IMAGE_ALIASES)
        img = pygame.image.load(path).convert_alpha()
        if scale:
            img = pygame.transform.scale(img, scale)
        return img
    except (FileNotFoundError, pygame.error) as error:
        print(f"Image gagal dimuat ({name}): {error}")
        size = scale or (80, 40)
        placeholder = pygame.Surface(size, pygame.SRCALPHA)
        placeholder.fill((200, 60, 60, 180))
        pygame.draw.rect(placeholder, (255, 255, 255), placeholder.get_rect(), 2)
        return placeholder

#Background awal game
awal_bg = load_image("HAL AWAL.png", (WIDTH, HEIGHT))
awal_button_img = load_image("play.png",(260,60))

# Backgrounds & UI
menu_bg = load_image("HAL KEDUA.png", (WIDTH, HEIGHT))
options_bg = load_image("6.png", (WIDTH, HEIGHT))
progress_bg = load_image("progress bg.png", (WIDTH, HEIGHT))
credit_bg = load_image("kredit bg.png", (WIDTH, HEIGHT))
collection_bg = load_image("koleksi bg.png", (WIDTH, HEIGHT))

save_data_bg = load_image("14.png", (WIDTH, HEIGHT))

pause_bg_img = load_image("8.png", (WIDTH, HEIGHT))
kontrol_bg = load_image("13.png", (WIDTH, HEIGHT))
suara_bg= load_image("7.png", (WIDTH, HEIGHT))
logo_pause_img = load_image("logo pause 2.png", (50, 50))
volume_img = load_image("volume.png", (260, 60))

game_over_bg = load_image("10.png", (WIDTH, HEIGHT))
victory_bg = load_image("9.png", (WIDTH, HEIGHT))

level1_bg = load_image("level 1 bg.png", (WIDTH, HEIGHT))
land_lvl1 = load_image("grasslvl1.png", (WIDTH, 550))

level2_bg = load_image("level 2 bg.png", (WIDTH, HEIGHT))
land_lvl2 = load_image("grasslvl2.png", (WIDTH, HEIGHT))

level3_bg = load_image("level 3 bg.png", (WIDTH, HEIGHT))
land_lvl3 = load_image("grasslvl3.png", (WIDTH, HEIGHT))

# Buttons
play_img = load_image("play.png", (260, 60))
options_img = load_image("options.png", (260, 60))
exit_img = load_image("exit.png", (260, 60))
kredit_img = load_image("kredit.png", (220, 52))
koleksi_img = load_image("koleksi.png", (220, 52))
main_img = load_image("main.png", (260, 60))

pause_resume_img = load_image("resume.png", (260, 60))
pause_exit_img = load_image("exit.png", (260, 60))

bullets_img = load_image("bullets.jpeg", (200, 90))
health_img = load_image("health.jpeg", (200, 90))
gravity_img = load_image("gravity.jpeg", (200, 90))

respawn_img = load_image("respawn.png", (260,60))
next_img = load_image("next.png", (260, 60))
restart_img = load_image("restart.png", (260,60))
quit_img = load_image("quit.png", (260,60))

# Player & Musuh
player_right = load_image("player right.png", (PLAYER_WIDTH, PLAYER_HEIGHT))
player_left = load_image("player left.png", (PLAYER_WIDTH, PLAYER_HEIGHT))

player_run_0_right = load_image("0.png", (PLAYER_RUN_WITDH, PLAYER_RUN_HEIGHT))
player_run_1_right = load_image("1.png", (PLAYER_RUN_WITDH, PLAYER_RUN_HEIGHT))
player_run_2_right = load_image("2.png", (PLAYER_RUN_WITDH, PLAYER_RUN_HEIGHT))
player_run_3_right = load_image("3.png", (PLAYER_RUN_WITDH, PLAYER_RUN_HEIGHT))
player_run_4_right = load_image("4.png", (PLAYER_RUN_WITDH, PLAYER_RUN_HEIGHT))

player_run_0_left = load_image("0 left.png", (PLAYER_RUN_WITDH, PLAYER_RUN_HEIGHT))
player_run_1_left = load_image("1 left.png", (PLAYER_RUN_WITDH, PLAYER_RUN_HEIGHT))
player_run_2_left = load_image("2 left.png", (PLAYER_RUN_WITDH, PLAYER_RUN_HEIGHT))
player_run_3_left = load_image("3 left.png", (PLAYER_RUN_WITDH, PLAYER_RUN_HEIGHT))
player_run_4_left = load_image("4 left.png", (PLAYER_RUN_WITDH, PLAYER_RUN_HEIGHT))

player_jump_0_right = load_image("0 lompat kanan.png", (PLAYER_JUMP_WITDH, PLAYER_JUMP_HEIGHT))
player_jump_1_right = load_image("1 lompat kanan.png", (PLAYER_JUMP_WITDH, PLAYER_JUMP_HEIGHT))

player_jump_0_left = load_image("0 lompat kiri.png", (PLAYER_JUMP_WITDH, PLAYER_JUMP_HEIGHT))
player_jump_1_left = load_image("1 lompat kiri.png", (PLAYER_JUMP_WITDH, PLAYER_JUMP_HEIGHT))

player_jump_right = [
    player_jump_0_right,  # naik
    player_jump_1_right   # turun
]

player_jump_left = [
    player_jump_0_left,   # naik
    player_jump_1_left    # turun
]

# MUSUH
musuh_0_img = load_image("musuh 0.png", (MUSUH_WIDTH, MUSUH_HEIGHT))
musuh_1_img = load_image("musuh 1.png", (MUSUH_WIDTH, MUSUH_HEIGHT))
musuh_2_img = load_image("musuh 2.png", (MUSUH_WIDTH, MUSUH_HEIGHT))
musuh_3_img = load_image("musuh 3.png", (MUSUH_WIDTH, MUSUH_HEIGHT))
musuh_4_img = load_image("musuh 4.png", (MUSUH_WIDTH, MUSUH_HEIGHT))

musuh_0_kanan = load_image("musuh 0 kanan.png", (MUSUH_WIDTH, MUSUH_HEIGHT))
musuh_1_kanan = load_image("musuh 1 kanan.png", (MUSUH_WIDTH, MUSUH_HEIGHT))
musuh_2_kanan = load_image("musuh 2 kanan.png", (MUSUH_WIDTH, MUSUH_HEIGHT))
musuh_3_kanan = load_image("musuh 3 kanan.png", (MUSUH_WIDTH, MUSUH_HEIGHT))
musuh_4_kanan = load_image("musuh 4 kanan.png", (MUSUH_WIDTH, MUSUH_HEIGHT))

musuh_frames = [
    musuh_0_img, musuh_1_img, musuh_2_img, musuh_3_img, musuh_4_img
]

musuh_frames_kanan = [
    musuh_0_kanan, musuh_1_kanan, musuh_2_kanan, musuh_3_kanan, musuh_4_kanan
]

fireball_0_img = load_image("fireball 0.png", (20,20))
fireball_1_img = load_image("fireball 1.png", (20,20))
fireball_2_img = load_image("fireball 2.png", (20,20))

fireball_frames = [
    fireball_0_img, fireball_1_img, fireball_2_img
]

# Tile
dekor_img = load_image("kayu.png", (KAYU_WIDTH, KAYU_HEIGHT))
kristal_img = load_image("dekor.png", (118,33))

#Sound
sfx = {
    "click" : load_sound("click.wav", 0.6),
    "game" : load_sound("backsound game.mp3", 1.5),
    "level3" : load_sound("backsound level 3.mp3", 1.5),
    "cutscene" : load_sound("sound cutscene.mp3", 1.2)
}

# jarak musuh muncul 
ENEMY_APPEAR_PLAYER_X = 800

# backsound
menu_bgm = sfx["game"]
menu_bgm_channel = get_channel(1)
menu_bgm_playing = False

ingame_channel = get_channel(2)
ingame_bgm_playing = False
ingame_bgm_key = None

cutscene_bgm = sfx["cutscene"]
cutscene_channel = get_channel(3)
cutscene_bgm_playing = False

def update_bgm():
    global menu_bgm_playing, ingame_bgm_playing, ingame_bgm_key, cutscene_bgm_playing

    if game_state in (CUTSCENE, LOSE_CUTSCENE, WIN_CUTSCENE):
        if menu_bgm_playing:
            menu_bgm_channel.fadeout(500)
            menu_bgm_playing = False
        if ingame_bgm_playing:
            ingame_channel.fadeout(500)
            ingame_bgm_playing = False
            ingame_bgm_key = None

        cutscene_bgm.set_volume(volume)
        if not cutscene_bgm_playing and not getattr(cutscene_bgm, "is_silent", False):
            cutscene_channel.play(cutscene_bgm, loops=-1, fade_ms=500)
            cutscene_bgm_playing = True

    elif game_state not in (PLAY, DYING, WINNING):
        # ===== MENU =====
        if ingame_bgm_playing:
            ingame_channel.fadeout(500)
            ingame_bgm_playing = False
            ingame_bgm_key = None
        if cutscene_bgm_playing:
            cutscene_channel.fadeout(500)
            cutscene_bgm_playing = False

        menu_bgm.set_volume(volume)
        if not menu_bgm_playing and not getattr(menu_bgm, "is_silent", False):
            menu_bgm_channel.play(menu_bgm, loops=-1, fade_ms=500)
            menu_bgm_playing = True

    else:
        # ===== IN GAME =====
        if menu_bgm_playing:
            menu_bgm_channel.fadeout(500)
            menu_bgm_playing = False

        desired_bgm_key = "level3" if enemy_encounter_started() else "cutscene"
        if desired_bgm_key == "cutscene":
            if ingame_bgm_playing:
                ingame_channel.fadeout(500)
                ingame_bgm_playing = False
                ingame_bgm_key = None

            cutscene_bgm.set_volume(volume)
            if not cutscene_bgm_playing and not getattr(cutscene_bgm, "is_silent", False):
                cutscene_channel.play(cutscene_bgm, loops=-1, fade_ms=500)
                cutscene_bgm_playing = True
            return

        if cutscene_bgm_playing:
            cutscene_channel.fadeout(500)
            cutscene_bgm_playing = False

        ingame_bgm = sfx["level3"]
        ingame_bgm.set_volume(volume)

        if ingame_bgm_playing and ingame_bgm_key != "level3":
            ingame_channel.fadeout(500)
            ingame_bgm_playing = False

        if not ingame_bgm_playing and not getattr(ingame_bgm, "is_silent", False):
            ingame_channel.play(ingame_bgm, loops=-1, fade_ms=500)
            ingame_bgm_playing = True
            ingame_bgm_key = "level3"

# Play click SFX instantly (no overlap/loop) and trim long file
CLICK_MAX_MS = 1250
click_channel = get_channel(0)

def play_click():
    if getattr(sfx["click"], "is_silent", False):
        return
    click_channel.stop()
    click_channel.play(sfx["click"], maxtime=CLICK_MAX_MS)


# =============================
# SKILL 
# =============================
SKILL_COOLDOWN = 10000  
last_skill_time = -SKILL_COOLDOWN  
skill_start_time = 0
SKILL_DURATION = 5000  

# ==================================================
# SKILL MODE (SLOW TIME)
# ==================================================
skill_mode = False
slow_time_scale = 0.1
normal_time_scale = 1.0
current_time_scale = 1.0

# ==================================================
# CLASSES
# ==================================================
class Slider: # (VOLUME)
    def __init__(self, x, y, width, height, min_val=0, max_val=1, start_val=0.5):
        self.rect = pygame.Rect(x, y, width, height)
        self.knob_radius = height // 2 + 4
        self.min_val = min_val
        self.max_val = max_val
        self.value = start_val
        self.dragging = False

    def handle_event(self, event):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.Rect(self.rect.x - self.knob_radius, self.rect.y - self.knob_radius,
                           self.rect.width + self.knob_radius*2, self.rect.height + self.knob_radius*2).collidepoint(mouse_x, mouse_y):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                new_x = max(self.rect.x, min(mouse_x, self.rect.x + self.rect.width))
                self.value = (new_x - self.rect.x) / self.rect.width

    def draw(self, surface):
        pygame.draw.rect(surface, (3,3,3), self.rect)
        knob_x = int(self.rect.x + self.value * self.rect.width)
        knob_y = self.rect.y + self.rect.height // 2
        pygame.draw.circle(surface, WHITE, (knob_x, knob_y), self.knob_radius)
        layar.blit(volume_img, (470, 230))

class Player(pygame.Rect): # ( PLAYER)
    def __init__(self):
        super().__init__(PLAYER_X, PLAYER_SPAWN_Y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.image = player_right
        self.velocity_y = 0
        self.direction = "right"
        self.jump_count = 0
        self.max_jump = 2
        self.melompat = False
        self.darah_max = 150
        self.darah = self.darah_max

        # ===== ANIMASI LARI =====
        self.run_frames_right = [
            player_run_0_right, player_run_1_right,
            player_run_2_right, player_run_3_right,
            player_run_4_right
        ]
        self.run_frames_left = [
            player_run_0_left, player_run_1_left,
            player_run_2_left, player_run_3_left,
            player_run_4_left
        ]
        self.run_index = 0
        self.run_timer = 0
        self.RUN_ANIM_SPEED = 6  # makin kecil makin cepat

    def update_image(self):
        keys = pygame.key.get_pressed()
        moving = keys[pygame.K_a] or keys[pygame.K_d]

        # ===== JUMP =====
        if self.melompat:
            if self.velocity_y < 0:  # NAIK
                frame = 0
            else:           # TURUN
                frame = 1

            if self.direction == "right":
                self.image = player_jump_right[frame]
            else:
                self.image = player_jump_left[frame]
            return

        # PRIORITAS 2: LARI
        if moving:
            self.run_timer += 1
            if self.run_timer >= self.RUN_ANIM_SPEED:
                self.run_timer = 0
                self.run_index = (self.run_index + 1) % len(self.run_frames_right)

            if self.direction == "right":
                self.image = self.run_frames_right[self.run_index]
            else:
                self.image = self.run_frames_left[self.run_index]

        # PRIORITAS 3: DIAM
        else:
            self.run_index = 0
            self.image = player_right if self.direction == "right" else player_left

class PlayerBullet(pygame.Rect): # (PLAYER PELURU)
    # Nabrak BOSS
    def __init__(self, x, y, arah):
        super().__init__(x, y, 12, 6)
        self.arah = arah

    def update(self):
        self.x += self.arah * PLAYER_BULLET_SPEED * current_time_scale

    def draw(self):
        pygame.draw.rect(
            layar,
            (255, 255, 0),
            (self.x - CAMERA_X, self.y, self.width, self.height)
        )

def draw_health_bar(): # (HEALTH BAR PLAYER)
    teks_darah = font.render("HEALTH BAR", True, WHITE)
    pygame.draw.rect(layar, RED, (80, 540, player.darah_max * 3, 15))
    pygame.draw.rect(layar, GREEN, (80, 540, int(player.darah * 3), 15))
    layar.blit(teks_darah, (80, 560))


def enemy_encounter_started():
    return player.x > ENEMY_APPEAR_PLAYER_X


class Musuh(pygame.Rect):
    def __init__(self, x, y, attack_type="ranged"):
        super().__init__(x, y, MUSUH_WIDTH, MUSUH_HEIGHT)
        self.attack_type = attack_type

        # ===== ANIMASI =====
        self.frames_left = musuh_frames
        self.frames_right = musuh_frames_kanan
        self.frames = self.frames_left  # default hadap kiri

        self.frame_index = 0
        self.anim_timer = 0
        self.ANIM_SPEED = 8
        self.image = self.frames[0].copy()

        # ===== ARAH =====
        self.direction = "left"

        # ===== STATUS =====
        self.cooldown = 0
        self.speed = MUSUH_SPEED
        self.peluru = []
        self.melee_timer = 0
        self.melee_hit_frame = False
        self.darah_max = MUSUH_MAX_HEALTH
        self.darah = self.darah_max

        # ===== MATI & FADE =====
        self.dead = False
        self.alpha = 255
        self.fade_speed = 8

    def update(self):
        global hit_flash_time

        # ===== FADE SAAT MATI =====
        if self.dead:
            self.alpha -= self.fade_speed
            if self.alpha < 0:
                self.alpha = 0
            self.image.set_alpha(self.alpha)
            return   # STOP LOGIC SAAT MATI

       # HITUNG JARAK KE PLAYER
        old_x = self.x
        jarak = self.centerx - player.centerx
        jarak_abs = abs(jarak)

        if jarak_abs < JARAK_MIN_MUSUH and not (self.attack_type == "melee" and jarak_abs <= MELEE_RANGE):
            if jarak > 0:
                # GERAK KE KIRI
                if self.direction != "left":
                    self.frame_index = 0
                self.x -= self.speed * current_time_scale
                self.direction = "left"
                self.frames = self.frames_left
            else:
                # GERAK KE KANAN
                if self.direction != "right":
                    self.frame_index = 0
                self.x += self.speed * current_time_scale
                self.direction = "right"
                self.frames = self.frames_right

        # === COLLISION TILE ===
        if check_musuh_tile_collision_x(self, old_x):
            return

        # === ANIMASI ===
        self.anim_timer += 1
        if self.anim_timer >= self.ANIM_SPEED:
            self.anim_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index].copy()

        self.cooldown += 1
        if self.melee_timer > 0:
            self.melee_timer -= 1

        # ===== SERANG =====
        if self.attack_type == "melee":
            if jarak_abs <= MELEE_RANGE and self.cooldown >= MELEE_COOLDOWN:
                self.melee_timer = 18
                self.melee_hit_frame = True
                self.cooldown = 0
                if player.colliderect(self.get_melee_rect()):
                    player.darah -= MELEE_DAMAGE
                    player.darah = max(0, player.darah)
                    hit_flash_time = pygame.time.get_ticks()
            elif self.melee_timer <= 0:
                self.melee_hit_frame = False

        elif self.cooldown >= SHOOT_DELAY:
            arah = -1 if jarak > 0 else 1
            vx = arah * PELURU_SPEED
            vy = 0
            self.peluru.append(Fireball(self.centerx, self.centery, vx, vy))
            self.cooldown = 0

        for p in self.peluru[:]:
            p.update()

            if p.colliderect(player):
                player.darah -= PELURU_DAMAGE
                player.darah = max(0, player.darah)
                hit_flash_time = pygame.time.get_ticks()
                self.peluru.remove(p)
                continue

            if enemy_bullet_hits_tile(p):
                self.peluru.remove(p)
                continue

            if p.x < 0 or p.x > WORLD_WIDTH:
                self.peluru.remove(p)

    def get_melee_rect(self):
        if self.direction == "left":
            return pygame.Rect(self.left - MELEE_RANGE, self.centery - 25, MELEE_RANGE, 50)
        return pygame.Rect(self.right, self.centery - 25, MELEE_RANGE, 50)

    def draw(self):
        layar.blit(self.image, (self.x - CAMERA_X, self.y))
        if not self.dead:
            bar_width = 56
            bar_height = 7
            bar_x = self.centerx - CAMERA_X - bar_width // 2
            bar_y = self.y - 14
            fill_width = int(bar_width * (self.darah / self.darah_max))
            pygame.draw.rect(layar, RED, (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(layar, GREEN, (bar_x, bar_y, fill_width, bar_height))
            pygame.draw.rect(layar, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height), 1)
        if self.attack_type == "melee" and self.melee_timer > 0:
            attack_rect = self.get_melee_rect()
            start_x = self.centerx - CAMERA_X
            start_y = self.centery - 8
            end_x = attack_rect.centerx - CAMERA_X
            end_y = attack_rect.centery
            color = (255, 230, 90) if self.melee_hit_frame else (255, 160, 60)
            pygame.draw.line(layar, color, (start_x, start_y), (end_x, end_y), 8)
            pygame.draw.circle(layar, color, (end_x, end_y), 10)
        for p in self.peluru:
            p.draw()


class Fireball(pygame.Rect):
    def __init__(self, x, y, vx, vy):
        self.frames = fireball_frames
        self.frame_index = 0
        self.anim_timer = 0
        self.ANIM_SPEED = 5

        self.image = self.frames[0].copy()
        rect = self.image.get_rect(center=(x, y))
        super().__init__(rect)

        self.vx = vx
        self.vy = vy

    def update(self):
        self.x += self.vx * current_time_scale
        self.y += self.vy * current_time_scale

        old_center = self.center

        self.anim_timer += 1
        if self.anim_timer >= self.ANIM_SPEED:
            self.anim_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index].copy()
            self.center = old_center

        if self.vx < 0:
            self.image = pygame.transform.flip(self.image, True, False)

    def draw(self):
        layar.blit(self.image, (self.x - CAMERA_X, self.y))

class Tile: # (RINTANGAN)
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, KAYU_WIDTH, KAYU_HEIGHT)

    def draw(self):
        layar.blit(dekor_img, (self.rect.x - CAMERA_X, self.rect.y))


def bullet_hits_tile(bullet): # (KETIKA BULLET PLAYER MENABRAK OBJEK)
    for tile in tiles:
        if bullet.colliderect(tile.rect):
            return True
    return False

def enemy_bullet_hits_tile(bullet): # (KETIKA BULLET MUSUH MENABRAK OBJEK)
    for tile in tiles:
        if bullet.colliderect(tile.rect):
            return True
    return False

class Button: # (TOMBOL OPSI. SKILL)
    def __init__(self, image, x, y):
        self.image = image
        self.rect = image.get_rect(center=(x, y))
        self.base_y = y

    def update(self):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()[0]
        self.rect.centery = self.base_y
        if self.rect.collidepoint(mouse):
            self.rect.centery = self.base_y - 6
            if click:
                self.rect.centery = self.base_y + 8

    def draw(self):
        layar.blit(self.image, self.rect)

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(pygame.mouse.get_pos())

# ==================================================
# BUTTON INSTANCES
# ==================================================
awal_button = Button(awal_button_img, WIDTH//2, HEIGHT//2 + 100)

play_button = Button(play_img, WIDTH//2, 270)
options_button = Button(options_img, WIDTH//2, 360)
exit_button = Button(exit_img, WIDTH//2, 450)
kredit_button = Button(kredit_img, 170, HEIGHT - 55)
koleksi_button = Button(koleksi_img, WIDTH - 170, HEIGHT - 55)
progress_exit_button = Button(exit_img, WIDTH//2, HEIGHT - 55)
save_exit_button = Button(exit_img, 170, HEIGHT - 55)
save_main_button = Button(main_img, WIDTH - 170, HEIGHT - 55)

progress_slots = [
    pygame.Rect(WIDTH//2 - 260, 155 + i * 78, 520, 58)
    for i in range(4)
]

name_input_rect = pygame.Rect(WIDTH//2 - 220, 185, 440, 52)
difficulty_rects = {
    "MUDAH": pygame.Rect(WIDTH//2 - 285, 305, 170, 58),
    "NORMAL": pygame.Rect(WIDTH//2 - 85, 305, 170, 58),
    "SUSAH": pygame.Rect(WIDTH//2 + 115, 305, 170, 58),
}
collection_skin_rect = pygame.Rect(WIDTH//2 - 430, 180, 360, 220)
collection_skill_rect = pygame.Rect(WIDTH//2 + 70, 180, 360, 220)
collection_exit_button = Button(exit_img, 170, HEIGHT - 55)
credit_exit_button = Button(exit_img, 170, HEIGHT - 55)

pause_button = Button(logo_pause_img, 50, 50)
pause_resume_button = Button(pause_resume_img, WIDTH//2, 250)
options_pause_button = Button(options_img, WIDTH//2, 350)
pause_exit_button = Button(pause_exit_img, WIDTH//2, 450)

volume_slider = Slider(WIDTH//2 - 150, 330, 300, 20, start_val=volume)

respawn_button = Button(respawn_img, 400, HEIGHT//2)
next_button = Button(next_img, 400, HEIGHT//2)
restart_button = Button(restart_img, 800, HEIGHT//2)
quit_button = Button(quit_img, 600, HEIGHT//2 + 80)

# ======================
# BUTTON SKILL
# ======================
SKILL_Y = HEIGHT // 2
SKILL_GAP = 250

bullets_rect = bullets_img.get_rect(center=(WIDTH//2 - SKILL_GAP, SKILL_Y))
health_rect = health_img.get_rect(center=(WIDTH//2, SKILL_Y))
gravity_rect = gravity_img.get_rect(center=(WIDTH//2 + SKILL_GAP, SKILL_Y))

# ==================================================
# PLAYER & LEVEL START
# ==================================================
player = Player()
current_level = 3
MAX_LEVEL = 3

RESPAWN_MAX = 3
respawn_left = RESPAWN_MAX

tiles = []
musuh_list = []


def apply_difficulty():
    global MUSUH_SPEED, SHOOT_DELAY, PELURU_DAMAGE, MUSUH_BODY_DAMAGE, MELEE_DAMAGE

    config = DIFFICULTY_CONFIG[selected_difficulty]
    MUSUH_SPEED = config["enemy_speed"]
    SHOOT_DELAY = config["shoot_delay"]
    PELURU_DAMAGE = config["bullet_damage"]
    MUSUH_BODY_DAMAGE = config["body_damage"]
    MELEE_DAMAGE = config["melee_damage"]


def create_musuh_list():
    musuh_y = LANTAI - MUSUH_HEIGHT
    config = DIFFICULTY_CONFIG.get(selected_difficulty, DIFFICULTY_CONFIG["NORMAL"])
    return [
        Musuh(x, musuh_y, attack_type)
        for x, attack_type in config["enemy_spawns"]
    ]


def create_obstacle_list():
    obstacle_y = LANTAI - KAYU_HEIGHT
    config = DIFFICULTY_CONFIG.get(selected_difficulty, DIFFICULTY_CONFIG["NORMAL"])
    return [
        Tile(x, obstacle_y)
        for x in config["obstacle_spawns"]
    ]


def can_start_game():
    return bool(player_name.strip()) and selected_difficulty is not None


def get_user_json_path():
    safe_name = "".join(
        char.lower() if char.isalnum() else "_"
        for char in player_name.strip()
    ).strip("_")
    if not safe_name:
        safe_name = "player"
    return os.path.join(JSON_PATH, f"{safe_name}.json")


def get_slot_json_path(slot_number):
    return os.path.join(JSON_PATH, f"slot_{slot_number}.json")


def load_slot_data(slot_number):
    try:
        with open(get_slot_json_path(slot_number), "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError, PermissionError, OSError):
        pass

    try:
        user_files = sorted(
            file_name for file_name in os.listdir(JSON_PATH)
            if file_name.endswith(".json") and not file_name.startswith("slot_")
        )
    except (FileNotFoundError, PermissionError, OSError):
        return None

    for index, file_name in enumerate(user_files, start=1):
        if index != slot_number:
            continue
        try:
            with open(os.path.join(JSON_PATH, file_name), "r", encoding="utf-8") as file:
                return json.load(file)
        except (json.JSONDecodeError, PermissionError, OSError):
            return None

    return None


def save_user_data_to_json():
    try:
        os.makedirs(JSON_PATH, exist_ok=True)
    except (PermissionError, OSError) as error:
        print(f"Progress gagal disimpan: {error}")
        return False

    waktu_bermain = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = {
        "nama": player_name.strip(),
        "difficulty": selected_difficulty,
        "slot": selected_progress_slot,
        "waktu_bermain": waktu_bermain,
        "level": current_level,
        "darah": player.darah_max,
        "respawn_max": RESPAWN_MAX
    }

    try:
        with open(get_user_json_path(), "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        with open(get_slot_json_path(selected_progress_slot), "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
    except (PermissionError, OSError) as error:
        print(f"Progress gagal disimpan: {error}")
        return False

    return True


def try_start_game_from_save():
    global save_warning_text, save_warning_start_time

    if can_start_game():
        start_game_from_save(show_cutscene=True, show_tutorial=True)
        return

    save_warning_text = "ISI NAMA DAN PILIH DIFFICULTY DULU"
    save_warning_start_time = pygame.time.get_ticks()


def start_game_from_save(write_save=True, show_cutscene=False, show_tutorial=False):
    global current_level, game_state, musuh_list, tiles, player_bullets, CAMERA_X
    global respawn_left, player_dead_effect, death_fade_alpha
    global last_player_shoot_time, last_skill_time
    global skill_mode, current_time_scale
    global cutscene_start_time

    apply_difficulty()
    current_level = 3
    if write_save:
        save_user_data_to_json()
    CAMERA_X = 0
    respawn_left = RESPAWN_MAX
    player_dead_effect = False
    death_fade_alpha = 0
    skill_mode = False
    current_time_scale = normal_time_scale
    last_player_shoot_time = 0
    last_skill_time = -SKILL_COOLDOWN
    player_bullets.clear()
    reset_skill_effect()

    player.x = PLAYER_X
    player.y = PLAYER_SPAWN_Y
    player.velocity_y = 0
    player.direction = "right"
    player.jump_count = 0
    player.melompat = False
    player.darah = player.darah_max

    tiles = create_obstacle_list()
    musuh_list = create_musuh_list()
    if show_tutorial:
        reset_control_tutorial()
    else:
        disable_control_tutorial()
    if show_cutscene:
        cutscene_start_time = pygame.time.get_ticks()
        game_state = CUTSCENE
    else:
        game_state = PLAY


def start_game_from_slot(slot_number, slot_data):
    global player_name, selected_difficulty, selected_progress_slot

    player_name = str(slot_data.get("nama", "PLAYER")).strip() or "PLAYER"
    selected_difficulty = slot_data.get("difficulty")
    if selected_difficulty not in DIFFICULTY_CONFIG:
        selected_difficulty = "NORMAL"
    selected_progress_slot = slot_number
    start_game_from_save(write_save=False)


def respawn_player_after_death():
    global game_state, player_dead_effect, death_fade_alpha
    global game_over_fade_alpha, game_over_fade_mode, CAMERA_X
    global skill_mode, current_time_scale

    player_dead_effect = False
    death_fade_alpha = 0
    game_over_fade_alpha = 0
    game_over_fade_mode = None
    skill_mode = False
    current_time_scale = normal_time_scale
    reset_skill_effect()
    player_bullets.clear()

    player.x = max(0, min(last_player_x, WORLD_WIDTH - PLAYER_WIDTH))
    player.y = min(last_player_y, LANTAI - PLAYER_HEIGHT)
    player.velocity_y = 0
    player.jump_count = 0
    player.melompat = False
    player.darah = player.darah_max

    for musuh in musuh_list:
        musuh.peluru.clear()
        musuh.cooldown = 0
        musuh.melee_timer = 0
        musuh.melee_hit_frame = False

    update_camera()
    game_state = PLAY


def start_death_sequence():
    global game_state, death_fade_alpha, death_start_time
    global skill_mode, current_time_scale

    skill_mode = False
    current_time_scale = slow_time_scale
    death_fade_alpha = 0
    death_start_time = pygame.time.get_ticks()
    game_state = DYING


def start_lose_cutscene():
    global game_state, lose_cutscene_start_time
    global current_time_scale

    current_time_scale = normal_time_scale
    lose_cutscene_start_time = pygame.time.get_ticks()
    game_state = LOSE_CUTSCENE


def start_win_cutscene():
    global game_state, win_cutscene_start_time
    global current_time_scale

    current_time_scale = normal_time_scale
    win_cutscene_start_time = pygame.time.get_ticks()
    game_state = WIN_CUTSCENE


def start_win_sequence():
    global game_state, death_fade_alpha, win_delay_start_time
    global skill_mode, current_time_scale

    skill_mode = False
    current_time_scale = slow_time_scale
    death_fade_alpha = 0
    win_delay_start_time = pygame.time.get_ticks()
    player_bullets.clear()
    for musuh in musuh_list:
        musuh.peluru.clear()
    game_state = WINNING

# ==================================================
# TUTORIAL TEXT
# ==================================================
show_level_text = False
show_move_text = False
tutorial_start_time = 0
tutorial_done = False
show_skill_hint = False
skill_hint_shown = False
skill_hint_start_x = 0
show_jump_text = False
jump_done = False
show_double_jump_text = False
double_jump_done = False
show_shot_button = False
shot_button = False
show_q_tutorial = False
q_done = False
k_done = False

TUTORIAL_STEPS = [
    ("a", "A UNTUK MUNDUR"),
    ("d", "D UNTUK MAJU"),
    ("space", "SPACE UNTUK LOMPAT"),
    ("q", "Q UNTUK MENEMBAK"),
    ("k", "K UNTUK SKILL ULTIMATE"),
]
tutorial_step_index = 0
tutorial_active = False
tutorial_alpha = 0
tutorial_fade_mode = "in"


def reset_control_tutorial():
    global tutorial_step_index, tutorial_active, tutorial_alpha, tutorial_fade_mode
    tutorial_step_index = 0
    tutorial_active = True
    tutorial_alpha = 0
    tutorial_fade_mode = "in"


def disable_control_tutorial():
    global tutorial_step_index, tutorial_active, tutorial_alpha, tutorial_fade_mode
    tutorial_step_index = len(TUTORIAL_STEPS)
    tutorial_active = False
    tutorial_alpha = 0
    tutorial_fade_mode = None


def advance_control_tutorial(action):
    global tutorial_fade_mode
    if not tutorial_active or tutorial_fade_mode == "out":
        return
    if tutorial_step_index < len(TUTORIAL_STEPS) and TUTORIAL_STEPS[tutorial_step_index][0] == action:
        tutorial_fade_mode = "out"


def update_control_tutorial():
    global tutorial_step_index, tutorial_active, tutorial_alpha, tutorial_fade_mode
    if not tutorial_active:
        return

    if tutorial_fade_mode == "in":
        tutorial_alpha += 12
        if tutorial_alpha >= 255:
            tutorial_alpha = 255
            tutorial_fade_mode = None
    elif tutorial_fade_mode == "out":
        tutorial_alpha -= 12
        if tutorial_alpha <= 0:
            tutorial_alpha = 0
            tutorial_step_index += 1
            if tutorial_step_index >= len(TUTORIAL_STEPS):
                tutorial_active = False
                tutorial_fade_mode = None
            else:
                tutorial_fade_mode = "in"


def draw_control_tutorial():
    if not tutorial_active or tutorial_step_index >= len(TUTORIAL_STEPS):
        return

    text = TUTORIAL_STEPS[tutorial_step_index][1]
    text_surface = tutorial_font_small.render(text, True, WHITE)
    shadow_surface = tutorial_font_small.render(text, True, (0, 0, 0))
    text_surface.set_alpha(tutorial_alpha)
    shadow_surface.set_alpha(tutorial_alpha)

    rect = text_surface.get_rect(center=(WIDTH//2, 80))
    shadow_rect = rect.copy()
    shadow_rect.x += 3
    shadow_rect.y += 3
    layar.blit(shadow_surface, shadow_rect)
    layar.blit(text_surface, rect)


def draw_center_text_fade(text, font, y_offset=0, alpha=255):
    text_surface = font.render(text, True, (0, 0, 0))
    shadow_surface = font.render(text, True, (60, 60, 60))

    text_surface.set_alpha(alpha)
    shadow_surface.set_alpha(alpha)

    rect = text_surface.get_rect(center=(WIDTH//2, 100 + y_offset))
    shadow_rect = rect.copy()
    shadow_rect.x += 3
    shadow_rect.y += 3

    layar.blit(shadow_surface, shadow_rect)
    layar.blit(text_surface, rect)

# ==================================================
# COLLISION & MOVEMENT
# ==================================================
def check_tile_collision_x(old_x):
    for tile in tiles:
        if player.colliderect(tile.rect):
            if player.x > old_x:
                player.right = tile.rect.left
            else:
                player.left = tile.rect.right

def check_tile_collision_y():
    for tile in tiles:
        if player.colliderect(tile.rect):
            if player.velocity_y > 0:
                player.bottom = tile.rect.top
                player.velocity_y = 0
                player.jump_count = 0
                player.melompat = False
            elif player.velocity_y < 0:
                player.top = tile.rect.bottom
                player.velocity_y = 0

def check_musuh_tile_collision_x(musuh, old_x):
    for tile in tiles:
        if musuh.colliderect(tile.rect):
            if musuh.x > old_x:
                musuh.right = tile.rect.left
            else:
                musuh.left = tile.rect.right
            return True   # Nabrak tile
    return False          # Tidak nabrak

def move_player():
    keyboard = pygame.key.get_pressed()
    old_x = player.x
    if keyboard[pygame.K_a]:
        player.x -= PLAYER_SPEED * current_time_scale
        player.direction = "left"
    if keyboard[pygame.K_d]:
        player.x += PLAYER_SPEED * current_time_scale
        player.direction = "right"
    check_tile_collision_x(old_x)
    player.velocity_y += GRAVITASI * current_time_scale
    player.y += player.velocity_y * current_time_scale
    check_tile_collision_y()
    if player.bottom >= LANTAI:
        player.bottom = LANTAI
        player.velocity_y = 0
        player.jump_count = 0
        player.melompat = False

def update_camera():
    global CAMERA_X
    CAMERA_X = player.x - WIDTH // 2
    if CAMERA_X < 0:
        CAMERA_X = 0
    elif CAMERA_X > WORLD_WIDTH - WIDTH:
        CAMERA_X = WORLD_WIDTH - WIDTH

def draw_dark_overlay(alpha=120):
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(alpha)
    layar.blit(overlay, (0, 0))


def get_credit_scenes():
    names = " & ".join(DEVELOPER_NAMES)
    return [
        ["THE LAST OF ANCALA", "Prototype Version"],
        ["Developed by", names],
        ["Programming", names, "Game Design", names, "Art & UI", names],
        ["Made with", "Python", "Pygame", "Canva"],
        ["Assets & Resources", "Some assets from:", "itch.io", "OpenGameArt", "Freepik", "Special thanks to asset creators"],
        ["Special Thanks", "Guru / Teman / Mentor"],
        ["Ini adalah versi prototype", "Fitur dan konten", "masih dapat berubah"],
        ["Terima kasih sudah bermain"]
    ]


def get_credit_scene_state():
    total_duration = sum(CREDIT_SCENE_DURATIONS)
    elapsed = (pygame.time.get_ticks() - credit_start_time) % total_duration
    current_start = 0

    for index, duration in enumerate(CREDIT_SCENE_DURATIONS):
        if elapsed < current_start + duration:
            local_elapsed = elapsed - current_start
            fade_time = 700
            if local_elapsed < fade_time:
                alpha = int(255 * (local_elapsed / fade_time))
            elif local_elapsed > duration - fade_time:
                alpha = int(255 * ((duration - local_elapsed) / fade_time))
            else:
                alpha = 255
            return index, max(0, min(255, alpha))
        current_start += duration

    return len(CREDIT_SCENE_DURATIONS) - 1, 255


def draw_credit_scene():
    scene_index, alpha = get_credit_scene_state()
    scene_lines = get_credit_scenes()[scene_index]
    line_gap = 42
    start_y = HEIGHT//2 - (len(scene_lines) * line_gap)//2

    for index, line in enumerate(scene_lines):
        line_font = menu_font if index == 0 else font
        text_surface = line_font.render(line, True, WHITE)
        text_surface.set_alpha(alpha)
        layar.blit(
            text_surface,
            (
                WIDTH//2 - text_surface.get_width()//2,
                start_y + index * line_gap
            )
        )


def get_cutscene_scenes():
    nama = player_name.strip() or "PLAYER"
    return [
        [f"WELCOME TO ANCALA, {nama.upper()}"],
        ["Terjadi banyak peperangan", "yang melanda Ancala"],
        [
            "Para penjajah mulai melakukan kerja paksa,",
            "perampasan wilayah, dan beberapa kekerasan",
            "yang sangat tidak manusiawi"
        ],
        ["Kalahkan mereka", "dan rebut kembali Ancala", "dari para penjajah"],
        [f"Kami percaya kepadamu, {nama}"]
    ]


def get_lose_cutscene_scenes():
    nama = player_name.strip() or "PLAYER"
    return [
        [f"Perjuanganmu sangat keras, {nama}"],
        ["Kamu adalah pahlawan"],
        ["Kematian ini akan membuatmu dikenang", "di Ancala sebagai pahlawan"],
        [
            "Namun, kematianmu juga menghantarkan",
            "kesengsaraan bagi rakyat Ancala",
            "yang berjuang bersamamu"
        ],
        ["Mungkin di kehidupan yang lain", "kita akan bertempur kembali"],
        [f"Kamu hebat, {nama}"]
    ]


def get_win_cutscene_scenes():
    nama = player_name.strip() or "PLAYER"
    return [
        ["Akhirnya.."],
        ["Ancala bebas dari para penjajah..."],
        [f"Perjuanganmu sangat keras, {nama}"],
        ["Namun, usaha kita masih belum selesai"],
        ["(timeline maju 10 tahun kemudian)"],
        ["Para penjajah itu kembali lagi"],
        ["Selamat berjuang"],
        ["THE LAST OF ANCALA 2", "COMING SOON"]
    ]


def get_timed_scene_state(start_time, durations):
    elapsed = pygame.time.get_ticks() - start_time
    current_start = 0

    for index, duration in enumerate(durations):
        if elapsed < current_start + duration:
            local_elapsed = elapsed - current_start
            fade_time = 800
            if local_elapsed < fade_time:
                alpha = int(255 * (local_elapsed / fade_time))
            elif local_elapsed > duration - fade_time:
                alpha = int(255 * ((duration - local_elapsed) / fade_time))
            else:
                alpha = 255
            scroll_y = 30 - int(60 * (local_elapsed / duration))
            return index, max(0, min(255, alpha)), scroll_y, False
        current_start += duration

    return len(durations) - 1, 0, 0, True


def get_cutscene_scene_state():
    return get_timed_scene_state(cutscene_start_time, CUTSCENE_SCENE_DURATIONS)


def get_lose_cutscene_scene_state():
    return get_timed_scene_state(lose_cutscene_start_time, LOSE_CUTSCENE_SCENE_DURATIONS)


def get_win_cutscene_scene_state():
    return get_timed_scene_state(win_cutscene_start_time, WIN_CUTSCENE_SCENE_DURATIONS)


def get_cutscene_line_font(scene_index, line_index, line):
    if line.startswith("(") and line.endswith(")"):
        return cutscene_font_italic
    if scene_index == 0 and line_index == 0:
        return cutscene_font_title
    if line == "THE LAST OF ANCALA 2":
        return cutscene_font_title
    return cutscene_font_body


def draw_cutscene_scene(scenes, scene_state):
    scene_index, alpha, scroll_y, finished = scene_state
    if finished:
        return

    layar.fill((0, 0, 0))
    scene_lines = scenes[scene_index]
    line_gap = 48
    start_y = HEIGHT//2 - (len(scene_lines) * line_gap)//2 + scroll_y

    for index, line in enumerate(scene_lines):
        line_font = get_cutscene_line_font(scene_index, index, line)
        text_surface = line_font.render(line, True, WHITE)
        glow_surface = line_font.render(line, True, (120, 120, 120))
        max_text_width = WIDTH - 160
        if text_surface.get_width() > max_text_width:
            scale = max_text_width / text_surface.get_width()
            new_size = (max_text_width, max(1, int(text_surface.get_height() * scale)))
            text_surface = pygame.transform.smoothscale(text_surface, new_size)
            glow_surface = pygame.transform.smoothscale(glow_surface, new_size)

        text_surface.set_alpha(alpha)
        glow_surface.set_alpha(alpha // 2)
        rect = text_surface.get_rect(center=(WIDTH//2, start_y + index * line_gap))
        glow_rect = rect.copy()
        glow_rect.x += 3
        glow_rect.y += 3
        layar.blit(glow_surface, glow_rect)
        layar.blit(text_surface, rect)


def draw_cutscene():
    draw_cutscene_scene(get_cutscene_scenes(), get_cutscene_scene_state())


def draw_lose_cutscene():
    draw_cutscene_scene(get_lose_cutscene_scenes(), get_lose_cutscene_scene_state())


def draw_win_cutscene():
    draw_cutscene_scene(get_win_cutscene_scenes(), get_win_cutscene_scene_state())


def skill_on_cooldown():
    return pygame.time.get_ticks() - last_skill_time < SKILL_COOLDOWN

# =============================
# DEFAULT VALUE (ANTI STACK)
# =============================
DEFAULT_PLAYER_SPEED = PLAYER_SPEED
DEFAULT_GRAVITASI = BASE_GRAVITASI
active_skill = None   # skill yang sedang aktif

def reset_skill_effect():
    global PLAYER_SHOOT_COOLDOWN, GRAVITASI, active_skill

    PLAYER_SHOOT_COOLDOWN = DEFAULT_PLAYER_SHOOT_COOLDOWN
    GRAVITASI = DEFAULT_GRAVITASI
    active_skill = None

# ==================================================
# GAME LOOP
# ==================================================
text_alpha = 0
text_fade_mode = "in"
game_over_fade_alpha = 0
game_over_fade_mode = "in"   # "in" atau "out"

running = True
while running:
    keys = pygame.key.get_pressed()

    if game_state == PLAY and not skill_mode:
        if keys[pygame.K_q]:

            advance_control_tutorial("q")

            if show_q_tutorial and not q_done:
                q_done = True
                text_fade_mode = "out"

            now = pygame.time.get_ticks()
            if now - last_player_shoot_time >= PLAYER_SHOOT_COOLDOWN:
                arah = 1 if player.direction == "right" else -1
                bullet_x = player.centerx
                bullet_y = player.centery - 10
                player_bullets.append(PlayerBullet(bullet_x, bullet_y, arah))
                last_player_shoot_time = now

    event = pygame.event.Event(pygame.NOEVENT)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_clicked = True

        # ---------------- AWAL ----------------
        if game_state == AWAL:
            if awal_button.clicked(event):
                play_click()
                pygame.time.delay(150)
                game_state = MENU

        # ---------------- MENU ----------------
        elif game_state == MENU:
            if play_button.clicked(event):
                play_click()
                game_state = PROGRESS
            elif options_button.clicked(event):
                play_click()
                previous_state = MENU
                game_state = OPTIONS
            elif exit_button.clicked(event):
                pygame.quit()
                sys.exit()
            elif kredit_button.clicked(event):
                play_click()
                credit_start_time = pygame.time.get_ticks()
                game_state = CREDIT
            elif koleksi_button.clicked(event):
                play_click()
                collection_message = ""
                game_state = COLLECTION

        elif game_state == CREDIT:
            if credit_exit_button.clicked(event):
                play_click()
                game_state = MENU

        elif game_state == CUTSCENE:
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                play_click()
                game_state = PLAY
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                play_click()
                game_state = PLAY

        elif game_state == LOSE_CUTSCENE:
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                play_click()
                game_state = GAME_OVER
                game_over_fade_alpha = 255
                game_over_fade_mode = "in"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                play_click()
                game_state = GAME_OVER
                game_over_fade_alpha = 255
                game_over_fade_mode = "in"

        elif game_state == WIN_CUTSCENE:
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                play_click()
                game_state = VICTORY
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                play_click()
                game_state = VICTORY

        elif game_state == COLLECTION:
            if collection_exit_button.clicked(event):
                play_click()
                game_state = MENU
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos_event = pygame.mouse.get_pos()
                if collection_skin_rect.collidepoint(mouse_pos_event):
                    play_click()
                    collection_message = "COOMING SOON"
                elif collection_skill_rect.collidepoint(mouse_pos_event):
                    play_click()
                    collection_message = "COOMING SOON"

        elif game_state == PROGRESS:
            if progress_exit_button.clicked(event):
                play_click()
                game_state = MENU
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos_event = pygame.mouse.get_pos()
                for index, slot_rect in enumerate(progress_slots, start=1):
                    if slot_rect.collidepoint(mouse_pos_event):
                        play_click()
                        selected_progress_slot = index
                        slot_data = load_slot_data(index)
                        if slot_data:
                            start_game_from_slot(index, slot_data)
                        else:
                            game_state = SAVE_DATA
                        break
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                play_click()
                selected_progress_slot = 1
                slot_data = load_slot_data(1)
                if slot_data:
                    start_game_from_slot(1, slot_data)
                else:
                    game_state = SAVE_DATA

        elif game_state == SAVE_DATA:
            if save_exit_button.clicked(event):
                play_click()
                game_state = PROGRESS
            elif save_main_button.clicked(event):
                play_click()
                try_start_game_from_save()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                play_click()
                try_start_game_from_save()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos_event = pygame.mouse.get_pos()
                name_input_active = name_input_rect.collidepoint(mouse_pos_event)
                for difficulty, difficulty_rect in difficulty_rects.items():
                    if difficulty_rect.collidepoint(mouse_pos_event):
                        play_click()
                        selected_difficulty = difficulty
                        break
            elif event.type == pygame.KEYDOWN and name_input_active:
                if event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif event.key == pygame.K_ESCAPE:
                    name_input_active = False
                elif len(player_name) < 16 and event.unicode and event.unicode.isprintable():
                    player_name += event.unicode

        # ---------------- OPTIONS ----------------
        elif game_state == OPTIONS:
            volume_slider.handle_event(event)
            if exit_button.clicked(event):
                play_click()
                game_state = previous_state

        # ---------------- PLAY ----------------
        if game_state == PLAY:
            if event.type == pygame.KEYDOWN:   
                if event.key == pygame.K_a:
                    advance_control_tutorial("a")
                elif event.key == pygame.K_d:
                    advance_control_tutorial("d")
                elif event.key == pygame.K_SPACE:
                    advance_control_tutorial("space")
                elif event.key == pygame.K_q:
                    advance_control_tutorial("q")
                elif event.key == pygame.K_k:
                    advance_control_tutorial("k")

                if event.key == pygame.K_k and not skill_mode:
                    if not skill_on_cooldown() and not active_skill:
                        skill_mode = True
                        current_time_scale = slow_time_scale
                    else:
                        feedback_text = "SKILL MASIH COOLDOWN!"
                        show_feedback = True
                        feedback_start_time = pygame.time.get_ticks()

                    # tutorial hanya mati sekali
                    if show_skill_hint:
                        tutorial_done = True
                        show_skill_hint = False
                        skill_hint_shown = True

                    # tutorial Q selesai
                    if show_shot_button and not shot_button:
                        shot_button = True
                        show_shot_button = False
                        text_fade_mode = "out"
                    
                        show_skill_hint = True    
                        text_alpha = 0
                        text_fade_mode = "in"
                    now = pygame.time.get_ticks()

                if event.key == pygame.K_ESCAPE:
                    game_state = PAUSE
                if event.key == pygame.K_SPACE:
                    if player.jump_count < player.max_jump:
                        player.velocity_y = PLAYER_VELOCITY_Y
                        player.melompat = True
                        player.jump_count += 1
            if pause_button.clicked(event):
                game_state = PAUSE

        # ---------------- PAUSE ----------------
        elif game_state == PAUSE:
            if pause_resume_button.clicked(event):
                play_click()
                game_state = PLAY
            if options_pause_button.clicked(event):
                play_click()
                previous_state = PAUSE
                game_state = OPTIONS
            if pause_exit_button.clicked(event):
                play_click()
                game_state = MENU

        if game_state == GAME_OVER:
            # ===== RESPAWN (SELAMA MASIH ADA) =====
            if respawn_left > 0:
                if respawn_button.clicked(event):
                    play_click()
                    respawn_left -= 1
                    respawn_player_after_death()

            # ===== RESTART (SELALU BOLEH) =====
            if restart_button.clicked(event):
                play_click()
                tutorial_permanently_disabled = True
                start_game_from_save()

            # ===== QUIT (SELALU BOLEH) =====
            if quit_button.clicked(event):
                play_click()
                tutorial_permanently_disabled = True
                game_state = MENU

        if game_state == VICTORY:
            if next_button.clicked(event):
                play_click()
                game_state = PROGRESS
            elif restart_button.clicked(event):
                play_click()
                start_game_from_save()
            elif quit_button.clicked(event):
                play_click()
                game_state = MENU

    # ---------------- UPDATE ----------------
    mouse_pos = pygame.mouse.get_pos()

    if game_state == AWAL:
        awal_button.update()

    if game_state == MENU:
        play_button.update()
        options_button.update()
        exit_button.update()
        kredit_button.update()
        koleksi_button.update()

    elif game_state == CREDIT:
        credit_exit_button.update()

    elif game_state == CUTSCENE:
        if get_cutscene_scene_state()[3]:
            game_state = PLAY

    elif game_state == LOSE_CUTSCENE:
        if get_lose_cutscene_scene_state()[3]:
            game_state = GAME_OVER
            game_over_fade_alpha = 255
            game_over_fade_mode = "in"

    elif game_state == WIN_CUTSCENE:
        if get_win_cutscene_scene_state()[3]:
            game_state = VICTORY

    elif game_state == COLLECTION:
        collection_exit_button.update()

    elif game_state == PROGRESS:
        progress_exit_button.update()

    elif game_state == OPTIONS:
        volume = volume_slider.value
        set_music_volume(volume)
        exit_button.update()

    elif game_state == SAVE_DATA:
        save_exit_button.update()
        save_main_button.update()

    elif game_state in (PLAY, DYING, WINNING):
        if game_state == PLAY:
            pause_button.update()

        if game_state == PLAY and not skill_mode:
            player.update_image()
            move_player()
            update_camera()

        if enemy_encounter_started():
            for m in musuh_list[:]:
                m.update()
                if m.dead and m.alpha <= 0:
                    musuh_list.remove(m)
                    # ===== CEK KALAHKAN SEMUA MUSUH =====
                    if len(musuh_list) == 0 and game_state == PLAY:
                        start_win_sequence()

            for m in musuh_list:
                if player.colliderect(m) and not m.dead and m.attack_type == "ranged":
                    player.darah -= MUSUH_BODY_DAMAGE
        else:
            for m in musuh_list:
                m.peluru.clear()
                    
        for b in player_bullets[:]:
            b.update()

            # keluar dunia
            if b.x < 0 or b.x > WORLD_WIDTH:
                player_bullets.remove(b)
                continue

            #  Nabrak TILE → HILANG
            if bullet_hits_tile(b):
                player_bullets.remove(b)
                continue

            #  Nabrak MUSUH
            if enemy_encounter_started():
                for m in musuh_list:
                    if b.colliderect(m) and not m.dead:
                        m.darah -= PLAYER_BULLET_DAMAGE
                        if m.darah <= 0:
                            m.darah = 0
                            m.dead = True
                        player_bullets.remove(b)
                        break

        # ===== PLAYER MATI (MASUK SEKALI SAJA) =====
        if player.darah <= 0 and game_state == PLAY:
            last_player_x = player.x
            last_player_y = player.y
            tutorial_permanently_disabled = True

            last_player_x = player.x
            last_player_y = player.y

            tutorial_permanently_disabled = True  

            start_death_sequence()

    elif game_state == SAVE_DATA:
        pass

    # ================= GAME OVER =================
    if game_state == GAME_OVER:
        if respawn_left > 0:
            respawn_button.update()
            restart_button.update()
            quit_button.update()
        else:
            restart_button.update()
            quit_button.update()

        # Fade masuk sekali saja
        if game_over_fade_mode == "in":
            game_over_fade_alpha -= 6
            if game_over_fade_alpha <= 0:
                game_over_fade_alpha = 0
                game_over_fade_mode = None

    elif game_state == VICTORY:
        next_button.update()
        restart_button.update()
        quit_button.update()

     # ================= DYING =================
    elif game_state == DYING:
        death_elapsed = pygame.time.get_ticks() - death_start_time
        if death_elapsed < DEATH_SLOW_DURATION:
            death_fade_alpha = int(110 * (death_elapsed / DEATH_SLOW_DURATION))
        else:
            fade_elapsed = death_elapsed - DEATH_SLOW_DURATION
            fade_progress = min(1, fade_elapsed / DEATH_FADE_DURATION)
            death_fade_alpha = int(110 + (145 * fade_progress))

        if death_elapsed >= DEATH_SLOW_DURATION + DEATH_FADE_DURATION:
            death_fade_alpha = 255
            current_time_scale = normal_time_scale
            if respawn_left > 0:
                game_state = GAME_OVER
                game_over_fade_alpha = 255
                game_over_fade_mode = "in"
            else:
                start_lose_cutscene()

    # ================= WINNING DELAY =================
    elif game_state == WINNING:
        win_elapsed = pygame.time.get_ticks() - win_delay_start_time
        if win_elapsed < DEATH_SLOW_DURATION:
            death_fade_alpha = int(110 * (win_elapsed / DEATH_SLOW_DURATION))
        else:
            fade_elapsed = win_elapsed - DEATH_SLOW_DURATION
            fade_progress = min(1, fade_elapsed / DEATH_FADE_DURATION)
            death_fade_alpha = int(110 + (145 * fade_progress))

        if win_elapsed >= DEATH_SLOW_DURATION + DEATH_FADE_DURATION:
            death_fade_alpha = 255
            start_win_cutscene()

    if show_feedback and pygame.time.get_ticks() - feedback_start_time > 2000:
        show_feedback = False

    # ================= SKILL TIMER =================
    if active_skill:
        if pygame.time.get_ticks() - skill_start_time >= SKILL_DURATION:
            reset_skill_effect()
            last_skill_time = pygame.time.get_ticks()

    # ================= TUTORIAL UPDATE =================
    if game_state == PLAY and current_level == 1 and not tutorial_done:
        now = pygame.time.get_ticks()

        # Fade logic
        if text_fade_mode == "in":
            text_alpha += 10
            if text_alpha >= 255:
                text_alpha = 255
                text_fade_mode = None

        elif text_fade_mode == "out":
            text_alpha -= 10
            if text_alpha <= 0:
                text_alpha = 0
                text_fade_mode = None

                # Pindah teks
                if show_level_text:
                    show_level_text = False
                    show_move_text = True
                    text_fade_mode = "in"

                elif show_move_text:
                    show_move_text = False
                    show_jump_text = True          
                    text_alpha = 0
                    text_fade_mode = "in"

                elif show_q_tutorial and q_done:
                    show_q_tutorial = False
                    show_skill_hint = True
                    q_done = False
                    text_alpha = 0
                    text_fade_mode = "in"

                elif show_skill_hint and k_done:
                    show_skill_hint = False
                    k_done = False

        # LEVEL 1 tampil
        if show_level_text and now - tutorial_start_time >= 2000 and text_fade_mode is None:
            text_fade_mode = "out"

        # Tutorial kontrol hilang setelah maju 1000px
        if show_move_text and player.x >= PLAYER_X + 1500 and text_fade_mode is None:
            text_fade_mode = "out"

        # Jika tutorial lompat aktif dan player lompat
        if show_jump_text and not jump_done:
            if player.melompat:
                jump_done = True
                text_fade_mode = "out"

        # Setelah teks lompat hilang > tampilkan double jump
        elif show_jump_text and text_fade_mode is None and jump_done:
            show_jump_text = False
            show_double_jump_text = True
            text_alpha = 0
            text_fade_mode = "in"

        # Tutorial double jump
        if show_double_jump_text and not double_jump_done:
            if player.jump_count >= 2:
                double_jump_done = True
                text_fade_mode = "out"

        elif show_double_jump_text and text_fade_mode is None and double_jump_done:
            show_double_jump_text = False
            show_q_tutorial = True    
            text_alpha = 255           
            text_fade_mode = None

    if game_state == PLAY:
        update_control_tutorial()

    elif game_state == PAUSE:
        pause_resume_button.update()
        options_pause_button.update()
        pause_exit_button.update()

    update_bgm()

    # ---------------- DRAW ----------------
    if game_state == AWAL:
        layar.blit(awal_bg, (0, 0))
        awal_button.draw()

    elif game_state == MENU:
        layar.blit(menu_bg, (0, 0))
        play_button.draw()
        options_button.draw()
        exit_button.draw()
        kredit_button.draw()
        koleksi_button.draw()

    elif game_state == CREDIT:
        layar.blit(credit_bg, (0, 0))
        draw_credit_scene()
        credit_exit_button.draw()

    elif game_state == CUTSCENE:
        draw_cutscene()

    elif game_state == LOSE_CUTSCENE:
        draw_lose_cutscene()

    elif game_state == WIN_CUTSCENE:
        draw_win_cutscene()

    elif game_state == COLLECTION:
        layar.blit(collection_bg, (0, 0))
        for rect, label in [(collection_skin_rect, "SKIN"), (collection_skill_rect, "SKILL")]:
            hovered = rect.collidepoint(mouse_pos)
            fill_color = (245, 245, 245) if not hovered else (225, 235, 255)
            border_color = (30, 30, 30) if not hovered else (20, 80, 180)
            pygame.draw.rect(layar, fill_color, rect, border_radius=10)
            pygame.draw.rect(layar, border_color, rect, 4, border_radius=10)
            label_text = menu_font.render(label, True, (0, 0, 0))
            layar.blit(
                label_text,
                (
                    rect.centerx - label_text.get_width()//2,
                    rect.centery - label_text.get_height()//2
                )
            )
        if collection_message:
            soon_text = menu_font.render(collection_message, True, (0, 0, 0))
            layar.blit(soon_text, (WIDTH//2 - soon_text.get_width()//2, 450))
        collection_exit_button.draw()

    elif game_state == PROGRESS:
        layar.blit(progress_bg, (0, 0))
        for index, slot_rect in enumerate(progress_slots, start=1):
            warna_slot = (245, 245, 245)
            warna_border = (30, 30, 30)
            if slot_rect.collidepoint(mouse_pos):
                warna_slot = (225, 235, 255)
                warna_border = (20, 80, 180)

            pygame.draw.rect(layar, warna_slot, slot_rect, border_radius=8)
            pygame.draw.rect(layar, warna_border, slot_rect, 3, border_radius=8)

            nomor_slot = font.render(f"SLOT {index}", True, (0, 0, 0))
            layar.blit(nomor_slot, (slot_rect.x + 24, slot_rect.centery - nomor_slot.get_height()//2))
            slot_data = load_slot_data(index)
            if slot_data:
                nama_slot = font.render(str(slot_data.get('nama', '-')), True, (0, 0, 0))
                difficulty_slot = font.render(str(slot_data.get('difficulty', '-')), True, (0, 0, 0))
                waktu_slot = font.render(str(slot_data.get('waktu_bermain', '-')), True, (0, 0, 0))
                layar.blit(nama_slot, (slot_rect.x + 145, slot_rect.y + 8))
                layar.blit(difficulty_slot, (slot_rect.x + 145, slot_rect.y + 32))
                layar.blit(waktu_slot, (slot_rect.right - waktu_slot.get_width() - 22, slot_rect.y + 8))
            else:
                teks_slot = font.render("SLOT KOSONG", True, (0, 0, 0))
                layar.blit(teks_slot, (slot_rect.centerx - teks_slot.get_width()//2, slot_rect.centery - teks_slot.get_height()//2))

        progress_exit_button.draw()

    elif game_state == OPTIONS:
        layar.blit(options_bg, (0, 0))
        volume_slider.draw(layar)
        exit_button.draw()

    elif game_state == SAVE_DATA:
        layar.blit(save_data_bg, (0, 0))
        title_text = menu_font.render("MASUKKAN NAMA", True, (0, 0, 0))
        layar.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 135))

        input_color = (255, 255, 255) if name_input_active else (235, 235, 235)
        pygame.draw.rect(layar, input_color, name_input_rect, border_radius=8)
        pygame.draw.rect(layar, (20, 80, 180) if name_input_active else (30, 30, 30), name_input_rect, 3, border_radius=8)

        name_text = player_name if player_name else "NAMA PLAYER"
        name_color = (0, 0, 0) if player_name else (120, 120, 120)
        rendered_name = font.render(name_text, True, name_color)
        layar.blit(rendered_name, (name_input_rect.x + 18, name_input_rect.centery - rendered_name.get_height()//2))

        difficulty_title = menu_font.render("DIFFICULTY", True, (0, 0, 0))
        layar.blit(difficulty_title, (WIDTH//2 - difficulty_title.get_width()//2, 255))

        for difficulty, difficulty_rect in difficulty_rects.items():
            selected = difficulty == selected_difficulty
            hovered = difficulty_rect.collidepoint(mouse_pos)
            fill_color = (255, 220, 120) if selected else (245, 245, 245)
            border_color = (180, 90, 0) if selected else (30, 30, 30)
            if hovered and not selected:
                fill_color = (225, 235, 255)
                border_color = (20, 80, 180)

            pygame.draw.rect(layar, fill_color, difficulty_rect, border_radius=8)
            pygame.draw.rect(layar, border_color, difficulty_rect, 3, border_radius=8)

            difficulty_text = font.render(difficulty, True, (0, 0, 0))
            layar.blit(
                difficulty_text,
                (
                    difficulty_rect.centerx - difficulty_text.get_width()//2,
                    difficulty_rect.centery - difficulty_text.get_height()//2
                )
            )

        if save_warning_text and pygame.time.get_ticks() - save_warning_start_time < 2000:
            warning_text = font.render(save_warning_text, True, (180, 0, 0))
            layar.blit(warning_text, (WIDTH//2 - warning_text.get_width()//2, 385))

        save_exit_button.draw()
        save_main_button.draw()
        if not can_start_game():
            disabled_overlay = pygame.Surface(save_main_button.rect.size, pygame.SRCALPHA)
            disabled_overlay.fill((0, 0, 0, 100))
            layar.blit(disabled_overlay, save_main_button.rect)

    elif game_state in (PLAY, DYING):
        # ===== BACKGROUND PER LEVEL (MULTI LAYER) =====
        if current_level == 1:
            bg_back = level1_bg
            bg_front = land_lvl1

        elif current_level == 2:
            bg_back = level2_bg      
            bg_front = land_lvl2       

        elif current_level == 3:
            bg_back = level3_bg
            bg_front = land_lvl3

        else:
            bg_front = None

        # ===== DRAW BACKGROUND BELAKANG =====
        bg_width = bg_back.get_width()
        for x in range(0, WORLD_WIDTH, bg_width):
            layar.blit(bg_back, (x - CAMERA_X * 0.5, 0))
            # ^ 0.5 = efek parallax (opsional)


        # BACKGROUND DEPAN
        if bg_front:
            fg_width = bg_front.get_width()
            for x in range(0, WORLD_WIDTH, fg_width):
                layar.blit(bg_front, (x - CAMERA_X, 0))

        # 🔥 KAYU & TILE DI ATAS TANAH
        for tile in tiles:
            tile.draw()

        if enemy_encounter_started():
            for m in musuh_list:
                m.draw()

        if pygame.time.get_ticks() - hit_flash_time < 100:
            pygame.draw.rect(
                layar,
                (255, 0, 0),
                (player.x - CAMERA_X, player.y, PLAYER_WIDTH, PLAYER_HEIGHT),
                3
            )

        for b in player_bullets:
            b.draw()
        if PLAYER_SHOOT_COOLDOWN > 0:
            cooldown = max(0, (PLAYER_SHOOT_COOLDOWN - (pygame.time.get_ticks() - last_player_shoot_time)) // 1000)
            if cooldown > 0:
                txt = font.render(f"Q cooldown: {cooldown}s", True, (255, 255, 255))
                layar.blit(txt, (510, 535))

        # ===== TUTORIAL DRAW =====
        if show_level_text:
            draw_center_text_fade("LEVEL 1", tutorial_font_big, -40, text_alpha)
            draw_center_text_fade("TUTORIAL", tutorial_font_small, 30, text_alpha)
        if show_move_text:
            draw_center_text_fade("D UNTUK MAJU", tutorial_font_small, -20, text_alpha)
            draw_center_text_fade("A UNTUK MUNDUR", tutorial_font_small, 30, text_alpha)
        if show_skill_hint:
            draw_center_text_fade(
                "PENCET K UNTUK MENGAKTIFKAN SKILL",
                tutorial_font_small,
                10, 
                text_alpha
            )
        if show_jump_text:
            draw_center_text_fade(
                "PENCET SPACE UNTUK MELOMPAT",
                tutorial_font_small,
                20,
                text_alpha
            )
        if show_q_tutorial:
            draw_center_text_fade(
                "TEKAN Q UNTUK MENEMBAK",
                tutorial_font_small,
                20,
                text_alpha
            )
        draw_control_tutorial()

        layar.blit(player.image, (player.x - CAMERA_X, player.y))
        draw_health_bar()

        if show_double_jump_text:
            draw_center_text_fade(
                "TEKAN SPACE 2 KALI UNTUK DOUBLE JUMP",
                tutorial_font_small,
                20,
                text_alpha
            )

        if active_skill == "bullets":
            sisa = max(0, (SKILL_DURATION - (pygame.time.get_ticks() - skill_start_time)) // 1000)
            txt = font.render(f"UNLIMITED BULLETS : {sisa}s", True, (255, 200, 0))
            layar.blit(txt, (920, 545))

        elif active_skill:
            sisa = max(0, (SKILL_DURATION - (pygame.time.get_ticks() - skill_start_time)) // 1000)
            txt = font.render(f"{active_skill.upper()} : {sisa}s", True, (255, 255, 0))
            layar.blit(txt, (920, 545))
        if game_state == PLAY:
            pause_button.draw()

                    # ================= SKILL MODE UI =================
        if game_state == PLAY and skill_mode:
            draw_dark_overlay(160)
            # hover effect
            for rect in [bullets_rect, health_rect, gravity_rect]:
                if rect.collidepoint(mouse_pos):
                    pygame.draw.rect(
                        layar,
                        (255, 255, 255),
                        rect.inflate(12, 12),
                        3,
                        border_radius=12
                    )

            # draw skill images
            layar.blit(bullets_img, bullets_rect)
            layar.blit(health_img, health_rect)
            layar.blit(gravity_img, gravity_rect)

            if skill_mode and mouse_clicked:
                mouse_clicked = False
                now = pygame.time.get_ticks()
                last_skill_time = now
                skill_start_time = now

                if bullets_rect.collidepoint(mouse_pos):
                    PLAYER_SHOOT_COOLDOWN = 50
                    active_skill = "bullets"

                elif health_rect.collidepoint(mouse_pos):
                    player.darah = min(player.darah + 30, player.darah_max)
                    active_skill = None

                elif gravity_rect.collidepoint(mouse_pos):
                    GRAVITASI = DEFAULT_GRAVITASI * 0.5
                    active_skill = "gravity"

                # keluar dari skill mode
                skill_mode = False
                current_time_scale = normal_time_scale

        cooldown_left = max(0, (SKILL_COOLDOWN - (pygame.time.get_ticks() - last_skill_time)) // 1000)
        if cooldown_left > 0:
            cd_text = font.render(f"Skill cooldown: {cooldown_left}s", True, (255, 255, 255))
            layar.blit(cd_text, (80, 515))

        # ===== EFEK GELAP SAAT MATI =====
        if player_dead_effect:
            draw_dark_overlay(180)

    elif game_state == PAUSE:
        layar.blit(pause_bg_img, (0,0))
        pause_resume_button.draw()
        options_pause_button.draw()
        pause_exit_button.draw()

    elif game_state == VICTORY:
        layar.blit(victory_bg, (0, 0))
        next_button.draw()
        restart_button.draw()
        quit_button.draw()

    elif game_state == GAME_OVER:
        layar.blit(game_over_bg, (0, 0))

        if respawn_left > 0:
            respawn_button.draw()
            restart_button.draw()
            quit_button.draw()
        else:
            restart_button.draw()
            quit_button.draw()

        info = font.render(f"Batas respawn tersisa: {respawn_left}", True, (0, 0, 0))
        layar.blit(info, (WIDTH//2 - info.get_width()//2, HEIGHT - 45))

        if game_over_fade_alpha > 0:
            draw_dark_overlay(game_over_fade_alpha)

    # ===== FADE HITAM SAAT MATI / MENANG =====
    if game_state in (DYING, WINNING):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(death_fade_alpha)
        layar.blit(overlay, (0, 0))

    mouse_clicked = False
    pygame.display.update()
    clock.tick(FPS)
