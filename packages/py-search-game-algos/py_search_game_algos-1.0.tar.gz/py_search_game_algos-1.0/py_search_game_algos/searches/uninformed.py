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
sys.path.append("G:\\ai_project")
sys.path.append("G:\\ai_project\\src")
sys.path.append("G:\\ai_project\\src\\searches")
sys.path.append("G:\\ai_project\\src\\games")
sys.path.append("G:\\ai_project\\src\\utile")
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
            print(queue)
            path=queue.pop(0)
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
            for sb_node in problem.generate_successors(node) :
                new_path=path.copy()
                new_path.append(sb_node)
                queue.append(new_path)

        return path


    @staticmethod
    def dfs(problem) : #depth first search
        visited={}
        stack=[[problem.root]]
        i = 0 
        while stack :
            path=stack.pop()
            node=path[-1]
            if problem.test_goal(node):
                return path
            if isinstance(problem, Graph):
                temp = None
                try:
                    temp = visited[str(node.get_value())]
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
        return path


    @staticmethod
    def limited_dfs(problem, depth_limit):  # limited depth first search
        visited = []
        stack = [[problem.root]]
        while stack and depth_limit > 0 :
            depth_limit -= 1 
            path = stack.pop()
            node = path[-1]
            if problem.test_goal(node):
                return path
            if isinstance(problem, Graph):
                if node in visiteG:
                    continue
                visited.append(node)
        
            if isinstance(problem, Graph):
                temp = None
                try:
                    temp = visited[str(node.get_value())]
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
        return path

    @staticmethod
    def iddfs(problem):  # Iterative Deepening Depth-First Search
        depth = 1
        while True:
            result = limited_dfs(problem, depth)
            if result is not None and problem.test_goal(result[-1]):
                return result
            depth += 1
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



    