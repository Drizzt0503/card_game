from ..domain.card import CardDefinition, CardInstance


TOKEN_DEFINITIONS = {
    "healing_totem": CardDefinition(
        "healing_totem", "Healing Totem", 1, 0, 2,
        card_class="SHAMAN", rarity="TOKEN", collectible=False,
    ),
    "stoneclaw_totem": CardDefinition(
        "stoneclaw_totem", "Stoneclaw Totem", 1, 0, 2,
        card_class="SHAMAN", rarity="TOKEN", collectible=False,
        description_zh="嘲諷。", description_en="Taunt.", initial_statuses=("taunt",),
    ),
    "searing_totem": CardDefinition(
        "searing_totem", "Searing Totem", 1, 1, 1,
        card_class="SHAMAN", rarity="TOKEN", collectible=False,
    ),
    "wrath_of_air_totem": CardDefinition(
        "wrath_of_air_totem", "Wrath of Air Totem", 1, 0, 2,
        card_class="SHAMAN", rarity="TOKEN", collectible=False, spell_power=1,
    ),
    "silver_hand_recruit": CardDefinition(
        "silver_hand_recruit", "Silver Hand Recruit", 1, 1, 1,
        card_class="PALADIN", rarity="TOKEN", collectible=False,
    ),
    "mirror_image": CardDefinition(
        "mirror_image", "Mirror Image", 1, 0, 2,
        card_class="MAGE", rarity="TOKEN", collectible=False,
        description_zh="嘲諷。", description_en="Taunt.", initial_statuses=("taunt",),
    ),
    "boar": CardDefinition(
        "boar", "野豬", 1, 1, 1, tribe="BEAST", rarity="TOKEN", collectible=False,
        description_zh="衝鋒。", description_en="Charge.", initial_statuses=("charge",),
    ),
    "mechanical_dragonling": CardDefinition(
        "mechanical_dragonling", "機械幼龍", 1, 2, 1,
        tribe="MECH", rarity="TOKEN", collectible=False,
    ),
    "murloc_raider": CardDefinition(
        "murloc_raider", "魚人斥候", 1, 2, 1,
        tribe="MURLOC", card_class="NEUTRAL", rarity="TOKEN", collectible=False,
    ),
    "spirit_wolf": CardDefinition(
        "spirit_wolf", "幽靈狼", 2, 2, 3, card_class="SHAMAN",
        rarity="TOKEN", collectible=False, description_zh="嘲諷。",
        description_en="Taunt.", initial_statuses=("taunt",),
    ),
    "sheep": CardDefinition(
        "sheep", "綿羊", 1, 1, 1, rarity="TOKEN", collectible=False,
    ),
    "huffer": CardDefinition("huffer", "呼呼", 3, 4, 2, tribe="BEAST", rarity="TOKEN", collectible=False,
                             description_zh="衝鋒。", description_en="Charge.", initial_statuses=("charge",)),
    "misha": CardDefinition("misha", "米莎", 3, 4, 4, tribe="BEAST", rarity="TOKEN", collectible=False,
                            description_zh="嘲諷。", description_en="Taunt.", initial_statuses=("taunt",)),
    "leokk": CardDefinition("leokk", "雷歐克", 3, 2, 4, tribe="BEAST", rarity="TOKEN", collectible=False),
    "frog": CardDefinition("frog", "青蛙", 1, 0, 1, rarity="TOKEN", collectible=False),
}


def make_token(card_id: str, instance_id: int) -> CardInstance:
    try:
        definition = TOKEN_DEFINITIONS[card_id]
    except KeyError:
        raise ValueError(f"Unknown token: {card_id}") from None
    return CardInstance(instance_id, definition)
