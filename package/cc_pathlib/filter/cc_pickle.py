#!/usr/bin/env python3

import pickle

class _PICKLE_config_CONTEXT(dict) :
	def __init__(self, pth) :
		self.pth = pth

	def __enter__(self) :
		if not self.pth.is_file() :
			dict.__init__(self)
		else :
			dict.__init__(self, self.pth.load())
		return self
	
	def sync(self) :
		self.pth.save(self)

	def __exit__(self, exc_type, exc_value, traceback) :
		self.pth.save(self)


def pickle_to_str(obj, ** kwarg) :
	return pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)

def pickle_from_str(txt) :
	return pickle.loads(txt)

