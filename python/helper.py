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

if __name__ == "__main__":
	print (linearConversion(110, 0, 100, 0, 10))