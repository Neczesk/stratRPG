from opensimplex import OpenSimplex
import time

class noiseConfig:
	octaves: int
	frequency: float
	exp: int

	def __init__(self, o, f, e):
		self.octaves = o
		self.frequency = f
		self.exp = e

class wrappedNoise:
	def __init__(self, config):
		self.conf = config
		self.noise = OpenSimplex(int(time.time()))

	conf: noiseConfig
	noise: OpenSimplex



if __name__ == "__main__":
	n = noiseConfig(8, .0008, 1)
	w = wrappedNoise(n)

	if w.conf.octaves != 8:
		print(w.conf.octaves)
	"""print(w.noise.noise2d(x=3,y=7))
	