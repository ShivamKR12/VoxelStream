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

    def get_chunk_data(self, cx, cz):
        chunk_data = {}
        for dx in range(CHUNK_SIZE):
            for dz in range(CHUNK_SIZE):
                wx, wz = cx * CHUNK_SIZE + dx, cz * CHUNK_SIZE + dz
                h = sample_height(wx, wz)
                max_y = h
                placed_ys = [py for (px, py, pz) in self.placed if px == wx and pz == wz and self.placed[(px,py,pz)] != 0]
                if placed_ys:
                    max_y = max(max_y, max(placed_ys))
                for y in range(0, max_y+1):
                    pos = (wx, y, wz)
                    if pos in self.mined:
                        continue
                    bt = self.placed.get(pos) or compute_strata(y, h)
                    if bt != 0:
                        chunk_data[(dx, y, dz)] = bt
        return chunk_data

    def request_chunk(self, cx, cz):
        chunk_data = self.get_chunk_data(cx, cz)
        if (cx, cz) in self.chunks:
            self.chunks[(cx, cz)].update_mesh(chunk_data)
        else:
            chunk = Chunk(cx, cz, chunk_data)
            self.chunks[(cx, cz)] = chunk

    def update(self):
        pg = self.player.grid_pos()
        player_chunk = chunk_coords(pg)
        for cx in range(player_chunk[0] - 1, player_chunk[0] + 2):
            for cz in range(player_chunk[1] - 1, player_chunk[1] + 2):
                self.request_chunk(cx, cz)
        # Optionally handle unloading far chunks here

    def place_block(self, pos, block_type):
        self.placed[pos] = block_type
        cx, cz = chunk_coords(pos)
        self.request_chunk(cx, cz)

    def mine_block(self, pos):
        self.mined.add(pos)
        cx, cz = chunk_coords(pos)
        self.request_chunk(cx, cz)
        # For neighbor blocks, you may want to update their chunk if on edge
