#!/usr/bin/env python3

import random

class Env():
    """
    Encapsulate preferences for scoring
    """
    def __init__(self, gene_len=3, word_min=3, word_max=9, phrase_len=2):
        self.gene_len = gene_len
        self.word_min = word_min
        self.word_max = word_max
        self.phrase_len = 2
        self.gene_scores = {}

class Word():
    SCRABBLE = {"a": 1, "c": 3, "b": 3, "e": 1, "d": 2, "g": 2,
                "f": 4, "i": 1, "h": 4, "k": 5, "j": 8, "m": 3,
                "l": 1, "o": 1, "n": 1, "q": 10, "p": 3, "s": 1,
                "r": 1, "u": 1, "t": 1, "w": 4, "v": 4, "y": 4,
                "x": 8, "z": 10}

    def __init__(self, env, w, compute=True):
        """
        Define a new word using environment settings for scoring. By default,
        the score is computed on creation, but for efficiency, this can be
        disabled by the 'compute' parameter
        """
        self.env = env
        self.word = w.lower()
        if compute:
            self.compute_score()
        else:
            self.score = 0

    def genes(self):
        """
        Return a list of genes (sequential letter substrings) of the
        given length
        """
        return [self.word[i:i+self.env.gene_len] for i in range(0,len(self.word) - self.env.gene_len + 1)]

    def compute_score(self):
        """
        Set the internal score variables based on the stored environment
        """
        self.scrabble_score = sum([Word.SCRABBLE.get(l,0) for l in self.word])
        self.gene_score = sum([self.env.gene_scores.get(g,0) for g in self.genes()])
        self.score = self.scrabble_score + self.gene_score - max(0, self.env.word_min - len(self.word)) - max(0, len(self.word) - self.env.word_max)

class Phrase():
    """
    A phrase consists of one or more words, a phrase score is
    the sum of its words
    """

    def __init__(self, env, words):
        self.env = env
        self.words = words
        self.compute_score()

    def compute_score(self):
        """
        Given a desired gene length, and min and max letter lengths
        of the words (inclusive), compute the overall phrase score.
        Words too long or too short lose one point per letter outside
        the thresholds.
        """
        self.score = sum([w.score for w in self.words])

class Codename():

    def __init__(self, env, corpus=None):
        """
        Set up a new codename generator. Parameters are:
        env: a Env instance
        corpus: a list of starting words
        """
        self.env = env
        self.corpus = corpus
        self.population = {}
        self.compute_gene_scores()

    def compute_gene_scores(self):
        """
        Determine gene scores in the corpus by counting frequency of
        each gene's appearance. Uses Word() to split up the corpus
        into words and genes, and the environment settings for the
        gene length
        """
        seen_genes = {}
        for c in self.corpus:
            w = Word(self.env, c, compute=False)
            for g in w.genes():
                if g in seen_genes:
                    seen_genes[g] += 1
                else:
                    seen_genes[g] = 1
        self.env.gene_scores = seen_genes

if __name__=="__main__":
    p = Env()
    c = Codename(p)
