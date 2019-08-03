from __future__ import absolute_import
import sys
import os
sys.path.insert(0, os.path.join('..'))

from game.engine import Agent, Game, Card
from mcts.tree_policy import tree_policy
from mcts.default_policy import default_policy
from mcts.backup import backup
from mcts.tree import Node, State
from mcts.get_moves import get_moves
from mcts.get_bestchild import get_bestchild1
import numpy as np
from collections import Counter
import time


from rule_utils.card import action_space
from rule_utils.decomposer import Decomposer
from rule_utils.evaluator import cards_value
card_list = [
    "3", "4", "5", "6",
    "7", "8", "9", "10",
    "J", "Q", "K", "A",
    "2", "*", "$"
]


class MixModel(Agent):
    def __init__(self, player_id):
        super(MixModel, self).__init__(player_id)
        root = Node(None, None)
        self.current_node = root

    def choose(self, state):
        min_crads = min([sum(p.get_hand_card()) for p in self.game.players])
        if min_crads > 7:
            # 获得手牌
            hand_card = self.get_hand_card()
            # 拆牌器和引擎用了不同的编码 1 -> A, B -> *, R -> $
            trans_hand_card = [card_list[i] for i in range(15) for _ in range(hand_card[i])]
            # 获得上家出牌
            last_move = [card_list[i] for i in range(15) for _ in range(state.last_move[i])]
            # 拆牌
            D = Decomposer()
            combs, fine_mask = D.get_combinations(trans_hand_card, last_move)
            # 根据对手剩余最少牌数决定每多一手牌的惩罚
            left_crads = [sum(p.get_hand_card()) for p in self.game.players]
            min_oppo_crads = min(left_crads[1], left_crads[2]) if self.player_id == 0 else left_crads[0]
            round_penalty = 15 - 12 * min_oppo_crads / 20
            # 寻找最优出牌
            best_move = None
            best_comb = None
            max_value = -np.inf
            for i in range(len(combs)):
                # 手牌总分
                total_value = sum([cards_value[x] for x in combs[i]])
                small_num = 0
                for j in range(0, len(combs[i])):
                    if j > 0 and action_space[j][0] not in ["2", "R", "B"]:
                        small_num += 1
                total_value -= small_num * round_penalty
                for j in range(0, len(combs[i])):
                    # Pass 得分
                    if combs[i][j] == 0 and min_oppo_crads > 4:
                        if total_value > max_value:
                            max_value = total_value
                            best_comb = combs[i]
                            best_move = 0
                    # 出牌得分
                    elif combs[i][j] > 0 and (fine_mask is None or fine_mask[i, j] == True):
                        # 特判只有一手
                        if len(combs[i]) == 1 or len(combs[i]) == 2 and combs[i][0] == 0:
                            max_value = np.inf
                            best_comb = combs[i]
                            best_move = combs[i][-1]
                        move_value = total_value - cards_value[combs[i][j]] + round_penalty
                        if move_value > max_value:
                            max_value = move_value
                            best_comb = combs[i]
                            best_move = combs[i][j]
                if best_move is None:
                    best_comb = [0]
                    best_move = 0
            # 最优出牌
            best_cards = action_space[best_move]
            move = [best_cards.count(x) for x in card_list]
            # 输出选择的牌组
            # print("\nbest comb: ")
            # for m in best_comb:
            #     print(action_space[m], cards_value[m])
            # 输出 player i [手牌] // [出牌]
            print("Player {}".format(self.player_id), ' ', Card.visual_card(hand_card), end=' // ')
            print(Card.visual_card(move), "From RuleBasedModel")
            return move, None

        #  start = time.time()
        #  定位current_node
        cards_out = self.game.cards_out
        length = len(cards_out)
        #  判断是否定位到current_node的flag
        flag = 0
        if length > 2:
            #  前两步对手选择的move
            out1 = self.list_to_card(cards_out[length-2][1])
            out2 = self.list_to_card(cards_out[length-1][1])
            for child in self.current_node.get_children():
                if self.compare(child.state.action, out1):
                    self.current_node = child
                    flag = 1
                    break
            if flag == 1:
                for child in self.current_node.get_children():
                    if self.compare(child.state.action, out2):
                        self.current_node = child
                        flag = 2
                        break

        my_id = self.player_id
        if flag != 2:
            root = Node(None, None)
            self.current_node = root

            #  下家id
            next_id = (my_id + 1) % 3
            #  下下家id
            next_next_id = (my_id + 2) % 3
            my_card = self.card_list_to_dict(self.get_hand_card())
            #  下家牌
            next_card = self.card_list_to_dict(self.game.players[next_id].get_hand_card())
            #  下下家牌
            next_next_card = self.card_list_to_dict(self.game.players[next_next_id].get_hand_card())
            last_move = self.trans_card(Card.visual_card(self.game.last_move))
            last_p = self.game.last_pid
            moves_num = len(get_moves(my_card, last_move))
            state = State(my_id, my_card, next_card, next_next_card, last_move, -1, moves_num, None, last_p)
            self.current_node.set_state(state)

        #  搜索
        computation_budget = 2000
        for i in range(computation_budget):
            expand_node = tree_policy(self.current_node, my_id)
            reward = default_policy(expand_node, my_id)
            backup(expand_node, reward)
        best_next_node = get_bestchild1(self.current_node)
        move = best_next_node.get_state().action
        self.current_node = best_next_node
        new_move = self.card_to_list(move)

        hand_card = []
        for i, n in enumerate(Card.all_card_name):
            hand_card.extend([n] * self.get_hand_card()[i])
        print("Player {}".format(self.player_id), ' ', hand_card, end=' // ')
        print(Card.visual_card(new_move), "From MctsModel")
        #  end = time.time()
        #  dur = end - start
        #  print('cost: {}'.format(dur))
        return new_move, None

    @staticmethod
    #  用于比较两个无序的list
    def compare(s, t):
        return Counter(s) == Counter(t)

    @staticmethod
    def trans_card(before):
        after = []
        for card in before:
            after.append(int(card))
        return after

    @staticmethod
    def card_list_to_dict(card_list):
        #  e.g. [3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0] -> ['3':3, '4':3, '5':0, '6':0, '7':0, '8':0, '9':0, '10':0, '11':0, '12':0, '13':0, '1':1, '2':1, '14':0, '15':0]
        card_name = Card.all_card_name
        card_dict = dict(zip(card_name, card_list))
        return card_dict

    @staticmethod
    def card_to_list(before):
        #  e.g. [3, 3, 3, 4, 4, 4, 1, 2] -> [3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0]
        # index = [str(i) for i in range(3, 14)] + ['1', '2', '14', '15']
        tem = [0] * 15
        for card in before:
            tem[card - 1] += 1
        tem = tem[2:-2] + tem[:2] + tem[-2:]
        return tem

    @staticmethod
    def list_to_card(before):
        #  e.g. [3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0] -> [3, 3, 3, 4, 4, 4, 1, 2]
        cards = [i for i in range(3, 14)] + [1, 2, 14, 15]
        card = []
        for i, j in enumerate(before):
            card += ([cards[i]] * j)
        return card

class RandomModel(Agent):
    def choose(self, state):
        valid_moves = self.get_moves()

        # player i [手牌] // [出牌]
        hand_card = []
        for i, n in enumerate(Card.all_card_name):
            hand_card.extend([n]*self.get_hand_card()[i])
        #  print("Player {}".format(self.player_id), ' ', hand_card, end=' // ')

        i = np.random.choice(len(valid_moves))
        move = valid_moves[i]
        #  print(Card.visual_card(move))

        return move, None


if __name__=="__main__":
    #   game = Game([RandomModel(i) for i in range(3)])
    game = Game([RandomModel(0), RandomModel(1), RandomModel(2)])
    # win_count = [0, 0, 0]
    for i_episode in range(1):
        game.game_reset()
        # game.show()
        for i in range(100):
            pid, state, cur_moves, cur_move, winner, info = game.step()
            #game.show()
            if winner != -1:
                print(str(i_episode) + ': ' + 'Winner:{}'.format(winner))
                #  win_count[winner] += 1
                break
    #  print(win_count)