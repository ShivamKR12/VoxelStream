from ursina import Entity, MeshCollider
from chunk_mesh import generate_chunk_mesh
from utils import CHUNK_SIZE, block_colors

class Chunk(Entity):
    def __init__(self, cx, cz, chunk_data):
        self.cx = cx
        self.cz = cz
        self.chunk_data = chunk_data  # {(x,y,z): block_type}
        mesh = generate_chunk_mesh(chunk_data, block_colors)
        super().__init__(model=mesh, position=(cx * CHUNK_SIZE, 0, cz * CHUNK_SIZE))
        self.collider = MeshCollider(self, mesh)  # <-- Add this line!
        self.active = True

    def update_mesh(self, chunk_data):
        self.chunk_data = chunk_data
        mesh = generate_chunk_mesh(chunk_data, block_colors)
        self.model = mesh
        self.collider = MeshCollider(self, mesh)  # <-- Update collider to match mesh

    def show(self):
        self.visible = True
        self.active = True

    def hide(self):
        self.visible = False
        self.active = False