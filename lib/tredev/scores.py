import pandas as pd

from tredev.nodes import Nodes 
from tredev.annots import Annotations



class Scores(pd.DataFrame):
    
    stats = [ "precision", "recall", "f_score",
              "positives", "negatives", "unknowns", 
              "true_pos", "false_pos", "true_neg", "false_neg" ]
    
    def __init__(self, *args, **kwargs):
        if kwargs.get("columns") is None:
            kwargs["columns"] = self.stats
        pd.DataFrame.__init__(self, *args, **kwargs)
        
    def score_pat(self, true_values, matches, name=None):
        """
        Evaluate named pattern and store scores
        
        Parameters
        ----------
        true_values: pandas.Series
            true values from manual annotation
        matches: list of (tree_n, node_n) tuples
            nodes matching the pattern
        name : str, optional
            pattern name for storing score
        """
        is_pos = true_values ==  Annotations.positive
        is_neg = true_values == Annotations.negative
        is_unk = true_values == Annotations.unknown
        
        pos = sum(is_pos)
        neg = sum(is_neg)
        unk = sum(is_unk)
        
        pred_values = true_values.copy()
        pred_values[:] = Annotations.negative 
        for tree_n, node_n in matches:
            node_id = Nodes.get_node_id(tree_n, node_n)
            pred_values.loc[node_id] = Annotations.positive
            
        is_match = pred_values == Annotations.positive
            
        tp = sum(is_pos & is_match)
        fp = sum(is_neg & is_match)
        tn = sum(is_neg & ~is_match)
        fn = sum(is_pos & ~is_match)
        
        prec = (tp / (tp + fp)) * 100
        rec = (tp / (tp + fn)) * 100
        f = 2 * ((prec * rec) / (prec + rec))
        
        scores =  prec, rec, f, pos, neg, unk, tp, fp, tn, fn
        
        if name:
            # save score
            self.loc[name, :] = scores
            
        return scores
    
    def print_score(self, scores):
        for name, score in zip(self.columns, scores):
            print("{:12s} : {:.2f}".format(name, score))

        
    