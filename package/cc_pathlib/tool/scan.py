"""
scan un dossier, calcule les tailles et ou les hash

le format pour réprésenter l'arborescence des fichiers est inspirée de celle utilisées dans structarray version compacte

les lignes sont découpées par parties de chemin séparés par un /
les répétitions sont notées par une ligne qui commence par \t suivi d'un certain nombre de chiffres entre 0-9 et un /

"""

import ast
import re

from pathlib import Path

def save_map(pth, m) :
	q_lst = list()
	p_lst = list()
	for k in sorted(m) :
		n_lst = k.parts

		q = 0
		for p, n in zip(p_lst, n_lst) :
			if p != n :
				break
			q += 1
		q_lst.append((f"\0{q}/" if q else '') + Path(* n_lst[q:]) + '\t' + repr(m[k]))
	       
		p_lst = n_lst

	pth.write_text("\n".join(q_lst))

def load_map(pth) :
	r_map = dict()
	p_lst = list()

	zero_rec = re.compile(r'\0(?P<n>[0-9]+)/')
	for line in pth.read_text().splitlines() :
		k, v = line.partition('\t')
		
		zero_res = zero_rec.match(k)
		if zero_res is not None :
			n = int(zero_res['n'])
			k = k[zero_res.stop():]
		else :
			n = 0

		k_lst = p_lst[:n] + Path(k).parts
		r_map[Path(* k_lst)] = ast.literal_eval(v)
		p_lst = k_lst

	return r_map

class ScanDir() :
	def __init__(self, root_dir, cache_pth=None) :
		self.cache_pth = Path(cache_pth).resolve() if cache_pth is not None else None

