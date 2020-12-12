#!/usr/bin/env python
# coding: utf-8

# In[1]:


from copy import deepcopy
from collections import defaultdict

class Node:
    def __init__(self, name, data):
        self.name = name
        self.data = data
        self.children = []
        self.parent = None
        self.visit = False
        self.table = {}
        self.header = {}

    def insert_txn(self, root, txn, val):
        if len(txn) == 0:
            return
        children = self.children
        parent = self
        
        first_child = txn[0]
        
        for child in children:
            if child.name == first_child:
                child.data+=val
                child.insert_txn(root, txn[1:], val)
                return 
        
        
        new_child = Node(first_child, val)
        new_child.parent = parent
        
        self.children.append(new_child)
        
        
        if first_child not in root.table:
            root.table[first_child] = []
        
        else :
            pass
        
        root.table[first_child].append(new_child)
                    
        new_child.insert_txn(root, txn[1:], val)
        return 
    
    
                

    def headerBuilder(self, root):
        if len(self.children) == 0:
            return
        
        for child in self.children:
            tmp_data = child.data
            if child.name in root.header:
                root.header[child.name] = root.header[child.name] + tmp_data
            else :
                root.header[child.name] = tmp_data
            
            child.headerBuilder(root)
            
        
       
        

class FP_Growth:
    def __init__(self, data, min_supCount, mode = 'NAIVE'):
#         self.data = data
        self.min_supCount = min_supCount
        self.root = Node(-1, -1)
        self.freq_set = []
        self.sup_count = []
        self.mode = mode
        
        self.condPatBases = {}
        self.freq_list = {}
        self.optimisedDone = False
        
        
    def build_first_frequent_ranks(self, data, sup_cnt_arr = None):
        sup_cnt_map = {}    
        rank_map = {}
        
        for i,arr in enumerate(data):
            for val in arr:
                if val not in sup_cnt_map : 
                    if sup_cnt_arr == None : 
                        sup_cnt_map[val] = 1
                    else :
                        sup_cnt_map[val] = sup_cnt_arr[i]
                else :
                    if sup_cnt_arr == None:
                        sup_cnt_map[val] += 1
                    else :
                        sup_cnt_map[val] += sup_cnt_arr[i]
        
        # Now get sorted array
        sorted_array = sup_cnt_map.items()
        sorted_array = sorted(sorted_array, key = lambda item : item[1], reverse = True)
        
        
        
        i = 1
        for tmp in sorted_array:
            rank_map[tmp[0]] = i
            i+=1
        
        return sup_cnt_map, rank_map
        
    def build_fp_tree(self, data, root, sup_cnt_arr = None):
        # First is to build rank of 1 frequent sets
        sup_cnt_map, rank_map = self.build_first_frequent_ranks(data, sup_cnt_arr)
        
        for i,txn in enumerate(data):
            num = 1 if sup_cnt_arr == None else sup_cnt_arr[i]
            sorted_txn = sorted(txn, key = lambda val : rank_map[val])
            
            path = [x for x in sorted_txn if sup_cnt_map[x] > self.min_supCount]
            
            root.insert_txn(root, sorted_txn, num)
        
        root.headerBuilder(root)
        
        sorted_arr = sorted(root.header.items(), key=lambda item:item[1])
        
        root.header = {k:v for k,v in sorted_arr}
        root.table = {k:v for k,v in sorted(root.table.items(), key= lambda item:root.header[item[0]])}
        
        if self.mode == 'OPTIMIZED' and self.optimisedDone == False: 
#             print ("kekaaa")
            self.getAllCondPatBefore(root)
#             self.optimisedDone = True
            
    
    def getAllCondPatBefore(self, root):
        
        self.condPatBases = {}
        self.freq_list = {}
        self.optimisedDone = False
        
        for child in root.children:
            self.DFS(child, [])
            
    def DFS(self, root, prefixes):
        
        if root!= self.root and len(prefixes) > 0:
            if root.name not in self.condPatBases:
                self.condPatBases[root.name] = []
            reverse_prefix = prefixes[::-1]
            self.condPatBases[root.name].append(reverse_prefix)
            
            if root.name not in self.freq_list:
                self.freq_list[root.name] = []
            self.freq_list[root.name].append(root.data)
            
        
        prefixes.append(root.name)
        for child in root.children:
            self.DFS(child, prefixes)
        prefixes.pop()
        
    def print_fp_tree(self, root):
        print (str(root.name) + "(" + str(root.data) + ")")
        
        for node in root.children:
            self.print_fp_tree(node)
    
    def get_conditional_patterns(self, root, node_name):
        
        if self.mode == 'OPTIMIZED':
            
            kek = []
            
            if node_name not in self.freq_list:
                return []
            
            for i in range(len(self.freq_list[node_name])):
                kek.append((self.condPatBases[node_name][i], self.freq_list[node_name][i]))
            return kek
            
        conditional_patterns = []
        
        for node in root.table[node_name]: #For each prefix 
            tmp_pattern = []
            temp_node = node
            val = temp_node.data
            while temp_node.parent.name!=-1 : 
                
                parent_node_name = temp_node.parent.name
                tmp_pattern.append(parent_node_name)
                temp_node = temp_node.parent
                
            if len(tmp_pattern) > 0:
                conditional_patterns.append((tmp_pattern, val))
                
                
        return conditional_patterns
            
            
    
    def fp_growth_bottom_up(self, tree, alpha):
        
        opt_cond_patt_names = defaultdict(lambda : [])
        opt_cond_patt_vals = defaultdict(lambda : [])
        
        if len(tree.children) == 0:
            
            return 
        freq_item_sets = []
        for node_name in tree.header.keys():
            #For nodes starting with least sup_count find prefix paths and tree
            if tree.header[node_name] >= self.min_supCount:
                copy_alpha = deepcopy(alpha)
                copy_alpha.append(node_name)
                
                if len(copy_alpha) > 0:
                    self.freq_set.append(copy_alpha)
                    
                conditional_patterns = self.get_conditional_patterns(tree, node_name)
                
                cond_pat_names = []
                cond_pat_vals = []
                
                for element in conditional_patterns:
                    cond_pat_names.append(element[0])
                    cond_pat_vals.append(element[1])

                new_root = Node(-1,-1)
                
#                 print (cond_pat_names)
                
                self.build_fp_tree(cond_pat_names, new_root, cond_pat_vals)
                    
                if len(new_root.children) > 0 :
                    self.fp_growth_bottom_up(new_root, copy_alpha)
                
    
    
        


# In[ ]:





# In[6]:


import time



with open('data2.txt') as data_file:
    data = [[int(num) for num in line.split(' ') if num != '\n' and num != '' and num != '-1' and num != '-2\n' and num!='-2'] for line in data_file]


print (len(data))    
    
# data = test_data
start_time = time.time()

sup_count = 13000

naive = FP_Growth(data, sup_count, )
naive.build_fp_tree(data, naive.root)

print ("Tree built!")



naive.fp_growth_bottom_up(naive.root, [])

print ("Time taken by naive : ")

print (time.time() - start_time)

print ("Output : {}".format(len(naive.freq_set)))


# In[ ]:


start_time = time.time()

opt = FP_Growth(data, sup_count, 'OPTIMISED')
opt.build_fp_tree(data, opt.root)

print ("Tree built!")

opt.fp_growth_bottom_up(opt.root, [])


print ("Time taken by opt : ")

print (time.time() - start_time)

print ("Output : {}".format(len(opt.freq_set)))


# In[8]:


import time
def run_FP_Growth(data_path, sup_percentage, mode = 'NAIVE'):
    with open(data_path) as data_file:
        data = [[int(num) for num in line.split(' ') if num != '\n' and num != '' and num != '-1' and num != '-2\n' and num!='-2'] for line in data_file]

    sup_count = int(sup_percentage * len(data) / 100)
    
    s_t = time.time()
    
    inst = FP_Growth(data, sup_count, mode)
    inst.build_fp_tree(data, inst.root)
    
    inst.fp_growth_bottom_up(inst.root, [])
    
    time_taken = time.time() - s_t
    
    no_freq_sets = len(inst.freq_set)
    
    print(len(inst.root.header.keys()))
    
    max_len = 0
    for i in inst.freq_set:
        max_len = max(max_len, len(i))
        
    return time_taken, no_freq_sets, max_len
    


# In[32]:


min_support = [65, 50, 40]

times_naive, nums_naive, lens_naive = [], [], []

times_opt, nums_opt, lens_opt = [], [], []

for i in min_support:
    one, two, three = run_FP_Growth('./data1.txt', i, mode = 'OPTIMISED')
    times_opt.append(one)
    nums_opt.append(two)
    lens_opt.append(three)

print ("OPT Done")
    
for i in min_support:
    one, two, three = run_FP_Growth('./data1.txt', i, mode = 'NAIVE')
    times_naive.append(one)
    nums_naive.append(two)
    lens_naive.append(three)


# In[33]:


print (lens_naive)


# In[34]:


print (nums_naive, nums_opt)


# In[35]:


print (times_naive, times_opt)


# In[37]:


import matplotlib.pyplot as plt

plt.plot(min_support, times_naive, color = 'red', marker = 'o')
plt.plot(min_support, times_opt, color = 'orange', marker = 'o')
plt.xlabel("support")
plt.ylabel("Time taken in secs")
plt.show()


# In[ ]:




