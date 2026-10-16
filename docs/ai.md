# AI Agent

## 目前設計

AI 位於 `src/ai_agent/`，目前提供：

- `AIAgent`：未來 Rule-based、RL、搜尋型 Agent 共用的介面。
- `RuleBasedAgent`：目前可直接遊玩的基礎 AI。
- `card_knowledge.py`：AI 對直傷、AOE、解場武器與英雄技能的簡單知識表。

目前 AI 的介面是：

```python
action = agent.choose_action(state)
```

它現在接收完整 `GameState`，不是嚴格的玩家視角 observation。這是目前為了快速完成可玩版本的暫時設計。

## Rule-based 行為優先順序

目前 AI 大致依照以下順序：

1. 先找可以處理敵方手下的直傷、AOE、武器或英雄技能。
2. 攻擊時優先擊殺敵方手下，再處理威脅最高的目標。
3. 有 Taunt 時只選擇合法的 Taunt 目標。
4. 若無法解場，依費用與基本價值出牌。
5. 最後才讓 Hero 或手下打臉。
6. 沒有更好行動時結束回合。

AI 不解析中文/英文卡牌描述，而是透過 card id 知識表與遊戲狀態判斷效果。

## CLI 整合

`src/cli/main.py` 在 Player 2 選擇 AI 時建立 `RuleBasedAgent`。AI 回合會在背景連續選擇 Action，真人看不到 AI 回合中的即時畫面，但下一個真人回合會看到公開 Log 與目標。

## RL 需要新增的層

建議新增：

```text
src/rl/
├── observation.py
├── action_space.py
├── environment.py
└── rewards.py
```

責任建議如下：

- `ObservationBuilder`：從 GameState 產生指定玩家可見的 observation。
- `ActionSpace`：定義合法 Action 的編碼與 mask。
- `CardGameEnv`：提供 `reset()`、`step(action)`、`done`。
- `RewardModel`：定義勝利、死亡、解場與資源使用的 reward。

RL 版本不應直接讀 CLI renderer，也不應依賴中文卡牌文字。卡牌效果應由 domain/engine 執行，Agent 只接收 observation 並回傳 Action。
