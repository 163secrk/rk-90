import pygame
import sys
from config import *
from map import GameMap
from tower import Tower
from wave import WaveManager
from ui import UIManager


class TowerDefenseGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("铁壁塔防")
        self.clock = pygame.time.Clock()

        self.game_map = GameMap()
        self.wave_manager = WaveManager(self.game_map)
        self.ui_manager = UIManager(self.screen)

        self.enemies = []
        self.towers = []
        self.bullets = []

        self.gold = INITIAL_GOLD
        self.lives = INITIAL_LIVES

        self.game_state = 'playing'
        self.paused = False
        self.game_over = False
        self.won = False

        self.floating_texts = []

    def reset(self):
        self.game_map = GameMap()
        self.wave_manager = WaveManager(self.game_map)
        self.ui_manager.reset()

        self.enemies = []
        self.towers = []
        self.bullets = []

        self.gold = INITIAL_GOLD
        self.lives = INITIAL_LIVES

        self.game_state = 'playing'
        self.paused = False
        self.game_over = False
        self.won = False

        self.floating_texts = []

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.ui_manager.selected_tower_type:
                        self.ui_manager.selected_tower_type = None
                    else:
                        pygame.quit()
                        sys.exit()
                elif event.key == pygame.K_SPACE:
                    if not self.game_over:
                        if self.wave_manager.can_start_next_wave(pygame.time.get_ticks()):
                            self.wave_manager.start_next_wave()
                elif event.key == pygame.K_p:
                    if not self.game_over:
                        self.paused = not self.paused
                elif event.key == pygame.K_r:
                    self.reset()

            if event.type == pygame.MOUSEMOTION:
                self.ui_manager.update_mouse_pos(event.pos[0], event.pos[1])

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not self.paused and not self.game_over:
                    self.handle_click(event.pos[0], event.pos[1])
                elif event.button == 3:
                    self.ui_manager.selected_tower_type = None
                    self.ui_manager.selected_tower = None

    def handle_click(self, x, y):
        if self.ui_manager.check_upgrade_click(x, y, self.gold):
            cost = self.ui_manager.selected_tower.get_upgrade_cost()
            if self.ui_manager.selected_tower.upgrade():
                self.gold -= cost
                self.add_floating_text(x, y, f"-{cost}", YELLOW)
            return

        if self.ui_manager.check_sell_click(x, y):
            sell_value = self.ui_manager.selected_tower.get_sell_value()
            self.towers.remove(self.ui_manager.selected_tower)
            self.gold += sell_value
            self.add_floating_text(x, y, f"+{sell_value}", YELLOW)
            self.ui_manager.selected_tower = None
            return

        result = self.ui_manager.handle_click(x, y, self.gold, self.game_map, self.towers)

        if result == 'place_tower':
            grid_x = x // GRID_SIZE
            grid_y = y // GRID_SIZE
            tower_type = self.ui_manager.selected_tower_type
            cost = TOWER_TYPES[tower_type]['cost']

            tower = Tower(tower_type, grid_x, grid_y)
            self.towers.append(tower)
            self.gold -= cost
            self.add_floating_text(tower.x, tower.y, f"-{cost}", YELLOW)

    def add_floating_text(self, x, y, text, color):
        self.floating_texts.append({
            'text': text,
            'x': x,
            'y': y,
            'color': color,
            'life': 60,
            'vy': -1
        })

    def update(self):
        if self.paused or self.game_over:
            return

        current_time = pygame.time.get_ticks()

        self.wave_manager.update(self.enemies, current_time)

        for enemy in self.enemies:
            enemy.update()

        for tower in self.towers:
            tower.update(self.enemies, current_time, self.bullets)

        for bullet in self.bullets:
            bullet.update()

        self.check_enemy_rewards()
        self.check_lives()
        self.cleanup()
        self.update_floating_texts()
        self.check_win_condition()

    def check_enemy_rewards(self):
        for enemy in self.enemies:
            if not enemy.is_alive() and not enemy.has_reached_end() and not getattr(enemy, 'rewarded', False):
                enemy.rewarded = True
                self.gold += enemy.get_reward()
                self.add_floating_text(enemy.x, enemy.y, f"+{enemy.get_reward()}", YELLOW)

    def check_lives(self):
        for enemy in self.enemies:
            if enemy.has_reached_end() and not getattr(enemy, 'counted', False):
                enemy.counted = True
                self.lives -= 1
                self.add_floating_text(SCREEN_WIDTH - 100, 30, "-1", RED)

                if self.lives <= 0:
                    self.lives = 0
                    self.game_over = True
                    self.won = False

    def cleanup(self):
        self.enemies = [e for e in self.enemies if e.is_alive() or (not e.has_reached_end() and not getattr(e, 'rewarded', False))]
        self.bullets = [b for b in self.bullets if b.is_alive()]

        if len(self.enemies) > 50:
            self.enemies = self.enemies[-50:]

    def update_floating_texts(self):
        for ft in self.floating_texts:
            ft['y'] += ft['vy']
            ft['life'] -= 1

        self.floating_texts = [ft for ft in self.floating_texts if ft['life'] > 0]

    def check_win_condition(self):
        if self.wave_manager.get_wave() >= 20 and self.wave_manager.is_wave_complete():
            self.game_over = True
            self.won = True

    def draw(self):
        self.game_map.draw(self.screen)

        for tower in self.towers:
            show_range = self.ui_manager.selected_tower == tower
            tower.draw(self.screen, show_range)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        for bullet in self.bullets:
            bullet.draw(self.screen)

        self.draw_floating_texts()

        self.ui_manager.draw_ui(self.gold, self.lives, self.wave_manager, pygame.time.get_ticks())

        if self.paused:
            self.ui_manager.draw_pause()

        if self.game_over:
            self.ui_manager.draw_game_over(self.won, self.wave_manager.get_wave())

        pygame.display.flip()

    def draw_floating_texts(self):
        font = get_chinese_font(24)
        for ft in self.floating_texts:
            alpha = int(255 * (ft['life'] / 60))
            text_surface = font.render(ft['text'], True, ft['color'])
            text_surface.set_alpha(alpha)
            self.screen.blit(text_surface, (ft['x'] - text_surface.get_width() // 2, ft['y']))

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)


if __name__ == "__main__":
    game = TowerDefenseGame()
    game.run()
