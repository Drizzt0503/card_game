# 關鍵字與狀態

本文件記錄目前程式使用的狀態 ID 與其實際效果。

## 戰鬥狀態

- `taunt`：敵方有嘲諷手下時，攻擊必須指定嘲諷手下。
- `frozen`：角色不能攻擊。回合開始時解除；被凍結的角色解除後該回合仍不能攻擊。
- `windfury`：手下每回合可攻擊兩次。
- `charge`：卡牌或 Token 的初始狀態資料；目前可攻擊流程主要由 `can_attack` 與 `attacks_remaining` 控制。
- `divine_shield`：作為卡牌/手下狀態資料保留；目前效果解析需以實際效果實作為準，並非所有狀態都已完成完整戰鬥整合。

## 數值與衍生狀態

- `armor`：英雄的額外防禦值，受到傷害時優先消耗。
- `spell_power`：由手下或卡牌資料提供的法術強度欄位。
- Aura：依目前場面重新計算攻擊力或生命值，例如其他手下、Beast、Murloc 或相鄰手下的加成。
- `buff_attack`、`buff_health`：手下的持續加成資料。
- `temporary_attack`：英雄本回合臨時增加的攻擊力，回合結束時清除。

## 卡牌分類

- `MINION`：打出後進入場上。
- `SPELL`：支付費用後執行效果。
- `WEAPON`：裝備在英雄上並提供攻擊力與耐久度。
- `Beast`、`Murloc`、`Mech` 等為種族資料，可被卡牌效果、Aura 或 Trigger 使用。

## 事件反應

目前已實作的 Trigger 包含：

- 友方 Beast 被召喚時抽牌。
- 友方手下被治療時抽牌。

狀態、Aura 與 Trigger 的完整支援程度仍以 `src/auras/`、`src/triggers/` 與 `src/effects/` 的實作為準。
