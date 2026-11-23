import pygame
from pytmx.util_pygame import load_pygame
from settings import (
    CAMERA_HORIZONTAL_OFFSET,
    CAMERA_SMOOTHING,
    DEATH_CAMERA_SPEED,
    DEATH_LAYER_NAMES,
    FPS,
    PLAYER_WIDTH,
    SCREEN_WIDTH,
    SOLID_LAYER_NAMES,
)


class Tile(pygame.sprite.Sprite):

  def __init__(self, pos, surface):
    super().__init__()
    self.image = surface
    self.rect = self.image.get_rect(topleft=pos)


class Level:

  def __init__(self, map_path):
    self.display_surface = pygame.display.get_surface()
    self.tmx_data = load_pygame(map_path)

    # Larghezza totale della stanza in pixel (per bloccare la camera ai bordi)
    self.map_width = self.tmx_data.width * self.tmx_data.tilewidth
    self.map_height = self.tmx_data.height * self.tmx_data.tileheight
    self.camera_x = 0.0

    self.visible_sprites = pygame.sprite.Group()
    self.obstacle_sprites = pygame.sprite.Group()
    self.death_sprites = pygame.sprite.Group()

    self.setup_level()

  def setup_level(self):
    solid_names = [name.lower() for name in SOLID_LAYER_NAMES]
    death_names = [name.lower() for name in DEATH_LAYER_NAMES]

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
          is_solid_layer = layer.name.lower() in solid_names

          if is_solid_prop or is_solid_layer:
            self.obstacle_sprites.add(tile)

          is_death_prop = props is not None and (
              props.get("Death") or props.get("death")
          )
          is_death_layer = layer.name.lower() in death_names

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

  def update_camera(self, player, dt=1.0 / FPS):
    max_camera_x = max(0, self.map_width - SCREEN_WIDTH)

    if player.state == "animating_death":
      # Durante la morte la camera segue le particelle che rientrano verso lo spawn
      if hasattr(player, "get_particles_center_x") and player.particles:
        focus_x = player.get_particles_center_x()
      else:
        focus_x = player.spawn_x + (PLAYER_WIDTH * 0.5)

      target_x = focus_x - (SCREEN_WIDTH // 2) + CAMERA_HORIZONTAL_OFFSET
      target_x = max(0, min(target_x, max_camera_x))
      follow_speed = max(0.0, min(1.0, DEATH_CAMERA_SPEED))
    else:
      focus_x = player.rect.centerx
      target_x = focus_x - (SCREEN_WIDTH // 2) + CAMERA_HORIZONTAL_OFFSET
      target_x = max(0, min(target_x, max_camera_x))
      raw_smoothing = max(0.0, min(0.999, CAMERA_SMOOTHING))
      # Interpolazione fluida indipendente dal delta time di riferimento
      frame_scale = max(0.0, dt * FPS)
      follow_speed = 1.0 - ((1.0 - raw_smoothing) ** frame_scale)

    self.camera_x += (target_x - self.camera_x) * follow_speed
    self.camera_x = max(0.0, min(self.camera_x, float(max_camera_x)))

  def run(self, player, dt=1.0 / FPS):
    player.update()

    if player.state == "normal":
      self.horizontal_movement_collision(player)
      self.vertical_movement_collision(player)

    self.check_death_collision(player)
    self.update_camera(player, dt)

    cam_x_int = int(round(self.camera_x))

    for sprite in self.visible_sprites.sprites():
      draw_x = sprite.rect.x - cam_x_int
      # Disegna solo i tile visibili orizzontalmente nella finestra
      if draw_x + sprite.rect.width >= 0 and draw_x <= SCREEN_WIDTH:
        self.display_surface.blit(sprite.image, (draw_x, sprite.rect.y))

    draw_x, draw_y = (
        player.get_draw_pos()
        if hasattr(player, "get_draw_pos")
        else player.rect.topleft
    )
    self.display_surface.blit(player.image, (draw_x - cam_x_int, draw_y))
    player.draw_particles(self.display_surface, cam_x_int)