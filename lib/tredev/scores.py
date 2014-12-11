import pandas as pd

from tredev.nodes import Nodes 
from tredev.annots import Annotations



class Scores(pd.DataFrame):
    
    stats = [ "precision", "recall", "f_score",
              "#pred_pos", "#pred_neg",
              "#gold_pos", "#gold_neg", "#gold_unk", "#gold_ign", 
              "#true_pos", "#false_pos", "#true_neg", "#false_neg",
              "#unk_pos", "#unk_neg"]
    
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
        is_ign = true_values == Annotations.ignore
        
        gold_pos = sum(is_pos)
        gold_neg = sum(is_neg)
        gold_unk = sum(is_unk)
        gold_ign = sum(is_ign)
        
        pred_values = true_values.copy()
        pred_values[:] = Annotations.negative 
        for tree_n, node_n in matches:
            node_id = Nodes.get_node_id(tree_n, node_n)
            pred_values.loc[node_id] = Annotations.positive
            
        is_match = pred_values == Annotations.positive
        
        # predicting positives and predicted negatives (discounting nothing)
        pred_pos = sum(is_match)
        pred_neg = sum(~is_match)
         
        # true posities, false positives, true negatives and fasle negatives,  
        # discounting unknown and ignored instances 
        true_pos = sum(is_pos & is_match)
        false_pos = sum(is_neg & is_match)
        true_neg = sum(is_neg & ~is_match)
        false_neg = sum(is_pos & ~is_match)
        
        prec = (true_pos / (true_pos + false_pos)) * 100
        rec = (true_pos / (true_pos + false_neg)) * 100
        f = 2 * ((prec * rec) / (prec + rec))
        
        # unknown positives and unknown negatives,
        # discounting true, false and ignored instances
        unk_pos = sum(is_unk & is_match)
        unk_neg = sum(is_unk & ~is_match)
        
        scores =  prec, rec, f, pred_pos, pred_neg, gold_pos, gold_neg, gold_unk, gold_ign, true_pos, false_pos, true_neg, false_neg, unk_pos, unk_neg
        
        if name:
            # save score
            self.loc[name, :] = scores
            
        return scores
    
    def print_score(self, scores):
        for name, score in zip(self.columns, scores):
            print("{:12s} : {:.2f}".format(name, score))

        
    