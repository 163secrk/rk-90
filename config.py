import pygame
import os

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
GRID_SIZE = 40
FPS = 60


def get_chinese_font(size):
    font_candidates = [
        "Microsoft YaHei",
        "SimHei",
        "SimSun",
        "KaiTi",
        "FangSong",
        "Arial Unicode MS",
    ]
    for font_name in font_candidates:
        try:
            font_path = pygame.font.match_font(font_name)
            if font_path:
                return pygame.font.Font(font_path, size)
        except Exception:
            continue
    return pygame.font.Font(None, size)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
GRASS_GREEN = (34, 139, 34)
PATH_COLOR = (160, 140, 100)

TOWER_TYPES = {
    'arrow': {
        'name': '箭塔',
        'cost': 100,
        'damage': 25,
        'range': 150,
        'fire_rate': 1000,
        'color': (139, 90, 43),
        'upgrade_cost': 75,
        'damage_upgrade': 15,
        'range_upgrade': 20,
    },
    'cannon': {
        'name': '炮塔',
        'cost': 200,
        'damage': 60,
        'range': 120,
        'fire_rate': 2000,
        'color': (80, 80, 80),
        'upgrade_cost': 150,
        'damage_upgrade': 30,
        'range_upgrade': 15,
    },
    'magic': {
        'name': '魔法塔',
        'cost': 150,
        'damage': 35,
        'range': 180,
        'fire_rate': 1500,
        'color': (138, 43, 226),
        'upgrade_cost': 100,
        'damage_upgrade': 20,
        'range_upgrade': 25,
    },
}

ENEMY_TYPES = {
    'basic': {
        'name': '小兵',
        'health': 100,
        'speed': 1.0,
        'reward': 15,
        'color': (178, 34, 34),
        'size': 15,
    },
    'fast': {
        'name': '快兵',
        'health': 60,
        'speed': 2.0,
        'reward': 20,
        'color': (255, 165, 0),
        'size': 12,
    },
    'tank': {
        'name': '重甲',
        'health': 300,
        'speed': 0.5,
        'reward': 40,
        'color': (70, 70, 70),
        'size': 20,
    },
    'boss': {
        'name': 'BOSS',
        'health': 1000,
        'speed': 0.3,
        'reward': 200,
        'color': (128, 0, 128),
        'size': 30,
    },
}

INITIAL_GOLD = 300
INITIAL_LIVES = 20

WAVE_DELAY = 5000

PATH_POINTS = [
    (0, 200),
    (200, 200),
    (200, 400),
    (500, 400),
    (500, 150),
    (800, 150),
    (800, 500),
    (1000, 500),
    (1000, 300),
    (1200, 300),
]
