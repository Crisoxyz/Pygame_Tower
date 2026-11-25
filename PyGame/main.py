import sys
import pygame
from level import Level
from player import Player
from settings import FPS, LEVELS, LOOP_LEVELS, SCREEN_HEIGHT, SCREEN_WIDTH, TITLE
from transition import LevelTransition


class Game:

  def __init__(self):
    pygame.init()
    self.screen = pygame.display.set_mode(
        (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE | pygame.SCALED
    )
    pygame.display.set_caption(TITLE)
    self.clock = pygame.time.Clock()

    self.level_index = 0
    map_path, spawn_x, spawn_y, bg_color = self._get_level_config(
        self.level_index
    )
    self.bg_color = bg_color
    self.level = Level(map_path)
    self.player = Player(x=spawn_x, y=spawn_y)
    self.transition = LevelTransition()

  def _get_level_config(self, index):
    entry = LEVELS[index]
    if isinstance(entry, (list, tuple)):
      map_path = entry[0]
      spawn_x = entry[1] if len(entry) > 1 else 50
      spawn_y = entry[2] if len(entry) > 2 else 124
      bg_color = entry[3] if len(entry) > 3 else (25, 2, 102)
      return map_path, spawn_x, spawn_y, bg_color
    return entry, 50, 124, (25, 2, 102)

  def _reset_player(self, spawn_x, spawn_y):
    self.player.spawn_x = spawn_x
    self.player.spawn_y = spawn_y
    self.player.rect.topleft = (spawn_x, spawn_y)
    self.player.velocity_x = 0
    self.player.velocity_y = 0
    self.player.on_ground = False
    self.player._was_on_ground = False
    self.player._prev_velocity_y = 0.0
    self.player.coyote_timer = 0
    self.player.jump_buffer_timer = 0
    self.player.jumps_left = 1
    self.player.particles = []
    self.player.dust_particles = []
    self.player.image.set_alpha(255)
    self.player.state = "normal"

  def load_level(self, index):
    if index >= len(LEVELS):
      index = 0 if LOOP_LEVELS else len(LEVELS) - 1

    self.level_index = index
    map_path, spawn_x, spawn_y, bg_color = self._get_level_config(
        self.level_index
    )
    self.bg_color = bg_color
    self.level = Level(map_path)
    self._reset_player(spawn_x, spawn_y)

  def run(self):
    while True:
      dt = self.clock.tick(FPS) / 1000.0

      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          pygame.quit()
          sys.exit()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
          pygame.display.toggle_fullscreen()

        if not self.transition.active and not self.player.movement_locked:
          self.player.handle_event(event)

      self.screen.fill(self.bg_color)
      self.level.run(self.player, dt)

      if self.level.transition_triggered and not self.transition.active:
        next_index = self.level_index + 1
        self.player.set_movement_locked(True)
        self.transition.start(lambda: self.load_level(next_index))

      was_active = self.transition.active
      self.transition.update(dt)
      if was_active and not self.transition.active:
        self.player.set_movement_locked(False)

      self.transition.draw(self.screen)
      pygame.display.flip()


if __name__ == "__main__":
  game = Game()
  game.run()
