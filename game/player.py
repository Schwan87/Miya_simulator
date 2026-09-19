"""
game/player.py - Player bow class with mouse aiming, angle limits,
subtle trajectory projection, and futuristic minimalist rendering.
"""

import math
import pygame
from settings import (
    BOW_POS_X, BOW_POS_Y, BOW_RADIUS, BOW_MIN_ANGLE, BOW_MAX_ANGLE,
    ARROW_SPEED, ARROW_GRAVITY, TRAJECTORY_POINTS, TRAJECTORY_STEP,
    COLOR_CYAN, COLOR_TEXT_WHITE, COLOR_TEXT_MUTED
)

class PlayerBow:
    """The player's bow with interactive mouse aiming and aesthetic rendering."""

    def __init__(self, x=BOW_POS_X, y=BOW_POS_Y):
        self.x = x
        self.y = y
        self.angle = 0.0          # in radians (-pi to pi)
        self.target_angle = 0.0
        self.min_angle = math.radians(BOW_MIN_ANGLE)
        self.max_angle = math.radians(BOW_MAX_ANGLE)
        self.is_drawn = False     # string pull back state
        self.draw_amount = 0.0    # 0.0 to 1.0 tension animation

    def update_aim(self, mouse_pos):
        """Calculates clamped angle towards mouse position."""
        dx = mouse_pos[0] - self.x
        dy = mouse_pos[1] - self.y

        raw_angle = math.atan2(dy, dx)
        # Clamp to realistic forward-facing arc
        clamped_angle = max(self.min_angle, min(self.max_angle, raw_angle))
        
        # Smooth interpolation towards target angle for natural feel
        angle_diff = clamped_angle - self.angle
        self.angle += angle_diff * 0.42

    def set_draw_state(self, is_drawn):
        self.is_drawn = is_drawn

    def update(self, dt=1.0):
        # Animate bowstring tension smoothly
        target_tension = 0.85 if self.is_drawn else 0.0
        self.draw_amount += (target_tension - self.draw_amount) * 0.25 * dt

    def get_arrow_spawn(self):
        """Returns spawn position (x, y), angle (radians), and velocity (vx, vy)."""
        # Slight setback when drawn
        pull_offset = 12.0 * self.draw_amount
        spawn_x = self.x + math.cos(self.angle) * (15.0 - pull_offset)
        spawn_y = self.y + math.sin(self.angle) * (15.0 - pull_offset)
        
        vx = math.cos(self.angle) * ARROW_SPEED
        vy = math.sin(self.angle) * ARROW_SPEED
        return (spawn_x, spawn_y), self.angle, (vx, vy)

    def draw_trajectory(self, surface):
        """Draws subtle, elegant prediction dots along arrow path."""
        (start_x, start_y), _, (vx, vy) = self.get_arrow_spawn()
        curr_x = start_x
        curr_y = start_y
        cur_vx = vx
        cur_vy = vy

        # Render dashed glowing trajectory dots
        for i in range(TRAJECTORY_POINTS):
            for _ in range(int(TRAJECTORY_STEP)):
                curr_x += cur_vx * 0.5
                curr_y += cur_vy * 0.5
                cur_vy += ARROW_GRAVITY * 0.5

            if curr_x > 1200 or curr_y < 50 or curr_y > 670:
                break

            progress = i / TRAJECTORY_POINTS
            alpha = int(180 * (1.0 - progress * 0.75))
            dot_radius = max(1.0, 2.5 * (1.0 - progress * 0.5))

            dot_surf = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(dot_surf, (56, 189, 248, alpha), (4, 4), dot_radius)
            surface.blit(dot_surf, (int(curr_x - 4), int(curr_y - 4)))

    def draw(self, surface):
        """Renders the modern minimalist recurve bow."""
        # Calculate bow limbs arc
        # Up limb tip & Down limb tip relative to bow angle
        radius = BOW_RADIUS
        half_arc = math.radians(65)
        
        up_angle = self.angle - half_arc
        down_angle = self.angle + half_arc

        up_tip_x = self.x + math.cos(up_angle) * radius
        up_tip_y = self.y + math.sin(up_angle) * radius

        down_tip_x = self.x + math.cos(down_angle) * radius
        down_tip_y = self.y + math.sin(down_angle) * radius

        # Bow handle / riser center (slightly forward)
        riser_x = self.x + math.cos(self.angle) * 12
        riser_y = self.y + math.sin(self.angle) * 12

        # Draw string notch / nocking point
        nock_pull = 16.0 * self.draw_amount
        nock_x = self.x - math.cos(self.angle) * (8.0 + nock_pull)
        nock_y = self.y - math.sin(self.angle) * (8.0 + nock_pull)

        # Draw bow limbs glow
        glow_surf = pygame.Surface((radius * 3, radius * 3), pygame.SRCALPHA)
        glow_offset_x = self.x - radius * 1.5
        glow_offset_y = self.y - radius * 1.5

        # Limb curve points (smooth bezier-like arc via polyline)
        limb_points = []
        steps = 14
        for i in range(steps + 1):
            t = i / steps
            interp_ang = up_angle + (down_angle - up_angle) * t
            # slight curve outwards
            cur_r = radius * (1.0 + 0.12 * math.sin(t * math.pi))
            px = self.x + math.cos(interp_ang) * cur_r
            py = self.y + math.sin(interp_ang) * cur_r
            limb_points.append((px, py))

        # 1. Subtle Outer Glow
        if len(limb_points) >= 2:
            pygame.draw.lines(surface, (20, 90, 140), False, limb_points, 6)

        # 2. Sleek Dark Riser Base
        if len(limb_points) >= 2:
            pygame.draw.lines(surface, (30, 41, 59), False, limb_points, 4)

        # 3. Cyan Neon Accent Line
        if len(limb_points) >= 2:
            pygame.draw.lines(surface, COLOR_CYAN, False, limb_points, 2)

        # 4. Bowstring (Two lines meeting at nock)
        string_color = (226, 232, 240)
        pygame.draw.line(surface, string_color, (up_tip_x, up_tip_y), (nock_x, nock_y), 1)
        pygame.draw.line(surface, string_color, (down_tip_x, down_tip_y), (nock_x, nock_y), 1)

        # 5. Bow Handle / Grip Riser
        handle_len = 16
        hx1 = riser_x - math.sin(self.angle) * handle_len * 0.5
        hy1 = riser_y + math.cos(self.angle) * handle_len * 0.5
        hx2 = riser_x + math.sin(self.angle) * handle_len * 0.5
        hy2 = riser_y - math.cos(self.angle) * handle_len * 0.5
        pygame.draw.line(surface, (241, 245, 249), (hx1, hy1), (hx2, hy2), 4)

        # 6. Center Pivot Dot
        pygame.draw.circle(surface, COLOR_CYAN, (int(self.x), int(self.y)), 4)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), 2)

        # 7. When arrow is loaded/drawn, draw ready arrow resting on bow
        arrow_tip_x = nock_x + math.cos(self.angle) * 48
        arrow_tip_y = nock_y + math.sin(self.angle) * 48
        # Arrow shaft
        pygame.draw.line(surface, (203, 213, 225), (nock_x, nock_y), (arrow_tip_x, arrow_tip_y), 2)
        # Arrow head
        tip_surf = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(surface, COLOR_CYAN, (int(arrow_tip_x), int(arrow_tip_y)), 3)
