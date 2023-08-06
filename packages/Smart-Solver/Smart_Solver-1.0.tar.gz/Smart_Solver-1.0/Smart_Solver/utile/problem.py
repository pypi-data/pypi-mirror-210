import numbers
import random 
import math
import numpy as np
import copy


class Node:
    def __init__(self,value,parent=None,f=None,g=None,sibilings=[],params={}):
        if not isinstance(params,dict) :
            print("wrong type, params should be a dict {par1:value}")
            return
        if not isinstance(parent,Node) and parent:
            print("wrong type, parent must be Node or None")
            return 
        if not isinstance(sibilings,list):
            print("wrong type, sibilings must be list")
            return
            
        self.f = f
        self.g = g
        self._parent = parent
        self._sibilings = sibilings      
        if self._parent:
            self._depth = self.calculate_depth()
        else :
            self._depth = None
        self._value = value
        for key, value in params.items():
            setattr(self, key, value)
    
    def __str__(self):
        return f"{self._value}"
    
    def __lt__(self, other): 
        if self.f!= None and other.f!=None :
            return self.f < other.f 
        else:
            return self.get_value() < other.get_value()

    def __eq__(self, other): 
        if self.f!= None and other.f!=None :
            return self.f == other.f 
        else:
            return self.get_value() == other.get_value()
    
    def __le__(self,other): 
        if self.f!= None and other.f!=None :
            return self.f <= other.f 
        else:
            return self.get_value() <= other.get_value()

    def equale(self,other):
        try:
            return  self.get_value() == other.get_value() 
        except :
            return False

    
    def add_sibiling(self,children):
        if  (isinstance(children,list) and any( (not isinstance(c,Node)) for c in children)) or (not isinstance(children,list) and not isinstance(children,Node)):
            pass
            #print("wrong type,children should be a list of nodes or a node")
        if isinstance(children,list):
            for c in children:
                c._parent = self
                c._depth = c.calculate_depth()
            self._sibilings=self._sibilings+children
        elif isinstance(children,Node)  : #one element
            children._parent = self
            children._depth = children.calculate_depth()
            self._sibilings=self._sibilings+[children]         
        return True
    def drop_sibiling(self,children):
        if  (isinstance(children,list) and any(not isinstance(c,Node) for c in children)) or not isinstance(children,Node):
            print("wrong type,children should be a list of nodes or a node")
            return False
        if isinstance(children,list):
            #delete list of children
            self._sibilings = [c for c in self._sibilings if c not in children]
        else : #delete one element
            self._sibilings.remove(children)
        return True
    def drop_sibiling_index(self,index):
        if  not isinstance(index,int) :
            print("wrong type,index should be integer")
            return False
        try :
            del self._sibilings[index]
        except :
            return False
        return True
    
    def __hash__(self):
        return hash(self._value)
    def add_att(self,name,value):
        setattr(self, name, value)
    def print_sibilings(self):
        print(self,'->',[str(key) for key in self._sibilings])
    def g(self,sibiling):
        return g
    def generate_successors(self):
        return self._sibilings
    def equale(self,other):
        return self._value == other._value 
    def set_value(self,value):
        self._value = value
        return
    def set_parent(self,value):
        self._parent = value
        self._depth = self.calculate_depth()
        return
    def get_depth(self):
        if not self._parent:
            return 0
        return self._depth
    def get_parent(self):
        return self._parent
    def get_value(self):
        return self._value
    def calculate_depth(self):
        depth = 0 
        node = self
        while node :
            node = node._parent
            depth+=1
        return depth



class Point(Node):
    # 'node':{'sibiling node':cost}
    # a vertice can be add just by passing {"node_name"}
    def __init__(self,value,parent=None,f=None,cost=False,dictionary={},params={}):
        if not isinstance(cost,bool):
            print("wrong type, cost must be a boolean")
            return
        if not isinstance(params,dict) :
            print("wrong type, params should be a dict {par1:value}")
            return
        if not isinstance(parent,Point) and parent:
            print("wrong type, parent must be Point or None")
            return 
        self.cost = cost #does it hold record of costs ? boolean if yes this is the g function value,  
        if dictionary:
            if self.cost and not all(isinstance(v, numbers.Number) for w in dictionary.values() for v in w.values()) : 
                print("Wrong input in dict, must have cost")
                self._sibilings = dict()
            else:
                self._sibilings = dictionary 
        elif self.cost:
            self._sibilings = dict()
        else:
            self._sibilings = []
            
        self.f = f
        self._parent = parent
        if self._parent:
            self._depth = self.calculate_depth()
        else :
            self._depth = None
        self._value = value
        #allow user to have custom parameters 
        for key, value in params.items():
            setattr(self, key, value)
            
    def add_sibiling(self,edge_dict):
        # check if invalid input like k.add_edge({"A":{"D"}}) or k.add_edge({"A":{"D":"hello"}})
        if self.cost and not isinstance(edge_dict,dict):
            print("Wrong input must be a dict ")
            return False
        if not self.cost and not isinstance(edge_dict,list):
            print("Wrong input must be a list ")
            return False
        if  self.cost and not any(isinstance(v,numbers.Number) for v in edge_dict.values() ):
            print("Wrong input cost must be a number")
            return False
        if self.cost and not any(isinstance(v,Point) for v in edge_dict.keys() ):
            print("Wrong input should be a dict 'node':{'sibiling node':cost}")
            return False
        if self.cost :
            self._sibilings.update(edge_dict)
        else:
            self._sibilings = self._sibilings + edge_dict
        return True
    def get_sibilings(self):
        return self._sibilings
    
    def drop_sibiling(self,edge):
        try:
            if self.cost:
                self._sibilings.pop(edge) #try catch if it doesnt exists it will return an error
            else:
                self._sibilings.remove(edge)
            return True
        except :
            return False
    def add_att(self,name,value):
        setattr(self, name, value)
    def print_sibilings(self):
        if self.cost :
            print(self,'->',[str(key)+' '+str(value) for key, value in self._sibilings.items()])
        else:
            print(self,'->',[str(key) for key in self._sibilings])
    def g(self,sibiling):   
        if self.cost :
            return  self._sibilings[sibiling]
        return None




class Problem:
    def __init__(self,start_point,goal_point=None,lst=[]):
        if not isinstance(start_point,Node) :
            print("start point and end point must be of class Point")
        if not isinstance(lst,list):
            print("Problem map must be a list of Problem_Points")
        
        self.map = lst   
        self.root = start_point
        self.goal = goal_point
        self.size = len(self.map)
        
    def __str__(self):
        return f"start: {self.root}\ngoal:{self.goal}\n"
    def random_state(self):
        return self.map[random.randint(0, len(self.map)-1)]
    def test_goal(self,node):
        return self.goal == node
    def generate_successors(self,node):
        return node.generate_successors()
    

    





    
class Graph:
    def __init__(self,start_point,goal_point=None,lst=[]):
        if not isinstance(start_point,Point) or  not isinstance(goal_point,Point):
            print("start point and end point must be of class Point")
        if not isinstance(lst,list) or not any(isinstance(v,Point) for v in lst ):
            print("graph map must be a list of points")
        
        self.root = start_point
        self.goal = goal_point
        self.map = lst
        self.size = len(self.map)
    def __str__(self):
        return f"start: {self.root}\ngoal:{self.goal}\n"
    
    def random_state(self):
        return self.map[random.randint(0, len(self.map)-1)]   
    def test_goal(self,node):
        return self.goal == node
    def generate_successors(self,node):
        return node.generate_successors()



class Tree: 
    def __init__(self,root,goal,cost=False):
        self.cost = cost 
        if not isinstance(root,Node):
            print("wrong type, root shoud be a node")
        if not isinstance(goal,Node):
            print("wrong type, goal shoud be a node")
        if not isinstance(goal,Node) and goal:
            print("wrong type, goal shoud be a node or None")
        self.root = root
        if self.root.f is not None and not cost : 
            self.root.f = None
        self.goal=goal
        self.size = self.__getsize(self.root)

    def traverse(self):
        self.__traverse_tree(self.root)
    
    def __traverse_tree(self,node, depth=0):
        if node.equale(self.goal) :
            print("  "*depth , " " , node,'*' )   
        else:
            print("  "*depth , " " , node )      
        for child in node.generate_successors():
            self.__traverse_tree(child, depth+1)
    def random_state(self):
        limit = random.randint(1, 3)
        chosen = self.root
        while limit > 0 :
            if len(chosen.generate_successors())<0 :
                 continue
            chosen = chosen.generate_successors()[random.randint(0, len(chosen.generate_successors())-1)]
            limit = limit - 1 
        return chosen
    def __getsize(self, node):
        if not node:
            return 0
        size = 1
        for child in node.generate_successors():
            if child:
                size += self.__getsize(child)
        return size
    def test_goal(self,node):
        return self.goal == node
    def generate_successors(self,node):
        return node.generate_successors()
    


import sys
print(sys.getsizeof(Node))
