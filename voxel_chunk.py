from ursina import Entity
from voxel import Voxel
from utils import CHUNK_SIZE, block_colors, FACE_DEFS, BLOCK_AIR

class Chunk(Entity):
    def __init__(self, cx, cz, chunk_data, chunk_blocks):
        super().__init__(parent=None, position=(cx*CHUNK_SIZE,0,cz*CHUNK_SIZE))
        self.cx = cx
        self.cz = cz
        self.chunk_data = chunk_data  # {(x,y,z): block_type}
        self.chunk_blocks = chunk_blocks  # {(x,y,z): Voxel}
        self.active = True

    def show(self):
        self.active = True
        for voxel in self.chunk_blocks.values():
            voxel.visible = True

    def hide(self):
        self.active = False
        for voxel in self.chunk_blocks.values():
            voxel.visible = False

    def update_colliders(self, player_pos):
        # Only enable colliders for blocks within 2 units of player
        px, py, pz = player_pos
        for voxel in self.chunk_blocks.values():
            vx, vy, vz = voxel.grid_pos
            if abs(vx - px) < 2 and abs(vy - py) < 2 and abs(vz - pz) < 2:
                voxel.collider = 'box'
            else:
                voxel.collider = None

    def reset(self, cx, cz, chunk_data, chunk_blocks):
        # Move the chunk to new coordinates and update voxels
        self.cx = cx
        self.cz = cz
        self.chunk_data = chunk_data
        # Remove old voxels
        for voxel in self.chunk_blocks.values():
            voxel.disable()  # or destroy(), but for pooling, disable is better
        self.chunk_blocks = chunk_blocks
        # Enable new voxels
        for voxel in self.chunk_blocks.values():
            voxel.enable()
        self.active = True