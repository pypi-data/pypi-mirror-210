import random
from rand.modules import splitmix64 as test_mod
import dataclasses
from rand.common import intwise
import typing as _tp


def split(seq: _tp.Sequence, order: _tp.Iterable):
	start, stop = 0, 0
	for n in order:
		stop += n
		yield seq[start:stop]
		start += n


def get_entropies(cls):
	fields = ((field.name, field.type) for field in dataclasses.fields(cls))
	entropies = (t.BITS_N for n, t in fields)
	return entropies


def get_args(entropies: _tp.Sequence, seed: bytes):
	seeds = tuple(split(seed, (n // 8 for n in entropies)))
	args = (intwise.combine_little(s) for s in seeds)
	return args


def get_args_from_data(data):
	fields = ((field.name, field.type) for field in dataclasses.fields(type(data)))
	args = (getattr(data, n) for n, t in fields)
	return args


def get_seed(entropies: _tp.Sequence, args: _tp.Iterable):
	args = (bytes(intwise.split_little_ex(x, n // 8)) for x, n in zip(args, entropies))
	data = b"".join(args)
	return data


def rand_args(entropies: _tp.Sequence):
	args = (random.getrandbits(entropy) for entropy in entropies)
	return args


def rand_seed(entropies: _tp.Sequence):
	args = rand_args(entropies)
	seed = b"".join(get_seed(entropies, args))
	return seed


class Calc:
	def __init__(self, module, seed=None, offset=0):
		self.module = module
		self.entropies = entropies = tuple(get_entropies(module.Data))
		if seed is None:
			self.data = module.Data(*rand_args(entropies))
		elif isinstance(seed, module.Data):
			self.data = seed
		else:
			self.data = module.Data(*get_args(entropies, seed))
		self.offset = offset

	def __repr__(self):
		seed = get_seed(self.entropies, get_args_from_data(self.data))
		return f"{type(self).__name__}({self.module}, {seed}, {self.offset})"

	def __iter__(self):
		return self

	def __next__(self):
		self.offset += 1
		return self.module.next(self.data)

	__call__ = __next__


class CalcEx:
	"""calculate prandom nr with scaling"""
	pass


def g():
	fn = Calc(test_mod)
	print(fn)

	for i, n in zip(range(10), fn):
		print(n)

	print(fn)


def h():
	e = tuple(get_entropies(test_mod))
	c = tuple(rand_args(e))
	print(c)
	a = get_seed(e, c)
	b = tuple(get_args(e, a))
	print(b)
	print(a)


def main():
	g()


if __name__ == '__main__':
	main()
