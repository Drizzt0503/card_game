# 2014 Basic Set 卡牌規劃

## 目標

本專案先以 2014 年《爐石戰記》原始 Basic Set 作為卡牌效果的參考範圍：

- 43 張中立卡
- 9 個職業，每個職業 10 張卡
- 共 133 張可收集卡

這份文件記錄「系統需要支援的效果」，不是要求每張卡都建立一個專用的 Effect 類別。

卡牌應該由多個通用的 Effect、Trigger、Status 和 Target Rule 組合而成。

---

## 一、卡牌類型

第一階段先支援：

- Minion：手下，放到場上，可以攻擊
- Spell：法術，打出後產生效果
- Weapon：武器，裝備到 Hero 上並消耗耐久度

暫時不做：

- Hero Card
- Location

---

## 二、核心 Effect

### 召喚

`SummonEffect`

需要支援：

- 召喚指定手下
- 召喚多個手下
- 召喚 Token
- 召喚隨機手下
- 場上滿時無法召喚

涵蓋的卡牌類型例子：

- 召喚兩個 0/2 嘲諷手下
- 召喚一個 1/1 手下
- 召喚一個 2/1 手下

### 傷害

`DamageEffect`

需要支援：

- 對單一手下造成傷害
- 對敵方 Hero 造成傷害
- 對敵方手下造成傷害
- 對所有敵方手下造成傷害
- 對所有角色造成傷害
- 隨機選擇目標
- 將傷害隨機分配到多個目標

### 治療

`HealEffect`

需要支援：

- 治療單一角色
- 治療所有友方角色
- 將手下恢復至滿血
- 治療 Hero

### 抽牌

`DrawEffect`

需要支援：

- 抽一張牌
- 抽兩張牌
- 抽多張牌
- 符合條件時抽牌，例如擊殺目標後抽牌

### Buff

`BuffEffect`

需要支援：

- 增加攻擊力
- 增加生命值
- 同時增加攻擊力與生命值
- 永久 Buff
- 持續到回合結束的 Buff
- 增加友方角色攻擊力
- 增加 Hero 攻擊力

### 摧毀

`DestroyEffect`

需要支援：

- 摧毀指定敵方手下
- 摧毀受傷手下
- 摧毀武器
- 條件符合時摧毀目標

### 變形

`TransformEffect`

需要支援：

- 將手下變成指定 Token
- 將手下變成另一個手下
- 清除原本手下的狀態與效果

### 返回手牌

`ReturnToHandEffect`

需要支援：

- 將敵方手下返回對手手牌
- 將自己的手下返回自己手牌
- 定義返回手牌後是否保留暫時 Buff

### 丟棄手牌

`DiscardEffect`

需要支援：

- 隨機丟棄一張手牌
- 丟棄指定手牌
- 丟牌後產生其他效果

### Mana 調整

`ModifyManaEffect`

需要支援：

- 增加本回合可用 Mana
- 增加最大 Mana 水晶
- 消耗下回合可用 Mana
- 改變卡牌費用

### 裝備武器

`EquipWeaponEffect`

需要支援：

- 裝備武器
- 替換目前武器
- 設定武器攻擊力
- 設定武器耐久度

### 狀態效果

`GiveStatusEffect`

`RemoveStatusEffect`

用來加入或移除：

- Taunt
- Charge
- Divine Shield
- Windfury
- Freeze
- Spell Damage
- Overload
- Damaged

### 選擇與隨機

`ChooseEffect`

需要支援玩家從多個效果中選一個。

`RandomEffect`

需要支援：

- 隨機選擇一個目標
- 隨機選擇一張牌
- 隨機召喚手下
- 隨機分配傷害

### 牌庫選擇

`DiscoverFromDeckEffect`

需要支援：

- 查看牌庫頂端數張牌
- 玩家選擇其中一張加入手牌
- 其他牌依規則放回牌庫或丟棄

---

## 三、需要的 Trigger

### Battlecry

`BattlecryTrigger`

手下打出並完成召喚後觸發。

可以產生：

- 傷害
- 治療
- 抽牌
- 召喚
- Buff
- 摧毀武器

### Deathrattle

`DeathrattleTrigger`

手下死亡並離開場上後觸發。

### On Summon

`OnSummonTrigger`

每當指定玩家或任一玩家召喚手下時觸發。

### On Damage

`OnDamageTrigger`

角色受到傷害時觸發。

### On Turn Start

`OnTurnStartTrigger`

回合開始時觸發。

### On Turn End

`OnTurnEndTrigger`

回合結束時觸發。

### On Spell Cast

`OnSpellCastTrigger`

法術成功打出後觸發。

### Aura

`AuraTrigger`

持續存在於場上，並影響其他角色的衍生狀態。

Aura 來源離場後，效果應該自然消失，不應永久修改目標的基礎數值。

---

## 四、需要的 Status / Keyword

### Taunt

有嘲諷手下存在時，敵方攻擊目標受到限制。

### Charge

手下召喚當回合可以攻擊。

### Divine Shield

抵消下一次受到的傷害，之後移除聖盾。

### Windfury

一個回合可以攻擊兩次。

### Freeze

目標下一次不能攻擊。

### Spell Damage

增加法術造成的傷害。

### Overload

鎖住下一回合部分 Mana 水晶。

### Combo

本回合先打出其他牌後，啟用額外效果。

### Damaged

用來判斷角色目前是否曾受傷且尚未滿血。

---

## 五、Target Rule

效果需要能指定以下目標範圍：

- 自己
- 自己的 Hero
- 自己的手下
- 敵方 Hero
- 敵方手下
- 任意角色
- 所有友方手下
- 所有敵方手下
- 所有角色
- 隨機敵方角色
- 隨機敵方手下
- 受傷的敵方手下

---

## 六、需要的特殊規則

- 場上最多 7 個手下
- 手牌上限
- 牌庫抽空後的疲勞傷害
- 武器攻擊與耐久度消耗
- 手下死亡檢查
- 多個手下同時死亡時的結算順序
- 隨機目標的可重現 Seed
- 卡牌打出前的合法目標檢查
- 法術傷害加成
- 手下召喚當回合是否可以攻擊
- 臨時 Buff 的回合結束清除

---

## 七、建議實作順序

1. `DamageEffect`
2. `HealEffect`
3. `DrawEffect`
4. `BuffEffect`
5. `DestroyEffect`
6. `GiveStatusEffect`
7. `BattlecryTrigger`
8. `DeathrattleTrigger`
9. `TransformEffect`
10. `ReturnToHandEffect`
11. `Weapon` 與 `EquipWeaponEffect`
12. `ChooseEffect` 與牌庫選擇
13. Aura 與複雜條件 Trigger

英雄系統會另外規劃，不在這份卡牌效果清單中展開。
