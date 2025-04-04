import numpy as np
from vpython import *
import os
import sys

from sunlight import Sunlight
from solar_panels import *
from graph3D import *


running = True
def end_sim():
    global running
    running = False

def restart_program():
    scene.delete()
    os.execl(sys.executable, sys.executable, *sys.argv)

class Simulation:
    def __init__(self, sunlight, solar_panel):
        self.sunlight = sunlight # sunlight vector
        # Convert np.array containing direction of sunlight to vector usable in vpython
        self.sun_vector = array_to_vector(*self.sunlight.direction)

        self.solar_panel = solar_panel # solar panel vector
        # Direction that the solar panel is facing in vector form
        self.solar_panel_surface_normal_vector = array_to_vector(*self.solar_panel.surface_normal)

        self.magnitude = sunlight.magnitude * solar_panel.area
        self.dot_product = np.clip(np.dot(sunlight.direction, solar_panel.surface_normal), -1.0, 1.0)
        self.electricity = self.get_electricity() # Store value for total electricity collected by solar panel

        self.model = Graph3D(1000, 800) # Set up scene


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
        # Store original values for x y z for reset button
        self.orig_xyz = vector(self.solar_panel_surface_normal_vector.x,self.solar_panel_surface_normal_vector.y,self.solar_panel_surface_normal_vector.z)

        '''Draw the sun'''
        #TODO sun is coded to be above in this scene, need way to customize it. Idea: position of sun based on vector, use moon model if light intensity goes below certain value
        sun_height = 4.5 # scale
        sun = sphere(canvas=scene, pos=(self.model.unit_vectors[2] * sun_height), radius=0.2, color=color.yellow, emmissive=True)
        sun2 = sphere(canvas=scene, pos=sun.pos, radius=0.3, color=color.yellow,emmissive=True, opacity=0.6)
        sun3 = sphere(canvas=scene, pos=sun.pos, radius=0.5, color=color.yellow,emmissive=True, opacity=0.2)

        '''Draw the sun arrow'''
        # Draw arrow from sun sphere
        sun_arrow = arrow(canvas=scene, pos=sun.pos, axis=self.sun_vector, color=color.yellow)
        # Label the sun vector
        label(canvas=scene, pos=(sun.pos + self.sun_vector), text=', '.join(f"{x:.2f}" for x in self.sunlight.direction), color=color.yellow, box=False)

        '''Draw the solar panel plane'''
        solar_c = 0.25 # scale l w h for rectangular solar panels
        if self.solar_panel.name == "Square" or self.solar_panel.name == "Rectangle":
            self.solar_panel_plane = box(canvas=scene,pos=self.model.origin, length = solar_c*self.solar_panel.length, width = solar_c*self.solar_panel.width, height = solar_c*self.solar_panel.height, color=color.white, opacity = 0.65)
        elif self.solar_panel.name == "Circle":
            self.solar_panel_plane = cylinder(canvas=scene,pos=self.model.origin,radius=solar_c*self.solar_panel.radius, axis=vector(0,0.1,0))
        else:
            raise RuntimeError("Solar Panel not valid.")

        '''Draw the solar panel arrow and align it to the plane'''
        # Draw arrow for surface normal
        self.solar_panel_surface_normal_arrow = arrow(canvas=scene, pos=self.model.origin, axis=self.solar_panel_surface_normal_vector, color=color.white)
        # Label the surface normal vector
        self.solar_panel_label = label(canvas=scene, pos=(self.model.origin + self.solar_panel_surface_normal_vector) * 1.2, text=', '.join(f"{x:.2f}" for x in self.solar_panel.surface_normal), color=color.white, box=False)

        # Rotate solar panel plane to align with its solar panel
        self.align_plane_to_normal(vector(0,1,0))

        '''Labels'''
        # Add Label displaying total electricity
        #self.electricity_label = label(canvas=scene, pos = vector(-1,-2,0), text =f"Electricity: {self.electricity + 0.0:.2f} W", height = 25, box = True)

        '''Buttons'''
        # Create separate overlay for buttons and sliders
        controls = canvas(width = 0, height = 0, background=color.black)
        controls.align = "right"
        controls.append_to_caption("\n    ")

        # Buttons to end and restart simulation
        btn_end = button(canvas=controls, text="End simulation", bind=lambda _: end_sim(), color=color.red)
        btn_restart = button(canvas=controls, text="Restart simulation", bind=lambda _: restart_program(), color=color.blue)

        controls.append_to_caption("\n\n    ")

        # Add button displaying total electricity, no other function
        self.electricity_label = button(canvas=controls, text =f"Electricity: {self.electricity + 0.0:.2f} W", bind=None)
        controls.append_to_caption("\n\n    ")

        # Add button to reset view
        btn_reset_view = button(canvas=controls, text="Reset view", bind=lambda _: self.model.reset_view())
        btn_reset_orientation = button(canvas=controls, text="Reset orientation", bind=lambda _: self.reset_orientation())

        '''Sliders'''
        # TODO need to add textbox and angle (degree) controls for vectors. Allow rotation from -180 to 180 degrees.
        # Sliders to control orientation of the solar panel
        limit_magnitude = 2
        controls.append_to_caption("\n\n    Rotate X Axis")
        self.slider_spn_x = slider(min=-limit_magnitude, max=limit_magnitude, length=500, value = np.clip(self.solar_panel_surface_normal_vector.x,-1,1), bind= self.update_spn_x)
        #slider_spn_x = slider(min=-180, max=180, length=360, value=0, bind=self.rotate_around_y) #TODO doesn't work properly
        controls.append_to_caption("\n\n    ")
        controls.append_to_caption("\n\n    Rotate Y Axis")
        self.slider_spn_y = slider(min=-limit_magnitude, max=limit_magnitude, length=500, value = np.clip(-self.solar_panel_surface_normal_vector.z,-1,1), bind= self.update_spn_y)
        controls.append_to_caption("\n\n    ")
        controls.append_to_caption("\n\n    Rotate Z Axis")
        self.slider_spn_z = slider(min=-limit_magnitude, max=limit_magnitude, length=500, value=np.clip(self.solar_panel_surface_normal_vector.y,-1,1), bind=self.update_spn_z)


        scene.userzoom = False
        scene.userpan = False

        # Lock the overlay to the main scene
        self.model.overlay.camera.pos = scene.camera.pos
        self.model.overlay.camera.axis = scene.camera.axis
        self.model.overlay.camera.up = scene.camera.up

        while running:
            # Lock the overlay to the main scene
            self.model.overlay.camera.pos = scene.camera.pos
            self.model.overlay.camera.axis = scene.camera.axis
            self.model.overlay.camera.up = scene.camera.up

            rate(1000)  # Keeps the scene running

    def align_plane_to_normal(self, original_normal):
        """Update the alignment of the solar panel object based on the surface normal vector."""
        rotation_axis = cross(original_normal, self.solar_panel_surface_normal_vector)
        if mag(rotation_axis) > 1e-6:
            rotation_angle = diff_angle(original_normal, self.solar_panel_surface_normal_vector)
            self.solar_panel_plane.rotate(angle=rotation_angle, axis=rotation_axis, origin=vector(0, 0, 0))

    def reset_orientation(self):
        # Get original orientation
        original_orientation = vector(self.solar_panel_surface_normal_vector.x,self.solar_panel_surface_normal_vector.y,self.solar_panel_surface_normal_vector.z)

        # Reset surface normal vector and arrow
        self.solar_panel.surface_normal = vector_to_array(self.orig_xyz.x,self.orig_xyz.y,self.orig_xyz.z)
        # Normalize np.array
        self.solar_panel.surface_normal = normalize_vector(self.solar_panel.surface_normal)
        # Update vector
        self.solar_panel_surface_normal_vector = array_to_vector(*self.solar_panel.surface_normal)

        # Update arrow orientation and label text
        self.solar_panel_surface_normal_arrow.axis = self.solar_panel_surface_normal_vector
        self.solar_panel_label.text = ', '.join(f"{x:.2f}" for x in self.solar_panel.surface_normal)

        # Rotate solar panel orientation
        self.align_plane_to_normal(original_orientation)

        # Reset sliders
        self.slider_spn_x.value = self.solar_panel_surface_normal_vector.x
        self.slider_spn_y.value = -self.solar_panel_surface_normal_vector.z
        self.slider_spn_z.value = self.solar_panel_surface_normal_vector.y

        # Update values for electricity
        self.dot_product = np.clip(np.dot(self.sunlight.direction, self.solar_panel.surface_normal), -1.0, 1.0)
        self.electricity = self.get_electricity()
        self.electricity_label.text = f"Electricity: {self.electricity + 0.0:.2f} W"

    def rotate_around_y(self, angle):
        previous_x = vector(self.solar_panel_surface_normal_vector.x,self.solar_panel_surface_normal_vector.y,self.solar_panel_surface_normal_vector.z)
        self.solar_panel_surface_normal_arrow.rotate(angle=radians(angle.value), axis=vector(0, 0, -1), origin=self.model.origin)
        self.align_plane_to_normal(previous_x)

    def update_solar_panel_normal(self, axis, component):
        """Update solar panel surface normal z component """
        previous_vector = vector(self.solar_panel_surface_normal_vector.x, self.solar_panel_surface_normal_vector.y,self.solar_panel_surface_normal_vector.z)
        self.solar_panel.surface_normal[axis] = component.value
        # Normalize np.array
        self.solar_panel.surface_normal = normalize_vector(self.solar_panel.surface_normal)
        # Update vector
        self.solar_panel_surface_normal_vector = array_to_vector(*self.solar_panel.surface_normal)

        # Update other two sliders
        if axis == 0:
            self.slider_spn_y.value = -self.solar_panel_surface_normal_vector.z
            self.slider_spn_z.value = self.solar_panel_surface_normal_vector.y
        elif axis == 1:
            self.slider_spn_x.value = self.solar_panel_surface_normal_vector.x
            self.slider_spn_z.value = self.solar_panel_surface_normal_vector.y
        elif axis == 2:
            self.slider_spn_x.value = self.solar_panel_surface_normal_vector.x
            self.slider_spn_y.value = -self.solar_panel_surface_normal_vector.z

        # Update arrow orientation and label text
        self.solar_panel_surface_normal_arrow.axis = self.solar_panel_surface_normal_vector
        self.solar_panel_label.text = ', '.join(f"{x:.2f}" for x in self.solar_panel.surface_normal)

        # Rotate solar panel orientation
        self.align_plane_to_normal(previous_vector)

        # Update values for electricity
        self.dot_product = np.clip(np.dot(self.sunlight.direction, self.solar_panel.surface_normal), -1.0, 1.0)
        self.electricity = self.get_electricity()
        self.electricity_label.text = f"Electricity: {self.electricity + 0.0:.2f} W"

    def update_spn_x(self, x):
        """Update solar panel surface normal x component."""
        self.update_solar_panel_normal(0, x)

    def update_spn_y(self, y):
        """Update solar panel surface normal y component."""
        self.update_solar_panel_normal(1, y)

    def update_spn_z(self, z):
        """Update solar panel surface normal z component """
        self.update_solar_panel_normal(2, z)

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
        case 3:
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
    run_test(5)