import numpy as np
from vpython import *

def normalize_vector(vector):
    """Returns a normalized vector given a vector."""
    norm = np.linalg.norm(vector)
    if norm != 0:
        return vector / norm
    return vector

def convert_vectors(x, y, z):
    """Convert object with type np.array from numpy to object with type vector from vpython."""
    vec_x = x
    vec_y = z
    vec_z = -y
    return vector(vec_x, vec_y, vec_z)