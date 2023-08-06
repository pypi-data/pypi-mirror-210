"""
https://github.com/lemire/testingRNG/blob/master/source/pcg64.h

Modified by D. Lemire based on original code by M. O'Neill, August 2017

start of the code copied verbatim from O'Neill's, except that we declare some
functions "static"
"""

from dataclasses import dataclass
from ..common.int_t import *
from . import splitmix64


def pcg_128bit_const(high, low):
	return (high << 64) + low


PCG_DEFAULT_MULTIPLIER_128 = pcg_128bit_const(2549297995355413924, 4865540595714422341)
PCG_DEFAULT_INCREMENT_128 = pcg_128bit_const(6364136223846793005, 1442695040888963407)


@dataclass
class Data:
	state: UInt128
	inc: UInt128


def pcg_setseq_128_step_r(data: Data) -> None:
	data.state = data.state * PCG_DEFAULT_MULTIPLIER_128 + data.inc


def pcg_setseq_128_srandom_r(data: Data, init_state: UInt128, init_seq: UInt128) -> None:
	data.state = 0
	data.inc = (init_seq << 1) | 1
	pcg_setseq_128_step_r(data)
	data.state += init_state
	pcg_setseq_128_step_r(data)


# verbatim from O'Neill's except that we skip her assembly:
def pcg_rotr_64(value: UInt64, rot: UInt32) -> UInt64:
	return UInt64.BITS & ((value >> rot) | (value << ((-rot) & 63)))


def pcg_output_xsl_rr_128_64(state: UInt128) -> UInt64:
	return pcg_rotr_64(UInt64.BITS & ((state >> 64) ^ state), UInt32.BITS & (state >> 122))


def pcg_setseq_128_xsl_rr_64_random_r(data: Data) -> UInt64:
	pcg_setseq_128_step_r(data)
	return pcg_output_xsl_rr_128_64(data.state)


# rest is our code
def new(seed: UInt64) -> Data:
	# use splitmix64 to seed the program
	splitmix64_data = splitmix64.new(seed)
	splitmix64_values = tuple(splitmix64.next(splitmix64_data) for _ in range(4))

	init_state: UInt128 = pcg_128bit_const(splitmix64_values[0], splitmix64_values[1])

	# we pick a sequence at random
	init_seq: UInt128 = pcg_128bit_const(splitmix64_values[2], splitmix64_values[3])

	# should not be necessary, but let us be careful.
	init_seq |= 1

	data = Data(UInt128(), UInt128())
	pcg_setseq_128_srandom_r(data, init_state, init_seq)
	return data


def next(data: Data) -> UInt64:
	return pcg_setseq_128_xsl_rr_64_random_r(data)
