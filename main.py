from ursina import Ursina, Sky, application, window, Text, DirectionalLight, AmbientLight, color, Entity, raycast, camera
from player import Player
from terrain import Terrain
from input_handler import handle_input
from utils import block_types  # Import your block_types list here

app = Ursina()

application.target_fps = 60
window.vsync = False
window.fullscreen = True

selected_block_index = 0  # <--- DEFINE THIS BEFORE USING IT

player = Player()
terrain = Terrain(player)

Sky(texture='sky_sunset')

# --- UI Texts ---
block_type_text = Text(
    f"Block: {block_types[selected_block_index][0]}",
    position=(-0.7, 0.45), scale=2
)
player_coord_text = Text(
    f"Player: (0,0,0)",
    position=(-0.7, 0.4), scale=2
)

highlighter = Entity(
    model='cube',
    color=color.rgba32(255,255,0,64),  # Yellow, mostly transparent
    scale=1.01,  # Slightly bigger than a normal block, so it surrounds
    visible=False
)

def update():
    terrain.update()
    player.update()
    # Update block type text and player position
    block_type_text.text = f"Block: {block_types[selected_block_index][0]}"
    pos = player.position
    player_coord_text.text = f"Player: ({int(pos.x)}, {int(pos.y)}, {int(pos.z)})"

    # --- Raycast to find hovered block ---
    hit_info = raycast(camera.world_position, camera.forward, distance=8, ignore=[player, ])
    hovered_block = (hit_info.entity if hit_info.hit 
                     and hasattr(hit_info.entity, 'block_type') 
                     and hit_info.entity.block_type != 'air'  # <-- Only highlight if not air
    else None)

    # In your update loop, set highlighter.position to the hovered block, and set visible as needed
    if hovered_block:
        highlighter.position = hovered_block.position
        highlighter.visible = True
    else:
        highlighter.visible = False

def input(key):
    global selected_block_index
    # Block type selection (for example, 1, 2, 3 keys)
    if key in ('1', '2', '3'):
        selected_block_index = int(key) - 1
    handle_input(key, player, terrain, block_types[selected_block_index][1])  # Pass selected type to handler

# Add this after creating the Ursina app:
sun = DirectionalLight()
sun.look_at((-1,-1,-2))  # Change direction for effect
sun.color = color.white   # You can tint this for mood

ambient = AmbientLight()
ambient.color = color.rgb32(80, 80, 80)  # Soft gray ambient light

app.run()