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

class uninformed:
    def __init__(self):
         pass
    @staticmethod
    def bfs(problem): # best first search
        visited={}  
        queue=[[problem.root]]
        while queue :
            path=queue.pop(0)
            node=path[-1]
            print(node)
            if problem.test_goal(node):
                return path
            if isinstance(problem, Graph):
                temp = None
                try:
                    temp = visited[str(child.get_value())]
                except:
                    temp = None
                if temp :
                    continue
                visited[str(node.get_value())]=True
            for sb_node in problem.generate_successors(node) :
                new_path=path.copy()
                new_path.append(sb_node)
                queue.append(new_path)
        return None


    @staticmethod
    def dfs(problem) : #depth first search
        visited={}
        stack=[[problem.root]]
        i = 0 
        while stack :
            for i in stack :
                print([k.get_value() for k in i])
            print("ds")
            path=stack.pop()
            node=path[-1]
            if problem.test_goal(node):
                return path
            if isinstance(problem, Graph):
                temp = None
                try:
                    temp = visited[str(child.get_value())]
                except:
                    temp = None
                if temp :
                    continue
                visited[str(node.get_value())]=True
            successors = problem.generate_successors(node)
            for i in range(len(successors)):
                    new_path=path.copy()
                    new_path.append(problem.generate_successors(node)[len(successors)-1-i])
                    stack.append(new_path)     
        return None


    @staticmethod
    def limited_dfs(problem, depth_limit):  # limited depth first search
        visited = []
        stack = [[problem.root]]
        while stack:
            path = stack.pop()
            node = path[-1]
            if node in visited:
                continue
            visited.append(node)
            if node.equale(problem.goal):
                return path
            if len(path) >= depth_limit:
                continue
            if isinstance(problem, Graph):
                temp = None
                try:
                    temp = visited[str(child.get_value())]
                except:
                    temp = None
                if temp :
                    continue
                visited[str(node.get_value())]=True
            siblings = problem.generate_successors(node)
            for sb_node in siblings:
                new_path = path.copy()
                new_path.append(sb_node)
                stack.append(new_path)
        return None

    @staticmethod
    def iddfs(problem):  # Iterative Deepening Depth-First Search
        depth = 0
        while True:
            result = limited_dfs(problem, depth)
            if result is not None:
                return result
            depth += 1
