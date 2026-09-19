"""
game/arrow.py - Arrow projectile physics, motion trails, tip coordinates,
and target-attachment behavior.
"""

import math
import pygame
from settings import (
    ARROW_SPEED, ARROW_GRAVITY, ARROW_LENGTH, SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_CYAN, COLOR_TEXT_WHITE
)

class Arrow:
    """High-speed precision arrow with realistic motion and glowing trail."""

    STATE_FLYING = "FLYING"
    STATE_STUCK = "STUCK"
    STATE_MISSED = "MISSED"
    STATE_INACTIVE = "INACTIVE"

    def __init__(self, x, y, angle, speed=ARROW_SPEED):
        self.x = float(x)
        self.y = float(y)
        self.angle = float(angle)
        self.speed = float(speed)
        self.vx = math.cos(angle) * self.speed
        self.vy = math.sin(angle) * self.speed
        self.length = ARROW_LENGTH
        self.active = True
        self.state = self.STATE_FLYING

        # Motion trail: list of past (tip_x, tip_y) positions
        self.trail = []
        self.max_trail = 12

        # Target attachment parameters
        self.target_ref = None
        self.stuck_rel_x = 0.0
        self.stuck_rel_y = 0.0
        self.fade_alpha = 255
        self.stuck_timer = 0

    def get_tip_pos(self):
        """Returns the exact (x, y) coordinates of the arrowhead tip."""
        half_len = self.length * 0.5
        tip_x = self.x + math.cos(self.angle) * half_len
        tip_y = self.y + math.sin(self.angle) * half_len
        return tip_x, tip_y

    def get_tail_pos(self):
        """Returns the exact (x, y) coordinates of the arrow nock/fletching."""
        half_len = self.length * 0.5
        tail_x = self.x - math.cos(self.angle) * half_len
        tail_y = self.y - math.sin(self.angle) * half_len
        return tail_x, tail_y

    def update(self, dt=1.0):
        if self.state == self.STATE_FLYING:
            # Update trajectory physics
            self.vy += ARROW_GRAVITY * dt
            self.x += self.vx * dt
            self.y += self.vy * dt

            # Update orientation dynamically to match flight path
            self.angle = math.atan2(self.vy, self.vx)

            # Record trail
            tip_x, tip_y = self.get_tip_pos()
            self.trail.insert(0, (tip_x, tip_y))
            if len(self.trail) > self.max_trail:
                self.trail.pop()

            # Boundary checks
            if self.x > SCREEN_WIDTH + 80 or self.y > SCREEN_HEIGHT + 100 or self.y < -100:
                self.state = self.STATE_MISSED
                self.active = False

        elif self.state == self.STATE_STUCK:
            # Follow target's position
            if self.target_ref:
                self.x = self.target_ref.x + self.stuck_rel_x
                self.y = self.target_ref.y + self.stuck_rel_y
            
            # Fade trail quickly
            if self.trail:
                self.trail.pop()

            # Stay stuck for a brief time before fading out
            self.stuck_timer += dt
            if self.stuck_timer > 90:
                self.fade_alpha = max(0, self.fade_alpha - int(8 * dt))
                if self.fade_alpha <= 0:
                    self.active = False
                    self.state = self.STATE_INACTIVE

    def stick_to_target(self, target):
        """Embeds the arrow tip into the target."""
        self.state = self.STATE_STUCK
        self.target_ref = target
        self.stuck_rel_x = self.x - target.x
        self.stuck_rel_y = self.y - target.y
        self.vx = 0
        self.vy = 0

    def draw(self, surface):
        if not self.active and self.fade_alpha <= 0:
            return

        # 1. Draw glowing motion trail
        if len(self.trail) > 1 and self.state == self.STATE_FLYING:
            trail_len = len(self.trail)
            for i in range(trail_len - 1):
                p1 = self.trail[i]
                p2 = self.trail[i + 1]
                ratio = 1.0 - (i / trail_len)
                alpha = int(120 * ratio)
                width = max(1, int(3 * ratio))
                
                # Glowing trail segment
                t_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                pygame.draw.line(t_surf, (56, 189, 248, alpha), p1, p2, width)
                surface.blit(t_surf, (0, 0))

        # 2. Draw Arrow Entity
        tip_x, tip_y = self.get_tip_pos()
        tail_x, tail_y = self.get_tail_pos()

        # If fading, prepare alpha surface or direct draw
        alpha = self.fade_alpha
        draw_surf = surface
        if alpha < 255:
            # Use alpha blitting
            box_r = int(self.length + 10)
            box_surf = pygame.Surface((box_r * 2, box_r * 2), pygame.SRCALPHA)
            cx, cy = box_r, box_r
            rel_tip_x = cx + math.cos(self.angle) * (self.length * 0.5)
            rel_tip_y = cy + math.sin(self.angle) * (self.length * 0.5)
            rel_tail_x = cx - math.cos(self.angle) * (self.length * 0.5)
            rel_tail_y = cy - math.sin(self.angle) * (self.length * 0.5)
            self._render_arrow_geom(box_surf, rel_tip_x, rel_tip_y, rel_tail_x, rel_tail_y, alpha)
            surface.blit(box_surf, (int(self.x - box_r), int(self.y - box_r)))
        else:
            self._render_arrow_geom(surface, tip_x, tip_y, tail_x, tail_y, 255)

    def _render_arrow_geom(self, surface, tip_x, tip_y, tail_x, tail_y, alpha):
        """Renders arrow shaft, arrowhead, and aerodynamic fletchings."""
        shaft_color = (241, 245, 249) if alpha == 255 else (241, 245, 249, alpha)
        accent_color = COLOR_CYAN if alpha == 255 else (56, 189, 248, alpha)

        # Shaft
        pygame.draw.line(surface, shaft_color, (tail_x, tail_y), (tip_x, tip_y), 2)

        # Arrowhead (futuristic needle chisel)
        head_size = 9.0
        angle = self.angle
        p_left = (
            tip_x - math.cos(angle - 0.45) * head_size,
            tip_y - math.sin(angle - 0.45) * head_size
        )
        p_right = (
            tip_x - math.cos(angle + 0.45) * head_size,
            tip_y - math.sin(angle + 0.45) * head_size
        )
        pygame.draw.polygon(surface, accent_color, [(tip_x, tip_y), p_left, p_right])

        # Fletchings (feathers at nock)
        fletch_len = 10.0
        fletch_ang = 0.55
        f1_start = (tail_x + math.cos(angle) * 3, tail_y + math.sin(angle) * 3)
        f1_end = (f1_start[0] - math.cos(angle - fletch_ang) * fletch_len,
                  f1_start[1] - math.sin(angle - fletch_ang) * fletch_len)
        f2_end = (f1_start[0] - math.cos(angle + fletch_ang) * fletch_len,
                  f1_start[1] - math.sin(angle + fletch_ang) * fletch_len)
        
        pygame.draw.line(surface, accent_color, f1_start, f1_end, 2)
        pygame.draw.line(surface, accent_color, f1_start, f2_end, 2)
