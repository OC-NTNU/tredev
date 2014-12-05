#!/usr/bin/env python3 -u

"""
Sample session for writing tree regular expressions

Note: run setup_sample.py first to create environment data files
"""

from tredev import Tredev

# common prefix for all data files  
path_prefix = "sample"

# directory with files containing parse trees as labeled brackets structure
parse_dir = "parses"

# load data files
td = Tredev.load(path_prefix, parse_dir)

# define pattern as tree regular expression
pattern = "NP > (PP <<in > (NP <<increase))"   

# define target label
label="increase"

# start interactive annotation session
td.annotate(pattern, label)

# name pattern
name = "p1"

# store and score pattern
td.add(name, pattern, label)

# print report on scores
td.report()

# start another interactive annotation session,
# showing unknown instances only
td.annotate(pattern, label, unknown_only=True)

# recompute scores
td.rescore(name="p1")

# save environment data files
td.save(path_prefix)