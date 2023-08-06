"""
https://github.com/lemire/testingRNG/blob/master/source/splitmix64.h

Modified by D. Lemire, August 2017

Fast Splittable Pseudorandom Number Generators
Steele Jr, Guy L., Doug Lea, and Christine H. Flood. "Fast splittable
pseudorandom number generators."
ACM SIGPLAN Notices 49.10 (2014): 453-472.

Written in 2015 by Sebastiano Vigna (vigna@acm.org)
To the extent possible under law, the author has dedicated all copyright
and related and neighboring rights to this software to the public domain
worldwide. This software is distributed without any warranty.
See <http://creativecommons.org/publicdomain/zero/1.0/>.

original documentation by Vigna:
	This is a fixed-increment version of Java 8's SplittableRandom generator
	See http://dx.doi.org/10.1145/2714064.2660195 and
	http://docs.oracle.com/javase/8/docs/api/java/util/SplittableRandom.html
	It is a very fast generator passing BigCrush, and it can be useful if
	for some reason you absolutely want 64 bits of state; otherwise, we
	rather suggest to use a xoroshiro128+ (for moderately parallel
	computations) or xorshift1024* (for massively parallel computations)
	generator.
"""

from ..common.int_t import *
from dataclasses import dataclass


# floor( ( (1+sqrt(5))/2 ) * 2**64 MOD 2**64)
GOLDEN_GAMMA = UInt64(0x9E3779B97F4A7C15)


@dataclass
class Data:
	z: UInt64


def new(seed: UInt64) -> Data:
	return Data(seed)


def next(data: Data) -> UInt64:
	"""
	returns random number, modifies seed[0]
	compared with D. Lemire against
	http://grepcode.com/file/repository.grepcode.com/java/root/jdk/openjdk/8-b132/java/util/SplittableRandom.java#SplittableRandom.0gamma
	"""
	# original c++:
	#  uint64_t z = (*seed += GOLDEN_GAMMA);
	# yeah, that's ambiguous
	# tested with online compiler, += return is post evaluation
	data.z += GOLDEN_GAMMA
	data.z &= UInt64.BITS
	z: UInt64 = data.z
	# David Stafford's Mix13 for MurmurHash3's 64-bit finalizer
	z = UInt64.BITS & ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9)
	z = UInt64.BITS & ((z ^ (z >> 27)) * 0x94D049BB133111EB)
	return UInt64.BITS & (z ^ (z >> 31))


def getitem(seed: UInt64, offset: UInt64) -> UInt64:
	seed += offset * GOLDEN_GAMMA
	seed &= UInt64.BITS
	return next(Data(seed))
