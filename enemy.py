import pygame
from config import *


class Enemy:
    def __init__(self, enemy_type, game_map, health_multiplier=1.0):
        self.type = enemy_type
        self.config = ENEMY_TYPES[enemy_type]
        self.game_map = game_map
        self.path_length = game_map.get_path_length()

        self.distance = 0
        self.speed = self.config['speed'] * 60 / FPS
        self.max_health = int(self.config['health'] * health_multiplier)
        self.health = self.max_health
        self.reward = self.config['reward']
        self.color = self.config['color']
        self.size = self.config['size']

        self.x, self.y = game_map.get_position_on_path(0)
        self.alive = True
        self.reached_end = False

    def update(self):
        if not self.alive:
            return

        self.distance += self.speed

        if self.distance >= self.path_length:
            self.reached_end = True
            self.alive = False
            return

        self.x, self.y = self.game_map.get_position_on_path(self.distance)

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.alive = False

    def draw(self, screen):
        if not self.alive and not self.reached_end:
            return

        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.size + 2)
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

        if self.type == 'boss':
            crown_points = [
                (self.x - 12, self.y - self.size - 5),
                (self.x - 6, self.y - self.size - 12),
                (self.x, self.y - self.size - 5),
                (self.x + 6, self.y - self.size - 12),
                (self.x + 12, self.y - self.size - 5),
            ]
            pygame.draw.polygon(screen, YELLOW, crown_points)

        eye_offset = self.size // 3
        eye_size = max(2, self.size // 5)
        pygame.draw.circle(screen, WHITE, (int(self.x - eye_offset), int(self.y - eye_offset)), eye_size)
        pygame.draw.circle(screen, WHITE, (int(self.x + eye_offset), int(self.y - eye_offset)), eye_size)
        pygame.draw.circle(screen, BLACK, (int(self.x - eye_offset), int(self.y - eye_offset)), eye_size // 2)
        pygame.draw.circle(screen, BLACK, (int(self.x + eye_offset), int(self.y - eye_offset)), eye_size // 2)

        if self.health < self.max_health:
            bar_width = self.size * 2
            bar_height = 4
            bar_x = int(self.x - bar_width // 2)
            bar_y = int(self.y - self.size - 10)

            pygame.draw.rect(screen, BLACK, (bar_x - 1, bar_y - 1, bar_width + 2, bar_height + 2))
            pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))

            health_ratio = self.health / self.max_health
            health_color = GREEN if health_ratio > 0.5 else YELLOW if health_ratio > 0.25 else RED
            pygame.draw.rect(screen, health_color, (bar_x, bar_y, int(bar_width * health_ratio), bar_height))

    def get_position(self):
        return (self.x, self.y)

    def is_alive(self):
        return self.alive

    def has_reached_end(self):
        return self.reached_end

    def get_reward(self):
        return self.reward
