# -*- coding: utf-8 -*-
"""
自定义相关类
"""
from __future__ import absolute_import

from gameutil import card_show
import numpy as np
from typing import List, Tuple, Dict
import pandas as pd
from collections import defaultdict
from card_util import All as backup
from os.path import join, abspath, dirname


############################################
#                 游戏类                   #
############################################
class GameState():
    def __init__(self):
        self.hand = None
        self.out = None
        self.up_out = None
        self.down_out = None
        self.self_out = None
        self.other_hand = None


class Game(object):
    def __init__(self, agents: List['Agent']):
        # 初始化players
        self.players = []
        for p in agents:
            p.game = self
            self.players.append(p)
        self.game_reset()
        
    def get_state(self)->GameState:
        state = GameState()
        state.hand = Card.vectorize_card_dict(self.players[self.index].get_hand_card())
        tmp, state.out = Card.vectorized_card_out(self.cards_out, len(self.players))
        state.up_out = tmp[self.get_up_index()]
        state.down_out = tmp[self.get_down_index()]
        state.self_out = tmp[self.index]
        state.other_hand = (np.array([4]*13+[1,1]) - state.hand - state.out).tolist()
        return state

    def get_up_index(self):
        return len(self.players)-1 if self.index==0 else self.index-1
    
    def get_down_index(self):
        return 0 if self.index==len(self.players)-1 else self.index+1

    # 游戏环境重置
    def game_reset(self):
        #初始化一副扑克牌类
        cards = Card.init_card_suit()
        #洗牌
        np.random.shuffle(cards)
        #发牌并排序
        self.mingpai = cards[:3]
        p1_cards = cards[:20]
        p1_cards.sort(key=lambda x: x.rank)
        p2_cards = cards[20:37]
        p2_cards.sort(key=lambda x: x.rank)
        p3_cards = cards[37:]
        p3_cards.sort(key=lambda x: x.rank)
        self.players[0].set_hand_card( p1_cards )
        self.players[1].set_hand_card( p2_cards )
        self.players[2].set_hand_card( p3_cards )
        self.cards_out = []

        #play相关参数
        self.end = False    # 游戏是否结束
        self.last_desc = self.last_move = None
        self.playround = 1  # 回合数
        self.index = 0  # 当前玩家的id，0代表地主，1代表地主下家，2代表地主上家
        self.yaobuqis = []
        return Card.vectorize_card_dict(self.players[0].get_hand_card()),\
               Card.vectorize_card_dict(self.players[1].get_hand_card()),\
               Card.vectorize_card_dict(self.players[2].get_hand_card()),\
               Card.vectorized_card_list(self.mingpai)

    
    #游戏进行    
    def step(self):
        cur_move, cur_desc, self.end, buyao = self.players[self.index].step(self.get_state())
        if buyao:
            self.yaobuqis.append(self.index)
        else:
            self.yaobuqis = []
            self.last_move = cur_move
            self.last_desc = cur_desc
            self.is_start = False

        #都要不起
        if len(self.yaobuqis) == len(self.players)-1:
            self.yaobuqis = []
            self.last_desc = self.last_move = None

        winner = -1
        if self.end:
            winner = self.index

        self.index = self.index + 1
        #一轮结束
        if self.index >= len(self.players):
            #playrecords.show("=============Round " + str(playround) + " End=============")
            self.playround = self.playround + 1
            #playrecords.show("=============Round " + str(playround) + " Start=============")
            self.index = 0
        
        #todo: return more information
        return winner

    def show(self):
        for i in range(len(self.players)):
            card_show(self.players[i].get_hand_card(), "Player {}".format(i), 1)

############################################
#              扑克牌相关类                 #
############################################

class Card(object):
    """
    扑克牌类
    """
    color_show = {}
#    color_show = {'a': '♠', 'b':'♥', 'c':'♣', 'd':'♦'}
    name_show = {'11':'J', '12':'Q', '13':'K', '14':'B', '15':'R'}
    name_to_rank = {'3':1, '4':2, '5':3, \
                    '6':4, '7':5, '8':6, '9':7, '10':8, '11':9, '12':10, '13':11, \
                    '1':12, '2':13, '14':14, '15':15}
    all_card_type = ['1-a', '1-b','1-c','1-d',
                  '2-a', '2-b','2-c','2-d',
                  '3-a', '3-b','3-c','3-d',
                  '4-a', '4-b','4-c','4-d',
                  '5-a', '5-b','5-c','5-d',
                  '6-a', '6-b','6-c','6-d',
                  '7-a', '7-b','7-c','7-d',
                  '8-a', '8-b','8-c','8-d',
                  '9-a', '9-b','9-c','9-d',
                  '10-a', '10-b','10-c','10-d',
                  '11-a', '11-b','11-c','11-d',
                  '12-a', '12-b','12-c','12-d',
                  '13-a', '13-b','13-c','13-d',
                  '14-a', '15-a']

    all_card_name = [str(i) for i in range(3, 14)] + ['1', '2', '14', '15']

    @staticmethod
    def vectorize_card_dict(cards: Dict[str, List['Card']]):
        """
        cards: defaultdict(list).
        返回cards的vector表示，长度为15。
        每个元素依次表示 有多少个 3/4/5.../Q/K/A/2/14/15。
        """
        v = []
        for n in Card.all_card_name:
            v.append(len(cards[n]))
        return v

    @staticmethod
    def vectorized_card_list(cards: List):
        v = [0] * len(Card.all_card_name)
        for c in cards:
            if isinstance(c, int):
                i = Card.name_to_rank[str(c)]
            elif isinstance(c, str):
                i = Card.name_to_rank[c]
            elif isinstance(c, Card):
                i = c.rank-1
            else:
                print("Warn: Unkown card.")
            v[ i ]+=1
        return v

    @staticmethod
    def vectorized_card_out(cards_out: List[Tuple[int, str, List['Card']]], total_player=3):
        cnt = {}
        for rec in cards_out:
            a = cnt.get(rec[0], np.zeros( len(Card.all_card_name) )) # 15
            b = np.array( Card.vectorized_card_list(rec[2])  )
            cnt[rec[0]] = a+b
        a = np.zeros( len(Card.all_card_name) )
        for v in cnt.values():
            a+=v
        res = []
        for i in range(total_player):
            res.append(cnt.get(i, np.zeros( len(Card.all_card_name) )).tolist())
        return res, a.tolist()

    @staticmethod
    def init_card_suit():
        cards = []
        for card_type in Card.all_card_type:
            cards.append(Card(card_type))
        return cards


    def __init__(self, card_type):
        self.card_type = card_type  # '牌面数字-花色' 举例来说，红桃A的card_type为'1-a'
        self.name = self.card_type.split('-')[0] # 名称,即牌面数字
        self.color = self.card_type.split('-')[1] # 花色
        # 大小
        self.rank = Card.name_to_rank[self.name]


    def __str__(self):
        return Card.name_show.get(self.name, self.name)
#        return Card.name_show.get(self.name, self.name) + Card.color_show.get(self.color, self.color)
    
    __repr__ = __str__
    

def get_move_desc(move: List[int]):
    """
    输入出牌， 返回牌型描述：总张数，主牌，类型
    """
    key = str(sorted(move))
    row = backup[ backup['key']==key ]
    if len(row)!=1:
        return None
    i = row.index[0]
    return (row.at[i, 'sum'], row.at[i, 'main'], row.at[i, 'type'])

def get_decomposition(hand_card, last_move):
    """
    hand_card: 长度为15的list， 每个元素分别表示手牌中有多少个3/4/5/.../A/2/14/15.
    last_move: 上一个有效出牌，e.g. [3,3,3,2]。空表示随意出牌。
    返回当前有效出牌， 格式：[{'3':0, '4':3, '5':1, ...}, {...}]。性能会有问题。
    """
    frame = backup.copy()
    mat = frame[Card.all_card_name].values
    enough = []
    for i in range(len(mat)):
        if all(np.greater_equal(hand_card, mat[i])):
            enough.append(True)
        else:
            enough.append(False)
    frame['enough'] = enough
    moves = frame[frame['enough']]

    if len(last_move)>0:
        last_desc = get_move_desc(last_move)
        sm, mn, tp = last_desc
        moves = moves[ ( (moves['type']==tp)&(moves['main']>mn)&(moves['sum']==sm) )
                         | ( (moves['type']=='zha')&(moves['main']>mn) )
                         | (moves['type']=='buyao') | (moves['type']=='wangezha')  ]
    return moves.to_dict(orient='records')


############################################
#              玩家相关类                   #
############################################
class Agent(object):
    """
    玩家类,所有模型都应继承此类并重写choose方法
    """
    def __init__(self, player_id):
        self.player_id = player_id  # 0代表地主，1代表地主下家，2代表地主上家
        self.__cards_left = defaultdict(list)  # e.g. {'3':[cards], ...}
        self.game = None
        self.moves = None

    def set_hand_card(self, cards):
        self.__cards_left = defaultdict(list)  # e.g. {'3':[cards], ...}
        for c in cards:
            self.__cards_left[c.name].append( c )
        self.moves = self.__get_all_moves( backup.copy() )

    def get_hand_card(self):
        return self.__cards_left

    def __get_all_moves(self, frame):
        """
        根据手牌，筛选合法的组合。
        """
        enough = []
        v = Card.vectorize_card_dict(self.__cards_left)
        mat = frame[Card.all_card_name].values
        for i in range(len(mat)):
            if all(np.greater_equal(v, mat[i])):
                enough.append(True)
            else:
                enough.append(False)
        frame['enough'] = enough
        moves = frame[frame['enough']]
        return moves

    def get_moves(self, last_move, last_desc)->List[dict]:
        '''
        根据前面玩家的出牌来选牌，返回下一步所有合法出牌。
        '''
        if self.game.last_desc is None:
            movs = self.moves
        else:
            sm, mn, tp = last_desc
            movs = self.moves[ ( (self.moves['type']==tp)&(self.moves['main']>mn)&(self.moves['sum']==sm) )
                             | ( (self.moves['type']=='zha')&(self.moves['main']>mn) )
                             | (self.moves['type']=='buyao') | (self.moves['type']=='wangzha')  ]
        return movs.to_dict(orient='records')
    
    # 模型选择如何出牌
    def choose(self, state: GameState) -> List[int]:
        return []

    # 进行一步之后的公共操作
    def __common_step(self, move, move_desc):
        #分配花色/重新计算可行出牌; 移除出掉的牌; 记录
        out = []
        for card in move:
            out.append(self.__cards_left[str(card)].pop())
        self.moves = self.__get_all_moves(self.moves)
        self.game.cards_out.append( (self.player_id, move_desc[-1], out) )

        #是否牌局结束
        end = False
        if sum([len(v) for v in self.__cards_left.values()]) == 0:
            end = True
        return end, move_desc[-1]=='buyao'

    # 出牌
    def step(self, state):
        #在next_moves中选择出牌方法
        move = self.choose(state)
        desc = get_move_desc(move)
        end, buyao = self.__common_step(move, desc)
        return move, desc, end, buyao


class ManualAgent(Agent):
    def step(self, state):
        print("Player {}  ".format(self.player_id), end=' ')
        #输入举例: [9] 或 [10]*4 + [11]*2 等。不要或要不起输入[]
        desc = None
        while desc is None:
            move = eval(input())
            desc = get_move_desc(move)
            #todo: 检查已出牌数量
            if desc is not None:
                end, buyao = self.__common_step(move, desc)
                return move, desc, end, buyao


