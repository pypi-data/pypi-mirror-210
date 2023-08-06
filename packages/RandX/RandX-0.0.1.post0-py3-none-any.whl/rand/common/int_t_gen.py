
def n(x):
	r = f"""

class UInt{x}(int):
	BITS_N = {x}
	BITS = _bits({x})


class Int{x}(int):
	BITS_N = {x}
	BITS = _resign({x})(_bits({x}))
"""
	return r


def gen():
	a = """from .intwise import bits as _bits, resign as _resign
	"""
	r = [a, *(n(2 ** i) for i in range(3, 8))]
	return r


def main():
	with open("int_t.py", "w") as fd:
		for s in gen():
			print(s, end='')
			fd.write(s)
	print("\n<END>")


if __name__ == '__main__':
	main()
