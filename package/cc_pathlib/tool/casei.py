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
	def __init__(self, base_dir:Path, pattern_lst=None, cache_arg=True) :
		self.base_dir = Path(base_dir).resolve()

		assert self.base_dir.is_dir(), f"ASSERT:the base_dir must be an existing director:{self.base_dir}"

		self.f_map = dict()

		if cache_arg :
			if isinstance(cache_arg, str) or isinstance(cache_arg, Path) :
				cache_dir = Path(cache_arg).resolve().make_dirs()
			else :
				# hash based cache name is given
				txt = str(self.base_dir).encode('utf8')
				hsh = hashlib.blake2b(txt, digest_size=24, salt=b"cc")
				key = base64.urlsafe_b64encode(hsh.digest()).decode('ascii')
				cache_dir = (Path('/tmp') / f"pathlib_{key}").make_dirs('private')
			
			self.cache_pth = cache_dir / f"insensitive.pickle"
			if self._debug :
				print(f"{__class__.__name__}.__init__() :: cache_pth = {self.cache_pth}")

			if self.cache_pth.is_file() :
				self.f_map = self.cache_pth.load()
			else :
				self.f_map = dict()
				if pattern_lst :
					self.scan(* pattern_lst)

		else :
			# cache disabled completely
			self.cache_pth = None

	def scan(self, * pattern_lst) :
		print(">>> InsensitiveDir.scan()")

		p_set = set(pattern_lst) if pattern_lst is not None else set()

		self.f_map = dict()
		for root, d_lst, f_lst in self.base_dir.walk() :
			if any(r for r in root.parts if r.startswith(".")) :
				continue
			for f in f_lst :
				u = root / f
				if u.suffix.lower() in p_set :
					p = u.relative_to(self.base_dir)
					k = str(p)
					q = k.lower()
					if k != q :
						# print(f"{q} -> {k}")
						self.f_map[q] = k

		if self.cache_pth is not None :
			self.cache_pth.save(self.f_map)
			if self._debug :
				self.cache_pth.with_suffix('.json').save(self.f_map)
		return self

	def __getitem__(self, local_nam:str) :
		return self.f_map.get(local_nam.lower(), local_nam)
		
	def __truediv__(self, local_nam:str) :
		v = self.base_dir / self[local_nam]
		if not v.exists() :
			print(f"error:file not found:{local_nam}")
			self.scan()
			v = self.base_dir / self[local_nam]
		return v

if __name__ == '__main__' :
	import time

	t0 = time.time()
	cid = InsensitiveDir(pattern_lst=['.etp', '.saofd', '.ann', '.ssl', '.vsw'])
	for local_nam in sys.argv[1:] :
		z = cid / local_nam
	t1 = time.time()
	cid.scan()
	t2 = time.time()
	print(t1 - t0)
	print(t2 - t1)
	