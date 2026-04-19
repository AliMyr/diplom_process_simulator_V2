# tests/test_engine.py

import pytest
import numpy as np
from src.core.simulation_engine import SimulationEngine
from src.core.interfaces import SimulationState
from src.models import HarmonicOscillator, SIRModel


class TestSimulationEngine:
    def test_run_simulation(self):
        """Базовый тест симуляции."""
        engine = SimulationEngine()
        model = HarmonicOscillator()
        engine.set_model(model)

        result = engine.run(t_start=0, t_end=10, num_points=100)

        assert len(result.time) == 100
        assert "x" in result.states
        assert "v" in result.states
        assert result.metadata['model'] == model.name

    def test_engine_state_transitions(self):
        """Проверить переходы состояний движка."""
        engine = SimulationEngine()
        model = HarmonicOscillator()

        assert engine.get_state() == SimulationState.IDLE
        engine.set_model(model)
        assert engine.get_state() == SimulationState.IDLE

        result = engine.run(t_start=0, t_end=1, num_points=10)
        assert engine.get_state() == SimulationState.COMPLETED
        assert engine.last_result is not None

    def test_invalid_time_params(self):
        """Некорректные параметры времени должны вызвать ошибку."""
        engine = SimulationEngine()
        model = HarmonicOscillator()
        engine.set_model(model)

        with pytest.raises(ValueError):
            engine.run(t_start=10, t_end=5, num_points=100)  # t_end < t_start

    def test_model_not_set(self):
        """Симуляция без установленной модели должна вызвать ошибку."""
        engine = SimulationEngine()

        with pytest.raises(RuntimeError):
            engine.run(t_start=0, t_end=10, num_points=100)

    def test_parameter_update(self):
        """Тест обновления параметров."""
        engine = SimulationEngine()
        model = HarmonicOscillator()
        engine.set_model(model)

        new_params = {"m": 2.0, "k": 20.0, "gamma": 1.0, "x0": 2.0, "v0": 1.0}
        engine.set_parameters(new_params)

        result = engine.run(t_start=0, t_end=5, num_points=50)
        assert result.metadata['parameters']['m'] == 2.0