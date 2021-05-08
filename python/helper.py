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

if __name__ == "__main__":
	print(get_ellipse_points((0,0), 20, 50))

