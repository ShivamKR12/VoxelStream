from ursina import Vec3, Vec2, color, camera
from ursina import Mesh
from opensimplex import OpenSimplex
import math

BLOCK_AIR   = 0
BLOCK_GRASS = 1
BLOCK_DIRT  = 2
BLOCK_STONE = 3

block_types = [
    ("Grass", BLOCK_GRASS),
    ("Dirt", BLOCK_DIRT),
    ("Stone", BLOCK_STONE),
]

block_colors = {
    BLOCK_AIR:   color.clear,
    BLOCK_GRASS: color.rgb32(34, 139, 34),
    BLOCK_DIRT:  color.rgb32(139, 69, 19),
    BLOCK_STONE: color.rgb32(100, 100, 100),
}

FACE_DEFS = {
    'north':  (Vec3(0,0,1),  [Vec3(0,0,1), Vec3(1,0,1), Vec3(1,1,1), Vec3(0,1,1)]),
    'south':  (Vec3(0,0,-1), [Vec3(1,0,0), Vec3(0,0,0), Vec3(0,1,0), Vec3(1,1,0)]),
    'east':   (Vec3(1,0,0),  [Vec3(1,0,1), Vec3(1,0,0), Vec3(1,1,0), Vec3(1,1,1)]),
    'west':   (Vec3(-1,0,0), [Vec3(0,0,0), Vec3(0,0,1), Vec3(0,1,1), Vec3(0,1,0)]),
    'top':    (Vec3(0,1,0),  [Vec3(0,1,1), Vec3(1,1,1), Vec3(1,1,0), Vec3(0,1,0)]),
    'bottom': (Vec3(0,-1,0), [Vec3(0,0,0), Vec3(1,0,0), Vec3(1,0,1), Vec3(0,0,1)]),
}

NOISE_SCALE = 0.1
MAX_HEIGHT = 5
TERRAIN_RADIUS = 8  # in blocks, not chunks
# TERRAIN_RADIUS = 8 to load only 9 chunks (3x3 grid)
# Or set TERRAIN_RADIUS = 4 for even fewer!
CHUNK_SIZE = 8
VISIBLE_RADIUS = 8  # blocks

noise = OpenSimplex(seed=42)

def sample_height(wx, wz):
    n   = noise.noise2(wx * NOISE_SCALE, wz * NOISE_SCALE)
    n01 = (n + 1)/2
    return int(n01 * MAX_HEIGHT)

def compute_strata(y, h):
    if y == h:
        return BLOCK_GRASS
    if h-4 <= y < h:
        return BLOCK_DIRT
    if h-14 <= y < h-4:
        return BLOCK_STONE
    return BLOCK_AIR

def chunk_coords(pos):
    # Returns (chunk_x, chunk_z) for world position pos (tuple or Vec3)
    return (int(pos[0]) // CHUNK_SIZE, int(pos[2]) // CHUNK_SIZE)

def block_in_chunk_coords(pos):
    # Returns block position relative to chunk origin
    return (int(pos[0]) % CHUNK_SIZE, int(pos[1]), int(pos[2]) % CHUNK_SIZE)

def world_from_chunk(cx, cz, bx, by, bz):
    # Converts chunk+block position to world position
    return (cx * CHUNK_SIZE + bx, by, cz * CHUNK_SIZE + bz)

def make_mesh_with_backface_culling(*, vertices, triangles, uvs=None, colors=None, mode='triangle'):
    mesh = Mesh(vertices=vertices, triangles=triangles, uvs=uvs, colors=colors, mode=mode)
    mesh.disable_backface_culling = False
    return mesh

def is_chunk_in_frustum(cx, cz, camera=None, fov=120, max_dist=None):
    """
    Returns True if the chunk at (cx, cz) is likely in the camera's view frustum.
    Uses the chunk center for the test.
    """
    if camera is None:
        from ursina import camera as global_camera
        camera = global_camera

    # Chunk world center
    chunk_center = Vec3(cx * CHUNK_SIZE + CHUNK_SIZE/2, 0, cz * CHUNK_SIZE + CHUNK_SIZE/2)

    # Vector from camera to chunk
    cam_pos = camera.world_position
    to_chunk = chunk_center - cam_pos
    dist = to_chunk.length()
    to_chunk_norm = to_chunk.normalized()

    # Angle between camera forward and chunk center
    dot = camera.forward.normalized().dot(to_chunk_norm)
    angle = math.degrees(math.acos(dot)) if -1 < dot < 1 else (0 if dot >= 1 else 180)

    # Use camera's FOV (horizontal) for cone culling
    half_fov = (fov if fov else camera.fov) / 2

    # Optionally clamp by distance (clip plane)
    max_dist = max_dist if max_dist else getattr(camera, "clip_plane_far", 200)
    return angle < half_fov and dist < max_dist