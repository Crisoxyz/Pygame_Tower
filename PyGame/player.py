import random
import pygame
from particles import DeathParticle
from settings import (
    COYOTE_DURATION,
    DEATH_PARTICLE_SIZE,
    DEATH_PARTICLE_STEP,
    FRAME_HEIGHT,
    FRAME_WIDTH,
    GRAVITY,
    IDLE_ANIMATION_SPEED,
    IDLE_SHEET_PATH,
    JUMP_ANIMATION_SPEED,
    JUMP_BUFFER_DURATION,
    JUMP_CUT_MULTIPLIER,
    JUMP_FORCE,
    JUMP_SHEET_PATH,
    MAX_FALL_SPEED,
    PARTICLE_COUNT,
    PLAYER_HEIGHT,
    PLAYER_IMAGE_PATH,
    PLAYER_SPEED,
    PLAYER_WIDTH,
    RUN_ANIMATION_SPEED,
    RUN_SHEET_PATH,
)


class Player(pygame.sprite.Sprite):

  def __init__(self, x, y):
    super().__init__()
    self.spawn_x = x
    self.spawn_y = y

    # Caricamento animazioni da sprite sheet 16x20 senza bordi/padding
    self.animations = {
        "idle": self._load_sheet(IDLE_SHEET_PATH, FRAME_WIDTH, FRAME_HEIGHT),
        "run": self._load_sheet(RUN_SHEET_PATH, FRAME_WIDTH, FRAME_HEIGHT),
        "jump": self._load_sheet(JUMP_SHEET_PATH, FRAME_WIDTH, FRAME_HEIGHT),
    }

    # Velocità separate per ciascuna animazione
    self.animation_speeds = {
        "idle": IDLE_ANIMATION_SPEED,
        "run": RUN_ANIMATION_SPEED,
        "jump": JUMP_ANIMATION_SPEED,
    }

    self.current_anim = "idle"
    self.frame_index = 0.0
    self.facing_right = True

    # Immagine iniziale con fallback di sicurezza
    if self.animations["idle"]:
      self.image = self.animations["idle"][0].copy()
    else:
      try:
        original_image = pygame.image.load(
            PLAYER_IMAGE_PATH
        ).convert_alpha()
        self.image = pygame.transform.scale(
            original_image, (FRAME_WIDTH, FRAME_HEIGHT)
        )
      except (pygame.error, FileNotFoundError):
        self.image = pygame.Surface(
            (FRAME_WIDTH, FRAME_HEIGHT), pygame.SRCALPHA
        )
        self.image.fill((230, 50, 50))

    # Hitbox fisica mantenuta a PLAYER_WIDTH x PLAYER_HEIGHT
    self.rect = pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)

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

  def _load_sheet(self, path, frame_w, frame_h):
    """Estrae i frame orizzontali di dimensione frame_w x frame_h da uno sprite sheet."""
    frames = []
    try:
      sheet = pygame.image.load(path).convert_alpha()
      sheet_w, sheet_h = sheet.get_size()
      num_frames = sheet_w // frame_w
      rows = max(1, sheet_h // frame_h)

      for row in range(rows):
        for col in range(num_frames):
          rect = pygame.Rect(col * frame_w, row * frame_h, frame_w, frame_h)
          frame = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
          frame.blit(sheet, (0, 0), rect)
          frames.append(frame)
    except (pygame.error, FileNotFoundError):
      pass
    return frames

  def start_death_animation(self):
    if self.state != "normal":
      return

    self.state = "animating_death"
    self.velocity_x = 0
    self.velocity_y = 0
    self.particles = []

    draw_x, draw_y = self.get_draw_pos()
    img_w, img_h = self.image.get_size()
    self.image.set_alpha(0)  # Nasconde lo sprite principale

    step = DEATH_PARTICLE_STEP
    particle_size = DEATH_PARTICLE_SIZE

    target_base_x = self.spawn_x - (img_w - PLAYER_WIDTH) // 2
    target_base_y = self.spawn_y - (img_h - PLAYER_HEIGHT) // 2

    for py_offset in range(0, img_h, step):
      for px_offset in range(0, img_w, step):
        try:
          pixel_color = self.image.get_at((px_offset, py_offset))
          if len(pixel_color) > 3 and pixel_color[3] == 0:
            continue

          world_px = draw_x + px_offset
          world_py = draw_y + py_offset

          target_px = target_base_x + px_offset
          target_py = target_base_y + py_offset

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

  def get_particles_center_x(self):
    """Restituisce il centro X medio delle particelle durante l'animazione di morte."""
    if not self.particles:
      return self.spawn_x + PLAYER_WIDTH * 0.5
    total_x = sum(p.x + p.size * 0.5 for p in self.particles)
    return total_x / len(self.particles)

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
          self.velocity_y *= JUMP_CUT_MULTIPLIER

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
      self.facing_right = False
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
      self.velocity_x = PLAYER_SPEED
      self.facing_right = True

  def apply_gravity(self):
    if self.state != "normal":
      return
    self.velocity_y += GRAVITY
    if self.velocity_y > MAX_FALL_SPEED:
      self.velocity_y = MAX_FALL_SPEED

  def _select_animation(self):
    if not self.on_ground:
      return "jump"
    if abs(self.velocity_x) > 0:
      return "run"
    return "idle"

  def _update_animation(self):
    next_anim = self._select_animation()
    if next_anim != self.current_anim:
      self.current_anim = next_anim
      self.frame_index = 0.0

    frames = self.animations.get(self.current_anim, [])
    if not frames:
      return

    speed = self.animation_speeds.get(self.current_anim, 0.15)
    self.frame_index += speed
    if self.frame_index >= len(frames):
      self.frame_index = 0.0

    current_frame = frames[int(self.frame_index)]
    if not self.facing_right:
      current_frame = pygame.transform.flip(current_frame, True, False)

    self.image = current_frame.copy()
    if self.state != "normal":
      self.image.set_alpha(0)

  def get_draw_pos(self):
    """Centra lo sprite 16x20 sull'hitbox PLAYER_WIDTH x PLAYER_HEIGHT."""
    draw_x = self.rect.centerx - self.image.get_width() // 2
    draw_y = self.rect.bottom - self.image.get_height()
    return draw_x, draw_y

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

      self._update_animation()

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
        self.current_anim = "idle"
        self.frame_index = 0.0
        self._update_animation()
        self.image.set_alpha(255)
        self.state = "normal"
        self.particles = []

  def draw_particles(self, surface, camera_x=0):
    if self.state == "animating_death":
      for p in self.particles:
        pygame.draw.rect(
            surface,
            p.color,
            (int(p.x - camera_x), int(p.y), p.size, p.size),
        )