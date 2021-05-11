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


class MapFeature:
	def __init__(self):
		self.subtiles = set()
		self.boundary = set()
		self.center = (-1,-1)

	def find_center(self) -> tuple:
		sumx = 0
		sumy = 0
		for point in self.subtiles:
			sumx += point[0]
			sumy += point[1]
		return (round(sumx/len(self.subtiles)), round(sumy/len(self.subtiles)))

	def add_subtile(self, new_subtile):
		self.all_subtiles.add(new_subtile)

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

	def fill_to_boundary(self) -> set:
		return geometry.get_points_inside_shape(self.boundary, self.center)

	def rotate(self, angle):
		self.boundary = set()
		self.subtiles = geometry.rotate_shape(self.subtiles, angle)
		overlooked = set()
		for point in self.subtiles:
			for mod in [(0,1),(1,0),(1,1),(-1,-1),(-1,0),(0,-1),(-1,1),(1,-1)]:
				current = geometry.add_coordinates(point, mod)
				if current not in self.subtiles:
					num_neighbors = 0
					for mod2 in [(0,1),(1,0),(1,1),(-1,-1),(-1,0),(0,-1),(-1,1),(1,-1)]:
						if geometry.add_coordinates(current, mod2) in self.subtiles:
							num_neighbors += 1
					if num_neighbors >= 4:
						overlooked.add(current)
		self.subtiles.update(overlooked)

		self.boundary = self.find_boundary()





class Continent(MapFeature):
	def __init__(self, boundary):
		super().__init__()
		self.boundary = boundary
		self.subtiles.update(boundary)
		self.center = self.find_center()
		self.subtiles.update(self.fill_to_boundary())

	def combine_continents(self, continent2):
		new_subtiles = self.subtiles.union(continent2.subtiles)
		temp = MapFeature()
		temp.subtiles = new_subtiles
		temp.boundary = temp.find_boundary()
		return Continent(temp.boundary)

class MountainRange(MapFeature):
	def __init__(self, anchors):
		super().__init__()
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
			output[(x,y)] = 50
	continents = list()
	for i in range(mapconfig.num_continents):
		# new_ellipse = geometry.get_ellipse_points((random.randrange(0, mapconfig.width*mapconfig.subtiles), random.randrange(0, mapconfig.height*mapconfig.subtiles)), random.randrange(25,75), random.randrange(25,75))
		# # new_ellipse = geometry.rotate_shape(new_ellipse, random.randrange(360))
		# new_continent = Continent(new_ellipse)
		# new_continent.rotate(random.randrange(360))
		continents.append(build_continent(3, mapconfig.width*mapconfig.subtiles, mapconfig.height*mapconfig.subtiles))
		new_elevations = raise_continent_to_elevation(continents[i], 70)
		output.update(new_elevations)
	mountain_ranges = list()
	for continent in continents:
		subtile_list = list(continent.subtiles)
		for n in range(0, mapconfig.num_mnts_per_continent):
			num_anchors = random.randrange(3,8)
			min_spacing = 10
			max_spacing = 25
			new_anchors = list()
			new_anchors.append(random.choice(subtile_list))
			for i in range(1, num_anchors):
				outer = geometry.get_points_in_circle(new_anchors[n-1], max_spacing)
				outer.update(geometry.get_points_inside_shape(outer, new_anchors[n-1]))
				inner = geometry.get_points_in_circle(new_anchors[n-1], min_spacing)
				inner.update(geometry.get_points_inside_shape(inner, new_anchors[n-1]))
				possibles = outer.difference(inner)
				possibles = possibles.intersection(continent.subtiles)
				possibles = list(possibles)
				new_anchors.append(random.choice(possibles))

			print(new_anchors)
			new_mountain_range = MountainRange(new_anchors)
			mountain_ranges.append(new_mountain_range)

	for mountain_range in mountain_ranges:
		new_elevations = raise_mountain_range(mountain_range)
		output.update(new_elevations)

	# output = elevation_fuzz(mapconfig.roughness, output)

	for subtile in output:
		if output[subtile] < 0:
			output[subtile] = 0
		elif output[subtile] > 255:
			output[subtile] = 255
	return output

def raise_continent_to_elevation(continent, elevation) -> dict:
	output = dict()
	for subtile in continent.subtiles:
		output[subtile] = elevation
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

def build_continent(n_subcontinents, width, height):
	start = geometry.get_ellipse_points((random.randrange(0, width), random.randrange(0, height)), random.randrange(25,100), random.randrange(25,100))
	subcontinent_a = Continent(start)
	subcontinent_a.rotate(random.randrange(360))
	subcontinents = list()
	subcontinents.append(subcontinent_a)
	for n in range(1, n_subcontinents):
		possibles = subcontinents[n-1].boundary
		possibles = list(possibles)
		sub_outline = geometry.get_ellipse_points(random.choice(possibles), random.randrange(25,100), random.randrange(25,100))
		next_continent = Continent(sub_outline)
		next_continent.rotate(random.randrange(360))
		subcontinents.append(next_continent)
	output = subcontinents[0]
	for i in range(0, len(subcontinents)-1):
		output = subcontinents[i].combine_continents(subcontinents[i+1])

	noise_config = wrappednoise.NoiseConfig(1, 0.1, 1, 0.5, 1)
	noisey = wrappednoise.WrappedNoise(noise_config)
	noisex = wrappednoise.WrappedNoise(noise_config)
	noisex.reseed(random.randrange(-10000, 10000))
	perturbed = set()
	for subtile in output.subtiles:
		new_x = int(subtile[0] + noisex.noise_at_point(subtile[0], subtile[1]))
		new_y = int(subtile[1] + noisey.noise_at_point(subtile[0], subtile[1]))
		perturbed.add((new_x, new_y))
	print( perturbed)

	output.subtiles = perturbed
	return output

def elevation_fuzz(roughness, el_dict) -> dict:
	noise_config = wrappednoise.NoiseConfig(3, 0.03, 0.8, 0.5, roughness)
	noise = wrappednoise.WrappedNoise(noise_config)
	noise_dict = {key: int(noise.noise_at_point(key[0], key[1])) for key, value in el_dict.items()}
	output = {key: int((el_dict[key] + noise_dict[key])/2) for key in el_dict}
	return output





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
