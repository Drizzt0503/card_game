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

Event 可以把它理解成一筆「有結構的遊戲 Log」：

- 它描述已經發生的事實
- 它本身不改 Entity State
- Trigger 可以監聽它
- 之後也能拿來做 battle log / replay / debug

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

- type
- source
- target
- owner
- amount
- card
- minion

### Event Check / Trigger Dispatch

第一版不一定需要 `event_queue`。

Effect 執行完成後，可以同步把 Event 交給 Engine：

`emit_event(event)`
-> `process_event(event)`

Engine 做：

1. 收到 Event
2. 找目前有效的 Entity
3. 掃描這些 Entity 的 `triggers[]`
4. 呼叫 `trigger.matches(event)`
5. 符合條件的 Trigger 產生新的 Effect
6. 新 Effect 加進 `effect_queue`

概念：

`Effect`
-> Entity State 改變
-> Event
-> `process_event(event)`
-> Trigger Check
-> 新 Effect
-> `effect_queue`

Trigger 不直接修改 State。

真正改 State 的仍然只能是 Effect。

Event 本身也不執行 Trigger；是 Engine 的 Event Dispatcher 負責：

`Event -> 找 Trigger -> 產生 Effect`

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

不是所有結果都來自某個 Event。

有些規則必須直接檢查「目前整個遊戲世界的狀態」。

這類叫：

`State-based Check`

它和 Trigger 的差別：

- `Trigger`：看到某個 Event 才反應
- `State Check`：直接查看目前 Entity / Zone / Game 的狀態

第一版建議只保留幾個核心 Check。

### Death Check

檢查 Battlefield 上的 Minion：

`hp <= 0`
或
`pending_destroy == True`

符合時進入死亡流程：

`Battlefield -> Graveyard`
-> 發出 `MinionDiedEvent`

接著：

`MinionDiedEvent`
-> Trigger Check
-> Deathrattle
-> 新 Effect

注意：

`DamageEvent` 不等於 `MinionDiedEvent`。

受到傷害後可能仍然活著。

### Game Over Check

檢查 Hero：

`hero.hp <= 0`

符合時：

`phase = GAME_OVER`

並決定勝負結果。

### Aura Check / Derived State Recalculation

Aura 不直接永久修改其他 Entity 的 base state。

例如：

`RaidLeader`
-> Aura：其他友軍 +1 Attack

白板怪：

`base_attack = 3`

實際讀取攻擊力時：

`effective_attack`
=
`base_attack`
+
`modifiers`
+
`current aura modifiers`

Aura source 離場後，不需要對每個受影響 Entity 手動做 `-1`。

重新計算 derived state 後，Aura 自然消失。

### State Check 的執行時機

State Check 應該由 Engine 在固定的 resolution boundary 執行。

簡化版流程：

`Effect`
-> 修改 State
-> Event
-> Trigger Check
-> 新 Effect 入 queue
-> State Check
-> 如果產生新 Event / Effect，繼續 resolve
-> Stable

之後如果要更接近爐石，可以把死亡檢查延後到一組 Effect / Phase 完成後統一處理。

State Check 不要變成所有規則的垃圾桶。

像：

- 手牌滿不滿
- Battlefield 有沒有空位
- Target 合不合法

通常更適合在對應 Effect / Action validation 裡處理。

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


---

## 14. Zone

`Zone` 表示遊戲中的「區域 / 容器」。

它和 `Entity` 不一樣：

- `Entity` = 遊戲世界中的東西
- `Zone` = Entity 所處的位置 / 容器

第一版可以先有：

- `DECK`
- `HAND`
- `BATTLEFIELD`
- `GRAVEYARD`（可晚點做）

例如：

`Wolf Entity`
- 在 `HAND` 時：是一張可打出的手牌
- 移到 `BATTLEFIELD` 後：成為場上的 Minion
- 死亡後：可以進 `GRAVEYARD`

概念上是：

`DECK -> HAND -> BATTLEFIELD -> GRAVEYARD`

而不是一定要：

`Card Entity -> 刪除 -> 建立新的 Minion Entity`

比較接近爐石式的設計是：

> 同一個 Entity 可以在不同 Zone 中，依目前 Zone 啟用不同規則與狀態。

### Zone 不是 Entity

`Zone` 本身主要負責：

- 容納 Entity
- 限制容量
- 維持順序
- 提供區域查詢

例如：

`HandZone`
- cards[]
- max_size

`BattlefieldZone`
- entities[]
- max_slots

因此：

- `Board` 不一定需要做成 Entity
- `Battlefield` 可以直接是一個 Zone

如果之後要有真正的「場地卡 / 地形」，那應該做成一個 Entity 放在 Battlefield，而不是把整個 Battlefield 變成 Entity。

例如：

`PoisonFog Entity`
- zone = BATTLEFIELD
- triggers = [...]
- statuses = [...]

---

## 15. Hero 與 Zone

Hero 概念上屬於場上存在的 Entity，因此可以視為：

`hero.zone = BATTLEFIELD`

但實作上不一定要把 Hero 塞進 `battlefield.entities[]`。

推薦：

`Player`
- hero
- deck_zone
- hand_zone
- battlefield_zone

也就是：

- Hero 概念上在 Battlefield
- Minion 也在 Battlefield
- 但 Hero 可獨立存成 `player.hero`

這樣查詢「所有 Minion」時比較乾淨。

---

## 16. Entity 與 Zone 的關係

目前核心 Entity 可以先有：

- `Hero`
- `Card/Minion Entity`
- `Location`（未來）
- `Weapon`（未來）
- 其他持續存在的 Battlefield Entity

Entity 共同可以有：

- `id`
- `owner`
- `zone`
- `statuses[]`
- `triggers[]`
- `modifiers[]`

不同 Entity 再有自己的 state。

### Hero

- hp
- max_hp
- armor
- hero_skill
- statuses[]
- triggers[]
- modifiers[]

### Card / Minion Entity

同一個 Entity 在不同 Zone 中用途不同。

在 `HAND`：

- 可執行 `PlayCardAction`
- 有 cost
- 有 play effects
- 有 target rule

在 `BATTLEFIELD`：

- 啟用 attack / hp / max_hp
- 可執行 `AttackAction`
- 啟用 statuses[]
- 啟用 triggers[]
- 啟用 modifiers[]

例如：

`Wolf Entity`

在手上：

`zone = HAND`
- cost = 2
- play_effect = Summon / EnterBattlefield

打出後：

`zone = BATTLEFIELD`
- attack = 3
- hp = 2

死亡後：

`zone = GRAVEYARD`

這樣 Entity identity 可以保持不變。

---

## 17. Zone 轉移本身也可以由 Effect 處理

如果採用 Zone 模型，很多原本的 Effect 可以重新理解成 Zone transition。

例如：

### DrawEffect

`DECK -> HAND`

### Play Minion

`HAND -> BATTLEFIELD`

### ReturnToHandEffect

`BATTLEFIELD -> HAND`

### Death

`BATTLEFIELD -> GRAVEYARD`

### DiscardEffect

`HAND -> GRAVEYARD`

因此可以考慮底層有一個通用：

`MoveZoneEffect(entity, from_zone, to_zone)`

但第一版不用強迫所有 Effect 都統一成 MoveZoneEffect。

可以先保留語意明確的：

- `DrawEffect`
- `ReturnToHandEffect`
- `Summon/PlayMinionEffect`

底層再共用 zone move 邏輯。

---

## 18. 更新後的整體核心

目前整套概念可以整理成：

`Entity`
= 遊戲中的東西

`Zone`
= Entity 現在位於哪裡

`Action`
= 玩家 / 系統想做什麼

`Effect`
= 實際改變 Entity / Zone / State

`Event`
= 已經發生的事實

`Trigger`
= 對 Event 的反應

`Status`
= 掛在 Entity 上、可透過 Hook 介入規則

`Modifier`
= 對數值提供持續或暫時修改

`Phase`
= 遊戲流程現在在哪一段

`State Check`
= 根據整體狀態推導強制結果

整體流程：

`Phase`
-> `Action`
-> `Effect`
-> 修改 Entity / Zone
-> `Event`
-> `Trigger`
-> 新 Effect
-> `State Check`
-> Stable
-> 回到 Phase
