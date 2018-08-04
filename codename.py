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

    letter_weight: multiplier for letter scores for fitness
    gene_weight: multiplier for gene scores for fitness
    variety_weight: multiplier for number of different letters

    short_weight: multiplier for short-word penalty
    long_weight: multiplier for long_word penalty
    """
    def __init__(self, gene_len=3, word_min=3, word_max=9,
                 phrase_len=2, pop_size=100,
                 letter_weight=1, gene_weight=1, variety_weight=1,
                 short_weight=-1, long_weight=-1):
        self.gene_len = gene_len
        self.word_min = word_min
        self.word_max = word_max
        self.phrase_len = phrase_len
        self.pop_size = pop_size
        self.letter_weight = letter_weight
        self.gene_weight = gene_weight
        self.short_weight = short_weight
        self.variety_weight = variety_weight
        self.long_weight = long_weight

        self.gene_scores = {}


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

    def __str__(self):
        return self.word

    def genes(self):
        """
        Return a list of genes (sequential letter substrings) of the
        given length
        """
        g = self.env.gene_len
        max_genes = len(self.word)//g * g

        return [self.word[i:i+g] for i in range(0, max_genes)]

    def breed(parent1, parent2):
        """
        Given two parent Words (the caller plus one other), generate a new
        baby word starting from the caller, and splicing in a gene from
        the other parent such that the start of the gene is found in the
        new baby.

        Starting with an empty word results in an empty string, and breeding
        against an empty word results in no change.
        """

        e = parent1.env

        baby = parent1.word
        if not baby:
            return baby

        pool = set(parent2.genes())
        if not pool:
            return baby

        while pool:
            splice_me = pool.pop()
            if splice_me[0:e.gene_len-1] not in baby:
                continue

            # pick a random point where the gene may be spliced in
            pts = [i for i, v in enumerate(list(baby)) if v == splice_me[0]]
            pt = random.choice(pts)
            baby = baby[0:pt] + splice_me + baby[pt+e.gene_len:]
            break

        return baby


class ScoredWord(Word):
    """
    Derivative of Word: a word with a score set at create time
    """
    SCORES = {"a": 1, "c": 3, "b": 3, "e": 1, "d": 2, "g": 2,
              "f": 4, "i": 1, "h": 4, "k": 5, "j": 8, "m": 3,
              "l": 1, "o": 1, "n": 1, "q": 10, "p": 3, "s": 1,
              "r": 1, "u": 1, "t": 1, "w": 4, "v": 4, "y": 4,
              "x": 8, "z": 10}

    def __init__(self, env, w):
        """
        Define a new word using environment settings for scoring.
        """
        super().__init__(env, w)
        self.letter_score = sum([ScoredWord.SCORES.get(l, -1*env.letter_weight)
                                 for l in self.word])
        self.gene_score = sum([self.env.gene_scores.get(g, -1*env.gene_weight)
                               for g in self.genes()])
        self.variety_score = len(set(self.word))

        # how many letters under/over the word is compared to the bounds
        len_short = max(0, self.env.word_min - len(self.word))
        len_long = max(0, len(self.word) - self.env.word_max)

        self.score = sum([self.letter_score*env.letter_weight,
                          self.gene_score*env.gene_weight,
                          self.variety_score*env.variety_weight,
                          len_short*env.short_weight,
                          len_long*env.long_weight])

    def __str__(self):
        f = "{} {: 0.2f}:{: 0.2f}:{: 0.2f} => {: 0.2f}"
        return f.format(self.word,
                        self.letter_score, self.gene_score, self.variety_score,
                        self.score)


class Phrase():
    """
    A phrase consists of one or more words, a phrase score is
    the sum of its words
    """

    def __init__(self, env, words):
        self.env = env
        self.words = words
        self.score = sum([w.score for w in words])

    def __str__(self):
        swords = [str(w) for w in self.words]
        return "[{}] ==> {: 0.2f}".format("; ".join(swords), self.score)

    def breed(phrase1, phrase2):
        """
        Breed corresponding words between the two phrases, generating a new
        phrase. If the phrases are of unequal length, the new phrase will
        be of the same length of the shortest parent phrase.
        """
        baby_len = min(len(phrase1.words), len(phrase2.words))
        baby_words = []
        for i in range(baby_len):
            baby = phrase1.words[i].breed(phrase2.words[i])
            baby_words.append(ScoredWord(phrase1.env, baby))

        return Phrase(phrase1.env, baby_words)


class Codename():

    def __init__(self, env, corpus=None):
        """
        Set up a new codename generator. Parameters are:
        env: a Env instance
        corpus: a list of starting words
        """
        self.env = env
        self.corpus = [c for c in corpus if
                       len(c) >= env.word_min and c[0].isalpha()]
        self.compute_gene_scores()
        self.build_population()

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

    def build_population(self):
        """
        Starting with the corpus, divide up all the words into a population of
        phrases, such that each word is used at most once in the population,
        and no phrases are built without the desired number of words.
        """
        e = self.env
        pool = self.corpus[:]
        random.shuffle(pool)
        self.population = []
        for i in range(0, len(pool), e.phrase_len):
            words = pool[i:i+e.phrase_len]
            if len(words) == e.phrase_len:
                self.population.append(Phrase(e, [ScoredWord(e, w)
                                                  for w in words]))

    def reduce_population(self):
        """
        Winnow the population down to the maximum size, ensuring that the
        highest-scoring phrases are preserved for the next generation.
        The current population is replaced by this method and the previous
        is discarded.
        """
        p = sorted(self.population,
                   key=lambda x: x.score,
                   reverse=True)[:self.env.pop_size]
        self.population = p

    def breed(self):
        """
        Starting with the current population, randomly crossbreed phrases
        such that each parent phrase is used only once. After breeding,
        the population should be reduced before the next generation.
        """
        newpop = {}

        while len(newpop.keys()) < self.env.pop_size*1.5:
            p1, p2 = random.choices(self.population, k=2)
            baby = p1.breed(p2)
            newpop[str(baby)] = baby

        for p in self.population:
            newpop[str(p)] = p

        self.population = list(newpop.values())

    def print_population(self):
        for p in self.population:
            print(str(p))

    def pretty_population(self):
        for p in self.population:
            print(" ".join([w.word for w in p.words]))
