# RuleBasedModelV1

## 环境

根据系统替换`RuleBasedModelV1/game/r`与`RuleBasedModelV1/rule_utils/env`

[于俊写的r](https://github.com/deecamp2019-group20/bottleneck)

[Combinational Q-Learning论文中的env](https://github.com/qq456cvb/doudizhu-C)

## Rule-based Model

### 基本思路

1. 拆牌, 直接调用了[Combinational Q-Learning](https://github.com/qq456cvb/doudizhu-C)写的拆牌器, 即<10张暴力拆完, 否则用DLX搜100个方案, 不保证最优但是基本包括比较常见的方案.
2. 评价牌组, 基于权重的方案评分, 权重参考DeecampReference中的[简书](https://www.jianshu.com/p/9fb001daedcf).
   - 补充了四带二的权重(与单牌一样).
   - 在每牌组的penalty上, 采用一个关于对手最少牌数线性增长的形式, 即越到后期手上多拆一组牌的代价越大, 会更倾向于出牌. **海耀提供**
3. 方案选择, 贪心选最好的拆牌方案, 能出牌的话选择一手出.

### 特判

局末经常攒着大牌不出, 增加两个特判:

1. 某方案只剩一手牌, 直接出
2. 对手最少牌数到四张, 能不Pass就不Pass

### 结果评价

- 坐庄打俩随机胜率.95+, 考虑到随机前期容易把自己牌打散, 大牌也是能出则出, 后期基本接不上, 意义不大
- 出牌整体呈现小牌优先(价值小), 缺少对牌组的整体考虑(例如自己能否接上拿回牌权), 拆大牌和出大牌仍不够果断, 有时呈现奇怪方式?

## MCTS Model

[致波 & 博林 MCTS](https://github.com/deecamp2019-group20/DC2019-DDZ-MCTS)

## Mixed Model

继承了Rule和MCTS, 当场上最少手牌数大于7时采用Rule决策, 否则采用MCTS