# Data

這個資料夾保存目前遊戲的靜態卡牌資料。資料欄位依照 [rules/cards.md](../rules/cards.md) 定義，並對應 `CardDefinition`。

## 檔案

- [cards.json](cards.json)：目前卡牌登錄表，包含可收集卡與不可收集的幸運幣。
- [tokens.json](tokens.json)：效果或英雄技能產生的 Token。

## 資料與規則的界線

Data 只保存卡牌的靜態描述：

- `card_id`、名稱、費用、攻擊力、生命值。
- 卡牌類型、職業、稀有度、是否可收集、種族。
- 中文/英文卡面文字。
- 目標規則代號。
- 初始狀態、Spell Power、Aura/Trigger/Effect 的引用 ID。

Data 不保存：

- 某一場遊戲中的 instance ID。
- 手牌、牌庫、場面或目前生命值。
- 本回合是否可攻擊。
- RL observation、action mask 或 reward。
- Effect 的執行程式。

`effect_id`、`aura_ids` 與 `trigger_ids` 是規則/執行邏輯的引用，不是把執行邏輯直接塞進資料。卡牌實際行為目前仍由 `src/cards/`、`src/effects/`、`src/auras/` 與 `src/triggers/` 實作。

## 來源與同步

這兩個 JSON 是目前程式卡牌登錄的資料快照：

- 主要卡牌來源：`src/cards/card_registry.py`
- Token 來源：`src/cards/tokens.py`

新增或修改卡牌時，應同步更新來源程式與這裡的資料快照，直到 Data 正式成為唯一載入來源。

