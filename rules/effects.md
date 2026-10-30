# 效果、Trigger、Aura 與穩定流程

## Effect

卡牌、英雄技能與戰鬥會被轉成可組合的 Effect。現有 Effect 涵蓋：

- 傷害、治療、抽牌、護甲。
- 召喚、摧毀、變形、回手、偷取與複製。
- Buff、設定攻擊力/生命值、凍結與賦予狀態。
- 裝備、修改與摧毀武器。
- 全體角色/手下效果、隨機目標與隨機選擇。
- Mana、棄牌與死亡後抽牌。

Effect 不直接由 CLI 執行，而是交給 `EffectResolver`。

## Resolver 的目前流程

目前 `EffectResolver` 會：

1. 依序取出待執行的 Effect。
2. 執行 Effect 並取得 Event。
3. 依 Event 加入後續 Trigger Effect。
4. 清理死亡手下並產生死亡 Event。
5. 繼續處理新加入的 Effect，直到佇列清空。

這使一次 Action 造成的連鎖效果能在回傳前完成。Engine 目前還會在 Resolver 完成後重新計算 Aura 並檢查勝負。

## Aura

Aura 不是一次性傷害或治療，而是依場面重新計算的衍生數值。目前包含：

- 其他手下 +1/+1。
- 其他手下 +1 攻擊力。
- 其他 Murloc +1 攻擊力。
- 其他 Beast +1 攻擊力。
- 相鄰手下 +2 攻擊力。
- 其他手下 +1 生命值。

## Event

Event 是已發生的遊戲事實，用於 Trigger 與日誌；它不是玩家 Action，也不負責 RL reward 或 observation。現有 Event 包含事件類型、來源/目標、數值、卡牌 ID 與額外資料。

## 穩定狀態

目前一個 Action 的效果解析會持續到 Effect 佇列與由事件產生的後續 Effect 都完成，再由 Engine 做死亡清理、Aura 重算與勝負檢查。未來 Core API 應把這個「回傳前必須完成到穩定狀態」列為正式契約。
