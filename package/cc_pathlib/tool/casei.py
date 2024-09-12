#!/usr/bin/env python3

import sys

from pathlib import Path

class Insensitive() :
	""" case insensitive path solver """
	def __init__(self, base_dir:Path=None, pattern_lst=None, cache_pth=None) :
		self.base_dir = Path(base_dir if base_dir is not None else '.').resolve()

		assert self.base_dir.is_dir(), f"ASSERT:must be an existing director:{self.base_dir}"

		self.f_map = dict()
		self.p_set = set(pattern_lst) if pattern_lst is not None else set()

		if cache_pth is not None :
			# if str(cache_dir).startswith('/tmp') :
			#       txt = str(self.p).encode('utf8')
			#       hsh = hashlib.blake2b(txt, digest_size=24, salt=b"cc")
			#       key = base64.urlsafe_b64encode(hsh.digest()).decode('ascii')

			#       self.cache_pth = cache_dir / f"{key}.pickle"
			# else :
			self.cache_pth = cache_pth.with_suffix('.pickle')

			if self.cache_pth.is_file() :
				self.f_map = self.cache_pth.load()
			else :
				self.f_map = dict()
				if pattern_lst is not None :
					self.scan(pattern_lst)
		else :
			self.cache_pth = None
			self.f_map = dict()

	def scan(self) :
		print(">>> InsensitiveDir.scan()")
		self.f_map = dict()
		for root, d_lst, f_lst in self.base_dir.walk() :
			if any(r for r in root.parts if r.startswith(".")) :
				continue
			for f in f_lst :
				u = root / f
				if u.suffix.lower() in self.p_set :
					p = u.relative_to(self.base_dir)
					k = str(p)
					q = k.lower()
					if k != q :
						# print(f"{q} -> {k}")
						self.f_map[q] = k

		if self.cache_pth is not None :
				self.cache_pth.save(self.f_map)

		return self

	def __getitem__(self, local_pth:str) :
		return self.f_map.get(local_pth.lower(), local_pth)
		
	def __truediv__(self, local_pth:str) :
		v = self.base_dir / self[local_pth]
		if not v.exists() :
			print(f"error:file not found:{local_pth}")
			self.scan()
			v = self.base_dir / self[local_pth]
		return v

if __name__ == '__main__' :
	import time

	t0 = time.time()
	cid = InsensitiveDir(pattern_lst=['.etp', '.saofd', '.ann', '.ssl', '.vsw'])
	for local_pth in sys.argv[1:] :
		z = cid / local_pth
	t1 = time.time()
	cid.scan()
	t2 = time.time()
	print(t1 - t0)
	print(t2 - t1)
	