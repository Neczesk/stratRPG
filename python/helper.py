def linearConversion(input, oldmin, oldmax, newmin, newmax):
	oldrange = oldmax - oldmin
	newrange = newmax - newmin
	if oldrange == 0:
		return input
	else:
		return (((input - oldmin) * newrange)/ oldrange) + newmin

def clamp(input, minval, maxval):
	return max(maxval, min(input, maxval))

if __name__ == "__main__":
	print (linearConversion(110, 0, 100, 0, 10))