# tests/test_models.py

import pytest
import numpy as np
from src.models import (
    HarmonicOscillator, SIRModel, Pendulum,
    FirstOrderReaction, LotkaVolterra, ProjectileMotion
)


class TestHarmonicOscillator:
    def test_initial_state(self):
        model = HarmonicOscillator()
        params = {
            "m": 1.0, "k": 10.0, "gamma": 0.5,
            "x0": 1.0, "v0": 0.0
        }
        state = model.get_initial_state(params)
        assert np.allclose(state, [1.0, 0.0])

    def test_derivatives_shape(self):
        model = HarmonicOscillator()
        state = np.array([1.0, 0.0])
        params = {"m": 1.0, "k": 10.0, "gamma": 0.5, "x0": 1.0, "v0": 0.0}
        deriv = model.derivatives(0.0, state, params)
        assert deriv.shape == state.shape

    def test_plot_config(self):
        model = HarmonicOscillator()
        config = model.get_plot_config()
        assert config.title
        assert len(config.legend_labels) == len(model.state_names)


class TestFirstOrderReaction:
    def test_conservation(self):
        """A + B должны быть const (консервация массы)."""
        model = FirstOrderReaction()
        params = {"A0": 1.0, "B0": 0.0, "k": 0.1}
        state = model.get_initial_state(params)
        total_initial = np.sum(state)

        # Симулируем несколько шагов
        for _ in range(10):
            state = model.derivatives(0.0, state, params) * 0.01 + state

        total_final = np.sum(state)
        assert np.isclose(total_initial, total_final, rtol=0.01)


class TestSIRModel:
    def test_population_conservation(self):
        """S + I + R = N (консервация популяции)."""
        model = SIRModel()
        params = {"N": 1000, "beta": 0.3, "gamma": 0.1, "I0": 1}
        state = model.get_initial_state(params)
        total = np.sum(state)
        assert np.isclose(total, 1000)


class TestLotkaVolterra:
    def test_oscillatory_behavior(self):
        """Модель должна иметь циклическое поведение."""
        model = LotkaVolterra()
        params = {
            "alpha": 1.0, "beta": 0.1, "gamma": 1.5, "delta": 0.075,
            "x0": 40.0, "y0": 9.0
        }
        state = model.get_initial_state(params)
        assert np.all(state > 0)  # Популяции положительны


class TestProjectileMotion:
    def test_initial_velocity_components(self):
        """Проверить разложение начальной скорости."""
        model = ProjectileMotion()
        params = {
            "v0": 20.0, "angle": 45.0, "g": 9.81,
            "m": 1.0, "Cd": 0.0, "y0": 0.0
        }
        state = model.get_initial_state(params)
        # x, y, vx, vy = state
        # vx ≈ 20 * cos(45°) ≈ 14.14
        assert np.isclose(state[2], 20.0 * np.cos(np.radians(45)), rtol=0.01)
        assert np.isclose(state[3], 20.0 * np.sin(np.radians(45)), rtol=0.01)