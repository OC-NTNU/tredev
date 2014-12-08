import numpy as np
import pandas as pd


class Annotations(pd.DataFrame):
    positive = 1
    unknown = 0
    negative = -1
    ignore = -2
    
    @classmethod
    def from_nodes(cls, nodes, annot_labels):
        data = np.zeros((len(nodes), len(annot_labels)), dtype=np.int8)
        data = cls.unknown
        return cls(data, columns=annot_labels, index=nodes.index)
    
    def get_value(self, node_id, label):
        return self.ix[node_id, label] 
        
    def set_positive(self, node_id, label):
        # Labels are assumed to be mutually exclusive, so if one them is
        # true, then all the others must be false. 
        # TODO: check for conflicts
        self.loc[node_id] = self.negative
        self.ix[node_id, label] = self.positive
        
    def set_negative(self, node_id, label):
        self.ix[node_id, label] = self.negative
        
    def set_unknown(self, node_id, label):
        self.ix[node_id, label] = self.unknown
        
    def set_ignore(self, node_id, label):
        self.ix[node_id, label] = self.ignore
        
    def is_positive(self, node_id, label):
        return self.ix[node_id, label] == self.positive
        
    def is_negative(self, node_id, label):
        return self.ix[node_id, label] == self.negative
    
    def is_unknown(self, node_id, label):
        return self.ix[node_id, label] == self.unknown
    
    def is_ignore(self, node_id, label):
        return self.ix[node_id, label] == self.ignore