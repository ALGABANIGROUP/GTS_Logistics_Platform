from __future__ import annotations

from typing import Iterable, List, Tuple


class SimpleLinearRegression:
    def __init__(self) -> None:
        self.coef_: float | None = None
        self.intercept_: float | None = None

    def fit(self, x_values: Iterable[float], y_values: Iterable[float]) -> "SimpleLinearRegression":
        x_list = [float(x) for x in x_values]
        y_list = [float(y) for y in y_values]

        if not x_list or len(x_list) != len(y_list):
            raise ValueError("x_values and y_values must be the same non-empty length.")

        n = float(len(x_list))
        x_mean = sum(x_list) / n
        y_mean = sum(y_list) / n

        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_list, y_list))
        denominator = sum((x - x_mean) ** 2 for x in x_list)

        if denominator == 0:
            self.coef_ = 0.0
        else:
            self.coef_ = numerator / denominator
        self.intercept_ = y_mean - (self.coef_ * x_mean)
        return self

    def predict(self, x_values: Iterable[float]) -> List[float]:
        if self.coef_ is None or self.intercept_ is None:
            raise ValueError("Model is not fitted.")
        return [self.coef_ * float(x) + self.intercept_ for x in x_values]


MARKETING_DATA: List[Tuple[float, float]] = [
    (1000.0, 200.0),
    (2000.0, 400.0),
    (3000.0, 600.0),
    (4000.0, 800.0),
    (5000.0, 1000.0),
]

_MODEL = SimpleLinearRegression()
_MODEL.fit([row[0] for row in MARKETING_DATA], [row[1] for row in MARKETING_DATA])


def predict_sales(budget: float) -> float:
    """Predict sales based on the advertising budget."""
    return _MODEL.predict([budget])[0]
