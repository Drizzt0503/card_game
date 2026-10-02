# 底層引擎

## 主要入口

`src/engine/game_engine.py` 的 `GameEngine` 是目前牌局規則的主要入口。

### `start(state)`

1. 依先後手抽起手牌。
2. 先手 3 張，後手 4 張。
3. 由 `session` 額外加入後手的幸運幣。
4. 開始先手回合，增加 Mana、抽回合牌並重置可行動狀態。

### `apply_action(state, action)`

目前支援：

- `PlayCardAction`
- `AttackAction`
- `HeroAttackAction`
- `HeroPowerAction`
- `EndTurnAction`

Engine 會先驗證 Action，再執行效果，最後統一：

1. 移除死亡手下。
2. 重算 Aura。
3. 檢查 Hero 是否死亡。
4. 回傳公開 Log。

## 效果解析

`EffectResolver` 使用 queue 依序處理 Effect。每個 Effect 可以：

- 修改 `GameState`。
- 產生 `Event`。
- 讓 `TriggerEngine` 產生更多後續 Effect。
- 觸發死亡檢查與 `minion_died` 事件。

因此一張帶戰吼的手下牌不是在 Engine 裡硬編流程，而是組成：

```text
SummonEffect -> Battlecry effects -> Events -> Trigger effects
```

## 回合流程

- 回合結束時清除 Hero 的臨時攻擊力。
- 切換目前玩家並增加回合數。
- 新回合增加 Mana、補滿 Mana、重置英雄技能與攻擊狀態。
- 凍結中的角色解除凍結，但該回合仍不能攻擊。
- 抽一張牌。
- 手下依照 Charge、Windfury 等狀態設定可攻擊次數。

## 戰鬥規則

- 攻擊力為 0 的手下不能攻擊。
- 同一回合不能重複攻擊，Windfury 可攻擊兩次。
- 有嘲諷手下時，Hero 和手下只能攻擊嘲諷目標。
- 手下互相攻擊會互相造成傷害。
- Hero 攻擊手下時，Hero 會承受手下的攻擊力傷害。
- 武器攻擊後消耗 1 點耐久，耐久歸零時移除武器。
- 聖盾第一次受到傷害時只移除聖盾，不扣生命。

## 規則常數

位於 `src/engine/rules.py`：

| 常數 | 目前值 |
|---|---:|
| 最大手牌 | 10（目前尚未強制） |
| 最大場上手下 | 7 |
| 最大 Mana | 10 |
| 先手起手基準 | 3 |
| 牌組張數 | 30 |
| 普通卡最大張數 | 2 |

## 尚待補強

- fatigue 與牌庫抽空規則。
- 手牌滿時的抽牌處理。
- 更完整的 combat event，例如攻擊前、攻擊中、攻擊後。
- 將部分 `card_effects.py` 的特例分解成可註冊的 Effect Builder。
- 把 Engine 的公開事件與 UI Log 分開。
