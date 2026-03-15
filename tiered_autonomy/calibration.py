"""Confidence calibration subsystem (paper Section III-B).

The tiered-autonomy controller gates agent authority on a *calibrated*
confidence signal, not on a raw model score. Raw LLM confidence is
systematically overconfident, so promoting an agent to an autonomous tier on
that signal would delegate authority the agent has not earned. This module
turns the paper's two proposed calibration mechanisms into running code:

1. **Post-hoc recalibration** on a rolling window of recently resolved
   incidents, using *predicted-vs-realized success* as the reliability target.
   Two estimators are provided:
     * :class:`TemperatureScaler` -- single-parameter logit rescaling, the
       standard remedy for uniform over/under-confidence.
     * :class:`IsotonicCalibrator` -- non-parametric monotonic mapping via the
       pool-adjacent-violators algorithm (implemented here; no scikit-learn),
       for non-uniform miscalibration.
   :class:`RollingCalibrator` wraps either estimator in a fixed-size window so
   the mapping is refreshed on the cadence at which infrastructure drifts.

2. **Ensemble disagreement** across specialized diagnostic agents as an
   *independent* reliability proxy (:func:`ensemble_disagreement`). It is
   combined with the recalibrated score conservatively via
   :func:`conservative_estimate` = ``min(recalibrated, 1 - disagreement)``:
   an agent is only trusted when it is both well-calibrated in the aggregate
   *and* its specialized peers concur on this specific incident.

:func:`expected_calibration_error` and :func:`reliability_diagram` are the
measurement side -- they let the paper report the *measured* ECE a mechanism
achieves rather than merely proposing calibration.

Dependency footprint: numpy + scipy + matplotlib only.
"""
from __future__ import annotations

from collections import deque
from typing import Deque, Optional, Tuple

import numpy as np
from scipy.optimize import minimize_scalar

__all__ = [
    "TemperatureScaler",
    "IsotonicCalibrator",
    "ensemble_disagreement",
    "conservative_estimate",
    "expected_calibration_error",
    "reliability_diagram",
    "RollingCalibrator",
]

# Guard probabilities away from the {0, 1} boundary so logit()/log() stay
# finite. Applied everywhere a probability is fed into a logit or a log.
_EPS = 1e-6


def _as_1d_float(x) -> np.ndarray:
    """Coerce input to a 1-D float64 array (copy, never a view)."""
    return np.asarray(x, dtype=np.float64).ravel()


def _clip_prob(p: np.ndarray) -> np.ndarray:
    """Clip probabilities into ``[_EPS, 1 - _EPS]``."""
    return np.clip(p, _EPS, 1.0 - _EPS)


def _logit(p: np.ndarray) -> np.ndarray:
    p = _clip_prob(p)
    return np.log(p) - np.log1p(-p)


def _sigmoid(z: np.ndarray) -> np.ndarray:
    # Numerically stable logistic sigmoid.
    out = np.empty_like(z, dtype=np.float64)
    pos = z >= 0
    out[pos] = 1.0 / (1.0 + np.exp(-z[pos]))
    ez = np.exp(z[~pos])
    out[~pos] = ez / (1.0 + ez)
    return out


class TemperatureScaler:
    """Single-parameter temperature scaling of confidence scores.

    Fits a scalar temperature ``T > 0`` by minimizing the negative
    log-likelihood of the observed binary outcomes under the rescaled
    probabilities. Rescaling is performed in logit space::

        p_calibrated = sigmoid( logit(p_raw) / T )

    ``T > 1`` softens an overconfident model (pulls scores toward 0.5);
    ``T < 1`` sharpens an underconfident one. Temperature scaling is
    monotone and therefore never changes the *ranking* of confidences, only
    their absolute calibration -- exactly the property the tier gate needs.

    Attributes
    ----------
    temperature_ : float
        The fitted temperature. ``None`` until :meth:`fit` is called.
    """

    def __init__(self, bounds: Tuple[float, float] = (1e-2, 1e2)) -> None:
        self.bounds = bounds
        self.temperature_: Optional[float] = None

    def fit(self, confidences, outcomes) -> "TemperatureScaler":
        """Fit the temperature on (predicted confidence, realized outcome).

        Parameters
        ----------
        confidences : array-like, shape (n,)
            Raw predicted success probabilities in [0, 1].
        outcomes : array-like, shape (n,)
            Realized binary outcomes (1 = success, 0 = failure).
        """
        conf = _as_1d_float(confidences)
        y = _as_1d_float(outcomes)
        if conf.shape != y.shape:
            raise ValueError("confidences and outcomes must have equal length")
        if conf.size == 0:
            raise ValueError("cannot fit on empty data")

        logits = _logit(conf)

        def nll(t: float) -> float:
            # t is the temperature; scale logits and evaluate cross-entropy.
            p = _clip_prob(_sigmoid(logits / t))
            return float(-np.sum(y * np.log(p) + (1.0 - y) * np.log1p(-p)))

        res = minimize_scalar(nll, bounds=self.bounds, method="bounded")
        # minimize_scalar(bounded) returns a positive x within bounds.
        self.temperature_ = float(res.x)
        return self

    def transform(self, confidences) -> np.ndarray:
        """Apply the fitted temperature to new confidence scores."""
        if self.temperature_ is None:
            raise RuntimeError("TemperatureScaler must be fit before transform")
        conf = _as_1d_float(confidences)
        return _sigmoid(_logit(conf) / self.temperature_)

    def fit_transform(self, confidences, outcomes) -> np.ndarray:
        return self.fit(confidences, outcomes).transform(confidences)


class IsotonicCalibrator:
    """Non-parametric monotonic calibration (pool-adjacent-violators).

    Learns a non-decreasing mapping from raw confidence to empirical success
    rate. Unlike temperature scaling this can correct *non-uniform*
    miscalibration (e.g. well-calibrated in the mid-range but overconfident at
    the top), at the cost of needing more data to be stable.

    The pool-adjacent-violators algorithm (PAVA) is implemented directly here
    (the task forbids scikit-learn). Given points sorted by input, PAVA is the
    exact least-squares isotonic regressor: it repeatedly merges adjacent
    blocks that violate monotonicity into their weighted mean.

    Prediction interpolates linearly between the learned knots and clamps to
    the endpoint values outside the observed input range.
    """

    def __init__(self) -> None:
        self.x_thresholds_: Optional[np.ndarray] = None
        self.y_thresholds_: Optional[np.ndarray] = None

    @staticmethod
    def _pava(y: np.ndarray, w: np.ndarray) -> np.ndarray:
        """Pool-adjacent-violators; returns non-decreasing fit for each point.

        ``y`` must already be ordered by the (ascending) input variable.
        Blocks are tracked as [value, weight, count] so they can be expanded
        back to per-point fitted values.
        """
        blocks = []  # each: [value, weight, count]
        for i in range(y.shape[0]):
            blocks.append([float(y[i]), float(w[i]), 1])
            # Merge while the previous block is higher than the current one.
            while len(blocks) > 1 and blocks[-2][0] > blocks[-1][0]:
                v2, w2, c2 = blocks.pop()
                v1, w1, c1 = blocks.pop()
                nw = w1 + w2
                nv = (v1 * w1 + v2 * w2) / nw
                blocks.append([nv, nw, c1 + c2])
        out = np.empty(y.shape[0], dtype=np.float64)
        idx = 0
        for v, _w, c in blocks:
            out[idx:idx + c] = v
            idx += c
        return out

    def fit(self, confidences, outcomes) -> "IsotonicCalibrator":
        conf = _as_1d_float(confidences)
        y = _as_1d_float(outcomes)
        if conf.shape != y.shape:
            raise ValueError("confidences and outcomes must have equal length")
        if conf.size == 0:
            raise ValueError("cannot fit on empty data")

        # Aggregate duplicate x values into a single weighted point so the
        # knot grid is strictly increasing (np.interp requires that).
        order = np.argsort(conf, kind="mergesort")
        xs = conf[order]
        ys = y[order]
        uniq_x, inv = np.unique(xs, return_inverse=True)
        counts = np.bincount(inv).astype(np.float64)
        sums = np.bincount(inv, weights=ys)
        mean_y = sums / counts

        fitted = self._pava(mean_y, counts)

        self.x_thresholds_ = uniq_x
        self.y_thresholds_ = np.clip(fitted, 0.0, 1.0)
        return self

    def transform(self, confidences) -> np.ndarray:
        if self.x_thresholds_ is None:
            raise RuntimeError("IsotonicCalibrator must be fit before transform")
        conf = _as_1d_float(confidences)
        if self.x_thresholds_.size == 1:
            # Degenerate: a single knot -> constant mapping.
            return np.full(conf.shape, float(self.y_thresholds_[0]))
        # np.interp clamps to endpoint y-values outside [x_min, x_max], which
        # is the desired monotone extrapolation for unseen inputs.
        return np.interp(conf, self.x_thresholds_, self.y_thresholds_)

    def fit_transform(self, confidences, outcomes) -> np.ndarray:
        return self.fit(confidences, outcomes).transform(confidences)


def ensemble_disagreement(member_confidences) -> np.ndarray:
    """Per-sample disagreement across ensemble members, in [0, 1].

    Parameters
    ----------
    member_confidences : array-like, shape (n_samples, n_members)
        Confidence each specialized diagnostic agent assigns to the same
        incident.

    Returns
    -------
    np.ndarray, shape (n_samples,)
        Disagreement score in [0, 1].

    Choice of statistic
    -------------------
    We use ``2 * std`` (population standard deviation across members), clipped
    to ``[0, 1]``. For confidences confined to [0, 1] the maximum spread is
    achieved by two members at 0 and 1, giving ``std = 0.5``; the factor of 2
    therefore rescales the attainable range to a full [0, 1] so the value is
    directly comparable to a probability and can be subtracted from 1 in
    :func:`conservative_estimate`. A single member yields disagreement 0.
    """
    m = np.asarray(member_confidences, dtype=np.float64)
    if m.ndim == 1:
        m = m.reshape(-1, 1)
    if m.ndim != 2:
        raise ValueError("member_confidences must be 2-D (n_samples, n_members)")
    if m.shape[1] < 2:
        return np.zeros(m.shape[0], dtype=np.float64)
    std = m.std(axis=1)  # population std (ddof=0)
    return np.clip(2.0 * std, 0.0, 1.0)


def conservative_estimate(recalibrated, disagreement) -> np.ndarray:
    """Combine the two reliability signals conservatively.

    Returns ``min(recalibrated, 1 - disagreement)`` elementwise: authority is
    only granted when the agent is well-calibrated in the aggregate *and* its
    specialized peers agree on this specific incident.
    """
    r = _as_1d_float(recalibrated)
    d = _as_1d_float(disagreement)
    if r.shape != d.shape:
        raise ValueError("recalibrated and disagreement must have equal length")
    return np.minimum(r, 1.0 - d)


def expected_calibration_error(confidences, outcomes, n_bins: int = 10) -> float:
    """Expected Calibration Error (equal-width binning), in [0, 1].

    ECE = sum_b (|b| / N) * | acc(b) - conf(b) |, where the sum is over
    ``n_bins`` equal-width confidence bins on [0, 1], ``acc(b)`` is the
    empirical success rate in bin ``b`` and ``conf(b)`` is the mean predicted
    confidence in bin ``b``. Empty bins contribute nothing.
    """
    conf = _as_1d_float(confidences)
    y = _as_1d_float(outcomes)
    if conf.shape != y.shape:
        raise ValueError("confidences and outcomes must have equal length")
    if conf.size == 0:
        raise ValueError("cannot compute ECE on empty data")
    if n_bins < 1:
        raise ValueError("n_bins must be >= 1")

    n = conf.size
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    # Assign each confidence to a bin index in [0, n_bins-1]; np.digitize with
    # right=True puts the boundary point in the lower bin, and we clamp so both
    # 0.0 and 1.0 land in a valid bin.
    idx = np.clip(np.digitize(conf, edges[1:-1], right=True), 0, n_bins - 1)

    ece = 0.0
    for b in range(n_bins):
        mask = idx == b
        cnt = int(mask.sum())
        if cnt == 0:
            continue
        acc = float(y[mask].mean())
        avg_conf = float(conf[mask].mean())
        ece += (cnt / n) * abs(acc - avg_conf)
    return float(ece)


def reliability_diagram(confidences, outcomes, path, n_bins: int = 10,
                        title: Optional[str] = None) -> str:
    """Save a reliability diagram (bin accuracy vs. confidence) to ``path``.

    Uses the non-interactive ``Agg`` backend so it runs headless. The diagonal
    is the perfect-calibration reference; bars above it indicate
    underconfidence, bars below indicate overconfidence. The measured ECE is
    annotated on the plot. Returns the path written.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    conf = _as_1d_float(confidences)
    y = _as_1d_float(outcomes)
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    centers = 0.5 * (edges[:-1] + edges[1:])
    idx = np.clip(np.digitize(conf, edges[1:-1], right=True), 0, n_bins - 1)

    bin_acc = np.full(n_bins, np.nan)
    bin_conf = np.full(n_bins, np.nan)
    for b in range(n_bins):
        mask = idx == b
        if mask.any():
            bin_acc[b] = y[mask].mean()
            bin_conf[b] = conf[mask].mean()

    ece = expected_calibration_error(conf, y, n_bins=n_bins)

    fig, ax = plt.subplots(figsize=(4.5, 4.5))
    width = 1.0 / n_bins
    valid = ~np.isnan(bin_acc)
    ax.bar(centers[valid], bin_acc[valid], width=width * 0.9,
           edgecolor="black", color="#4C72B0", alpha=0.85,
           label="Observed accuracy")
    # Gap bars (predicted - observed) to visualize miscalibration.
    ax.bar(centers[valid], bin_conf[valid] - bin_acc[valid], width=width * 0.9,
           bottom=bin_acc[valid], edgecolor="#8B0000", color="#C44E52",
           alpha=0.35, hatch="//", label="Calibration gap")
    ax.plot([0, 1], [0, 1], "k--", linewidth=1.2, label="Perfect calibration")

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Predicted confidence")
    ax.set_ylabel("Empirical success rate")
    ax.set_title(title or "Reliability diagram")
    ax.text(0.05, 0.92, f"ECE = {ece:.3f}", transform=ax.transAxes,
            fontsize=11, bbox=dict(boxstyle="round", facecolor="white",
                                   edgecolor="gray", alpha=0.8))
    ax.legend(loc="lower right", fontsize=8)
    ax.set_aspect("equal", adjustable="box")
    fig.tight_layout()
    fig.savefig(path, format="pdf", bbox_inches="tight")
    plt.close(fig)
    return str(path)


class RollingCalibrator:
    """Recalibration over a fixed-size rolling window of resolved incidents.

    Infrastructure drifts, so a calibration mapping learned once goes stale.
    This wrapper keeps only the most recent ``window_size`` (confidence,
    outcome) observations and refits the underlying calibrator on demand.

    Window semantics
    ----------------
    * :meth:`observe` appends one resolved incident; when the window is full
      the oldest observation is evicted (FIFO / sliding window).
    * :meth:`refresh` refits the wrapped calibrator on the *current* window
      contents. Nothing is refit automatically -- the caller controls the
      refresh cadence (e.g. nightly, or every K incidents), matching the
      drift timescale of the environment.
    * :meth:`transform` applies the most recently fitted mapping. Before the
      first successful :meth:`refresh` it is the identity (returns inputs
      unchanged), so the system degrades gracefully to raw confidence.
    """

    def __init__(self, base_calibrator=None, window_size: int = 500) -> None:
        if window_size < 1:
            raise ValueError("window_size must be >= 1")
        self.base = base_calibrator if base_calibrator is not None else TemperatureScaler()
        self.window_size = window_size
        self._conf: Deque[float] = deque(maxlen=window_size)
        self._out: Deque[float] = deque(maxlen=window_size)
        self._fitted = False

    def observe(self, confidence, outcome) -> "RollingCalibrator":
        """Append one resolved incident to the rolling window."""
        self._conf.append(float(confidence))
        self._out.append(float(outcome))
        return self

    def observe_many(self, confidences, outcomes) -> "RollingCalibrator":
        """Append a batch of resolved incidents (convenience)."""
        c = _as_1d_float(confidences)
        o = _as_1d_float(outcomes)
        if c.shape != o.shape:
            raise ValueError("confidences and outcomes must have equal length")
        for ci, oi in zip(c, o):
            self.observe(ci, oi)
        return self

    def refresh(self) -> "RollingCalibrator":
        """Refit the wrapped calibrator on the current window."""
        if len(self._conf) == 0:
            raise RuntimeError("cannot refresh on an empty window")
        conf = np.fromiter(self._conf, dtype=np.float64)
        out = np.fromiter(self._out, dtype=np.float64)
        self.base.fit(conf, out)
        self._fitted = True
        return self

    def transform(self, confidences) -> np.ndarray:
        """Apply the last-refreshed mapping (identity before first refresh)."""
        conf = _as_1d_float(confidences)
        if not self._fitted:
            return conf.copy()
        return self.base.transform(conf)

    @property
    def n_observed(self) -> int:
        """Number of incidents currently in the window."""
        return len(self._conf)
