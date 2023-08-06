"""
https://github.com/lemire/testingRNG/blob/master/source/mersennetwister.h

adapted from code by Piotr Stefaniak

A C-program for MT19937, with initialization improved 2002/1/26.
Coded by Takuji Nishimura and Makoto Matsumoto.
Copyright (C) 1997 - 2002, Makoto Matsumoto and Takuji Nishimura,
All rights reserved.
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:
	1. Redistributions of source code must retain the above copyright
		notice, this list of conditions and the following disclaimer.
	2. Redistributions in binary form must reproduce the above copyright
		notice, this list of conditions and the following disclaimer in the
		documentation and/or other materials provided with the distribution.
	3. The names of its contributors may not be used to endorse or promote
		products derived from this software without specific prior written
		permission.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER
OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
Any feedback is very welcome.
http://www.math.sci.hiroshima-u.ac.jp/~m-mat/MT/emt.html
email: m-mat @ math.sci.hiroshima-u.ac.jp (remove space)
"""

from ..common.int_t import *
from dataclasses import dataclass, field
import typing as _tp


# Period parameters
N = 624
M = 397
A = N - M
B = N - 1
# 'unsigned long'
MATRIX_A = 0x9908b0df  # constant vector a
UPPER_MASK = 0x80000000  # most significant w-r bits
LOWER_MASK = 0x7fffffff  # least significant r bits


@dataclass
class Data:
	mt: _tp.MutableSequence = field(default_factory=lambda: [UInt32(), ] * N)  # the array for the state vector
	mti: UInt32 = N + 1  # mti==N+1 means mt[N] is not initialized


# initializes mersennetwister_mt[N] with a seed
def init(data: Data, seed: UInt64) -> None:
	data.mt[0] = 0xffffffff & seed
	data.mti = 1
	while data.mti < N:
		# See Knuth TAOCP Vol2. 3rd Ed. P.106 for multiplier.
		# In the previous versions, MSBs of the seed affect
		# only MSBs of the array mersennetwister_mt[].
		# 2002/01/09 modified by Makoto Matsumoto
		data.mt[data.mti] = UInt32.BITS & (1812433253 * (data.mt[data.mti - 1] ^ (data.mt[data.mti - 1] >> 30)) + data.mti)
		data.mti += 1


# generates a random number on [0,0xffffffff]-interval
def next(data: Data) -> UInt32:
	# generate N words at one time
	if data.mti >= N:
		# mag01[x] = x * MATRIX_A  for x=0,1
		mag01 = (0, MATRIX_A)

		for kk in range(0, A):
			y = (data.mt[kk] & UPPER_MASK) | (data.mt[kk + 1] & LOWER_MASK)
			data.mt[kk] = UInt32.BITS & (data.mt[kk + M] ^ (y >> 1) ^ mag01[y & 1])

		for kk in range(A, B):
			y = (data.mt[kk] & UPPER_MASK) | (data.mt[kk + 1] & LOWER_MASK)
			data.mt[kk] = UInt32.BITS & (data.mt[kk + (M - N)] ^ (y >> 1) ^ mag01[y & 1])

		y = (data.mt[N - 1] & UPPER_MASK) | (data.mt[0] & LOWER_MASK)
		data.mt[N - 1] = UInt32.BITS & (data.mt[M - 1] ^ (y >> 1) ^ mag01[y & 1])

		data.mti = 0

	y = data.mt[data.mti]
	data.mti += 1

	# Tempering
	y ^= (y >> 11)
	y ^= (y << 7) & 0x9d2c5680
	y ^= (y << 15) & 0xefc60000
	y ^= (y >> 18)

	return y
