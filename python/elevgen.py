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
import geometry

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
		q.put(geometry.add_coordinates(start, (0,1)))
		q.put(geometry.add_coordinates(start, (1,0)))
		q.put(geometry.add_coordinates(start, (-1, 0)))
		q.put(geometry.add_coordinates(start, (0, -1)))

		while not q.empty():
			current = q.get()
			if current not in self.all_subtiles:
				self.add_subtile(current)
				q.put(geometry.add_coordinates(current, (0,1)))
				q.put(geometry.add_coordinates(current, (1,0)))
				q.put(geometry.add_coordinates(current, (-1, 0)))
				q.put(geometry.add_coordinates(current, (0, -1)))

class MountainRange:
	def __init__(self, anchors):
		self.anchors = list(anchors)
		self.mainline = self.set_mainline(self.anchors)
		self.highlands = self.set_highlands(2)
		self.foothills = self.set_foothills(6)
		self.subtiles = self.set_subtiles()
		self.center = self.find_center()
		self.boundary = self.find_boundary()
		# self.quadrants = self.create_quadrants()

	def set_highlands(self, generations) -> set:
		output = set()
		q = queue.Queue()
		for point in self.mainline:
			q.put(point)
		for i in range(generations):
			new_tiles = set()
			while not q.empty():
				tile = q.get()
				for mod in [(0,1),(1,0),(-1,0),(0,-1),(1,1),(-1,-1),(-1,1),(1,-1)]:
					current = geometry.add_coordinates(tile, mod)
					if current not in self.mainline:
						new_tiles.add(current)
			output.update(new_tiles)
			for point in new_tiles:
				q.put(point)

		return output

	def set_foothills(self, generations) -> set:
		output = set()
		q = queue.Queue()
		for point in self.highlands:
			q.put(point)
		for i in range(generations):
			new_tiles = set()
			while not q.empty():
				tile = q.get()
				for mod in [(0,1),(1,0),(-1,0),(0,-1)]:
					current = geometry.add_coordinates(tile, mod)
					if current not in self.mainline and current not in self.highlands:
						new_tiles.add(current)
			output.update(new_tiles)
			for point in new_tiles:
				q.put(point)

		return output

	def set_subtiles(self) -> set:
		return self.mainline.union(self.highlands, self.foothills)

	def set_mainline(self, anchors) -> set:
		output = set()
		for i in range(0, len(anchors)):
			if (i+1) >= len(anchors):
				break
			else:
				new_line = geometry.get_line_points(anchors[i], anchors[i+1])
				for point in new_line:
					output.add(point)
		return output


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
					if geometry.add_coordinates(subtile, (x,y)) not in self.subtiles:
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
		new_elevations = raise_continent_to_elevation(continents[i], 70)
		output.update(new_elevations)
	mountain_ranges = list()
	for continent in continents:
		subtile_list = list(continent.all_subtiles)
		for i in range(mapconfig.num_mnts_per_continent):
			num_anchors = random.randrange(2,6)
			min_spacing = int(500/num_anchors)
			max_spacing = int(2000/num_anchors)
			#TODO Add this number to config/template
			anchors = list()
			for n in range(num_anchors):
				if n == 0:
					anchors.append(random.choice(subtile_list))
					continue
				else:
					possibles = list()
					for y in range(-max_spacing, max_spacing):
						for x in range(-max_spacing, max_spacing):
							print(x,y)
							if geometry.distance_between_two_points(anchors[n-1], geometry.add_coordinates(anchors[n-1], (x,y))) > min_spacing:
								possibles.append(geometry.add_coordinates(anchors[n-1], (x,y)))
					new_anchor = random.choice(possibles)

					anchors.append(new_anchor)
			new_mountain_range = MountainRange(anchors)
			mountain_ranges.append(new_mountain_range)

	for mountain_range in mountain_ranges:
		raise_mountain_range(mountain_range)


	for subtile in output:
		if output[subtile] < 0:
			output[subtile] = 0
		elif output[subtile] > 255:
			output[subtile] = 255
	return output

def raise_continent_to_elevation(continent, elevation) -> dict:
	output = dict()
	for subtile in continent.all_subtiles:
		output[subtile] = elevation
	for subtile in continent.boundary:
		output[subtile] = 50
	# print(len(output))
	# print(output)
	return output

def raise_mountain_range(mountain_range) -> dict:
	output = dict()
	for point in mountain_range.foothills:
		output[point] = 100
	for point in mountain_range.highlands:
		output[point] = 128
	for point in mountain_range.mainline:
		output[point] = 180
	for point in mountain_range.boundary:
		output[point] = 220
	for point in mountain_range.anchors:
		output[point] = 255
	return output

def create_continent(origin, sizex, sizey):
	new_continent = continent(origin)
	new_continent.origin = origin
	current = origin
	continent_outline = geometry.get_ellipse_points(origin, sizex, sizey)
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
