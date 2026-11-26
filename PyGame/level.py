import pygame
from pytmx.util_pygame import load_pygame
from settings import (
    CAMERA_HORIZONTAL_OFFSET,
    CAMERA_SMOOTHING,
    CAMERA_VERTICAL_OFFSET,
    CLAMP_PLAYER_TO_BOUNDS,
    DEATH_CAMERA_SPEED,
    DEATH_LAYER_NAMES,
    FPS,
    PLAYER_HEIGHT,
    PLAYER_WIDTH,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SOLID_LAYER_NAMES,
    TRANSITION_LAYER_NAMES,
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

    self.map_width = self.tmx_data.width * self.tmx_data.tilewidth
    self.map_height = self.tmx_data.height * self.tmx_data.tileheight
    self.camera_x = 0.0
    self.camera_y = 0.0

    self.visible_sprites = pygame.sprite.Group()
    self.obstacle_sprites = pygame.sprite.Group()
    self.death_sprites = pygame.sprite.Group()
    self.transition_sprites = pygame.sprite.Group()
    self.transition_triggered = False

    self.setup_level()

  def _has_property(self, props, names):
    if props is None:
      return False
    return any(props.get(name) for name in names)

  def setup_level(self):
    solid_names = {name.lower() for name in SOLID_LAYER_NAMES}
    death_names = {name.lower() for name in DEATH_LAYER_NAMES}
    transition_names = {name.lower() for name in TRANSITION_LAYER_NAMES}

    for layer_idx, layer in enumerate(self.tmx_data.visible_layers):
      if not hasattr(layer, "data"):
        continue

      layer_name = layer.name.lower()
      for x, y, surf in layer.tiles():
        pos = (x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight)
        tile = Tile(pos, surf)
        self.visible_sprites.add(tile)

        gid = self.tmx_data.get_tile_gid(x, y, layer_idx)
        props = self.tmx_data.get_tile_properties_by_gid(gid)

        if self._has_property(props, ("solid", "Solid")) or layer_name in solid_names:
          self.obstacle_sprites.add(tile)

        if self._has_property(props, ("Death", "death")) or layer_name in death_names:
          self.death_sprites.add(tile)

        if (
            self._has_property(
                props, ("transazione", "Transazione", "transition", "Transition")
            )
            or layer_name in transition_names
        ):
          self.transition_sprites.add(tile)

  def clamp_player_to_bounds(self, player):
    if not CLAMP_PLAYER_TO_BOUNDS:
      return

    if player.rect.left < 0:
      player.rect.left = 0
      player.velocity_x = max(0, player.velocity_x)

    if player.rect.right > self.map_width:
      player.rect.right = self.map_width
      player.velocity_x = min(0, player.velocity_x)

    if player.rect.top < 0:
      player.rect.top = 0
      player.velocity_y = max(0, player.velocity_y)

    if player.rect.bottom > self.map_height:
      player.rect.bottom = self.map_height
      player.velocity_y = min(0, player.velocity_y)
      player.on_ground = True

  def horizontal_movement_collision(self, player):
    player.rect.x += player.velocity_x
    for sprite in self.obstacle_sprites:
      if sprite.rect.colliderect(player.rect):
        if player.velocity_x > 0:
          player.rect.right = sprite.rect.left
        elif player.velocity_x < 0:
          player.rect.left = sprite.rect.right

  def vertical_movement_collision(self, player):
    player.rect.y += player.velocity_y
    player.on_ground = False

    for sprite in self.obstacle_sprites:
      if sprite.rect.colliderect(player.rect):
        if player.velocity_y > 0:
          player.rect.bottom = sprite.rect.top
          player.velocity_y = 0
          player.on_ground = True
        elif player.velocity_y < 0:
          player.rect.top = sprite.rect.bottom
          player.velocity_y = 0

    if not player.on_ground and hasattr(player, "has_solid_floor_below"):
      if player.has_solid_floor_below(self.obstacle_sprites):
        player.on_ground = True
        if player.velocity_y > 0:
          player.velocity_y = 0

  def check_death_collision(self, player):
    if player.state == "normal":
      for sprite in self.death_sprites:
        if sprite.rect.colliderect(player.rect):
          player.start_death_animation()
          break

  def check_transition_collision(self, player):
    if player.state == "normal" and not self.transition_triggered:
      for sprite in self.transition_sprites:
        if sprite.rect.colliderect(player.rect):
          self.transition_triggered = True
          break

  def _clamp_camera_target(self, focus_x, focus_y, max_camera_x, max_camera_y):
    target_x = focus_x - (SCREEN_WIDTH // 2) + CAMERA_HORIZONTAL_OFFSET
    target_y = focus_y - (SCREEN_HEIGHT // 2) + CAMERA_VERTICAL_OFFSET
    return (
        max(0, min(target_x, max_camera_x)),
        max(0, min(target_y, max_camera_y)),
    )

  def update_camera(self, player, dt=1.0 / FPS):
    max_camera_x = max(0, self.map_width - SCREEN_WIDTH)
    max_camera_y = max(0, self.map_height - SCREEN_HEIGHT)

    if player.state == "animating_death":
      if hasattr(player, "get_particles_center_x") and player.particles:
        focus_x = player.get_particles_center_x()
      else:
        focus_x = player.spawn_x + PLAYER_WIDTH * 0.5

      if hasattr(player, "get_particles_center_y") and player.particles:
        focus_y = player.get_particles_center_y()
      else:
        focus_y = player.spawn_y + PLAYER_HEIGHT * 0.5

      target_x, target_y = self._clamp_camera_target(
          focus_x, focus_y, max_camera_x, max_camera_y
      )
      follow_speed = max(0.0, min(1.0, DEATH_CAMERA_SPEED))
    else:
      target_x, target_y = self._clamp_camera_target(
          player.rect.centerx, player.rect.centery, max_camera_x, max_camera_y
      )
      raw_smoothing = max(0.0, min(0.999, CAMERA_SMOOTHING))
      frame_scale = max(0.0, dt * FPS)
      follow_speed = 1.0 - ((1.0 - raw_smoothing) ** frame_scale)

    self.camera_x += (target_x - self.camera_x) * follow_speed
    self.camera_x = max(0.0, min(self.camera_x, float(max_camera_x)))

    self.camera_y += (target_y - self.camera_y) * follow_speed
    self.camera_y = max(0.0, min(self.camera_y, float(max_camera_y)))

  def run(self, player, dt=1.0 / FPS):
    player.update()

    if player.state == "normal":
      self.horizontal_movement_collision(player)
      self.vertical_movement_collision(player)
      self.clamp_player_to_bounds(player)

    self.check_death_collision(player)
    self.check_transition_collision(player)
    self.update_camera(player, dt)

    cam_x_int = int(round(self.camera_x))
    cam_y_int = int(round(self.camera_y))

    for sprite in self.visible_sprites:
      draw_x = sprite.rect.x - cam_x_int
      draw_y = sprite.rect.y - cam_y_int
      if (
          draw_x + sprite.rect.width >= 0
          and draw_x <= SCREEN_WIDTH
          and draw_y + sprite.rect.height >= 0
          and draw_y <= SCREEN_HEIGHT
      ):
        self.display_surface.blit(sprite.image, (draw_x, draw_y))

    if hasattr(player, "draw_dust_particles"):
      player.draw_dust_particles(self.display_surface, cam_x_int, cam_y_int)

    draw_x, draw_y = (
        player.get_draw_pos()
        if hasattr(player, "get_draw_pos")
        else player.rect.topleft
    )
    self.display_surface.blit(
        player.image, (draw_x - cam_x_int, draw_y - cam_y_int)
    )
    player.draw_particles(self.display_surface, cam_x_int, cam_y_int)
