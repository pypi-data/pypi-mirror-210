from .intwise import bits as _bits, resign as _resign
	

class UInt8(int):
	BITS_N = 8
	BITS = _bits(8)


class Int8(int):
	BITS_N = 8
	BITS = _resign(8)(_bits(8))


class UInt16(int):
	BITS_N = 16
	BITS = _bits(16)


class Int16(int):
	BITS_N = 16
	BITS = _resign(16)(_bits(16))


class UInt32(int):
	BITS_N = 32
	BITS = _bits(32)


class Int32(int):
	BITS_N = 32
	BITS = _resign(32)(_bits(32))


class UInt64(int):
	BITS_N = 64
	BITS = _bits(64)


class Int64(int):
	BITS_N = 64
	BITS = _resign(64)(_bits(64))


class UInt128(int):
	BITS_N = 128
	BITS = _bits(128)


class Int128(int):
	BITS_N = 128
	BITS = _resign(128)(_bits(128))
