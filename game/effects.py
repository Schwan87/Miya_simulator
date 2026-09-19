"""
game/effects.py - Visual effects system: Screen shake, Particle bursts,
Shockwave rings, Floating text popups, and Ambient background dust.
"""

import math
import random
import pygame
from settings import (
    COLOR_BG, COLOR_CYAN, COLOR_GOLD, COLOR_GREEN, COLOR_RED,
    SCREEN_WIDTH, SCREEN_HEIGHT
)

class ScreenShake:
    """Decaying trauma-based screen shake for punchy impacts."""
    def __init__(self):
        self.trauma = 0.0
        self.max_offset = 12.0
        self.offset_x = 0
        self.offset_y = 0

    def add_trauma(self, amount, max_offset=None):
        self.trauma = min(1.0, self.trauma + amount)
        if max_offset:
            self.max_offset = max_offset

    def update(self, dt=1.0):
        if self.trauma > 0:
            self.trauma = max(0.0, self.trauma - 0.045 * dt)
            shake_amount = (self.trauma ** 2) * self.max_offset
            self.offset_x = int((random.random() * 2.0 - 1.0) * shake_amount)
            self.offset_y = int((random.random() * 2.0 - 1.0) * shake_amount)
        else:
            self.offset_x = 0
            self.offset_y = 0

    def get_offset(self):
        return self.offset_x, self.offset_y


class Particle:
    """Individual particle with velocity, drag, and fade."""
    def __init__(self, x, y, vx, vy, color, size, lifespan, shape="circle"):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.initial_size = size
        self.lifespan = lifespan
        self.age = 0.0
        self.shape = shape
        self.alive = True

    def update(self, dt=1.0):
        self.age += dt
        if self.age >= self.lifespan:
            self.alive = False
            return

        # Slight air resistance
        self.vx *= 0.94
        self.vy *= 0.94
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Shrink over time
        progress = self.age / self.lifespan
        self.size = max(0.5, self.initial_size * (1.0 - progress))

    def draw(self, surface):
        if not self.alive:
            return
        alpha = int(255 * (1.0 - (self.age / self.lifespan)))
        if alpha <= 0:
            return

        r, g, b = self.color[:3]
        radius = max(1, int(self.size))
        
        # Create small temporary surface with per-pixel alpha for glowing smoothness
        surf_size = radius * 2 + 2
        p_surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
        pygame.draw.circle(p_surf, (r, g, b, alpha), (surf_size // 2, surf_size // 2), radius)
        surface.blit(p_surf, (int(self.x - surf_size // 2), int(self.y - surf_size // 2)))


class Shockwave:
    """Expanding neon ring shockwave for major hits and bullseyes."""
    def __init__(self, x, y, color, max_radius=60, speed=4.0):
        self.x = x
        self.y = y
        self.color = color
        self.radius = 8.0
        self.max_radius = max_radius
        self.speed = speed
        self.alive = True

    def update(self, dt=1.0):
        self.radius += self.speed * dt
        if self.radius >= self.max_radius:
            self.alive = False

    def draw(self, surface):
        if not self.alive:
            return
        progress = self.radius / self.max_radius
        alpha = int(255 * (1.0 - progress))
        if alpha <= 0:
            return

        r, g, b = self.color[:3]
        int_r = int(self.radius)
        surf_dim = int_r * 2 + 6
        s_surf = pygame.Surface((surf_dim, surf_dim), pygame.SRCALPHA)
        center = surf_dim // 2
        width = max(1, int(3 * (1.0 - progress * 0.5)))
        pygame.draw.circle(s_surf, (r, g, b, alpha), (center, center), int_r, width)
        surface.blit(s_surf, (int(self.x - center), int(self.y - center)))


class AmbientParticle:
    """Gentle floating background dust giving a futuristic clean atmosphere."""
    def __init__(self):
        self.reset()
        self.x = random.uniform(0, SCREEN_WIDTH)

    def reset(self):
        self.x = random.uniform(0, SCREEN_WIDTH)
        self.y = random.uniform(0, SCREEN_HEIGHT)
        self.vx = random.uniform(0.15, 0.45)
        self.vy = random.uniform(-0.25, 0.25)
        self.radius = random.uniform(1.0, 2.2)
        self.base_alpha = random.randint(30, 80)
        self.pulse_phase = random.uniform(0, math.pi * 2)

    def update(self, dt=1.0):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.pulse_phase += 0.03 * dt
        if self.x > SCREEN_WIDTH + 10 or self.y < -10 or self.y > SCREEN_HEIGHT + 10:
            self.reset()
            self.x = -5

    def draw(self, surface):
        alpha = int(self.base_alpha + 25 * math.sin(self.pulse_phase))
        alpha = max(10, min(120, alpha))
        p_surf = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.circle(p_surf, (56, 189, 248, alpha), (3, 3), int(self.radius))
        surface.blit(p_surf, (int(self.x) - 3, int(self.y) - 3))


class FloatingText:
    """Smooth animated popup text for 'HIT!', 'BULLSEYE!', 'MISS', and score bonuses."""
    def __init__(self, text, x, y, color, size=32, is_major=False):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.is_major = is_major
        self.lifespan = 45 if not is_major else 60
        self.age = 0.0
        self.alive = True
        self.vy = -1.8 if not is_major else -2.2
        self.font = pygame.font.SysFont("Segoe UI, Arial, sans-serif", self.size, bold=True)

    def update(self, dt=1.0):
        self.age += dt
        if self.age >= self.lifespan:
            self.alive = False
            return
        self.y += self.vy * dt
        self.vy *= 0.95

    def draw(self, surface):
        if not self.alive:
            return

        progress = self.age / self.lifespan
        alpha = int(255 * (1.0 - (progress ** 1.5)))
        if alpha <= 0:
            return

        # Scale popup bounce during first few frames
        scale = 1.0
        if self.age < 8:
            scale = 0.7 + 0.35 * (self.age / 8.0)
        elif self.age < 15:
            scale = 1.05 - 0.05 * ((self.age - 8) / 7.0)

        rendered = self.font.render(self.text, True, self.color)
        if scale != 1.0:
            w = max(1, int(rendered.get_width() * scale))
            h = max(1, int(rendered.get_height() * scale))
            rendered = pygame.transform.smoothscale(rendered, (w, h))

        # Apply alpha
        alpha_surf = pygame.Surface(rendered.get_size(), pygame.SRCALPHA)
        alpha_surf.blit(rendered, (0, 0))
        alpha_surf.set_alpha(alpha)

        # Subtle dark backdrop shadow for extreme clarity
        shadow = self.font.render(self.text, True, (0, 0, 0))
        if scale != 1.0:
            shadow = pygame.transform.smoothscale(shadow, rendered.get_size())
        shadow_surf = pygame.Surface(shadow.get_size(), pygame.SRCALPHA)
        shadow_surf.blit(shadow, (0, 0))
        shadow_surf.set_alpha(int(alpha * 0.6))

        draw_x = int(self.x - rendered.get_width() // 2)
        draw_y = int(self.y - rendered.get_height() // 2)

        surface.blit(shadow_surf, (draw_x + 2, draw_y + 2))
        surface.blit(alpha_surf, (draw_x, draw_y))


class EffectsManager:
    """Coordinates all particle effects, shockwaves, floating text, and screen shake."""
    def __init__(self):
        self.particles = []
        self.shockwaves = []
        self.floating_texts = []
        self.ambient_particles = [AmbientParticle() for _ in range(35)]
        self.shake = ScreenShake()

    def add_hit_burst(self, x, y, is_bullseye=False):
        """Spawns spark burst and shockwave on hit."""
        count = 32 if is_bullseye else 18
        palette = [COLOR_GOLD, (255, 255, 255), COLOR_RED] if is_bullseye else [COLOR_CYAN, COLOR_GREEN, (255, 255, 255)]
        
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2.5, 8.5) if is_bullseye else random.uniform(1.8, 5.5)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            col = random.choice(palette)
            size = random.uniform(2.0, 4.2)
            life = random.uniform(20, 40)
            self.particles.append(Particle(x, y, vx, vy, col, size, life))

        # Add expanding shockwave
        wave_color = COLOR_GOLD if is_bullseye else COLOR_CYAN
        max_r = 75 if is_bullseye else 45
        self.shockwaves.append(Shockwave(x, y, wave_color, max_radius=max_r, speed=4.5))

        # Screen shake
        trauma = 0.55 if is_bullseye else 0.25
        self.shake.add_trauma(trauma)

    def add_miss_effect(self, x, y):
        """Adds subtle dust puff on miss."""
        for _ in range(8):
            angle = random.uniform(-math.pi * 0.8, -math.pi * 0.2)
            speed = random.uniform(1.0, 3.0)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            self.particles.append(Particle(x, y, vx, vy, (120, 130, 145), 2.5, 22))
        self.shake.add_trauma(0.12)

    def add_floating_text(self, text, x, y, color, size=32, is_major=False):
        self.floating_texts.append(FloatingText(text, x, y, color, size, is_major))

    def update(self, dt=1.0):
        # Update shake
        self.shake.update(dt)

        # Update particles
        self.particles = [p for p in self.particles if p.alive]
        for p in self.particles:
            p.update(dt)

        # Update shockwaves
        self.shockwaves = [s for s in self.shockwaves if s.alive]
        for s in self.shockwaves:
            s.update(dt)

        # Update floating texts
        self.floating_texts = [f for f in self.floating_texts if f.alive]
        for f in self.floating_texts:
            f.update(dt)

        # Update ambient particles
        for ap in self.ambient_particles:
            ap.update(dt)

    def draw_ambient(self, surface):
        for ap in self.ambient_particles:
            ap.draw(surface)

    def draw_effects(self, surface):
        for s in self.shockwaves:
            s.draw(surface)
        for p in self.particles:
            p.draw(surface)
        for f in self.floating_texts:
            f.draw(surface)

    def clear(self):
        self.particles.clear()
        self.shockwaves.clear()
        self.floating_texts.clear()
