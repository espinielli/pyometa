#!/usr/bin/env python
# -*- mode: python -*-

import sys
from pyometa.boot import BootOMetaGrammar
from pyometa.builder import TreeBuilder, writePython

if len(sys.argv) != 3:
 print "Usage: generate_grammar grammar-filename python-filename"
 sys.exit(1)

grammarFile = open(sys.argv[1], 'r')
pythonFile =  open(sys.argv[2], 'w')

g = BootOMetaGrammar(grammarFile.read())
tree = g.parseGrammar("Parser", TreeBuilder)
source = writePython(tree)
pythonFile.write("from pymeta.runtime import OMetaBase as GrammarBase\n")
pythonFile.write(source)
