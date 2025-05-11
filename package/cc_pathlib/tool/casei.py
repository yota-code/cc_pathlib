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
	fichier sous Windows sont insensibles à la casse


	"""

	def __init__(self, base_dir:Path, cache_arg=False) :
		self.base_dir = Path(base_dir).resolve()

		assert self.base_dir.is_dir(), f"ASSERT:the base_dir must be an existing director:{self.base_dir}"

		self.f_map = dict() # str(pth.resolve().relative_to(self.base_dir)).lower() -> str(pth.resolve().relative_to(self.base_dir))

		if cache_arg :
			if isinstance(cache_arg, str) or isinstance(cache_arg, Path) :
				cache_dir = Path(cache_arg).resolve().make_dirs()
			else :
				# hash based cache name is given
				txt = str(self.base_dir).encode('utf8')
				hsh = hashlib.blake2b(txt, digest_size=24, salt=b"cc_pathlib")
				key = base64.urlsafe_b64encode(hsh.digest()).decode('ascii')
				cache_dir = (Path('/tmp') / f"pathlib_{key}").make_dirs('private')
			
			self.cache_pth = cache_dir / f"insensitive.pickle"

			if self._debug :
				print(f"{__class__.__name__}.__init__() :: cache_pth = {self.cache_pth}")

			if self.cache_pth.is_file() :
				self.f_map = self.cache_pth.load()
		else :
			# cache disabled completely
			self.cache_pth = None

	def scan(self, * suffix_lst) :
		print(">>> Insensitive.scan()")

		self.f_map = dict()
		for pth in self.base_dir.iter_on_suffix(* suffix_lst) :
			p = pth.relative_to(self.base_dir)
			k = str(p)
			q = k.lower()
			if k != q :
				self.f_map[q] = k

		if self.cache_pth is not None :
			self.cache_pth.save(self.f_map)
			if self._debug :
				self.cache_pth.with_suffix('.json').save(self.f_map)

		return self

	def __getitem__(self, key:str) :
		return self.f_map.get(key.lower(), key)
		
	def __truediv__(self, key:str) :
		return self.base_dir / self[key]

if __name__ == '__main__' :
	import time

	t0 = time.time()
	base_dir = Path(sys.argv[1]).resolve()
	u = Insensitive(base_dir).scan('.etp', '.saofd', '.ann', '.ssl', '.vsw')
	t1 = time.time()
	print(t1 - t0)
