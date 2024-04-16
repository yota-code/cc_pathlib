#!/usr/bin/env python3

import base64
import hashlib
import sys

from cc_pathlib.path import Path

class InsensitiveDir() :
	""" case insensitive path solver """
	def __init__(self, base_dir:Path=None, cache_dir:Path=None, pattern_lst:list=None) :
		
		self.p = (Path(base_dir) if base_dir is not None else Path()).resolve()

		assert self.p.is_dir()
		
		if cache_dir is not None :
			cache_dir = Path(cache_dir).resolve()
			# if str(cache_dir).startswith('/tmp') :
			# 	txt = str(self.p).encode('utf8')
			# 	hsh = hashlib.blake2b(txt, digest_size=24, salt=b"cc")
			# 	key = base64.urlsafe_b64encode(hsh.digest()).decode('ascii')

			# 	self.cache_pth = cache_dir / f"{key}.pickle"
			# else :
			self.cache_pth = cache_dir / f"case_insensitive.pickle"

			if self.cache_pth.is_file() :
				self.m = self.cache_pth.load()
			else :
				self.m = dict()
				if pattern_lst is not None :
					self.scan(pattern_lst)
		else :
			self.cache_pth = None
			self.m = dict()

	def scan(self, pattern_lst) :
		for root, d_lst, f_lst in self.p.walk() :
			for f in f_lst :
				p = (root / f).relative_to(self.p)
				q = str(p).lower()
				if str(p) != q :
					if pattern_lst is None or p.suffix.lower() in pattern_lst :
						self.m[q] = p
		if self.cache_pth is not None :
			self.cache_pth.save(self.m)
		
	def __truediv__(self, other:str) :
		q = self.p / str(other)
		if q.is_file() :
			return q
		
		k = str(other).lower()
		if k in self.m :
			q = self.q / self.m[k]
			if q.is_file() :
				return q

		raise FileNotFoundError(f"case insensitive path does not exists:{other} in {self.p}")