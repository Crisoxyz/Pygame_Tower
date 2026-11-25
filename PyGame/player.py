import random
import pygame
from particles import DeathParticle, DustParticle
from settings import (
    COYOTE_DURATION,
    DEATH_PARTICLE_SIZE,
    DEATH_PARTICLE_STEP,
    DUST_COLORS,
    DUST_JUMP_COUNT,
    DUST_LAND_COUNT,
    DUST_MAX_LIFETIME,
    DUST_MAX_SIZE,
    DUST_MIN_FALL_SPEED_FOR_LAND,
    DUST_MIN_LIFETIME,
    DUST_MIN_SIZE,
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

    self.animations = {
        "idle": self._load_sheet(IDLE_SHEET_PATH, FRAME_WIDTH, FRAME_HEIGHT),
        "run": self._load_sheet(RUN_SHEET_PATH, FRAME_WIDTH, FRAME_HEIGHT),
        "jump": self._load_sheet(JUMP_SHEET_PATH, FRAME_WIDTH, FRAME_HEIGHT),
    }

    self.animation_speeds = {
        "idle": IDLE_ANIMATION_SPEED,
        "run": RUN_ANIMATION_SPEED,
        "jump": JUMP_ANIMATION_SPEED,
    }

    self.current_anim = "idle"
    self.frame_index = 0.0
    self.facing_right = True
    self.image = self._create_initial_image()

    self.rect = pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)
    self.velocity_x = 0
    self.velocity_y = 0
    self.on_ground = False
    self._was_on_ground = False
    self._prev_velocity_y = 0.0
    self.movement_locked = False

    self.coyote_timer = 0
    self.coyote_duration = COYOTE_DURATION
    self.jump_buffer_timer = 0
    self.jump_buffer_duration = JUMP_BUFFER_DURATION
    self.jumps_left = 1

    self.state = "normal"
    self.particles = []
    self.dust_particles = []

  def _create_initial_image(self):
    if self.animations["idle"]:
      return self.animations["idle"][0].copy()

    try:
      original_image = pygame.image.load(PLAYER_IMAGE_PATH).convert_alpha()
      return pygame.transform.scale(original_image, (FRAME_WIDTH, FRAME_HEIGHT))
    except (pygame.error, FileNotFoundError):
      fallback = pygame.Surface((FRAME_WIDTH, FRAME_HEIGHT), pygame.SRCALPHA)
      fallback.fill((230, 50, 50))
      return fallback

  def set_movement_locked(self, locked):
    self.movement_locked = locked
    if locked:
      self.velocity_x = 0
      self.velocity_y = 0
      self.jump_buffer_timer = 0

  def _load_sheet(self, path, frame_w, frame_h):
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

  def spawn_dust(self, mode="jump", impact_speed=0.0):
    if mode == "land":
      intensity = min(2.0, max(1.0, impact_speed / 8.0))
      count = max(1, int(round(DUST_LAND_COUNT * intensity)))
    else:
      count = DUST_JUMP_COUNT

    foot_y = self.rect.bottom - 1
    for _ in range(count):
      size = random.randint(DUST_MIN_SIZE, DUST_MAX_SIZE)
      px = random.uniform(self.rect.left - 1, self.rect.right - size + 1)
      py = random.uniform(foot_y - size, foot_y)

      if mode == "jump":
        vx = random.uniform(-1.1, 1.1) - (self.velocity_x * 0.25)
        vy = random.uniform(-1.4, -0.35)
      else:
        side = -1.0 if px < self.rect.centerx else 1.0
        vx = side * random.uniform(0.3, 1.5) + random.uniform(-0.35, 0.35)
        vy = random.uniform(-1.1, -0.2)

      self.dust_particles.append(
          DustParticle(
              x=px,
              y=py,
              vx=vx,
              vy=vy,
              color=random.choice(DUST_COLORS),
              size=size,
              lifetime=random.randint(DUST_MIN_LIFETIME, DUST_MAX_LIFETIME),
              gravity=0.03 if mode == "jump" else 0.05,
              drag=0.91,
          )
      )

  def _update_dust_particles(self):
    if not self.dust_particles:
      return
    for particle in self.dust_particles:
      particle.update()
    self.dust_particles = [p for p in self.dust_particles if p.alive]

  def start_death_animation(self):
    if self.state != "normal":
      return

    self.state = "animating_death"
    self.velocity_x = 0
    self.velocity_y = 0
    self.particles = []

    draw_x, draw_y = self.get_draw_pos()
    img_w, img_h = self.image.get_size()
    self.image.set_alpha(0)

    target_base_x = self.spawn_x - (img_w - PLAYER_WIDTH) // 2
    target_base_y = self.spawn_y - (img_h - PLAYER_HEIGHT) // 2

    for py_offset in range(0, img_h, DEATH_PARTICLE_STEP):
      for px_offset in range(0, img_w, DEATH_PARTICLE_STEP):
        try:
          pixel_color = self.image.get_at((px_offset, py_offset))
          if len(pixel_color) > 3 and pixel_color[3] == 0:
            continue

          self.particles.append(
              DeathParticle(
                  draw_x + px_offset,
                  draw_y + py_offset,
                  target_base_x + px_offset,
                  target_base_y + py_offset,
                  pixel_color,
                  DEATH_PARTICLE_SIZE,
              )
          )
        except (IndexError, AttributeError):
          continue

  def get_particles_center_x(self):
    if not self.particles:
      return self.spawn_x + PLAYER_WIDTH * 0.5
    return sum(p.x + p.size * 0.5 for p in self.particles) / len(self.particles)

  def get_particles_center_y(self):
    if not self.particles:
      return self.spawn_y + PLAYER_HEIGHT * 0.5
    return sum(p.y + p.size * 0.5 for p in self.particles) / len(self.particles)

  def handle_event(self, event):
    if self.state != "normal" or self.movement_locked:
      return

    jump_keys = (pygame.K_SPACE, pygame.K_UP, pygame.K_w)
    if event.type == pygame.KEYDOWN and event.key in jump_keys:
      self.attempt_jump()
    elif event.type == pygame.KEYUP and event.key in jump_keys:
      if self.velocity_y < 0:
        self.velocity_y *= JUMP_CUT_MULTIPLIER

  def attempt_jump(self):
    if self.movement_locked:
      return
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
    self._was_on_ground = False
    self.coyote_timer = 0
    self.jump_buffer_timer = 0
    self.spawn_dust(mode="jump")

  def get_input(self):
    if self.state != "normal" or self.movement_locked:
      self.velocity_x = 0
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
    if self.state != "normal" or self.movement_locked:
      return
    self.velocity_y = min(MAX_FALL_SPEED, self.velocity_y + GRAVITY)

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
    self.frame_index = (self.frame_index + speed) % len(frames)

    current_frame = frames[int(self.frame_index)]
    if not self.facing_right:
      current_frame = pygame.transform.flip(current_frame, True, False)

    self.image = current_frame.copy()
    if self.state != "normal":
      self.image.set_alpha(0)

  def get_draw_pos(self):
    draw_x = self.rect.centerx - self.image.get_width() // 2
    draw_y = self.rect.bottom - self.image.get_height()
    return draw_x, draw_y

  def _respawn_after_death(self):
    self.rect.topleft = (self.spawn_x, self.spawn_y)
    self.velocity_x = 0
    self.velocity_y = 0
    self.jumps_left = 1
    self.coyote_timer = 0
    self.jump_buffer_timer = 0
    self.on_ground = False
    self._was_on_ground = False
    self._prev_velocity_y = 0.0
    self.current_anim = "idle"
    self.frame_index = 0.0
    self._update_animation()
    self.image.set_alpha(255)
    self.state = "normal"
    self.particles = []

  def update(self):
    self._update_dust_particles()

    if self.state == "normal":
      if self.movement_locked:
        self.velocity_x = 0
        self.velocity_y = 0
        self._was_on_ground = self.on_ground
        self._prev_velocity_y = self.velocity_y
        self._update_animation()
        return

      if self.on_ground and not self._was_on_ground:
        if self._prev_velocity_y >= DUST_MIN_FALL_SPEED_FOR_LAND:
          self.spawn_dust(mode="land", impact_speed=self._prev_velocity_y)

      self._was_on_ground = self.on_ground
      self._prev_velocity_y = self.velocity_y

      self.get_input()
      self.apply_gravity()

      if self.jump_buffer_timer > 0:
        self.jump_buffer_timer -= 1

      if self.on_ground:
        self.coyote_timer = self.coyote_duration
        self.jumps_left = 1
        if self.jump_buffer_timer > 0:
          self.jump()
      elif self.coyote_timer > 0:
        self.coyote_timer -= 1

      self._update_animation()

    elif self.state == "animating_death":
      all_arrived = True
      for particle in self.particles:
        particle.update()
        dist_sq = (particle.target_x - particle.x) ** 2 + (
            particle.target_y - particle.y
        ) ** 2
        if dist_sq > 4:
          all_arrived = False

      if all_arrived:
        self._respawn_after_death()

  def draw_dust_particles(self, surface, camera_x=0, camera_y=0):
    for particle in self.dust_particles:
      particle.draw(surface, camera_x, camera_y)

  def draw_particles(self, surface, camera_x=0, camera_y=0):
    if self.state == "animating_death":
      for particle in self.particles:
        pygame.draw.rect(
            surface,
            particle.color,
            (
                int(particle.x - camera_x),
                int(particle.y - camera_y),
                particle.size,
                particle.size,
            ),
        )
