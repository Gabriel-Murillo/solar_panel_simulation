import numpy as np
from vpython import *

from sunlight import Sunlight
from solar_panels import *
from graph3D import *
import sys

running = True
def end_sim():
    global running
    running = False

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
        """Create simulation for flat solar panels. TODO complete description"""
        model = Graph3D(1000, 800) # Set up scene

        '''Draw the sun'''
        #TODO sun is coded to be above in this scene, need way to customize it
        sun_height = 4.5 # scale
        sun = sphere(canvas=scene, pos=(model.unit_vectors[2] * sun_height), radius=0.2, color=color.yellow, emmissive=True)

        '''Draw the sun arrow'''
        # Convert np.array containing direction of sunlight to vector usable in vpython
        sun_vector = array_to_vector(*self.sunlight.direction)
        # Draw arrow from sun sphere
        sun_arrow = arrow(canvas=scene, pos=sun.pos, axis=sun_vector, color=color.yellow)
        # Label the sun vector
        label(canvas=scene, pos=(sun.pos + sun_vector), text=', '.join(f"{x:.2f}" for x in self.sunlight.direction), color=color.yellow, box=False)

        '''Draw the solar panel plane'''
        # TODO draw circles
        solar_c = 0.25 # scale l w h for rectangular solar panels
        if self.solar_panel.name == "Square" or self.solar_panel.name == "Rectangle":
            self.solar_panel_plane = box(canvas=scene,pos=model.origin, length = solar_c*self.solar_panel.length, width = solar_c*self.solar_panel.width, height = solar_c*self.solar_panel.height, color=color.white, opacity = 0.65)
        elif self.solar_panel.name == "Circle":
            self.solar_panel_plane = cylinder(canvas=scene,pos=model.origin,radius=solar_c*self.solar_panel.radius, axis=vector(0,0.1,0))
        else:
            exit("No valid solar panel object.")
        '''Draw the solar panel arrow and align it to the plane'''
        # Direction that the solar panel is facing in vector form
        self.solar_panel_surface_normal_vector = array_to_vector(*self.solar_panel.surface_normal)
        # Draw arrow for surface normal
        self.solar_panel_surface_normal_arrow = arrow(canvas=scene, pos=model.origin, axis=self.solar_panel_surface_normal_vector, color=color.white)
        # Label the surface normal vector
        self.solar_panel_label = label(canvas=scene, pos=(model.origin + self.solar_panel_surface_normal_vector) * 1.2, text=', '.join(f"{x:.2f}" for x in self.solar_panel.surface_normal), color=color.white, box=False)

        # Rotate solar panel plane to align with its solar panel
        self.align_plane_to_normal(vector(0,1,0))

        '''Labels'''
        # Add Label displaying total electricity
        self.electricity = self.get_electricity()
        self.electricity_label = label(canvas=scene, pos = vector(-1,-2,0), text =f"Electricity: {self.electricity + 0.0:.2f} W", height = 25, box = True)

        '''Buttons'''
        # Add button to reset view
        btn_reset_view = button(canvas=scene, text="Reset view", bind=lambda _: model.reset_view(), right = 100)

        # Button to end simulation
        btn_end = button(canvas=scene, text="End simulation", bind=lambda _: end_sim(), right = 100)

        # Sliders to control orientation of the solar panel
        slider_spn_x = slider(min=-1.2, max=1.2, value = self.solar_panel_surface_normal_vector.x, bind= self.update_spn_x)

        scene.userzoom = False
        scene.userpan = False

        while running:
            # Lock the overlay to the main scene
            model.overlay.camera.pos = scene.camera.pos
            model.overlay.camera.axis = scene.camera.axis
            model.overlay.camera.up = scene.camera.up

            rate(60)  # Keeps the scene running

    def update_spn_x(self, x):
        """Update solar panel surface normal x component."""
        previous_x = vector(self.solar_panel_surface_normal_vector.x,self.solar_panel_surface_normal_vector.y,self.solar_panel_surface_normal_vector.z)
        self.solar_panel.surface_normal[0] = x.value
        # Normalize np.array
        self.solar_panel.surface_normal = normalize_vector(self.solar_panel.surface_normal)
        # Update vector
        self.solar_panel_surface_normal_vector = array_to_vector(*self.solar_panel.surface_normal)

        # Update arrow orientation and label text
        self.solar_panel_surface_normal_arrow.axis = self.solar_panel_surface_normal_vector
        self.solar_panel_label.text = ', '.join(f"{x:.2f}" for x in self.solar_panel.surface_normal)

        # Rotate solar panel orientation
        self.align_plane_to_normal(previous_x)

        self.dot_product = np.clip(np.dot(self.sunlight.direction, self.solar_panel.surface_normal), -1.0, 1.0)
        self.electricity = self.get_electricity()
        self.electricity_label.text = f"Electricity: {self.electricity + 0.0:.2f} W"

    def update_spn_y(self, y):
        """Update solar panel surface normal x component """
        self.solar_panel_surface_normal_vector.y = y

    def update_spn_z(self, z):
        """Update solar panel surface normal x component """
        self.solar_panel_surface_normal_vector.z = z

    def align_plane_to_normal(self, original_normal):
        rotation_axis = cross(original_normal, self.solar_panel_surface_normal_vector)
        if mag(rotation_axis) > 1e-6:
            rotation_angle = diff_angle(original_normal, self.solar_panel_surface_normal_vector)
            self.solar_panel_plane.rotate(angle=rotation_angle, axis=rotation_axis, origin=vector(0, 0, 0))

def run_test(experiment):
    # Create sunray objects
    sunray_0 = Sunlight() # New moon
    sunray_down = Sunlight(10, np.array([0, 0, -1]))
    sunray_bottom_right = Sunlight(10, np.array([1, 0, -1]))
    sunray_top_right = Sunlight(10, np.array([1, 0, 1])) # unphysical
    sunray_along_x = Sunlight(10, np.array([1, 0, 0])) # unphysical

    match experiment:
        case 1:
            square_panel = SolarPanelRectangle(10, 10, 0.5, np.array([0, 1, 1]))
            sim = Simulation(sunray_down, square_panel) # Create simulation

            print(f"Angle in radians: {sim.get_angle_radians():.2f}")
            print(f"Angle in degrees: {sim.get_angle_degrees():.2f}°")
            print(f"Total Electricity: {sim.get_electricity() + 0.0:.2f} W") # normalize negative zero to positive zero by adding 0.0
            print()

            sim.graph_vector_representation()
        case 2:
            long_panel = SolarPanelRectangle(20, 5, 0.5, np.array([0, 1, 1]))
            sim = Simulation(sunray_bottom_right, long_panel)

            sim.graph_vector_representation()
        case 3: # TODO AttributeError: 'SolarPanelCircle' object has no attribute 'length'
            circle_panel = SolarPanelCircle(5, 0.5, np.array([0, 0, 1]))
            sim = Simulation(sunray_down, circle_panel)

            sim.graph_vector_representation()
        case 4:
            # Test that changing x for solar panel will change value for electricity
            square_panel = SolarPanelRectangle(10, 10, 0.5, np.array([0, 1, 1]))
            sim = Simulation(sunray_along_x, square_panel)  # Create simulation

            sim.graph_vector_representation()
        case 5:
            square_panel = SolarPanelRectangle(10, 10, 0.5, np.array([0, 0, 1]))
            sim = Simulation(sunray_down, square_panel)  # Create simulation

            sim.graph_vector_representation()
        case 6:
            square_panel = SolarPanelRectangle(10, 10, 0.5, np.array([0, 1, 0]))
            sim = Simulation(sunray_down, square_panel)  # Create simulation

            sim.graph_vector_representation()

if __name__ == '__main__':
    run_test(3)