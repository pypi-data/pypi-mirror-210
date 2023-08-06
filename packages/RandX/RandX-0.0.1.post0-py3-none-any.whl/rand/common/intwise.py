import typing as _tp


# generic impl
def bits(n: int) -> int:
	return (1 << n) - 1


def resign(n_bits: int = 64) \
		-> _tp.Callable[[int, ], int]:
	"""resign a previously unsigned integer"""
	shift = n_bits - 1
	sign_bit = 1 << shift

	def f(x: int) -> int:
		is_neg = bool(sign_bit & x)
		return (-is_neg << shift) | x

	return f


word_size = 8
word_mask = bits(word_size)


def split_little_ex(x: int, n_words: int) -> _tp.Generator[int, None, None]:
	for i in range(n_words):
		yield word_mask & x
		x >>= word_size
	return


def combine_little(it: _tp.Iterable[int]) -> int:
	# _tp.Iterable[int] includes bytes type
	r = 0
	for i, v in enumerate(it):
		v <<= word_size * i
		r |= v
	return r
