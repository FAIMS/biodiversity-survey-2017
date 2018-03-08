#!/usr/bin/env python
#https://docs.google.com/feeds/download/documents/export/Export?id=1vEBuq5Jz_mX35zkzg_JTJC2m38n1n7B6v3Q_lJoz16Q&exportFormat=html
from bs4 import BeautifulSoup
from copy import copy, deepcopy
import os
import sys
import urllib
import re
from lxml import etree
from xml.dom import minidom
import codecs

URL_DOC       = 'https://docs.google.com/feeds/download/documents/export/Export?id=1vEBuq5Jz_mX35zkzg_JTJC2m38n1n7B6v3Q_lJoz16Q&exportFormat=html'
PATH_PICTURES = '../data/Species Photos'
PATH_HTML     = 'data/Species ID Info.docx.html'
PATH_XML      = '../vocab/animal-type.xml'

def getFiles():
    files = []
    for dirpath, dirnames, filenames in os.walk(PATH_PICTURES):
        files.append(dirpath)
        for f in filenames:
            path = os.path.join(dirpath, f)
            path = os.path.normpath(path)
            files.append(path)
    return files

def getHtmlNodes():
    urllib.urlretrieve(URL_DOC, PATH_HTML)

    with open(PATH_HTML) as html:
        soup = BeautifulSoup(html, 'html.parser')
        return list(soup.body.contents)

def htmlBoundaryFuns():
    def fun(tagName):
        return lambda n : n.name == tagName

    tags = ['h1', 'h2', 'p']
    return [fun(t) for t in tags]

def fileBoundaryFuns():
    return [lambda n : os.path.isdir(n)]

def soupToText(n):
    if not hasattr(n, 'data'):
        return
    if n.data == None:
        return
    n.data = n.data.text.strip()

def coalesceDescriptions(n):
    hasDescription = any(isDescription(c) for c in n)
    if not hasDescription:
        return

    littleDescriptions = [c.data for c in n]
    bigDescription = '\n\n'.join(littleDescriptions)
    descriptionNode = Tree([bigDescription], [], parent=n)
    n.children = [descriptionNode]

def turnDirsToImages(n):
    if not n.data:
        return
    if not os.path.isdir(n.data):
        return
    if not len(n):
        return
    n.data = n[0].data

def isDescription(n):
    return n.depth() > 3

def doesPartiallyAssymetricallyUnify(t1, t2):
    d1, d2 = t1.data, t2.data
    if not isDescription(t1):
        d1 = re.sub('[^\\w\\s\\-\\(\\)]+', '_', d1)

    return \
            d1 == d2 or \
            os.sep + d1 in d2

def doesPartiallyUnify(t1, t2):
    try:
        return doesPartiallyAssymetricallyUnify(t1, t2) or \
               doesPartiallyAssymetricallyUnify(t2, t1)
    except Exception as e:
        #print e
        return False

def partiallyUnifyTrees(t1, t2):
    unified = (t2.data, t1.data)
    t1.data, t2.data = unified, unified
    t1.unified = t2.unified = True

def unifyTrees(t1, t2, isFirstCall=True):
    if isFirstCall:
        t1, t2 = deepcopy(t1), deepcopy(t2)

    partiallyUnifyTrees(t1, t2)
    for c1 in t1:
        # Find node c2 in t2 which we can at least partly unify with c1 in t1
        for c2 in t2:
            if doesPartiallyUnify(c1, c2):
                unifyTrees(c1, c2, isFirstCall=False)

    return t1, t2

def isPartiallyUnified(t):
    return hasattr(t, 'unified') and t.unified

def findUnunified(t):
    if not isPartiallyUnified(t):
        return [t]

    ununified = []
    for c in t:
        ununified += findUnunified(c)
    return ununified

def treeToXml(t):
    emptyData = (None, None)
    if t.data == emptyData: tag = 'opts'
    elif isDescription(t):  tag = 'desc'
    else:                   tag = 'opt'

    if isDescription(t):        path, text = '', t.data
    elif isPartiallyUnified(t): path, text = t.data
    else:                       path, text = '', t.data

    if path:
        path = path.split(os.sep)[-3:]
        path = os.sep.join(path)

    xml = etree.Element(tag)
    xml.extend([treeToXml(c) for c in t])
    if t.data != emptyData:
        if path:
            xml.attrib['p'] = path
        xml.text = text
    return xml

def prettyPrintLxml(t):
    xmlDec = '<?xml version="1.0" ?>\n'
    xmlString = etree.tostring(t)
    dom = minidom.parseString(xmlString)
    out = dom.toprettyxml(indent='  ')
    out = out[len(xmlDec):]
    return out

class Tree:
    def __init__(self, nodeList, boundaryFuns, parent=None):
        self.parent = parent
        nodeList, boundaryFuns = copy(nodeList), copy(boundaryFuns)

        if parent == None:
            nodeList = filter(self.isAppendable, nodeList)
            nodeList = nodeList[1:]
        if not len(nodeList):
            raise Exception('Node list cannot be empty')

        self.data = None if parent == None else nodeList.pop(0)
        self.children = nodeList

        if not len(nodeList):
            return
        if not len(boundaryFuns):
            boundaryFuns = [lambda n : True]

        self.isBoundary = boundaryFuns.pop(0)

        splitted = self.getSplitted(nodeList)
        self.children = [Tree(n, boundaryFuns, parent=self) for n in splitted]

    def getBoundarySingles(self, nodeList):
        return [i for i in range(len(nodeList)) if self.isBoundary(nodeList[i])]

    def getNextBoundarySingles(self, nodeList, tagIndices):
        if len(tagIndices) == 0:
            return [0, len(nodeList)]
        return tagIndices[1:] + [len(nodeList)]

    def getBoundaryPairs(self, nodeList):
        tagIndices = self.getBoundarySingles(nodeList)
        nextTagIndices = self.getNextBoundarySingles(nodeList, tagIndices)
        return zip(tagIndices, nextTagIndices)

    def getSplitted(self, nodeList):
        boundaries = self.getBoundaryPairs(nodeList)
        return [nodeList[lo:hi] for lo, hi in boundaries]

    def isAppendable(self, node):
        try:
            return bool(node.text.strip())
        except:
            pass
        return True

    def __iter__(self):
        return iter(self.children)

    def __len__(self):
        return len(self.children)

    def __repr__(self):
        data = repr(self.data)

        children = str(self.children).replace(', ', ',\n').replace('\n', '\n\t')
        children = '(\n\t%s\n)' % children[1:-1]
        children = children.replace('\n', '\n\t')

        return 'Tree(\n\t%s,\n\t%s\n)' % (data, children)

    def sortKey(self):
        try:
            return self.data.text
        except:
            return self.data

    def doForceLastInSort(self):
        return self.depth() == 2 and len(self) == 0

    def __lt__(self, other):
        if self .doForceLastInSort(): return False
        if other.doForceLastInSort(): return True

        return self.sortKey() < other.sortKey()

    def sort(self):
        self.children.sort()
        for child in self:
            try:
                child.sort()
            except:
                pass

    def __str__(self):
        return repr(self)

    def __getitem__(self, i):
        return self.children[i]

    def depth(self):
        count = 0
        p = self
        while p != None:
            p = p.parent
            count += 1
        return count

    def apply(self, fun):
        fun(self)
        for child in self:
            child.apply(fun)

docTree = Tree(getHtmlNodes(), htmlBoundaryFuns())
dirTree = Tree(getFiles(), fileBoundaryFuns())

docTree.apply(soupToText)
docTree.apply(coalesceDescriptions)

docTree.sort()
dirTree.sort()

dirTree.apply(turnDirsToImages)
#print 'docTree'
#print docTree
#print
#print 'dirTree'
#print dirTree
#print
docTreeUnified, dirTreeUnified = unifyTrees(docTree, dirTree)
#print 'docTree unified'
#print docTreeUnified
#print
#print 'dirTree unified'
#print dirTreeUnified
#print
#print 'docTree ununified'
#print filter(lambda n : not isDescription(n), findUnunified(docTreeUnified))
#print
#print 'dirTree ununified'
#print filter(lambda n : not isDescription(n), findUnunified(dirTreeUnified))
#print
#print 'docTree xml'
docTreeXml = treeToXml(docTreeUnified)
with codecs.open(PATH_XML, 'w', 'utf-8') as f:
    xmlString = prettyPrintLxml(docTreeXml)
    f.write(xmlString)
