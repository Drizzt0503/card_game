# 建議的後續分層

目前已足夠支援第一版 CLI 對戰，但為了 RL、重播與更多卡牌，建議後續增加以下模組。

## 1. Observation layer

```text
GameState -> ObservationBuilder(player_id) -> Observation
```

統一處理資訊遮罩：自己的手牌內容可見，對手手牌只提供數量與必要統計。這層應同時給 CLI、Rule-based AI 與 RL 使用，但 CLI renderer 不應直接扮演這個角色。

## 2. Action validation / Action space

現在 Engine 內有部分合法性檢查，未來可以提供 `legal_actions(state, player_id)` 與 action mask，讓 CLI 能列出合法選項，也讓 RL 不必大量嘗試非法 Action。

## 3. Card content data layer

當卡牌數量增加後，可將卡牌靜態資料移到 JSON/YAML 或獨立資料模組；Python registry 保留建構與驗證。效果仍應以可測試的 Effect class 組成。

## 4. Event log / Replay

目前 Engine 回傳人類可讀 Log。建議改成保存結構化 Event，再由 CLI formatter 轉中文，這樣可以支援 replay、測試斷言與訓練資料收集。

## 5. Match/session service

未來把牌局建構、玩家連線、回合流程與保存/載入分開，避免 `session` 同時承擔太多責任。
