#!/usr/bin/env python3

from pathlib import Path

class UniversalWriter() :
	"""
	behave differently depending on the output parameter given
		output is None : open a io.String() ou io.Bytes()
		output is a Path : open the file in 'wt' or 'wb' mode
		else : out must have a write() method
	"""
	def __init__(self, output=None, mode='t') :
		self.output = output
		self.mode = mode

	def open(self) :
		if self.output is None :
			if self.mode == 't' :
				self.fid = io.StringIO()
			elif self.mode == 'b' :
				self.fid = io.BytesIO()
			else :
				raise ValueError(f"unknown mode {self.mode}")
		elif self.output == "__stack__" :
			self.output = list()
			return self.output.append
		elif isinstance(self.output, list) :
			return self.output.append
		else :
			try :
				self.fid = self.output.open('w' + self.mode)
			except AttributeError :
				self.fid = self.output
		return self.fid.write

	def close(self) :
		if self.output is None :
			self.output = self.fid.getvalue()
			return self.output
		elif isinstance(self.output, list) :
			return ''.join(self.output)
		else :
			pass

	def __enter__(self) :
		return self, self.open()

	def __exit__(self, exc_type, exc_value, traceback) :
		return self.close()