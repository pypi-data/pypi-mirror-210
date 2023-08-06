#!/usr/bin/env python3
import random 
import math
import numpy as np
from sympy import symbols, Eq, solve,parse_expr
import copy
import numbers
import math
from bintrees import FastAVLTree
import random
import heapq
from queue import PriorityQueue
import sys
sys.path.append("G:\\ai_project")
sys.path.append("G:\\ai_project\\src")
sys.path.append("G:\\ai_project\\src\\searches")
sys.path.append("G:\\ai_project\\src\\games")
sys.path.append("G:\\ai_project\\src\\utile")
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
                elif not g is None:
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
                elif not g is None:
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
                
                if (isinstance(structer,Tree) and not structer.generate_successors(child)) or ((isinstance(structer,Graph) and (not structer.generate_successors(child)) or top_node.get_depth()+1>memory_limit)):#add depth
                    child.state =  "impossible"
                    child.f = float('inf')
                    continue #leaf node and not the goal no need for it
            
                g_value = 0
                if isinstance(structer,Graph) and not g:
                    g_value=top_node.g(child)
                elif not g is None:
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
    def SMABT(structer,memory_limit,h,g=None):

        pq_evaluated = []
        visited = {} 
        traversed = [] #return a list of the traversed nodes
        memory_used = 1
        #push root in the frontier
        bt_evaluated = FastAVLTree()
        
        structer.root.f = h(structer.root,structer.goal)
        structer.root.set_parent(None)
        
        bt_evaluated.insert(structer.root,structer.root)
        
        if not hasattr(structer.root,'state'):
            structer.root.add_att('state',"alive")
        if structer.goal and not hasattr(structer.goal,'state'):
            structer.goal.add_att('state',"alive")
        top_node = None
        while not bt_evaluated.is_empty() :       
             
            top_node =  bt_evaluated.min_item()[0]
            
            print(top_node)
               
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
                
                if (isinstance(structer,Tree) and not structer.generate_successors(child)) or ((isinstance(structer,Graph) and (not structer.generate_successors(child)) or top_node.get_depth()+1>memory_limit)):#add depth
                    child.state =  "impossible"
                    child.f = float('inf')
                    continue #leaf node and not the goal no need for it
            
                g_value = 0
                if isinstance(structer,Graph) and not g:
                    g_value=top_node.g(child)
                elif not g is None:
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
                        temp2 = [ child.equale(i[0]) for i in bt_evaluated.items()].index(True)
                    except :    
                        temp2 = None
                    if not temp and not temp2 :
                        if not child.equale(structer.root):
                            child.set_parent(top_node) 
                        bt_evaluated.insert(child,child)                            
                    else:
                        if (temp2 and child.equale(bt_evaluated.get(temp2)) and child.f<bt_evaluated.get(temp2).f) or (temp and child.equale(temp) and child.f<temp.f) : 
                            if temp:
                                del visited[str(child.get_value())]
                            if not child.equale(structer.root):
                                child.set_parent(top_node)
                            bt_evaluated.insert(child,child)        
                else: 
                    temp=None
                    try:
                        temp = [ child.equale(i[0]) for i in bt_evaluated.items()].index(True)
                    except :    
                        temp = None
                    if not temp :
                        if not child.equale(structer.root):
                            child.set_parent(top_node)
                        bt_evaluated.insert(child,child) 
                    elif child.equale(bt_evaluated.get(temp)) and child.f<bt_evaluated.get(temp).f :
                        # Add the child to the yet_to_visit list if its better or not there 
                        if not child.equale(structer.root):
                            child.set_parent(top_node)
                        bt_evaluated.insert(child,child) 
                memory_used  = memory_used+1
                if memory_limit <  memory_used : 
                    #get shallowest node(has been expanded) with biggest f value
                    worst =  bt_evaluated.max_item()[0] #i have to change this satastructer later on 
                    
                    bt_evaluated.discard(worst)
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
                        
                        if  not  bt_evaluated.__contains__(worst.get_parent()):
                            bt_evaluated.insert(worst.get_parent(),worst.get_parent())
                    memory_used = memory_used-1

            if not top_node.equale(structer.root):
                informed.backup(structer,top_node,h,g)
            bt_evaluated.discard(top_node)
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
                    g_value = 0
                    if node.g(child):
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

    