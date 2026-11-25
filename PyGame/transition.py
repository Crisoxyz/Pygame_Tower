import pygame
from settings import (
    FPS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TRANSITION_BAND_COLOR,
    TRANSITION_CLOSE_SPEED,
    TRANSITION_HOLD_DURATION,
    TRANSITION_OPEN_SPEED,
    TRANSITION_SLAM_ACCEL,
)


class LevelTransition:

  def __init__(self):
    self.active = False
    self.phase = "idle"
    self.band_height = 0.0
    self.max_band_height = SCREEN_HEIGHT * 0.5
    self.current_speed = 0.0
    self.hold_timer = 0.0
    self.on_midpoint = None

  def start(self, on_midpoint_callback):
    if self.active:
      return
    self.active = True
    self.phase = "closing"
    self.band_height = 0.0
    self.max_band_height = SCREEN_HEIGHT * 0.5
    self.current_speed = TRANSITION_CLOSE_SPEED
    self.hold_timer = 0.0
    self.on_midpoint = on_midpoint_callback

  def update(self, dt=1.0 / FPS):
    if not self.active:
      return

    if self.phase == "closing":
      self.current_speed += TRANSITION_SLAM_ACCEL * dt
      self.band_height += self.current_speed * dt

      if self.band_height >= self.max_band_height:
        self.band_height = self.max_band_height
        self.current_speed = 0.0
        if self.on_midpoint is not None:
          self.on_midpoint()
          self.on_midpoint = None
        self.phase = "holding"
        self.hold_timer = TRANSITION_HOLD_DURATION

    elif self.phase == "holding":
      self.hold_timer -= dt
      if self.hold_timer <= 0.0:
        self.hold_timer = 0.0
        self.phase = "opening"
        self.current_speed = TRANSITION_OPEN_SPEED

    elif self.phase == "opening":
      self.band_height -= TRANSITION_OPEN_SPEED * dt
      if self.band_height <= 0.0:
        self.band_height = 0.0
        self.phase = "idle"
        self.active = False

  def draw(self, surface):
    if not self.active and self.band_height <= 0.0:
      return

    h = int(round(self.band_height))
    if h <= 0:
      return

    top_rect = pygame.Rect(0, 0, SCREEN_WIDTH, h)
    bottom_rect = pygame.Rect(0, SCREEN_HEIGHT - h, SCREEN_WIDTH, h)

    pygame.draw.rect(surface, TRANSITION_BAND_COLOR, top_rect)
    pygame.draw.rect(surface, TRANSITION_BAND_COLOR, bottom_rect)
