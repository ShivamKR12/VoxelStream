from ursina import Entity, Vec3, color
from ursina.mesh_importer import Mesh

def generate_chunk_mesh(voxel_data, block_colors, default_color=color.green):
    """
    Given a set of (x, y, z) positions and block_colors dict, generate a mesh with only visible faces.
    Returns a Mesh object suitable for an Entity.
    """
    directions = {
        Vec3(0, 0, 1): [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)],  # front
        Vec3(0, 0, -1): [(1, 0, 0), (0, 0, 0), (0, 1, 0), (1, 1, 0)],  # back
        Vec3(0, 1, 0): [(0, 1, 1), (1, 1, 1), (1, 1, 0), (0, 1, 0)],  # top
        Vec3(0, -1, 0): [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)],  # bottom
        Vec3(1, 0, 0): [(1, 0, 1), (1, 0, 0), (1, 1, 0), (1, 1, 1)],  # right
        Vec3(-1, 0, 0): [(0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)],  # left
    }
    verts, tris, uvs, colors = [], [], [], []
    for pos in voxel_data:
        block_type = voxel_data[pos]
        for normal, face in directions.items():
            neighbor = tuple(Vec3(pos) + normal)
            if neighbor not in voxel_data:  # Only add face if air
                i = len(verts)
                face_world = [Vec3(p) + Vec3(pos) for p in face]
                verts.extend(face_world)
                tris.extend([i, i+2, i+1, i, i+3, i+2])
                uvs.extend([(0, 0), (1, 0), (1, 1), (0, 1)])
                c = block_colors.get(block_type, default_color)
                colors.extend([c] * 4)
    mesh = Mesh(vertices=verts, triangles=tris, uvs=uvs, colors=colors, mode='triangle')
    mesh.disable_backface_culling = False
    return mesh