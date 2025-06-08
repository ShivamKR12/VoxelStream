from ursina.prefabs.first_person_controller import FirstPersonController
from utils import sample_height
from ursina import invoke

class Player(FirstPersonController):
    def __init__(self):
        try:
            ground_y = sample_height(0, 0)
            if ground_y is None or not isinstance(ground_y, (int, float)):
                print("Warning: sample_height(0, 0) returned invalid value, defaulting to 0")
                ground_y = 0
        except Exception as e:
            print(f"Error in sample_height: {e}, defaulting to 0")
            ground_y = 0

        try:
            super().__init__(position=(0, ground_y + 10, 0))
        except Exception as e:
            print(f"Error initializing FirstPersonController: {e}")
            # Fallback to a basic Entity if needed (optional, for robustness)
            # from ursina import Entity
            # Entity.__init__(self, position=(0, ground_y + 10, 0))
            return

        self.gravity_paused = True
        self._original_gravity = getattr(self, 'gravity', 1)
        self.gravity = 0  # Pause gravity at start

        # Schedule gravity to be enabled after 5 seconds, handle errors
        try:
            invoke(self.enable_gravity, delay=5)
        except Exception as e:
            print(f"Error scheduling gravity enable: {e}")

    def enable_gravity(self):
        self.gravity = self._original_gravity
        self.gravity_paused = False

    def grid_pos(self):
        # Returns the player's current position snapped to grid (XZ)
        try:
            return (int(round(self.x)), 0, int(round(self.z)))
        except Exception as e:
            print(f"Error computing grid_pos: {e}")
            return (0, 0, 0)

    def update(self):
        # Only apply update if gravity is enabled or for other logic
        try:
            super().update()
        except Exception as e:
            print(f"Error in Player.update: {e}")