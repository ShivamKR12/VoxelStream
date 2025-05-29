from utils import BLOCK_GRASS, BLOCK_DIRT, BLOCK_STONE
from ursina import application, raycast, mouse, camera

def handle_input(key, player, terrain, selected_block_type):
    # Key toggles
    if key == 'f':
        terrain.frustum_culling_enabled = not terrain.frustum_culling_enabled
        print(f"Frustum culling: {terrain.frustum_culling_enabled}")
    elif key == 'd':
        terrain.distance_culling_enabled = not terrain.distance_culling_enabled
        print(f"Distance culling: {terrain.distance_culling_enabled}")
    elif key == 'l':
        terrain.dynamic_loading_enabled = not terrain.dynamic_loading_enabled
        print(f"Dynamic loading: {terrain.dynamic_loading_enabled}")

    # Mouse interaction (mining/placing) with raycast
    if key == 'left mouse down':
        # Mining: Remove the block you are looking at
        hit_info = raycast(camera.world_position, camera.forward, distance=5)
        if hit_info.hit and hasattr(hit_info.entity, "position"):
            block_pos = tuple(int(round(x)) for x in hit_info.entity.position)
            terrain.mine_block(block_pos)
    elif key == 'right mouse down':
        # Placing: Add a block to the face you are looking at
        hit_info = raycast(camera.world_position, camera.forward, distance=5)
        if hit_info.hit and hasattr(hit_info.entity, "position") and hasattr(hit_info, "normal"):
            # place_pos = hit_info.entity.position + hit_info.normal
            # block_pos = tuple(map(int, place_pos))
            block_pos = tuple(int(round(x)) for x in hit_info.entity.position + hit_info.normal)
            print("Placing block at", block_pos)
            terrain.place_block(block_pos, selected_block_type)

    if key == 'escape':
        application.quit()