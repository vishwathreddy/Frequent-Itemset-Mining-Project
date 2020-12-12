import itertools
from collections import defaultdict
import numpy as np
import time

def find_frequent_1item_sets(data,min_sup):
    #returns frequent items sets of length 1 and their counts
    l1 = set()
    freq = defaultdict(int)
    f = defaultdict(int)
    for items in data:
        for item in items:
            if freq.get(item):
                freq[item]+=1
            else:
                freq[item]=1
    
    for key,value in freq.items():
        if(value >= min_sup):
            l1.add(key)
            f[key]=value
    return l1,f

def apriori(data,min_sup):
    #main apriori function
    whole_fset = defaultdict(int)
    l,f1_set = find_frequent_1item_sets(data,min_sup)
    k=2
    cl = l
    whole_fset = f1_set    
    while bool(cl):
        ck = apriori_gen(cl,k)  #ck
        # print(ck)
        frequent_items = defaultdict(int)
        fk_set = defaultdict(int)
        for transaction in data:
            for item in ck:
                a = set(item)
                # print(item)
                if a.issubset(transaction):  
                    frequent_items[item]+=1
        # print(frequent_items)
        lk = set()
        for key,value in frequent_items.items():
            if int(value) >= min_sup:
                lk.add(key)
                fk_set[key]=value
        whole_fset.update(fk_set)
        cl = lk
        k+=1
    # print(whole_fset)
    return whole_fset

def apriori_Trans_reduction(data,min_sup):
    #Optimazation with Transaction Reduction method
    whole_fset = defaultdict(int)
    l,f1_set = find_frequent_1item_sets(data,min_sup)
    k=2
    cl = l
    whole_fset = f1_set
    i = 0
    marked = np.zeros(len(data),dtype=bool)
    
    while bool(cl):
        ck = apriori_gen(cl,k)  #ck
        # print(ck)
        frequent_items = defaultdict(int)
        fk_set = defaultdict(int)
        i=0
        for transaction in data:
            if marked[i]==0:
                flag = True
                for item in ck:
                    a = set(item)
                    # print(item)
                    if a.issubset(transaction):  
                        frequent_items[item]+=1
                        flag = False
                marked[i]=flag
            i+=1
        # print(frequent_items)
        lk = set()
        for key,value in frequent_items.items():
            if int(value) >= min_sup:
                lk.add(key)
                fk_set[key]=value
        whole_fset.update(fk_set)
        cl = lk
        k+=1
    # print(whole_fset)
    return whole_fset   
    

def apriori_gen(l,k):
    #lk generation from lk-1
    ck = set()
    if k == 2:
        for item1 in l:
            c = []
            for item2 in l:
                
                if (item1<item2):
                # print(k-2)
                    c.append(item1)
                    c.append(item2)
                    ck.add(tuple(c))
                    c.clear()

    else:
        for item1 in l:
            c = []
            for item2 in l:
                flag = True
                for i in range(k-2):
                # print(1)
                    if(item1[i]!=item2[i]):
                        flag = False
                        break

                if flag & (item1[k-2]<item2[k-2]):
                    # print(k-2)
                    for i in range(k-2):
                        c.append(item1[i])
                    c.append(item1[k-2])
                    c.append(item2[k-2])
                    if has_infrequent_subset(c,l):
                        c.clear()
                    else:
                        # print(1)
                        ck.add(tuple(c))
                        c.clear()        
    return ck

def has_infrequent_subset(c,l):
    #returns if c has infrequent subsets from lk-1
    n = len(c) - 1
    # print(c)
    subsets = itertools.combinations(c, n)
    for subset in subsets:
        if subset in l:
            continue
        else:
            return True
    return False

def get_assoicationrules(freq_sets,min_confidence):
    #From lk prints assoication rules with minimum confindence
    for key,value in freq_sets.items():
        if type(key) is int :
            continue
        else:
            l = set(key)
            subsets = []
            for i in range(1,len(l)):
                c = itertools.combinations(l,i)
                for a in c:
                    subsets.append(list(a))
            for subset in subsets:
                # print(subset)
                remain = l.difference(subset)
                if len(subset) == 1:
                    confidence = value/freq_sets[subset[0]]
                    if confidence >= min_confidence:
                        print(subset,"==>",list(remain),confidence)
                else:
                    if tuple(subset) in freq_sets:
                        confidence = value/freq_sets[tuple(subset)]
                        if confidence >= min_confidence:
                            print(subset,"==>",list(remain),confidence)


def main():

    start = time.time()
    with open('data1.txt') as data_file:
        data = [[int(num) for num in line.split(' ') if num != '\n' and num != '' and num != '-1' and num != '-2\n' and num!='-2'] for line in data_file]
    # print(data)
    #naive code
    min_sup = 400
    freq_sets = apriori(data,min_sup)
    print("Number of frequent sets =",len(freq_sets))
    print("Frequent item sets with their support values")
    print(freq_sets)
    min_confidence = 0.7
    print("Assoication Rules,Confidence")
    get_assoicationrules(freq_sets,min_confidence)
    end1 = time.time()
    print("Time Taken by unoptimized apriori =",end1-start)
    #Transaction reduction
    min_sup = 400
    freq_sets = apriori_Trans_reduction(data,min_sup)
    print("Number of frequent sets =",len(freq_sets))
    print("Frequent item sets with their support values")
    print(freq_sets)
    min_confidence = 0.7
    print("Assoication Rules,Confidence")
    get_assoicationrules(freq_sets,min_confidence)
    end2 = time.time()
    print("Time Taken by apriori using Transaction reduction =",end2-end1)
    #Partitioning
    min_sup = 400
    split_data = np.array_split(data,3)

    gobal_set = defaultdict(int)
    for d in split_data:
        freq_sets = apriori_Trans_reduction(d,min_sup/3)
        gobal_set.update(freq_sets)
    
    final_set = defaultdict(int)
    for transaction in data:
        for key in gobal_set.keys():
            if type(key) is int:
                if key in transaction:
                    final_set[key]+=1
            else:
                a = set(key)
                if a.issubset(transaction):
                    final_set[key]+=1
    final_freq_set = defaultdict(int)
    for key,value in final_set.items():
        if value >= min_sup:
            final_freq_set[key] = value
    print("Number of frequent sets =" ,len(final_freq_set))
    print("Frequent item sets with their support values")
    print(final_freq_set)
    print("Assoication Rules,Confidence")
    get_assoicationrules(final_freq_set,min_confidence)
    end3 = time.time()
    print("Time Taken by apriori using Partitioning method =",end3-end2)

main()