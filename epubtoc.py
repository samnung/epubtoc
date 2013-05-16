#!/usr/bin/env python3
import sys, re
import argparse
from lxml import etree as ET
from lxml import html

XHTML = 'xhtml'
NCX = 'ncx'


XHTML_HEADER = '''<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head>
	<title></title>
</head>
<body>
<nav epub:type="toc">
'''
XHTML_FOOTER = '''</nav>
</body>
</html>
'''

NCX_HEADER = '''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN"
 "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:isbn" content="urn:isbn:" />
    <meta name="dtb:depth" content="1" />
    <meta name="dtb:totalPageCount" content="1" />
    <meta name="dtb:maxPageNumber" content="1" />
  </head>
  <docTitle>
    <text></text>
  </docTitle>
 '''

NCX_FOOTER = '''</ncx>'''


def errorExit(str, exitCode=None):
	''' prints error to STDERR and exit if exitCode is defined '''
	print('Error: ' + str, file=sys.stderr)
	if exitCode is not None:
		sys.exit(exitCode)


def removePrefix(name):
	if name[0] == '{':
		uri, tag = name[1:].split('}')
		return tag
	else:
		return name


def addNcxPrefix(name):
	return '{http://www.daisy.org/z3986/2005/ncx/}' + name

def addXHTMLPrefix(name):
	return '{http://www.w3.org/1999/xhtml}' + name


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

	def parseFromRootXHTML(self, etree):
		body = etree.find('body')
		nav = body.find('nav')

		lis = nav.findall('ol/li')

		for li in lis:
			level = TocLevel()
			level.parseFromXHTMl(li)
			self.levels.append(level)

	def toXHTML(self):

		ol = ET.Element('ol')

		for level in self.levels:
			level.toXHTML(ol)

		return ol

	def toNCX(self, orderNumber = 1):

		navMap = ET.Element('navMap')

		for level in self.levels:
			orderNumber = level.toNCX(navMap, orderNumber)

		return navMap

	def printTOC(self):
		for level in self.levels:
			level.printTree()




class TocLevel(object):
	''' Class representing one TOC level (h1, h2, h3, ...) '''
	def __init__(self, etree = None):
		super(TocLevel, self).__init__()
		self.text = ''
		self.href = ''
		self.subLevels = []

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


	def parseFromXHTMl(self, etreeElement):

		ahref = etreeElement.find('a')
		self.href = ahref.attrib['href']
		self.text = ahref.text

		lis = etreeElement.findall('ol/li')

		for li in lis:
			newlevel = TocLevel()
			newlevel.parseFromXHTMl(li)
			self.addSubLevel(newlevel)


	def toXHTML(self, parent):

		root = ET.SubElement(parent, 'li')
		a = ET.SubElement(root, 'a', {'href' : self.href})
		a.text = self.text

		if len(self.subLevels) > 0:

			ol = ET.SubElement(root, 'ol')

			for level in self.subLevels:
				level.toXHTML(ol)


	def toNCX(self, parent, orderNumber = 1):

		navPoint = ET.SubElement(parent, 'navPoint', {'id' : 'navPoint_' + str(orderNumber), 'playOrder' : str(orderNumber)})

		navLabel = ET.SubElement(navPoint, 'navLabel')
		text = ET.SubElement(navLabel, 'text')
		text.text = self.text

		content = ET.SubElement(navPoint, 'content', {'src' : self.href})

		orderNumber += 1

		for level in self.subLevels:
			orderNumber = level.toNCX(navPoint, orderNumber)


		return orderNumber



	def addSubLevel(self, level):
			self.subLevels.append(level)


	def printTree(self, indent = 0):
		print('   '*indent, self.text, ':  ', self.href)
		for sub in self.subLevels:
			sub.printTree(indent + 1)


def parseArguments():

	""" Argument parsing, returns argparse.parse_args() object """

	args_parser = argparse.ArgumentParser()
	args_parser.add_argument('--from', choices = [NCX, XHTML], required = True, help = 'input format', dest = 'arg_from')
	args_parser.add_argument('--to', choices = [NCX, XHTML], required = True, help = 'output format', dest = 'arg_to')
	args_parser.add_argument('input', help = 'input file')
	args_parser.add_argument('output', help = 'output file')

	args = args_parser.parse_args()

	return args


if __name__ == '__main__':

	args = parseArguments()


	toc = Toc()

	try:
		if args.arg_from == XHTML:
			document = html.parse(args.input)
			toc.parseFromRootXHTML(document.getroot())
		elif args.arg_from == NCX:
			document = ET.parse(args.input)
			toc.parseFromRootNCX(document.getroot())

	except FileNotFoundError:
		errorExit("file doesn't exists `{}'".format(args.input), 2)
	except ET.ParseError:
		errorExit("invalid input format `{}'".format(args.input), 3)


	output = open(args.output, 'w')





	if args.arg_to == XHTML:
		# create xhtml string
		xhtml = XHTML_HEADER + ET.tostring(toc.toXHTML(), encoding = 'unicode', pretty_print = True) + XHTML_FOOTER

#		doc = minidom.parseString(xhtml)
#		uglyXML = doc.toprettyxml(indent='  ')

#		text_re = re.compile('>\n\s+([^<>\s].*?)\n\s+</', re.DOTALL)
#		prettyXML = text_re.sub('>\g<1></', uglyXML)

		output.write(xhtml)

	elif args.arg_to == NCX:
		ncx = NCX_HEADER + ET.tostring(toc.toNCX(), encoding = 'unicode', pretty_print = True) + NCX_FOOTER
		output.write(ncx)

