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

if __name__ == "__main__":
	print (linearConversion(110, 0, 100, 0, 10))