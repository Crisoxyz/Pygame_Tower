import random
import pygame
from settings import PARTICLE_MIN_SIZE, PARTICLE_MAX_SIZE


class DeathParticle:

  def __init__(self, x, y, target_x, target_y, color, size):
    self.x = x
    self.y = y
    self.target_x = target_x
    self.target_y = target_y

    # Spinta iniziale per l'esplosione dei frammenti
    self.vx = random.uniform(-4, 4)
    self.vy = random.uniform(-4, 4)
    self.size = size  # Dimensione del blocchetto proporzionale al campionamento
    self.color = color

    # Fasi dell'animazione
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
      dx = self.target_x - self.x
      dy = self.target_y - self.y
      self.x += dx * 0.12
      self.y += dy * 0.12