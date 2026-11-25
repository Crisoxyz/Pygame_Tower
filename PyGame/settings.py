# Finestra e framerate
SCREEN_WIDTH = 240
SCREEN_HEIGHT = 160
FPS = 60
TITLE = "Platformer 2D con Tiled"

# Dimensioni e sprite del personaggio
PLAYER_WIDTH = 12
PLAYER_HEIGHT = 20
FRAME_WIDTH = 16
FRAME_HEIGHT = 20
PLAYER_IMAGE_PATH = "assets/enid.png"
IDLE_SHEET_PATH = "assets/Idle.png"
RUN_SHEET_PATH = "assets/Run.png"
JUMP_SHEET_PATH = "assets/Jump.png"

# Velocità delle animazioni
IDLE_ANIMATION_SPEED = 0.05
RUN_ANIMATION_SPEED = 0.30
JUMP_ANIMATION_SPEED = 0.10

# Fisica e movimento
PLAYER_SPEED = 2
GRAVITY = 0.50
MAX_FALL_SPEED = 16
JUMP_FORCE = -6.5
JUMP_CUT_MULTIPLIER = 0.45
CLAMP_PLAYER_TO_BOUNDS = True

# Piccoli aiuti sul salto (coyote time e jump buffer)
COYOTE_DURATION = 10
JUMP_BUFFER_DURATION = 12

# Camera
CAMERA_HORIZONTAL_OFFSET = 0
CAMERA_VERTICAL_OFFSET = 0
CAMERA_SMOOTHING = 0.10
DEATH_CAMERA_SPEED = 0.15

# Elenco livelli: [mappa, spawn_x, spawn_y, colore_sfondo]
LEVELS = [
    ["assets/ScenaTest.tmx", 50, 124, (20, 10, 70)],
    ["assets/Livello1.tmx", 10, 40, (20, 10, 70)],
    ["assets/Livello2.tmx", 10, 120, (20, 10, 70)],
    ["assets/Livello3.tmx", 120, 350, (20, 10, 70)],
    ["assets/Livello4.tmx", 200, 320, (20, 10, 70)],
]
LOOP_LEVELS = True

# Transizione tra un livello e l'altro
TRANSITION_CLOSE_SPEED = 620.0
TRANSITION_SLAM_ACCEL = 1800.0
TRANSITION_HOLD_DURATION = 0.5
TRANSITION_OPEN_SPEED = 620.0
TRANSITION_BAND_COLOR = (0, 0, 0)

# Nomi dei layer in Tiled
SOLID_LAYER_NAMES = [
    "muri",
    "solidi",
    "walls",
    "terrain",
    "collisioni",
    "tile layer 1",
]
DEATH_LAYER_NAMES = [
    "morte",
    "spike",
    "spikes",
    "trap",
]
TRANSITION_LAYER_NAMES = [
    "transazione",
    "transition",
    "transizioni",
]

# Particelle quando il personaggio muore
PARTICLE_COUNT = 45
PARTICLE_MIN_SIZE = 3
PARTICLE_MAX_SIZE = 6
PARTICLE_COLOR = (230, 50, 50)
DEATH_PARTICLE_STEP = 2
DEATH_PARTICLE_SIZE = 2

# Particelle di polvere per salto e atterraggio
DUST_JUMP_COUNT = 6
DUST_LAND_COUNT = 8
DUST_MIN_SIZE = 2
DUST_MAX_SIZE = 3
DUST_MIN_LIFETIME = 12
DUST_MAX_LIFETIME = 22
DUST_COLORS = [
    (220, 215, 235),
    (185, 178, 210),
    (150, 142, 180),
]
DUST_MIN_FALL_SPEED_FOR_LAND = 1.5
