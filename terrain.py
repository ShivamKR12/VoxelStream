import time
from math import floor
from ursina import scene, camera
from utils import *
from ursina import invoke
from chunk import Chunk
from voxel import Voxel

import threading
from queue import Queue

class Terrain:
    def __init__(self, player):
        self.player = player

        self.chunks = {}  # (cx,cz): Chunk
        self.mined = set()
        self.placed = {}
        self.chunk_pool = []     # Pool of unused Chunk objects

        self.frustum_culling_enabled = False
        self.distance_culling_enabled = False
        self.dynamic_loading_enabled = True

        self._last_print_time = 0

        # --- Multithreading additions ---
        self.chunk_build_queue = Queue()
        self.chunk_building = set()  # To avoid duplicate work
        self._pending_finalizations = []  # List of (cx, cz, pending_blocks_list)
        self._stop_event = threading.Event()

        # Start background thread to finalize built chunks
        invoke(self.process_chunk_queue, delay=0.05)

    def chunk_bounds(self, cx, cz):
        x0, x1 = cx*CHUNK_SIZE, (cx+1)*CHUNK_SIZE
        z0, z1 = cz*CHUNK_SIZE, (cz+1)*CHUNK_SIZE
        return x0, x1, z0, z1

    def request_chunk(self, cx, cz):
        # Called from main thread; triggers background build if not present
        key = (cx, cz)
        if key in self.chunks or key in self.chunk_building:
            return
        self.chunk_building.add(key)
        threading.Thread(target=self.background_chunk_build, args=(cx, cz), daemon=True).start()

    def background_chunk_build(self, cx, cz):
        # Build chunk data in a background thread
        chunk_blocks = {}
        chunk_data = {}
        for dx in range(CHUNK_SIZE):
            for dz in range(CHUNK_SIZE):
                wx, wz = cx*CHUNK_SIZE + dx, cz*CHUNK_SIZE + dz
                # Find the highest non-mined block
                h = sample_height(wx, wz)
                # For all possible y values (from 0 to h, and any placed block above)
                max_y = h
                placed_ys = [py for (px, py, pz) in self.placed if px == wx and pz == wz and self.placed[(px,py,pz)] != BLOCK_AIR and (wx,py,wz) not in self.mined]
                if placed_ys:
                    max_y = max(max_y, max(placed_ys))
                for y in range(0, max_y+1):
                    pos = (wx, y, wz)
                    if (pos in self.mined):
                        continue
                    if (pos in self.placed) and self.placed[pos] == BLOCK_AIR:
                        continue
                    # Only spawn if at least one neighbor is air or mined or outside terrain/placed
                    exposed = False
                    for n in [
                        (wx+1,y,wz), (wx-1,y,wz),
                        (wx,y+1,wz), (wx,y-1,wz),
                        (wx,y,wz+1), (wx,y,wz-1)
                    ]:
                        nx, ny, nz = n
                        above_terrain = ny > sample_height(nx,nz)
                        placed_air = (n in self.placed and self.placed[n]==BLOCK_AIR)
                        mined = (n in self.mined)
                        out_of_bounds = ny < 0
                        not_present = (ny > max_y)
                        if (above_terrain or placed_air or mined or out_of_bounds or not_present):
                            exposed = True
                    if not exposed:
                        continue
                    # Get block type
                    if pos in self.placed:
                        bt = self.placed[pos]
                    else:
                        bt = compute_strata(y, h)
                    if bt == BLOCK_AIR:
                        continue
                    chunk_data[(dx, y, dz)] = bt

        # --- ADD THIS BLOCK ---
        # Ensure placed blocks above the terrain are included
        for pos, block_type in self.placed.items():
            wx, y, wz = pos
            if (cx * CHUNK_SIZE <= wx < (cx + 1) * CHUNK_SIZE) and (cz * CHUNK_SIZE <= wz < (cz + 1) * CHUNK_SIZE):
                dx = wx - cx * CHUNK_SIZE
                dz = wz - cz * CHUNK_SIZE
                if (dx, y, dz) not in chunk_data and block_type != BLOCK_AIR and (wx, y, wz) not in self.mined:
                    # Only include if it is exposed (nothing above it)
                    if (wx, y+1, wz) not in self.placed and (wx, y+1, wz) not in chunk_data:
                        chunk_data[(dx, y, dz)] = block_type

        columns = set()
        for (dx, y, dz) in chunk_data:
            columns.add((dx, dz))
        print(f"Chunk ({cx},{cz}) has {len(chunk_data)} blocks, {len(columns)} columns")

        # Occlusion culling: only create Voxels for exposed faces
        exposed_voxels = []
        for (dx, y, dz), bt in chunk_data.items():
            world_pos = (cx*CHUNK_SIZE + dx, y, cz*CHUNK_SIZE + dz)
            exposed_faces = []
            for normal, _ in FACE_DEFS.values():
                npos = (dx+int(normal.x), y+int(normal.y), dz+int(normal.z))
                if npos not in chunk_data:
                    exposed_faces.append(normal)
            if exposed_faces:
                exposed_voxels.append((world_pos, bt, exposed_faces))
        # Queue for main thread to finalize
        self.chunk_build_queue.put((cx, cz, exposed_voxels))

    def process_chunk_queue(self):
        # Process completed chunk data from the background thread
        # Called regularly on main thread
        while not self.chunk_build_queue.empty():
            cx, cz, exposed_voxels = self.chunk_build_queue.get()
            # Instead of creating all, queue for batched finalization
            self._pending_finalizations.append([cx, cz, exposed_voxels, 0, {}])  # 0 = start index, {} = chunk_blocks
            
        # Process a few blocks for each pending chunk this frame
        BATCH_SIZE = 15  # You can tweak this
        still_pending = []
        for entry in self._pending_finalizations:
            cx, cz, exposed_voxels, idx, chunk_blocks = entry
            end = min(idx + BATCH_SIZE, len(exposed_voxels))
            for i in range(idx, end):
                world_pos, bt, exposed_faces = exposed_voxels[i]
                dx = world_pos[0] - cx*CHUNK_SIZE
                y  = world_pos[1]
                dz = world_pos[2] - cz*CHUNK_SIZE
                voxel = Voxel(world_pos, bt)
                voxel.parent = scene
                voxel.update_mesh(exposed_faces)
                chunk_blocks[(dx, y, dz)] = voxel
            if end < len(exposed_voxels):
                # Not done yet, continue next frame
                still_pending.append([cx, cz, exposed_voxels, end, chunk_blocks])
            else:
                # Before creating a new Chunk, try to reuse a pooled one!
                chunk_data = { (dx, y, dz): bt for (world_pos, bt, exposed_faces) in exposed_voxels }
                if self.chunk_pool:
                    chunk = self.chunk_pool.pop()
                    chunk.reset(cx, cz, chunk_data, chunk_blocks)  # You'll implement reset()
                else:
                    chunk = Chunk(cx, cz, chunk_data, chunk_blocks)
                chunk.update_colliders((self.player.x, self.player.y, self.player.z))
                self.chunks[(cx, cz)] = chunk
                self.chunk_building.discard((cx, cz))
        self._pending_finalizations = still_pending

        # Schedule next check
        invoke(self.process_chunk_queue, delay=0.05)

    def unload_far_chunks(self, player_chunk):
        chunks_to_unload = []
        for (cx, cz) in self.chunks:
            if abs(cx - player_chunk[0]) > TERRAIN_RADIUS // CHUNK_SIZE or abs(cz - player_chunk[1]) > TERRAIN_RADIUS // CHUNK_SIZE:
                chunks_to_unload.append((cx, cz))
        for key in chunks_to_unload:
            chunk = self.chunks.pop(key)
            chunk.disable()  # <--- DISABLE the chunk entity and all its voxels
            self.chunk_pool.append(chunk)

    def load_near_chunks(self, player_chunk):
        # for cx in range(player_chunk[0] - TERRAIN_RADIUS // CHUNK_SIZE, player_chunk[0] + TERRAIN_RADIUS // CHUNK_SIZE + 1):
        #     for cz in range(player_chunk[1] - TERRAIN_RADIUS // CHUNK_SIZE, player_chunk[1] + TERRAIN_RADIUS // CHUNK_SIZE + 1):
        for cx in range(player_chunk[0] - 1, player_chunk[0] + 2):
            for cz in range(player_chunk[1] - 1, player_chunk[1] + 2):
                if self.frustum_culling_enabled:
                    if not is_chunk_in_frustum(cx, cz, camera=camera):
                        # Optionally, hide the chunk if it was already loaded:
                        if (cx, cz) in self.chunks:
                            self.chunks[(cx, cz)].disable()
                        continue
                if (cx, cz) not in self.chunks:
                    self.request_chunk(cx, cz)
                else:
                    self.chunks[(cx, cz)].show()

    def update(self):
        pg = self.player.grid_pos()
        player_chunk = chunk_coords(pg)
        self.load_near_chunks(player_chunk)
        self.unload_far_chunks(player_chunk)

        # Colliders only near player
        px, py, pz = self.player.x, self.player.y, self.player.z
        for chunk in self.chunks.values():
            chunk.update_colliders((px, py, pz))
            # self.chunks[(px, pz)] = chunk

        # Print debug info once per second
        ct = time.time()
        if ct - self._last_print_time > 1.0:
            active_chunks = sum(1 for c in self.chunks.values() if c.active)
            block_count = sum(len(c.chunk_blocks) for c in self.chunks.values() if c.active)
            print(f"Chunks: {active_chunks}, Blocks: {block_count}, Waiting builds: {len(self.chunk_building)}")
            self._last_print_time = ct

    def place_block(self, pos, block_type):
        print("Terrain.place_block called with", pos, block_type)
        self.placed[pos] = block_type
        cx, cz = chunk_coords(pos)
        # Remove from chunks and request rebuild (threaded)
        if (cx, cz) in self.chunks:
            old_chunk = self.chunks.pop((cx, cz))
            old_chunk.disable()            # Properly disables chunk and its voxels
            self.chunk_pool.append(old_chunk)
        self.request_chunk(cx, cz)

    def mine_block(self, pos):
        self.mined.add(pos)
        cx, cz = chunk_coords(pos)
        if (cx, cz) in self.chunks:
            old_chunk = self.chunks.pop((cx, cz))
            old_chunk.disable()            # Properly disables chunk and its voxels
            self.chunk_pool.append(old_chunk)
        # Check all 6 neighbors and request their chunk to rebuild if necessary
        for dx, dy, dz in [
            (1,0,0), (-1,0,0), (0,1,0), (0,-1,0), (0,0,1), (0,0,-1)
        ]:
            npos = (pos[0]+dx, pos[1]+dy, pos[2]+dz)
            if npos[1] < 0:
                continue
            ncx, ncz = chunk_coords(npos)
            if (ncx, ncz) in self.chunks:
                old_chunk = self.chunks.pop((ncx, ncz))
                old_chunk.disable()
                self.chunk_pool.append(old_chunk)
            self.request_chunk(ncx, ncz)
        self.request_chunk(cx, cz)
