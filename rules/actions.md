# Action 規則

目前外部可以要求 Engine 執行以下五種 Action：

| Action | 用途 |
|---|---|
| `PlayCardAction` | 從手牌打出一張牌 |
| `AttackAction` | 手下攻擊 |
| `HeroAttackAction` | 英雄攻擊 |
| `HeroPowerAction` | 使用英雄技能 |
| `EndTurnAction` | 結束回合 |

所有 Action 都只能由目前玩家執行；牌局結束後不能再執行 Action。

## 打出卡牌

`PlayCardAction` 目前以手牌索引指定卡牌，必要時附帶目標。

合法條件：

- 手牌索引存在。
- 卡牌費用不高於目前 Mana。
- 手下牌只能在己方場上少於 7 個手下時打出。
- 卡牌需要目標時，目標必須符合該卡牌的 `TargetRule`。

合法出牌會先移除手牌並扣除 Mana，再執行卡牌效果。

## 手下攻擊

`AttackAction` 目前以己方場上索引指定攻擊者，以 `hero` 或 `minion:<index>` 指定目標。

合法條件：

- 攻擊者存在。
- 攻擊力大於 0。
- 本回合仍可攻擊。
- 目標存在且符合嘲諷限制。

## 英雄攻擊

`HeroAttackAction` 目前以 `hero` 或 `minion:<index>` 指定目標。

合法條件：

- 英雄攻擊力大於 0。
- 本回合尚未攻擊。
- 英雄沒有凍結。
- 目標存在且符合嘲諷限制。

攻擊後會消耗武器耐久；武器耐久耗盡時移除武器。

## 英雄技能

`HeroPowerAction` 使用目前職業的英雄技能，必要時附帶目標。

合法條件：

- 本回合尚未使用英雄技能。
- Mana 至少為技能費用。
- 目標符合英雄技能的目標規則。

目前所有英雄技能費用都是 2 Mana。

## 結束回合

`EndTurnAction` 不需要目標。執行後立即切換到另一位玩家並開始其回合。

## 目前介面限制

這是目前程式使用的 Action 形式，不是最終 Core API 契約。索引與字串目標容易因場面變化而失效；未來應改用穩定的 card/minion instance ID。現在的 Engine 會以 `InvalidAction` 拒絕非法 Action，尚未統一成結構化 `ActionValidation`。
