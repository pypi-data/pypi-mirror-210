"""
https://github.com/lemire/testingRNG/blob/master/source/jenkinssmall.h

"""

from ..common.int_t import *
from dataclasses import dataclass


@dataclass
class Data:
	a: UInt64
	b: UInt64
	c: UInt64
	d: UInt64


def rot(x, k):
	return (x << k) | (x >> (64 - k))


def init(data: Data, seed: UInt64) -> None:
	data.a = 0xf1ea5eed
	data.b = data.c = data.d = seed
	for i in range(20):
		next(data)


def next(data: Data) -> UInt64:
	e: UInt64 = data.a - rot(data.b, 7)
	data.a = data.b ^ rot(data.c, 13)
	data.b = data.c + rot(data.d, 37)
	data.c = data.d + e
	data.d = e + data.a
	return data.d
