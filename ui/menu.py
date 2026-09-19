"""
ui/menu.py - Screen layouts for Main Menu, How To Play, Game Over, and Pause.
"""

import math
import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_CYAN, COLOR_GOLD, COLOR_GREEN,
    COLOR_RED, COLOR_TEXT_WHITE, COLOR_TEXT_MUTED
)
from ui.buttons import Button

class MenuManager:
    """Manages menu screens, UI buttons, transitions, and text layouts."""

    def __init__(self, audio_mgr):
        self.audio = audio_mgr

        # Fonts
        self.font_title = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 68, bold=True)
        self.font_subtitle = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 22, bold=False)
        self.font_heading = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 40, bold=True)
        self.font_body = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 20, bold=False)
        self.font_bold = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 22, bold=True)
        self.font_stat_val = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 46, bold=True)

        # Buttons for Main Menu
        cx = SCREEN_WIDTH // 2
        self.btn_play = Button("PLAY", cx, 420, width=240, height=54, font_size=24)
        self.btn_how_to_play = Button("HOW TO PLAY", cx, 495, width=240, height=54, font_size=22)
        self.btn_quit = Button("QUIT", cx, 570, width=240, height=54, font_size=22)

        # Buttons for How To Play
        self.btn_back_how = Button("BACK", cx, 630, width=200, height=50, font_size=22)

        # Buttons for Game Over
        self.btn_play_again = Button("PLAY AGAIN", cx - 140, 600, width=230, height=54, font_size=22)
        self.btn_main_menu_go = Button("MAIN MENU", cx + 140, 600, width=230, height=54, font_size=22)

        # Buttons for Pause
        self.btn_resume = Button("RESUME", cx, 320, width=240, height=52, font_size=22)
        self.btn_restart_pause = Button("RESTART", cx, 395, width=240, height=52, font_size=22)
        self.btn_main_menu_pause = Button("MAIN MENU", cx, 470, width=240, height=52, font_size=22)

        self.anim_timer = 0.0

    def update(self, dt=1.0):
        self.anim_timer += 0.03 * dt
        for btn in [
            self.btn_play, self.btn_how_to_play, self.btn_quit,
            self.btn_back_how, self.btn_play_again, self.btn_main_menu_go,
            self.btn_resume, self.btn_restart_pause, self.btn_main_menu_pause
        ]:
            btn.update(dt)

    # ---------------- MAIN MENU ----------------
    def handle_menu_event(self, event):
        """Returns action string: 'PLAY', 'HOW_TO_PLAY', 'QUIT', or None."""
        if self.btn_play.handle_event(event, self.audio):
            return "PLAY"
        if self.btn_how_to_play.handle_event(event, self.audio):
            return "HOW_TO_PLAY"
        if self.btn_quit.handle_event(event, self.audio):
            return "QUIT"
        return None

    def draw_menu(self, surface):
        cx = SCREEN_WIDTH // 2
        
        # Animated decorative rings behind title
        pulse_r = int(120 + 8 * math.sin(self.anim_timer * 1.5))
        halo_surf = pygame.Surface((pulse_r * 2 + 10, pulse_r * 2 + 10), pygame.SRCALPHA)
        pygame.draw.circle(halo_surf, (56, 189, 248, 25), (pulse_r + 5, pulse_r + 5), pulse_r, 2)
        pygame.draw.circle(halo_surf, (251, 191, 36, 30), (pulse_r + 5, pulse_r + 5), int(pulse_r * 0.65), 1)
        surface.blit(halo_surf, (cx - pulse_r - 5, 200 - pulse_r - 5))

        # Title with cyan neon glow
        title_surf = self.font_title.render("ARCHERY", True, COLOR_TEXT_WHITE)
        title_shadow = self.font_title.render("ARCHERY", True, (56, 189, 248))
        
        # Glow blit
        glow_alpha = pygame.Surface(title_shadow.get_size(), pygame.SRCALPHA)
        glow_alpha.blit(title_shadow, (0, 0))
        glow_alpha.set_alpha(80)
        surface.blit(glow_alpha, (cx - title_surf.get_width() // 2 - 2, 160 - 2))
        surface.blit(title_surf, (cx - title_surf.get_width() // 2, 160))

        # Subtitle
        sub_surf = self.font_subtitle.render("P R E C I S I O N   C H A L L E N G E", True, COLOR_CYAN)
        surface.blit(sub_surf, (cx - sub_surf.get_width() // 2, 245))

        # Horizontal accent lines
        line_w = 160
        y_line = 290
        pygame.draw.line(surface, (56, 189, 248, 120), (cx - line_w, y_line), (cx + line_w, y_line), 1)
        pygame.draw.circle(surface, COLOR_CYAN, (cx, y_line), 3)

        # Buttons
        self.btn_play.draw(surface)
        self.btn_how_to_play.draw(surface)
        self.btn_quit.draw(surface)

    # ---------------- HOW TO PLAY ----------------
    def handle_how_to_play_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.audio:
                self.audio.play("click")
            return "BACK"
        if self.btn_back_how.handle_event(event, self.audio):
            return "BACK"
        return None

    def draw_how_to_play(self, surface):
        cx = SCREEN_WIDTH // 2

        # Title
        title_surf = self.font_heading.render("HOW TO PLAY", True, COLOR_TEXT_WHITE)
        surface.blit(title_surf, (cx - title_surf.get_width() // 2, 80))

        # Card container for instructions
        card_w, card_h = 760, 430
        card_rect = pygame.Rect(cx - card_w // 2, 160, card_w, card_h)
        card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        card_surf.fill((18, 22, 32, 235))
        pygame.draw.rect(card_surf, (51, 65, 85, 200), (0, 0, card_w, card_h), 1, border_radius=12)
        surface.blit(card_surf, (card_rect.x, card_rect.y))

        # Left Column: Controls
        col1_x = card_rect.x + 60
        y = card_rect.y + 45

        c_head = self.font_bold.render("CONTROLS & MECHANICS", True, COLOR_CYAN)
        surface.blit(c_head, (col1_x, y))
        y += 42

        instructions = [
            ("Move Mouse", "Aim the bow angle"),
            ("Left Click", "Shoot arrow with velocity"),
            ("Hit Target", "Score points based on ring"),
            ("Bullseye", "Maximum 100 points reward"),
            ("Combo Streak", "Consecutive hits give multipliers")
        ]

        for action, desc in instructions:
            act_s = self.font_bold.render(action, True, COLOR_TEXT_WHITE)
            arrow_s = self.font_body.render(" ->  " + desc, True, COLOR_TEXT_MUTED)
            surface.blit(act_s, (col1_x, y))
            surface.blit(arrow_s, (col1_x + 150, y + 2))
            y += 38

        # Right Column: Scoring Ring Legend
        col2_x = card_rect.x + 460
        y2 = card_rect.y + 45
        s_head = self.font_bold.render("RING VALUES", True, COLOR_GOLD)
        surface.blit(s_head, (col2_x, y2))
        y2 += 42

        tiers = [
            ("Bullseye", "100 pts", (239, 68, 68)),
            ("Inner Ring", "50 pts", (245, 158, 11)),
            ("Middle Ring", "25 pts", (2, 132, 199)),
            ("Outer Ring", "10 pts", (71, 85, 105)),
        ]

        for name, pts, col in tiers:
            # mini dot indicator
            pygame.draw.circle(surface, col, (col2_x + 12, y2 + 12), 8)
            n_s = self.font_body.render(name, True, COLOR_TEXT_WHITE)
            p_s = self.font_bold.render(pts, True, col)
            surface.blit(n_s, (col2_x + 30, y2))
            surface.blit(p_s, (col2_x + 160, y2))
            y2 += 38

        # ESC hint
        esc_hint = self.font_body.render("Press ESC to return to main menu", True, (100, 116, 139))
        surface.blit(esc_hint, (cx - esc_hint.get_width() // 2, card_rect.bottom - 40))

        # Back button
        self.btn_back_how.draw(surface)

    # ---------------- GAME OVER ----------------
    def handle_game_over_event(self, event):
        if self.btn_play_again.handle_event(event, self.audio):
            return "PLAY_AGAIN"
        if self.btn_main_menu_go.handle_event(event, self.audio):
            return "MAIN_MENU"
        return None

    def draw_game_over(self, surface, final_score, hits, total_shots, max_combo):
        cx = SCREEN_WIDTH // 2

        # Title
        title_surf = self.font_heading.render("GAME OVER", True, COLOR_RED)
        surface.blit(title_surf, (cx - title_surf.get_width() // 2, 90))

        sub_surf = self.font_subtitle.render("Challenge Summary", True, COLOR_TEXT_MUTED)
        surface.blit(sub_surf, (cx - sub_surf.get_width() // 2, 145))

        # Stats Card
        card_w, card_h = 680, 360
        card_rect = pygame.Rect(cx - card_w // 2, 195, card_w, card_h)
        card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        card_surf.fill((18, 22, 32, 240))
        pygame.draw.rect(card_surf, (51, 65, 85, 200), (0, 0, card_w, card_h), 1, border_radius=12)
        surface.blit(card_surf, (card_rect.x, card_rect.y))

        # 1. Big Final Score Box
        fs_lbl = self.font_body.render("FINAL SCORE", True, COLOR_TEXT_MUTED)
        fs_val = self.font_stat_val.render(f"{final_score:,}", True, COLOR_CYAN)
        surface.blit(fs_lbl, (cx - fs_lbl.get_width() // 2, card_rect.y + 35))
        surface.blit(fs_val, (cx - fs_val.get_width() // 2, card_rect.y + 65))

        # Divider line
        div_y = card_rect.y + 145
        pygame.draw.line(surface, (30, 41, 59), (card_rect.x + 40, div_y), (card_rect.right - 40, div_y), 1)

        # 3 Sub-stats row
        accuracy_pct = int((hits / total_shots * 100)) if total_shots > 0 else 0
        stats = [
            ("TARGETS HIT", f"{hits}", COLOR_GREEN),
            ("ACCURACY", f"{accuracy_pct}%", COLOR_GOLD),
            ("MAX STREAK", f"x{max_combo}", COLOR_CYAN)
        ]

        col_spacing = card_w // 3
        for i, (label, val, val_col) in enumerate(stats):
            bx = card_rect.x + col_spacing * i + col_spacing // 2
            lbl_s = self.font_body.render(label, True, COLOR_TEXT_MUTED)
            val_s = self.font_heading.render(val, True, val_col)
            surface.blit(lbl_s, (bx - lbl_s.get_width() // 2, div_y + 30))
            surface.blit(val_s, (bx - val_s.get_width() // 2, div_y + 65))

        # Buttons
        self.btn_play_again.draw(surface)
        self.btn_main_menu_go.draw(surface)

    # ---------------- PAUSE OVERLAY ----------------
    def handle_pause_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.audio:
                self.audio.play("click")
            return "RESUME"
        if self.btn_resume.handle_event(event, self.audio):
            return "RESUME"
        if self.btn_restart_pause.handle_event(event, self.audio):
            return "RESTART"
        if self.btn_main_menu_pause.handle_event(event, self.audio):
            return "MAIN_MENU"
        return None

    def draw_pause(self, surface):
        cx = SCREEN_WIDTH // 2

        # Dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 10, 15, 180))
        surface.blit(overlay, (0, 0))

        # Pause Title
        p_title = self.font_heading.render("GAME PAUSED", True, COLOR_TEXT_WHITE)
        surface.blit(p_title, (cx - p_title.get_width() // 2, 220))

        sub_tip = self.font_body.render("Press ESC to resume", True, COLOR_TEXT_MUTED)
        surface.blit(sub_tip, (cx - sub_tip.get_width() // 2, 275))

        # Pause buttons
        self.btn_resume.draw(surface)
        self.btn_restart_pause.draw(surface)
        self.btn_main_menu_pause.draw(surface)
