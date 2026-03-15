"""Tests for the calibration subsystem (paper Section III-B).

These tests pin the behavioral contracts the tier gate relies on:
recalibration reduces ECE on overconfident data, ECE is a well-formed metric,
the ensemble proxy and conservative combination behave as specified, isotonic
output is monotone, and the rolling recalibrator corrects drifted data.
"""
from __future__ import annotations

import numpy as np
import pytest

from tiered_autonomy.calibration import (
    IsotonicCalibrator,
    RollingCalibrator,
    TemperatureScaler,
    conservative_estimate,
    ensemble_disagreement,
    expected_calibration_error,
)

SEED = 20260714


def _overconfident(n, rng, bias=0.12):
    """(confidence, outcome) for a systematically overconfident agent."""
    p = rng.beta(3.5, 1.5, size=n)
    conf = np.clip(p + bias + rng.normal(0.0, 0.05, size=n), 0.0, 1.0)
    out = (rng.random(n) < p).astype(np.float64)
    return conf, out


def _well_calibrated(n, rng):
    """(confidence, outcome) where outcome ~ Bernoulli(confidence)."""
    conf = rng.uniform(0.0, 1.0, size=n)
    out = (rng.random(n) < conf).astype(np.float64)
    return conf, out


# --------------------------------------------------------------------------- #
# Temperature scaling reduces ECE
# --------------------------------------------------------------------------- #
def test_temperature_scaling_reduces_ece():
    rng = np.random.default_rng(SEED)
    conf_tr, out_tr = _overconfident(3000, rng)
    conf_te, out_te = _overconfident(3000, rng)

    ece_before = expected_calibration_error(conf_te, out_te)
    scaler = TemperatureScaler().fit(conf_tr, out_tr)
    ece_after = expected_calibration_error(scaler.transform(conf_te), out_te)

    assert ece_after < ece_before
    # An overconfident model should be softened: T > 1.
    assert scaler.temperature_ > 1.0


# --------------------------------------------------------------------------- #
# ECE is a well-formed metric in [0, 1]
# --------------------------------------------------------------------------- #
def test_ece_in_unit_interval():
    rng = np.random.default_rng(SEED)
    conf, out = _overconfident(2000, rng)
    ece = expected_calibration_error(conf, out)
    assert 0.0 <= ece <= 1.0


def test_ece_maximal_case():
    # Confident-and-always-wrong -> ECE close to 1.
    conf = np.full(500, 0.99)
    out = np.zeros(500)
    assert expected_calibration_error(conf, out) > 0.95


def test_perfectly_calibrated_near_zero_ece():
    rng = np.random.default_rng(SEED)
    conf, out = _well_calibrated(20000, rng)
    ece = expected_calibration_error(conf, out, n_bins=10)
    assert ece < 0.05


# --------------------------------------------------------------------------- #
# Ensemble disagreement
# --------------------------------------------------------------------------- #
def test_disagreement_zero_when_members_agree():
    members = np.array([[0.8, 0.8, 0.8], [0.3, 0.3, 0.3]])
    d = ensemble_disagreement(members)
    assert np.allclose(d, 0.0)
    assert np.all((d >= 0.0) & (d <= 1.0))


def test_disagreement_larger_when_members_disagree():
    agree = ensemble_disagreement(np.array([[0.5, 0.52, 0.48]]))
    disagree = ensemble_disagreement(np.array([[0.0, 0.5, 1.0]]))
    assert disagree[0] > agree[0]
    assert np.all((disagree >= 0.0) & (disagree <= 1.0))


def test_disagreement_bounds_and_single_member():
    # Extreme split -> saturates near 1.
    extreme = ensemble_disagreement(np.array([[0.0, 1.0]]))
    assert extreme[0] == pytest.approx(1.0)
    # Single member -> no disagreement.
    single = ensemble_disagreement(np.array([[0.7], [0.2]]))
    assert np.allclose(single, 0.0)


# --------------------------------------------------------------------------- #
# Conservative combination
# --------------------------------------------------------------------------- #
def test_conservative_estimate_never_exceeds_inputs():
    rng = np.random.default_rng(SEED)
    recal = rng.uniform(0.0, 1.0, size=1000)
    disagree = rng.uniform(0.0, 1.0, size=1000)
    cons = conservative_estimate(recal, disagree)
    assert np.all(cons <= recal + 1e-12)
    assert np.all(cons <= (1.0 - disagree) + 1e-12)


# --------------------------------------------------------------------------- #
# Isotonic monotonicity
# --------------------------------------------------------------------------- #
def test_isotonic_output_is_monotone():
    rng = np.random.default_rng(SEED)
    conf, out = _overconfident(2000, rng)
    iso = IsotonicCalibrator().fit(conf, out)
    grid = np.linspace(0.0, 1.0, 200)
    mapped = iso.transform(grid)
    diffs = np.diff(mapped)
    assert np.all(diffs >= -1e-9)
    assert np.all((mapped >= 0.0) & (mapped <= 1.0))


def test_isotonic_reduces_ece_too():
    rng = np.random.default_rng(SEED)
    conf_tr, out_tr = _overconfident(4000, rng)
    conf_te, out_te = _overconfident(4000, rng)
    iso = IsotonicCalibrator().fit(conf_tr, out_tr)
    before = expected_calibration_error(conf_te, out_te)
    after = expected_calibration_error(iso.transform(conf_te), out_te)
    assert after < before


# --------------------------------------------------------------------------- #
# Rolling recalibrator corrects drifted (overconfident) data
# --------------------------------------------------------------------------- #
def test_rolling_calibrator_refresh_reduces_ece():
    rng = np.random.default_rng(SEED)
    roller = RollingCalibrator(TemperatureScaler(), window_size=1000)

    # Before any refresh, transform is the identity.
    probe = np.array([0.3, 0.6, 0.9])
    assert np.allclose(roller.transform(probe), probe)

    # Stream resolved overconfident incidents into the window, then refresh.
    obs_conf, obs_out = _overconfident(1500, rng)  # window keeps last 1000
    roller.observe_many(obs_conf, obs_out)
    roller.refresh()

    # Fresh overconfident batch: recalibrated ECE must beat raw ECE.
    fresh_conf, fresh_out = _overconfident(2000, rng)
    ece_raw = expected_calibration_error(fresh_conf, fresh_out)
    ece_cal = expected_calibration_error(roller.transform(fresh_conf), fresh_out)
    assert ece_cal < ece_raw


def test_rolling_window_evicts_oldest():
    roller = RollingCalibrator(TemperatureScaler(), window_size=100)
    for _ in range(250):
        roller.observe(0.9, 1.0)
    assert roller.n_observed == 100


# --------------------------------------------------------------------------- #
# Demo is runnable and returns reproducible metrics
# --------------------------------------------------------------------------- #
def test_demo_runs_and_reduces_ece():
    from examples.calibration_demo import main

    metrics = main()
    assert metrics["ece_after"] < metrics["ece_before"]
    assert metrics["temperature"] > 1.0
    assert 0.0 <= metrics["ece_after"] <= 1.0
    assert metrics["figures_written"] is True
