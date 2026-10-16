# RL

這個資料夾負責將目前的卡牌遊戲核心引擎整理成適合 RL 使用的介面。

目前先以「可以執行的最小環境」為目標，不急著處理固定長度 observation、Action encoding 或特定 RL 演算法。

## 目前方向

第一版先直接使用完整的 `GameState`：

```text
GameState
  -> Agent 選擇現有的 Action
  -> CardGameEnv.step(action)
  -> GameEngine.apply_action(action)
  -> 回傳更新後的 GameState、reward、done、info
```

目前環境位於 `environment.py`：

```python
from src.rl import CardGameEnv
from src.actions.action import EndTurnAction

env = CardGameEnv(seed=7, reward_player_id=0)
state = env.reset()
result = env.step(EndTurnAction())
```

`CardGameEnv` 目前提供：

- `reset()`：建立新牌局並回傳完整 `GameState`。
- `reset(state=..., engine=...)`：使用外部建立的遊戲狀態。
- `step(action)`：接收現有的 `Action` 並交給 `GameEngine` 執行。
- `result.state`：更新後的完整遊戲狀態。
- `result.reward`：目前以指定的 `reward_player_id` 計算勝負 reward。
- `result.done`：遊戲是否結束。
- `result.info["logs"]`：這次 Action 產生的公開 Log。

## Observation 規劃

第一版的目標是讓 Agent 根據目前場面和手上資源做決策，不先加入歷史行動紀錄。

預計的資訊分類如下：

```text
Observation
├── 牌局基本資訊
│   ├── turn_number
│   ├── current_player
│   ├── phase
│   └── game_over / winner
│
├── 英雄資訊
│   ├── 我方英雄
│   └── 對手英雄
│
├── 場面資訊
│   ├── 我方場面
│   └── 對手場面
│
├── 手牌資訊
│   ├── 我方手牌內容
│   └── 對手手牌數量
│
└── 資源資訊
    ├── 我方 Mana / max Mana
    ├── 對手 Mana / max Mana
    ├── 我方牌庫數量
    └── 對手牌庫數量
```

Observation 應遵守玩家視角：

- 我方手牌可以看到完整內容。
- 對手手牌只能看到數量，不能看到卡牌內容。
- 雙方場上的手下是公開資訊。
- 不放入 RNG、Engine 內部 queue 或其他玩家不可見的資訊。

## 卡牌資訊與效果語意

卡牌遊戲不能只依賴攻擊力、生命值和費用。卡面描述包含效果語意，例如：

```text
造成 6 點傷害。
```

因此卡牌資訊需要同時保留：

- 卡牌基本資料：`card_id`、類型、費用、攻擊力、生命值、種族。
- 動態狀態：目前生命、攻擊力、可否攻擊、凍結、嘲諷等。
- 卡牌效果：`effect_id`、`target_rule`、Aura、Trigger 與效果順序。
- 卡面描述：中文或英文原始描述。

未來可以加入 `CardSemanticsExtractor`，把卡面文字轉成：

```text
原始文字
  -> 正規化文字
  -> 效果語意 embedding
  -> 結構化參數
```

例如：

```text
原始文字：造成 6 點傷害。
正規化文字：造成 [DAMAGE_AMOUNT] 點傷害。
結構化資料：
{
    "effect_type": "damage",
    "damage_amount": 6,
    "target_type": "enemy_character"
}
```

正規化文字可以交給 BERT 或其他 Language Model 取得固定維度的語意向量；精確數值、目標類型與效果參數則保留為結構化資料。

```text
文字 embedding：理解「這是一個傷害效果」
結構化數值：理解「傷害是 3 還是 6」
```

目前不把 one-hot 效果欄位視為唯一的長期方案，因為未來希望持續加入新卡牌與新效果，而不需要每次都修改 observation 維度。固定範圍的狀態欄位仍可以使用 binary 或 categorical representation。

## 第一版暫不處理

- 公開行動歷史與對手行為推測。
- 固定長度 observation tensor。
- Action encoding 與 action mask。
- BERT 或其他 Language Model 的實際串接。
- 完整自然語言卡牌解析器。
- 特定 RL 演算法與訓練流程。

先確認 `CardGameEnv`、GameState 邊界與 observation 資訊範圍正確，再逐步加入上述功能。
