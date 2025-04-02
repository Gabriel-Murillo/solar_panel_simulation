import numpy as np
from vpython import *

def normalize_vector(vector):
    """Returns a normalized vector given a vector."""
    norm = np.linalg.norm(vector)
    if norm != 0:
        return vector / norm
    return vector

def array_to_vector(x, y, z):
    """Convert np.array from numpy to vector from vpython."""
    vec_x = x
    vec_y = z
    vec_z = -y
    return vector(vec_x, vec_y, vec_z)

def vector_to_array(x, y , z):
    """Convert vector from vpython to np.array from numpy."""
    vec_x = x
    vec_y = -z
    vec_z = y
    return np.array([vec_x, vec_y, vec_z])