import numpy as np
from vector_methods import *

class SolarPanel:
    def __init__(self, name = "", area = 0.0, surface_vector = np.array([0, 0, 1]), efficiency = 1):
        self.name = name
        self.area = area
        self.surface_normal = normalize_vector(surface_vector)  # normalize surface vector if not already normalized
        self.efficiency = efficiency

    def print(self):
        """Prints the area and surface normal of the solar panel."""
        print(f"Name: {self.name}, Area: {self.area} m², Surface Normal: ({', '.join(map(str, self.surface_normal))}) m")

class SolarPanelRectangle(SolarPanel):
    def __init__(self, length=5, width=5, height=0.5, surface_vector = np.array([0, 0, 1]), efficiency = 1):
        """Creates a rectangle shaped solar panel object."""
        if length == width:
            name = "Square"
        else:
            name = "Rectangle"
        area = length * width

        super().__init__(name, area, surface_vector, efficiency)
        self.length = length
        self.width = width
        self.height = height

class SolarPanelCircle(SolarPanel):
    def __init__(self, radius=5, height=0.5,surface_vector = np.array([0, 0, 1]), efficiency = 1):
        """Creates a circle shaped solar panel object."""
        name = "Circle"
        area = np.pi * (radius ** 2)

        super().__init__(name, area, surface_vector, efficiency)
        self.radius = radius
        self.height = height


