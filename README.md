# In short

This libray propose to extend the capabilities of pathlib.
The Path class provided here is a sub-class of the original pathlib.Path class.

It especially enable an easy interaction with widespread file formats like json, pickle or tsv files, plain or compressed.

Options are mostly not setable, this package was meant to fit my needs, not all :D.

	from cc_pathlib import Path

# In detail

`Path.make_dirs(self, umask='shared')` is an equivalent of `Path.mkdir(parents=True, exists_ok=True)`, with the added possibility to set a umask to each directory created in-between. Especially, the default value is 'shared' for a mask value of 0o2770 (which means: available for read and write access to user and group but not others, and gid set such as each new file or directory created subsequently keep this properties).

`Path.make_parents(self, umask='shared')` same as `Path.make_dirs(self, umask='shared')` but works on files, it create the whole directory structure above it. It does not create the file though.

`Path.delete(self, content_only=False)` delete recursively if the `Path` is a directory. If `content_only=True` it keeps the root directory once emptied.

`Path.or_archive` return the name of a corresponding archive if it exists. Looking at the following extensions, in this order, `.br`, `.lz`, `.gz`. This function is meant to work on files, not on complex archives like `.tar` files.

`Path.load(self, encoding='utf-8')` is an auto-loader. The type of file is guessed from the extension

# The auto-loader

The auto-loader works in two steps :

1. if the file is compressed with one of the following extensions, it is first unzipped :
	* `.gz` for gzip
	* `.br` for brotli
	* `.lz` for lzip
2. if the file match one of the following filter, the content is properly parsed, and only the resulting object is returned:
	* `.pickle` for a pickled file
	* `.json` for a json data structure
	* `.tsv` for a tab separated value type of file, returned as a `list()` of `list()` of `str()`. The complete spec of a `.tsv` file is described below
	
	

