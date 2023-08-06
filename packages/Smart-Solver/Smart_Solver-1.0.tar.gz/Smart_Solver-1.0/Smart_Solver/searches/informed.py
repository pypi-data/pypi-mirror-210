#!/usr/bin/env python3
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

class informed:

    def __init__(self):
         pass
     
    @staticmethod
    def A_Star(structer,h,g=None,depth=None):
        pq_evaluated = []
        visited = dict()
        traversed = [] #return a list of the traversed nodes
        #push root in the frontier
        structer.root.f = h(structer.root,structer.goal)
                    
        heapq.heappush(pq_evaluated,structer.root)
        while bool(pq_evaluated) :
            top_node = heapq.heappop(pq_evaluated)
            traversed.append(top_node)
            if isinstance(structer,Graph):
                visited[str(top_node.get_value())]=top_node
            if structer.test_goal(top_node) or (depth!=None and depth <= 0) :
                return [top_node,traversed]
            if depth!= None :
                depth -= 1
            for child in structer.generate_successors(top_node):
                g_value = 0
                if isinstance(structer,Graph) and not g:
                    g_value=top_node.g(child)
                elif not g :
                    g_value = child.g if child.g else 0
                else:
                    g_value = g(child,top_node)
                    
                child.f = h(child,structer.goal)+g_value
                if structer.test_goal(child) : # or (depth!=None and depth <= 0) 
                    traversed.append(child)
                    return [top_node,traversed]
                if isinstance(structer,Graph) :
                    temp,temp2 = None,None
                    try:
                        temp=visited[str(child.get_value())]
                    except :
                        temp = None
                    try:
                        temp2 = [ child.equale(i) for i in pq_evaluated].index(True)
                    except :    
                        temp2 = None
                    if not temp and not temp2 :
                        heapq.heappush(pq_evaluated,child)
                    else:
                        if (temp2 and child.equale(pq_evaluated[temp2]) and child.f<pq_evaluated[temp2].f) or (temp and child.equale(temp) and child.f<temp.f) : 
                            if temp:
                                del visited[str(child.get_value())]
                            heapq.heappush(pq_evaluated,child)            
                else:
                    temp=None
                    try:
                        temp = [ child.equale(i) for i in pq_evaluated].index(True)
                    except :    
                        temp = None
                    if not temp : #not in the pq
                        heapq.heappush(pq_evaluated,child)
                    elif child.equale(pq_evaluated[temp]) and child.f<pq_evaluated[temp].f :
                        # Add the child to the yet_to_visit list if its better or not there 
                        heapq.heappush(pq_evaluated,child)
                if not child.equale(structer.root):
                        child.set_parent(top_node)
    @staticmethod
    def backup(structer,n,h,g):
        k = structer.generate_successors(n)
        for i in k:
            # if child is not explored yet 
            if i.f == None:
                g_value = None
                if isinstance(structer,Graph) and not g:
                    g_value=n.g(i)
                elif not g :
                    g_value = i.g
                else:
                    g_value = g(i,n)
                i.f = max(n.f,g_value+h(i,structer.goal))
        if k :
                min_f = min(k)
        else:
            return
        if not ( n.f is min_f ):
            n.f = min_f.f
            try:
                if n.get_parent() :
                    informed.backup(n.get_parent(),h)
            except: 
                return 
        return 
            
    @staticmethod
    def SMA(structer,memory_limit,h,g=None):

        pq_evaluated = []
        visited = {} 
        traversed = [] #return a list of the traversed nodes
        memory_used = 1
        cut_leafs = MaxHeap()
        #push root in the frontier
        
        structer.root.f = h(structer.root,structer.goal)
        structer.root.set_parent(None)
        heapq.heappush(pq_evaluated,structer.root)
        
        if not hasattr(structer.root,'state'):
            structer.root.add_att('state',"alive")
        if structer.goal and not hasattr(structer.goal,'state'):
            structer.goal.add_att('state',"alive")
        top_node = None
        while bool(pq_evaluated) :        
            top_node = heapq.nsmallest(1,pq_evaluated)[0]
    
            traversed.append(top_node)

            if structer.test_goal(top_node)  :
                print("yay")
                return top_node,traversed
            
            if top_node.state == "impossible" or top_node.f == float('inf'): #no memory left or a dead end 
                return top_node,traversed 
            
            if isinstance(structer,Graph):
                visited[str(top_node.get_value())]=top_node
                
            
            for child in structer.generate_successors(top_node):
                if not hasattr(child,'state'): #check if its removed from its parent's successor list by setting a state to dead or alive
                    child.add_att('state',"alive")
            
                elif child.f == float('inf'):#not in parent's successor list 
                    continue
                if structer.test_goal(child) :
                    traversed.append(child)
                    return top_node,traversed
                
                if (isinstance(structer,Tree) and not child.children) or ((isinstance(structer,Graph) and (not structer.generate_successors(child)) or top_node.get_depth()+1>memory_limit)):#add depth
                    child.state =  "impossible"
                    child.f = float('inf')
                    continue #leaf node and not the goal no need for it
            
                g_value = None
                if isinstance(structer,Graph) and not g:
                    g_value=top_node.g(child)
                elif not g :
                    g_value = child.g
                else:
                    g_value = g(child,top_node)
                    
                child.f = max(top_node.f,g_value+h(child,structer.goal))  #why is it the max?
                
                if isinstance(structer,Graph) :
                    temp,temp2 = None,None
                    try:
                        temp =  visited[str(child.get_value())]
                    except :
                        temp = None
                    try:
                        temp2 = [ child.equale(i) for i in pq_evaluated].index(True)
                    except :    
                        temp2 = None
                    if not temp and not temp2 :
                        if not child.equale(structer.root):
                            child.set_parent(top_node)                             
                        heapq.heappush(pq_evaluated,child)
                    else:
                        if (temp2 and child.equale(pq_evaluated[temp2]) and child.f<pq_evaluated[temp2].f) or (temp and child.equale(temp) and child.f<temp.f) : 
                            if temp:
                                del visited[str(child.get_value())]
                            if not child.equale(structer.root):
                                child.set_parent(top_node)
                            heapq.heappush(pq_evaluated,child)            
                else: 
                    temp=None
                    try:
                        temp = [ child.equale(i) for i in pq_evaluated].index(True)
                    except :    
                        temp = None
                    if not temp :
                        if not child.equale(structer.root):
                            child.set_parent(top_node)
                        heapq.heappush(pq_evaluated,child)
                    elif child.equale(pq_evaluated[temp]) and child.f<pq_evaluated[temp].f :
                        # Add the child to the yet_to_visit list if its better or not there 
                        if not child.equale(structer.root):
                            child.set_parent(top_node)
                        heapq.heappush(pq_evaluated,child)
                memory_used  = memory_used+1
                if memory_limit <  memory_used : 
                    #get shallowest node(has been expanded) with biggest f value
                    worst =  heapq.nlargest(1,pq_evaluated)[0] #i have to change this satastructer later on 
                    pq_evaluated.remove(worst)
                    if isinstance(structer,Graph) :
                        try:
                            del visited[str(worst.get_value())]
                        except :
                            nothing = 0
                    #remove from successor list 
                    worst.f = float('inf')
                    #backup parents f score
                    if not top_node.equale(structer.root) and worst.get_parent():
                        informed.backup(structer,worst.get_parent(),h,g)
                        
                        if  worst.get_parent() not in pq_evaluated:
                            heapq.heappush(pq_evaluated,worst.get_parent())
                    memory_used = memory_used-1

            if not top_node.equale(structer.root):
                informed.backup(structer,top_node,h,g)
            heapq.heappop(pq_evaluated)
            memory_used = memory_used-1
        
        return top_node,traversed

    @staticmethod
    def itterrative_deepening_a_star(structer,h,g=None,itt=None):
        threshold  = h(structer.root,structer.goal)
        result,new_threshold,path = None,None,None
        while True :
            result,new_threshold,path = informed.recursive_itterrative_deepening_a_star(structer,structer.root,0,threshold,h,g)
            if result  : 
                return   result,new_threshold,path
            elif new_threshold == float("inf"):  #reached infinity nothing found 
                return None,new_threshold,path
            else :
                threshold = new_threshold
            if itt != None and itt <0 : 
                return result,new_threshold,path
            if itt != None : 
                itt -= 1
            print(itt)
        return None,threshold,path
    

    @staticmethod
    def recursive_itterrative_deepening_a_star(structer,node,cost,limit,h,g=None,visited={},path=[]):
        threshold = cost+h(node,structer.goal)
        node.f = threshold
        path = path + [node]
        if structer.test_goal(node):
            return node,threshold,path
        if threshold>limit:
            print('thre ')
            return None,threshold,path
        if isinstance(structer,Graph):
            visited[node.get_value()]=node

        inf = float("inf")
        for child in structer.generate_successors(node):
                r,t,p = None,None,None
                if not isinstance(structer,Graph):
                    r,t,p = informed.recursive_itterrative_deepening_a_star(structer,child,g(child,node),limit,h,g,path=path)
                elif isinstance(structer,Graph) :#and all(not child.equale(i) for i in visited) : #get the better path one if its in visited but this path costs less
                    g_value = None
                    if not g:
                        g_value = node.g(child)
                    else:
                        g_value = g(child,node)
                    temp = None
                    try:
                        temp = visited[child.get_value()]
                    except:
                        temp = None
                    if temp and temp.f > g_value+h(child,structer.goal):
                        del visited[child.get_value()]
                    elif temp :
                        continue
                    r,t,p = informed.recursive_itterrative_deepening_a_star(structer,child,g_value,limit,h,g,visited,path=path) 
                else:
                    continue
                if r :
                    return [r,t,p]
                elif t < inf :
                    inf = t
                if not child.equale(structer.root):
                        child.set_parent(node)
        return None,inf,path




    @staticmethod
    def greedy_algorithm(prblm_input, cost_function,depth = None):
        # Initialize an empty solution set
        # Create a dictionary to keep track of the nodes that have been visited
        visited = {}
        pq = []
        # Choose a starting node (can be any node in the graph/tree)
        start_node = prblm_input.root
        start_node.f = 0
        path = []
        heapq.heappush(pq,prblm_input.root)
        current = None
        # Loop until all nodes are visited
        while pq:
            # Initialize the minimum cost and edge variables
            min_cost = float('inf')
            min_edge = None
            current = heapq.heappop(pq)
            path.append(current)
            if isinstance(prblm_input, Graph):
                visited[current.get_value()]=True
            if prblm_input.test_goal(current):
                return path,current
            if depth != None and depth < 0 :
                return path,current
            # Loop through all edges in the graph/tree
            for node in prblm_input.generate_successors(current):
                    if isinstance(prblm_input, Graph):
                        try:  
                            # try checking if from this parent it hase better cos function then the older, if yes append it to the pq 
                            v = visited[node.get_value()]
                            continue 
                        except:
                            cost = cost_function(node, prblm_input.goal)
                            if cost < min_cost:
                                min_cost = cost
                                min_edge = node
                                min_edge.f = cost
                    else :
                        cost = cost_function(node, prblm_input.goal)
                        if cost < min_cost:
                            min_cost = cost
                            min_edge = node
                            min_edge.f = cost
            
            if min_edge:
                if not min_edge.equale(prblm_input.root):
                        min_edge.set_parent(current)
                heapq.heappush(pq,min_edge)
            if depth != None :
                depth-=1
        # Return the solution set
        return path,current

    @staticmethod
    def ucs(problem,g,limit=None):
        visited_nodes = {}
        nodes_to_be_expanded = PriorityQueue()
        path = []
        
        # Add the starting node to the queue
        problem.root.f = 0 
        nodes_to_be_expanded.put(problem.root)
        node = None
        while nodes_to_be_expanded:
        # if no path is present beteween two nodes 	
            #The method get removes and returns the item with the lowest cost from the nodes to be expanded
            #it gets the last node of the path list 
            node = nodes_to_be_expanded.get()
            path.append(node)
            #if we find the goal node we append its cost to the path list and return the updated path
            if problem.test_goal(node) :
                return path,node
            if limit!=None and limit < 0:
                return  path,node
            #add the node with lowest cost to the visited nodes
            if isinstance(problem, Graph):
                try:  
                    v = visited[node.get_value()]
                    continue 
                except:
                    visited_nodes[node.get_value()]=True
            for child in problem.generate_successors(node):
                    new_cost = g(child,node)  # we can use the g method here
                    child.f = new_cost
                    if not child.equale(problem.root):
                        child.set_parent(node)
                    nodes_to_be_expanded.put(child)
            if limit != None:
                limit -=1
        return path,node



    #selection methods 
    @staticmethod
    def roulette_wheel_selection(population,k,fitness):
        f_score = []
        final=[]
        result = []
        f_score = [fitness(i) for i in population]
        total_proba=sum(f_score)
        f_score = [i/total_proba for i in f_score]
        result,f_score = mergeSort(population,f_score,"dsc")
        cumulative_probs = [0]*len(f_score)
        cumulative_probs = np.cumsum(f_score)
        final_indices = np.searchsorted(cumulative_probs, np.random.rand(len(result)))
        final_indices = final_indices.astype(int)
        f_score = [f_score[i] for i in final_indices]
        final =  [result[i] for i in final_indices]
        final,_ = mergeSort(final,f_score,"asc")
        return final
    @staticmethod
    def stochastic_universal_sampling(pupulation,k,fitness):
        result = []
        f_score2 = []
        f_score = [fitness(i) for i in pupulation]
        total_proba=sum(f_score)
        distance = int(total_proba/k) if not int(total_proba/k) == 0 else 1
        start = random.randint(0,distance)
        pupulation,f_score= mergeSort(pupulation,f_score,"dsc")
        pointers = [start+i*distance for i in range(0,k)]
        cumultative = 0 
        for p in pointers:
            i = 0 
            try:
                while sum([f_score[k] for k in range(0,i+1)]) < p:
                    i += 1
            except:
                nothing = 0 #do nothing out of range cant put the if statement there or else its gonna be an infinite loop
            if(i>=len(pupulation)):
                i = i%len(pupulation)
            result = result +[pupulation[i]]
            f_score2 = f_score2 + [f_score[i]]
        result,_= mergeSort(result,f_score2,"asc")
        return result
        
    @staticmethod
    def tournament_selection(population,k,fitness):
        final = []   
        f_scores = []
        for _ in range(k):
            temp = []
            f_score = 0
            best = 0
            for i in range(len(population)):
                temp = temp + [random.choice(population)]
                if f_score < fitness(temp[-1]):
                    f_score = fitness(temp[-1])
                    best = i    
            final = final + [temp[best]]
            f_scores = f_scores + [f_score]
        final,_= mergeSort(final,f_scores,"asc") 
        return final

    #ranked 
    @staticmethod
    def tournament_selection(population,k,fitness):
        final = []   
        f_scores = []
        for _ in range(k):
            temp = None
            f_score = 0
            best = 0
            for i in range(len(population)):
                temp =  random.choice(population)
                if temp is None or f_score < fitness(temp):
                    f_score = fitness(temp)
                    best = str(temp) 
            final = final + [best]
            f_scores = f_scores + [f_score]
        final,f_scores= mergeSort(final,f_scores,"asc") 
        return final

    @staticmethod
    def linear_ranked_selection(population,k,fitness,sp=1.5):
        #sp which can take values between 1.0 (no selection pressure) and 2.0 (high selection pressure)
        if sp > 2 or sp < 1 :
            sp = 1.5
        f_score = [fitness(i) for i in population]
        result,f_score= mergeSort(population,f_score,"dsc")
        #calculating the probabilities 
        #f_score = [(sp-((2*sp-2)*((i-1)/(len(result)-1))))/len(result) for i in range(1,len(result)+1)] uses desc order
        f_score = [(2-sp+2*(sp-1)*((i-1)/(len(result)-1)))/len(result) for i in range(1,len(result)+1)] 
        chosen_indices = np.random.choice(np.arange(len(result)), size=k, p=f_score, replace=False)
        f_score = [f_score[i] for i in chosen_indices]
        result = [result[i] for i in chosen_indices]
        result,_ = mergeSort(result,f_score,"asc")
        
        return result
    @staticmethod
    def non_linear_ranked_selection(population,k,fitness,sp=1.5):
        #doesnt work if the root in non real
        #permits higher selective pressures than the linear ranking method
        if sp > 2 or sp < 1 :
            sp = 1.5
        f_score = [fitness(i) for i in population]
        result,f_score= mergeSort(population,f_score,"dsc")
        #0=(SP-1) X^(Nind-1)+SP X^(Nind-2)+...+SP X+SP.
        equation = ""
        for i in range(1,len(result)+1):
            equation+= f"+{sp}*(x**({str(len(result)-i)}))"
        equation = f"{sp-1}*"+equation[1:]+"+"+str(sp)
        equation = parse_expr(equation)
        sol = solve(Eq(equation,0))[0]  
        if isinstance(sol, complex):
            return None
        #Fitness(Pos)=Nind X^(Pos-1)/sum(X^(i-1)); i=1...Nind. x is the sol variable
        f_score = [float(((sol**(i-1))*len(result))/((1 - sol**(len(result)-1)) / (1 - sol))) for i in range(1,len(result)+1)] 
        #if not sum(f_score) == 1:
        for i in range(len(result)+1) : 
            if f_score[i]>=0  :
                f_score[i] = f_score[i]/sum(f_score) 
            else : 
                f_score.remove(f_score[i])
            
        if(len(f_score) == 0):
            return None
        chosen_indices = np.random.choice(np.arange(len(f_score)), size=k, p=f_score, replace=False)
        f_score = [f_score[i] for i in chosen_indices] 
        result = [result[i] for i in chosen_indices]
        result,_ = mergeSort(result,f_score,"asc")
        return result 
        
        
    #random usualy avoided 
    @staticmethod
    def random_selection(population,k):
        return np.random.choice(result, size=k)


    # crossover methods
    @staticmethod
    def one_point_crossover(parents,crossover_probability=.8):
        children = []
        for i in range(0,len(parents),2):
            if math.floor(random.random())  <= crossover_probability: 
                random_point = random.randint(0,len(parents[0])-1)
                children = children + [parents[i][:random_point]+parents[i+1][random_point:]]
                children = children + [parents[i][random_point:]+parents[i+1][:random_point]]
            else:
                children = children + [parents[i],parents[i+1]]

        return children

    #Uniform Crossover
    '''In this type of crossover, 
    each gene for an offspring is selected with 0.5 probability from Parent-1 and 0.5 probability from Parent-2.
    If a gene from parent – 1 is selected, the same indexed gene from parent – 2 is chosen for the other offspring. 
    It is demonstrated in the following diagram.
    '''
    @staticmethod
    def uniform_crossover(parents,crossover_probability=.8):
        children = []
        for i in range(0,len(parents),2):
            if math.floor(random.random())  <= crossover_probability: 
                mask = [random.randint(0,1) for i in range(len(parents[0]))]
                child = ""
                child2 = ""
                for i in range(len(parents[0])):
                    child = child + parents[i+mask[i]][i]
                    child2 = child2 + parents[i+1-mask[i]][i]
                children = children + [child,child2]
            else:
                children = children + [parents[i],parents[i+1]]
        return children



    #multipoint crossover
    @staticmethod
    def multipoint_crossover(parents,crossover_probability=.8,points=2):
        children = []
        if points > len(parents[0]):
            points = len(parents[0])-1
        for i in range(0,len(parents),2):
            if math.floor(random.random())  <= crossover_probability: 
                child = ""
                child2 = ""
                a = random.sample(range(1, len(parents[0])), points)
                random_points,_ = mergeSort(a,a ,"dsc" )
                parent_is = 0 
                current = 0
                for k,point in enumerate(random_points):
                    if k == len(random_points)-1:
                        point = len(parents[0])
                    child +=   parents[i+parent_is][current:point]
                    child2 +=   parents[i+1-parent_is][current:point]
                    parent_is = 1 - parent_is #permutate parents 
                    current = point
                children = children + [child,child2]
            else:
                children = children + [parents[i],parents[i+1]]
        return children




    #mutation methods 
    @staticmethod
    #Swap mutation: This method involves swapping the values of two genes within an individual's chromosome.
    def swap_mutation(generation,mutation_rate=0.01):
        for i in range(0,len(generation)-1) :
            if math.floor(random.random()) <= mutation_rate:
                random_f_point = random.randint(0,len(generation[0])-1)
                random_s_point = random.randint(0,len(generation[0])-1)
                temp = generation[i][random_f_point]
                generation[i] = generation[i][:random_f_point]+generation[i+1][random_s_point]+generation[i][random_f_point+1:]
                generation[i+1] = generation[i+1][:random_s_point]+temp+generation[i+1][random_s_point+1:]            
        return generation
    @staticmethod
    #Random mutation: This method involves randomly changing one or more genes in an individual's chromosome to a new value.
    def random_initialization(generation,genes,mutation_rate=0.01):
        for i in range(0,len(generation)) :
            if math.floor(random.random()) <= mutation_rate:
                random_point = random.randint(0,len(generation[0])-1)
                random_gene = genes[random.randint(0,len(genes)-1)]
                generation[i] = generation[i][:random_point]+random_gene+generation[i][random_point+1:]
        return generation

    @staticmethod
    def random_mutation(generation,genes,mutation_rate=0.01,genes_number=1):
        if genes_number > len(generation[0]) : 
            genes_number = len(generation[0])
        for i in range(0,len(generation)) :
            if math.floor(random.random()) <= mutation_rate:
                random_gene = copy.deepcopy(generation[i])
                for k in range(0,genes_number):
                    random_point = random.randint(0,len(generation[0])-1)
                    random_gene = genes[random.randint(0,len(genes)-1)]
                    generation[i] = generation[i][:random_point]+random_gene+generation[i][random_point+1:]
                generation[i] = generation[i][:random_point]+random_gene+generation[i][random_point+1:]
        return generation
        
        
    #Inversion mutation: This method involves reversing the order of a sequence of genes within an individual's chromosome.

    @staticmethod
    def inversion_mutation(generation,genes,mutation_rate=0.01,genes_number=1):
        if genes_number > len(generation[0]) : 
            genes_number = len(generation[0])
        for i in range(0,len(generation)) :
            if math.floor(random.random()) <= mutation_rate:
                if not genes_number :
                    genes_number = 0
                while genes_number == 0 :
                    random_point = random.randint(0,len(generation[0])-1)
                    genes_number = random.randint(0,len(generation[0])-random_point)
                    generation[i] = generation[i][:random_point]+generation[i][random_point:random_point+genes_number][::-1]+generation[i][random_point+genes_number:]
        return generation


    #Scramble mutation: This method involves reversing the order of a sequence of genes within an individual's chromosome.

    @staticmethod
    def scramble_mutation(generation,genes,mutation_rate=0.01,genes_number=1):
        if genes_number > len(generation[0]) : 
            genes_number = len(generation[0])
        for i in range(0,len(generation)) :
            if math.floor(random.random()) <= mutation_rate:
                if not genes_number :
                    genes_number = 0
                while genes_number == 0 :
                    random_point = random.randint(0,len(generation[0])-1)
                    genes_number = random.randint(0,len(generation[0])-random_point)
                    scrumbled = ''.join(random.sample(generation[i][random_point:random_point+genes_number], genes_number))
                    generation[i] = generation[i][:random_point]+scrumbled+generation[i][random_point+genes_number:]
        return generation
    
    @staticmethod
    #Boundary mutation: This method involves changing the value of a gene in an individual's chromosome to the nearest boundary value if it exceeds the allowed range.
    def boundary_mutation(generation,genes,bondary_a,bondary_b,mutation_rate=0.1,genes_number=1):
        if genes_number > len(generation[0]) : 
            genes_number = len(generation[0])
        for i in range(0,len(generation)) :
            if math.floor(random.random()) <= mutation_rate:
                for k in range(0,genes_number):
                    random_point = random.randint(0,len(generation[0])-1)
                    random_gene = genes[random.randint(0,len(genes)-1)]
                    random_gene = max(bondary_a,random_gene) #to stay in boundary 
                    random_gene = min(random_gene,bondary_b) #to stay in boundary 
                    generation[i] = generation[i][:random_point]+random_gene+generation[i][random_point+1:]
                generation[i] = generation[i][:random_point]+random_gene+generation[i][random_point+1:]
        return generation



    '''
    Gaussian mutation: This method involves adding a small random value to each gene in an individual's chromosome, with the random values drawn from a Gaussian distribution.
    '''
  
    @staticmethod
    def GA(population, fitness,genes, k=30, mutation_rate=0.01, crossover_probability=0.8, fit_limit=1, time_limit=float("inf"),selection_function="roulette_wheel",crossover_function="one_point",mutation_function="random",sp=1.5,crossover_points_number=2,mutation_genes_number=1,boundary_a=None,boundary_b=None):
            solution = None
            initial_population = []
            time = 0

            initial_population = population
            generation = 0
            path = []
            mutate,crossover,select = None,None,None
            
            if selection_function == "SUS":
                select = informed.stochastic_universal_sampling
            elif selection_function == "tournament":
                select = informed.tournament_selection
            elif selection_function == "l_ranked":
                select = informed.linear_ranked_selection
            elif selection_function == "NL_ranked":
                select = informed.non_linear_ranked_selection
            elif random  == "SUS":
                select = informed.random_selection
            else :
                select = informed.roulette_wheel_selection



            if crossover_function == "uniform" :
                crossover = informed.uniform_crossover
            elif crossover_function == "multi_point":
                crossover = informed.multipoint_crossover
            else:
                crossover = informed.one_point_crossover

            if mutation_function == "swap" :
                mutate = informed.swap_mutation
            elif mutation_function == "inverse":
                mutate = informed.inversion_mutation
            elif mutation_function == "scramble":
                mutate = informed.scramble_mutation
            elif mutation_function == "boundary":
                mutate = informed.boundary_mutation
                if not boudary_a:
                    boundary_a = min(genes)
                if not boudary_b:
                    boudary_b = max(genes)
            else:
                mutate = informed.random_mutation

            next_generation_parents,next_generation_children,next_generation_embryos=[],[],[]

            while not solution:
                
                generation +=1
                if selection_function == "random":
                    next_generation_parents = select(initial_population,k)
                elif selection_function == "NL_ranked" or selection_function == "l_ranked":
                    next_generation_parents = select(initial_population,k, fitness,sp)
                else : 
                    next_generation_parents = select(initial_population,k, fitness)


                if fitness(next_generation_parents[0])>=fit_limit:
                    return next_generation_parents[0],path

                if time_limit != float("inf") and time > time_limit:
                    return next_generation_parents[0],path

                if crossover_function=="multi_point":
                    next_generation_embryos = crossover(next_generation_parents, crossover_probability,crossover_points_number)
                
                else :
                    next_generation_embryos = crossover(next_generation_parents, crossover_probability)            

                if mutation_function == "swap":
                    next_generation_children = mutate(next_generation_embryos, mutation_rate)
                elif mutation_function == "boundary":
                    next_generation_children = mutate(next_generation_embryos,genes,boundary_a,boundary_b, mutation_rate,mutation_genes_number)
                elif mutation_function == "inverse":
                    next_generation_children = mutate(next_generation_embryos,genes,mutation_rate,mutation_genes_number)
                else :
                    next_generation_children = mutate(next_generation_embryos,genes, mutation_rate)

                initial_population = next_generation_children
                path.append(next_generation_parents[0])   
                # Check time limit
                if time_limit != float("inf"):
                    time += 1
            
            return solution,path
        
        