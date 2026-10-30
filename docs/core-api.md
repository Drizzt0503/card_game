# Core API 契約

## 目的

本文件定義卡牌遊戲 Core 對外提供的 API。Core 負責完整牌局狀態、Action 驗證與執行、結構化 Event，以及牌局結束判斷。

RL、CLI 與其他外部使用者不應依賴 `GameEngine`、`EffectResolver` 或其他 Core 內部模組；它們應透過本文件定義的 `GameCore` 介面使用遊戲。

本文件是設計規格。目前專案尚未完整實作本契約。

## 設計方向

Core 採用 Imperative Game API：一次呼叫只執行一個完整 Action。

```text
外部使用者
  -> GameCore.apply_action(action)
  -> Core 驗證 Action
  -> Core 執行規則、Effect 與 Trigger
  -> 回傳新的 State snapshot 與 Events
```

Core 內部可以繼續使用 mutable `GameState` 與 `GameEngine`，但對外必須提供穩定、獨立的 snapshot 與資料結構。

Action 的產生與執行分離：`GameEngine` 不負責列舉目前所有可能的 Action；它只負責驗證與執行外部送入的 Action。合法 Action 的產生由獨立的 `LegalActionGenerator` 負責。

## 對外介面

```python
class GameCore:
    def reset(self, config: GameConfig | None = None) -> CoreState:
        ...

    def get_state(self) -> CoreState:
        ...

    def get_legal_actions(self, player_id: int) -> tuple[CoreAction, ...]:
        ...

    def validate_action(self, action: CoreAction) -> ActionValidation:
        ...

    def apply_action(self, action: CoreAction) -> ActionResult:
        ...

    def is_terminal(self) -> bool:
        ...

    def get_winner(self) -> int | None:
        ...
```

### reset

`reset` 建立新遊戲並回傳初始 State。

```python
state = core.reset(
    GameConfig(
        seed=7,
        player_classes=("MAGE", "WARRIOR"),
    )
)
```

`seed` 必須控制洗牌、先後手、隨機目標、隨機卡牌或 Token，以及其他隨機 Effect。

同一個設定、相同的初始狀態與相同的 Action 序列，必須產生相同的 State 與 Event 序列。

### get_state

回傳目前完整的 canonical State snapshot。

Core API 回傳完整狀態，不負責玩家視角遮罩。手牌隱藏、玩家可見資訊與 RL observation 由外部 adapter 處理。

State 至少包含：

```text
CoreState
├── turn_number
├── current_player_id
├── phase
├── players
├── winner_id
└── game_over
```

回傳的 snapshot 必須是 immutable 或 detached copy。外部修改 snapshot 不得影響 Core 內部狀態。

### 卡牌與場上手下資訊

第一版採用簡單的資訊格式：手牌與場上手下都直接提供卡面基本資訊與卡面文字。

```text
CardInfo
├── card_id
├── name
├── card_type
├── cost
├── attack
├── health
└── description
```

手牌中的卡牌至少提供：

```text
instance_id
card_id
name
card_type
cost
attack
health
description
```

場上手下提供相同的卡面資訊，並額外提供目前戰場狀態：

```text
attack
hp
max_hp
can_attack
attacks_remaining
statuses
```

`statuses` 是公開狀態 ID 的集合，例如 `taunt`、`frozen`、`divine_shield` 與 `windfury`。

第一版不要求外部依賴 `effect_id`、`aura_ids`、`trigger_ids` 或其他 Core 內部實作欄位。外部透過 `description` 取得卡面文字。

### get_legal_actions

回傳指定玩家在目前狀態下可以執行的完整 Action：

```python
actions = core.get_legal_actions(player_id=0)
```

Core 必須處理 Mana、手牌、出牌目標、手下攻擊、攻擊目標、嘲諷、Hero 攻擊、Hero Power、目前玩家與牌局結束等合法性規則。

`get_legal_actions` 不等於列出所有可能的非法 Action；Core 不需要提供 `get_all_actions()`。

對外的 `GameCore.get_legal_actions()` 由內部的 `LegalActionGenerator` 提供結果。Generator 從 State 產生各類 Action 的候選，再交給 `GameEngine.validate_action()` 驗證；合法性規則只由 Engine 維護一份。

### validate_action

對外部提供的單一 Action 進行合法性檢查：

```python
validation = core.validate_action(action)

if validation.is_legal:
    ...
```

`validate_action` 不得修改牌局狀態，也不應消耗或改變隨機數狀態。

```python
@dataclass(frozen=True)
class ActionValidation:
    is_legal: bool
    error: CoreError | None = None
```

### apply_action

一次只執行一個完整 Action：

```python
result = core.apply_action(action)
```

Core 必須在執行時再次驗證 Action。外部先呼叫 `validate_action` 不代表之後可以跳過驗證。

Core 不提供一次送入多個 Action 的 batch API。外部若要執行多步，必須逐次呼叫：

```python
for action in actions:
    result = core.apply_action(action)
```

## ActionResult

```python
@dataclass(frozen=True)
class ActionResult:
    accepted: bool
    state: CoreState
    events: tuple[CoreEvent, ...]
    error: CoreError | None = None
```

合法 Action 的結果：

```text
accepted == True
error is None
state == 執行後的完整 State snapshot
events == 本次 Action 產生的有序 Events
```

非法 Action 的結果：

```text
accepted == False
events == ()
state == 執行前狀態的 detached snapshot
error != None
```

非法 Action 不得造成部分執行或部分狀態修改。

`CoreError` 應包含穩定錯誤代碼，文字只作為輔助資訊：

```python
@dataclass(frozen=True)
class CoreError:
    code: str
    message: str
```

例如：`INVALID_TARGET`、`INSUFFICIENT_MANA`、`NOT_CURRENT_PLAYER`、`MINION_CANNOT_ATTACK`、`GAME_ALREADY_OVER`、`UNSUPPORTED_ACTION`。

## CoreEvent

Core 已經採用 Effect、Event 與 Trigger 的內部架構，因此對外回傳結果應使用結構化 Event，而不是 CLI 文字 Log。

```python
@dataclass(frozen=True)
class CoreEvent:
    event_type: str
    source_id: int | None
    target_id: int | None
    data: Mapping[str, object]
```

Event 必須依實際發生順序排列，內容可以包括卡牌打出、召喚、傷害、治療、抽牌、Trigger、死亡、回合開始/結束、Hero 死亡與牌局結束。

範例：

```python
CoreEvent(
    event_type="damage_dealt",
    source_id=12,
    target_id=25,
    data={"amount": 6, "target_kind": "hero"},
)
```

Event 是機器可讀的遊戲事實，不負責 UI 顯示、RL reward、RL observation 或 Action encoding。

## 內部責任分工

### GameEngine

`GameEngine` 是 Core 的規則執行器，不負責列舉 possible actions。

```python
class GameEngine:
    def validate_action(
        self,
        state: GameState,
        action: CoreAction,
    ) -> ActionValidation:
        ...

    def apply_action(
        self,
        state: GameState,
        action: CoreAction,
    ) -> ActionResult:
        ...
```

`validate_action()` 必須是 read-only，不修改 State，也不消耗 RNG。`apply_action()` 執行前必須再次驗證 Action。

### LegalActionGenerator

`LegalActionGenerator` 從 State 產生 Action 候選，並使用 `GameEngine.validate_action()` 過濾出合法 Action：

```python
class LegalActionGenerator:
    def get_actions(
        self,
        state: GameState,
        player_id: int,
    ) -> tuple[CoreAction, ...]:
        ...
```

Generator 可以依 Action 類型分拆內部 provider：

```text
LegalActionGenerator
├── PlayCardActionProvider
├── MinionAttackActionProvider
├── HeroAttackActionProvider
├── HeroPowerActionProvider
└── EndTurnActionProvider
```

Generator 不修改 State、不執行 Action，也不應自行維護另一套合法性規則。

### GameCore

`GameCore` 是對外 facade，負責管理目前 State，並將查詢與執行委派給對應元件：

```text
GameCore
├── get_legal_actions()
│   └── LegalActionGenerator
├── validate_action()
│   └── GameEngine.validate_action()
└── apply_action()
    └── GameEngine.apply_action()
```

## 遊戲結束

遊戲結束資訊必須存在於 State snapshot：

```python
state.game_over
state.winner_id
state.phase
```

並提供：

```python
core.is_terminal()
core.get_winner()
```

Hero 死亡後，該次 `ActionResult` 必須包含更新後 State、`game_over=True`、正確的 `winner_id`，以及對應的死亡與結束 Events。

## 責任邊界

### Core 負責

- 完整遊戲狀態與 State snapshot。
- Action schema、合法 Action 查詢與合法性驗證。
- Action 執行、Effect、Trigger 與結構化 Events。
- 隨機 seed 與可重現性。
- 遊戲結束與勝利者。

### Core 不負責

- RL observation 與玩家視角遮罩。
- Action encoding、Tensor 或 action mask 格式。
- Reward、Gym/PettingZoo wrapper。
- CLI 顯示文字。
- AI 決策。
- 一次執行多個 Action 的 batch API。

## 驗收條件

1. `reset()` 能回傳完整初始 State。
2. 合法出牌後，結果包含更新後的手牌、Mana、場面與 Events。
3. 非法 Action 回傳結構化 error，且 State 完全不變。
4. `get_legal_actions()` 回傳的每個 Action 都通過 `validate_action()`。
5. `validate_action()` 不修改 State，也不改變 RNG 狀態。
6. `apply_action()` 對非法 Action 不產生任何 Event。
7. 死亡、Trigger、抽牌與回合事件順序穩定。
8. Hero 死亡後正確回傳 `game_over` 與 `winner_id`。
9. 相同 seed 與相同 Action 序列產生相同 State 與 Events。
10. 外部只依賴 `ActionResult.state` 就能連續執行遊戲，不需要存取 `GameEngine` 或 `EffectResolver`。

## 與目前程式的關係

目前的 `GameEngine.apply_action(state, action)` 是 Core 內部規則執行器，不直接等同於本文件的對外 API。

未來應由 `GameCore` facade 包住目前的：

```text
GameState
GameEngine
LegalActionGenerator
EffectResolver
TriggerEngine
```

並將目前的人類可讀 Log 逐步轉換成對外的 `CoreEvent`。既有 CLI 可以繼續將 `CoreEvent` 格式化成中文顯示，RL 則透過 adapter 將 `CoreState` 轉成 observation。
