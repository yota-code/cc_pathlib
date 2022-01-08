#!/usr/bin/env python3

import sys

import numpy as np

from cc_pathlib import Path

u = np.mgrid[0:5,0:5]
u = np.random.random((1440, 5)).astype(np.float32)

pth = Path("test.npy")
pth.save(u)

v = pth.load()

if (u == v).all() :
	sys.exit(0)
else :
	print("ERROR")
	sys.exit(1)
