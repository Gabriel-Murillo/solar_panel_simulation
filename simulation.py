from string import whitespace

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
        self.sun_pos_radius = 6

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
        scene.visible = False  # display nothing

        # Store original values for x y z for reset button
        self.orig_xyz = vector(self.solar_panel_surface_normal_vector.x,self.solar_panel_surface_normal_vector.y,self.solar_panel_surface_normal_vector.z)

        '''Draw the sun'''
        #TODO sun is coded to be above in this scene, need way to customize it. use moon model if light intensity goes below certain value
        sun_pos = self.get_sun_pos()
        sun = sphere(canvas=scene, pos=sun_pos, radius=0.2, color=color.yellow, emissive=True)
        sun2 = sphere(canvas=scene, pos=sun.pos, radius=0.3, color=color.yellow, opacity=0.6, emissive=True)
        sun3 = sphere(canvas=scene, pos=sun.pos, radius=0.5, color=color.yellow, opacity=0.1, emissive=True)

        '''Draw the sun arrow'''
        # Draw arrow from sun sphere
        sun_arrow = arrow(canvas=scene, pos=sun.pos, axis=self.sun_vector*0.9, color=color.yellow, emissive=True, shaftwidth=0.08, round = True)
        # Label the sun vector
        label(canvas=scene, pos=(sun.pos + self.sun_vector*1.5), text=', '.join(f"{x:.2f}" for x in self.sunlight.direction), color=color.yellow, box=False)

        '''Draw the solar panel plane'''
        solar_c = 0.25 # scale l w h for rectangular solar panels
        top_panel_scale = 1.05
        if self.solar_panel.name == "Square" or self.solar_panel.name == "Rectangle":
            solar_panel_box = box(canvas=scene,pos=self.model.origin, length = solar_c*self.solar_panel.length*top_panel_scale, width = solar_c*self.solar_panel.width*top_panel_scale, height = solar_c*self.solar_panel.height,color=color.black)
            solar_panel_texture = box(canvas=scene,pos=solar_panel_box.pos+vector(0,0.02,0), length = solar_c*self.solar_panel.length, width = solar_c*self.solar_panel.width, height = 0.1, color=color.white)
            scene.select()
            self.solar_panel_plane = compound([solar_panel_texture, solar_panel_box],texture="textures/SolarPanel002_1K-JPG_Color.jpg", shininess=1)
        elif self.solar_panel.name == "Circle":
            solar_panel_disk = cylinder(canvas=scene,pos=self.model.origin,radius=solar_c*self.solar_panel.radius*top_panel_scale, axis=solar_c*vector(0,self.solar_panel.height,0), color=color.black)
            solar_panel_texture = cylinder(canvas=scene, pos=solar_panel_disk.pos + vec(0, 0.04, 0),radius=solar_c*self.solar_panel.radius, axis=vector(0,0.06,0), color=color.white)
            scene.select()
            self.solar_panel_plane = compound([solar_panel_texture, solar_panel_disk], texture="textures/SolarPanel002_1K-JPG_Color.jpg", shininess=1)



        '''Draw the solar panel arrow and align it to the plane'''
        # Draw arrow for surface normal
        self.solar_panel_surface_normal_arrow = arrow(canvas=scene, pos=self.model.origin, axis=self.solar_panel_surface_normal_vector*0.9, color=color.white, shaftwidth=0.08, round = True, emissive=True)
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
        #controls.align = "right"
        controls.append_to_caption("\n    ")

        # Add wtext displaying instructions
        self.instructions_label = wtext(canvas=controls, text="To rotate \"camera\", drag with right button or Ctrl-drag.\n    Touch screen: pinch/extend to zoom.")
        controls.append_to_caption("\n\n    ")

        # Buttons to end and restart simulation
        btn_end = button(canvas=controls, text="  END  ", bind=lambda _: end_sim(), background=color.white)
        controls.append_to_caption(" "*5)
        btn_restart = button(canvas=controls, text="RESTART", bind=lambda _: restart_program(), background=color.white)

        controls.append_to_caption("\n\n\n    ")

        # Add wtext displaying total electricity
        self.electricity_label = wtext(canvas=controls, text =f"Electricity: {self.electricity + 0.0:.2f} Watts")
        controls.append_to_caption("\n\n    ")
        # Add wtext displaying distance between Earth and Sun
        self.distance_label = wtext(canvas=controls, text="Distance from Sun: 1.5 * 10¹¹ meters")
        controls.append_to_caption("\n\n    ")
        # Add wtext displaying solar panel dimensions
        if self.solar_panel.name == "Square" or self.solar_panel.name == "Rectangle":
            # Add wtext displaying length, width, and height
            self.length_label = wtext(canvas=controls, text=f"Solar Panel Length: {self.solar_panel.length} meters")
            controls.append_to_caption("\n\n    ")
            self.width_label = wtext(canvas=controls, text=f"Solar Panel Width: {self.solar_panel.width} meters")
            controls.append_to_caption("\n\n    ")
            self.height_label = wtext(canvas=controls, text=f"Solar Panel Height: {self.solar_panel.height} meters")
            controls.append_to_caption("\n\n    ")
        elif self.solar_panel.name == "Circle":
            self.length_label = wtext(canvas=controls, text=f"Solar Panel Radius: {self.solar_panel.radius} meters")
            controls.append_to_caption("\n\n    ")
            self.height_label = wtext(canvas=controls, text=f"Solar Panel Height: {self.solar_panel.height} meters")
            controls.append_to_caption("\n\n    ")

        # Add button to reset view
        btn_reset_view = button(canvas=controls, text="Reset view", bind=lambda _: self.model.reset_view())
        controls.append_to_caption(" "*5)
        btn_reset_orientation = button(canvas=controls, text="Reset orientation", bind=lambda _: self.reset_orientation())

        '''Sliders'''
        # TODO add buttons to the left and right to increase and decrease value without needing to slide
        # Sliders to control orientation of the solar panel
        limit_magnitude = 1
        ds = 20
        slider_length = 700 # sets the slider's length TODO need to scale this to the width of the simulation
        controls.append_to_caption("\n\n\n    Solar Panel")
        controls.append_to_caption("\n\n    Rotate Y Axis (X) ")
        button(canvas=controls, text="-", bind= lambda _:self.update_spn_x_btn(self.solar_panel_surface_normal_vector.x - limit_magnitude/ds))
        self.slider_spn_x = slider(canvas=controls,min=-limit_magnitude, max=limit_magnitude, step=limit_magnitude/ds, length=slider_length, value = np.clip(self.solar_panel_surface_normal_vector.x,-1,1), bind= self.update_spn_x)
        button(canvas=controls, text="+", bind= lambda _:self.update_spn_x_btn(self.solar_panel_surface_normal_vector.x + limit_magnitude/ds))

        #slider_spn_x = slider(min=-180, max=180, length=360, value=0, bind=self.rotate_around_y) #TODO doesn't work properly
        controls.append_to_caption("\n    ")
        controls.append_to_caption("\n\n    Rotate X Axis (Y) ")
        button(canvas=controls, text="-", bind= lambda _:self.update_spn_y_btn(-self.solar_panel_surface_normal_vector.z - limit_magnitude/ds))
        self.slider_spn_y = slider(canvas=controls,min=-limit_magnitude, max=limit_magnitude, step=limit_magnitude/ds,length=slider_length, value = np.clip(-self.solar_panel_surface_normal_vector.z,-1,1), bind= self.update_spn_y)
        button(canvas=controls, text="+",bind=lambda _: self.update_spn_y_btn(-self.solar_panel_surface_normal_vector.z + limit_magnitude / ds))

        controls.append_to_caption("\n    ")
        controls.append_to_caption("\n\n                   Tilt (Z) ")
        button(canvas=controls, text="-", bind=lambda _: self.update_spn_z_btn(self.solar_panel_surface_normal_vector.y - limit_magnitude / ds))
        self.slider_spn_z = slider(canvas=controls,min=-limit_magnitude, max=limit_magnitude, step=limit_magnitude/ds,length=slider_length, value=np.clip(self.solar_panel_surface_normal_vector.y,-1,1), bind=self.update_spn_z)
        button(canvas=controls, text="+", bind=lambda _: self.update_spn_z_btn(self.solar_panel_surface_normal_vector.y + limit_magnitude / ds ))

        # only allow user to rotate their camera
        scene.autoscale = True
        scene.userzoom = False # prevent user from controlling zoom
        scene.userpan = False # prevent user from controlling the camera pan

        # Lock the overlay to the main scene
        self.model.overlay.camera.pos = scene.camera.pos
        self.model.overlay.camera.axis = scene.camera.axis
        self.model.overlay.camera.up = scene.camera.up

        '''Lighting'''
        scene.lights[0].direction = sun.pos
        scene.lights.pop() # remove distant light object

        intensity = 0.9
        scene.lights[0].color = color.white*intensity

        '''Display scene after loading textures'''
        scene.waitfor("textures")
        scene.visible = True  # now display everything
        '''As the program runs...'''
        while running:
            rate(60)  # Keeps the scene running

            # Lock the overlay to the main scene
            self.model.overlay.camera.pos = scene.camera.pos
            self.model.overlay.camera.axis = scene.camera.axis
            self.model.overlay.camera.up = scene.camera.up

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
        self.electricity_label.text = f"Electricity: {self.electricity + 0.0:.2f} Watts"

    def update_solar_panel_normal(self, axis, component, is_button=False):
        """Update solar panel surface normal z component """
        previous_vector = vector(self.solar_panel_surface_normal_vector.x, self.solar_panel_surface_normal_vector.y,self.solar_panel_surface_normal_vector.z)
        self.solar_panel.surface_normal[axis] = component
        # Normalize np.array
        self.solar_panel.surface_normal = normalize_vector(self.solar_panel.surface_normal)
        # Update vector
        self.solar_panel_surface_normal_vector = array_to_vector(*self.solar_panel.surface_normal)

        # Update arrow orientation and label text
        self.solar_panel_surface_normal_arrow.axis = self.solar_panel_surface_normal_vector
        self.solar_panel_label.text = ', '.join(f"{x:.2f}" for x in self.solar_panel.surface_normal)

        # Rotate solar panel orientation
        self.align_plane_to_normal(previous_vector)

        # Update values for electricity
        self.dot_product = np.clip(np.dot(self.sunlight.direction, self.solar_panel.surface_normal), -1.0, 1.0)
        self.electricity = self.get_electricity()
        self.electricity_label.text = f"Electricity: {self.electricity + 0.0:.2f} Watts"

        # Update other two sliders
        self.update_sliders(axis, is_button)

    def update_spn_x(self, x):
        """Update solar panel surface normal x component."""
        self.update_solar_panel_normal(0, x.value)

    def update_spn_x_btn(self, x):
        """Update solar panel surface normal x component."""
        self.update_solar_panel_normal(0, x, True)

    def update_spn_y(self, y):
        """Update solar panel surface normal y component."""
        self.update_solar_panel_normal(1, y.value)

    def update_spn_y_btn(self, y):
        """Update solar panel surface normal x component."""
        self.update_solar_panel_normal(1, y, True)

    def update_spn_z(self, z):
        """Update solar panel surface normal z component """
        self.update_solar_panel_normal(2, z.value)

    def update_spn_z_btn(self, z):
        """Update solar panel surface normal x component."""
        self.update_solar_panel_normal(2, z, True)

    def update_sliders(self, axis, is_button):
        if is_button:
            if axis == 0:
                self.slider_spn_x.value = self.solar_panel_surface_normal_vector.x
                self.slider_spn_y.value = -self.solar_panel_surface_normal_vector.z
                self.slider_spn_z.value = self.solar_panel_surface_normal_vector.y
            elif axis == 1:
                self.slider_spn_x.value = self.solar_panel_surface_normal_vector.x
                self.slider_spn_y.value = -self.solar_panel_surface_normal_vector.z
                self.slider_spn_z.value = self.solar_panel_surface_normal_vector.y
            elif axis == 2:
                self.slider_spn_x.value = self.solar_panel_surface_normal_vector.x
                self.slider_spn_y.value = -self.solar_panel_surface_normal_vector.z
                self.slider_spn_z.value = self.solar_panel_surface_normal_vector.y
        else:
            if axis == 0:
                self.slider_spn_y.value = -self.solar_panel_surface_normal_vector.z
                self.slider_spn_z.value = self.solar_panel_surface_normal_vector.y
            elif axis == 1:
                self.slider_spn_x.value = self.solar_panel_surface_normal_vector.x
                self.slider_spn_z.value = self.solar_panel_surface_normal_vector.y
            elif axis == 2:
                self.slider_spn_x.value = self.solar_panel_surface_normal_vector.x
                self.slider_spn_y.value = -self.solar_panel_surface_normal_vector.z

    def get_sun_pos(self):
        """Convert unit vector to position on sphere for sun position coordinates."""
        direction = self.sunlight.direction # get normalized vector direction
        radius = self.sun_pos_radius

        # Scale direction vector to get position on the sphere
        sun_pos = vector(-direction[0] * radius, -direction[2] * radius, direction[1] * radius)

        return sun_pos



def run_test(experiment):
    # Create sunray objects
    sunray_0 = Sunlight() # New moon
    sunray_down = Sunlight(10, np.array([0, 0, -1]))
    sunray_bottom_right = Sunlight(10, np.array([1, 0, -1]))
    sunray_top_right = Sunlight(10, np.array([1, 0, 1])) # unphysical
    sunray_along_x = Sunlight(10, np.array([1, 0, 0])) # unphysical

    match experiment:
        case 1: # Sun points down, solar panel points up. Basic example.
            square_panel = SolarPanelRectangle(10, 10, 0.25, np.array([0.1, 0.1, 1]))
            sim = Simulation(sunray_down, square_panel) # Create simulation

            sim.graph_vector_representation()
        case 2: # Rectangular solar panel.
            long_panel = SolarPanelRectangle(20, 5, 0.25, np.array([0.1, 1, 1]))
            sim = Simulation(sunray_bottom_right, long_panel)

            sim.graph_vector_representation()
        case 3: # Circular solar panel.
            circle_panel = SolarPanelCircle(5, 0.25, np.array([0.1, -0.1, 1]))
            sim = Simulation(sunray_down, circle_panel)

            sim.graph_vector_representation()
        case 4:
            # Test that changing x for solar panel will change value for electricity
            square_panel = SolarPanelRectangle(10, 10, 0.25, np.array([0, 1, 1]))
            sim = Simulation(sunray_along_x, square_panel)  # Create simulation

            sim.graph_vector_representation()
        case 5:
            square_panel = SolarPanelRectangle(10, 10, 0.25, np.array([0, 0, 1]))
            sim = Simulation(sunray_down, square_panel)  # Create simulation

            sim.graph_vector_representation()
        case 6:
            square_panel = SolarPanelRectangle(10, 10, 0.25, np.array([0.1, 1, 0]))
            sim = Simulation(sunray_down, square_panel)  # Create simulation

            sim.graph_vector_representation()
        case 7:
            sunray = Sunlight(10, np.array([-1, 0.5, 1]))  # unphysical
            square_panel = SolarPanelRectangle(10, 10, 0.25, np.array([0, 0, 1]))
            sim = Simulation(sunray, square_panel)  # Create simulation

            sim.graph_vector_representation()

if __name__ == '__main__':
    run_test(4)