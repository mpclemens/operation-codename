#!/usr/bin/env python3

import random


class Env():
    """
    Encapsulate preferences for scoring and breeding words:

    gene_len: letter sequence length for a gene
    word_min/word_max: preferred bounds for new words
    phrase_len: how many words make up a phrase
    gene_scores: dict of {gene: score} mappings
    pop_size: max population size of each generation
    """
    def __init__(self, gene_len=3, word_min=3, word_max=9,
                 phrase_len=2, pop_size=100):
        self.gene_len = gene_len
        self.word_min = word_min
        self.word_max = word_max
        self.phrase_len = 2
        self.gene_scores = {}
        self.pop_size = pop_size


class Word():
    """
    Base class for words, with methods to extract genes and cross-breed
    """
    def __init__(self, env, w):
        """
        Define a new word, saving settings for gene splitting.
        """
        self.env = env
        self.word = w.lower()

    def genes(self):
        """
        Return a list of genes (sequential letter substrings) of the
        given length
        """
        return [self.word[i:i+self.env.gene_len]
                for i in range(0, len(self.word) - self.env.gene_len + 1)]

    def breed(parent1, parent2):
        """
        Given two parent Words (the caller plus one other), generate a new
        string made from a random smattering of the genes of the parents,
        just like real life!
        """
        pool = parent1.genes() + parent2.genes()
        e = parent1.env

        if not pool:
            return ""

        # decides how many genes go into the "baby" word
        baby_min = min(int(e.word_min/e.gene_len + 0.5), e.gene_len)
        baby_max = e.word_max//e.gene_len
        baby_len = random.randint(baby_min, baby_max)
        return "".join(random.sample(pool, baby_len))


class ScoredWord(Word):
    """
    Derivative of Word: a word with a score set at create time
    """
    SCRABBLE = {"a": 1, "c": 3, "b": 3, "e": 1, "d": 2, "g": 2,
                "f": 4, "i": 1, "h": 4, "k": 5, "j": 8, "m": 3,
                "l": 1, "o": 1, "n": 1, "q": 10, "p": 3, "s": 1,
                "r": 1, "u": 1, "t": 1, "w": 4, "v": 4, "y": 4,
                "x": 8, "z": 10}

    def __init__(self, env, w):
        """
        Define a new word using environment settings for scoring.
        """
        super().__init__(env, w)
        self.scrabble_score = sum([ScoredWord.SCRABBLE.get(l, 0)
                                   for l in self.word])
        self.gene_score = sum([self.env.gene_scores.get(g, 0)
                               for g in self.genes()])
        self.score = self.scrabble_score + self.gene_score - \
            max(0, self.env.word_min - len(self.word)) - \
            max(0, len(self.word) - self.env.word_max)


class Phrase():
    """
    A phrase consists of one or more words, a phrase score is
    the sum of its words
    """

    def __init__(self, env, words):
        self.env = env
        self.words = words
        self.score = sum([w.score for w in words])

    def breed(phrase1, phrase2):
        """
        Breed corresponding words between the two phrases, generating a new
        phrase. If the phrases are of unequal length, the new phrase will
        be of the same length of the shortest.
        """
        baby_len = min(len(phrase1.words), len(phrase2.words))
        baby_words = []
        for i in range(baby_len):
            baby_words.append(phrase1.words[i].breed(phrase2.words[i]))

        return Phrase(phrase1.env, baby_words)


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
            w = Word(self.env, c)
            for g in w.genes():
                if g in seen_genes:
                    seen_genes[g] += 1
                else:
                    seen_genes[g] = 1
        self.env.gene_scores = seen_genes


if __name__ == "__main__":
    p = Env()
    c = Codename(p)
