from ursina import application, raycast, mouse, camera

def handle_input(key, player, terrain, selected_block_type):
    if key == 'left mouse down':
        hit_info = raycast(camera.world_position, camera.forward, distance=5)
        if hit_info.hit:
            block_pos = tuple(int(round(x)) for x in hit_info.world_point - hit_info.normal / 2)
            terrain.mine_block(block_pos)
    elif key == 'right mouse down':
        hit_info = raycast(camera.world_position, camera.forward, distance=5)
        if hit_info.hit:
            block_pos = tuple(int(round(x)) for x in hit_info.world_point + hit_info.normal / 2)
            terrain.place_block(block_pos, selected_block_type)
    if key == 'escape':
        application.quit()