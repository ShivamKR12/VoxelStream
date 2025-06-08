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

# Validate block_types and block_colors at import
for name, btype in block_types:
    if btype not in block_colors:
        print(f"Warning: Block type {btype} ({name}) is missing in block_colors.")

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
CHUNK_SIZE = 8
VISIBLE_RADIUS = 8  # blocks

try:
    noise = OpenSimplex(seed=42)
except Exception as e:
    print(f"Error initializing OpenSimplex noise: {e}")
    noise = None

def sample_height(wx, wz):
    if noise is None:
        print("Noise generator unavailable, defaulting height to 0")
        return 0
    try:
        n   = noise.noise2(wx * NOISE_SCALE, wz * NOISE_SCALE)
        n01 = (n + 1)/2
        h = int(n01 * MAX_HEIGHT)
        if h < 0: h = 0
        return h
    except Exception as e:
        print(f"Error in sample_height: {e}")
        return 0

def compute_strata(y, h):
    try:
        if y == h:
            return BLOCK_GRASS
        if h-4 <= y < h:
            return BLOCK_DIRT
        if h-14 <= y < h-4:
            return BLOCK_STONE
        return BLOCK_AIR
    except Exception as e:
        print(f"Error in compute_strata: {e}")
        return BLOCK_AIR

def chunk_coords(pos):
    # Returns (chunk_x, chunk_z) for world position pos (tuple or Vec3)
    try:
        if isinstance(pos, Vec3):
            x, _, z = pos
        elif hasattr(pos, "__getitem__") and len(pos) >= 3:
            x, _, z = pos
        else:
            raise ValueError("Invalid position for chunk_coords")
        if CHUNK_SIZE == 0:
            raise ValueError("CHUNK_SIZE cannot be zero")
        return (int(x) // CHUNK_SIZE, int(z) // CHUNK_SIZE)
    except Exception as e:
        print(f"Error in chunk_coords: {e}")
        return (0, 0)

def block_in_chunk_coords(pos):
    # Returns block position relative to chunk origin
    try:
        if isinstance(pos, Vec3):
            x, y, z = pos
        elif hasattr(pos, "__getitem__") and len(pos) >= 3:
            x, y, z = pos
        else:
            raise ValueError("Invalid position for block_in_chunk_coords")
        if CHUNK_SIZE == 0:
            raise ValueError("CHUNK_SIZE cannot be zero")
        return (int(x) % CHUNK_SIZE, int(y), int(z) % CHUNK_SIZE)
    except Exception as e:
        print(f"Error in block_in_chunk_coords: {e}")
        return (0, 0, 0)

def world_from_chunk(cx, cz, bx, by, bz):
    try:
        return (cx * CHUNK_SIZE + bx, by, cz * CHUNK_SIZE + bz)
    except Exception as e:
        print(f"Error in world_from_chunk: {e}")
        return (0, 0, 0)

def make_mesh_with_backface_culling(*, vertices, triangles, uvs=None, colors=None, mode='triangle'):
    try:
        mesh = Mesh(vertices=vertices, triangles=triangles, uvs=uvs, colors=colors, mode=mode)
        mesh.disable_backface_culling = False
        return mesh
    except Exception as e:
        print(f"Error in make_mesh_with_backface_culling: {e}")
        return None

def is_chunk_in_frustum(cx, cz, camera=None, fov=120, max_dist=None):
    """
    Returns True if the chunk at (cx, cz) is likely in the camera's view frustum.
    Uses the chunk center for the test.
    """
    try:
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
        half_fov = (fov if fov else getattr(camera, 'fov', 120)) / 2

        # Optionally clamp by distance (clip plane)
        max_dist = max_dist if max_dist else getattr(camera, "clip_plane_far", 200)
        return angle < half_fov and dist < max_dist
    except Exception as e:
        print(f"Error in is_chunk_in_frustum: {e}")
        return True  # Default to visible if uncertain
    
def project_aabb_to_screen(min_pt: Vec3, max_pt: Vec3):
    """
    Returns (x0, y0, x1, y1) in normalized screen space [0,1].
    """
    # eight corners of the box
    corners = [
        Vec3(x, y, z)
        for x in (min_pt.x, max_pt.x)
        for y in (min_pt.y, max_pt.y)
        for z in (min_pt.z, max_pt.z)
    ]
    sx = [camera.world_to_screen(c).x for c in corners]
    sy = [camera.world_to_screen(c).y for c in corners]
    return (min(sx), min(sy), max(sx), max(sy))

def aabb_is_fully_occluded(screen_rect, occlusion_grid, grid_size=(16,16)):
    """
    screen_rect = (x0,y0,x1,y1) in [0,1].
    occlusion_grid is a 2D boolean array of size grid_size 
       marking which cells are already covered.
    Returns True if ALL cells overlapped by the rect are marked covered.
    """
    cols, rows = grid_size
    x0, y0, x1, y1 = screen_rect
    # convert to cell indices
    ci0, ri0 = int(x0 * cols), int(y0 * rows)
    ci1, ri1 = min(cols-1, int(x1 * cols)), min(rows-1, int(y1 * rows))
    for ci in range(ci0, ci1+1):
        for ri in range(ri0, ri1+1):
            if not occlusion_grid[ri][ci]:
                return False
    return True

def mark_occlusion(screen_rect, occlusion_grid, grid_size=(16,16)):
    cols, rows = grid_size
    x0, y0, x1, y1 = screen_rect
    ci0, ri0 = int(x0 * cols), int(y0 * rows)
    ci1, ri1 = min(cols-1, int(x1 * cols)), min(rows-1, int(y1 * rows))
    for ci in range(ci0, ci1+1):
        for ri in range(ri0, ri1+1):
            occlusion_grid[ri][ci] = True
