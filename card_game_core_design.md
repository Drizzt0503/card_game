# 卡牌對戰 CLI 核心架構整理

## 目標

先做一個類似《爐石戰記》的 CLI 卡牌對戰遊戲。

重點不是 UI，而是先把核心規則與結算流程設計清楚。

---

## 1. Entity

`Entity` 代表遊戲世界中可以被識別、操作或影響的東西。

目前先定：

- `Hero`
- `CardInHand`
- `Minion`
- `Board`
- `Player`

其中玩家在自己的回合中主要可以主動選擇：

- `Hero`
- `CardInHand`
- `Minion`

### Hero

主要狀態例如：

- HP
- Armor
- Hero Skill

可主動產生的 Action：

- `HeroSkillAction`

之後如果加入武器，也可以加：

- `HeroAttackAction`

### CardInHand

主要狀態例如：

- card id
- name
- cost
- type
- effects
- target rule

玩家對手牌的主動操作只有：

- `PlayCardAction`

不同牌的差異不在 Action 類型，而在它具有哪些 `Effect`。

例如：

白板怪：

`PlayCardAction -> SummonEffect`

火球：

`PlayCardAction -> DamageEffect`

Buff 卡：

`PlayCardAction -> BuffEffect`

有戰吼的怪：

`PlayCardAction -> SummonEffect + Battlecry 相關效果`

### Minion

主要狀態例如：

- attack
- hp
- max_hp
- status
- trigger

第一版玩家主動操作先只做：

- `AttackAction`

像嘲諷、死亡之聲、光環等，不是玩家主動 Action。

---

## 2. Action

`Action` 表示：

> 某個玩家或系統主動要做什麼。

目前主要玩家 Action：

- `PlayCardAction`
- `AttackAction`
- `HeroSkillAction`
- `EndTurnAction`

Action 數量應該保持少。

不要因為牌的效果不同，就建立：

- `DamageCardAction`
- `BuffCardAction`
- `SummonCardAction`

這些應該都是同一個：

`PlayCardAction`

只是後續產生不同的 Effect。

CLI 的「選 Entity -> 選操作 -> 選 Target」只是輸入介面流程。

最後交給 Engine 的應該是一個完整 Action，例如：

`AttackAction(attacker=Wolf, target=EnemyMinion)`

或：

`PlayCardAction(card=Fireball, target=EnemyHero)`

---

## 3. Effect

`Effect` 表示：

> Action 實際對遊戲世界造成什麼改變。

Action 是意圖，Effect 才是真正修改 Entity state 的東西。

常見 Effect：

- `SummonEffect`
- `DamageEffect`
- `HealEffect`
- `BuffEffect`
- `DrawEffect`
- `DestroyEffect`
- `GainArmorEffect`
- `ModifyManaEffect`
- `ReturnToHandEffect`
- `TransformEffect`

例如：

`PlayCardAction(Fireball)`
-> `DamageEffect(target, 6)`

`PlayCardAction(Wolf)`
-> `SummonEffect(Wolf)`

`AttackAction(A, B)`
-> `DamageEffect(A -> B)`
-> `DamageEffect(B -> A)`

核心原則：

**Action 很少，Effect 很多。**

---

## 4. Event

`Event` 不負責修改 State。

它代表：

> 剛剛真的發生了什麼。

是給 Trigger 系統監聽的通知。

例如：

`DamageEffect`
-> 修改 target.hp
-> 發出 `DamageEvent`

`SummonEffect`
-> Minion 進場
-> 發出 `MinionSummonedEvent`

`DrawEffect`
-> 抽牌成功
-> 發出 `CardDrawnEvent`

所以：

**Effect 改 State。**

**Event 描述剛剛發生的事。**

Event 可能包含：

- source
- target
- owner
- amount
- card
- minion

---

## 5. Trigger

`Trigger` 表示：

> 當某種 Event 發生，而且條件符合時，再產生新的 Effect。

例如：

「每當你召喚一個手下，抽一張牌」

可以表示成：

- listen: `MinionSummonedEvent`
- condition: `event.owner == self.owner`
- effect: `DrawEffect(1)`

流程：

`SummonEffect`
-> `MinionSummonedEvent`
-> Trigger
-> `DrawEffect`
-> `CardDrawnEvent`

Entity 可以攜帶 Trigger。

例如 Minion：

- `OnDeath`
- `OnDamage`
- `OnSummon`
- `OnSpellCast`
- `OnTurnStart`
- `OnTurnEnd`

Entity 本身不需要一直跑 loop。

中央 Engine 收到 Event 後，再去找符合的 Trigger。

---

## 6. 嘲諷 / 戰吼 / 死亡之聲

這三個剛好代表三種不同機制。

### Taunt

嘲諷不是 Trigger。

它比較像：

- status
- rule modifier

主要作用是改變 `AttackAction` 的合法 target。

如果敵方有 Taunt：

攻擊目標只能是 Taunt Minion。

### Battlecry

戰吼是打出卡牌時發生的效果。

例如：

`PlayCardAction`
-> `SummonEffect`
-> Battlecry Effect

第一版甚至可以直接把 Battlecry 當作 Card 的 on-play effects。

之後再泛化成：

`OnPlay Trigger`

### Deathrattle

死亡之聲適合透過 Event + Trigger。

例如：

Minion 死亡
-> `MinionDiedEvent`
-> Deathrattle Trigger
-> 新 Effect

---

## 7. State Check

不是所有東西都一定靠 Event Listener。

有些規則比較適合直接看目前遊戲狀態。

這類叫：

`State-based Check`

例如：

- hp <= 0 -> 死亡
- Hero hp <= 0 -> Game Over
- 手牌超過上限
- 某些暫時狀態過期
- Aura / 全局狀態更新

死亡流程例如：

`DamageEffect`
-> hp 改變
-> `DamageEvent`
-> State Check
-> 發現 hp <= 0
-> 處理死亡
-> `MinionDiedEvent`
-> Deathrattle Trigger

`DamageEvent` 和 `MinionDiedEvent` 應該分開。

受到傷害不一定代表死亡。

---

## 8. Phase

`Phase` 表示：

> 遊戲流程目前進行到哪一段。

Phase 是流程狀態，不是 Entity State。

第一版可以只做：

- `TURN_START`
- `ACTION_PHASE`
- `TURN_END`
- `GAME_OVER`

### TURN_START

系統自動：

- max mana +1
- 補滿 mana
- Draw
- 處理 turn start trigger

### ACTION_PHASE

玩家可以反覆做：

- PlayCard
- Attack
- HeroSkill
- EndTurn

每做一個 Action：

都要先完整跑一次 Resolution Loop。

全部結算完才回到 `ACTION_PHASE`。

### TURN_END

系統：

- 處理 turn end trigger
- 清除 until-end-of-turn 狀態
- 換 current player
- 進入下一個 TURN_START

---

## 9. Engine Resolution Loop

目前最核心的結論：

`Action`
-> `Effect`
-> Engine 執行 Effect
-> Entity State 改變
-> Event
-> Trigger
-> 新 Effect
-> State Check
-> 繼續結算
-> Stable

可以理解成：

1. 收到 Action
2. Validate Action
3. Action 產生 Effects
4. Engine Resolve Effects
5. Effect 修改 Entity State
6. Effect 發出 Events
7. 找符合的 Triggers
8. Trigger 產生新的 Effects
9. 做 State-based Check
10. 如果又產生 Event / Effect / Trigger，繼續
11. 全部穩定後才回到目前 Phase

---

## 10. 整個遊戲其實是一個自動機

從抽象角度：

`State + Input -> New State`

其中 Input 可能來自：

- Player Action
- System Action

整個架構可以看成兩層。

### 外層：Game Flow State Machine

`TURN_START`
-> `ACTION_PHASE`
-> `TURN_END`
-> `TURN_START`

這台狀態機只管：

- 現在哪個 Phase
- 現在輪到誰
- 是否接受玩家輸入

它不需要知道：

- 哪隻怪剩多少血
- 哪張牌有 Taunt
- 手牌內容

那些放在各 Entity 自己的 State。

### 內層：Resolution Loop

`Action`
-> `Effect`
-> `Event`
-> `Trigger`
-> `Effect`
-> ...
-> Stable

所以可以理解成：

> 一個事件驅動的流程自動機，其中一部分 transition 由玩家輸入觸發。

---

## 11. Game / GameContext

不一定需要一個巨大 `GameState` 把全部 State 都塞進去。

比較適合目前設計的是：

`Entity` 自己管理 local state。

例如：

`Hero`
- hp
- armor

`Minion`
- hp
- attack
- status

`Player`
- mana
- hand
- deck
- board

中央 `Game` 或 `GameContext` 只負責：

- current player
- phase
- turn
- event queue
- effect queue
- resolution loop
- entity 之間的關係
- game over

也就是：

**Entity 管自己的 State。**

**Game 管 Entity 之間的規則與流程。**

---

## 12. 第一版建議的核心類別

先不要過度設計。

可以從：

- `Game`
- `Player`
- `Hero`
- `Card`
- `Minion`
- `Board`

加上：

- `Action`
- `Effect`
- `Event`
- `Trigger`
- `Phase`

開始。

概念關係：

`Player`
- Hero
- Hand -> Card[]
- Deck -> Card[]
- Board -> Minion[]

`Game`
- players
- current_player
- phase
- resolution queue

---

## 13. 最後一句總結

目前整個核心可以記成：

**Entity = 世界中的東西**

**Action = 玩家 / 系統想做什麼**

**Effect = 實際改變什麼**

**Event = 剛剛發生了什麼**

**Trigger = 對 Event 的反應**

**State Check = 檢查目前世界狀態是否產生強制結果**

**Phase = 遊戲流程現在進行到哪**

整個引擎：

`Phase Loop`
-> `Action`
-> `Effect`
-> `Event`
-> `Trigger`
-> `State Check`
-> `Stable`
-> 回到 `Phase Loop`

---

## 14. Status 與 Hook 機制

如果 Status 很多，直接在 Engine 裡寫大量：

`if target has TAUNT ...`

`if target has FROZEN ...`

`if target has DIVINE_SHIELD ...`

會讓 Engine 越來越髒。

因此可以讓 Engine 只提供少數固定的 Hook 點，而 Status 自己決定要不要介入。

核心概念：

**Status 是掛在 Entity 身上的物件。**

**Hook 是 Engine 在固定流程節點呼叫 Status 的介面。**

例如：

`Minion`
- hp
- attack
- statuses[]

可能有：

`statuses = [TauntStatus, DivineShieldStatus]`

第一版可以先提供四個 Hook：

- `before_action`
- `after_action`
- `before_effect`
- `after_effect`

整體流程：

`Action`
-> basic validation
-> `before_action` hooks
-> Action 產生 Effects
-> Engine resolve Effect
-> `before_effect` hooks
-> Effect.execute()
-> Entity state 改變
-> `after_effect` hooks
-> Event
-> Trigger
-> State Check
-> `after_action` hooks
-> stable

不同 Status 可以只實作自己有需要的 Hook。

例如：

- `Frozen`：用 `before_action` 阻止 `AttackAction`
- `Taunt`：影響 legal target 計算
- `DivineShield`：用 `before_effect` 攔截 `DamageEffect`
- `Lifesteal`：之後可以用 `after_effect` 根據實際傷害產生 HealEffect

### Divine Shield 範例

假設一隻 Minion：

`Wolf`
- hp = 3
- statuses = `[DivineShieldStatus]`

Engine 執行 Effect 時：

```python
def resolve_effect(effect):
    target = effect.target

    for status in list(target.statuses):
        result = status.before_effect(effect)

        if result.cancel:
            return

    effect.execute()

    for status in list(target.statuses):
        status.after_effect(effect)
```

`DivineShieldStatus`：

```python
class DivineShieldStatus:
    def before_effect(self, effect):
        if isinstance(effect, DamageEffect):
            effect.target.remove_status(self)
            return HookResult(cancel=True)

        return HookResult(cancel=False)
```

`DamageEffect`：

```python
class DamageEffect:
    def __init__(self, source, target, amount):
        self.source = source
        self.target = target
        self.amount = amount

    def execute(self):
        self.target.hp -= self.amount
```

如果：

`DamageEffect(Fireball, Wolf, 6)`

流程：

`Engine.resolve_effect(DamageEffect)`
-> 找到 target = Wolf
-> 跑 Wolf.statuses 的 `before_effect`
-> DivineShieldStatus 發現是 DamageEffect
-> 移除 Divine Shield
-> 回傳 `cancel=True`
-> Engine 不執行 DamageEffect
-> Wolf hp 仍然是 3

下一次再受到傷害時，Divine Shield 已不存在：

`before_effect`
-> 沒有 Status 阻擋
-> `DamageEffect.execute()`
-> Wolf.hp -= damage

這樣 Engine 不需要知道 Divine Shield 的具體規則。

Engine 只需要知道：

`在固定 Hook 點詢問 Entity 身上的 Status 是否要介入。`

因此擴充新的 Status 時，通常只需要新增新的 Status class，而不用一直修改 Engine 主流程。
