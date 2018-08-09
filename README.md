# operation-codename
Goofiness to make GA-derived project- and release-names

    usage: make_codenames.py [-h] [--infile [INFILE]] [--outfile [OUTFILE]]
                             [--raw_output [RAW_OUTPUT]]
                             [--generations [GENERATIONS]] [--gene_len [GENE_LEN]]
                             [--word_min [WORD_MIN]] [--word_max [WORD_MAX]]
                             [--phrase_len [PHRASE_LEN]] [--pop_size [POP_SIZE]]
                             [--letter_weight [LETTER_WEIGHT]]
                             [--gene_weight [GENE_WEIGHT]]
                             [--variety_weight [VARIETY_WEIGHT]]

    usage: cat input.txt input.txt input.txt | make_codenames.py [...] > output.txt

CLI for codename generation.

    optional arguments:
      -h, --help                   show help message and exit
      --infile [INFILE]            source data file, or pipe from STDIN
      --outfile [OUTFILE]          output results, or pipe to STDOUT
      --raw_output                 toggle output of word and phrase scores  
      --generations [GENERATIONS]  how many iterations to run
      --gene_len [GENE_LEN]        how many letters in a row are a "gene"
      --word_min [WORD_MIN]        bounds for number of characters per word,
      --word_max [WORD_MAX]         exceeding bounds is a penalty
      --phrase_len [PHRASE_LEN]    how many words per output phrase
      --pop_size [POP_SIZE]        size of breeding population carried forward

    Scoring every word is done by a combination of the letter score from Scrabble,
    a gene score based on the frequency seen in the infile, and how many unique
    letters appear per word. Each value here is a float multiplier to adjust
    the fitness score of phrases. Turn on --raw_output to see the unweighted
    scores per word, and then the final weighted sum, including penalties for
    words that are outside the --word_min and --word_max in length

    --letter_weight [LETTER_WEIGHT]
    --gene_weight [GENE_WEIGHT]
    --variety_weight [VARIETY_WEIGHT]
