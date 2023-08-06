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


class local:
    def  __init__(self):
        pass

    @staticmethod
    def local_beam(problem, heuristic, k):
        path = []
        # Initialize k random states
        current_states = [problem.random_state() for _ in range(k)]
        while True:
            # Generate all the successors of the current k states
            successors = []
            for state in current_states:
                successors.extend(problem.generate_successors(state))
            if len(successors) == 0:
                break
            # Select k best states from successors
            next_states = sorted(successors, key=lambda successor: heuristic(successor, problem.goal), reverse=True)[:k]
            # If one of the next states is the goal, return it
            for next_state in next_states:
                if problem.test_goal(next_state):
                    return next_state
            # If none of the next states is better than current states, break
            if all(heuristic(next_state, problem.goal) <= heuristic(current_state, problem.goal) for next_state, current_state in zip(next_states, current_states)):
                break
            # Select the k best states from the next states
            current_states = sorted(next_states, key=lambda state: heuristic(state, problem.goal), reverse=True)[:k]
        # Return the best state from current k states
        return path,max(current_states, key=lambda state: heuristic(state, problem.goal))


    @staticmethod
    def simulated_annealing(problem,initial_temp,final_temp,max_iter):
        current_state = problem.random_state()
        current_state_h = heuristic(current_state,problem.goal)
        current_temp = initial_temp
        path = [current_state]
        iter = 0
        while current_temp > final_temp and iter < max_iter :
            next_state = problem.generate_successors(current_state)
            next_state_h = heuristic(next_state,problem.goal)
            Delta = next_state_h - current_state_h
            #if the new solution is better, accept it
            if Delta > 0 :
                current_state = next_state
                current_state_h = next_state_h
            #if it is not, accept it with some probability less than 1
            else :
                if math.exp(-Delta / current_temp) > random.uniform(0, 1) :
                    current_state = next_state
                    current_state_h = next_state_h
            #calculate temperature using logarithmic cooling schedule
            current_temp = initial_temp / math.log(iter + 1)
            iter += 1
            path = path + [current_state]
        return path,current_state




    #steepest ascent hill climbing algorithm
    @staticmethod
    def steepest_ascent_hc(problem,heuristic):
        current_state = problem.root
        path = [current_state]
        while not problem.test_goal(current_state): #loop until the current state is the goal state of the problem
                successors = problem.generate_successors(current_state)
                best_state = None
                for successor in successors:
                    if not best_state: # i changed this hb
                        best_state = successor  # i changed this hb
                    if problem.test_goal(successor) :
                        path = path + [successor]
                        return path,successor
                    elif heuristic(successor,problem.goal) < heuristic(best_state,problem.goal):
                        best_state = successor
                if  heuristic(best_state,problem.goal) <  heuristic(current_state,problem.goal):
                    current_state = best_state
                
                path = path + [best_state]
                
        return path,current_state
                
    #first choice hill climbing algorithm
    @staticmethod
    def first_choice_hc(problem,heuristic):
        current_state = problem.root
        path = [current_state]
        while not problem.test_goal(current_state):
            successors = problem.generate_successors(current_state)
            temp = current_state
            for successor in successors:
                if problem.test_goal(successor):
                        path = [successor]
                        return path,successor
                elif heuristic(successor,problem.goal) < heuristic(current_state,problem.goal):
                    current_state = successor 
                    break
            if current_state == temp :
                #going down? must return failure i guess
                    return path,None
            path = path+[current_state]
        return path,current_state

    @staticmethod
    #stochastic hill climbing algorithm
    def stochastic_hc(problem,heuristic):
        current_state = problem.root  # Initialize current solution
        path = [current_state]
        while not problem.test_goal(current_state):
            successors = problem.generate_successors(current_state) # Generate neighboring solutions
            #random.shuffle(successors)  # Shuffle the neighbors randomly to introduce stochasticity
            
            if isinstance(successors,dict):
                l = list(successors.items())
                random.shuffle(l)
                successors = dict(l)
            else:
                random.shuffle(successors)
            
            # Select the first improving neighbor, if any
            temp = current_state
            for successor in successors:
                if problem.test_goal(successor):
                        path = path + [successor]
                        return path,successor
                if   heuristic(successor,problem.goal) < heuristic(current_state,problem.goal):
                    current_state = successor
                    break
            if current_state == temp :
                #going down? must return failure i guess
                    return path,None
            path = path + [current_state]
        return path,current_state

    #random restart hill climbing algorithm
    @staticmethod
    def random_restart_hc(problem,h,max_restarts=100):
        count=0
        current_state = problem.root
        path = []
        while (not current_state or (not problem.test_goal(current_state) )) and count < max_restarts:
            path,current_state = steepest_ascent_hc(problem,h)
            count +=1
        return path,current_state



    