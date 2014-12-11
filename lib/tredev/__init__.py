"""
Main Tredev class
"""

import pandas as pd

from tredev.nodes import Nodes
from tredev.annots import Annotations 
from tredev.tregex import get_matches
from tredev.getch import getch
from tredev.scores import Scores
from tredev.patterns import Patterns

try:
    import nltk
except ImportError:
    pass

__all__ = ["Tredev"]


help = """
# t = true      n = next        a = pattern     e = evaluation
# f = false     p = previous    s = subtree     q = quit  
# u = unknown                   r = full tree
# i = ignore                    d = draw tree
"""


class Tredev(object):
    """
    Tredev is a wrapper around the Tregex software to support interactive
    development of tree matching patterns interleaved with manual annotation
    of instances.
    """

    def __init__(self, nodes, annots, patterns, scores, parse_dir):
        """
        Initialize Tredev data for given parse trees and annotation labels
        
        Parameters
        ----------
        nodes: tredev.nodes.Nodes instance
            nodes in all parse trees
        annots: tredev.annots.Annotations instance
            annotations associated to nodes
        patterns: tredev.patterns.Patterns instance
            tree matching patterns
        scores: tredev.scores.Scores instance
            pattern matching scores
        parse_dir: str
            directory with files containing parse trees
            
        Comments
        --------
        You probably want to use the method Tredev.from_parses or Tredev.load
        """
        self.nodes = nodes
        self.annots = annots
        self.patterns = patterns
        self.scores = scores
        self.parse_dir = parse_dir
        self.nodes_saved = False
    
    @classmethod
    def load(cls, path_prefix, parse_dir):
        """
        Load Tredev data files
        
        Parameters
        ----------
        path_prefix: str
            common file path prefix for all data files
        parse_dir: str
            directory with files containing parse trees
            
        Comments
        --------
        Reads the data files 
        <path_prefix>_nodes.pkl
        <path_prefix>_annots.pkl
        <path_prefix>_patterns.pkl
        <path_prefix>_scores.pkl
        """
        tredev = cls(pd.read_pickle(path_prefix + "_nodes.pkl"),
                     pd.read_pickle(path_prefix + "_annots.pkl"),
                     pd.read_pickle(path_prefix + "_patterns.pkl"),
                     pd.read_pickle(path_prefix + "_scores.pkl"),
                     parse_dir)
        tredev.nodes_saved = True
        return tredev
        
    @classmethod
    def from_parses(cls, parse_dir, labels):
        """
        Initialize Tredev data for given parse trees and annotation labels
        
        Parameters
        ----------
        parse_dir: str
            directory with files containing parse trees
        labels: sequence
            annotation labels
        """
        nodes = Nodes.from_parses(parse_dir)
        return cls(nodes,
                   Annotations.from_nodes(nodes, labels),
                   Patterns(),
                   Scores(),
                   parse_dir)
    
    def save(self, path_prefix):
        """
        Save Tredev data files
        
        Parameters
        ----------
        path_prefix: str
            common file path prefix for all data files
            
        Comments
        --------
        Writes the data files 
        <path_prefix>_nodes.pkl
        <path_prefix>_annots.pkl
        <path_prefix>_patterns.pkl
        <path_prefix>_scores.pkl
        
        
        """
        # The nodes file is written only once, because it does not change
        # during annotation
        if not self.nodes_saved:
            self.nodes.to_pickle(path_prefix + "_nodes.pkl")
            self.nodes_saved = True
        self.annots.to_pickle(path_prefix + "_annots.pkl")
        self.patterns.to_pickle(path_prefix + "_patterns.pkl")
        self.scores.to_pickle(path_prefix + "_scores.pkl")
        
    def add(self, name, pattern, label, comment=""):
        """
        Add a new pattern
        
        Parameters
        ----------
        name: str
            unique identifier
        pattern: str
            tree regular expression
        label: str
            targeted label
        comment: str, optional
            optional comment
        """
        if label not in self.annots.columns:
            print('*** invalid label "{}" ***'.format(label))
        else:
            self.patterns.add_pat(name, pattern, label, comment)
            self._score_pat(pattern, label, name)
        
    def remove(self, name):
        """
        Remove named pattern
        
        Parameters
        ----------
        name: str
            pattern name        
        """
        if name not in self.patterns.index:
            print('*** unknown name "{}" ***'.format(label))
        else:
            self.patterns.drop(name, inplace=True)
            self.scores.drop(name, inplace=True)
        
    def rescore(self, name=None, label=None):
        """
        Recompute scores
        
        Parameters
        ----------
        name: str, optional
            pattern name: only rescores named pattern   
        label: str, optional
            label: only rescores patterns targetting label
            
        Comments
        --------
        Prints a report of updated scores
        """
        if name:
            self._score_pat(self.patterns.at[name, "pattern"], 
                            self.patterns.at[name, "label"],
                            name)
        elif label:
            selection = self.patterns[self.patterns["label"] == label]
            for row_name, row in selection.iterrows():
                self._score_pat(row["pattern"], label, row_name)
        else:
            for row_name, row in self.patterns.iterrows():
                self._score_pat(row["pattern"], row["label"], row_name)
                
        self.report(name, label)
        
    def report(self, name=None, label=None, column="precision"):
        """
        Report pattern matching scores
        
        Parameters
        ----------
        name: str, optional
            pattern name: only scores named pattern   
        label: str, optional
            label: only scores patterns targetting label
        column: str
            column used for sorting rows
        
        Comments
        --------
        Prints a report of scores        
        """
        t = pd.merge(left=self.patterns, right=self.scores,
                     left_index=True, right_index=True)
        if name:
            # single row as DataFrame (t.loc[name] returns Series)
            t = t[t.index == name]
        elif label:
            t = t[t["label"] == label]
        # move "comment" column to the end
        cols = t.columns.tolist()
        cols.remove("comment")
        cols.append("comment")
        t = t[cols]
        t.sort(columns=column, ascending=False, inplace=True)
        print(t.to_string())
        
    def annotate(self, pattern, label, unknown_only=False):
        """
        Interactive manual annotation
        
        Parameters
        ----------
        pattern: str
            tree regular expression
        label: str
            targeted label
        unknown_only: bool
            show unknown matches only, skipping true and false matches
        """
        n = 0
        matches = get_matches(pattern, self.parse_dir)
        max_n = len(matches) - 1
        
        if unknown_only:
            all_matches = matches.copy()
            matches = [pair for pair in matches
                       if self.annots.is_unknown(Nodes.get_node_id(*pair), label)]
        else:
            all_matches = matches
        
        while matches:
            tree_n, node_n = matches[n]
            
            print(78 * "-")
            print("Match: {}/{}, Sentence: {}, Node: {}".format(
                n+1, len(matches), tree_n, node_n))
            print(78 * "-")
            
            node_id = self.nodes.get_node_id(tree_n, node_n)            
            sentence = self.nodes.get_sentence(node_id)
            substring = self.nodes.get_substring(node_id)
            
            contexts = sentence.split(substring)
            
            if len(contexts) != 2:
                print('* Warning: substring "{}" not (unique) in sentence "{}"'.format(
                    substring, sentence))
            else:
                print(contexts[0].strip())
                print("==> {} <==".format(substring))
                print(contexts[1].strip())
            
            if self.annots.is_positive(node_id, label):
                value = "True"
            elif self.annots.is_negative(node_id, label):
                value = "False"
            else:
                value = "Unknown"    
                
            print("Label:", value)        
            
            while True:
                print("?", end="", flush=True)
                try:
                    # command line
                    cmd = getch()
                    print(cmd)
                except:
                    # Wing IDE
                    cmd = input()
                
                if cmd == "a":
                    print(pattern)
                elif cmd == "d":
                    lbs = self.nodes.get_full_tree(node_id)
                    try:
                        tree = nltk.tree.Tree.fromstring(lbs)
                    except NameError:
                        print("* nltk not installed")
                    else:
                        tree.draw()
                elif cmd == "e":
                    scores = self.scores.score_pat(
                        self.annots[label], all_matches)
                    self.scores.print_score(scores)
                elif cmd == "f":
                    self.annots.set_negative(node_id, label)
                    print("# set match {}/{} to False".format(n + 1, 
                                                              len(matches)))                
                    n = min(n + 1, max_n)                
                    break   
                elif cmd == "i":
                    self.annots.set_ignore(node_id, label)
                    print("# set match {}/{} to Ignore".format(n + 1, 
                                                               len(matches)))                
                    n = min(n + 1, max_n)                
                    break   
                elif cmd == "n":
                    n = min(n + 1, max_n)
                    break
                elif cmd == "p":
                    n = max(n - 1, 0)
                    break
                elif cmd == "q":
                    print("# quit")
                    return        
                elif cmd == "t":
                    self.annots.set_positive(node_id, label)
                    print("# set match {}/{} to True".format(n + 1, 
                                                             len(matches)))                 
                    n = min(n + 1, max_n)                
                    break
                elif cmd == "r":
                    print(self.nodes.get_full_tree(node_id, indent=2))
                elif cmd == "s":
                    print(self.nodes.get_subtree(node_id, indent=2))
                elif cmd == "u":
                    self.annots.set_unknown(node_id, label)
                    print("# set match {}/{} to Unknown".format(n, len(matches)))                
                    n = min(n + 1, max_n)                
                    break
                else:
                    print("* Unknown commmand") 
                    print(help)
        else:
            print("*** pattern has zero (unknown) matches ***")
            
            
    def reannotate(self, name, unknown_only=False):
        """
        Continue interactive manual annotation for named pattern
        
        Parameters
        ----------
        name: str
            pattern name     
        unknown_only: bool
            show unknown matches only, skipping true and false matches
        """
        if name not in self.patterns.index:
            print('*** unknown name "{}" ***'.format(label))
        else:
            self.annotate(self.patterns.at[name, "pattern"], 
                          self.patterns.at[name, "label"], 
                          unknown_only)
    
    def _score_pat(self, pattern, label, name=None):
        matches = get_matches(pattern, self.parse_dir)
        return self.scores.score_pat(self.annots[label], matches, name) 
                
                    
        