# Rules

這個資料夾記錄目前遊戲實際包含的規則。規則文件以目前程式行為為準，不是未來 Core API 或 RL 的理想規格。

## 文件

- [global.md](global.md)：牌局、牌組、回合、Mana、場地與勝負。
- [actions.md](actions.md)：目前可以送進 Engine 的 Action 與合法條件。
- [heroes.md](heroes.md)：英雄技能。
- [keywords.md](keywords.md)：目前使用的狀態、關鍵字與衍生效果。
- [effects.md](effects.md)：Effect、Trigger、Aura 與 Resolver 的目前行為。
- [cards.md](cards.md)：卡牌資料與卡牌規則的來源。

## 規則來源

目前規則仍分散在程式中：

| 規則類型 | 目前來源 |
|---|---|
| 全域常數 | `src/engine/rules.py` |
| Action 驗證與回合流程 | `src/engine/game_engine.py` |
| 卡牌靜態資料 | `src/cards/card_registry.py`、`src/cards/tokens.py` |
| 卡牌效果 | `src/cards/card_effects.py`、`src/effects/` |
| 英雄技能 | `src/heroes/hero_powers.py` |
| 目標條件 | `src/targeting/target.py` |
| Aura | `src/auras/aura.py` |
| Trigger | `src/triggers/trigger.py` |

因此本資料夾是目前規則的整理與對照文件；若文件和程式不一致，必須先標記差異，不把未實作內容寫成既有規則。

## 明確尚未實作

- 手牌上限雖定義為 10，但目前沒有完整執行手牌上限規則。
- 疲勞傷害尚未實作。
- Core 尚未提供正式的 `get_legal_actions()` 與 `validate_action()` 對外介面。
- 目前 Action 使用手牌/場上索引與字串目標；穩定的 instance ID Action 契約仍是後續工作。
