"""
ui/buttons.py - Modern interactive buttons with hover glow, smooth transitions,
and sound integration.
"""

import pygame
from settings import (
    COLOR_CYAN, COLOR_CARD_BG, COLOR_TEXT_WHITE, COLOR_TEXT_MUTED
)

class Button:
    """Sleek minimalist dark-mode button with hover animation and glow."""

    def __init__(self, text, x, y, width=220, height=52, font_size=22, callback=None):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.callback = callback

        self.rect = pygame.Rect(x - width // 2, y - height // 2, width, height)
        self.is_hovered = False
        self.hover_progress = 0.0 # 0.0 to 1.0 smooth lerp
        
        self.font = pygame.font.SysFont("Segoe UI, Arial, sans-serif", font_size, bold=True)

    def handle_event(self, event, audio_mgr=None):
        """Processes mouse events. Returns True if clicked."""
        if event.type == pygame.MOUSEMOTION:
            was_hovered = self.is_hovered
            self.is_hovered = self.rect.collidepoint(event.pos)
            if not was_hovered and self.is_hovered and audio_mgr:
                audio_mgr.play("click")

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if audio_mgr:
                    audio_mgr.play("click")
                if self.callback:
                    self.callback()
                return True
        return False

    def update(self, dt=1.0):
        target = 1.0 if self.is_hovered else 0.0
        self.hover_progress += (target - self.hover_progress) * 0.22 * dt

    def draw(self, surface):
        """Renders the button with glowing border and background."""
        hp = self.hover_progress

        # Base dimensions with subtle hover scale
        scale_pad = int(hp * 2)
        draw_rect = pygame.Rect(
            self.rect.x - scale_pad,
            self.rect.y - scale_pad,
            self.rect.width + scale_pad * 2,
            self.rect.height + scale_pad * 2
        )

        # 1. Dark Glass Card Background
        bg_alpha = int(180 + hp * 60)
        bg_surf = pygame.Surface((draw_rect.width, draw_rect.height), pygame.SRCALPHA)
        # Background color shifts slightly brighter on hover
        r = int(18 + hp * 16)
        g = int(22 + hp * 22)
        b = int(32 + hp * 36)
        pygame.draw.rect(bg_surf, (r, g, b, bg_alpha), (0, 0, draw_rect.width, draw_rect.height), border_radius=10)
        surface.blit(bg_surf, (draw_rect.x, draw_rect.y))

        # 2. Border Glow (Cyan when hovered, subtle muted slate when idle)
        border_r = int(51 + hp * (56 - 51))
        border_g = int(65 + hp * (189 - 65))
        border_b = int(85 + hp * (248 - 85))
        border_color = (border_r, border_g, border_b)
        border_width = 2 if hp > 0.3 else 1
        pygame.draw.rect(surface, border_color, draw_rect, border_width, border_radius=10)

        # 3. Outer Glow when hovered
        if hp > 0.05:
            glow_surf = pygame.Surface((draw_rect.width + 12, draw_rect.height + 12), pygame.SRCALPHA)
            glow_alpha = int(hp * 65)
            pygame.draw.rect(
                glow_surf,
                (56, 189, 248, glow_alpha),
                (0, 0, draw_rect.width + 12, draw_rect.height + 12),
                2,
                border_radius=14
            )
            surface.blit(glow_surf, (draw_rect.x - 6, draw_rect.y - 6))

        # 4. Text Label
        text_color = COLOR_TEXT_WHITE if hp > 0.4 else COLOR_TEXT_MUTED
        txt_surf = self.font.render(self.text, True, text_color)
        tx = draw_rect.centerx - txt_surf.get_width() // 2
        ty = draw_rect.centery - txt_surf.get_height() // 2
        surface.blit(txt_surf, (tx, ty))
