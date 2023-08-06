#!/usr/bin/env python
# -*- coding: utf-8 -*-

from earley import Earley
import sys
import json
import codecs
from utils import tree_to_view

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('python YAEP.py [grammar] "[sentence]"')
        exit(1)

    grammar_file = codecs.open(sys.argv[1], 'r', 'utf-8')
    words = str(sys.argv[2]).split(' ')
    grammar = json.load(grammar_file)

    chart = Earley().earley_parse(words, grammar)

    parsed = [s for s in chart[-1] if s.left == 'S']

    print(f"The sentence has {len(parsed)} abstract syntax tree.")

    for i,p in enumerate(parsed):
        try:
            tree_to_view(p,words,output=f"tree{i}")
        except:
            pass