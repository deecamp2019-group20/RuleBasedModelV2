from __future__ import absolute_import
from engine import Agent, Game, Card
import numpy as np


from card import action_space
from decomposer import Decomposer
from evaluator import cards_value


name2card = {
    1: "A", 2: "2", 3: "3", 4: "4",
    5: "5", 6: "6", 7: "7", 8: "8",
    9: "9", 10: "10", 11: "J", 12: "Q",
    13: "K", 14: "*", 15: "$"
}
card2name = {v: k for k, v in name2card.items()}


class RuleBasedModel(Agent):
    def choose(self, state):
        # 获得手牌
        hand_card = []
        for ls in self.get_hand_card().values():
            hand_card.extend(list(ls))
        # 拆牌器和引擎用了不同的编码 1 -> A, B -> *, R -> $
        trans_hand_card = [str(c) for c in hand_card]
        trans_hand_card = ["A" if x == "1" else
                           "*" if x == "B" else
                           "$" if x == "R" else x for x in trans_hand_card]
        # 获得上家出牌
        last_move = [name2card[x] for x in self.game.last_move] if self.game.last_move is not None else []
        # 拆牌
        D = Decomposer()
        combs, fine_mask = D.get_combinations(trans_hand_card, last_move)
        # 根据对手剩余最少牌数决定每多一手牌的惩罚
        left_crads = [sum(len(v) for k, v in p.get_hand_card().items()) for p in self.game.players]
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
        move = [card2name[x] for x in best_cards]
        # 输出选择的牌组
        # print("\nbest comb: ")
        # for m in best_comb:
        #     print(action_space[m], cards_value[m])
        # 输出 player i [手牌] // [出牌]
        # print("Player {}".format(self.player_id), ' ', hand_card, end=' // ')
        # print(move)
        return move


class RandomModel(Agent):
    def choose(self, state):
        valid_moves = self.get_moves(self.game.last_move, self.game.last_desc)
        if self.game.last_move is None:
            valid_moves = [x for x in valid_moves if x["type"] != "buyao"]
        hand_card = []
        for ls in self.get_hand_card().values():
            hand_card.extend(list(ls))
        i = np.random.choice(len(valid_moves))
        tmp = valid_moves[i]
        move = []
        for k in Card.all_card_name:
            move.extend([int(k)] * tmp.get(k, 0))
        # player i [手牌] // [出牌]
        # print("Player {}".format(self.player_id), ' ', hand_card, end=' // ')
        # print(move)
        return move


cnt = 0
game = Game([RuleBasedModel(0), RandomModel(1), RandomModel(2)])
for i_episode in range(1000):
    game.game_reset()
    game.show()
    for i in range(100):
        winner = game.step()
        # game.show()
        if winner != -1:
            print('Winner:{}'.format(winner))
            if winner == 0:
                cnt += 1
            break
    print(cnt, "/", 1 + i_episode)