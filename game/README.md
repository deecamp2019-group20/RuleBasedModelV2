### python文件介绍
- actions.py 所有的action
- engine.py 引擎相关类
- gameutil.py 相关工具类

### 使用方法示例
```Python
from.game.engine import Agent

# 自己的模型继承Agent类并重写choose方法
class MyModel(Agent):
    
    def choose(self):
		'''
			模型根据当前状态选择出牌的方法
            说明：
			self.player_id 当前玩家的id，0代表地主，1代表地主下家，2代表地主上家
			self.get_hand_card() 当前剩余手牌，格式: {牌面: [Card]}
			self.game.cards_out 所有玩家按序打出的牌。格式：[ (player_id, type, move), ... ]
			self.game.last_desc 上家出的牌的描述（如果上家未出则是上上家），三元组（总张数，主牌rank，类型）
			self.game.last_move 上家出的牌


            应返回出牌列表，空列表表示不要/要不起， 格式举例：
            [13]
            [1,1,1,4]
            [3,3]
            [14,15]
            [2,2,2,2]
		'''

        return []

game = Game([MyModel(i) for i in range(3)])
MAX_ROUNDS = 100
TRAIND_ID = 0	# 进行训练的模型，0代表地主，1代表地主下家，2代表地主上家

for i_episode in range(1):
    game.game_reset()
    game.show()	# 输出当前各个玩家的手牌
    for i in range(MAX_ROUNDS):
        winner = game.step()	#-1代表游戏未结束，0代表地主获胜，1代表地主下家获胜，2代表地主上家获胜
        game.show()
        if winner != -1:
            
            if TRAIND_ID == 0 and winner == 0:
                # do some positive reward
            elif TRAIND_ID != 0 and winner != 0:
                # do some positive reward
            else:
                # do some negative reward
            
            break
    
```