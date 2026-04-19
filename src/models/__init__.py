from .base_model import BaseModel
from .harmonic_oscillator import HarmonicOscillator
from .pendulum import Pendulum
from .population import LotkaVolterra
from .epidemic import SIRModel
from .mechanics import ProjectileMotion
from .chemistry import FirstOrderReaction, ReversibleReaction, Brusselator
from .physics import NewtonCooling, RLCCircuit, ThermalMass


def get_models_by_category():
    return {
        "Механика": [HarmonicOscillator(), Pendulum(), ProjectileMotion()],
        "Популяции": [LotkaVolterra()],
        "Эпидемиология": [SIRModel()],
        "Химия": [FirstOrderReaction(), ReversibleReaction(), Brusselator()],
        "Физика": [NewtonCooling(), RLCCircuit(), ThermalMass()],
    }