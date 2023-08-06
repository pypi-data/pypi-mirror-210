from sdl.layers import Relu, Affine
import numpy as np


def test_Relu():
    relu = Relu()
    x = np.array([-1, 0, 1, 3])
    y = relu.forward(x)
    assert(np.array_equal(y, [0, 0, 1, 3]))

    back = relu.backward(np.array([-1, 0, 1, 3]))
    assert(np.array_equal(back, [0, 0, 1, 3]))

def test_Affine():
    affine = Affine(np.array([[1, 2], [1, 2], [1, 2]]), np.array([1, 1]))
    y = affine.forward(np.array([1, 2, 3]))
    assert(np.array_equal(y, [7, 13]))

# test_Relu()

test_Affine()
