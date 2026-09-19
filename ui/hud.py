"""
ui/hud.py - Minimalist futuristic heads-up display showing score, round,
remaining arrows, accuracy, and combo streak.
"""

import pygame
from settings import (
    SCREEN_WIDTH, COLOR_TEXT_WHITE, COLOR_TEXT_MUTED, COLOR_CYAN,
    COLOR_GOLD, COLOR_GREEN, COLOR_RED
)

class HUD:
    """Renders the top gameplay status bar with sleek typography and glass panel."""

    def __init__(self):
        self.font_main = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 20, bold=True)
        self.font_val = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 26, bold=True)
        self.font_sub = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 15, bold=False)

    def draw(self, surface, score, current_round, max_rounds, arrows_left, max_arrows, combo=0, hits=0, shots=0):
        """Draws the top HUD bar."""
        # Top banner background (glassmorphic dark bar)
        bar_height = 68
        bar_surf = pygame.Surface((SCREEN_WIDTH, bar_height), pygame.SRCALPHA)
        bar_surf.fill((12, 16, 24, 215))
        # Subtle bottom border line
        pygame.draw.line(bar_surf, (30, 41, 59, 180), (0, bar_height - 1), (SCREEN_WIDTH, bar_height - 1), 1)
        surface.blit(bar_surf, (0, 0))

        # 1. SCORE Section (Left-Center)
        self._render_stat_block(
            surface,
            label="SCORE",
            value=f"{score:,}",
            val_color=COLOR_CYAN,
            x=180,
            y=34
        )

        # 2. ROUND Section (Center)
        self._render_stat_block(
            surface,
            label="ROUND",
            value=f"{current_round} / {max_rounds}",
            val_color=COLOR_TEXT_WHITE,
            x=SCREEN_WIDTH // 2 - 120,
            y=34
        )

        # 3. ARROWS Section
        self._render_stat_block(
            surface,
            label="ARROWS",
            value=f"{arrows_left}",
            val_color=COLOR_GREEN if arrows_left > 2 else COLOR_RED,
            x=SCREEN_WIDTH // 2 + 120,
            y=34
        )

        # 4. Accuracy / Hit stats (Right-Center)
        acc_pct = int((hits / shots * 100)) if shots > 0 else 100
        self._render_stat_block(
            surface,
            label="ACCURACY",
            value=f"{acc_pct}%",
            val_color=COLOR_GOLD if acc_pct >= 80 else COLOR_TEXT_MUTED,
            x=SCREEN_WIDTH - 220,
            y=34
        )

        # 5. Combo multiplier badge if active
        if combo > 1:
            badge_text = f"STREAK x{combo}"
            b_surf = self.font_main.render(badge_text, True, COLOR_GOLD)
            bx = SCREEN_WIDTH // 2
            by = 48
            # glow backing
            pad_x, pad_y = 12, 4
            bg_rect = pygame.Rect(bx - b_surf.get_width() // 2 - pad_x, by - pad_y,
                                  b_surf.get_width() + pad_x * 2, b_surf.get_height() + pad_y * 2)
            pygame.draw.rect(surface, (40, 30, 10, 200), bg_rect, border_radius=6)
            pygame.draw.rect(surface, COLOR_GOLD, bg_rect, 1, border_radius=6)
            surface.blit(b_surf, (bx - b_surf.get_width() // 2, by))

        # 6. Subtle control hint
        hint_surf = self.font_sub.render("[ESC] Pause", True, (100, 116, 139))
        surface.blit(hint_surf, (24, 25))

    def _render_stat_block(self, surface, label, value, val_color, x, y):
        lbl_surf = self.font_sub.render(label, True, COLOR_TEXT_MUTED)
        val_surf = self.font_val.render(value, True, val_color)

        total_width = max(lbl_surf.get_width(), val_surf.get_width())
        
        surface.blit(lbl_surf, (x - total_width // 2, y - 20))
        surface.blit(val_surf, (x - total_width // 2, y + 2))
