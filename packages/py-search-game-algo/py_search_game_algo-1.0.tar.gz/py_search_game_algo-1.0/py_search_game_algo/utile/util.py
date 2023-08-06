import numpy as np
import copy
import numbers
import math
import random
import networkx as nx
import matplotlib.pyplot as plt
import networkx as nx
import matplotlib.pyplot as plt




class MaxHeap:
    def __init__(self):
        self.heap = []
        
    def get_parent(self, i):
        return (i-1)//2
    
    def get_left_child(self, i):
        return 2*i+1
    
    def get_right_child(self, i):
        return 2*i+2
    
    def has_parent(self, i):
        return self.get_parent(i) >= 0
    
    def has_left_child(self, i):
        return self.get_left_child(i) < len(self.heap)
    
    def has_right_child(self, i):
        return self.get_right_child(i) < len(self.heap)
    
    def swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
    
    def peek(self):
        if len(self.heap) == 0:
            return None
        return self.heap[0]
    
    def pop(self):
        if len(self.heap) == 0:
            return None
        max_value = self.heap[0]
        self.heap[0] = self.heap[-1]
        del self.heap[-1]
        self.heapify_down()
        return max_value
    
    def push(self, value):
        self.heap.append(value)
        self.heapify_up()
    
    def heapify_up(self):
        index = len(self.heap) - 1
        while (self.has_parent(index) and 
               (self.heap[index].get_depth() > self.heap[self.get_parent(index)].get_depth()
                or (self.heap[index].get_depth() == self.heap[self.get_parent(index)].get_depth()
                    and self.heap[index] > self.heap[self.get_parent(index)]))):
            self.swap(index, self.get_parent(index))
            index = self.get_parent(index)
    
    def heapify_down(self):
        index = 0
        while (self.has_left_child(index)):
            smaller_child_index = self.get_left_child(index)
            if (self.has_right_child(index) and 
                (self.heap[self.get_right_child(index)].get_depth() > self.heap[smaller_child_index].get_depth()
                 or (self.heap[self.get_right_child(index)].get_depth() == self.heap[smaller_child_index].get_depth()
                     and self.heap[self.get_right_child(index)] >= self.heap[smaller_child_index]))):
                smaller_child_index = self.get_right_child(index)
            if (self.heap[index].get_depth() > self.heap[smaller_child_index].get_depth()
                or (self.heap[index].get_depth() == self.heap[smaller_child_index].get_depth()
                    and self.heap[index] > self.heap[smaller_child_index])):
                break
            self.swap(index, smaller_child_index)
            index = smaller_child_index
            
    def print_heap(self):
        if len(self.heap) == 0:
            print("Heap is empty")
        else:
            height = int(math.ceil(math.log(len(self.heap) + 1, 2))) - 1
            nodes_in_level = 1
            current_level = 0
            current_index = 0
            while current_level <= height:
                for i in range(nodes_in_level):
                    if current_index >= len(self.heap):
                        break
                    node = self.heap[current_index]
                    print("{:^5}".format(str(node)), end="")
                    current_index += 1
                print("")
                nodes_in_level *= 2
                current_level += 1

def mergeSort(arr,f_score,way):
    if len(arr) > 1:
        mid_indx = len(arr)//2
        left = arr[:mid_indx]
        right = arr[mid_indx:]
        f_left = f_score[:mid_indx]
        f_right = f_score[mid_indx:]
        mergeSort(left,f_left,way)
        mergeSort(right,f_right,way)
        i = j = k = 0
        if way == "dsc":
            while i < len(left) and j < len(right):
                if f_left[i] <= f_right[j]:
                    f_score[k] = f_left[i]
                    arr[k] = left[i]
                    i += 1
                else:
                    f_score[k] = f_right[j]
                    arr[k] = right[j]
                    j += 1
                k += 1
        elif  way == "asc":
            while i < len(left) and j < len(right):
                if f_left[i] >= f_right[j]:
                    f_score[k] = f_left[i]
                    arr[k] = left[i]
                    i += 1
                else:
                    f_score[k] = f_right[j]
                    arr[k] = right[j]
                    j += 1
                k += 1
 
        while i < len(left):
            f_score[k] = f_left[i]
            arr[k] = left[i]
            i += 1
            k += 1
 
        while j < len(right):
            f_score[k] = f_right[j]
            arr[k] = right[j]
            j += 1
            k += 1
    return arr,f_score




def visualize_graph(mygraph):
    # create the networkx graph object
    G = nx.DiGraph()

    # add nodes
    for node in mygraph.map:
        G.add_node(node._value, pos=(node.x,node.y))

    # add edges
    for node in mygraph.map:
        for sibling in node._sibilings:
            G.add_edge(node._value, sibling._value)

    # set node positions
    pos = nx.get_node_attributes(G,'pos')

    # draw the graph
    nx.draw_networkx_nodes(G, pos, node_size=500)
    nx.draw_networkx_edges(G, pos, width=1)
    nx.draw_networkx_labels(G, pos, font_size=16, font_family="sans-serif")

    # add edge labels
    labels = nx.get_edge_attributes(G,'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_size=12)

    # show the graph
    plt.axis('off')
    plt.show()


def visualize_node(node):
    # create graph
    G = nx.DiGraph()
    
    # add node
    G.add_node(str(node))

    fig, ax = plt.subplots(figsize=(1, 1))

    # draw graph
    pos = nx.spring_layout(G)
    
    nx.draw(G, pos, with_labels=True, node_size=750)
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    plt.show()