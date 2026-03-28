"""
Nadaraya Wrapper - para probar distintos backends (custom, statsmodels, pyGRNN)
"""

from typing import List, Union
import numpy as np

class NadarayaWrapper:
    def __init__(self, h: float = 4.0, r: float = 4.0, backend: str = "statsmodels"):
        """
        :param h: bandwidth horizontal
        :param r: bandwidth vertical (si aplica)
        :param backend: "custom" | "statsmodels" | "grnn"
        """
        self.h = h
        self.r = r
        self.backend = backend

    def predict(self, x: Union[List, np.ndarray], y: Union[List, np.ndarray]) -> np.ndarray:
        """
        Calcula valores estimados de y dado x
        """
        if self.backend == "statsmodels":
            return self._predict_statsmodels(x, y)
        elif self.backend == "grnn":
            return self._predict_grnn(x, y)
        else:
            return self._predict_custom(x, y)

    # ----------------------------
    # Backends disponibles
    # ----------------------------
    def _predict_statsmodels(self, x, y):
        """Usa statsmodels.nonparametric.KernelReg"""
        from statsmodels.nonparametric.kernel_regression import KernelReg
        x = np.asarray(x)
        y = np.asarray(y)
        kr = KernelReg(endog=y, exog=x, var_type="c", reg_type="lc")
        mean, _ = kr.fit(x)
        return mean

    def _predict_grnn(self, x, y):
        """Usa pyGRNN (si está instalado)"""
        try:
            from pyGRNN import GRNN
            x = np.atleast_2d(x).T
            y = np.array(y)
            model = GRNN()
            model.fit(x, y)
            return model.predict(x)
        except ImportError:
            raise RuntimeError("pyGRNN no está instalado. Instálalo con: pip install pyGRNN")

    def _predict_custom(self, x, y):
        """Implementación casera Nadaraya-Watson"""
        x = np.asarray(x)
        y = np.asarray(y)
        weights = np.exp(-0.5 * ((x[:, None] - x[None, :]) / self.h) ** 2)
        weights /= weights.sum(axis=1)[:, None]
        return (weights @ y)

