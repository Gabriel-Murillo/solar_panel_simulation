from vpython import *

class Graph3D:
    def __init__(self, width=800, height=600):
        self.origin = vector(0,0,0)

        # Set the scene
        scene.width = width
        scene.height = height
        scene.background = color.black
        scene.userzoom = False

        scene.center = self.origin # center the view
        scene.range = 6 # Zoom level (smaller = more zoom)

        # Define unit vectors
        i = arrow(pos=self.origin, axis=vector(1, 0, 0), color=color.red)
        j = arrow(pos=self.origin, axis=vector(0, 0, -1), color=color.blue)
        k = arrow(pos=self.origin, axis=vector(0, 1, 0), color=color.green)
        self.unit_vectors = [i.axis, j.axis, k.axis]

        # Label unit vectors
        label(pos=i.axis * 1.1, text='X', color=color.red, box=False)
        label(pos=j.axis * 1.1, text='Y', color=color.blue, box=False)
        label(pos=k.axis * 1.1, text='Z', color=color.green, box=False)

        # Get isometric view:
        self._isometric_view()

    def _isometric_view(self):
        """Get an isometric view."""
        # 1. Rotate around X by -45 degrees
        scene.camera.rotate(angle=radians(-45), axis=self.unit_vectors[0], origin=self.origin)
        scene.center = vector(0, 0, 0)  # center of view
        # 2. Rotate around Z by 45 degrees
        scene.camera.rotate(angle=radians(45), axis=self.unit_vectors[2], origin=self.origin)
        scene.center = vector(0, 0, 0)  # center of view

    def _undo_isometric_view(self):
        """Undo the isometric view."""
        # 2. Rotate around Z by -45 degrees
        scene.camera.rotate(angle=radians(-45), axis=self.unit_vectors[2], origin=self.origin)
        scene.center = vector(0, 0, 0)  # center the view
        # 1. Rotate around X by 45 degrees
        scene.camera.rotate(angle=radians(45), axis=self.unit_vectors[0], origin=self.origin)
        scene.center = vector(0, 0, 0)  # center the view


