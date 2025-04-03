from vpython import *

class Graph3D:
    def __init__(self, width, height):
        # Define vector at origin
        self.origin = vector(0,0,0)

        # Set the main scene
        scene.width = width
        scene.height = height
        scene.background = color.black
        scene.center = self.origin # center the view
        scene.range = 6 # Zoom level (smaller = more zoom)

        # Create separate canvas for coordinates
        self.overlay = canvas(width = 200, height = 200, background=color.black)
        #self.overlay.visible = True
        #self.overlay.align = 'left'

        #self.overlay.append_to_caption('\n') # Adds space between main scene and overlay

        # Define unit vectors, assign them to overlay
        self.unit_vectors = [vector(1, 0, 0), vector(0, 0, -1), vector(0, 1, 0)]

        u = self.unit_vectors # keep names simple
        c = 3 # constant
        i = arrow(canvas=self.overlay, pos=self.origin, axis=c*u[0], color=color.red)
        j = arrow(canvas=self.overlay,pos=self.origin, axis=c*u[1], color=color.blue)
        k = arrow(canvas=self.overlay,pos=self.origin, axis=c*u[2], color=color.green)

        # Label unit vectors
        label(canvas=self.overlay,pos=i.axis, text='X', color=color.red, box=False)
        label(canvas=self.overlay,pos=j.axis, text='Y', color=color.blue, box=False)
        label(canvas=self.overlay,pos=k.axis, text='Z', color=color.green, box=False)

        # Initialize syncing, continue syncing in main loop (simulation.py)
        self.overlay.camera.pos = scene.camera.pos
        self.overlay.camera.axis = scene.camera.axis
        self.overlay.camera.up = scene.camera.up



    def _isometric_view(self):
        """Get an isometric view."""
        # 1. Rotate around X by -45 degrees
        scene.camera.rotate(angle=radians(-45), axis=self.unit_vectors[0], origin=self.origin)
        #scene.center = self.origin  # center of view
        # 2. Rotate around Z by 45 degrees
        scene.camera.rotate(angle=radians(45), axis=self.unit_vectors[2], origin=self.origin)
        scene.center = vector(0, 0, 0)  # center of view

    def _undo_isometric_view(self):
        """Undo the isometric view."""
        # 2. Rotate around Z by -45 degrees
        scene.camera.rotate(angle=radians(-45), axis=self.unit_vectors[2], origin=self.origin)
        scene.center = self.origin  # center the view
        # 1. Rotate around X by 45 degrees
        scene.camera.rotate(angle=radians(45), axis=self.unit_vectors[0], origin=self.origin)
        scene.center = vector(0, 0, 0)  # center the view

    def reset_view(self):
        scene.forward = vector(0, 0, -1)  # Camera direction
        scene.up = vector(0, 1, 0)  # Up direction
        scene.center = vector(0, 0, 0)  # Center of the view

