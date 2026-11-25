import random
import pygame


class DeathParticle:

  def __init__(self, x, y, target_x, target_y, color, size):
    self.x = x
    self.y = y
    self.target_x = target_x
    self.target_y = target_y
    self.vx = random.uniform(-4, 4)
    self.vy = random.uniform(-4, 4)
    self.size = size
    self.color = color
    self.phase = "exploding"
    self.timer = random.randint(12, 20)

  def update(self):
    if self.phase == "exploding":
      self.x += self.vx
      self.y += self.vy
      self.vx *= 0.88
      self.vy *= 0.88
      self.timer -= 1
      if self.timer <= 0:
        self.phase = "returning"
    elif self.phase == "returning":
      self.x += (self.target_x - self.x) * 0.12
      self.y += (self.target_y - self.y) * 0.12


class DustParticle:

  def __init__(
      self,
      x,
      y,
      vx,
      vy,
      color,
      size,
      lifetime=18,
      gravity=0.04,
      drag=0.92,
  ):
    self.x = float(x)
    self.y = float(y)
    self.vx = float(vx)
    self.vy = float(vy)
    self.color = color
    self.size = size
    self.lifetime = max(1, int(lifetime))
    self.max_lifetime = self.lifetime
    self.gravity = gravity
    self.drag = drag
    self.alive = True

  def update(self):
    if not self.alive:
      return
    self.x += self.vx
    self.y += self.vy
    self.vx *= self.drag
    self.vy = (self.vy + self.gravity) * self.drag
    self.lifetime -= 1
    if self.lifetime <= 0:
      self.alive = False

  def draw(self, surface, camera_x=0, camera_y=0):
    if not self.alive or self.size <= 0:
      return

    alpha = max(0, min(255, int(255 * (self.lifetime / self.max_lifetime))))
    draw_x = int(round(self.x - camera_x))
    draw_y = int(round(self.y - camera_y))

    if alpha >= 250:
      pygame.draw.rect(surface, self.color, (draw_x, draw_y, self.size, self.size))
    else:
      particle_surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
      r, g, b = self.color[0], self.color[1], self.color[2]
      particle_surf.fill((r, g, b, alpha))
      surface.blit(particle_surf, (draw_x, draw_y))
