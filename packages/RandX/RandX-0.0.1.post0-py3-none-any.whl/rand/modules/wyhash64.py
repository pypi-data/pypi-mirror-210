"""
https://github.com/lemire/testingRNG/blob/master/source/wyhash64.h

"""

from ..common.int_t import *
from dataclasses import dataclass


@dataclass
class Data:
	x: UInt128


def next(data: Data) -> UInt64:
	data.x += 0x60bee2bee120fc15
	data.x &= UInt64.BITS
	tmp: UInt128 = UInt128.BITS & (data.x * 0xa3b195354a39b70d)
	m1: UInt64 = UInt64.BITS & ((tmp >> 64) ^ tmp)
	tmp = UInt128.BITS & (m1 * 0x1b03738712fad5c9)
	m2: UInt64 = UInt64.BITS & ((tmp >> 64) ^ tmp)
	return m2
