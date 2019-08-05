# -*- coding: utf-8 -*-
"""
自定义相关类
"""
import numpy as np
from typing import List, Tuple, Dict
import pandas as pd
from collections import defaultdict
from os.path import join, abspath, dirname
from .card_util import All as backup, cache
from .gameutil import card_show
from copy import copy
from .r import get_moves

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
        self.last_move = [0]*15 # 上一个有效出牌，全零表示主动权
        self.last_pid = -1 # 上一个有效出牌的玩家编号，-1表示主动权
        self.last_move_ = np.zeros(15, dtype=int)  # 上一个出牌，不管有效与否
        self.last_last_move_ = np.zeros(15, dtype=int) # 上上个出牌，不管有效与否

class Game(object):
    def __init__(self, agents: List['Agent']):
        # 初始化players
        self.players = agents
        for p in agents:
            p.game = self
        self.game_reset()

    def get_state(self)->GameState:
        state = GameState()
        state.hand = self.players[self.index].get_hand_card().copy()
        tmp, state.out = Card.vectorized_card_out(self.cards_out, len(self.players))
        state.up_out = tmp[self.get_up_index()]
        state.down_out = tmp[self.get_down_index()]
        state.self_out = tmp[self.index]
        state.other_hand = (np.array([4]*13+[1,1]) - state.hand - state.out).tolist()
        state.last_move = self.last_move.copy()
        state.last_pid = self.last_pid
        if len(self.cards_out)>=1:
            self.last_move_ = self.cards_out[-1][-1].copy()
        if len(self.cards_out)>=2:
            self.last_last_move_ = self.cards_out[-2][-1].copy()
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
        self.last_move = [0]*15
        self.last_pid = -1
        self.playround = 1  # 回合数
        self.index = 0  # 当前玩家的id，0代表地主，1代表地主下家，2代表地主上家
        self.yaobuqis = []
        return self.players[0].get_hand_card(),\
               self.players[1].get_hand_card(),\
               self.players[2].get_hand_card(),\
               Card.vectorized_card_list(self.mingpai)

    
    #游戏进行    
    def step(self):
        player = self.players[self.index]
        state = self.get_state()
        state, cur_moves, cur_move, self.end, info = player.step(state) #返回：在状态state下，当前玩家的出牌列表、游戏是否结束、choose自定义返回值
        if sum(cur_move)==0:
            self.yaobuqis.append(self.index)
            #都要不起
            if len(self.yaobuqis) == len(self.players)-1:
                self.yaobuqis = []
                self.last_move = [0]*15
                self.last_pid = -1
        else:
            self.yaobuqis = []
            self.last_move = cur_move
            self.last_pid = self.index

        winner = -1
        if self.end:
            winner = self.index

        self.index = self.index + 1
        #一轮结束
        if self.index >= len(self.players):
            self.playround = self.playround + 1
            self.index = 0
        
        return player.player_id, state, cur_moves, cur_move, winner, info

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
    #color_show = {'a': '♠', 'b':'♥', 'c':'♣', 'd':'♦'}
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
    def visual_card(cards):
        c = []
        for i, n in enumerate(Card.all_card_name):
            c.extend([n]*cards[i])
        return c

    @staticmethod
    def vectorized_card_list(cards: List):
        v = [0] * len(Card.all_card_name)
        for c in cards:
            if isinstance(c, int):
                i = Card.name_to_rank[str(c)]-1
            elif isinstance(c, str):
                i = Card.name_to_rank[c]-1
            elif isinstance(c, Card):
                i = c.rank-1
            else:
                print("Warn: Unkown card.")
            v[ i ]+=1
        return v

    @staticmethod
    def vectorized_card_out(cards_out: List[Tuple[int, np.array]], total_player=3):
        cnt = {}
        for rec in cards_out:
            a = cnt.get(rec[0], np.zeros( 15, dtype=int )) # 15
            b = np.array( rec[-1], dtype=int  )
            cnt[rec[0]] = a+b
        a = np.zeros( 15, dtype=int )
        for v in cnt.values():
            a+=v
        res = []
        for i in range(total_player):
            res.append(cnt.get(i, np.zeros( 15, dtype=int )).tolist())
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
        #return Card.name_show.get(self.name, self.name) + Card.color_show.get(self.color, self.color)
    
    __repr__ = __str__
    
def get_move_desc(move: List[int]):
    """
    输入出牌， 返回牌型描述：总张数，主牌rank，类型
    move: 长度为15的数组，元素表示3/4/5/...15出多少张。全零表示不要。
    """
    lst = []
    for i, n in enumerate(Card.all_card_name):
        lst.extend([int(n)]*move[i])
    key = str(sorted(lst))
    return cache[key]

def group_by_type(moves: List[Dict]):
    """
    输入moves， 返回按牌型分组的描述。
    返回值：
    { 'type1': [(move1, desc1), ...], ...  }
    move1 是一个15的列表，desc1是namedtuple，可用属性：sum/type/main/kicker
    """
    res = defaultdict(list)
    for m in moves:
        desc = get_move_desc(m)
        res[desc.type].append( (m, desc) )
    return res

############################################
#              玩家相关类                   #
############################################
class Agent(object):
    """
    玩家类,所有模型都应继承此类并重写choose方法
    """
    def __init__(self, player_id):
        self.player_id = player_id  # 0代表地主，1代表地主下家，2代表地主上家
        self.__cards_left = np.zeros(15, dtype=int) # 表示3/4/5.../15有多少张
        self.game = None
        self.state = None  # 当前游戏状态

    def set_hand_card(self, cards):
        self.__cards_left = np.zeros(15, dtype=int) # 表示3/4/5.../15有多少张
        for c in cards:
            self.__cards_left[c.rank-1]+=1

    def get_hand_card(self):
        return self.__cards_left

    def get_moves(self):
        '''
        根据前面玩家的出牌来选牌，返回下一步所有合法出牌。
        '''
        moves = get_moves(self.__cards_left, self.game.last_move)
        return moves
    
    # 模型选择如何出牌
    def choose(self, state: GameState) -> Tuple[List[int], object]:
        return [], None

    # 进行一步之后的公共操作
    def __common_step(self, move):
        #移除出掉的牌; 记录
        try:
            assert( np.all(self.__cards_left>=move)  )
            assert( np.all(self.__cards_left[:-2]<=4) and np.all(self.__cards_left[-2:])<=1 )
        except AssertionError:
            print("手牌：", self.__cards_left)
            print("出牌：", move)
            raise AssertionError()
        self.__cards_left -= move
        self.game.cards_out.append( (self.player_id, move) )

        #是否牌局结束
        end = False
        if self.__cards_left.sum() == 0:
            end = True
        return end

    # 出牌
    def step(self, state):
        self.move_list = self.get_moves() # 可在self.choose里使用
        move, info = self.choose(state)
        end = self.__common_step(move)
        return state, self.move_list, move, end, info

    def observation(self):
        return self.game.get_state(), self.get_moves()


