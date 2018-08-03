#!/usr/bin/env python3

import unittest

from codename import Env, Word, ScoredWord, Phrase, Codename


class TestCodename(unittest.TestCase):

    def test_word(self):
        e = Env()

        w = Word(e, "hello")
        self.assertIsNotNone(w.word, msg="expected word defined")
        self.assertIsNotNone(w.genes(), msg="expected genes defined")

    def test_word_breeding(self):
        e = Env()

        w1 = Word(e, "hello")
        w2 = Word(e, "world")

        self.assertNotEqual("", w1.breed(w2),
                            msg="expected nonempty baby word 1")

        w1 = Word(e, "")
        w2 = Word(e, "world")

        self.assertNotEqual("", w1.breed(w2),
                            msg="expected nonempty baby word 2")

        w1 = Word(e, "hello")
        w2 = Word(e, "")

        self.assertNotEqual("", w1.breed(w2),
                            msg="expected nonempty baby word 3")

        w1 = Word(e, "")
        w2 = Word(e, "")

        self.assertEqual("", w1.breed(w2),
                         msg="expected empty baby word")

    def test_scrabble_and_gene_scores(self):
        e = Env()

        e.gene_len = 2
        e.gene_scores = {'ap': 5,
                         'pp': 6,
                         'zo': 1,
                         'oo': 10}

        # { word: (expected scrabble score, expected gene score) }
        test_data = {
                "apple": (9, 11),
                "bee": (5, 0),
                "cat": (5, 0),
                "zoo": (12, 11),
        }

        for w, s in test_data.items():
            word = ScoredWord(e, w)
            scrabble, gene = s[:]
            self.assertEqual(scrabble, word.scrabble_score,
                             msg="{} scrabble score".format(w))
            self.assertEqual(gene, word.gene_score,
                             msg="{} gene score".format(w))

    def test_word_length_scores(self):
        e = Env()

        e.gene_len = 2
        e.gene_scores = {}
        e.word_min = 4
        e.word_max = 6

        # using the same letters to get a score purely based on Scrabble value,
        # minus any deductions for being too long or short
        #
        # 'd' scores 2 points, and going over or under the word amounts costs
        # one point
        base_word = ScoredWord(e, "dddd")
        short_word = ScoredWord(e, "dd")
        long_word = ScoredWord(e, "dddddddd")

        self.assertNotEqual(0, base_word.score,
                            msg="expected test word to have a score")
        self.assertTrue(base_word.score > short_word.score,
                        msg="expected base word > short word")
        self.assertTrue(long_word.score > base_word.score,
                        msg="expected long word > base word")

        self.assertTrue(long_word.score < long_word.scrabble_score,
                        msg="expected long word penalty")
        self.assertTrue(short_word.score < short_word.scrabble_score,
                        msg="expected short word penalty")

        self.assertEqual(2*2 - 2, short_word.score)
        self.assertEqual(2*8 - 2, long_word.score)

    def test_phrase_score_is_sum(self):
        e = Env()

        w1 = ScoredWord(e, "hello")
        w2 = ScoredWord(e, "world")
        p = Phrase(e, [w1, w2])

        self.assertEqual(w1.score + w2.score, p.score,
                         msg="expected phrase score to be sum of words")

    def test_compute_gene_scores(self):
        e = Env()
        e.gene_len = 2

        self.assertEqual(0, len(e.gene_scores), "expected no gene scores yet")

        c = Codename(e,
                     corpus=["apple", "banana", "cherry", "cheese", "chalk"])

        self.assertIsNotNone(c, msg="making flake8 happy with unused variable")

        # initializing c initializes e.gene_scores
        self.assertNotEqual(0, len(e.gene_scores), "expected gene scores")

        self.assertTrue(e.gene_scores.get('ch') > 0,
                        "expected gene score for 'ch'")
        self.assertTrue(e.gene_scores.get('pp') > 0,
                        "expected gene score for 'pp'")
        self.assertTrue(e.gene_scores.get('ch') > e.gene_scores.get('pp'),
                        "expected 'ch' score > 'pp' score")

    def test_build_population(self):
        e = Env(phrase_len=2)
        c = Codename(e,
                     corpus=["apple", "banana", "cherry", "cheese", "chalk"])
        self.assertEqual(2, len(c.population),
                         msg="expected initialized population 1")

        e.phrase_len = 1
        c = Codename(e,
                     corpus=["apple", "banana", "cherry", "cheese", "chalk"])
        self.assertEqual(5, len(c.population),
                         msg="expected initialized population 2")

        e.phrase_len = 5
        c = Codename(e,
                     corpus=["apple", "banana", "cherry", "cheese", "chalk"])
        self.assertEqual(1, len(c.population),
                         msg="expected initialized population 3")

        e.phrase_len = 10
        c = Codename(e,
                     corpus=["apple", "banana", "cherry", "cheese", "chalk"])
        self.assertEqual(0, len(c.population),
                         msg="expected empty population")

    def test_reduce_population(self):
        e = Env(phrase_len=1,
                word_min=1,
                pop_size=10)

        # words 'a', 'b', 'c', ... 'z'
        c = Codename(e, corpus=[chr(ord('a')+i) for i in range(26)])
        self.assertEqual(26, len(c.population),
                         msg="expected full alphabet")

        c.reduce_population()
        self.assertEqual(10, len(c.population),
                         msg="expected reduced population")

    def test_breed_a_generation(self):
        e = Env(phrase_len=2,
                word_min=1,
                gene_len=2,
                pop_size=10)

        # words 'aaa', 'bbb', 'ccc', ... 'zzz'
        c = Codename(e, corpus=[chr(ord('a')+i)*3 for i in range(26)])
        self.assertEqual(13, len(c.population),
                         msg="expected phrase pairs before breed")

        c.breed()
        self.assertEqual(13 + 13//2, len(c.population),
                         msg="expected population growth after breed")

        c.reduce_population()
        self.assertEqual(10, len(c.population),
                         msg="expected reduced population")

    def test_breed_ten_generations(self):
        e = Env(phrase_len=2,
                gene_len=2,
                pop_size=10)

        # words 'aaa', 'bbb', 'ccc', ... 'zzz'
        c = Codename(e, corpus=[chr(ord('a')+i)*3 for i in range(26)])
        self.assertEqual(13, len(c.population),
                         msg="expected phrase pairs before breed")

        for i in range(10):
            c.breed()
            c.reduce_population()

        self.assertEqual(10, len(c.population),
                         msg="expected reduced population")


if __name__ == "__main__":
    unittest.main()
