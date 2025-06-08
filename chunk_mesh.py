from ursina import Vec3, color
from ursina.mesh_importer import Mesh

def generate_chunk_mesh(voxel_data, block_colors, default_color=color.green):
    """
    Given a set of (x, y, z) positions and block_colors dict, generate a mesh with only visible faces.
    Returns a Mesh object suitable for an Entity.
    """
    # Input validation
    if not isinstance(voxel_data, dict):
        raise ValueError("voxel_data must be a dictionary of positions to block types")
    if not isinstance(block_colors, dict):
        raise ValueError("block_colors must be a dictionary")

    directions = {
        Vec3(0, 0, 1): [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)],  # front
        Vec3(0, 0, -1): [(1, 0, 0), (0, 0, 0), (0, 1, 0), (1, 1, 0)],  # back
        Vec3(0, 1, 0): [(0, 1, 1), (1, 1, 1), (1, 1, 0), (0, 1, 0)],  # top
        Vec3(0, -1, 0): [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)],  # bottom
        Vec3(1, 0, 0): [(1, 0, 1), (1, 0, 0), (1, 1, 0), (1, 1, 1)],  # right
        Vec3(-1, 0, 0): [(0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)],  # left
    }
    verts, tris, uvs, colors, normals = [], [], [], [], []
    max_verts = 60000  # Safety: avoid excessive mesh size

    for pos in voxel_data:
        # Ensure pos is tuple or Vec3
        try:
            vec_pos = Vec3(*pos) if not isinstance(pos, Vec3) else pos
        except Exception:
            print(f"Warning: invalid position {pos}, skipping.")
            continue

        block_type = voxel_data[pos]
        for normal, face in directions.items():
            neighbor = tuple(vec_pos + normal)
            if neighbor not in voxel_data:  # Only add face if air
                i = len(verts)
                face_world = [Vec3(p) + vec_pos for p in face]
                verts.extend(face_world)
                tris.extend([i, i+2, i+1, i, i+3, i+2])
                uvs.extend([(0, 0), (1, 0), (1, 1), (0, 1)])
                c = block_colors.get(block_type, default_color)
                if c is None:
                    print(f"Warning: No color for block_type {block_type}, using default.")
                    c = default_color
                colors.extend([c] * 4)
                normals.extend([normal] * 4)  # Add normal vector for each vertex
                if len(verts) > max_verts:
                    print("Warning: chunk mesh too large, truncating.")
                    break

    try:
        mesh = Mesh(vertices=verts, triangles=tris, uvs=uvs, colors=colors, normals=normals, mode='triangle')
        mesh.disable_backface_culling = False
    except Exception as e:
        print(f"Error creating mesh: {e}")
        return None

    return mesh