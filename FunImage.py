from SimpleImage import (read_image, write_image, get_width, get_height)
import random
from math import (sin, cos, sqrt, radians, trunc)
from functools import partial

BLACK = 0
WHITE = 255

class Function(object):
    def __init__(self, function):
        self.function = function

    # f >> g == \x -> g(f(x))
    def __rshift__(self, other_function):
        return Function(lambda x: other_function(self.function(x)))

    # f << g == \x -> f(g(x))
    def __lshift__(self, other_function):
        return Function(lambda x: self.function(other_function(x)))

    def __call__(self, x):
        return self.function(x)

# example images

def constant_image(intensity):
    return lambda x, y: intensity

black_image = constant_image(BLACK)
white_image = constant_image(WHITE)

def random_image(x, y):
    return random.randint(0, 255)

def grid(x_line_thick, y_line_thick, grid_width, grid_height):
    def this_image(x, y):
        if x % grid_width < x_line_thick or y % grid_height < y_line_thick:
            return BLACK
        else:
            return WHITE
    return this_image

def mandelbrot(x, y):
    z = complex(0.0, 0.0)
    complex_point = complex(x, y) 
    for iteration_number in range(255):
        # absolute value of a complex number is the distance from the origin
        # to the number in the complex plane
        if abs(z) >= 2.0:
            return iteration_number
        else:
            z = z * z + complex_point 
    return BLACK 

# transformations

def invert(image):
    return lambda x, y: WHITE - image(x, y)

def translate(x_delta, y_delta, image):
    return lambda x, y: image(x - x_delta, y - y_delta)

def scale_at_origin(x_scale, y_scale, image):
    return lambda x, y: image(x / x_scale, y / y_scale)

# translate image to origin, perform transformation, translate back again
def at_point(point_x, point_y, transform, image):
    at_origin = translate(-point_x, -point_y, image)
    transformed = transform(at_origin)
    return translate(point_x, point_y, transformed)

def scale_at_point(point_x, point_y, x_scale, y_scale, image):
    return at_point(point_x, point_y, partial(scale_at_origin, x_scale, y_scale), image)

def rotate_at_origin(angle_degrees, image):
    angle_radians = radians(angle_degrees)
    def this_image(x, y):
        rot_x = x * cos(angle_radians) - y * sin(angle_radians)
        rot_y = x * sin(angle_radians) + y * cos(angle_radians)
        return image(rot_x, rot_y)
    return this_image

def rotate_at_point(point_x, point_y, angle_degrees, image):
    return at_point(point_x, point_y, partial(rotate_at_origin, angle_degrees), image)

def ripple(image):
    def this_image(x, y):
        distance = sqrt(x * x + y * y)
        scale = cos(radians(distance)) * 20 
        if x <= 0:
            new_x = x - scale
        else:
            new_x = x + scale
        if y <= 0:
            new_y = y - scale
        else:
            new_y = y + scale
        return image(new_x, new_y)
    return this_image

def edge_detect(threshold, image):
    def this_image(x, y):
        gradient_vertical = \
            image(x - 1, y + 1) + 2 * image(x, y + 1) + image(x + 1, y + 1) \
            - image(x - 1, y - 1) - 2 * image(x, y - 1) - image(x + 1, y - 1)
        gradient_horizontal = \
            image(x + 1, y - 1) + 2 * image(x + 1, y) + image(x + 1, y + 1) \
            - image(x - 1, y - 1) - 2 * image(x - 1, y) - image(x - 1, y + 1)
        gradient_magnitute = sqrt(gradient_vertical ** 2 + gradient_horizontal ** 2)
        if gradient_magnitute > threshold:
            return WHITE 
        else:
            return BLACK 
    return this_image

# convert image to grid of pixels

def rasterise(top_left_x, top_left_y, bottom_right_x, bottom_right_y, image_fun):
    rows = []
    for y in range(top_left_y, bottom_right_y - 1, -1):
        this_row = []
        for x in range(top_left_x, bottom_right_x + 1, 1):
            pixel = image_fun(x, y)
            this_row.append(pixel)
        rows.append(this_row)
    return rows

# read frim a file to an image

def from_raster(raster, tile=False):
    width = get_width(raster)
    height = get_height(raster)
    def this_image(x, y):
        x = trunc(x)
        y = trunc(y)
        if tile:
            x = x % width
            y = y % height
        if tile or ((0 <= x < width) and (0 <= y < height)):
            col = x
            row = (height - y) - 1
            return raster[row][col]
        else:
            return BLACK
    return (this_image, width, height)

# demos

def demo1():
    raster = read_image("images/floyd.png")
    image, width, height = from_raster(raster, tile=True)
    image = scale_at_origin(0.3, 0.3, image)
    raster = rasterise(0, height*2, width*2, 0, image)
    write_image(raster, "tiled_floyd.png")

def demo2():
    transform = Function(partial(scale_at_point, -0.7487666666666666, 0.107017, 1000000, 1000000)) >> \
                Function(invert) >> \
                Function(partial(rotate_at_origin, 45))
    image = transform(mandelbrot)
    i = rasterise(-1000, 1000, 1000, -1000, image)
    write_image(i, "mandel.png")

def main():
    demo2()


if __name__ == '__main__':
    main()
