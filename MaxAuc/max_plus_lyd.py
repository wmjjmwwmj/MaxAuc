#!/usr/bin/env python
# coding: utf-8

## 

# In[78]:


n = 4
deltas=[9,8,6,2]
relation_dict = {"ss":[(2,3),(1,2)],"es":[],"ee":[(0,2),(2,3)],"se":[(3,2),(0,1)]} #(0,1)<=>x_0<x_1


# In[79]:


def oplus(x,y):
    if x == 'e':
        return y
    elif y == 'e':
        return x
    else:
        return max(x,y)

def otimes(x,y):
    if x == 'e' or y == 'e':
        return 'e'
    else:
        return x + y


def adjacent_matrix(n,deltas,relation_dict):
    A = [['e' for i in range(n)] for j in range(n)]
    for tup in relation_dict["ss"]: #x_i<x_j
        A[tup[1]][tup[0]] = oplus(1, A[tup[1]][tup[0]])
    for tup in relation_dict["es"]: #x_i+delta_i < x_j
        A[tup[1]][tup[0]] = oplus(deltas[tup[0]]+1,A[tup[1]][tup[0]])
    for tup in relation_dict["se"]: #x_i < x_j+delta_j
        A[tup[1]][tup[0]] = oplus(-deltas[tup[1]]+1,A[tup[1]][tup[0]])
    for tup in relation_dict["ee"]: #x_i+delta_i < x_j + delta_j
        A[tup[1]][tup[0]] = oplus(deltas[tup[0]]-deltas[tup[1]]+1,A[tup[1]][tup[0]])
    return A
def print_matrix(A,n):
    for i in range(n):
        l = ""
        for j in range(n):
            l += str(A[i][j])+" "
        print(l + " \n")


# In[80]:


print_matrix(adjacent_matrix(n,deltas,relation_dict),n)


# In[71]:


def get_star(A,n):
    result = A
    temp = [['e' for i in range(n)] for j in range(n)]
    for k in range(n):

        for i in range(n):
            for j in range(n):
                if result[k][k]!='e' and result[k][k]>0:
                    return None

                else:
                    temp[i][j] = oplus(result[i][j],otimes(result[i][k],result[k][j]))
        
        result = temp
    for k in range(n):
        result[k][k] = oplus(0,result[k][k])
    return result


# In[72]:


A = [['e','e',-2,'e'],['e','e',-3,-2],['e',1,'e','e'],[1,2,'e','e']]
get_star(A,4)


# In[73]:


def maximum(L):
    res = 'e'
    for x in L:
        res = oplus(res,x)
    return res


# In[74]:


def solution(n,deltas,relation_dict):
    A = adjacent_matrix(n,deltas,relation_dict)
    

    if A != None:
        A_star = get_star(A,n)
        return [maximum(A_star[k]) for k in range(n)]
    else:
        return None


# In[77]:


print(solution(n,deltas,relation_dict))


# In[46]:





# In[ ]:




