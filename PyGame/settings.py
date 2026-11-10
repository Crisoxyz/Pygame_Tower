# --- Finestra e Display ---
SCREEN_WIDTH = 240
SCREEN_HEIGHT = 160
FPS = 60
TITLE = "Platformer 2D con Tiled"

# --- Configurazione Player ---
PLAYER_WIDTH = 14
PLAYER_HEIGHT = 20
PLAYER_IMAGE_PATH = (
    "assets/enid.png"  # Percorso dell'immagine PNG del personaggio
)
PLAYER_SPEED = 3
GRAVITY = 0.75
JUMP_FORCE = -8.5

# --- Tempi e Tolleranze (Coyote & Buffer) ---
COYOTE_DURATION = 10  # Frame di tolleranza per il coyote time
JUMP_BUFFER_DURATION = 12  # Frame di memorizzazione del salto

# --- Animazione Particelle di Morte ---
PARTICLE_COUNT = 45
PARTICLE_MIN_SIZE = 3
PARTICLE_MAX_SIZE = 6
PARTICLE_COLOR = (230, 50, 50)