"""
https://github.com/lemire/testingRNG/blob/master/source/xorshift32.h

"""

from ..common.int_t import *
from dataclasses import dataclass


@dataclass
class Data:
	y: UInt128


def next(data: Data) -> UInt32:
	data.y ^= (data.y << 13)
	data.y ^= (data.y >> 17)
	data.y ^= (data.y << 5)
	data.y = UInt32.BITS & data.y
	return data.y
