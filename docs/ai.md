# AI Agent

## 責任分層

AI Agent 只負責根據目前可用資訊選擇 Action，不負責執行遊戲規則。

```text
GameCore
  -> CoreState
  -> get_legal_actions()
  -> Agent 選擇 CoreAction
  -> GameCore.apply_action()
  -> ActionResult
```

各元件責任如下：

| 元件 | 責任 |
|---|---|
| `GameCore` | 保存狀態、驗證 Action、執行規則、回傳 State 與 Events |
| `LegalActionGenerator` | 從 State 產生目前可執行的合法 Action |
| `RuleBasedAgent` | 從合法 Action 中選擇一個 Action |
| `RL Environment` | 將 CoreState 轉成 observation，計算 reward |
| CLI | 顯示狀態、收集真人輸入、建立 Action |

AI 不應直接依賴 `GameEngine`、`EffectResolver` 或 CLI renderer。

## Agent 介面

目前 Rule-based AI 的舊介面是：

```python
action = agent.choose_action(state)
```

這個介面目前直接接收完整 `GameState`，是可玩版本的暫時設計。

配合新的 Core API，長期介面應改為由呼叫端提供合法 Action：

```python
legal_actions = core.get_legal_actions(player_id)
action = agent.choose_action(state, legal_actions)
result = core.apply_action(action)
```

Agent 可以使用完整 `CoreState` 或外部建立的 observation，但 Agent 不應自行重寫合法性規則。

## Rule-based Agent

目前的實作位於 `src/ai_agent/`，包括：

- `AIAgent`：Agent 共用介面。
- `RuleBasedAgent`：目前可直接遊玩的基礎 AI。
- `card_knowledge.py`：直傷、AOE、解場武器與英雄技能的簡單知識表。

目前 AI 的大致優先順序：

1. 優先尋找能處理敵方手下的直傷、AOE、武器或英雄技能。
2. 攻擊時優先擊殺敵方手下。
3. 有嘲諷時只選擇合法的嘲諷目標。
4. 無法解場時，依費用與基本價值出牌。
5. 沒有更好行動時使用 Hero 或手下攻擊。
6. 沒有其他合法行動時結束回合。

AI 不解析卡面自然語言；目前透過 card id 知識表與 Core 提供的 State 判斷行動。

## CLI 整合

CLI 選擇 AI 對手時，建立 `RuleBasedAgent`。AI 回合的流程應是：

```text
CoreState
  -> GameCore.get_legal_actions(1)
  -> RuleBasedAgent.choose_action(...)
  -> GameCore.apply_action(action)
  -> 重複直到 AI 結束回合或牌局結束
```

CLI 只負責顯示 Core 回傳的 State 與 Events，不應把卡牌規則或合法性判斷複製到 AI。

## RL Agent 與 Environment

RL Agent 不直接取代 Core，也不直接操作 `GameEngine`。RL Environment 負責將 Core API 包裝成 RL 介面：

```text
CoreState
  -> ObservationBuilder
  -> Observation
  -> RL Agent
  -> CoreAction
  -> GameCore.apply_action()
  -> ActionResult
  -> Observation / Reward / Termination
```

RL Environment 的責任：

- 將 `CoreState` 轉成 observation。
- 依玩家視角處理資訊遮罩。
- 將 Agent 的輸出轉成 `CoreAction`。
- 根據 State 與 Events 計算 reward。
- 判斷 `terminated` 與 `truncated`。

Core 的責任：

- 提供完整 canonical State。
- 提供合法 Action。
- 驗證並執行 Action。
- 回傳結構化 Events。
- 判斷勝負與牌局是否結束。

第一版可以直接讓 Agent 使用 Core 的 `CoreAction`；固定長度 action encoding、action mask 與特定 RL framework adapter 留在 RL 層處理。

## 資訊邊界

Core 對外提供完整 canonical State。CoreState 中的卡牌與場上手下資訊至少包含：

- `card_id`
- `name`
- `card_type`
- `cost`
- `attack`
- `health`
- `description`
- 場上手下的目前生命、可攻擊狀態與 `statuses`

是否隱藏對手手牌、哪些欄位進入 observation，由 RL Environment 決定。AI 若需要受限資訊，也應由呼叫端提供相應的 view 或 observation，而不是讓 Agent 直接讀取 Core 內部資料。

## 未來 Agent

未來可以在相同的 Core API 上加入：

- RL Agent。
- 搜尋型 Agent。
- Self-play Agent。
- 外部服務型 Agent。

這些 Agent 都應遵守相同流程：取得可用資訊、選擇一個 `CoreAction`，再交由 `GameCore` 驗證與執行。
