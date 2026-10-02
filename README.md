# Card Game MVP

目前版本是單機雙人 CLI 原型：兩名玩家先選擇職業，再輪流使用各自的 30 張預設牌組對戰；Player 2 也可以交由基礎 Rule-based AI 控制。

## 執行

在專案根目錄執行：

```bash
python -m src.cli.main
```

## 目前規則

- 每副牌 30 張，由中立卡與所選職業卡隨機組成。
- 目前 registry 有 134 個卡牌定義，其中 133 張可收集卡、1 張不可收集的幸運幣。
- 支援手下、法術、武器、英雄技能、Token、嘲諷、聖盾、凍結、Aura 與部分 Trigger。
- Hero 初始 30 HP。
- 每回合增加 1 Mana，最多 10 Mana。
- 每回合開始抽 1 張牌。
- 場上最多 7 個手下，手牌最多的規則尚未實作。
- 手下出場當回合不能攻擊。
- 手下可以攻擊敵方 Hero 或敵方手下。
- Hero HP 歸零時遊戲結束。
- 非傳說牌最多放 2 張；傳說牌最多放 1 張。
- 開始遊戲時可以選擇 Player 2 由真人或基本 Rule-based AI 控制；AI 職業會隨機選擇。
- AI 回合會在背景執行，AI 的公開行動 Log 會在下一個玩家回合顯示。
- 先手起手 3 張，後手起手 4 張並獲得 1 張幸運幣。

攻擊時，目標輸入 `0` 代表敵方 Hero；輸入 `1` 以上代表敵方場上手下的編號。

目前尚未包含完整的手牌上限處理、疲勞傷害、牌組編輯器與 RL environment。

## 架構文件

詳細模組說明請看 [AGENTS.md](AGENTS.md) 與 [`docs/`](docs/)。
## Windows executable

在 Windows 環境中雙擊 `build_windows.bat`，或在命令列執行：

```bat
build_windows.bat
```

完成後執行：

```text
dist\card_game.exe
```

目標電腦不需要另外安裝 Python。打包需要在 Windows 環境執行，且建議使用與開發環境相同的 Python 版本。
