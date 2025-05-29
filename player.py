from ursina.prefabs.first_person_controller import FirstPersonController
from utils import sample_height
from ursina import invoke

class Player(FirstPersonController):
    def __init__(self):
        ground_y = sample_height(0, 0)
        super().__init__(position=(0, ground_y + 10, 0))
        self.gravity_paused = True
        self._original_gravity = self.gravity
        self.gravity = 0  # Pause gravity at start

        # Schedule gravity to be enabled after 5 seconds
        invoke(self.enable_gravity, delay=5)

    def enable_gravity(self):
        self.gravity = self._original_gravity
        self.gravity_paused = False

    def grid_pos(self):
        # Returns the player's current position snapped to grid (XZ)
        return (int(round(self.x)), 0, int(round(self.z)))

    def update(self):
        # Only apply update if gravity is enabled or for other logic
        super().update()