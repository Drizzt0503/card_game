# 卡牌規則與資料

卡牌本身是靜態 Data，不是牌局中的 GameState，也不是 RL observation。牌局只需要保存卡牌的 `card_id` 與卡牌 instance 的動態狀態；卡名、描述、費用、類型與效果資料由卡牌資料查詢。

## 目前卡牌資料

目前 registry 有 134 個定義：

| 類型 | 數量 |
|---|---:|
| 可收集卡 | 133 |
| 不可收集卡（幸運幣） | 1 |
| 手下 | 57 |
| 法術 | 73 |
| 武器 | 4 |
| 有效果定義的卡 | 94 |

完整卡牌名稱、ID、職業與描述請見 [docs/cards-and-effects.md](../docs/cards-and-effects.md)。實際靜態欄位以 `src/cards/card_registry.py` 為準，Token 以 `src/cards/tokens.py` 為準。

## 卡牌資料欄位

目前卡牌可包含：

- `card_id`、名稱、費用、攻擊力、生命值。
- 卡牌類型、職業、稀有度、是否可收集、種族。
- 中文/英文卡面描述。
- `target_rule`。
- 初始狀態、Spell Power。
- `effect_id`、`aura_ids`、`trigger_ids`、`attack_trigger_ids`。

## 卡牌行為

- 手下牌會召喚手下，再執行其戰吼或其他出牌效果。
- 法術牌會支付費用並執行效果。
- 武器牌會裝備到英雄，提供英雄攻擊力與耐久度。
- Token 是效果產生的卡牌/手下，不進入隨機牌組池。
- 卡牌效果可以產生新的 Effect、Event、Trigger 或 Aura 變化。

## 目前已知的資料與規則邊界

卡面文字是給人閱讀的規則說明；Engine 目前透過 `effect_id` 與 builder 執行對應行為。長期應讓卡牌資料與規則文件成為可查詢的 Rule/Data 來源，避免卡牌規則只存在於 Engine 的分支程式中。
