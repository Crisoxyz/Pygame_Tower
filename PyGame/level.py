import pygame
from pytmx.util_pygame import load_pygame


class Tile(pygame.sprite.Sprite):

  def __init__(self, pos, surface):
    super().__init__()
    self.image = surface
    self.rect = self.image.get_rect(topleft=pos)


class Level:

  def __init__(self, map_path):
    self.display_surface = pygame.display.get_surface()
    self.tmx_data = load_pygame(map_path)

    self.visible_sprites = pygame.sprite.Group()
    self.obstacle_sprites = pygame.sprite.Group()
    self.death_sprites = pygame.sprite.Group()

    self.setup_level()

  def setup_level(self):
    for layer_idx, layer in enumerate(self.tmx_data.visible_layers):
      if hasattr(layer, "data"):
        for x, y, surf in layer.tiles():
          pos = (x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight)
          tile = Tile(pos, surf)
          self.visible_sprites.add(tile)

          gid = self.tmx_data.get_tile_gid(x, y, layer_idx)
          props = self.tmx_data.get_tile_properties_by_gid(gid)

          is_solid_prop = props is not None and (
              props.get("solid") or props.get("Solid")
          )
          is_solid_layer = layer.name.lower() in [
              "muri",
              "solidi",
              "walls",
              "terrain",
              "collisioni",
              "tile layer 1",
          ]

          if is_solid_prop or is_solid_layer:
            self.obstacle_sprites.add(tile)

          is_death_prop = props is not None and (
              props.get("Death") or props.get("death")
          )
          is_death_layer = layer.name.lower() in [
              "morte",
              "spike",
              "spikes",
              "trap",
          ]

          if is_death_prop or is_death_layer:
            self.death_sprites.add(tile)

  def horizontal_movement_collision(self, player):
    player.rect.x += player.velocity_x
    for sprite in self.obstacle_sprites.sprites():
      if sprite.rect.colliderect(player.rect):
        if player.velocity_x > 0:
          player.rect.right = sprite.rect.left
        elif player.velocity_x < 0:
          player.rect.left = sprite.rect.right

  def vertical_movement_collision(self, player):
    player.rect.y += player.velocity_y
    player.on_ground = False

    for sprite in self.obstacle_sprites.sprites():
      if sprite.rect.colliderect(player.rect):
        if player.velocity_y > 0:
          player.rect.bottom = sprite.rect.top
          player.velocity_y = 0
          player.on_ground = True
        elif player.velocity_y < 0:
          player.rect.top = sprite.rect.bottom
          player.velocity_y = 0

  def check_death_collision(self, player):
    if player.state == "normal":
      for sprite in self.death_sprites.sprites():
        if sprite.rect.colliderect(player.rect):
          player.start_death_animation()
          break

  def run(self, player):
    player.update()

    if player.state == "normal":
      self.horizontal_movement_collision(player)
      self.vertical_movement_collision(player)

    self.check_death_collision(player)

    self.visible_sprites.draw(self.display_surface)
    self.display_surface.blit(player.image, player.rect)
    player.draw_particles(self.display_surface)