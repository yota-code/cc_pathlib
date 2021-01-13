#!/usr/bin/env python3

import sys

from pathlib import Path

class CaseCollation() :
	
	def __init__(self, root_dir=Path(), logger=None) :
		
		self.root_dir = root_dir.resolve()
		self.logger = logger

		self.m = dict()
		self.alternate_lst = list()

	def _cache_freeze(self) :
		pass

	def log(self, msg) :
		if self.logger is not None :
			with self.logger.open('at') as fid :
				fid.write(f"{__class__.__name__}: {msg}\n")

	def add(self, pattern) :
		for pth in self.root_dir.rglob(pattern) :
			pth = pth.relative_to(self.root_dir)
			self.m[str(pth).lower()] = pth
		return self

	def search_dir(self, pth) :
		self.alternate_lst.append(pth)

	def __getitem__(self, pth) :
		cs_pth = pth.relative_to(self.root_dir)
		ci_pth = self.m[str(pth.lower())]
		if cs_pth != ci_pth :
			self.log(f"tried to access '{cs_pth}', found '{ci_pth}' instead")
		return self.root_dir / ci_pth

	def solve(self, pth) :
		if pth.exists() :
			return pth
		rel_pth = pth.relative_to(self.root_dir)
		k = str(rel_pth).lower()
		if k in self.m :
			ci_pth = self.root_dir / self.m[k]
			if ci_pth.exists() :
				self.log(f"tried to access '{rel_pth}', found '{ci_pth.relative_to(self.root_dir)}' instead")
				return (self.root_dir / ci_pth)
		for alternate_dir in self.alternate_lst :
			k = str(alternate_dir / rel_pth).lower()
			if k in self.m :
				ci_pth = self.root_dir / self.m[str(alternate_dir / rel_pth).lower()]
				if ci_pth.exists() :
					self.log(f"tried to access '{rel_pth}', found '{ci_pth.relative_to(self.root_dir)}' instead")
					return (self.root_dir / ci_pth)

		raise FileNotFoundError("\x1b[31mError\x1b[0m:File Not Found '{0}'".format(rel_pth))