#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pydot
from cairosvg import svg2png

def tree_to_digraph(state, words, rank=[]):
    """
    Create a digraph representation of the tree rooted at the given state.

    Parameters:
    - state: The root state of the tree
    - words: The list of input words
    - rank: A list to maintain the order of states for visualization
    """
    content = f"{id(state)} [label=\"{state.left}\"]\n"

    for s in state.completed_by:
        content += f"{id(state)} -> {id(s)}\n"
        content += tree_to_digraph(s, words)

    if not state.completed_by:
        rank.append(state)

    if state.left == "S":
        for s in rank:
            if s.i < len(words):
                content += f"{id(words[s.i])} [label=\"{words[s.i]}\"]\n"
                content += f"{id(s)} -> {id(words[s.i])}\n"
        content += "{{rank=same;{}}}\n".format(" ".join(str(id(words[s.i])) for s in rank if s.i < len(words)))
        return f"digraph g {{node [shape=plaintext];\n{content}}}"

    return str(content)


def tree_to_view(state, words, output="out"):
    """
    Convert the tree rooted at the given state into an image file.

    Parameters:
    - state: The root state of the tree
    - words: The list of input words
    - output: The output filename (default: "out")
    """
    dot_string = tree_to_digraph(state, words, [])

    graphs = pydot.graph_from_dot_data(dot_string)
    svg_string = graphs[0].create_svg()

    with open(f"{output}", "wb") as f:
        svg2png(bytestring=svg_string, write_to=f)
