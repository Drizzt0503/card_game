# 卡牌與效果

## 卡牌資料來源

主要來源是：

- `src/cards/card_registry.py`：可收集卡牌與幸運幣。
- `src/cards/tokens.py`：不可放入牌組的 Token。
- `src/domain/card.py`：`CardDefinition` 與 `CardInstance`。

`CardDefinition` 保存卡牌的靜態資料；`CardInstance` 代表牌局中一張有獨立 instance id 的卡。

## 目前數量

目前 registry 共有 134 個定義：

| 分類 | 數量 |
|---|---:|
| 可放入牌組 | 133 |
| 不可收集幸運幣 | 1 |
| 中立卡定義（含幸運幣） | 44 |
| 每個職業卡 | 10 |
| 手下 | 57 |
| 法術 | 73 |
| 武器 | 4 |
| 有 `effect_id` 的卡 | 94 |

九個職業為：Druid、Hunter、Mage、Paladin、Priest、Rogue、Shaman、Warlock、Warrior。牌組從「中立卡 + 自己職業卡」中隨機產生 30 張。

目前有 Beast 與 Murloc 種族；Token 另外包含 Mech 等種族資料。

## 卡牌欄位

卡牌可以描述：

- 基本資料：id、名稱、費用、攻擊力、生命值、卡牌類型。
- 分類資料：職業、稀有度、是否可收集、種族。
- 顯示文字：中文與英文描述。
- 目標規則：`TargetRule`。
- 初始狀態：Charge、Taunt 等。
- 關聯行為：`effect_id`、`aura_ids`、`trigger_ids`、`attack_trigger_ids`。
- Spell Power。

CLI 只顯示 `description_zh`；英文描述保留給未來資料檢查、API 或其他 UI 使用。

## 目前實作的效果類型

`src/effects/effect.py` 已有以下可組合效果：

- 召喚、傷害、抽牌、治療、獲得護甲。
- 臨時攻擊力、裝備武器、修改武器、摧毀武器。
- 全體角色/手下傷害與治療。
- 賦予 Charge、設定攻擊力、設定生命值、生命值倍率。
- 偷取手下、複製手牌、回手、全體回手、變形。
- 棄牌、隨機敵人傷害、隨機選擇、凍結。
- 修改 Mana、摧毀目標、死亡後抽牌。

效果由 `EffectResolver` 依序解析，不直接由 CLI 修改遊戲狀態。

## 戰吼、Aura、Trigger

手下出牌會先建立 `SummonEffect`，再組合該卡的 battlecry effect。這讓「打出手下」與「召喚 Token」可以共用同一個召喚流程。

Aura 位於 `src/auras/aura.py`，目前支援：

- 其他手下攻擊力或生命值加成。
- 其他 Beast/Murloc 的攻擊力加成。
- 相鄰手下攻擊力加成。
- 給 Beast 或小型手下 Charge。

Trigger 位於 `src/triggers/trigger.py`，目前支援：

- 友方 Beast 被召喚時抽牌。
- 友方手下被治療時抽牌。

## 職業技能與 Token

九個英雄技能都在 `src/heroes/hero_powers.py`：

| 職業 | 技能 | 效果 |
|---|---|---|
| Druid | Shapeshift | +1 攻擊力、+1 護甲 |
| Hunter | Steady Shot | 對敵方 Hero 造成 2 傷害 |
| Mage | Fireblast | 對任意角色造成 1 傷害 |
| Paladin | Reinforce | 召喚 1/1 Silver Hand Recruit |
| Priest | Lesser Heal | 恢復任意友方角色 2 生命 |
| Rogue | Dagger Mastery | 裝備 1/2 匕首 |
| Shaman | Totemic Call | 隨機召喚四種圖騰之一 |
| Warlock | Life Tap | 抽牌並讓自己 Hero 受到 2 傷害 |
| Warrior | Armor Up! | 獲得 2 護甲 |

Token 定義在 `src/cards/tokens.py`，包括圖騰、Silver Hand Recruit、Mirror Image、Boar、Animal Companion 與 Sheep 等。

## 新增卡牌的流程

1. 在 `card_registry.py` 加入 `CardDefinition`。
2. 需要目標時設定 `target_rule`。
3. 需要行為時設定 `effect_id`。
4. 將可組合邏輯放入 Effect；必要時在 `card_effects.py` 建立 builder。
5. 需要反應事件時新增 `trigger_ids` 與 Trigger。
6. 需要持續衍生數值時新增 `aura_ids` 與 Aura 規則。
7. 補中文/英文描述與測試。

## 目前可收集卡牌清單

完整數值與效果以 `src/cards/card_registry.py` 為準；以下是目前 registry 的名稱與 id 索引。

### NEUTRAL（43 張）

酸性沼澤軟泥怪 (`acidic_swamp_ooze`)、大法師 (`archmage`)、血沼迅猛龍 (`bloodfen_raptor`)、藍鰓戰士 (`bluegill_warrior`)、石拳巨魔 (`boulderfist_ogre`)、冰風雪人 (`chillwind_yeti`)、熔核犬 (`core_hound`)、達拉然法師 (`dalaran_mage`)、暗鱗治療者 (`darkscale_healer`)、機械幼龍技師 (`dragonling_mechanic`)、精靈弓箭手 (`elven_archer`)、藏寶海灣保鏢 (`booty_bay_bodyguard`)、霜狼步兵 (`frostwolf_grunt`)、霜狼督軍 (`frostwolf_warlord`)、侏儒發明家 (`gnomish_inventor`)、閃金鎮步兵 (`goldshire_footman`)、魚人招潮者 (`grimscale_oracle`)、古拉巴什狂暴者 (`gurubashi_berserker`)、鐵爐堡火槍手 (`ironforge_rifleman`)、鐵皮灰熊 (`ironfur_grizzly`)、狗頭人地卜師 (`kobold_geomancer`)、競技場之王 (`lord_of_the_arena`)、熔岩暴怒者 (`magma_rager`)、魚人斥候 (`murloc_raider`)、魚人海潮術士 (`murloc_tidehunter`)、夜刃刺客 (`nightblade`)、見習工程師 (`novice_engineer`)、綠洲鉗嘴龜 (`oasis_snapjaw`)、食人魔法師 (`ogre_magi`)、團隊隊長 (`raid_leader`)、剃刀沼澤獵人 (`razorfen_hunter`)、魯莽火箭手 (`reckless_rocketeer`)、闊步鱷魚 (`river_crocolisk`)、森金御盾大師 (`senjin_shieldmasta`)、破碎之日教士 (`shattered_sun_cleric`)、銀背族長 (`silverback_patriarch`)、石牙野豬 (`stonetusk_boar`)、霜狼步兵隊長 (`stormpike_commando`)、暴風城勇士 (`stormwind_champion`)、暴風城騎士 (`stormwind_knight`)、巫醫 (`voodoo_doctor`)、戰爭魔像 (`war_golem`)、狼騎兵 (`wolfrider`)

### 職業卡（各 10 張）

- **DRUID**：啟動 (`innervate`)、野性成長 (`wild_growth`)、治療之觸 (`healing_touch`)、爪擊 (`claw`)、月火術 (`moonfire`)、野性印記 (`mark_of_the_wild`)、野蠻咆哮 (`savage_roar`)、揮擊 (`swipe`)、星火術 (`starfire`)、鐵木樹皮守護者 (`ironbark_protector`)
- **HUNTER**：秘法射擊 (`arcane_shot`)、獵人印記 (`hunters_mark`)、追蹤 (`tracking`)、動物夥伴 (`animal_companion`)、森林狼 (`timber_wolf`)、餓狼 (`starving_buzzard`)、多重射擊 (`multi_shot`)、馴犬者 (`houndmaster`)、苔原犀牛 (`tundra_rhino`)、殺戮命令 (`kill_command`)
- **MAGE**：秘法智力 (`arcane_intellect`)、火球術 (`fireball`)、冰霜箭 (`frostbolt`)、鏡像 (`mirror_image`)、秘法飛彈 (`arcane_missiles`)、秘法爆炸 (`arcane_explosion`)、冰霜新星 (`frost_nova`)、變形術 (`polymorph`)、烈焰風暴 (`flamestrike`)、水元素 (`water_elemental`)
- **PALADIN**：力量祝福 (`blessing_of_might`)、聖光術 (`holy_light`)、奉獻 (`consecration`)、憤怒之錘 (`hammer_of_wrath`)、保護之手 (`hand_of_protection`)、王者祝福 (`blessing_of_kings`)、謙恭 (`humility`)、守護者之王 (`guardian_of_kings`)、光之正義 (`lights_justice`)、真銀勇士 (`truesilver_champion`)
- **PRIEST**：神聖懲擊 (`holy_smite`)、真言術：盾 (`power_word_shield`)、暗言術：痛 (`shadow_word_pain`)、神聖新星 (`holy_nova`)、神聖之靈 (`divine_spirit`)、暗言術：死 (`shadow_word_death`)、神聖之火 (`holy_fire`)、心靈控制 (`mind_control`)、心靈視界 (`mind_vision`)、北郡教士 (`northshire_cleric`)
- **ROGUE**：致命毒藥 (`deadly_poison`)、剔骨 (`eviscerate`)、背刺 (`backstab`)、邪惡攻擊 (`sinister_strike`)、悶棍 (`sap`)、剃骨刀 (`shiv`)、刀扇 (`fan_of_knives`)、刺殺 (`assassinate`)、疾跑 (`sprint`)、消失 (`vanish`)
- **SHAMAN**：閃電箭 (`lightning_bolt`)、石化武器 (`rockbiter_weapon`)、冰霜震擊 (`frost_shock`)、嗜血 (`bloodlust`)、野性之魂 (`feral_spirit`)、先祖治療 (`ancestral_healing`)、妖術 (`hex`)、圖騰之力 (`totemic_might`)、風怒 (`windfury`)、火舌圖騰 (`flametongue_totem`)
- **WARLOCK**：死亡纏繞 (`mortal_coil`)、暗影箭 (`shadow_bolt`)、生命吸取 (`drain_life`)、地獄烈焰 (`hellfire`)、靈魂之火 (`soulfire`)、腐蝕術 (`corruption`)、虛無行者 (`voidwalker`)、血之小鬼 (`blood_imp`)、惡魔守衛 (`felguard`)、恐懼地獄火 (`dread_infernal`)
- **WARRIOR**：熾炎戰斧 (`fiery_war_axe`)、奧金斧 (`arcanite_reaper`)、斬殺 (`execute`)、盾牌格擋 (`shield_block`)、衝鋒 (`charge`)、英勇打擊 (`heroic_strike`)、旋風斬 (`whirlwind`)、順劈斬 (`cleave`)、戰鬥怒火 (`battle_rage`)、戰歌指揮官 (`warsong_commander`)

### 不可收集卡

- 幸運幣 (`the_coin`)：0 費，這回合獲得 1 點 Mana。
- Token 另見 `src/cards/tokens.py`，不會進入隨機牌組池。
