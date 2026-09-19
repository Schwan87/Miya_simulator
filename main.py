"""
main.py - Entry point for the 2D Archery Precision Challenge Game.
Modern, minimalist, dark-themed archery target shooting simulator.
"""

import sys
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE
from game.game import Game

def create_window_icon():
    """Generates a stylish modern procedural icon for the window titlebar."""
    icon_surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    # Background circle
    pygame.draw.circle(icon_surf, (15, 23, 42), (16, 16), 15)
    # Cyan outer ring
    pygame.draw.circle(icon_surf, (56, 189, 248), (16, 16), 14, 2)
    # Gold bullseye
    pygame.draw.circle(icon_surf, (251, 191, 36), (16, 16), 6)
    # Red center
    pygame.draw.circle(icon_surf, (239, 68, 68), (16, 16), 3)
    return icon_surf

def main():
    """Initializes Pygame, creates display, and executes the game loop."""
    pygame.init()
    pygame.font.init()

    # Set up display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    
    try:
        pygame.display.set_icon(create_window_icon())
    except Exception:
        pass

    clock = pygame.time.Clock()
    game = Game()

    running = True
    while running:
        # Cap frame rate to 60 FPS and calculate delta time (normalized to ~1.0 at 60FPS)
        raw_dt_ms = clock.tick(FPS)
        dt = min(2.0, raw_dt_ms / (1000.0 / FPS))

        # Handle events
        events = pygame.event.get()
        if not game.handle_events(events):
            running = False
            break

        # Update game state
        game.update(dt)

        # Render current frame
        game.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
