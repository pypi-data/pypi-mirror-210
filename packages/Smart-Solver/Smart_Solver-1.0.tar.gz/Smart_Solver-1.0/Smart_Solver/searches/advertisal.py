import random 
import math
import numpy as np
from sympy import symbols, Eq, solve,parse_expr
import copy
import numbers
import math
import random
import heapq
from queue import PriorityQueue
import sys
sys.path.append("D:\\ai_project")
sys.path.append("D:\\ai_project\\src")
sys.path.append("D:\\ai_project\\src\\searches")
sys.path.append("D:\\ai_project\\src\\games")
sys.path.append("D:\\ai_project\\src\\utile")
from src.utile.util import *
from src.utile.problem import *


class advertisal:
    
    def __init__():
        pass
    @staticmethod
    def min_value(problem,node,depth,evaluate,visited):
        if node:
                visited.append(node)
        if problem.generate_successors(node) == [] or (depth!=None and depth == 0) or problem.test_goal(node):
            return node, evaluate(node)
        v = float('inf')
        min_node = None
        for successor in problem.generate_successors(node):
            _, max_val = advertisal.max_value(problem,successor, depth-1,evaluate,visited)
            if max_val < v:
                v = max_val
                min_node = successor
        return min_node, v
    @staticmethod
    def max_value(problem,node, depth,evaluate,visited):
        if node:
                visited.append(node)
        if problem.generate_successors(node) == [] or (depth!=None and depth == 0) or problem.test_goal(node):
            return  node, evaluate(node)
        v = float('-inf')
        max_node = None
        for successor in  problem.generate_successors(node):
            _, min_val = advertisal.min_value(problem,successor, depth-1,evaluate,visited)
            if min_val > v:
                v = min_val
                max_node = successor
        return max_node, v
    
    @staticmethod
    def minimax(problem, max_turn, evaluate,max_depth=None):
        visited = []
        if max_turn:
            res = advertisal.max_value(problem,problem.root, max_depth,evaluate,visited)
            return res[0],res[1],visited
        else:
            res = advertisal.min_value(problem,problem.root, max_depth,evaluate,visited)
            return  res[0],res[1],visited
    @staticmethod
    def max_alphabeta(problem,node, alpha, beta,depth,evaluate,visited):
            if node:
                visited.append(node)
            if (depth!=None and depth == 0) or problem.generate_successors(node) == [] or problem.test_goal(node):
                return node,evaluate(node)
            v = float('-inf')
            best_child = None
            for child in problem.generate_successors(node):
                _, value = advertisal.min_alphabeta(problem,child, alpha, beta,depth-1,evaluate,visited)
                if value > v:
                    v = value
                    best_child = child
                alpha = max(alpha, v)
                if beta <= alpha:
                    break
            return best_child, v
    @staticmethod
    def min_alphabeta(problem,node, alpha, beta,depth,evaluate,visited):
            if node:
                visited.append(node)
            if (depth!=None and depth == 0) or problem.generate_successors(node) == [] or problem.test_goal(node):
                return node,evaluate(node)
            v = float('inf')
            best_child = None
            for child in problem.generate_successors(node):
                _, value = advertisal.max_alphabeta(problem,child, alpha, beta,depth-1,evaluate,visited)
                if value < v:
                    v = value
                    best_child = child
                beta = min(beta, v)
                if beta <= alpha:
                    break
   
            return best_child, v
   
    @staticmethod        
    def alphabeta(problem, evaluate,max_turn,depth=None,alpha=float('-inf'), beta=float('inf')):
        visited = []
        if max_turn:
            res = advertisal.max_alphabeta(problem,problem.root,alpha,beta,depth,evaluate,visited)
            return res[0],res[1],visited
        else:
            res =  advertisal.min_alphabeta(problem,problem.root,alpha,beta,depth,evaluate,visited)
            return res[0],res[1],visited


