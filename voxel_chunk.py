from ursina import Entity
from chunk_mesh import generate_chunk_mesh
from utils import block_colors  # <-- Import block_colors

class Chunk(Entity):
    def __init__(self, cx, cz, chunk_data):
        Entity.__init__(self)
        self.cx = cx
        self.cz = cz
        self.chunk_data = chunk_data
        self.mesh = None
        self.collider = None
        self.visible = True  # For chunk unloading
        self.update_mesh(chunk_data)

    def update_mesh(self, chunk_data):
        # Input validation
        if not isinstance(chunk_data, dict):
            print(f"Warning: chunk_data is not a dict for chunk ({self.cx}, {self.cz})")
            chunk_data = {}
        self.chunk_data = chunk_data

        try:
            mesh = generate_chunk_mesh(self.chunk_data, block_colors)
            if mesh is None:
                print(f"Warning: Mesh generation failed for chunk ({self.cx}, {self.cz})")
                self.model = None
                self.collider = None
            else:
                self.model = mesh
                print(f"Chunk ({self.cx},{self.cz}) mesh verts:", len(mesh.vertices))
                self.texture = 'white_cube'
                self.collider = 'mesh' if mesh.vertices else None
        except Exception as e:
            print(f"Error updating mesh for chunk ({self.cx}, {self.cz}): {e}")
            self.model = None
            self.collider = None

    def hide(self):
        # Hide and cleanup chunk for unloading
        self.visible = False
        self.enabled = False
        self.model = None
        self.collider = None
        # Optionally mark for garbage collection
        try:
            del self.mesh
        except Exception:
            pass