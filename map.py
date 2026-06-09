import pygame
from config import *


class GameMap:
    def __init__(self):
        self.path_points = PATH_POINTS
        self.path_width = 60
        self.grid_size = GRID_SIZE
        self.blocked_positions = set()
        self._generate_blocked_positions()

    def _generate_blocked_positions(self):
        for i in range(len(self.path_points) - 1):
            start = self.path_points[i]
            end = self.path_points[i + 1]
            self._mark_path_segment(start, end)

    def _mark_path_segment(self, start, end):
        x1, y1 = start
        x2, y2 = end

        min_x = min(x1, x2) - self.path_width // 2
        max_x = max(x1, x2) + self.path_width // 2
        min_y = min(y1, y2) - self.path_width // 2
        max_y = max(y1, y2) + self.path_width // 2

        for x in range(int(min_x // self.grid_size), int(max_x // self.grid_size) + 1):
            for y in range(int(min_y // self.grid_size), int(max_y // self.grid_size) + 1):
                grid_x = x * self.grid_size + self.grid_size // 2
                grid_y = y * self.grid_size + self.grid_size // 2

                if self._is_point_near_path(grid_x, grid_y):
                    self.blocked_positions.add((x, y))

    def _is_point_near_path(self, px, py):
        for i in range(len(self.path_points) - 1):
            x1, y1 = self.path_points[i]
            x2, y2 = self.path_points[i + 1]

            dist = self._point_to_line_distance(px, py, x1, y1, x2, y2)
            if dist < self.path_width // 2 + 10:
                return True
        return False

    def _point_to_line_distance(self, px, py, x1, y1, x2, y2):
        line_len_sq = (x2 - x1) ** 2 + (y2 - y1) ** 2
        if line_len_sq == 0:
            return ((px - x1) ** 2 + (py - y1) ** 2) ** 0.5

        t = max(0, min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / line_len_sq))
        proj_x = x1 + t * (x2 - x1)
        proj_y = y1 + t * (y2 - y1)
        return ((px - proj_x) ** 2 + (py - proj_y) ** 2) ** 0.5

    def can_place_tower(self, grid_x, grid_y, towers):
        if (grid_x, grid_y) in self.blocked_positions:
            return False

        for tower in towers:
            if tower.grid_x == grid_x and tower.grid_y == grid_y:
                return False

        pos_x = grid_x * self.grid_size + self.grid_size // 2
        pos_y = grid_y * self.grid_size + self.grid_size // 2

        if pos_x < 0 or pos_x >= SCREEN_WIDTH or pos_y < 0 or pos_y >= SCREEN_HEIGHT - 100:
            return False

        return True

    def draw(self, screen):
        screen.fill(GRASS_GREEN)

        for x in range(0, SCREEN_WIDTH, self.grid_size):
            pygame.draw.line(screen, (30, 120, 30), (x, 0), (x, SCREEN_HEIGHT - 100), 1)
        for y in range(0, SCREEN_HEIGHT - 100, self.grid_size):
            pygame.draw.line(screen, (30, 120, 30), (0, y), (SCREEN_WIDTH, y), 1)

        if len(self.path_points) >= 2:
            pygame.draw.lines(screen, PATH_COLOR, False, self.path_points, self.path_width)
            pygame.draw.lines(screen, (120, 100, 80), False, self.path_points, self.path_width + 4)
            pygame.draw.lines(screen, PATH_COLOR, False, self.path_points, self.path_width)

        start_point = self.path_points[0]
        end_point = self.path_points[-1]

        pygame.draw.circle(screen, GREEN, start_point, 20)
        pygame.draw.circle(screen, DARK_GRAY, start_point, 16)
        pygame.draw.circle(screen, GREEN, start_point, 12)

        pygame.draw.circle(screen, RED, end_point, 20)
        pygame.draw.circle(screen, DARK_GRAY, end_point, 16)
        pygame.draw.circle(screen, RED, end_point, 12)

    def get_path_length(self):
        length = 0
        for i in range(len(self.path_points) - 1):
            x1, y1 = self.path_points[i]
            x2, y2 = self.path_points[i + 1]
            length += ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        return length

    def get_position_on_path(self, distance):
        remaining = distance
        for i in range(len(self.path_points) - 1):
            x1, y1 = self.path_points[i]
            x2, y2 = self.path_points[i + 1]
            segment_length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

            if remaining <= segment_length:
                ratio = remaining / segment_length
                x = x1 + ratio * (x2 - x1)
                y = y1 + ratio * (y2 - y1)
                return (x, y)
            remaining -= segment_length

        return self.path_points[-1]
