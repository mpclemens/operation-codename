#!/usr/bin/env python3

import argparse
import sys

from codename import Env, Codename

parser = argparse.ArgumentParser(description="CLI for codename generation")
parser.add_argument('--infile', type=argparse.FileType('r'), nargs='?',
                    default=sys.stdin)
parser.add_argument('--outfile', type=argparse.FileType('w'), nargs='?',
                    default=sys.stdout)
parser.add_argument('--raw_output', type=bool, nargs='?', const=True)
parser.add_argument('--generations', type=int, nargs='?', default=100)

parser.add_argument('--gene_len', type=int, nargs='?', default=4)
parser.add_argument('--word_min', type=int, nargs='?', default=3)
parser.add_argument('--word_max', type=int, nargs='?', default=12)
parser.add_argument('--phrase_len', type=int, nargs='?', default=2)
parser.add_argument('--pop_size', type=int, nargs='?', default=200)
parser.add_argument('--letter_weight', type=float, nargs='?', default=0.5)
parser.add_argument('--gene_weight', type=float, nargs='?', default=1)
parser.add_argument('--variety_weight', type=float, nargs='?', default=5)
# penalties
parser.add_argument('--short_weight', type=float, nargs='?', default=-10)
parser.add_argument('--long_weight', type=float, nargs='?', default=-10)

args = parser.parse_args()

e = Env(phrase_len=args.phrase_len,
        word_min=args.word_min,
        word_max=args.word_max,
        gene_len=args.gene_len,
        pop_size=args.pop_size,
        letter_weight=args.letter_weight,
        gene_weight=args.gene_weight,
        variety_weight=args.variety_weight,
        short_weight=args.short_weight,
        long_weight=-args.long_weight)

args.outfile.write("# {}\n".format(args))

corpus = set()
for l in args.infile:
    for w in l.split():
        corpus.add(w)

c = Codename(e, corpus=corpus)

for g in range(args.generations+1):
    args.outfile.write("# Generation {}\n".format(g))
    if args.raw_output:
        c.print_population(outfile=args.outfile)
    else:
        c.pretty_population(outfile=args.outfile)
    c.breed()
    c.reduce_population()
