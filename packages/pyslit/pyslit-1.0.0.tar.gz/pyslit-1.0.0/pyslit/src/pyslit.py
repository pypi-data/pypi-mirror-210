# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 22:11:32 2023

@author: Ashraq
"""
def size(sequence,index=None,element=None,balance=False):
    l = 0
    for i in sequence:
        l+=1

    if balance == False:
        if index != None:
            if index > l:
                return l
            if index < 0:
                index += l
                if index < 0:
                    return l
            l = index                                      #Does not consider the given element
        elif element != None:
            l = 0
            for i in sequence:
                if i == element:
                    break
                l+=1
        else:
            pass

    else:
        if index != None:
            if index > l:
                return l
            if index < 0:
                index += l
                if index < 0:
                    return l
            l -= index                               #Consider the given element
        elif element != None:
            h = 0
            for i in sequence:
                if i == element:
                    break
                h+=1
            l -= h
        else:
            pass
    return l

def edit(sequence,index,char):                 #Dictionary
    if type(sequence) == dict:
        if index not in sequence:
            return sequence
        else:
            sequence[index] = char
            return sequence

    length = (len(sequence)-1)
    n_len = -len(sequence)
    if index > length:
        return sequence
    if length == -1:
        return sequence
    if n_len > index:
        return sequence

    t = type(sequence)
    sequence = list(sequence)

    sequence[index]=char
    if t == str:
        s = ''
        for i in sequence:
            s+=i
    elif t == tuple:
        s = tuple(sequence)
    else:
        s = sequence
    sequence = s
    return sequence

def remove(sequence,index=None):              #Dictionary
    if type(sequence) == dict:
        for i in sequence:
            if sequence[i] == index:
                del dict[i]
                return sequence

    if index == None:
        sequence = sequence[:-1]
    else:
        l = sequence[:index]
        r = sequence[index+1:]
        sequence = l+r
    return sequence

def remove_item(sequence,element,occurance=1):   #remove element at a particular occurance
    length = len(sequence)
    h = 0
    l = sequence
    r = type(sequence)()
    for i in range(length):
        if sequence[i] == element:
            h += 1
            l = sequence[:i]
            r = sequence[i+1:]
        if h == occurance:
            break
    sequence = l+r
    return sequence

def remove_items(sequence,element,occurance=None):   #remove element for the number of times occurance
    length = len(sequence)
    if occurance == None:
        occurance = length
    l = ()
    r = ()
    h = 0
    e = 0
    for i in range(length):
        while sequence[i] == element:
            h += 1
            l = sequence[:i]
            r = sequence[i+1:]
            sequence = l+r
            if (len(sequence)-1) < i:
                e = 1
                break
            if h == occurance:
                e = 1
                break
        if e == 1:
            break
    return sequence

def add(sequence,element,index=-1):
    t = type(sequence)
    sequence = list(sequence)
    element = [element]
    
    if index == -1:
        s = sequence+element
    elif index < -1:
        l = sequence[:index+1]
        r = sequence[index+1:]
        s = l+element+r
    else:
        l = sequence[:index]
        r = sequence[index:]
        s = l+element+r
        
    if t == str:
        S = ''
        for i in s:
            S+=i
        s = S
    elif t == tuple:
        s = tuple(s)
    else:
        pass
    sequence = s
    return sequence

def sort(array,reverse=False):
    t = type(array)
    array = list(array)
    for i in range(1, len(array)):
        key_item = array[i]
        j = i - 1
        if type(array[j]) != type(key_item):
            raise TypeError('Comparison not supported between different data types')
        while j >= 0 and array[j] > key_item:
            array[j + 1] = array[j]
            j -= 1
            if type(array[j]) != type(key_item):
                raise TypeError('Comparison not supported between different data types')
        array[j + 1] = key_item
    if reverse == True:
        r = []
        for k in range(len(array)-1,-1,-1):
            r += [array[k]]
        array = r
    else:
        pass
    if t == str:
        S = ''
        for i in array:
            S+=i
        array = S
    elif t == tuple:
        array = tuple(array)
    else:
        pass
    return array

def sort_alpha(sequence,first='alpha',reverse=False):
    t = type(sequence)
    sequence = list(sequence)
    alpha = []
    other = []
    for i in sequence:
        if type(i) == str:
            alpha += [i]
        else:
            other += [i]
    alpha = sort(alpha,reverse)
    if alpha == None:
        return
    if first == 'alpha':
        sequence = alpha+other
    else:
        sequence = other+alpha
    if t == str:
        S = ''
        for i in sequence:
            S+=i
        sequence = S
    elif t == tuple:
        sequence = tuple(sequence)
    else:
        pass
    return sequence

def sort_num(sequence,first='num',reverse=False):
    t = type(sequence)
    sequence = list(sequence)
    num = []
    other = []
    for i in sequence:
        if type(i) == int:
            num += [i]
        else:
            other += [i]
    num = sort(num,reverse)
    if num == None:
        return
    if first == 'num':
        sequence = num+other
    else:
        sequence = other+num
    if t == str:
        S = ''
        for i in sequence:
            S+=i
        sequence = S
    elif t == tuple:
        sequence = tuple(sequence)
    else:
        pass
    return sequence

def sort_all(sequence,first='num',reverse_alpha=False,reverse_num=False,reverse=False):
    t = type(sequence)
    sequence = list(sequence)
    alpha = []
    num = []
    for i in sequence:
        if type(i) == str:
            alpha += [i]
        else:
            num += [i]
    alpha = sort(alpha,(reverse_alpha or reverse))
    num = sort(num,(reverse_num or reverse))
    if (alpha == None) or (num == None):
        return
    if first == 'num':
        sequence = num+alpha
    else:
        sequence = alpha+num
    if t == str:
        S = ''
        for i in sequence:
            S+=i
        sequence = S
    elif t == tuple:
        sequence = tuple(sequence)
    else:
        pass
    return sequence

def index(sequence,element,l=0,r=None,occurance=1):
    element = [element]
    if r == None:
        r = len(sequence)
    index = -1
    h = 0
    for i in range(l,r):
        if sequence[i:i+len(element)] == element:
            h += 1
            index = i
        if h == occurance:
            break
    return index

def index_all(sequence,element,l=0,r=None):
    element = [element]
    if r == None:
        r = len(sequence)
    index = []
    for i in range(l,r):
        if sequence[i:i+len(element)] == element:
            index += [i]
    if len(index) == 0:
        index = -1
    return index
    
def isnum(sequence,l=0,r=None):
    if r == None:
        r = len(sequence)
    sequence = sequence[l:r]
    for i in sequence:
        if (ord(i) >= 48) and (ord(i) <= 57):
            return True
        else:
            continue
    return False

def isaplha(sequence,l=0,r=None):
    if r == None:
        r = len(sequence)
    sequence = sequence[l:r]
    for i in sequence:
        if ((ord(i) >= 65) and (ord(i) <= 90)) or ((ord(i) >= 97) and (ord(i) <= 122)):
            return True
        else:
            continue
    return False

def isalphanum(sequence,l=0,r=None):
    if r == None:
        r = len(sequence)
    sequence = sequence[l:r]
    for i in sequence:
        if (((ord(i) >= 65) and (ord(i) <= 90)) or ((ord(i) >= 97) and (ord(i) <= 122))) or ((ord(i) >= 48) and (ord(i) <= 57)):
            return True
        else:
            continue
    return False

def replace(sequence,element,replace,l=0,r=None,occurance=1):
    i = index(sequence,element,l,r,occurance)
    if i == -1:
        return sequence
    L = sequence[:i]
    R = sequence[i+len(element):]
    sequence = L+replace+R
    return sequence

def replaces(sequence,element,replace,l=0,r=None,occurance=1):
    i = index_all(sequence,element,l,r)
    if i == -1:
        return sequence
    i = i[:occurance]
    for j in i:
        L = sequence[:i[j]]
        R = sequence[i[j]+len(element):]
        sequence = L+replace+R
    return sequence

def replace_all(sequence,element,replace,l=0,r=None):
    i = index_all(sequence,element,l,r)
    if i == -1:
        return sequence
    for j in i:
        L = sequence[:i[j]]
        R = sequence[i[j]+len(element):]
        sequence = L+replace+R
    return sequence

def change_key(dict,key=None,value=None,n_key=None):
    if n_key == None:
        return dict
    if n_key in dict:
        raise KeyError('n_key is already present. Enter a new key')
    
    if key != None:
        for i in dict:
            if i == key:
                value = dict[key]
                del dict[i]
                dict[n_key] = value
                return dict
            else:
                pass
    else:
        for i in dict:
            if dict[i] == value:
                del dict[i]
                dict[n_key] = value
                return dict
            else:
                pass
    return dict

def get_key(dict,value=None,multiple=False):
    k = []
    for i in dict:
        if dict[i] == value:
            if multiple == False:
                return i
            else:
                k += [i]
    return k

def get_value(dict,key=None):
    if key == None:
        return dict
    for i in dict:
        if i == key:
            return dict[i]

