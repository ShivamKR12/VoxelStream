from ursina import Ursina, Sky, application, window, Text, DirectionalLight, AmbientLight, color, Entity, raycast, camera
from player import Player
from terrain import Terrain
from input_handler import handle_input
from utils import block_types

app = Ursina()
application.target_fps = 60
window.vsync = False
window.fullscreen = True

selected_block_index = 0

player = Player()
terrain = Terrain(player)

Sky(texture='sky_sunset')

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
    color=color.rgba32(255,255,0,64),
    scale=1.01,
    visible=False
)

def update():
    terrain.update()
    player.update()
    block_type_text.text = f"Block: {block_types[selected_block_index][0]}"
    pos = player.position
    player_coord_text.text = f"Player: ({int(pos.x)}, {int(pos.y)}, {int(pos.z)})"

    hit_info = raycast(camera.world_position, camera.forward, distance=8, ignore=[player])
    if hit_info.hit:
        block_pos = tuple(int(round(x)) for x in hit_info.world_point - hit_info.normal / 2)
        highlighter.position = block_pos
        highlighter.visible = True
    else:
        highlighter.visible = False

def input(key):
    global selected_block_index
    if key.isdigit() and 1 <= int(key) <= len(block_types):
        selected_block_index = int(key) - 1
    handle_input(key, player, terrain, block_types[selected_block_index][1])

sun = DirectionalLight()
sun.look_at((-1,-1,-2))
sun.color = color.white

ambient = AmbientLight()
ambient.color = color.rgb32(80, 80, 80)

app.run()