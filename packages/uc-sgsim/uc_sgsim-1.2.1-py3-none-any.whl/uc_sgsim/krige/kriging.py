import numpy as np
from scipy.spatial.distance import pdist, squareform
from uc_sgsim.cov_model.base import CovModel
from uc_sgsim.krige.base import Kriging


class SimpleKrige(Kriging):
    def __init__(self, model: CovModel):
        super().__init__(model)

    def prediction(self, sample: np.array, unsampled: np.array) -> tuple[float, float]:
        n_sampled = len(sample)
        dist_diff = abs(sample[:, 0] - unsampled)
        dist_diff = dist_diff.reshape(len(dist_diff), 1)

        grid = np.hstack([sample, dist_diff])
        meanvalue = 0

        cov_dist = np.array(self.model.cov_compute(grid[:, 2])).reshape(-1, 1)
        cov_data = squareform(pdist(grid[:, :1])).flatten()
        cov_data = np.array(self.model.cov_compute(cov_data))
        cov_data = cov_data.reshape(n_sampled, n_sampled)

        weights = np.linalg.solve(cov_data, cov_dist)

        residuals = grid[:, 1] - meanvalue
        estimation = np.dot(weights.T, residuals) + meanvalue
        krige_var = float(self.model.sill - np.dot(weights.T, cov_dist))

        if krige_var < 0:
            krige_var = 0

        krige_std = np.sqrt(krige_var)

        return estimation, krige_std

    def simulation(self, x: np.array, unsampled: np.array, **kwargs) -> float:
        neighbor = kwargs.get('neighbor')
        if neighbor is not None:
            dist = abs(x[:, 0] - unsampled)
            dist = dist.reshape(len(dist), 1)
            has_neighbor = self.find_neighbor(dist, neighbor)
            if has_neighbor:
                return has_neighbor
            x = np.hstack([x, dist])
            x = np.array(sorted(x, key=lambda itr: itr[2])[:neighbor])

        estimation, krige_std = self.prediction(x, unsampled)

        random_fix = np.random.normal(0, krige_std, 1)
        return estimation + random_fix

    def find_neighbor(self, dist: list[float], neighbor: int) -> float:
        if neighbor == 0:
            return np.random.normal(0, self.model.sill**0.5, 1)
        close_point = 0

        criteria = self.k_range * 1.732 if self.model.model_name == 'Gaussian' else self.k_range

        for item in dist:
            if item <= criteria:
                close_point += 1

        if close_point == 0:
            return np.random.normal(0, self.model.sill**0.5, 1)
