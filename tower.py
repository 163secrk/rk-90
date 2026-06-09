import pygame
import math
from config import *


class Tower:
    def __init__(self, tower_type, grid_x, grid_y):
        self.type = tower_type
        self.config = TOWER_TYPES[tower_type]
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.x = grid_x * GRID_SIZE + GRID_SIZE // 2
        self.y = grid_y * GRID_SIZE + GRID_SIZE // 2

        self.level = 1
        self.damage = self.config['damage']
        self.range = self.config['range']
        self.fire_rate = self.config['fire_rate']
        self.color = self.config['color']
        self.last_shot = 0
        self.angle = 0
        self.target = None

    def update(self, enemies, current_time, bullets):
        self.find_target(enemies)

        if self.target and self.target.is_alive():
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            self.angle = math.degrees(math.atan2(dy, dx))

            if current_time - self.last_shot >= self.fire_rate:
                self.shoot(bullets)
                self.last_shot = current_time
        else:
            self.target = None

    def find_target(self, enemies):
        closest_enemy = None
        max_distance = -1

        for enemy in enemies:
            if not enemy.is_alive():
                continue

            dist = math.hypot(enemy.x - self.x, enemy.y - self.y)
            if dist <= self.range:
                if enemy.distance > max_distance:
                    max_distance = enemy.distance
                    closest_enemy = enemy

        self.target = closest_enemy

    def shoot(self, bullets):
        if self.target:
            bullet = Bullet(
                self.x,
                self.y,
                self.target,
                self.damage,
                self.type,
                self.range
            )
            bullets.append(bullet)

    def upgrade(self):
        if self.level >= 3:
            return False

        self.level += 1
        self.damage += self.config['damage_upgrade']
        self.range += self.config['range_upgrade']
        self.fire_rate = max(300, self.fire_rate - 100)
        return True

    def get_upgrade_cost(self):
        if self.level >= 3:
            return None
        return self.config['upgrade_cost'] * self.level

    def get_sell_value(self):
        total_cost = self.config['cost']
        for i in range(1, self.level):
            total_cost += self.config['upgrade_cost'] * i
        return int(total_cost * 0.6)

    def draw(self, screen, show_range=False):
        if show_range:
            range_surface = pygame.Surface((self.range * 2, self.range * 2), pygame.SRCALPHA)
            pygame.draw.circle(range_surface, (255, 255, 255, 30), (self.range, self.range), self.range)
            pygame.draw.circle(range_surface, (255, 255, 255, 80), (self.range, self.range), self.range, 2)
            screen.blit(range_surface, (self.x - self.range, self.y - self.range))

        base_size = 18
        pygame.draw.rect(screen, DARK_GRAY, (self.x - base_size, self.y - base_size, base_size * 2, base_size * 2))
        pygame.draw.rect(screen, GRAY, (self.x - base_size + 2, self.y - base_size + 2, base_size * 2 - 4, base_size * 2 - 4))

        tower_size = 14
        if self.type == 'arrow':
            self._draw_arrow_tower(screen, tower_size)
        elif self.type == 'cannon':
            self._draw_cannon_tower(screen, tower_size)
        elif self.type == 'magic':
            self._draw_magic_tower(screen, tower_size)

        if self.level > 1:
            for i in range(self.level - 1):
                star_x = self.x - 8 + i * 10
                star_y = self.y - base_size - 8
                self._draw_star(screen, star_x, star_y, 5, YELLOW)

    def _draw_arrow_tower(self, screen, size):
        pygame.draw.circle(screen, self.color, (self.x, self.y), size)
        pygame.draw.circle(screen, (101, 67, 33), (self.x, self.y), size - 4)

        barrel_length = 20
        end_x = self.x + math.cos(math.radians(self.angle)) * barrel_length
        end_y = self.y + math.sin(math.radians(self.angle)) * barrel_length
        pygame.draw.line(screen, (139, 69, 19), (self.x, self.y), (end_x, end_y), 4)
        pygame.draw.circle(screen, (139, 69, 19), (int(end_x), int(end_y)), 3)

    def _draw_cannon_tower(self, screen, size):
        pygame.draw.circle(screen, self.color, (self.x, self.y), size)
        pygame.draw.circle(screen, (50, 50, 50), (self.x, self.y), size - 4)

        barrel_length = 22
        end_x = self.x + math.cos(math.radians(self.angle)) * barrel_length
        end_y = self.y + math.sin(math.radians(self.angle)) * barrel_length
        pygame.draw.line(screen, (40, 40, 40), (self.x, self.y), (end_x, end_y), 8)
        pygame.draw.circle(screen, (30, 30, 30), (int(end_x), int(end_y)), 5)

    def _draw_magic_tower(self, screen, size):
        pygame.draw.circle(screen, self.color, (self.x, self.y), size)
        pygame.draw.circle(screen, (75, 0, 130), (self.x, self.y), size - 4)

        crystal_points = [
            (self.x, self.y - size - 2),
            (self.x + 6, self.y - 4),
            (self.x, self.y + 4),
            (self.x - 6, self.y - 4),
        ]
        pygame.draw.polygon(screen, (186, 85, 211), crystal_points)
        pygame.draw.polygon(screen, (218, 112, 214), crystal_points, 2)

        glow_radius = 8 + math.sin(pygame.time.get_ticks() / 200) * 3
        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (218, 112, 214, 100), (glow_radius, glow_radius), glow_radius)
        screen.blit(glow_surface, (self.x - glow_radius, self.y - glow_radius))

    def _draw_star(self, screen, x, y, size, color):
        points = []
        for i in range(10):
            angle = math.radians(i * 36 - 90)
            radius = size if i % 2 == 0 else size / 2
            points.append((x + radius * math.cos(angle), y + radius * math.sin(angle)))
        pygame.draw.polygon(screen, color, points)

    def is_clicked(self, mouse_x, mouse_y):
        return abs(mouse_x - self.x) < GRID_SIZE // 2 and abs(mouse_y - self.y) < GRID_SIZE // 2


class Bullet:
    def __init__(self, x, y, target, damage, bullet_type, max_range):
        self.x = x
        self.y = y
        self.target = target
        self.damage = damage
        self.type = bullet_type
        self.max_range = max_range
        self.speed = 8
        self.alive = True
        self.distance_traveled = 0

        if self.type == 'arrow':
            self.color = (139, 69, 19)
            self.size = 4
        elif self.type == 'cannon':
            self.color = (30, 30, 30)
            self.size = 6
        elif self.type == 'magic':
            self.color = (186, 85, 211)
            self.size = 5

        self.update_direction()

    def update_direction(self):
        if self.target and self.target.is_alive():
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            dist = math.hypot(dx, dy)
            if dist > 0:
                self.dx = (dx / dist) * self.speed
                self.dy = (dy / dist) * self.speed

    def update(self):
        if not self.alive:
            return

        self.update_direction()

        self.x += self.dx
        self.y += self.dy
        self.distance_traveled += self.speed

        if self.distance_traveled > self.max_range * 1.5:
            self.alive = False
            return

        if self.target and self.target.is_alive():
            dist = math.hypot(self.target.x - self.x, self.target.y - self.y)
            if dist < self.size + self.target.size:
                self.hit_target()

    def hit_target(self):
        if self.target and self.target.is_alive():
            self.target.take_damage(self.damage)
            self.alive = False

    def draw(self, screen):
        if not self.alive:
            return

        if self.type == 'arrow':
            angle = math.degrees(math.atan2(self.dy, self.dx))
            arrow_length = 12
            end_x = self.x + math.cos(math.radians(angle)) * arrow_length
            end_y = self.y + math.sin(math.radians(angle)) * arrow_length
            pygame.draw.line(screen, self.color, (self.x, self.y), (end_x, end_y), 3)

            head_length = 5
            head_angle1 = angle + 160
            head_angle2 = angle - 160
            head1_x = end_x + math.cos(math.radians(head_angle1)) * head_length
            head1_y = end_y + math.sin(math.radians(head_angle1)) * head_length
            head2_x = end_x + math.cos(math.radians(head_angle2)) * head_length
            head2_y = end_y + math.sin(math.radians(head_angle2)) * head_length
            pygame.draw.line(screen, self.color, (end_x, end_y), (head1_x, head1_y), 2)
            pygame.draw.line(screen, self.color, (end_x, end_y), (head2_x, head2_y), 2)

        elif self.type == 'cannon':
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
            pygame.draw.circle(screen, (100, 100, 100), (int(self.x), int(self.y)), self.size - 2)

        elif self.type == 'magic':
            glow_surface = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (186, 85, 211, 80), (self.size * 2, self.size * 2), self.size * 2)
            screen.blit(glow_surface, (self.x - self.size * 2, self.y - self.size * 2))
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
            pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), self.size - 2)

    def is_alive(self):
        return self.alive
