"""
game/game.py - Core game coordinator handling states, input, physics,
rules, score calculation, rounds, and rendering.
"""

import math
import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BG, COLOR_ARENA_LINE,
    TOTAL_ROUNDS, ARROWS_PER_ROUND, COLOR_GOLD, COLOR_GREEN,
    COLOR_RED, COLOR_CYAN, COMBO_MULTIPLIER_BONUS
)
from game.audio import AudioManager
from game.player import PlayerBow
from game.arrow import Arrow
from game.target import Target
from game.effects import EffectsManager
from ui.menu import MenuManager
from ui.hud import HUD

class Game:
    """Master game controller implementing the state machine and game loop."""

    STATE_MENU = "MENU"
    STATE_HOW_TO_PLAY = "HOW_TO_PLAY"
    STATE_PLAYING = "PLAYING"
    STATE_PAUSED = "PAUSED"
    STATE_GAME_OVER = "GAME_OVER"

    def __init__(self):
        self.state = self.STATE_MENU
        
        # Audio
        self.audio = AudioManager()

        # UI & Effects
        self.effects = EffectsManager()
        self.menu = MenuManager(self.audio)
        self.hud = HUD()

        # Game Entities
        self.player_bow = PlayerBow()
        self.target = Target()
        self.arrows = []

        # Gameplay Session Statistics
        self.current_round = 1
        self.arrows_left = ARROWS_PER_ROUND
        self.score = 0
        self.hits = 0
        self.total_shots = 0
        self.combo = 0
        self.max_combo = 0

        # Shoot delay & transition timers
        self.shoot_cooldown = 0
        self.round_transition_timer = 0
        self.game_over_timer = 0

    def start_new_game(self):
        """Resets all gameplay variables for a fresh match."""
        self.current_round = 1
        self.arrows_left = ARROWS_PER_ROUND
        self.score = 0
        self.hits = 0
        self.total_shots = 0
        self.combo = 0
        self.max_combo = 0
        self.shoot_cooldown = 0
        self.round_transition_timer = 0
        self.game_over_timer = 0

        self.arrows.clear()
        self.effects.clear()
        self.target = Target()
        self.target.configure_round(self.current_round)
        self.state = self.STATE_PLAYING

    def advance_round(self):
        """Progresses to the next round with increased target speed/movement."""
        self.current_round += 1
        self.arrows_left = ARROWS_PER_ROUND
        self.target.configure_round(self.current_round)
        self.target.reposition_randomly()
        
        # Visual notification
        self.effects.add_floating_text(
            f"ROUND {self.current_round}",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2,
            COLOR_CYAN,
            size=44,
            is_major=True
        )

    def handle_events(self, events):
        """Dispatches SDL events according to the active game state."""
        for event in events:
            if event.type == pygame.QUIT:
                return False

            if self.state == self.STATE_MENU:
                action = self.menu.handle_menu_event(event)
                if action == "PLAY":
                    self.start_new_game()
                elif action == "HOW_TO_PLAY":
                    self.state = self.STATE_HOW_TO_PLAY
                elif action == "QUIT":
                    return False

            elif self.state == self.STATE_HOW_TO_PLAY:
                action = self.menu.handle_how_to_play_event(event)
                if action == "BACK":
                    self.state = self.STATE_MENU

            elif self.state == self.STATE_PAUSED:
                action = self.menu.handle_pause_event(event)
                if action == "RESUME":
                    self.state = self.STATE_PLAYING
                elif action == "RESTART":
                    self.start_new_game()
                elif action == "MAIN_MENU":
                    self.state = self.STATE_MENU

            elif self.state == self.STATE_GAME_OVER:
                action = self.menu.handle_game_over_event(event)
                if action == "PLAY_AGAIN":
                    self.start_new_game()
                elif action == "MAIN_MENU":
                    self.state = self.STATE_MENU

            elif self.state == self.STATE_PLAYING:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.audio.play("click")
                    self.state = self.STATE_PAUSED
                
                # Bow Aiming & Shooting
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Avoid shooting if clicking in top HUD area
                    if event.pos[1] > 75:
                        self.player_bow.set_draw_state(True)

                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if self.player_bow.is_drawn:
                        self.player_bow.set_draw_state(False)
                        self.shoot_arrow()

        return True

    def shoot_arrow(self):
        """Fires an arrow from the bow if cooldown and arrows remaining permit."""
        if self.arrows_left <= 0 or self.shoot_cooldown > 0:
            return

        # Allow up to 3 concurrent arrows in flight with short cooldown
        flying_count = sum(1 for a in self.arrows if a.state == Arrow.STATE_FLYING)
        if flying_count >= 3:
            return

        spawn_pos, angle, _ = self.player_bow.get_arrow_spawn()
        arrow = Arrow(spawn_pos[0], spawn_pos[1], angle)
        self.arrows.append(arrow)

        self.arrows_left -= 1
        self.total_shots += 1
        self.shoot_cooldown = 18
        self.audio.play("shoot")

    def update(self, dt=1.0):
        """Updates game entities, physics, collision detection, and transitions."""
        self.menu.update(dt)

        if self.state == self.STATE_PLAYING:
            mouse_pos = pygame.mouse.get_pos()
            self.player_bow.update_aim(mouse_pos)
            self.player_bow.update(dt)
            self.target.update(dt)
            self.effects.update(dt)

            if self.shoot_cooldown > 0:
                self.shoot_cooldown = max(0, self.shoot_cooldown - int(dt))

            # Update Arrows & Collision
            self._update_arrows_and_collisions(dt)

            # Round & Game Over Progression Check
            self._check_round_progression(dt)

        elif self.state in (self.STATE_MENU, self.STATE_HOW_TO_PLAY, self.STATE_PAUSED, self.STATE_GAME_OVER):
            self.effects.update(dt)

    def _update_arrows_and_collisions(self, dt):
        """Handles continuous collision detection between arrow tips and the circular target."""
        for arrow in self.arrows:
            if not arrow.active:
                continue

            prev_tip = arrow.get_tip_pos()
            arrow.update(dt)
            new_tip = arrow.get_tip_pos()

            if arrow.state == Arrow.STATE_FLYING:
                # Continuous collision detection along arrow tip segment
                is_hit, points, hit_type, hit_x, hit_y = self.target.check_hit_segment(
                    prev_tip[0], prev_tip[1], new_tip[0], new_tip[1]
                )

                if is_hit:
                    # Adjust arrow so tip is exactly at impact point
                    half_len = arrow.length * 0.5
                    arrow.x = hit_x - math.cos(arrow.angle) * half_len
                    arrow.y = hit_y - math.sin(arrow.angle) * half_len
                    arrow.stick_to_target(self.target)

                    self.hits += 1
                    self.combo += 1
                    self.max_combo = max(self.max_combo, self.combo)

                    # Combo bonus calculation
                    bonus = (self.combo - 1) * COMBO_MULTIPLIER_BONUS
                    earned = points + bonus
                    self.score += earned

                    is_bullseye = (hit_type == "BULLSEYE")
                    if is_bullseye:
                        self.audio.play("bullseye")
                        self.effects.add_floating_text("BULLSEYE!", self.target.x - 30, self.target.y - 45, COLOR_GOLD, size=38, is_major=True)
                    else:
                        self.audio.play("hit")
                        self.effects.add_floating_text("HIT!", self.target.x - 20, self.target.y - 40, COLOR_GREEN, size=32)

                    # Score popup
                    score_str = f"+{points}" if bonus == 0 else f"+{points} (+{bonus})"
                    self.effects.add_floating_text(score_str, self.target.x + 20, self.target.y - 15, COLOR_CYAN, size=24)

                    self.effects.add_hit_burst(hit_x, hit_y, is_bullseye)

                elif arrow.state == Arrow.STATE_MISSED or (arrow.x > self.target.x + 80 and arrow.state == Arrow.STATE_FLYING):
                    # MISS!
                    arrow.state = Arrow.STATE_MISSED
                    arrow.active = False
                    self.combo = 0
                    self.audio.play("miss")
                    self.effects.add_floating_text("MISS", min(SCREEN_WIDTH - 60, arrow.x), max(80, min(SCREEN_HEIGHT - 60, arrow.y)), COLOR_RED, size=30)
                    self.effects.add_miss_effect(arrow.x, arrow.y)

        # Cleanup fully inactive arrows
        self.arrows = [a for a in self.arrows if a.active or a.state == Arrow.STATE_STUCK]
        # Keep maximum stuck arrows reasonable
        if len(self.arrows) > 8:
            self.arrows.pop(0)

    def _check_round_progression(self, dt):
        """Monitors when all arrows in the round are spent and resolves transitions."""
        all_resolved = not any(a.state == Arrow.STATE_FLYING for a in self.arrows)

        if self.arrows_left == 0 and all_resolved:
            if self.current_round < TOTAL_ROUNDS:
                self.round_transition_timer += dt
                if self.round_transition_timer > 60:
                    self.round_transition_timer = 0
                    self.advance_round()
            else:
                # Last round finished -> Game Over
                self.game_over_timer += dt
                if self.game_over_timer > 75:
                    self.state = self.STATE_GAME_OVER

    def draw(self, surface):
        """Draws current state with screen shake offset and dark minimalist aesthetic."""
        surface.fill(COLOR_BG)

        # Ambient floating dust for atmosphere
        self.effects.draw_ambient(surface)

        if self.state == self.STATE_MENU:
            self._draw_arena_decorations(surface)
            self.menu.draw_menu(surface)

        elif self.state == self.STATE_HOW_TO_PLAY:
            self._draw_arena_decorations(surface)
            self.menu.draw_how_to_play(surface)

        elif self.state in (self.STATE_PLAYING, self.STATE_PAUSED):
            # Screen shake offset
            shake_x, shake_y = self.effects.shake.get_offset()
            
            # Create arena surface for shake translation
            arena_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            arena_surf.fill(COLOR_BG)
            
            # Draw Arena grid / bounds
            self._draw_arena_decorations(arena_surf)

            # Draw Target
            self.target.draw(arena_surf)

            # Draw Stuck & Flying Arrows
            for arrow in self.arrows:
                arrow.draw(arena_surf)

            # Draw Bow & Trajectory
            self.player_bow.draw_trajectory(arena_surf)
            self.player_bow.draw(arena_surf)

            # Draw Custom Aim Reticle at mouse position
            self._draw_aim_reticle(arena_surf)

            # Draw Effects (bursts, shockwaves, floating text)
            self.effects.draw_effects(arena_surf)

            # Blit shaken arena to main surface
            surface.blit(arena_surf, (shake_x, shake_y))

            # HUD is drawn on top without shake for crystal clarity
            self.hud.draw(
                surface,
                score=self.score,
                current_round=self.current_round,
                max_rounds=TOTAL_ROUNDS,
                arrows_left=self.arrows_left,
                max_arrows=ARROWS_PER_ROUND,
                combo=self.combo,
                hits=self.hits,
                shots=self.total_shots
            )

            # Draw pause overlay if paused
            if self.state == self.STATE_PAUSED:
                self.menu.draw_pause(surface)

        elif self.state == self.STATE_GAME_OVER:
            self._draw_arena_decorations(surface)
            self.menu.draw_game_over(
                surface,
                final_score=self.score,
                hits=self.hits,
                total_shots=self.total_shots,
                max_combo=self.max_combo
            )

    def _draw_arena_decorations(self, surface):
        """Draws subtle modern grid lines and arena borders."""
        # Top boundary line below HUD
        pygame.draw.line(surface, COLOR_ARENA_LINE, (0, 70), (SCREEN_WIDTH, 70), 1)
        # Bottom boundary line
        pygame.draw.line(surface, COLOR_ARENA_LINE, (0, SCREEN_HEIGHT - 30), (SCREEN_WIDTH, SCREEN_HEIGHT - 30), 1)

        # Subtle vertical launch demarcation
        pygame.draw.line(surface, (20, 26, 38), (220, 70), (220, SCREEN_HEIGHT - 30), 1)

        # Target range line
        pygame.draw.line(surface, (20, 26, 38), (SCREEN_WIDTH - 220, 70), (SCREEN_WIDTH - 220, SCREEN_HEIGHT - 30), 1)

        # Center subtle crosshair mark in arena center
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        pygame.draw.line(surface, (24, 30, 44), (cx - 15, cy), (cx + 15, cy), 1)
        pygame.draw.line(surface, (24, 30, 44), (cx, cy - 15), (cx, cy + 15), 1)

    def _draw_aim_reticle(self, surface):
        """Draws a sleek minimalist futuristic aim indicator at the mouse position."""
        mx, my = pygame.mouse.get_pos()
        if my < 75:  # Don't draw reticle inside top HUD
            return

        is_drawn = self.player_bow.is_drawn
        ret_r = 14 if not is_drawn else 18
        alpha = 180 if not is_drawn else 240
        col = (56, 189, 248, alpha)

        ret_surf = pygame.Surface((ret_r * 2 + 10, ret_r * 2 + 10), pygame.SRCALPHA)
        center = ret_r + 5

        # Thin outer target circle
        pygame.draw.circle(ret_surf, col, (center, center), ret_r, 1)

        # 4 subtle tick marks
        tick_len = 5
        pygame.draw.line(ret_surf, col, (center - ret_r - 2, center), (center - ret_r + tick_len, center), 1)
        pygame.draw.line(ret_surf, col, (center + ret_r - tick_len, center), (center + ret_r + 2, center), 1)
        pygame.draw.line(ret_surf, col, (center, center - ret_r - 2), (center, center - ret_r + tick_len), 1)
        pygame.draw.line(ret_surf, col, (center, center + ret_r - tick_len), (center, center + ret_r + 2), 1)

        # Center dot
        pygame.draw.circle(ret_surf, (255, 255, 255, alpha), (center, center), 2)

        surface.blit(ret_surf, (mx - center, my - center))
