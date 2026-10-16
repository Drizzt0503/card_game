# Card Game 專案導覽

這是一個以 Python 實作的爐石風格卡牌遊戲原型。現在的目標是先維持一個可以由兩位玩家透過 CLI 完整遊玩的版本，再逐步把核心狀態整理成適合 Rule-based AI 與 RL 使用的環境。

## 執行方式

```bash
python -m src.cli.main
```

Windows 執行檔由 GitHub Actions 建立，流程設定在 `.github/workflows/build-windows.yml`。

## 模組責任

| 模組 | 責任 |
|---|---|
| `src/domain/` | 遊戲資料模型：卡牌、牌組、手牌、Hero、手下、武器、玩家狀態與牌局狀態。 |
| `src/actions/` | 玩家或 AI 提出的意圖，例如出牌、攻擊、英雄攻擊、英雄技能、結束回合。 |
| `src/engine/` | 驗證 Action、推進回合、呼叫效果解析、處理死亡、勝負與全域規則。 |
| `src/effects/` | 可組合的遊戲效果，例如傷害、治療、抽牌、召喚、武器、凍結與隨機選擇。 |
| `src/events/` | Effect 產生的遊戲事實，供 Trigger 反應。 |
| `src/triggers/` | 監聽事件並產生後續 Effect，例如野獸召喚抽牌、治療手下抽牌。 |
| `src/auras/` | 根據場面重新計算衍生數值，例如其他手下 +1 攻擊。 |
| `src/targeting/` | 以 `TargetRule` 和 `TargetRef` 統一處理合法目標。 |
| `src/cards/` | 卡牌註冊表、卡牌效果組裝、Token 與隨機牌組產生。 |
| `src/heroes/` | 九個職業的英雄技能定義與效果組裝。 |
| `src/session/` | 建立一場新遊戲，選擇職業、建立牌組、決定先後手與給後手幸運幣。 |
| `src/ai_agent/` | AI 介面與目前的 Rule-based AI；未來可在同一介面接 RL Agent。 |
| `src/cli/` | CLI 輸入、畫面渲染、真人/AI 回合流程與公開 Log。 |

## 核心資料流

```text
CLI / AI
  -> Action
  -> GameEngine.apply_action
  -> build effects
  -> EffectResolver
  -> Effect.apply
  -> Event
  -> Trigger effects
  -> remove dead minions / recalculate auras
  -> render next observation
```

## 目前規則重點

- 每副牌 30 張。
- 非傳說卡最多 2 張；傳說卡預留最多 1 張的規則。
- 先手起手 3 張，後手起手 4 張並取得 1 張幸運幣。
- 回合開始增加 1 點 Mana，最多 10 點，並抽 1 張牌。
- 場上最多 7 個手下。
- 目前尚未實作手牌上限、疲勞傷害與完整卡牌規則。

## RL 邊界

目前 `AIAgent.choose_action` 接收完整 `GameState`，這是為了先快速完成 Rule-based AI。正式 RL 版本應新增 `ObservationBuilder`，將完整狀態轉成玩家可見的 observation，再由 Agent 回傳標準化 `Action`。CLI 的 renderer 不應直接成為 RL observation。

## 詳細文件

- [底層引擎](docs/engine.md)
- [卡牌與效果](docs/cards-and-effects.md)
- [牌局與牌組管理](docs/game-and-deck-management.md)
- [AI Agent](docs/ai.md)
- [CLI UI](docs/cli-ui.md)
- [建議的後續分層](docs/future-architecture.md)
