#!/usr/bin/env python

from Tokenizer import DEFAULT_CATEGORIES, VERBATIM_CATEGORIES
from plasTeX import Command, Environment


class alltt(Environment):

    categories = VERBATIM_CATEGORIES[:]
    categories[0] = DEFAULT_CATEGORIES[0]
    categories[1] = DEFAULT_CATEGORIES[1]
    categories[2] = DEFAULT_CATEGORIES[2]
    categories[11] = DEFAULT_CATEGORIES[11]


