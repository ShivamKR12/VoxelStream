from ursina import camera
from utils import sample_height, compute_strata, chunk_coords, CHUNK_SIZE, TERRAIN_RADIUS, block_colors
from voxel_chunk import Chunk

class Terrain:
    def __init__(self, player):
        self.player = player
        self.chunks = {}  # (cx,cz): Chunk
        self.mined = set()
        self.placed = {}
        self.chunk_pool = []
        self.frustum_culling_enabled = False
        self.max_loaded_chunks = 32  # Limit to avoid memory leaks
        self.unload_distance = 3     # Chunks farther than this from player will be unloaded

    def get_chunk_data(self, cx, cz):
        chunk_data = {}
        try:
            for dx in range(CHUNK_SIZE):
                for dz in range(CHUNK_SIZE):
                    wx, wz = cx * CHUNK_SIZE + dx, cz * CHUNK_SIZE + dz
                    h = sample_height(wx, wz)
                    max_y = h
                    placed_ys = [py for (px, py, pz) in self.placed if px == wx and pz == wz and self.placed[(px, py, pz)] != 0]
                    if placed_ys:
                        max_y = max(max_y, max(placed_ys))
                    for y in range(0, max_y+1):
                        pos = (wx, y, wz)
                        if pos in self.mined:
                            continue
                        bt = self.placed.get(pos) or compute_strata(y, h)
                        if bt != 0:
                            chunk_data[(dx, y, dz)] = bt
        except Exception as e:
            print(f"Error in get_chunk_data: {e}")
        return chunk_data

    def request_chunk(self, cx, cz):
        chunk_data = self.get_chunk_data(cx, cz)
        try:
            if (cx, cz) in self.chunks:
                self.chunks[(cx, cz)].update_mesh(chunk_data)
            else:
                chunk = Chunk(cx, cz, chunk_data)
                self.chunks[(cx, cz)] = chunk
        except Exception as e:
            print(f"Error in request_chunk: {e}")

    def update(self):
        try:
            pg = self.player.grid_pos()
            player_chunk = chunk_coords(pg)
            # Load nearby chunks
            for cx in range(player_chunk[0] - 1, player_chunk[0] + 2):
                for cz in range(player_chunk[1] - 1, player_chunk[1] + 2):
                    self.request_chunk(cx, cz)
            # Unload far chunks
            self._unload_far_chunks(player_chunk)
        except Exception as e:
            print(f"Error in Terrain.update: {e}")

    def _unload_far_chunks(self, player_chunk):
        # Unload chunks far from the player to limit memory use
        try:
            to_unload = []
            for (cx, cz) in self.chunks:
                if abs(cx - player_chunk[0]) > self.unload_distance or abs(cz - player_chunk[1]) > self.unload_distance:
                    to_unload.append((cx, cz))
            for key in to_unload:
                chunk = self.chunks.pop(key)
                try:
                    chunk.hide()
                    del chunk
                except Exception as e:
                    print(f"Error unloading chunk {key}: {e}")
        except Exception as e:
            print(f"Error in _unload_far_chunks: {e}")

    def place_block(self, pos, block_type):
        if not isinstance(pos, (tuple, list)) or len(pos) < 3:
            print(f"Invalid block position: {pos}")
            return
        if not isinstance(block_type, int):
            print(f"Invalid block_type {block_type}, must be int")
            return
        print("Placing block at:", pos)
        self.placed[pos] = block_type
        try:
            cx, cz = chunk_coords(pos)
            self.request_chunk(cx, cz)
        except Exception as e:
            print(f"Error placing block {pos}: {e}")

    def mine_block(self, pos):
        if not isinstance(pos, (tuple, list)) or len(pos) < 3:
            print(f"Invalid mine position: {pos}")
            return
        print("Mining block at:", pos)
        self.mined.add(pos)
        try:
            cx, cz = chunk_coords(pos)
            self.request_chunk(cx, cz)
        except Exception as e:
            print(f"Error mining block {pos}: {e}")

    def get_block_type(self, pos):
        # Validate position
        if not isinstance(pos, (tuple, list)) or len(pos) < 3:
            print(f"Invalid position for get_block_type: {pos}")
            return 0  # air
        try:
            if pos in self.mined:
                return 0  # air
            if pos in self.placed:
                return self.placed[pos]
            wx, y, wz = pos
            h = sample_height(wx, wz)
            return compute_strata(y, h)
        except Exception as e:
            print(f"Error in get_block_type for {pos}: {e}")
            return 0  # default to air

    # Optionally, add methods for saving/loading placed/mined data for persistence