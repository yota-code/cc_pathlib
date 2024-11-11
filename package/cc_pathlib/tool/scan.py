"""
scan un dossier, calcule les tailles et ou les hash

le format pour réprésenter l'arborescence des fichiers est inspirée de celle utilisées dans structarray version compacte

les lignes sont découpées par parties de chemin séparés par un /
les répétitions sont notées par une ligne qui commence par \t suivi d'un certain nombre de chiffres entre 0-9 et un /

"""

import ast
import re

from cc_pathlib import Path

import xxhash

def save_map(pth, r_map) :
	q_lst = list()
	p_lst = list()
	for k in sorted(r_map) :
		n_lst = k.parts

		q = 0
		for p, n in zip(p_lst, n_lst) :
			if p != n :
				break
			q += 1
		q_lst.append((f"*{q}/" if q else '') + str(Path(* n_lst[q:])) + '\t' + repr(r_map[k]))
	       
		p_lst = n_lst

	pth.write_text("\n".join(q_lst))

def load_map(pth) :
	r_map = dict()
	p_lst = list()

	zero_rec = re.compile(r'^\*(?P<n>[0-9]+)/')
	with pth.open('rt') as fid :
		for line in fid :
			k, _, v = line.rstrip('\n').partition('\t')
			
			zero_res = zero_rec.match(k)
			if zero_res is not None :
				n = int(zero_res['n'])
				k = k[zero_res.end():]
			else :
				n = 0

			k_lst = p_lst[:n] + list(Path(k).parts)
			r_map[Path(* k_lst)] = ast.literal_eval(v)
			p_lst = k_lst

	return r_map

def compute_checksum(pth) :
	return xxhash.xxh3_64(pth.read_bytes()).digest()

class ScanDir() :
	def __init__(self, root_dir, cache_pth=None) :
		self.root_dir = Path(root_dir).resolve()
		assert self.root_dir.is_dir()

		self.cache_pth = Path(cache_pth).resolve() if cache_pth is not None else None

	def scan(self, * suffix_lst, do_checksum=False) :

		r_map = dict()
		for pth in self.root_dir.iter_recursive(* suffix_lst) :
			if do_checksum :
				v = (pth.stat().st_size, compute_checksum(pth))
			else :
				v = (pth.stat().st_size,)
			r_map[pth.relative_to(self.root_dir)] = v

		if self.cache_pth is not None :
			save_map(self.cache_pth, r_map)
			# self.cache_pth.with_suffix(".reference").write_text('\n'.join(str(i) for i in sorted(r_map)))
			# self.cache_pth.with_suffix(".loaded").write_text('\n'.join(str(i) for i in sorted(load_map(self.cache_pth))))

		return r_map

if __name__ == '__main__' :

	import sys
	u = ScanDir(Path(sys.argv[1]), Path("_scandir_cache")).scan()