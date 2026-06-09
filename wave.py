import pygame
from config import *
from enemy import Enemy


class WaveManager:
    def __init__(self, game_map):
        self.game_map = game_map
        self.wave = 0
        self.enemies_spawned = 0
        self.enemies_in_wave = 0
        self.spawn_timer = 0
        self.spawn_interval = 1000
        self.wave_active = False
        self.wave_complete = True
        self.last_wave_end = 0
        self.health_multiplier = 1.0

    def start_next_wave(self):
        if self.wave_active:
            return

        self.wave += 1
        self.enemies_spawned = 0
        self.wave_active = True
        self.wave_complete = False
        self.spawn_timer = 0
        self.health_multiplier = 1.0 + (self.wave - 1) * 0.15
        self.enemies_in_wave = self._calculate_wave_enemies()

    def _calculate_wave_enemies(self):
        base_enemies = 8
        return base_enemies + self.wave * 3

    def _get_enemy_type(self):
        wave = self.wave

        if wave >= 10 and self.enemies_spawned == self.enemies_in_wave - 1:
            return 'boss'

        if wave >= 5:
            rand = pygame.time.get_ticks() % 100
            if rand < 15:
                return 'tank'
            elif rand < 40:
                return 'fast'
            else:
                return 'basic'
        elif wave >= 3:
            rand = pygame.time.get_ticks() % 100
            if rand < 25:
                return 'fast'
            else:
                return 'basic'
        else:
            return 'basic'

    def update(self, enemies, current_time):
        if not self.wave_active:
            return

        if self.enemies_spawned < self.enemies_in_wave:
            if current_time - self.spawn_timer >= self.spawn_interval:
                enemy_type = self._get_enemy_type()
                enemy = Enemy(enemy_type, self.game_map, self.health_multiplier)
                enemies.append(enemy)
                self.enemies_spawned += 1
                self.spawn_timer = current_time

                if enemy_type == 'boss':
                    self.spawn_interval = 2000
                else:
                    self.spawn_interval = max(400, 1000 - self.wave * 30)

        alive_enemies = [e for e in enemies if e.is_alive()]
        if self.enemies_spawned >= self.enemies_in_wave and len(alive_enemies) == 0:
            self.wave_active = False
            self.wave_complete = True
            self.last_wave_end = current_time

    def is_wave_active(self):
        return self.wave_active

    def is_wave_complete(self):
        return self.wave_complete

    def get_wave(self):
        return self.wave

    def get_enemies_remaining(self):
        return self.enemies_in_wave - self.enemies_spawned

    def get_progress(self):
        if self.enemies_in_wave == 0:
            return 0
        return self.enemies_spawned / self.enemies_in_wave

    def can_start_next_wave(self, current_time):
        if self.wave_active:
            return False
        if self.wave == 0:
            return True
        return current_time - self.last_wave_end >= WAVE_DELAY

    def get_time_until_next_wave(self, current_time):
        if self.wave_active or self.wave == 0:
            return 0
        remaining = WAVE_DELAY - (current_time - self.last_wave_end)
        return max(0, remaining)

    def reset(self):
        self.wave = 0
        self.enemies_spawned = 0
        self.enemies_in_wave = 0
        self.spawn_timer = 0
        self.spawn_interval = 1000
        self.wave_active = False
        self.wave_complete = True
        self.last_wave_end = 0
        self.health_multiplier = 1.0
