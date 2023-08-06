"""
https://github.com/lemire/testingRNG/blob/master/source/pcg32.h

Modified by D. Lemire based on original code by M. O'Neill, August 2017
"""

from dataclasses import dataclass
from ..common.int_t import *
from . import splitmix64


@dataclass
class Data:
	state: UInt64  # RNG state.  All values are possible.  Will change over time.
	inc: UInt64  # Controls which RNG sequence (stream) is
	# selected. Must *always* be odd. Might be changed by the user, never by our
	# code.


def new(seed: UInt64) -> Data:
	data = splitmix64.new(seed)
	state: UInt64 = splitmix64.next(data)
	inc: UInt64 = splitmix64.next(data) | 1  # making sure it is odd
	return Data(state, inc)


def next(data: Data) -> UInt32:
	old_state: UInt64 = data.state
	data.state = UInt64.BITS & (old_state * 0x5851f42d4c957f2d + data.inc)
	xor_shifted: UInt32 = UInt32.BITS & (((old_state >> 18) ^ old_state) >> 27)
	rot: UInt32 = UInt32.BITS & (old_state >> 59)
	return UInt32.BITS & ((xor_shifted >> rot) | (xor_shifted << (32 - rot)))
