import random
import pygame
from particles import DeathParticle
from settings import (
    COYOTE_DURATION,
    GRAVITY,
    JUMP_BUFFER_DURATION,
    JUMP_FORCE,
    PARTICLE_COUNT,
    PLAYER_HEIGHT,
    PLAYER_IMAGE_PATH,
    PLAYER_SPEED,
    PLAYER_WIDTH,
)


class Player(pygame.sprite.Sprite):

  def __init__(self, x, y):
    super().__init__()
    self.spawn_x = x
    self.spawn_y = y

    # Caricamento dell'immagine PNG del player con fallback di sicurezza
    try:
      original_image = pygame.image.load(PLAYER_IMAGE_PATH).convert_alpha()
      self.image = pygame.transform.scale(
          original_image, (PLAYER_WIDTH, PLAYER_HEIGHT)
      )
    except (pygame.error, FileNotFoundError):
      # Fallback: se manca il file PNG, crea un rettangolo rosso
      self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
      self.image.fill((230, 50, 50))

    self.rect = self.image.get_rect(topleft=(x, y))

    # Vettori di movimento
    self.velocity_x = 0
    self.velocity_y = 0
    self.on_ground = False

    # Meccaniche di salto basate sui settings
    self.coyote_timer = 0
    self.coyote_duration = COYOTE_DURATION
    self.jump_buffer_timer = 0
    self.jump_buffer_duration = JUMP_BUFFER_DURATION
    self.jumps_left = 1

    # Stato del player ('normal' o 'animating_death')
    self.state = "normal"
    self.particles = []

  def start_death_animation(self):
    if self.state != "normal":
      return

    self.state = "animating_death"
    self.velocity_x = 0
    self.velocity_y = 0
    self.particles = []
    self.image.set_alpha(0)  # Nasconde lo sprite principale

    start_x = self.rect.x
    start_y = self.rect.y

    # Campionamento a blocchi (step = 2) per un numero bilanciato di particelle
    step = 2
    particle_size = 2

    for py_offset in range(0, PLAYER_HEIGHT, step):
      for px_offset in range(0, PLAYER_WIDTH, step):
        try:
          pixel_color = self.image.get_at((px_offset, py_offset))
          if len(pixel_color) > 3 and pixel_color[3] == 0:
            continue

          world_px = start_x + px_offset
          world_py = start_y + py_offset

          target_px = self.spawn_x + px_offset
          target_py = self.spawn_y + py_offset

          self.particles.append(
              DeathParticle(
                  world_px,
                  world_py,
                  target_px,
                  target_py,
                  pixel_color,
                  particle_size,
              )
          )
        except (IndexError, AttributeError):
          continue

  def handle_event(self, event):
    if self.state != "normal":
      return

    if event.type == pygame.KEYDOWN:
      if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
        self.attempt_jump()

    # Gestione del rilascio del tasto per il salto variabile (stile Celeste)
    elif event.type == pygame.KEYUP:
      if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
        if self.velocity_y < 0:
          self.velocity_y *= 0.45

  def attempt_jump(self):
    if self.on_ground or self.coyote_timer > 0:
      self.jump()
    elif self.jumps_left > 0:
      self.jump()
      self.jumps_left -= 1
    else:
      self.jump_buffer_timer = self.jump_buffer_duration

  def jump(self):
    self.velocity_y = JUMP_FORCE
    self.on_ground = False
    self.coyote_timer = 0
    self.jump_buffer_timer = 0

  def get_input(self):
    if self.state != "normal":
      return
    keys = pygame.key.get_pressed()
    self.velocity_x = 0
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
      self.velocity_x = -PLAYER_SPEED
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
      self.velocity_x = PLAYER_SPEED

  def apply_gravity(self):
    if self.state != "normal":
      return
    self.velocity_y += GRAVITY
    if self.velocity_y > 16:
      self.velocity_y = 16

  def update(self):
    if self.state == "normal":
      self.get_input()
      self.apply_gravity()

      if self.jump_buffer_timer > 0:
        self.jump_buffer_timer -= 1

      if self.on_ground:
        self.coyote_timer = self.coyote_duration
        self.jumps_left = 1
        if self.jump_buffer_timer > 0:
          self.jump()
      else:
        if self.coyote_timer > 0:
          self.coyote_timer -= 1

    elif self.state == "animating_death":
      all_arrived = True
      for p in self.particles:
        p.update()
        dist = (p.target_x - p.x) ** 2 + (p.target_y - p.y) ** 2
        if dist > 4:
          all_arrived = False

      if all_arrived:
        self.rect.topleft = (self.spawn_x, self.spawn_y)
        self.velocity_x = 0
        self.velocity_y = 0
        self.jumps_left = 1
        self.coyote_timer = 0
        self.jump_buffer_timer = 0
        self.image.set_alpha(255)
        self.state = "normal"
        self.particles = []

  def draw_particles(self, surface):
    if self.state == "animating_death":
      for p in self.particles:
        pygame.draw.rect(
            surface, p.color, (int(p.x), int(p.y), p.size, p.size)
        )