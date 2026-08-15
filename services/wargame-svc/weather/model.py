"""Stochastic weather states and their battlefield effects."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import random


class WeatherState(str, Enum):
    CLEAR = "CLEAR"
    RAIN = "RAIN"
    FOG = "FOG"
    SNOW = "SNOW"
    WIND = "WIND"


@dataclass(frozen=True)
class WeatherEffects:
    visibility: float
    movement_speed: float
    sensor_effectiveness: float
    communication_quality: float
    detection_probability: float


class WeatherModel:
    """A seeded Markov weather process, allowing conditions to evolve per tick."""

    effects = {
        WeatherState.CLEAR: WeatherEffects(1.0, 1.0, 1.0, 1.0, 1.0),
        WeatherState.RAIN: WeatherEffects(.7, .78, .75, .86, .78),
        WeatherState.FOG: WeatherEffects(.32, .75, .42, .82, .48),
        WeatherState.SNOW: WeatherEffects(.55, .58, .62, .76, .65),
        WeatherState.WIND: WeatherEffects(.82, .86, .7, .65, .73),
    }

    transitions = {
        WeatherState.CLEAR: ((WeatherState.CLEAR, .65), (WeatherState.RAIN, .12), (WeatherState.FOG, .1), (WeatherState.SNOW, .04), (WeatherState.WIND, .09)),
        WeatherState.RAIN: ((WeatherState.CLEAR, .18), (WeatherState.RAIN, .5), (WeatherState.FOG, .14), (WeatherState.SNOW, .08), (WeatherState.WIND, .1)),
        WeatherState.FOG: ((WeatherState.CLEAR, .2), (WeatherState.RAIN, .14), (WeatherState.FOG, .5), (WeatherState.SNOW, .06), (WeatherState.WIND, .1)),
        WeatherState.SNOW: ((WeatherState.CLEAR, .12), (WeatherState.RAIN, .08), (WeatherState.FOG, .12), (WeatherState.SNOW, .56), (WeatherState.WIND, .12)),
        WeatherState.WIND: ((WeatherState.CLEAR, .25), (WeatherState.RAIN, .12), (WeatherState.FOG, .08), (WeatherState.SNOW, .05), (WeatherState.WIND, .5)),
    }

    def __init__(self, initial: WeatherState | str = WeatherState.CLEAR, rng: random.Random | None = None):
        self.state = WeatherState(initial)
        self.rng = rng or random.Random()

    @property
    def current_effects(self) -> WeatherEffects:
        return self.effects[self.state]

    def advance(self) -> WeatherState:
        states, weights = zip(*self.transitions[self.state])
        self.state = self.rng.choices(states, weights=weights, k=1)[0]
        return self.state
