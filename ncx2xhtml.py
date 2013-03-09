#!/usr/bin/env python3
from xml.etree import ElementTree


def stringMultiply(text, count):
	retText = ''
	for x in range(0, count):
		retText += text

	return retText


class Toc(object):

	def __init__(self):
		super(Toc, self).__init__()
		self.levels = list()


	def parseFromRootNCX(self, etree):

		navmap = etree.find(addNcxPrefix('navMap'))
		for child in navmap:

			level = TocLevel()
			level.parseFromNCX(child)

			self.levels.append(level)

	def printTOC(self):
		for level in self.levels:
			level.printTree()


class TocLevel(object):

	def __init__(self):
		super(TocLevel, self).__init__()
		self.text = ''
		self.href = ''
		self.subLevels = list()

	def parseFromNCX(self, etreeElement):

		navLabel = etreeElement.find(addNcxPrefix('navLabel'))
		self.text = navLabel[0].text

		content = etreeElement.find(addNcxPrefix('content'))
		self.href = content.attrib['src']

		navpoints = etreeElement.findall(addNcxPrefix('navPoint'))

		for navpoint in navpoints:

			new = TocLevel()
			new.parseFromNCX(navpoint)
			self.addSubLevel(new)


	def addSubLevel(self, level):
			self.subLevels.append(level)


	def printTree(self, indent = 0):
		print(stringMultiply('   ', indent), self.text, ':  ', self.href)
		for sub in self.subLevels:
			sub.printTree(indent + 1)



def removePrefix(name):
	if name[0] == '{':
		uri, tag = name[1:].split('}')
		return tag
	else:
		return name

def addNcxPrefix(name):
	return '{http://www.daisy.org/z3986/2005/ncx/}' + name






document = ElementTree.parse('toc.ncx')

toc = Toc()
toc.parseFromRootNCX(document.getroot())
toc.printTOC()







