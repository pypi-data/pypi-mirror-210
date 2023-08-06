"""
https://github.com/lemire/testingRNG/blob/master/source/lehmer64.h

"""

from ..common.int_t import *
from dataclasses import dataclass


@dataclass
class Data:
	x: UInt128


def next(data: Data) -> UInt64:
	data.x *= 0xda942042e4dd58b5
	data.x &= UInt128.BITS  # restrict to 128 bits
	return UInt64.BITS & (data.x >> 64)
