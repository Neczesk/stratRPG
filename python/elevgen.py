#Standard library
import math
import statistics

#local imports
import wrappednoise
import helper

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





