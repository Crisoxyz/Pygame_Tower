# --- Finestra e Display ---
SCREEN_WIDTH = 240
SCREEN_HEIGHT = 160
FPS = 60
TITLE = "Platformer 2D con Tiled"

# --- Configurazione Player ---
PLAYER_WIDTH = 14
PLAYER_HEIGHT = 20
FRAME_WIDTH = 16
FRAME_HEIGHT = 20
PLAYER_IMAGE_PATH = (
    "assets/enid.png"  # Fallback se mancano gli sprite sheet
)
IDLE_SHEET_PATH = "assets/Idle.png"
RUN_SHEET_PATH = "assets/Run.png"
JUMP_SHEET_PATH = "assets/Jump.png"

# Velocità di animazione separate (incremento indice frame per update())
IDLE_ANIMATION_SPEED = 0.05
RUN_ANIMATION_SPEED = 0.30
JUMP_ANIMATION_SPEED = 0.10

PLAYER_SPEED = 3
GRAVITY = 0.75
MAX_FALL_SPEED = 16
JUMP_FORCE = -8.5
JUMP_CUT_MULTIPLIER = 0.45

# --- Tempi e Tolleranze (Coyote & Buffer) ---
COYOTE_DURATION = 10  # Frame di tolleranza per il coyote time
JUMP_BUFFER_DURATION = 12  # Frame di memorizzazione del salto

# --- Camera Orizzontale ---
CAMERA_HORIZONTAL_OFFSET = 0  # Spostamento orizzontale opzionale (in pixel) rispetto al centro schermo
CAMERA_SMOOTHING = 0.10  # Più basso = più fluido/morbido; 1.0 = aggancio immediato
DEATH_CAMERA_SPEED = 0.15  # Velocità con cui la camera segue le particelle verso lo spawn alla morte

# --- Nomi Layer TMX ---
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

# --- Animazione Particelle di Morte ---
PARTICLE_COUNT = 45
PARTICLE_MIN_SIZE = 3
PARTICLE_MAX_SIZE = 6
PARTICLE_COLOR = (230, 50, 50)
DEATH_PARTICLE_STEP = 2
DEATH_PARTICLE_SIZE = 2