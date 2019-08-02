"""
                       12
3 4 5 6 7 8 9 10 J Q K A   2 R B

NONE
dan         15
dui         13
san         13
san_yi      13*14 = 182
san_er      13*12 = 156
dan_shun    8+7+6+5+4+3+2+1 = 36
er_shun     10+9+8+7+6+5+4+3 = 52
feiji       11+10+9+8+7 = 45
xfeiji      11*C(13,2)+10*C(12,3)+9*C(11,4)+8*C(10,5) = 8044
dfeiji      11*C(11,2)+10*C(10,3)+9*C(9,4) = 2939
zha         13
si_erdan    13*C(14,2) = 1183
si_erdui    13*C(12,2) = 858
wangzha     1
"""

import pandas as pd
from itertools import combinations
from collections import defaultdict
from os.path import join, abspath, dirname, exists

card = [str(i) for i in range(3, 14)] + ['1', '2', '14', '15']
name_to_rank = {'3':1, '4':2, '5':3, \
                '6':4, '7':5, '8':6, '9':7, '10':8, '11':9, '12':10, '13':11, \
                '1':12, '2':13, '14':14, '15':15}


# [---name---] main type sum

def dan():
    f = pd.DataFrame(columns=card, dtype=int)
    for k in card:
        f = f.append({k:1, 'main':name_to_rank[k]}, ignore_index=True)
    f['type'] = 'dan'
    assert(len(f)==15)
    return f

def dui():
    f = pd.DataFrame(columns=card, dtype=int)
    for k in card[:-2]:
        f = f.append({k:2, 'main':name_to_rank[k]}, ignore_index=True)
    f['type'] = 'dui'
    assert(len(f)==13)
    return f

def san():
    f = pd.DataFrame(columns=card, dtype=int)
    for k in card[:-2]:
        f = f.append({k:3, 'main':name_to_rank[k]}, ignore_index=True)
    f['type'] = 'san'
    assert(len(f)==13)
    return f


def san_yi():
    f = pd.DataFrame(columns=card, dtype=int)
    for k in card[:-2]:
        comb = combinations(list(set(card)-{k}), 1)
        for c in comb:
            f = f.append({k:3, c[0]:1, 'main':name_to_rank[k]}, ignore_index=True)
    f['type'] = 'san_yi'
    assert(len(f)==182)
    return f

def san_er():
    f = pd.DataFrame(columns=card, dtype=int)
    for k in card[:-2]:
        comb = combinations(list(set(card[:-2])-{k}), 1)
        for c in comb:
            if c[0]!=k:
                f = f.append({k:3, c[0]:2, 'main':name_to_rank[k]}, ignore_index=True)
    f['type'] = 'san_er'
    assert(len(f)==156)
    return f

def dan_shun():
    f = pd.DataFrame(columns=card, dtype=int)
    for L in range(5, 13):
        for i in range(5+8-L):
            sli = card[i: i+L]
            data = {k:1 for k in sli}
            data['main'] = name_to_rank[sli[0]]
            f = f.append(data, ignore_index=True)
    f['type'] = 'dan_shun'
    assert(len(f)==36)
    return f

def er_shun():
    f = pd.DataFrame(columns=card, dtype=int)
    for L in range(3, 11):
        for i in range(3+10-L):
            sli = card[i: i+L]
            data = {k:2 for k in sli}
            data['main'] = name_to_rank[sli[0]]
            f = f.append(data, ignore_index=True)
    f['type'] = 'er_shun'
    assert(len(f)==52)
    return f

def feiji():
    f = pd.DataFrame(columns=card, dtype=int)
    for L in range(2, 7):
        for i in range(2+11-L):
            sli = card[i: i+L]
            data = {k:3 for k in sli}
            data['main'] = name_to_rank[sli[0]]
            f = f.append(data, ignore_index=True)
    f['type'] = 'feiji'
    assert(len(f)==45)
    return f


def xfeiji():
    f = pd.DataFrame(columns=card, dtype=int)
    for L in range(2, 6):
        for i in range(2+11-L):
            sli = card[i: i+L]
            comb = combinations(list( set(card)-set(sli) ), L)
            for c in comb:
                data = {k:1 for k in c}
                data.update( {k:3 for k in sli} )
                data['main'] = name_to_rank[sli[0]]
                f = f.append(data, ignore_index=True)
    f['type'] = 'xfeiji'
    assert(len(f)==8044)
    return f

def dfeiji():
    f = pd.DataFrame(columns=card, dtype=int)
    for L in range(2, 5):
        for i in range(2+11-L):
            sli = card[i: i+L]
            comb = combinations(list( set(card[:-2])-set(sli) ), L)
            for c in comb:
                data = {k:2 for k in c}
                data.update( {k:3 for k in sli} )
                data['main'] = name_to_rank[sli[0]]
                f = f.append(data, ignore_index=True)
    f['type'] = 'dfeiji'
    assert(len(f)==2939)
    return f

def zha():
    f = pd.DataFrame(columns=card, dtype=int)
    for k in card[:-2]:
        f = f.append({k:4, 'main':name_to_rank[k]}, ignore_index=True)
    f['type'] = 'zha'
    assert(len(f)==13)
    return f

def si_erdan():
    f = pd.DataFrame(columns=card, dtype=int)
    for k in card[:-2]:
        comb = combinations(list( set(card)-{k} ), 2)
        for c in comb:
            f = f.append({k:4, c[0]:1, c[1]:1, 'main':name_to_rank[k]}, ignore_index=True)
    f['type'] = 'si_erdan'
    assert(len(f)==1183)
    return f

def si_erdui():
    f = pd.DataFrame(columns=card, dtype=int)
    for k in card[:-2]:
        comb = combinations(list( set(card[:-2])-{k} ), 2)
        for c in comb:
            f = f.append({k:4, c[0]:2, c[1]:2, 'main':name_to_rank[k]}, ignore_index=True)
    f['type'] = 'si_erdui'
    assert(len(f)==858)
    return f

def wangzha():
    f = pd.DataFrame(columns=card, dtype=int)
    f = f.append({'14':1, '15':1, 'main':16}, ignore_index=True)
    f['type'] = 'wangzha'
    assert(len(f)==1)
    return f

def buyao():
    f = pd.DataFrame(columns=card, dtype=int)
    f = f.append({k:0 for k in card}, ignore_index=True)
    f['main'] = 0
    f['type'] = 'buyao'
    assert(len(f)==1)
    return f


def calc_key(row):
    s=[]
    for k in card:
        s.extend( [int(k)]*row[k] )
    s = str(sorted(s))
    return s


if exists(  join(dirname(abspath(__file__)), "patterns.csv")  ):
    All = pd.read_csv(join(dirname(abspath(__file__)), "patterns.csv")).fillna(0)
else:
    All = pd.concat([dan(), dui(), san(), san_yi(), san_er(), 
                     dan_shun(), er_shun(), feiji(), xfeiji(), dfeiji(), 
                     zha(), si_erdan(), si_erdui(), wangzha(), buyao()], axis=0, sort=False).fillna(0)
    All['sum'] = All[card].sum(axis=1)
    tp = All['type']
    All=All.drop('type', axis=1).astype(int)
    All['type'] = tp

    All['key'] = All.apply(calc_key, axis=1)

    All.to_csv(join(dirname(abspath(__file__)), "patterns.csv"), index=False)
