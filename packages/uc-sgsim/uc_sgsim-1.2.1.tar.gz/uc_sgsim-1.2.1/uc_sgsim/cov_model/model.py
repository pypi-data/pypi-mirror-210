import numpy as np
from uc_sgsim.cov_model.base import CovModel


class Gaussian(CovModel):
    model_name = 'Gaussian'

    def model(self, h: float) -> float:
        partial_sill = self.sill - self.nugget
        return partial_sill * (1 - np.exp(-3 * h**2 / self.k_range**2)) + self.nugget


class Spherical(CovModel):
    model_name = 'Spherical'

    def model(self, h: float) -> float:
        partial_sill = self.sill - self.nugget
        if h <= self.k_range:
            return (
                partial_sill * (1.5 * h / self.k_range - 0.5 * (h / self.k_range) ** 3.0)
                + self.nugget
            )
        else:
            return partial_sill + self.nugget


class Exponential(CovModel):
    model_name = 'Exponential'

    def model(self, h: float) -> float:
        partial_sill = self.sill - self.nugget
        return partial_sill * (1 - np.exp(-3 * h / self.k_range)) + self.nugget
