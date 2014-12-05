#!/usr/bin/env python3

"""
setup a sample development environment for writing tree regular expressions 
"""

from tredev import Tredev

# directory with files containing parse trees as labeled brackets structure
parse_dir = "parses"

# annotation labels (i.e targets fro patterns)
labels = "change", "increase", "decrease"

# setup a development environment for writing tree regular expressions 
td = Tredev.from_parses(parse_dir, labels) 

# common prefix for all data files  
path_prefix = "sample"

# save environment data files, which will create
# 1. sample_nodes.pkl : nodes from all trees found in parse_dir
# 2. sample_annots.pkl : stores manual annotations (i.e. nodes labeled as positive or negative for a certain label)  
# 3. sample_patterns.pkl : definition of tree regular expressions
# 4. sample_scores.pkl : scores and other statistics for each pattern
td.save(path_prefix)
