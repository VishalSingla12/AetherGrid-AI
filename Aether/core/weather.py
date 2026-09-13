"""
Aether Weather Engine
Manages environmental conditions and dynamic weather multipliers omega(t).
"""

from enum import Enum
import random
from typing import Optional


class WeatherType(Enum):
    """Weather classifications and temporal traversal multipliers."""
    CLEAR = "clear"
    RAIN = "rain"
    FOG = "fog"
    SNOW = "snow"

    @property
    def multiplier(self) -> float:
        """Returns the weather multiplier omega(t)."""
        multipliers = {
            WeatherType.CLEAR: 1.00,
            WeatherType.RAIN: 1.22,
            WeatherType.FOG: 1.45,
            WeatherType.SNOW: 1.85,
        }
        return multipliers[self]


class WeatherManager:
    """
    Tracks and updates the global atmospheric state across time steps.
    Supports manual overrides and deterministic Markovian weather shifts.
    """

    def __init__(self, initial_weather: WeatherType = WeatherType.CLEAR, rng: Optional[random.Random] = None):
        self.current_weather: WeatherType = initial_weather
        self.remaining_duration: float = float("inf")
        self.rng: random.Random = rng or random.Random(42)

        # Transition matrix for autonomous weather shifts: P[current][next]
        self.transitions = {
            WeatherType.CLEAR: [(WeatherType.CLEAR, 0.75), (WeatherType.RAIN, 0.18), (WeatherType.FOG, 0.07)],
            WeatherType.RAIN: [(WeatherType.RAIN, 0.60), (WeatherType.CLEAR, 0.30), (WeatherType.SNOW, 0.10)],
            WeatherType.FOG: [(WeatherType.FOG, 0.50), (WeatherType.CLEAR, 0.40), (WeatherType.RAIN, 0.10)],
            WeatherType.SNOW: [(WeatherType.SNOW, 0.65), (WeatherType.CLEAR, 0.20), (WeatherType.FOG, 0.15)],
        }

    @property
    def multiplier(self) -> float:
        """Current weather multiplier omega(t)."""
        return self.current_weather.multiplier

    def set_weather(self, weather: WeatherType, duration_seconds: float = float("inf")) -> None:
        """Manually forces a weather condition for a designated duration."""
        self.current_weather = weather
        self.remaining_duration = max(1.0, duration_seconds)

    def step(self, dt: float = 1.0) -> bool:
        """
        Advances the weather clock by dt seconds.
        Returns True if a weather transition occurred during this step.
        """
        if self.remaining_duration != float("inf"):
            self.remaining_duration -= dt
            if self.remaining_duration <= 0:
                self._transition_weather()
                return True
        return False

    def _transition_weather(self) -> None:
        """Executes a stochastic Markov transition to a new weather state."""
        options = self.transitions[self.current_weather]
        types, weights = zip(*options)
        new_weather = self.rng.choices(types, weights=weights, k=1)[0]
        # Duration between 300s (5 min) and 1800s (30 min)
        duration = self.rng.uniform(300.0, 1800.0)
        self.set_weather(new_weather, duration)
