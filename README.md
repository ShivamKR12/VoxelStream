# VoxelStream

> A streaming, chunked voxel engine built on Ursina — smooth terrain loading, frustum-culling, and multithreaded mesh builds.

VoxelStream is a modular Python project that turns Ursina into a high-performance, Minecraft-style voxel world. Chunks load and unload around the player, mesh generation happens in the background, and only visible faces ever hit the GPU.

---

## 🚀 Features

- **Chunked World**: World is partitioned into 16³-block chunks for easy streaming and LOD.
- **Asynchronous Mesh Builds**: Heavy terrain generation runs in worker threads; the main loop stays buttery-smooth.
- **Chunk Pooling**: Reuse chunk objects instead of destroying/recreating for minimal GC churn.
- **Frustum & Distance Culling**: Skip entire chunks outside the camera’s view or beyond a configurable radius.
- **Exposed-Face Meshing**: Only faces adjacent to air or mined blocks get built, cutting down on draw calls.
- **Pluggable Greedy Meshing Ready**: Mesh generator module primed for adding face-merging optimizations.
- **Clean Module Layout**: Eight focused modules—no more giant monoliths.

---

## 📂 Repository Structure

```

VoxelStream/
├── README.md
├── main.py              # App setup, UI, lighting & Ursina run loop
├── player.py            # FirstPersonController subclass & gravity logic
├── terrain.py           # Chunk manager, load/unload, threaded builds
├── chunk.py             # Chunk entity, pooling & collider logic
├── chunk_mesh.py        # Chunk-level mesh generator (exposed-face only)
├── voxel.py             # Per-block Entity for mining/placing & face updates
├── input_handler.py     # All key/mouse input & feature toggles (F/D/L)
└── utils.py             # Constants, noise, coords, frustum test & helpers

```

---

## ⚙️ Installation

1. **Clone the repo**  
   ```bash
   git clone https://github.com/ShivamKR12/VoxelStream.git
   cd VoxelStream
   ```

2. **Create a virtualenv & install dependencies**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install ursina opensimplex
   ```

3. **Run**

   ```bash
   python main.py
   ```

---

## 🎮 Usage

* **WASD + mouse** to move/look around.
* **Left-click / right-click** to mine/place blocks.
* **F** toggles frustum culling.
* **D** toggles distance culling.
* **L** toggles dynamic loading/unloading.
* **1/2/3** to cycle block types (Grass, Dirt, Stone).

---

## 🛠️ Architecture Overview

1. **`main.py`** initializes the Ursina app, sets up lighting, UI, and starts the game loop.
2. **`player.py`** delays gravity on spawn and offers grid-aligned helpers.
3. **`terrain.py`** watches the player’s chunk coordinate, requests chunk builds in threads, processes results in small batches, and handles stream-in/stream-out.
4. **`chunk.py`** wraps a chunk’s data & meshes in a recyclable Entity, with show/hide and collider toggles.
5. **`chunk_mesh.py`** exposes a function to generate a Mesh from block-type data (only exposed faces).
6. **`voxel.py`** provides a per-block Entity for mining/placing operations (ideal for click interaction).
7. **`input_handler.py`** centralizes all key and mouse bindings, forwarding actions to the terrain & player.
8. **`utils.py`** holds block IDs, colors, noise sampling, coordinate conversions, and a simple frustum-culling helper.

---

## 🌱 Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a Pull Request

Please keep commits focused, document new modules/functions, and add tests where applicable.

---

## 📄 License

MIT © [Shivam](https://github.com/ShivamKR12)

Happy voxeling! 🧱✨
