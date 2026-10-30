# Core 基礎架構與資訊邊界

## 目的

本文件定義卡牌遊戲 Core 的基礎分層。其他 Engine、卡牌、AI、RL 與牌局管理文件，都應以本文件為共同基準。

核心原則：

```text
Rules 是遊戲規則與靜態資料的來源。
GameState 保存牌局目前的資料與動態狀態。
Engine 將外部 Action 轉譯成可執行的遊戲流程。
Resolver 執行 Effect、更新 State 並產生 Event。
```

第一層先固定以下核心元件：

```text
Data
Rule
  -> Engine
  -> Resolver
  -> GameState
```

- `Data`：保存卡牌與其他遊戲內容的靜態資料。
- `Rule`：以人類可閱讀、且可被條理化的形式定義遊戲規則。
- `Engine`：將 Rule 轉譯成可執行的驗證與效果計畫。
- `GameState`：保存某一場遊戲目前的狀態。
- `Resolver`：執行效果計畫，讓遊戲從目前狀態推進到穩定狀態。

Data 保存靜態內容，Rule 是規則的唯一來源。Engine 不應另外維護一套隱藏規則；GameState 不保存卡牌效果實作；Resolver 不負責判斷外部 Action 是否合理。

Rule 必須是「人類可讀的結構化規則」，不能只是無法解析的任意自然語言。人可以閱讀同一份 Rule 理解怎麼玩，Engine 則將同一份 Rule 轉譯成程式流程。

例如：

```text
Fireball:
- 消耗 4 Mana。
- 目標：一個敵方角色。
- 對目標造成 6 點傷害。
```

Engine 將它轉成：

```text
SpendMana(4)
DealDamage(target, 6)
```

## 整體資料流

```text
外部 Action
  -> Rules 判斷語意與合法性
  -> Engine 轉譯成 Effect / 執行計畫
  -> Resolver 執行 Effect
  -> 更新 GameState
  -> 產生 Event
  -> 回傳 State snapshot 與 Event
```

合法 Action 的查詢：

```text
GameState
  -> LegalActionGenerator
  -> Rules / RuleBook
  -> 合法 CoreAction 清單
```

## Rules

Rules 是遊戲規則的來源，不屬於 Engine，也不屬於 RL。

Rules 包含：

- 卡牌定義與卡牌靜態資料。
- 卡牌文字與基本數值。
- 目標規則。
- Action 合法性規則。
- 回合與資源規則。
- 戰鬥規則。
- Effect、Aura 與 Trigger 的遊戲語意。
- 規則版本。

外部可以查詢卡牌規則：

```python
card_rule = rules.get_card("fireball")
```

查詢結果可以包含：

```text
card_id, name, card_type, cost, attack, health,
tribe, description, target_rule
```

Rules 不保存某一場遊戲的手牌、場面或目前生命值。

## GameState

GameState 只保存某一場牌局的目前狀態，不重複保存整份卡牌規則或效果實作。

手牌至少保存：

```text
instance_id
card_id
current_cost
```

場上手下至少保存：

```text
instance_id
card_id
attack
hp
max_hp
can_attack
attacks_remaining
statuses
```

`statuses` 是公開狀態 ID 的集合，例如 `taunt`、`frozen`、`divine_shield`、`windfury` 與 `charge`。

卡牌名稱、卡面文字、原始費用與卡牌效果語意由 `card_id` 查詢 Rules 取得；目前攻擊力、生命、凍結與本回合是否可攻擊則由 GameState 提供。

完整卡牌資訊來自：

```text
GameState.card_id
  + Rules.get_card(card_id)
  -> 完整卡牌資訊
```

## Engine

Engine 是 Action 到遊戲執行流程的轉譯器與協調器，不是規則的唯一來源。

Engine 負責：

- 接收外部 Action。
- 呼叫 Rules 判斷 Action 語意與合法性。
- 將 Action 轉成 Effect 或執行計畫。
- 將執行順序交給 Resolver。
- 協調 State 更新、死亡清理與 Event 流程。

Engine 不應另外維護一套與 Rules 不同的卡牌或合法性規則。

概念介面：

```python
class GameEngine:
    def validate_action(self, state, action):
        ...

    def translate_action(self, state, action):
        ...

    def apply_action(self, state, action):
        ...
```

## Resolver

Resolver 負責執行 Engine 產生的 Effect：

- 執行 Effect。
- 修改 GameState。
- 產生結構化 Event。
- 依 Event 觸發後續 Trigger。
- 處理死亡清理與後續效果。

Resolver 不負責決定外部 Action 是否應該出現，也不負責產生 RL reward。

## LegalActionGenerator

`LegalActionGenerator` 從 GameState 產生目前玩家的合法 Action。

可以依 Action 類型分拆：

```text
LegalActionGenerator
├── PlayCardActionProvider
├── MinionAttackActionProvider
├── HeroAttackActionProvider
├── HeroPowerActionProvider
└── EndTurnActionProvider
```

Generator 使用 Rules、GameState 與 Engine validation，但不執行 Action，也不修改 State。

```text
GameState
  -> Generator 產生候選 Action
  -> Rules / Engine validation
  -> 合法 CoreAction
```

## GameCore facade

GameCore 是外部使用者的統一入口，不承擔卡牌規則的唯一實作責任。

```python
class GameCore:
    def reset(self, config=None):
        ...

    def get_state(self):
        ...

    def get_legal_actions(self, player_id):
        ...

    def validate_action(self, action):
        ...

    def apply_action(self, action):
        ...

    def is_terminal(self):
        ...

    def get_winner(self):
        ...
```

GameCore 負責把外部 API 連接到 Rules、Engine、Resolver 與 GameState，但不應把 RL observation、reward 或 action encoding 放入 Core。

## 對外資訊揭露規則

Core 對外回傳 canonical state 時：

- State 提供 instance ID、card ID 與動態狀態。
- 靜態卡牌資訊透過 Rules / RuleBook 由 card ID 查詢。
- 場上手下的攻擊、生命、可攻擊狀態與 statuses 由 State 提供。
- Events 使用 card ID、instance ID 與結構化資料。
- 不要求外部依賴 `effect_id`、`aura_ids`、`trigger_ids` 等內部欄位。
- 玩家視角遮罩與 RL observation 由外部 adapter 負責。

## 規則版本與可重現性

Rules 必須有版本識別，例如：

```text
ruleset_version = "basic_set_2014_v1"
```

Replay、RL episode 與測試至少記錄：

- ruleset version。
- random seed。
- 初始設定。
- Action 序列。

同一個 ruleset version、seed、初始設定與 Action 序列，應產生相同的 State 與 Event 序列。

## 非目標

本文件不定義：

- RL observation 的固定格式。
- Action encoding 或 tensor shape。
- Reward 設計。
- CLI 顯示格式。
- 特定 RL 演算法。
- 特定網路傳輸格式。
