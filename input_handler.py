from ursina import application, raycast, camera
from math import floor

def world_to_block_coords(world_point):
    # Validate input
    if not hasattr(world_point, '__iter__') or len(world_point) < 3:
        raise ValueError(f"Invalid world_point: {world_point}")
    return tuple(int(floor(x + 0.5)) for x in world_point)

def can_place_block(pos, terrain):
    # Validate input
    if not hasattr(pos, '__iter__') or len(pos) < 3:
        print(f"Warning: Invalid block position: {pos}")
        return False
    try:
        for dx, dy, dz in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]:
            neighbor = (pos[0]+dx, pos[1]+dy, pos[2]+dz)
            try:
                neighbor_type = terrain.get_block_type(neighbor)
            except Exception as e:
                print(f"Error checking neighbor block: {e}")
                continue
            if neighbor_type != 0:
                return True
        return False
    except Exception as e:
        print(f"Error in can_place_block: {e}")
        return False

def handle_input(key, player, terrain, selected_block_type):
    try:
        hit_info = raycast(camera.world_position, camera.forward, distance=8, ignore=[player])
    except Exception as e:
        print(f"Raycast error: {e}")
        hit_info = None

    print("Input:", key, "| Raycast hit:", getattr(hit_info, 'hit', False))
    # Early out for missing or invalid hit_info attributes
    if hit_info and getattr(hit_info, 'hit', False):
        print("Raycast world_point:", hit_info.world_point)
        try:
            if key == 'left mouse down':
                mine_pos = hit_info.world_point - hit_info.normal * 0.5
                mine_coords = world_to_block_coords(mine_pos)
                print(f"Mining at (world): {mine_pos}, (snapped): {mine_coords}")
                try:
                    terrain.mine_block(mine_coords)
                except Exception as e:
                    print(f"Error mining block at {mine_coords}: {e}")

            elif key == 'right mouse down':
                place_pos = hit_info.world_point + hit_info.normal * 0.5
                place_coords = world_to_block_coords(place_pos)
                if can_place_block(place_coords, terrain):
                    print(f"Placing at (world): {place_pos}, (snapped): {place_coords}")
                    try:
                        terrain.place_block(place_coords, selected_block_type)
                    except Exception as e:
                        print(f"Error placing block at {place_coords}: {e}")
                else:
                    print(f"Cannot place block at {place_coords} (snapped from {place_pos}), no neighbor present.")
        except Exception as e:
            print(f"Error handling block input: {e}")
    if key == 'escape':
        # Add cleanup or save logic here if needed
        print("Quitting application.")
        application.quit()