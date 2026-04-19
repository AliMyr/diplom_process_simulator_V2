from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from ..core.interfaces import Parameter


@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]


class ParameterValidator:

    @staticmethod
    def validate_parameters(
        values: Dict[str, float],
        parameters: List[Parameter]
    ) -> ValidationResult:
        errors = []
        warnings = []

        param_dict = {p.name: p for p in parameters}

        for name, value in values.items():
            if name not in param_dict:
                warnings.append(f"Неизвестный параметр: {name}")
                continue

            param = param_dict[name]

            if value < param.min_value or value > param.max_value:
                errors.append(
                    f"'{param.display_name}' = {value} вне диапазона "
                    f"[{param.min_value}, {param.max_value}]"
                )

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )


class SimulationValidator:

    @staticmethod
    def validate_time_params(
        t_start: float,
        t_end: float,
        num_points: int
    ) -> ValidationResult:
        errors = []
        warnings = []

        if t_end <= t_start:
            errors.append("Конечное время должно быть больше начального")

        if num_points < 2:
            errors.append("Количество точек должно быть не менее 2")

        if num_points > 100000:
            warnings.append("Большое количество точек может замедлить расчёт")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )