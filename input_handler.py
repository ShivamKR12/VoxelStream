from ursina import application, raycast, camera
from math import floor

def world_to_block_coords(world_point):
    return tuple(int(floor(x + 0.5)) for x in world_point)

def can_place_block(pos, terrain):
    for dx,dy,dz in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]:
        neighbor = (pos[0]+dx, pos[1]+dy, pos[2]+dz)
        if terrain.get_block_type(neighbor) != 0:
            return True
    return False

def handle_input(key, player, terrain, selected_block_type):
    hit_info = raycast(camera.world_position, camera.forward, distance=8, ignore=[player])
    print("Input:", key, "| Raycast hit:", getattr(hit_info, 'hit', False))
    if hit_info and hit_info.hit:
        if key == 'left mouse down':
            mine_pos = hit_info.world_point - hit_info.normal * 0.5
            mine_coords = world_to_block_coords(mine_pos)
            print("Mining at:", mine_coords)
            terrain.mine_block(mine_coords)
        elif key == 'right mouse down':
            place_pos = hit_info.world_point + hit_info.normal * 0.5
            place_coords = world_to_block_coords(place_pos)
            if can_place_block(place_coords, terrain):
                print(f"Placing at: {place_coords}")
                terrain.place_block(place_coords, selected_block_type)
            else:
                print(f"Cannot place block at {place_coords}, no neighbor present.")
    if key == 'escape':
        application.quit()