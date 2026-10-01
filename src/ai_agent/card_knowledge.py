"""Small explicit rule table used only by the baseline AI."""

DAMAGE_BY_CARD = {
    "arcane_shot": 2, "fireball": 6, "frostbolt": 3,
    "holy_smite": 2, "holy_fire": 5, "moonfire": 1,
    "starfire": 5, "lightning_bolt": 3, "frost_shock": 1,
    "shadow_bolt": 4, "drain_life": 2, "eviscerate": 2,
    "backstab": 2, "shiv": 1, "kill_command": 3,
    "elven_archer": 1, "ironforge_rifleman": 1,
    "stormpike_commando": 2, "swipe": 4,
}

AREA_CLEAR_CARDS = {
    "arcane_explosion", "flamestrike", "holy_nova", "consecration",
    "hellfire", "fan_of_knives", "whirlwind", "cleave", "swipe",
}

REMOVAL_WEAPONS = {
    "fiery_war_axe", "arcanite_reaper", "lights_justice", "truesilver_champion",
}

HERO_POWER_DAMAGE = {
    "fireblast": 1,
}
