#Standard library
import math
import statistics
import random
import queue

#local imports
import wrappednoise
import helper
import db
import texgen

def generate_elevation_list(mapconfig, subtileratio) -> list:
	noise_config = wrappednoise.NoiseConfig(8, 0.01, 0.5, 0.5, 1)
	noise = wrappednoise.WrappedNoise(noise_config)
	# noise.conf.freq *= (1/subtileratio) #This should convert this to a subtile elevation list, which can then be averaged if needed for a tile elevation list
	output = list()
	for y in range(0,mapconfig.height*subtileratio):
		for x in range(0,mapconfig.width*subtileratio):
			percent = noise.noise_at_point(x, y)
			if percent > 1 or percent < -1:
				print("noise outside bounds")
			percent = helper.linearConversion(percent, -1, 1, 0, 100)
			output.append(percent)

	return output

def generate_tile_elevation_list(subtile_elevations, subtileratio) -> list:
	output = list()
	i = 0
	while i < len(subtile_elevations):
		k = i + int(math.pow(subtileratio, 2))
		next_tile = subtile_elevations[i:k]
		mean = statistics.mean(next_tile)
		output.append(mean)
		i += subtileratio

	return output


class continent:
	def __init__(self, origin):
		self.all_tiles = set()
		self.origin = origin
		self.all_tiles.add(origin)
		self.all_subtiles = set()
		self.boundary = set()

	def add_tile(self, new_tile):
		self.all_tiles.add(new_tile)

	def add_subtile(self, new_subtile):
		self.all_subtiles.add(new_subtile)

	def subtiles_to_tiles(self, subtileratio) -> set:
		tiles = set()
		for subtile in self.all_subtiles:
			new_tile = helper.subtile_to_tile(subtile, subtileratio)
			tiles.add(new_tile)

	def tiles_to_subtiles(self, subtileratio) -> set:
		subtiles = set()
		for tile in self.all_tiles:
			for y in range(subtileratio):
				for x in range(subtileratio):
					subtile = ((tile[0]*subtileratio + x),(tile[1]*subtileratio + y))
					subtiles.add(subtile)
		# print(len(self.all_tiles))
		# print(len(subtiles))
		# print(self.all_tiles)
		return subtiles

	def grow_continent(self, generations):
		for i in range(generations):
			new_tiles = set()
			for tile in self.all_tiles:
				for y in range(-1,2):
					for x in range(-1,2):
					# print("Checking: " + str(x) + ", " + str(y))
						if (tile[0]+x, tile[1]+y) != tile:
							new_tiles.add((tile[0]+x, tile[1]+y))
			self.all_tiles.update(new_tiles)

	def fill_continent(self):
		#Basic flood fill algorithm
		q = queue.Queue()
		start = self.origin
		q.put(helper.add_coordinates(start, (0,1)))
		q.put(helper.add_coordinates(start, (1,0)))
		q.put(helper.add_coordinates(start, (-1, 0)))
		q.put(helper.add_coordinates(start, (0, -1)))

		while not q.empty():
			current = q.get()
			if current not in self.all_subtiles:
				self.add_subtile(current)
				q.put(helper.add_coordinates(current, (0,1)))
				q.put(helper.add_coordinates(current, (1,0)))
				q.put(helper.add_coordinates(current, (-1, 0)))
				q.put(helper.add_coordinates(current, (0, -1)))

class MountainRange:
	def __init__(self, subtiles):
		self.subtiles = subtiles
		# print("finding center")
		self.center = self.find_center()
		# print("finding boundaries")
		self.boundary = self.find_boundary()
		# print("generating quadrants")
		self.quadrants = self.create_quadrants()
		self.anchors = set()

	def find_center(self) -> tuple:
		sumx = 0
		sumy = 0
		for point in self.subtiles:
			sumx += point[0]
			sumy += point[1]
		return (round(sumx/len(self.subtiles)), round(sumy/len(self.subtiles)))

	def find_boundary(self) -> set:
		output = set()
		for subtile in self.subtiles:
			boundary = False
			for y in range(-1,2):
				for x in range(-1,2):
					if x == 0 and y == 0:
						continue
					if helper.add_coordinates(subtile, (x,y)) not in self.subtiles:
						boundary = True
			if boundary:
				output.add(subtile)

		return output

	def is_same_mountain_range(self, mountain_range):
		if len(self.subtiles.difference(mountain_range.subtiles)) == 0:
			return True
		else:
			return False

	def create_quadrants(self) -> dict:
		# print("generating quadrants")
		output = dict()
		# print(self.boundary)
		for subtile in self.boundary:
			if subtile[0] >= self.center[0] and subtile[1] >= self.center[1]:
				output[subtile] = 1
			elif subtile[0] >= self.center[0] and subtile[1] <= self.center[1]:
				output[subtile] = 2
			elif subtile[0] <= self.center[0] and subtile[1] <= self.center[1]:
				output[subtile] = 3
			else:
				output[subtile] = 4
		# print(output)
		return output

	def set_anchors(self, anchor1, anchor2):
		self.anchors.add(anchor1)
		self.anchors.add(anchor2)




def generate_new_subtile_elevation_dict(mapconfig) -> dict:
	length = mapconfig.width * mapconfig.height * int((math.pow(mapconfig.subtiles, 2)))
	output = dict()
	for y in range(mapconfig.height*mapconfig.subtiles):
		for x in range(mapconfig.width * mapconfig.subtiles):
			output[(x,y)] = 0
	continents = list()
	for i in range(mapconfig.num_continents):
		continents.append(create_continent(\
			(random.randrange(0, mapconfig.width * mapconfig.subtiles),\
			 random.randrange(0, mapconfig.height *mapconfig.subtiles)), \
			random.randrange(25,75), random.randrange(25,75)))
		continents[i].all_tiles = continents[i].subtiles_to_tiles(mapconfig.subtiles)
		new_elevations = raise_continent_to_elevation(continents[i], 128)
		output.update(new_elevations)
	mountain_ranges = list()
	for continent in continents:
		other_continents = continents
		other_continents.remove(continent)
		for cont in other_continents:
			if len(continent.all_subtiles.intersection(cont.all_subtiles)) > 0:
				new_mountains_subtiles = continent.all_subtiles.intersection(cont.all_subtiles)
				new_mountain_range = MountainRange(new_mountains_subtiles)
				print(len(continent.boundary.intersection(cont.boundary)))
				if len(continent.boundary.intersection(cont.boundary)) >= 2:
					all_points = continent.boundary.intersection(cont.boundary)
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
					new_mountain_range.set_anchors(point1, point2)
				valid = True
				for m in mountain_ranges:
					if m.is_same_mountain_range(new_mountain_range):
						valid = False
				if valid:
					mountain_ranges.append(new_mountain_range)
					new_elevations = raise_mountain_range(new_mountain_range, 255)
					output.update(new_elevations)
	return output

def raise_continent_to_elevation(continent, elevation) -> dict:
	output = dict()
	for subtile in continent.all_subtiles:
		output[subtile] = elevation
	for subtile in continent.boundary:
		output[subtile] = 100
	# print(len(output))
	# print(output)
	return output

def raise_mountain_range(mountain_range, elevation) -> dict:
	output = dict()
	mainline = set()
	startpoint = random.choice(tuple(mountain_range.boundary))
	startquad = mountain_range.quadrants[startpoint]
	endquad = (startquad + 2) % 4 #Should return the opposite quadrant based on the standard cartesian quadrants
	if endquad == 0:
		endquad = 4
	# print(startquad)
	# print(endquad)
	# print("finding possible endpoints")
	# print(mountain_range.quadrants)
	possible_endpoints = [point for point in mountain_range.quadrants if mountain_range.quadrants[point] == endquad]
	# print(possible_endpoints)
	endpoint = random.choice(possible_endpoints)
	mainline = helper.get_line_points(startpoint, mountain_range.center)
	mainline = mainline.union(helper.get_line_points(mountain_range.center, endpoint))

	for subtile in mountain_range.subtiles:
		output[subtile] = 150
	for subtile in mountain_range.boundary:
		output[subtile] = 50
	for subtile in mainline:
		output[subtile] = 200
	for subtile in mountain_range.anchors:
		output[subtile] = 255
	return output

def create_continent(origin, sizex, sizey):
	new_continent = continent(origin)
	new_continent.origin = origin
	current = origin
	continent_outline = helper.get_ellipse_points(origin, sizex, sizey)
	for point in continent_outline:
		new_continent.add_subtile(point)
		new_continent.boundary.add(point)
	new_continent.fill_continent()
	return new_continent


def main():
	settings = db.ConfigDB()
	mapconfig = settings.get_script_config("test")
	settings.close()
	el_dict = generate_new_subtile_elevation_dict(mapconfig)
	# print(len(el_dict))
	texgen.draw_elevation_map(el_dict, "elev_map.png", mapconfig.width*mapconfig.subtiles, mapconfig.height*mapconfig.subtiles, 20)
	# print(el_dict)



if __name__ == '__main__':
	main()
