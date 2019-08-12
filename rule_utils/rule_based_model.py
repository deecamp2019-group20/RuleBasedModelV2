from game.engine import Agent, Card
import numpy as np


from rule_utils.card import action_space
from rule_utils.decomposer import Decomposer
from rule_utils.evaluator import cards_value
card_list = [
    "3", "4", "5", "6",
    "7", "8", "9", "10",
    "J", "Q", "K", "A",
    "2", "*", "$"
]


class RuleBasedModel(Agent):
    def choose(self, state):
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
        round_penalty = 15 - 12 * min_oppo_crads / 20  # 惩罚值调整为与敌人最少手牌数负线性相关
        # 寻找最优出牌
        best_move = None
        best_comb = None
        max_value = -np.inf
        for i in range(len(combs)):
            # 手牌总分
            total_value = sum([cards_value[x] for x in combs[i]])  # 计算牌组总分
            small_num = 0  # 如果一手牌为小牌, 需要加上惩罚值, 所以要统计小牌数量
            for j in range(0, len(combs[i])):  # 认为2, B, R是绝对大牌, 其他是小牌
                if j > 0 and action_space[j][0] not in ["2", "R", "B"]:
                    small_num += 1
            total_value -= small_num * round_penalty  # 减去小牌的惩罚值
            for j in range(0, len(combs[i])):
                # Pass 得分
                if combs[i][j] == 0 and min_oppo_crads > 4:  # 如果pass更优选择pass, 但是这里导致经常pass, 所以在对手小于4张时能不pass就不pass
                    if total_value > max_value:
                        max_value = total_value
                        best_comb = combs[i]
                        best_move = 0
                # 出牌得分
                elif combs[i][j] > 0 and (fine_mask is None or fine_mask[i, j] == True):  # 枚举非pass且fine_mask为True的出牌
                    # 特判只有一手
                    if len(combs[i]) == 1 or len(combs[i]) == 2 and combs[i][0] == 0:  # 如果只剩一手牌了, 直接出完 (不加这句经常局末不出牌了)
                        max_value = np.inf
                        best_comb = combs[i]
                        best_move = combs[i][-1]
                    move_value = total_value - cards_value[combs[i][j]] + round_penalty  # 出牌后的得分为减去价值, 返还惩罚值
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
        print(Card.visual_card(move))
        return move, None
