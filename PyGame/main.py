import sys
import pygame
from level import Level
from player import Player
from settings import FPS, SCREEN_HEIGHT, SCREEN_WIDTH, TITLE


class Game:

  def __init__(self):
    pygame.init()
    self.screen = pygame.display.set_mode(
        (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE | pygame.SCALED
    )
    pygame.display.set_caption(TITLE)
    self.clock = pygame.time.Clock()

    self.level = Level("assets/ScenaTest.tmx")
    self.player = Player(x=32, y=32)

  def run(self):
    while True:
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          pygame.quit()
          sys.exit()

        if event.type == pygame.KEYDOWN:
          if event.key == pygame.K_f:
            pygame.display.toggle_fullscreen()

        self.player.handle_event(event)

      self.screen.fill((135, 206, 235))
      self.level.run(self.player)

      pygame.display.flip()
      self.clock.tick(FPS)


if __name__ == "__main__":
  game = Game()
  game.run()