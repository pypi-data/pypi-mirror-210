"""
https://github.com/lemire/testingRNG/blob/master/source/mitchellmoore.h

adapted from code by Piotr Stefaniak

Mitchell-Moore algorithm from
"The Art of Computer Programming, Volume II"
by Donald E. Knuth

Improvements based on
"Uniform Random Number Generators for Vector and Parallel Computers"
by Richard P. Brent
"""

from ..common.int_t import *
from dataclasses import dataclass, field
import typing as _tp


# 'unsigned long'
R = 250
S = 200
T = 103
U = 50


@dataclass
class Data:
	sequence: _tp.MutableSequence = field(default_factory=lambda: [UInt32(), ] * R)
	a: UInt32 = R
	b: UInt32 = S
	c: UInt32 = T
	d: UInt32 = U


def init(data: Data, seed: UInt64) -> None:
	for i in range(0, R * 2):
		data.sequence[i % R] = seed = (1664525 * seed + 1013904223)
	data.sequence[0] <<= 1
	data.sequence[1] |= 1


def next(data: Data) -> UInt32:
	data.a += 1
	data.b += 1
	data.c += 1
	data.d += 1
	a, b, c, d = data.a % R, data.b % R, data.c % R, data.d % R
	# return data.sequence[a] += data.sequence[b] += data.sequence[c] += data.sequence[d];
	# what a nasty piece of code
	#  evaluate right to left
	# check with c++ compiler that we got this right
	"""/******************************************************************************
				https://www.onlinegdb.com/online_c++_compiler
	*******************************************************************************/
	
	#include <iostream>
	
	using namespace std;
	
	int main()
	{
		
		int a = 1; int b = 1; int c = 1; int d = 1; int r = 0;
		r = a += b += c += d;
		cout << a << endl << b << endl << c << endl << d << endl << r << endl;
		cout<<"<END> 0" << endl;
		
		a = 1; b = 1; c = 1; d = 1; r = 0;
		r = d; r += c; c = r; r += b; b = r; r += a; a = r;
		cout << a << endl << b << endl << c << endl << d << endl << r << endl;
		cout<<"<END> 1" << endl;
		
		a = 1; b = 1; c = 1; d = 1; r = 0;
		c += d; b += c; a += b; r = a;
		cout << a << endl << b << endl << c << endl << d << endl << r << endl;
		cout<<"<END> 2" << endl;
	
		return 0;
	}
	"""
	data.sequence[c] += data.sequence[d]
	data.sequence[b] += data.sequence[c]
	data.sequence[a] += data.sequence[b]
	return data.sequence[a]
