"""
game/target.py - Minimalist futuristic target with concentric scoring rings,
sinusoidal/patrol movement, hit-flash feedback, and distance-based collision.
"""

import math
import random
import pygame
from settings import (
    TARGET_DEFAULT_X, TARGET_RADIUS_OUTER, TARGET_RADIUS_MID,
    TARGET_RADIUS_INNER, TARGET_RADIUS_BULLSEYE,
    SCORE_OUTER, SCORE_MID, SCORE_INNER, SCORE_BULLSEYE,
    COLOR_RING_OUTER, COLOR_RING_MID, COLOR_RING_INNER, COLOR_RING_BULLSEYE,
    COLOR_CYAN, COLOR_GOLD, SCREEN_HEIGHT
)

class Target:
    """Dynamic bullseye archery target with distance-based collision and smooth movement."""

    def __init__(self, x=TARGET_DEFAULT_X, y=360):
        self.x = float(x)
        self.y = float(y)
        self.base_y = float(y)
        
        # Ring Radii
        self.r_outer = TARGET_RADIUS_OUTER
        self.r_mid = TARGET_RADIUS_MID
        self.r_inner = TARGET_RADIUS_INNER
        self.r_bullseye = TARGET_RADIUS_BULLSEYE

        # Movement settings
        self.move_speed = 1.6
        self.move_amplitude = 140.0
        self.move_phase = 0.0
        self.is_moving = True

        # Visual states
        self.flash_timer = 0
        self.hit_scale = 1.0
        self.pulse_phase = 0.0

    def configure_round(self, round_num):
        """Scale target difficulty based on round number."""
        if round_num <= 1:
            self.move_speed = 1.2
            self.move_amplitude = 100.0
        elif round_num == 2:
            self.move_speed = 1.8
            self.move_amplitude = 140.0
        elif round_num == 3:
            self.move_speed = 2.4
            self.move_amplitude = 180.0
        elif round_num == 4:
            self.move_speed = 3.0
            self.move_amplitude = 210.0
        else:
            self.move_speed = 3.6
            self.move_amplitude = 240.0

    def update(self, dt=1.0):
        # Update vertical oscillation
        if self.is_moving:
            self.move_phase += 0.025 * self.move_speed * dt
            self.y = self.base_y + math.sin(self.move_phase) * self.move_amplitude

            # Clamp within screen bounds
            min_y = self.r_outer + 60
            max_y = SCREEN_HEIGHT - self.r_outer - 60
            self.y = max(min_y, min(max_y, self.y))

        # Update hit flash & scale bounce
        if self.flash_timer > 0:
            self.flash_timer = max(0, self.flash_timer - int(dt))

        if self.hit_scale > 1.0:
            self.hit_scale = max(1.0, self.hit_scale - 0.03 * dt)

        # Subtle idle pulse
        self.pulse_phase += 0.04 * dt

    def check_hit_segment(self, x1, y1, x2, y2):
        """Calculates exact collision when arrow tip crosses the target's vertical plane.
        Returns (is_hit, score, hit_type, hit_x, hit_y).
        """
        # Did the segment cross or touch target.x?
        if (x1 <= self.x and x2 >= self.x) or (x1 >= self.x and x2 <= self.x):
            # Calculate intersection at target.x
            dx = x2 - x1
            if dx != 0:
                t = (self.x - x1) / dx
                t = max(0.0, min(1.0, t))
                hit_x = self.x
                hit_y = y1 + t * (y2 - y1)
            else:
                hit_x = self.x
                hit_y = y2

            # Distance from target center
            dist = math.hypot(hit_x - self.x, hit_y - self.y)

            if dist <= self.r_outer:
                if dist <= self.r_bullseye:
                    score = SCORE_BULLSEYE
                    hit_type = "BULLSEYE"
                elif dist <= self.r_inner:
                    score = SCORE_INNER
                    hit_type = "INNER"
                elif dist <= self.r_mid:
                    score = SCORE_MID
                    hit_type = "MIDDLE"
                else:
                    score = SCORE_OUTER
                    hit_type = "OUTER"

                self.flash_timer = 10
                self.hit_scale = 1.18
                return True, score, hit_type, hit_x, hit_y

        return False, 0, "MISS", x2, y2

    def check_hit(self, tip_x, tip_y):
        """Distance-based collision at a single point."""
        dist = math.hypot(tip_x - self.x, tip_y - self.y)
        if dist <= self.r_outer:
            if dist <= self.r_bullseye:
                score = SCORE_BULLSEYE
                hit_type = "BULLSEYE"
            elif dist <= self.r_inner:
                score = SCORE_INNER
                hit_type = "INNER"
            elif dist <= self.r_mid:
                score = SCORE_MID
                hit_type = "MIDDLE"
            else:
                score = SCORE_OUTER
                hit_type = "OUTER"

            self.flash_timer = 10
            self.hit_scale = 1.18
            return True, score, hit_type, dist
        return False, 0, "MISS", dist

    def reposition_randomly(self):
        """Relocates base_y to a fresh vertical position for added variety."""
        self.base_y = random.uniform(180, SCREEN_HEIGHT - 180)

    def draw(self, surface):
        """Renders the concentric target rings with optional hit flash."""
        cx = int(self.x)
        cy = int(self.y)
        scale = self.hit_scale

        # 1. Futuristic Target Rail / Guide Track in the background
        rail_x = cx
        rail_surf = pygame.Surface((4, SCREEN_HEIGHT), pygame.SRCALPHA)
        rail_surf.fill((30, 41, 59, 120))
        surface.blit(rail_surf, (rail_x - 2, 0))

        # 2. Outer Halo Ring (glowing accent)
        halo_r = int((self.r_outer + 8) * scale)
        halo_surf = pygame.Surface((halo_r * 2 + 6, halo_r * 2 + 6), pygame.SRCALPHA)
        halo_pulse = int(50 + 20 * math.sin(self.pulse_phase))
        pygame.draw.circle(halo_surf, (56, 189, 248, halo_pulse), (halo_r + 3, halo_r + 3), halo_r, 2)
        surface.blit(halo_surf, (cx - halo_r - 3, cy - halo_r - 3))

        # 3. Concentric Rings
        rings = [
            (self.r_outer * scale, COLOR_RING_OUTER),
            (self.r_mid * scale, COLOR_RING_MID),
            (self.r_inner * scale, COLOR_RING_INNER),
            (self.r_bullseye * scale, COLOR_RING_BULLSEYE)
        ]

        is_flashing = self.flash_timer > 0

        for radius, color in rings:
            r_int = max(2, int(radius))
            ring_color = (255, 255, 255) if is_flashing else color
            pygame.draw.circle(surface, ring_color, (cx, cy), r_int)
            # Thin dark ring separation for clean crisp modern look
            pygame.draw.circle(surface, (15, 23, 42), (cx, cy), r_int, 2)

        # Center pinpoint
        center_color = (255, 255, 255) if not is_flashing else (255, 220, 100)
        pygame.draw.circle(surface, center_color, (cx, cy), max(1, int(3 * scale)))
