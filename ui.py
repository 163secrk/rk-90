import pygame
from config import *


class UIManager:
    def __init__(self, screen):
        self.screen = screen
        self.font_small = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_large = pygame.font.Font(None, 48)

        self.tower_buttons = []
        self._create_tower_buttons()

        self.selected_tower_type = None
        self.selected_tower = None
        self.mouse_x = 0
        self.mouse_y = 0

    def _create_tower_buttons(self):
        button_width = 120
        button_height = 80
        start_x = 50
        y = SCREEN_HEIGHT - 90

        for i, (tower_type, config) in enumerate(TOWER_TYPES.items()):
            x = start_x + i * (button_width + 20)
            button = {
                'type': tower_type,
                'rect': pygame.Rect(x, y, button_width, button_height),
                'config': config,
            }
            self.tower_buttons.append(button)

    def update_mouse_pos(self, x, y):
        self.mouse_x = x
        self.mouse_y = y

    def handle_click(self, x, y, gold, game_map, towers):
        for button in self.tower_buttons:
            if button['rect'].collidepoint(x, y):
                if gold >= button['config']['cost']:
                    self.selected_tower_type = button['type']
                    self.selected_tower = None
                return 'select_tower_type'

        if y < SCREEN_HEIGHT - 100:
            if self.selected_tower_type:
                grid_x = x // GRID_SIZE
                grid_y = y // GRID_SIZE

                if game_map.can_place_tower(grid_x, grid_y, towers):
                    cost = TOWER_TYPES[self.selected_tower_type]['cost']
                    if gold >= cost:
                        return 'place_tower'
                return None

            for tower in towers:
                if tower.is_clicked(x, y):
                    self.selected_tower = tower
                    self.selected_tower_type = None
                    return 'select_tower'

            self.selected_tower = None
            return None

        return None

    def draw_ui(self, gold, lives, wave_manager, current_time):
        self._draw_top_bar(gold, lives, wave_manager, current_time)
        self._draw_bottom_bar()
        self._draw_tower_buttons(gold)

        if self.selected_tower:
            self._draw_tower_info(self.selected_tower)

        if self.selected_tower_type:
            self._draw_placement_preview()

    def _draw_top_bar(self, gold, lives, wave_manager, current_time):
        bar_height = 60
        pygame.draw.rect(self.screen, DARK_GRAY, (0, 0, SCREEN_WIDTH, bar_height))
        pygame.draw.rect(self.screen, GRAY, (0, bar_height - 4, SCREEN_WIDTH, 4))

        gold_text = self.font_medium.render(f"金币: {gold}", True, YELLOW)
        self.screen.blit(gold_text, (20, 15))

        lives_text = self.font_medium.render(f"生命: {lives}", True, RED)
        self.screen.blit(lives_text, (180, 15))

        wave_text = self.font_medium.render(f"波次: {wave_manager.get_wave()}", True, WHITE)
        self.screen.blit(wave_text, (340, 15))

        if wave_manager.is_wave_active():
            progress = wave_manager.get_progress()
            pygame.draw.rect(self.screen, BLACK, (480, 20, 200, 20))
            pygame.draw.rect(self.screen, RED, (482, 22, int(196 * progress), 16))
            pygame.draw.rect(self.screen, WHITE, (480, 20, 200, 20), 2)
            progress_text = self.font_small.render(f"生成中", True, WHITE)
            self.screen.blit(progress_text, (560, 22))
        elif wave_manager.get_wave() > 0 and not wave_manager.is_wave_active():
            time_left = wave_manager.get_time_until_next_wave(current_time)
            if time_left > 0:
                seconds = time_left // 1000 + 1
                next_text = self.font_medium.render(f"下一波: {seconds}秒", True, WHITE)
                self.screen.blit(next_text, (480, 15))
            else:
                ready_text = self.font_medium.render("按 SPACE 开始下一波!", True, GREEN)
                self.screen.blit(ready_text, (480, 15))
        else:
            start_text = self.font_medium.render("按 SPACE 开始游戏!", True, GREEN)
            self.screen.blit(start_text, (480, 15))

    def _draw_bottom_bar(self):
        bar_y = SCREEN_HEIGHT - 100
        pygame.draw.rect(self.screen, DARK_GRAY, (0, bar_y, SCREEN_WIDTH, 100))
        pygame.draw.rect(self.screen, GRAY, (0, bar_y, SCREEN_WIDTH, 4))

    def _draw_tower_buttons(self, gold):
        for button in self.tower_buttons:
            config = button['config']
            rect = button['rect']

            is_selected = self.selected_tower_type == button['type']
            can_afford = gold >= config['cost']

            if is_selected:
                border_color = YELLOW
                bg_color = (80, 80, 80)
            elif can_afford:
                border_color = LIGHT_GRAY
                bg_color = (60, 60, 60)
            else:
                border_color = (80, 80, 80)
                bg_color = (40, 40, 40)

            pygame.draw.rect(self.screen, bg_color, rect)
            pygame.draw.rect(self.screen, border_color, rect, 3)

            center_x = rect.centerx
            center_y = rect.top + 30

            tower_size = 12
            pygame.draw.circle(self.screen, config['color'], (center_x, center_y), tower_size)

            if button['type'] == 'arrow':
                pygame.draw.line(self.screen, (139, 69, 19), (center_x, center_y),
                                 (center_x + 15, center_y), 3)
            elif button['type'] == 'cannon':
                pygame.draw.line(self.screen, (40, 40, 40), (center_x, center_y),
                                 (center_x + 15, center_y), 6)
            elif button['type'] == 'magic':
                crystal_points = [
                    (center_x, center_y - tower_size - 2),
                    (center_x + 5, center_y - 2),
                    (center_x, center_y + 4),
                    (center_x - 5, center_y - 2),
                ]
                pygame.draw.polygon(self.screen, (186, 85, 211), crystal_points)

            name_text = self.font_small.render(config['name'], True, WHITE if can_afford else (128, 128, 128))
            name_rect = name_text.get_rect(centerx=rect.centerx, top=rect.top + 48)
            self.screen.blit(name_text, name_rect)

            cost_color = YELLOW if can_afford else (128, 128, 128)
            cost_text = self.font_small.render(f"{config['cost']}金", True, cost_color)
            cost_rect = cost_text.get_rect(centerx=rect.centerx, top=rect.top + 68)
            self.screen.blit(cost_text, cost_rect)

    def _draw_tower_info(self, tower):
        config = tower.config
        info_width = 250
        info_height = 180
        info_x = SCREEN_WIDTH - info_width - 20
        info_y = 80

        pygame.draw.rect(self.screen, DARK_GRAY, (info_x, info_y, info_width, info_height))
        pygame.draw.rect(self.screen, LIGHT_GRAY, (info_x, info_y, info_width, info_height), 2)

        title_text = self.font_medium.render(f"{config['name']} Lv.{tower.level}", True, YELLOW)
        self.screen.blit(title_text, (info_x + 15, info_y + 10))

        stat_y = info_y + 45
        damage_text = self.font_small.render(f"伤害: {tower.damage}", True, WHITE)
        self.screen.blit(damage_text, (info_x + 15, stat_y))

        range_text = self.font_small.render(f"范围: {tower.range}", True, WHITE)
        self.screen.blit(range_text, (info_x + 15, stat_y + 25))

        fire_rate_text = self.font_small.render(f"攻速: {1000 / tower.fire_rate:.1f}/秒", True, WHITE)
        self.screen.blit(fire_rate_text, (info_x + 15, stat_y + 50))

        button_y = info_y + 130

        upgrade_cost = tower.get_upgrade_cost()
        if upgrade_cost:
            upgrade_rect = pygame.Rect(info_x + 15, button_y, 100, 35)
            pygame.draw.rect(self.screen, (50, 100, 50), upgrade_rect)
            pygame.draw.rect(self.screen, GREEN, upgrade_rect, 2)
            upgrade_text = self.font_small.render(f"升级 {upgrade_cost}金", True, WHITE)
            upgrade_rect_text = upgrade_text.get_rect(center=upgrade_rect.center)
            self.screen.blit(upgrade_text, upgrade_rect_text)
            self.upgrade_rect = upgrade_rect
        else:
            max_text = self.font_small.render("已满级", True, YELLOW)
            self.screen.blit(max_text, (info_x + 15, button_y + 8))
            self.upgrade_rect = None

        sell_value = tower.get_sell_value()
        sell_rect = pygame.Rect(info_x + 135, button_y, 100, 35)
        pygame.draw.rect(self.screen, (100, 50, 50), sell_rect)
        pygame.draw.rect(self.screen, RED, sell_rect, 2)
        sell_text = self.font_small.render(f"出售 {sell_value}金", True, WHITE)
        sell_rect_text = sell_text.get_rect(center=sell_rect.center)
        self.screen.blit(sell_text, sell_rect_text)
        self.sell_rect = sell_rect

    def _draw_placement_preview(self):
        grid_x = self.mouse_x // GRID_SIZE
        grid_y = self.mouse_y // GRID_SIZE

        if self.mouse_y < SCREEN_HEIGHT - 100:
            config = TOWER_TYPES[self.selected_tower_type]
            preview_x = grid_x * GRID_SIZE + GRID_SIZE // 2
            preview_y = grid_y * GRID_SIZE + GRID_SIZE // 2

            range_surface = pygame.Surface((config['range'] * 2, config['range'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(range_surface, (255, 255, 255, 30), (config['range'], config['range']), config['range'])
            pygame.draw.circle(range_surface, (255, 255, 255, 80), (config['range'], config['range']), config['range'], 2)
            self.screen.blit(range_surface, (preview_x - config['range'], preview_y - config['range']))

            preview_surface = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
            pygame.draw.circle(preview_surface, (*config['color'], 180), (GRID_SIZE // 2, GRID_SIZE // 2), 14)
            self.screen.blit(preview_surface, (grid_x * GRID_SIZE, grid_y * GRID_SIZE))

    def check_upgrade_click(self, x, y, gold):
        if self.selected_tower and self.upgrade_rect and self.upgrade_rect.collidepoint(x, y):
            cost = self.selected_tower.get_upgrade_cost()
            if cost and gold >= cost:
                return True
        return False

    def check_sell_click(self, x, y):
        if self.selected_tower and self.sell_rect and self.sell_rect.collidepoint(x, y):
            return True
        return False

    def draw_game_over(self, won, wave):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        if won:
            title_text = self.font_large.render("胜利!", True, GREEN)
        else:
            title_text = self.font_large.render("游戏结束!", True, RED)

        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
        self.screen.blit(title_text, title_rect)

        wave_text = self.font_medium.render(f"到达波次: {wave}", True, WHITE)
        wave_rect = wave_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(wave_text, wave_rect)

        restart_text = self.font_medium.render("按 R 重新开始", True, YELLOW)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(restart_text, restart_rect)

    def draw_pause(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        pause_text = self.font_large.render("暂停", True, WHITE)
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        self.screen.blit(pause_text, pause_rect)

        resume_text = self.font_medium.render("按 P 继续", True, YELLOW)
        resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        self.screen.blit(resume_text, resume_rect)

    def reset(self):
        self.selected_tower_type = None
        self.selected_tower = None
        self.upgrade_rect = None
        self.sell_rect = None
