from os import listdir
from os.path import join
from collections import namedtuple

import pandas as pd



        
class Nodes(pd.DataFrame):
    NODE_OFFSET = 10 ** 3
    
    fields = ["node_id", "label", "parent", "children"]
    bracket_escapes = { "-LRB-": "(", "-RRB-": ")",
                        "-RSB-": "[", "-RSB-": "]",
                        "-LCB-": "{", "-RCB-": "}" }
    Node = namedtuple("Node", fields)
    
    @classmethod
    def get_node_id(cls, tree_n, node_n):
        return tree_n * cls.NODE_OFFSET + node_n 
    
    def get_root_node_id(self, node_id):
        node = self.get_node(node_id)
        while node.parent:
            node = self.get_node(node.parent)
        return node.name
    
    def get_node(self, node_id):
        return self.loc[node_id]
    
    def get_subtree(self, node_id, indent=0, _level=0):
        node = self.get_node(node_id)
        
        if not node.children:
            # terminal node
            subtree = node.label
        else:
            # non-terminal node            
            subtree = _level * indent * " " + "(" + node.label

            if indent and self.get_node(node.children[0]).children:
                # indented non-terminal node
                subtree += "\n"
            else:
                # non-indented or pre-terminal node, e.g. "(NN ocean)"
                subtree += " "
        
            if indent:
                subtree +=  "\n".join(self.get_subtree(child_id, indent, _level + 1) 
                                      for child_id in node.children)
            else:
                subtree +=  " ".join(self.get_subtree(child_id) 
                                     for child_id in node.children)            
            subtree += ")"  
        return subtree
    
    def get_full_tree(self, node_id, indent=0):
        return self.get_subtree(self.get_root_node_id(node_id), indent) 
    
    def get_substring(self, node_id):
        node = self.get_node(node_id)
        if not node.children:
            return self.unescape_brackets(node.label)
        
        return " ".join(self.get_substring(child_id) for child_id in node.children)
    
    @classmethod    
    def unescape_brackets(cls, label):
        """
        restore bracket escape symbols to original brackets
        """
        return cls.bracket_escapes.get(label, label)
    
    def get_sentence(self, node_id):
        return self.get_substring(self.get_root_node_id(node_id))    
    
    @classmethod
    def from_parses(cls, parse_dir):
        nodes = []
        node_id = 0
        
        for fname in listdir(parse_dir):
            if fname== ".DS_Store":
                continue
            fname = join(parse_dir, fname)
            for tree in open(fname, encoding="utf-8"):
                node_id += cls.NODE_OFFSET
                cls.parse_tree(tree, nodes, node_id)
                
        df = cls(nodes, columns=cls.fields)
        df.set_index("node_id", inplace=True)
        return df    

    @classmethod
    def parse_tree(cls, tree, nodes, node_id):
        # stack of Node objects representing path from root node up to current
        # node
        path = []
        
        for substr in tree.split():
            node_id += 1
            
            try:
                # try to get parent's id, which is the latest node on the path
                parent_id = path[-1].node_id
            except IndexError:
                # root node has no parent
                parent_id = 0
            else:
                # make current node a child of its parent
                path[-1].children.append(node_id)
    
            # create a new (non-)terminal node
            node = cls.Node(node_id, substr.strip("()"), parent_id, [])
            
            if substr.startswith("("):
                # non-terminal: push onto path stack
                path.append(node)
            else:
                # terminal: pop non-terminals from path stack, depending on the
                # number of closing brackets
                closures = substr.count(")")
                path = path[:-closures]
                
            nodes.append(node)  
