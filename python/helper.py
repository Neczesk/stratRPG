import math

def linearConversion(input, oldmin, oldmax, newmin, newmax):
	oldrange = oldmax - oldmin
	newrange = newmax - newmin
	if oldrange == 0:
		return input
	else:
		return (((input - oldmin) * newrange)/ oldrange) + newmin

def clamp(input, minval, maxval):
	if isinstance(input, complex):
		print(input)
	return max(minval, min(input, maxval))

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

	x = 0
	y = sizey

	

if __name__ == "__main__":
	print (linearConversion(110, 0, 100, 0, 10))