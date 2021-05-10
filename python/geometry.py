import math
import queue
import numpy as np

def get_points_in_circle(center, radius):
    output = set()
    f = 1 - radius
    ddf_x = 1
    ddf_y = -2 * radius
    x = 0
    y = radius
    x0 = center[0]
    y0 = center[1]
    output.add((x0, y0 + radius))
    output.add((x0, y0 - radius))
    output.add((x0 + radius, y0))
    output.add((x0 - radius, y0))
 
    while x < y:
        if f >= 0: 
            y -= 1
            ddf_y += 2
            f += ddf_y
        x += 1
        ddf_x += 2
        f += ddf_x    
        output.add((x0 + x, y0 + y))
        output.add((x0 - x, y0 + y))
        output.add((x0 + x, y0 - y))
        output.add((x0 - x, y0 - y))
        output.add((x0 + y, y0 + x))
        output.add((x0 - y, y0 + x))
        output.add((x0 + y, y0 - x))
        output.add((x0 - y, y0 - x))

    return output

def polar_to_cartesian(magnitude, angle):
    x = magnitude * math.cos(angle)
    y = magnitude * math.sin(angle)
    return (x,y)

def add_coordinates(coord1, coord2):
    coord3 = (coord1[0] + coord2[0], coord1[1] + coord2[1])
    return coord3

def get_ellipse_points(origin, sizex, sizey) -> set:
    center_x = origin[0]
    center_y = origin[1]
    output = set()

    x = 0
    y = sizey

    d1 = math.pow(sizey,2) - (sizey * math.pow(sizex,2)) + (math.pow(sizex,2) * 0.25)
    dx = 2 * math.pow(sizey, 2) * x
    dy = 2 * math.pow(sizex, 2) * y

    while (dx < dy):
        output.add((x+center_x, y+center_y))
        # print((x+center_x, y+center_y))
        output.add((-x + center_x, y + center_y))
        output.add((x + center_x, -y + center_y))
        output.add((-x + center_x, -y + center_y))

        if (d1 < 0):
            x += 1
            dx = dx + (2 * math.pow(sizey, 2))
            d1 = d1 + dx + math.pow(sizey, 2)
            # print("east")
        else:
            x+=1
            y -= 1
            dx = dx + (2 * math.pow(sizey, 2))
            dy = dy - (2 * math.pow(sizex, 2))
            d1 = d1 + dx - dy + math.pow(sizey, 2)
            # print("southeast")

    d2 = ((math.pow(sizey,2) * math.pow(x+0.5, 2)) + (math.pow(sizex,2) \
        * math.pow(y-1, 2)) - (math.pow(sizex,2) * math.pow(sizey,2)))

    while (y >= 0):
        output.add((x+center_x, y+center_y))
        output.add((-x + center_x, y + center_y))
        output.add((x + center_x, -y + center_y))
        output.add((-x + center_x, -y + center_y))
        # print((x+center_x, y+center_y))

        if (d2 > 0):
            y -= 1
            dy = dy - (2 * math.pow(sizex,2))
            d2 = d2 + math.pow(sizex,2) - dy
            # print("south")
        else:
            y -= 1
            x +=1
            dx = dx + (2 * math.pow(sizey, 2))
            dy = dy - (2 * math.pow(sizex, 2))
            d2 = d2 + dx - dy + math.pow(sizex, 2)
            # print("southeast")

    return output

def get_line_points(start, destination) -> set:
    output = set()
    dx = abs(destination[0] - start[0])
    dy = abs(destination[1] - start[1])
    # print("started drawing line")

    x = start[0]
    y = start[1]

    sx = -1 if start[0] > destination[0] else 1
    sy = -1 if start[1] > destination[1] else 1

    if dx > dy:
        err = dx / 2.0
        while x != destination[0]:
            output.add((x,y))
            # print((x,y))
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
    else:
        err = dy / 2.0
        while y != destination[1]:
            output.add((x,y))
            # print((x,y))
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy
    output.add((x,y))
    return output

def subtile_to_tile(subtile, subtileratio) -> tuple:
    return (math.floor(subtile[0]/subtileratio), math.floor(subtile[1]/subtileratio))

def longest_distance_between_points(all_points) -> tuple:
    max_distance = 0
    point1 = (0,0)
    point2 = (0,0)
    for pointa in all_points:
        other_points = all_points.difference(pointa)
        for pointb in other_points:
            distance = math.sqrt(math.pow(pointb[0]-pointa[0],2) + math.pow(pointb[1] - pointa[1], 2))
            if distance > max_distance:
                max_distance = distance
                point1 = pointa
                point2 = pointb
    return (max_distance, point1, point2)

def distance_between_two_points(start, dest):
    return math.sqrt(math.pow(dest[0]-start[0],2) + math.pow(dest[1] - start[1], 2))

def get_points_inside_shape(boundary, center) -> set:
    output = set()
    q = queue.Queue()
    q.put(add_coordinates(center, (0,1)))
    q.put(add_coordinates(center, (1,0)))
    q.put(add_coordinates(center, (-1, 0)))
    q.put(add_coordinates(center, (0, -1)))

    while not q.empty():
        current = q.get()
        if current not in output and current not in boundary:
            output.add(current)
            q.put(add_coordinates(current, (0,1)))
            q.put(add_coordinates(current, (1,0)))
            q.put(add_coordinates(current, (-1, 0)))
            q.put(add_coordinates(current, (0, -1)))

    return output

def rotate_point(point, angle, center_point=(0, 0)):
    """Rotates a point around center_point(origin by default)
    Angle is in degrees.
    Rotation is counter-clockwise
    """
    angle_rad = math.radians(angle % 360)
    # Shift the point so that center_point becomes the origin
    new_point = (point[0] - center_point[0], point[1] - center_point[1])
    new_point = (new_point[0] * math.cos(angle_rad) - new_point[1] * math.sin(angle_rad),
                 new_point[0] * math.sin(angle_rad) + new_point[1] * math.cos(angle_rad))
    # Reverse the shifting we have done
    new_point = (new_point[0] + center_point[0], new_point[1] + center_point[1])
    new_point = (round(new_point[0]), round(new_point[1]))
    return new_point

def find_center_of_points(points) -> tuple:
    sumx = 0
    sumy = 0
    for point in points:
        sumx += point[0]
        sumy += point[1]
    return (round(sumx/len(points)), round(sumy/len(points)))

def rotate_shape(shape, angle) -> set:
    """This function rotates a shape around its center using the rotate_point function. Which I stole."""
    center = find_center_of_points(shape)
    output = set()
    for point in shape:
        output.add(rotate_point(point, angle, center))
    return output




def main():
    circle = get_points_in_circle((0,0), 20)
    fill = get_points_inside_shape(circle, (0,0))
    print(fill)

if __name__ == "__main__":
    main()