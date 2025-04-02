import numpy as np
from vpython import *

from sunlight import Sunlight
from solar_panels import *
from graph3D import *


class Simulation:
    def __init__(self, sunlight, solar_panel):
        self.sunlight = sunlight # sunlight vector
        self.solar_panel = solar_panel # solar panel vector

        self.magnitude = sunlight.magnitude * solar_panel.area
        self.dot_product = np.clip(np.dot(sunlight.direction, solar_panel.surface_normal), -1.0, 1.0)

    def get_electricity(self):
        """Return the total electricity given a sunlight vector, area vector, and solar panel efficiency."""
        result = -1 * self.magnitude * self.dot_product * self.solar_panel.efficiency
        if result < 0: # negative electricity is an unphysical result in this scenario
            result = 0
        return result

    def get_angle_radians(self):
        return np.arccos(self.dot_product)

    def get_angle_degrees(self):
        return np.degrees(self.get_angle_radians())

    def graph_vector_representation(self):
        view = Graph3D()

        sun = sphere(pos=(view.unit_vectors[2] * 4.5), radius=0.2, color=color.yellow)
        sun_vector = array_to_vector(*self.sunlight.direction) # convert to usable format
        sun_arrow = arrow(pos=sun.pos, axis=sun_vector, color=color.yellow)

        label(pos=(sun.pos + sun_vector) * 1.1, text=', '.join(f"{x:.2f}" for x in self.sunlight.direction), color=color.yellow, box=False)

        solar_panel_surface_normal_vector = array_to_vector(*self.solar_panel.surface_normal)
        solar_panel_surface_normal_arrow = arrow(pos=view.origin, axis=solar_panel_surface_normal_vector, color=color.white)
        label(pos=(view.origin + solar_panel_surface_normal_vector) * 1.1, text=', '.join(f"{x:.2f}" for x in self.solar_panel.surface_normal), color=color.white, box=False)

        while True:
            rate(60)  # Keeps the scene running


if __name__ == '__main__':
    # Create sunray objects
    sunray_0 = Sunlight()
    sunray_down = Sunlight(10, np.array([0, 0, -1]))
    sunray_bottom_right = Sunlight(10,  np.array([1, 0, -1]))

    # Create solar panel objects
    square_panel = SolarPanelSquare(10, np.array([0, 0, 1]), 0.5)
    rectangle_panel = SolarPanelRectangle(20,5, np.array([0, 1, 1]))
    circle_panel = SolarPanelCircle(5, np.array([1, 1, 1]))

    # Create simulation
    sim1 = Simulation(sunray_down, square_panel)
    sim2 = Simulation(sunray_bottom_right, rectangle_panel)

    square_panel.print()

    print(f"Angle in radians: {sim1.get_angle_radians():.2f}")
    print(f"Angle in degrees: {sim1.get_angle_degrees():.2f}°")
    print(f"Total Electricity: {sim1.get_electricity():.2f} W")

    print()

    print(f"Angle in radians: {sim2.get_angle_radians():.2f}")
    print(f"Angle in degrees: {sim2.get_angle_degrees():.2f}°")
    print(f"Total Electricity: {sim2.get_electricity():.2f} W")

    #sim1.graph_vector_representation()
    sim2.graph_vector_representation()