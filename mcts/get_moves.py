import game.r as r
import numpy as np

        # test r
# all_cards = [4]*13 + [1,1]
# print(all_cards)
#
# handcards = [0,0,0,0,0,1,1,3,3,3,3,3,1,1,1]
# no_cards = [0]*15
#
# print(r.get_moves(handcards,no_cards))


# 根据当前手牌和上家的牌返回所有可能出的牌
# input：
#     handcards : dict e.g. 4455566 = {'3': 0, '4': 2, '5': 3, '6': 2, '7': 0, '8': 0, '9': 0, '10': 0, '11': 0, '12': 0, '13': 0, '1': 0, '2': 0, '14': 0, '15': 0}
#     lastcards: list e.g. 33 = [3,3]
# ouput:
#     list of dict

def get_moves(handcards, lastcards):
    if not lastcards:
        lastcards = []
    index = [str(i) for i in range(3,14)] + ['1','2','14','15']
    rhandcards = list(handcards.values())
    tem = dict(zip(index, [0]*15))
    for l in lastcards:
        tem[str(l)] += 1
    rlastcards = list(tem.values())

    moves = []
    rmoves = r.get_moves(rhandcards, rlastcards)
    for m in rmoves:
        moves.append(dict(zip(index, m)))
    return moves


'''
# test function:
index = [str(i) for i in range(3, 14)] + ['1', '2', '14', '15']
aa = [0, 2, 3, 2] + [0]*11
a = dict(zip(index, aa))
hand_card = {'3': 0, '5': 0, '6': 0, '7': 0, '8': 0, '10': 0, '11': 0, '12': 0, '13': 0, '1': 0, '4': 0, '9': 0, '2': 0, '14': 0, '15': 0}

b = []
moves = get_moves(hand_card, b)
print(moves)
'''
