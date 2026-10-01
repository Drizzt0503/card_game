from __future__ import annotations

from collections.abc import Callable
from typing import Any


EffectBuilder = Callable[..., list[Any]]


class EffectBuilderRegistry:
    def __init__(self) -> None:
        self._builders: dict[str, EffectBuilder] = {}

    def register(self, effect_id: str, builder: EffectBuilder) -> None:
        if effect_id in self._builders:
            raise ValueError(f"Duplicate effect builder: {effect_id}")
        self._builders[effect_id] = builder

    def get(self, effect_id: str) -> EffectBuilder | None:
        return self._builders.get(effect_id)

    def ids(self) -> tuple[str, ...]:
        return tuple(self._builders)
