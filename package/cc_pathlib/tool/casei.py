#!/usr/bin/env python3

import base64
import hashlib
import sys

from cc_pathlib import Path

class Insensitive() :

	_debug = True

	""" case insensitive path solver
	
	L'idée est de parcourir un dossier et de faire un tableau associant
	le nom d'un chemin mis en minuscule et son nom original (quand ils 
	sont différents), afin de contourner le fait que les systèmes de
	fichier sous Windows sont insensibles à la casse, alors que linux non.
	"""

	def __init__(self, base_dir:Path, cache_arg=False) :
		self.base_dir = Path(base_dir).resolve()

		assert self.base_dir.is_dir(), f"ASSERT:the base_dir must be an existing director:{self.base_dir}"

		self.f_map = dict() # str(pth.resolve().relative_to(self.base_dir)).lower() -> str(pth.resolve().relative_to(self.base_dir))

		if cache_arg :
			if isinstance(cache_arg, str) or isinstance(cache_arg, Path) :
				# if a cache_arg looks like a path, use it
				cache_dir = Path(cache_arg).resolve().make_dirs()
			else :
				# else, create a path based on a hash of base_dir
				cache_dir = (Path('/tmp') / f"pathlib_{hash(self.base_dir)}").make_dirs('private')
			
			self.cache_pth = cache_dir / f"insensitive.pickle"

			if self._debug :
				print(f"{__class__.__name__}.__init__() :: cache_pth = {self.cache_pth}")

			if self.cache_pth.is_file() :
				self.f_map = self.cache_pth.load()

		else :
			# if cache_arg is False, the cache is disabled completely
			if self._debug :
				print(f"{__class__.__name__}.__init__() :: cache disabled")

			self.cache_pth = None

	def scan(self, * suffix_lst) :
		print(">>> Insensitive.scan()")

		for pth in self.base_dir.iter_on_suffix(* suffix_lst) :
			p = pth.relative_to(self.base_dir)
			k = str(p)
			q = k.lower()
			if k != q :
				self.f_map[q] = k

		if self.cache_pth is not None :
			self.cache_pth.save(self.f_map)
			if self._debug :
				self.cache_pth.with_suffix('.json').save(self.f_map, verbose=True)

		return self

	def __getitem__(self, key:str) :
		# return the real path from one which may have the wrong casing
		return self.f_map.get(str(key).lower(), key)
		
	def __truediv__(self, key:str) :
		# resolve the real path to the base_dir
		return self.base_dir / self[key]

if __name__ == '__main__' :
	import time

	t0 = time.time()
	base_dir = Path(sys.argv[1]).resolve()
	u = Insensitive(base_dir).scan('.etp', '.saofd', '.ann', '.ssl', '.vsw')
	t1 = time.time()
	print(t1 - t0)
