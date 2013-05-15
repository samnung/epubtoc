# ncx2xhtml

Converter from EPUB 2 TOC (ncx) to EPUB 3 TOC (xhtml). Now supports reverse way.

Output is now readable (pretty printing output XML)

# Dependecies

- lxml (for python3)

# Usage

Type into Terminal:

	python3 epubtoc.py --from ncx --to xhtml toc.ncx nav.xhtml

Or

	python3 epubtoc.py --from xhtml --to ncx nav.xhtml toc.ncx
	

# !!! Known bugs !!!

- reverse way is not fully functional, in ncx is missing id and order attributes


# TODO:

- pretty print output xhtml ✓
- reverse way (epub 3 to epub 2) ✓
- adding landmarks from .opf file