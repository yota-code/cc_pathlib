#!/usr/bin/env python3

import io

import numpy

def numpy_to_bytes(obj, ** kwarg) :
	b = io.BytesIO()
	numpy.save(b, obj, allow_pickle=False)
	return b.getvalue()

def numpy_from_bytes(byt) :
	b = io.BytesIO(byt)
	return numpy.load(b)

