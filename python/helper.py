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

def subtile_to_tile(subtile, subtileratio) -> tuple:
	return (math.floor(subtile[0]/subtileratio), math.floor(subtile[1]/subtileratio))

if __name__ == "__main__":
	print(get_ellipse_points((0,0), 20, 50))

