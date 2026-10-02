# CLI UI

## 入口與流程

`src/cli/main.py` 是 CLI 主流程：

1. 清除畫面。
2. Player 1 選職業。
3. 選擇 Player 2 由真人或 AI 控制。
4. 若是 AI，隨機選擇 Player 2 職業。
5. 建立牌局並顯示公開 Log。
6. 真人回合顯示畫面並讀取 Action。
7. AI 回合在背景執行，Log 延後到真人回合顯示。

## Renderer

`src/cli/renderer.py` 的 `render(state)` 負責顯示目前玩家視角：

- 回合、目前玩家與職業。
- 自己的 Hero、護甲、攻擊力、武器、狀態。
- 對手的 Hero、護甲、攻擊力、武器、狀態、手牌數、牌庫數。
- 自己的完整手牌與中文卡牌描述。
- 雙方場上的手下、攻擊力、生命值、可攻擊狀態與狀態。
- Action 提示。

對手的手牌只顯示數量，不顯示卡牌內容，避免真人玩家看到不應知道的資訊。

## Input Handler

`src/cli/input_handler.py` 將文字輸入轉成 Action：

- 職業使用數字選擇。
- 手牌使用數字索引。
- 手下攻擊與 Hero 攻擊使用 `0` 代表敵方 Hero，`1` 以上代表敵方手下。
- 卡牌與英雄技能的目標使用 `TargetRef`，不直接把 UI 編號傳給 Engine。

## 資訊邊界

CLI 的 render 是給真人閱讀的 presentation layer，不是遊戲規則來源。Engine 才能決定 Action 是否合法；CLI 只負責輸入與顯示錯誤。

目前雙真人模式在結束回合時提示交換畫面，避免下一位玩家看到前一位的手牌。

## Windows

Linux 開發環境可以透過 GitHub Actions 的 Windows runner 打包。設定位於 `.github/workflows/build-windows.yml`，產物名稱是 `card_game-windows`，下載後包含 `card_game.exe`。
