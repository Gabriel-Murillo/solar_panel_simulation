import numpy as np
from vector_methods import *

class Sunlight:
    def __init__(self, magnitude = 0, direction = np.array([0, 0, 0])):
        """Sunlight vector containing magnitude and direction. Direction is automatically normalized. Default values:
        magnitude of 0 I/A (Intensity/Unit Area) and direction of (0,0,0) in cartesian coordinates. Coordinates mean
        the following: x: right, left; y: forward, backward; z: up, down."""
        self.magnitude = magnitude
        self.direction = normalize_vector(direction) # normalize direction if not already normalized

    def print(self):
        """Prints the magnitude and direction of the vector."""
        print(f"Magnitude: {self.magnitude}, Direction: ({', '.join(map(str, self.direction))})")