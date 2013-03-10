#!/usr/bin/env python3
from xml.etree import ElementTree
import sys


def stringMultiply(text, count):
	retText = ''
	for x in range(0, count):
		retText += text

	return retText


def removePrefix(name):
	if name[0] == '{':
		uri, tag = name[1:].split('}')
		return tag
	else:
		return name

def addNcxPrefix(name):
	return '{http://www.daisy.org/z3986/2005/ncx/}' + name


class Toc(object):
	''' Class representing TOC '''

	def __init__(self, rootEtree = None):
		super(Toc, self).__init__()
		self.levels = list()

		if rootEtree is not None:
			self.parseFromRootNCX(rootEtree)


	def parseFromRootNCX(self, etree):
		navmap = etree.find(addNcxPrefix('navMap'))
		for child in navmap:
			self.levels.append(TocLevel(child))

	def toXHTML(self):

		ol = ElementTree.Element('ol')

		for level in self.levels:
			level.toXHTML(ol)

		return ol


	def printTOC(self):
		for level in self.levels:
			level.printTree()




class TocLevel(object):
	''' Class representing one TOC level (h1, h2, h3, ...) '''
	def __init__(self, etree = None):
		super(TocLevel, self).__init__()
		self.text = ''
		self.href = ''
		self.subLevels = list()

		if etree is not None:
			self.parseFromNCX(etree)


	def parseFromNCX(self, etreeElement):

		navLabel = etreeElement.find(addNcxPrefix('navLabel'))
		self.text = navLabel[0].text

		content = etreeElement.find(addNcxPrefix('content'))
		self.href = content.attrib['src']

		navpoints = etreeElement.findall(addNcxPrefix('navPoint'))

		for navpoint in navpoints:

			self.addSubLevel(TocLevel(navpoint))


	def toXHTML(self, parent):

		root = ElementTree.SubElement(parent, 'li')
		a = ElementTree.SubElement(root, 'a', {'href' : self.href})
		a.text = self.text

		if len(self.subLevels) > 0:

			ol = ElementTree.SubElement(root, 'ol')

			for level in self.subLevels:
				level.toXHTML(ol)


	def addSubLevel(self, level):
			self.subLevels.append(level)


	def printTree(self, indent = 0):
		print(stringMultiply('   ', indent), self.text, ':  ', self.href)
		for sub in self.subLevels:
			sub.printTree(indent + 1)




if __name__ == '__main__':


	if len(sys.argv) is not 2:
		print('usage ncx2xhtml.py <file.ncx>', file=sys.stderr)
		sys.exit(0)

	else:
		try:
			document = ElementTree.parse(sys.argv[1])
		except FileNotFoundError:
			print("error when opening file `{}'".format(sys.argv[1]), file=sys.stderr)
			sys.exit(1)




	toc = Toc(document.getroot())

	xhtml = toc.toXHTML()

	print(ElementTree.tostring(xhtml, encoding='unicode'))













