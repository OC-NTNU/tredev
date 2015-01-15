import numpy as np
import pandas as pd

from tredev.tregex import get_matches


class Patterns(pd.DataFrame):

    fields = ["pattern", "label", "comment"]
    
    def __init__(self, *args, **kwargs):
        if kwargs.get("columns") is None:
            kwargs["columns"] = self.fields
        pd.DataFrame.__init__(self, *args, **kwargs)  
    
    def add_pat(self, name, pattern, label, comment=""):
        if name not in self.index:
            self.loc[name] = pattern, label, comment
        else:
            raise ValueError("pattern with name '{}' already exists".format(name))
            
    
    
        