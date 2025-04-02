import numpy as np
from vector_methods import *

class SolarPanel:
    def __init__(self, area = 0, surface_vector = np.array([0, 0, 1]), efficiency = 1):
        self.area = area
        self.surface_normal = normalize_vector(surface_vector)  # normalize surface vector if not already normalized
        self.efficiency = efficiency

    def print(self):
        """Prints the area and surface normal of the solar panel."""
        print(f"Area: {self.area} m², Surface Normal: ({', '.join(map(str, self.surface_normal))}) m")

class SolarPanelSquare(SolarPanel):
    def __init__(self, length = 1, surface_vector = np.array([0, 0, 1]), efficiency = 1):
        """Creates a square shaped solar panel object."""
        area = length ** 2
        super().__init__(area, surface_vector, efficiency)

class SolarPanelRectangle(SolarPanel):
    def __init__(self, length, width, surface_vector = np.array([0, 0, 1]), efficiency = 1):
        """Creates a rectangle shaped solar panel object."""
        area = length * width
        super().__init__(area, surface_vector, efficiency)

class SolarPanelCircle(SolarPanel):
    def __init__(self, radius, surface_vector = np.array([0, 0, 1]), efficiency = 1):
        """Creates a circle shaped solar panel object."""
        area = np.pi * (radius ** 2)
        super().__init__(area, surface_vector, efficiency)


