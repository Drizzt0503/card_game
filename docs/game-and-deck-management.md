# 牌局與牌組管理

## 新建牌局

入口是 `src/session/game_session.py` 的 `new_game()`。

流程：

1. 建立隨機數產生器。
2. 依兩位玩家的職業建立牌組。
3. 建立兩個 `PlayerState` 與 Hero。
4. 建立 `GameState` 與 `GameEngine`。
5. 隨機決定先手。
6. Engine 抽起手牌並開始先手回合。
7. 將幸運幣加入後手手牌。

## GameState

`GameState` 保存：

- 兩位玩家。
- 目前玩家 id。
- 回合數與 phase。
- 勝利者。
- 全域 Trigger。

`state.current_player` 與 `state.opponent` 是 Engine、AI、CLI 取得目前視角的主要入口。

## PlayerState

每位玩家保存：

- Hero。
- Deck。
- Hand。
- 場上手下。
- 職業。
- 當前 Mana 與最大 Mana。

## 牌組

`Deck` 目前提供：

- 保存 `CardInstance`。
- 使用指定 RNG 洗牌。
- 從牌庫頂端抽牌。

`build_random_deck()` 只選擇：

```text
definition.collectible == True
and definition.card_class in ("NEUTRAL", player_class)
```

非傳說卡最多兩張；傳說卡最多一張。牌組產生器會一直抽到 30 張，並使用同一個 RNG 讓測試可以透過 seed 重現。

## 手牌

`Hand` 目前是 `CardInstance` 的列表，支援加入、依索引移除與取得數量。CLI 使用手牌索引建立 `PlayCardAction`。

目前最大手牌規則常數是 10，但抽牌時尚未實作滿手牌燃燒/拒絕規則。

## 先後手與幸運幣

- 先手起手 3 張。
- 後手起手 4 張。
- 後手額外拿到不可收集的 `the_coin`。
- 幸運幣是法術，打出後本回合獲得 1 Mana，不會進入隨機牌組池。

## 目前尚未分離的責任

目前 `session` 同時負責建構遊戲與開局規則。未來若支援牌組編輯、重播、配對或 RL episode，建議拆出：

- `DeckBuilder`：驗證與建立牌組。
- `GameFactory`：建立乾淨的 GameState。
- `MatchSession`：管理一場遊戲的流程與參與者。
