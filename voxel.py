from ursina import Entity, Vec3, Mesh

class Voxel(Entity):
    def __init__(self, position=(0,0,0), block_type=0, block_colors=None, exposed_faces=None, **kwargs):
        # Validate input types
        if not isinstance(position, (tuple, list, Vec3)):
            print(f"Warning: Invalid position for Voxel: {position}, defaulting to (0,0,0)")
            position = (0, 0, 0)
        if block_colors is None or not isinstance(block_colors, dict):
            print("Warning: block_colors not provided or invalid, defaulting to empty dict")
            block_colors = {}
        if exposed_faces is not None and not isinstance(exposed_faces, (list, tuple)):
            print(f"Warning: Invalid exposed_faces: {exposed_faces}, defaulting to []")
            exposed_faces = []

        # Safely get color
        color = block_colors.get(block_type, None)
        if color is None:
            print(f"Warning: block_type {block_type} not found in block_colors. Using default (white).")
            from ursina import color as ursina_color
            color = ursina_color.white

        Entity.__init__(self, position=position, **kwargs)
        self.block_type = block_type

        # Only build mesh if exposed_faces are provided
        if exposed_faces:
            try:
                verts, tris, uvs, colors = [], [], [], []
                for normal, face in exposed_faces:
                    if not isinstance(face, (list, tuple)) or len(face) != 4:
                        print(f"Warning: Invalid face format: {face}")
                        continue
                    i = len(verts)
                    verts.extend([Vec3(p) + Vec3(*position) for p in face])
                    tris.extend([i, i+2, i+1, i, i+3, i+2])
                    uvs.extend([(0,0),(1,0),(1,1),(0,1)])
                    colors.extend([color]*4)
                if verts:
                    mesh = Mesh(vertices=verts, triangles=tris, uvs=uvs, colors=colors, mode='triangle')
                    mesh.disable_backface_culling = False
                    self.model = mesh
                else:
                    self.model = None
            except Exception as e:
                print(f"Error generating voxel mesh: {e}")
                self.model = None
        else:
            self.model = None  # No exposed faces, invisible

        # Collider is optional and should be set if needed
        self.collider = 'box' if self.model is not None else None

    # Optionally, add a safe update method if needed
    def update(self):
        try:
            # Placeholder for future logic
            pass
        except Exception as e:
            print(f"Error in Voxel.update: {e}")