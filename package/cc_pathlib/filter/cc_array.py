#!/usr/bin/en python3

import array

array_type_to_code_map = {
	'int8': 'b',
	'uint8': 'B',
	'int16': 'h',
	'uint16': 'H',
	'int32': 'l',
	'uint32': 'L',
	'int64': 'q',
	'uint64': 'Q',
	'float': 'f',
	'double': 'd',
}

def array_from_bytes(bin, c_type='float') :
	return array.array(array_type_to_code_map[c_type], bin)

def array_to_bytes(data) :
	return data.tobytes()