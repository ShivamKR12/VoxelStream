from ursina import Ursina, Sky, application, window, Text, DirectionalLight, AmbientLight, color, Entity, raycast, camera, Vec3
from player import Player
from terrain import Terrain
from input_handler import handle_input
from utils import block_types
from math import floor

app = Ursina()
application.target_fps = 60
window.vsync = False
window.fullscreen = True

selected_block_index = 0

try:
    player = Player()
except Exception as e:
    print(f"Error initializing Player: {e}")
    player = None

try:
    terrain = Terrain(player)
except Exception as e:
    print(f"Error initializing Terrain: {e}")
    terrain = None

Sky(texture='sky_sunset')

block_type_text = Text(
    f"Block: {block_types[selected_block_index][0]}" if block_types else "Block: N/A",
    position=(-0.7, 0.45), scale=2
)
player_coord_text = Text(
    f"Player: (0,0,0)",
    position=(-0.7, 0.4), scale=2
)

highlighter = Entity(
    model='cube',
    color=color.rgba32(255,255,0,64),
    scale=1.01,
    visible=False
)

def update():
    if terrain:
        try:
            terrain.update()
        except Exception as e:
            print(f"Error updating terrain: {e}")
    if player:
        try:
            player.update()
        except Exception as e:
            print(f"Error updating player: {e}")
    if block_types and 0 <= selected_block_index < len(block_types):
        block_type_text.text = f"Block: {block_types[selected_block_index][0]}"
    pos = getattr(player, 'position', Vec3(0,0,0))
    player_coord_text.text = f"Player: ({int(pos.x)}, {int(pos.y)}, {int(pos.z)})"

    try:
        hit_info = raycast(camera.world_position, camera.forward, distance=8, ignore=[player])
        if hit_info and hit_info.hit:
            block_pos = tuple(int(floor(x)) for x in hit_info.world_point - hit_info.normal * 0.5)
            highlighter.position = Vec3(block_pos) + Vec3(0.5, 0.5, 0.5)  # <-- Fix: center the highlighter
            highlighter.visible = True
        else:
            highlighter.visible = False
    except Exception as e:
        print(f"Error in raycast or highlighter logic: {e}")
        highlighter.visible = False

def input(key):
    global selected_block_index
    if block_types and key.isdigit() and 1 <= int(key) <= len(block_types):
        selected_block_index = int(key) - 1
    try:
        if player and terrain and block_types and 0 <= selected_block_index < len(block_types):
            handle_input(key, player, terrain, block_types[selected_block_index][1])
        else:
            print("Cannot handle input, missing player, terrain, or block_types.")
    except Exception as e:
        print(f"Error handling input: {e}")

sun = DirectionalLight()
sun.look_at((-1,-1,-2))
sun.color = color.white

ambient = AmbientLight()
ambient.color = color.rgb32(80, 80, 80)

try:
    app.run()
except Exception as e:
    print(f"Application encountered an error: {e}")
finally:
    # Add any resource cleanup or saving logic here
    print("Application exiting. Cleanup complete.")