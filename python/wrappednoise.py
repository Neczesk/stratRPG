#Standard Library
import time

#Third Party
from opensimplex import OpenSimplex


class NoiseConfig:
	oc: int #octaves
	freq: float
	exp: float #exponent

	def __init__(self, o, f, e):
		self.oc = o
		self.freq = f
		self.exp = e

class WrappedNoise:
	def __init__(self, config):
		self.conf = config
		self.noise = OpenSimplex(int(time.time()))

	conf: NoiseConfig
	noise: OpenSimplex

	def noise_at_point(self,x,y):
		output = 0.0
		divisor = 0.0
		octfac = 1.0
		for i in range(0,self.conf.oc):
			divisor += octfac
			output += octfac * \
			self.noise.noise2d(self.conf.freq * pow(2,i) * x, self.conf.freq * pow(2,i)*y)
			octfac *= 0.5
		output = output / divisor
		output = pow(output, self.conf.exp)
		return output



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

	testConfig = NoiseConfig(1,1,1)
	w.conf = testConfig
	w.noise = OpenSimplex()


	