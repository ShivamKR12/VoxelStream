from ursina import Entity, Mesh, Vec3, Vec2
from ursina.shaders import lit_with_shadows_shader
from utils import block_colors, FACE_DEFS

class Voxel(Entity):
    def __init__(self, position, block_type):
        super().__init__(
            parent=None,  # Set parent later by chunk
            position=position,
            model=None,
            texture='white_cube',
            shader=lit_with_shadows_shader,  # Use a shader for lighting
            scale=Vec3(1, 1, 1),  # Scale to 1x1x1
            collider=None,  # Enable as needed
            color=block_colors[block_type],
            visible=True
        )
        self.grid_pos = position
        self.block_type = block_type

    def update_mesh(self, exposed_faces):
        # exposed_faces: list of normals (Vec3) that should be rendered
        verts, tris, uvs, normals = [], [], [], []
        idx = 0
        offset = Vec3(0.5,0.5,0.5)
        for normal, corners in FACE_DEFS.values():
            if normal not in exposed_faces:
                continue
            for c in corners:
                verts.append(c - offset)
                uvs.append(Vec2(c.x, c.y))
                normals.append(normal)  # <--- Add this line
            tris += [idx,idx+2,idx+1, idx,idx+3,idx+2]
            idx += 4
        if verts:
            self.model = Mesh(vertices=verts, triangles=tris, uvs=uvs, normals=normals)  # <--- Pass normals!
            self.model.disable_backface_culling = False
        else:
            self.model = None