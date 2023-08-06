#!/usr/bin/env python
# -*- coding: utf-8 -*-
import uuid

class State:
    def __init__(self, left, right, dot, i, j, completed_by=None):
        self.left = left
        self.right = right
        self.dot = dot
        self.i = i
        self.j = j
        self.completed_by = completed_by or []
        self.id = int(uuid.uuid4())

    def is_complete(self):
        return self.dot >= len(self.right)

    def __eq__(self, other):
        return (
            self.left == other.left and
            self.right == other.right and
            self.dot == other.dot and
            self.i == other.i and
            self.j == other.j
        )

    def __repr__(self):
        return str(self)
    
    def __hash__(self):
        return hash(self.id)


class Earley:
    def __init__(self):
        self.grammar = []
        self.words = []
        self.chart = []    
        self.word_pos = {}

    def earley_parse(self, words, grammar):
        self.grammar = grammar
        self.words = words
        self.chart = [[] for _ in range(len(self.words) + 1)]

        self.enqueue(State('', ['S'], 0, 0, 0), 0)
        
        for i in range(len(self.words) + 1):
            for state in self.chart[i]:
                if not state.is_complete():
                    if not self.is_next_category_pos(state):
                        self.predictor(state)
                    else:
                        self.scanner(state)
                else:
                    self.completer(state)
        
        return self.chart


    def predictor(self, state):
        # Apply the predictor operation for the given state
        # Parameters:
        # - state: The current state in the Earley parser

        B = state.right[state.dot]
        j = state.j

        # Check if B is a non-terminal in the grammar
        if B in self.grammar:
            # Apply all rules for B in the grammar
            for rule in self.grammar[B]:
                self.enqueue(State(B, rule, 0, j, j), j)

    def scanner(self, state):
        # Apply the scanner operation for the given state
        # Parameters:
        # - state: The current state in the Earley parser

        B = state.right[state.dot]
        j = state.j

        # Check if there are remaining words to scan
        if j < len(self.words):
            word_i = self.words[j]

            # Check if B can be a part of speech for the current word
            if B in self.parts_of_speech(word_i):
                self.enqueue(State(B, [word_i], 1, j, (j + 1)), (j + 1))

    def completer(self, state):
        # Apply the completer operation for the given state
        # Parameters:
        # - state: The current state in the Earley parser

        B = state.left
        j, k = state.i, state.j

        # Iterate over the states in chart[j]
        for old_state in self.chart[j]:
            dot = old_state.dot

            # Check if the old_state can be completed by B
            if not old_state.is_complete() and old_state.right[dot] == B:
                i = old_state.i
                A = old_state.left
                cb = old_state.completed_by[:]

                # Create a new state by advancing the dot of old_state
                self.enqueue(State(A, old_state.right, (dot + 1), i, k, cb), k, state)

    def enqueue(self, state, chart_entry, completed_by=None):
        # Enqueue the state into the chart entry
        # Parameters:
        # - state: The state to enqueue
        # - chart_entry: The chart entry to enqueue the state into
        # - completed_by: Optional state that completed the enqueued state

        if not state in self.chart[chart_entry]:
            self.chart[chart_entry].append(state)

        if not completed_by is None and not completed_by in state.completed_by:
            state.completed_by.append(completed_by)


    def is_next_category_pos(self, state):
        # Check if the next category is a part of speech (POS)
        # Parameters:
        # - state: The current state in the Earley parser

        next_word = state.right[state.dot]

        # Check if the next_word is a terminal in the grammar
        if (not next_word in self.grammar and
                not next_word.lower() in self.grammar):
            # Next word is not a terminal
            # It might be a non-terminal or not recognized in the grammar
            return False

        # Check if the next_word produces a terminal
        return not self.grammar[next_word][0][0] in self.grammar


    # Caching by using set
    def parts_of_speech(self, word):
        if not self.word_pos:
            for l in self.grammar.keys():
                r = self.grammar[l]
                for alts in r:
                    for w in alts:
                        lower_w = w.lower()
                        if not lower_w in self.grammar:
                            if not lower_w in self.word_pos:
                                self.word_pos[lower_w] = set()
                            self.word_pos[lower_w].add(l)
        return self.word_pos[word.lower()]
