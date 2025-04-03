import numpy as np
from vpython import *

from sunlight import Sunlight
from solar_panels import *
from graph3D import *
import sys

RUNNING = True
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
        model = Graph3D(1000, 800) # Set up scene

        # Draw the sun
        #TODO sun is coded to be above in this scene, need way to customize it
        sun_height_c = 4.5
        sun = sphere(canvas=scene, pos=(model.unit_vectors[2] * sun_height_c), radius=0.2, color=color.yellow, emmissive=True)
        # Convert np.array containing direction of sunlight to vector usable in vpython
        sun_vector = array_to_vector(*self.sunlight.direction)
        # Draw arrow from sun sphere
        sun_arrow = arrow(canvas=scene, pos=sun.pos, axis=sun_vector, color=color.yellow)
        # Label the sun vector
        label(canvas=scene, pos=(sun.pos + sun_vector), text=', '.join(f"{x:.2f}" for x in self.sunlight.direction), color=color.yellow, box=False)

        # Direction that the solar panel is facing in vector form
        self.solar_panel_surface_normal_vector = array_to_vector(*self.solar_panel.surface_normal)
        # Draw arrow for surface normal
        solar_panel_surface_normal_arrow = arrow(canvas=scene, pos=model.origin, axis=self.solar_panel_surface_normal_vector, color=color.white)
        # Label the surface normal vector
        label(canvas=scene, pos=(model.origin + self.solar_panel_surface_normal_vector) * 1.2, text=', '.join(f"{x:.2f}" for x in self.solar_panel.surface_normal), color=color.white, box=False)

        # Draw solar panel plane
        # TODO draw circles
        solar_c = 0.25 # scale l w h for rectangular solar panels
        solar_panel_plane = box(canvas=scene,pos=model.origin, length = solar_c*self.solar_panel.length, width = solar_c*self.solar_panel.width, height = solar_c*self.solar_panel.height, color=color.white, opacity = 0.65)

        # Rotate solar panel plane to align with its solar panel
        rotation_axis = cross(vector(0,1,0), self.solar_panel_surface_normal_vector)
        if mag(rotation_axis) > 1e-6:
            rotation_angle = diff_angle(vector(0, 1, 0), self.solar_panel_surface_normal_vector)
            solar_panel_plane.rotate(angle=rotation_angle, axis=rotation_axis, origin=model.origin)

        # Add button to reset view
        btn_reset_view = button(canvas=scene, text="Reset view", bind=lambda _: model._reset_view())

        # Button to end simulation
        btn_end = button(canvas=scene, text="End simulation", bind=lambda _: end_sim())

        # Sliders to control orientation of the solar panel
        # slider_spn_x = slider(min = -1, max= 1, value = self.solar_panel_surface_normal_vector.x)

        scene.userzoom = False
        scene.userpan = False

        while RUNNING:
            # Lock the overlay
            model.overlay.camera.pos = scene.camera.pos
            model.overlay.camera.axis = scene.camera.axis
            model.overlay.camera.up = scene.camera.up

            rate(100)  # Keeps the scene running

    def update_spn_x(self, x):
        """Update solar panel surface normal x component """
        self.solar_panel_surface_normal_vector.x = x

    def update_spn_y(self, y):
        """Update solar panel surface normal x component """
        self.solar_panel_surface_normal_vector.y = y

    def update_spn_z(self, z):
        """Update solar panel surface normal x component """
        self.solar_panel_surface_normal_vector.z = z

def run_test(experiment):
    # Create sunray objects
    sunray_0 = Sunlight()
    sunray_down = Sunlight(10, np.array([0, 0, -1]))
    sunray_bottom_right = Sunlight(10, np.array([1, 0, -1]))
    sunray_top_right = Sunlight(10, np.array([1, 0, 1])) # sun on other side of planet? maybe??

    # Create solar panel objects
    #square_panel = SolarPanelSquare(10, np.array([0, 1, 1]), 0.5)
    long_panel = SolarPanelRectangle(20, 5, 0.5, np.array([0, 1, 1]))
    square_panel = SolarPanelRectangle(10, 10, 0.5, np.array([0, 1, 1]))
    circle_panel = SolarPanelCircle(5, 0.5, np.array([1, 1, 1]))

    match experiment:
        case 1:
            sim = Simulation(sunray_down, square_panel) # Create simulation

            square_panel.print()
            print(f"Angle in radians: {sim.get_angle_radians():.2f}")
            print(f"Angle in degrees: {sim.get_angle_degrees():.2f}°")
            print(f"Total Electricity: {sim.get_electricity() + 0.0:.2f} W") # normalize negative zero to positive zero by adding 0.0
            print()

            sim.graph_vector_representation()
        case 2:
            sim = Simulation(sunray_bottom_right, long_panel)

            long_panel.print()
            print(f"Angle in radians: {sim.get_angle_radians():.2f}")
            print(f"Angle in degrees: {sim.get_angle_degrees():.2f}°")
            print(f"Total Electricity: {sim.get_electricity() + 0.0:.2f} W")
            print()
            sim.graph_vector_representation()
        case 3:
            sim = Simulation(sunray_down, circle_panel)

            circle_panel.print()
            print(f"Angle in radians: {sim.get_angle_radians():.2f}")
            print(f"Angle in degrees: {sim.get_angle_degrees():.2f}°")
            print(f"Total Electricity: {sim.get_electricity() + 0.0:.2f} W")
            print()
            sim.graph_vector_representation()

def end_sim():
    global RUNNING
    RUNNING = False

if __name__ == '__main__':
    run_test(1)