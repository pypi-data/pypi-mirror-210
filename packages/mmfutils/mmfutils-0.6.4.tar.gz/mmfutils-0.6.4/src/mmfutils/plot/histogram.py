"""Histograms.
"""
import inspect
import warnings

import numpy as np

import scipy.stats
import scipy as sp

import matplotlib.pyplot as plt


rng = np.random.default_rng(seed=2)
Ns = 123
a = rng.normal(size=Ns)
w = rng.random(size=Ns)
range = (-1, 1)
n, bins = np.histogram(a, range=range, density=False)
x = 0.5 * (bins[:-1] + bins[1:])
dx = np.diff(bins)
t, b = np.histogram(a, bins=bins, density=False)
assert np.allclose(t, n) & np.allclose(b, bins)
h, b = np.histogram(a, bins=bins, density=True)
N = sum(n)
assert np.allclose(n, h * dx * N) & np.allclose(b, bins)

nw, b = np.histogram(a, bins=bins, density=False, weights=w)
hw, b = np.histogram(a, bins=bins, density=True, weights=w)
pw = hw * dx
Nw = sum(nw)
assert np.allclose(nw, hw * dx * Nw) & np.allclose(b, bins)


def histerr(x, histtype="step", sigma_bounds=(-1, 1), *v, **kw):
    """Adds errorbars to matplotlib's hist.

    Other Parameters
    ----------------
    sigma_bounds : (float, float)
        Confidence region to plot expressed in terms of 1D normal sigma percentiles.

    Notes
    -----
    Let `n` and `h` be the results of calling histogram with `density=False` and
    `density=True` respectively.  Then the probability corresponding to each bin is
    `p = h*dx` where `dx` is the width of the bin, so that `n = p*N` where `N=sum(n)`.



    """
    histogram_parameters = inspect.signature(np.histogram).parameters
    histogram_kw = {
        k: kw.get(k) for k in histogram_parameters if k in kw and k not in {"a"}
    }
    unknown_kw = {
        k: histogram_kw[k]
        for k in set(histogram_kw).difference({"bins", "range", "weights", "density"})
    }

    if unknown_kw:
        warnings.warn(
            "Unknown parameters {unknown_kw}: Assumptions about histogram may be invalid"
        )

    percentiles = 100 * sp.stats.norm().cdf(sigma_bounds)

    if samples is None:
        tops, bins = np.histogram(x, **histogram_kw)

        # Midpoints of the bins
        x = 0.5 * (bins[1:] + bins[:-1])
        dx = np.diff(bins)
        weights = histogram_kw.get("weights", np.ones_like(x))
        density = histogram_kw.get("density", histogram_parameters["density"].default)
        if density:
            weights /= (weights * dx).sum()
            assert np.allclose((weights * dx).sum(), 1)
            p = tops * dx

    else:
        histogram_kw
        for n in range(samples):
            kw.update(histtype=histtype)
            h, plt.hist(x, *v, **kw)
