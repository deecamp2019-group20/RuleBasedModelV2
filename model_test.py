from game.engine import Agent, Game, Card
import numpy as np


from rule_utils.rule_based_model import RuleBasedModel
from mcts.mcts_model import MctsModel
from mix_model.mix_model import MixModel


class RandomModel(Agent):
    def choose(self, state):
        valid_moves = self.get_moves()
        hand_card = []
        for i, n in enumerate(Card.all_card_name):
            hand_card.extend([n]*self.get_hand_card()[i])
        i = np.random.choice(len(valid_moves))
        move = valid_moves[i]
        # player i [手牌] // [出牌]
        print("Player {}".format(self.player_id), ' ', hand_card, end=' // ')
        print(Card.visual_card(move))
        return move, None


if __name__ == "__main__":
    cnt = 0
    game = Game([MixModel(0), RuleBasedModel(1), RuleBasedModel(2)])
    for i_episode in range(1000):
        game.game_reset()
        game.show()
        game.players[0].set_new_game()
        for i in range(100):
            pid, state, cur_moves, cur_move, winner, info = game.step()
            # game.show()
            if winner != -1:
                print('Winner:{}'.format(winner))
                if winner == 0:
                    cnt += 1
                break
        print("Winning Rate = ", cnt, "/", i_episode + 1, " = {:.2f}%\n".format(100 * cnt / (i_episode + 1)))
