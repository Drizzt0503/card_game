from __future__ import annotations

from ..domain.game_state import GameState


class AuraStateCheck:
    """Rebuilds derived minion values from the current board state."""

    def apply(self, state: GameState) -> None:
        for player in state.players:
            for minion in player.board:
                minion.aura_attack = 0
                minion.aura_health = 0

        for player in state.players:
            for source in player.board:
                if "buff_other_minions_attack_health" in source.aura_ids:
                    for target in player.board:
                        if target is not source:
                            target.aura_attack += 1
                            target.aura_health += 1
                elif "buff_other_minions_attack" in source.aura_ids:
                    for target in player.board:
                        if target is not source:
                            target.aura_attack += 1
                elif "buff_other_murlocs_attack" in source.aura_ids:
                    for target in player.board:
                        if target is not source and target.tribe == "MURLOC":
                            target.aura_attack += 1
                elif "buff_other_beasts_attack" in source.aura_ids:
                    for target in player.board:
                        if target is not source and target.tribe == "BEAST":
                            target.aura_attack += 1
                elif "buff_adjacent_attack" in source.aura_ids:
                    index = player.board.index(source)
                    for target_index in (index - 1, index + 1):
                        if 0 <= target_index < len(player.board):
                            player.board[target_index].aura_attack += 2
                elif "buff_other_minions_health" in source.aura_ids:
                    for target in player.board:
                        if target is not source:
                            target.aura_health += 1

        for player in state.players:
            for minion in player.board:
                old_max = minion.max_hp
                minion.attack = minion._base_attack + minion.buff_attack + minion.aura_attack
                minion.max_hp = minion._base_max_hp + minion.buff_health + minion.aura_health
                if minion.max_hp < old_max:
                    minion.hp = min(minion.hp, minion.max_hp)


def recalculate_auras(state: GameState) -> None:
    AuraStateCheck().apply(state)
