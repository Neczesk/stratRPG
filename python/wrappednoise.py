#Standard Library
import time
import statistics

#Third Party
from opensimplex import OpenSimplex


class NoiseConfig:
	oc: int #octaves
	freq: float
	exp: float #exponent
	persistence: float

	def __init__(self, o, f, e, p = 0.5):
		self.oc = o
		self.freq = f
		self.exp = e
		self.persistence = p

class WrappedNoise:
	def __init__(self, config):
		self.conf = config
		self.noise = OpenSimplex(int(time.time()))

	conf: NoiseConfig
	noise: OpenSimplex

	def noise_at_point(self,x,y):
		x= x +1
		y = y + 1
		if x == 0 and y == 0:
			print(self.noise.noise2d(x,y))
		output = 0.0
		divisor = 0.0
		octfac = 1.0
		for i in range(0,self.conf.oc):
			divisor += octfac
			output += octfac * \
			self.noise.noise2d(self.conf.freq * pow(2,i) * x, self.conf.freq * pow(2,i)*y)
			octfac *= self.conf.persistence
		output = output / divisor
		output = pow(output, self.conf.exp)
		return output

	def transform_noise_list(self, input, new_mean, new_sd):
		"""Calculates mean and standard deviation of the list given, then 
		transforms the list to have new_mean and new_sd"""
		mean = statistics.mean(input)
		stdev = statistics.pstdev(input, mean)

		mean_scaled_input = [(x-mean) for x in input]
		st_dev_transformed = [x * (new_sd/stdev) for x in mean_scaled_input]
		mean_scaled_output = [x + new_mean for x in st_dev_transformed]
		#Found on stack exchange post about transforming mean and stdev of dataset
		return mean_scaled_output


	def produce_noise_list_percent(self, sizex, sizey):
		"""Produces a list of floats between 0 to 100"""
		results = list()
		for y in range(0,sizey):
			row = list()
			for x in range(0,sizex):
				percent = self.noise_at_point(x, y)
				percent = noise_to_percent(percent)
				results.append(percent)
		return results

def noise_to_percent(input: float):
	return (((input + 1) * 100)/ 2)



if __name__ == "__main__":
	n0 = NoiseConfig(1,1,1)
	n = NoiseConfig(3, 1, 1)
	n1 = NoiseConfig(1,0.5, 1)
	n2 = NoiseConfig(1,1,2)
	w = WrappedNoise(n0)

	if w.conf.oc != 1:
		print(w.conf.oc)
	print(w.noise_at_point(100,200))
	w.conf = n
	print(w.noise_at_point(100,200))
	w.conf = n1
	print(w.noise_at_point(100,200))
	w.conf = n2
	print(w.noise_at_point(100,200))

	noise_list = w.produce_noise_list_percent(20, 10)
	transformed = w.transform_noise_list(noise_list, 40, statistics.pstdev(noise_list))
	print(statistics.mean(transformed))


	