"""Worked calibration example (paper Section III-B, measured ECE).

Builds a deliberately *overconfident* synthetic diagnostic agent, measures its
Expected Calibration Error, recalibrates it with temperature scaling on a
held-out split, and reports the ECE reduction. Also demonstrates the ensemble
disagreement proxy and the conservative combination. Reliability diagrams for
the before/after states are written to ``figures/``.

Run from the project root::

    python -m examples.calibration_demo

``main()`` returns the metrics dict so tests can consume the numbers.
"""
from __future__ import annotations

import os
from pathlib import Path

import numpy as np

from tiered_autonomy.calibration import (
    IsotonicCalibrator,
    TemperatureScaler,
    conservative_estimate,
    ensemble_disagreement,
    expected_calibration_error,
    reliability_diagram,
)

SEED = 20260714


def make_overconfident_agent(n: int, rng: np.random.Generator):
    """Synthesize an overconfident agent's (confidence, outcome) records.

    * True success probability  p ~ Beta(3.5, 1.5)   (mean ~= 0.70)
    * Reported confidence       = clip(p + 0.12 + N(0, 0.05), 0, 1)
      -- a systematic +0.12 optimism bias plus reporting noise.
    * Realized outcome          ~ Bernoulli(p)
    """
    p = rng.beta(3.5, 1.5, size=n)
    confidence = np.clip(p + 0.12 + rng.normal(0.0, 0.05, size=n), 0.0, 1.0)
    outcomes = (rng.random(n) < p).astype(np.float64)
    return confidence, outcomes


def main() -> dict:
    rng = np.random.default_rng(SEED)

    n_total = 4000
    confidence, outcomes = make_overconfident_agent(n_total, rng)

    # Train / held-out split (post-hoc recalibration is fit on resolved
    # incidents, then measured on incidents it never saw).
    n_train = n_total // 2
    conf_tr, out_tr = confidence[:n_train], outcomes[:n_train]
    conf_te, out_te = confidence[n_train:], outcomes[n_train:]

    n_bins = 10
    ece_before = expected_calibration_error(conf_te, out_te, n_bins=n_bins)

    scaler = TemperatureScaler().fit(conf_tr, out_tr)
    conf_te_cal = scaler.transform(conf_te)
    ece_after = expected_calibration_error(conf_te_cal, out_te, n_bins=n_bins)

    temperature = scaler.temperature_
    reduction_pct = 100.0 * (ece_before - ece_after) / ece_before if ece_before > 0 else 0.0

    # Isotonic regression corrects non-uniform (non-multiplicative) miscalibration,
    # so on this additively-biased agent it typically beats temperature scaling.
    iso = IsotonicCalibrator().fit(conf_tr, out_tr)
    conf_te_iso = iso.transform(conf_te)
    ece_after_iso = expected_calibration_error(conf_te_iso, out_te, n_bins=n_bins)
    reduction_iso_pct = (
        100.0 * (ece_before - ece_after_iso) / ece_before if ece_before > 0 else 0.0
    )

    # ------------------------------------------------------------------ #
    # Reliability diagrams (before / after) -> figures/
    # ------------------------------------------------------------------ #
    fig_dir = Path(__file__).resolve().parent.parent / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    before_path = fig_dir / "reliability_before.pdf"
    after_path = fig_dir / "reliability_after.pdf"
    reliability_diagram(conf_te, out_te, before_path, n_bins=n_bins,
                        title="Before recalibration (raw confidence)")
    reliability_diagram(conf_te_cal, out_te, after_path, n_bins=n_bins,
                        title=f"After temperature scaling (T={temperature:.2f})")

    # ------------------------------------------------------------------ #
    # Ensemble disagreement + conservative combination (small example).
    # Three specialized agents score four incidents. In the first two they
    # concur; in the last two they diverge sharply.
    # ------------------------------------------------------------------ #
    members = np.array([
        [0.90, 0.88, 0.91],   # strong agreement, high confidence
        [0.40, 0.42, 0.38],   # agreement, low confidence
        [0.90, 0.55, 0.20],   # wide disagreement
        [0.95, 0.10, 0.50],   # very wide disagreement
    ])
    member_mean = members.mean(axis=1)
    disagreement = ensemble_disagreement(members)
    # Recalibrate the ensemble mean with the fitted scaler, then combine.
    recal_mean = scaler.transform(member_mean)
    conservative = conservative_estimate(recal_mean, disagreement)

    # ------------------------------------------------------------------ #
    # Report
    # ------------------------------------------------------------------ #
    print("=" * 68)
    print("Tiered-Autonomy calibration demo (seed = %d)" % SEED)
    print("=" * 68)
    print("Synthetic overconfident agent: p ~ Beta(3.5,1.5), "
          "confidence = clip(p + 0.12 + N(0,0.05), 0, 1)")
    print("Samples: %d total (%d train / %d held-out), ECE bins: %d"
          % (n_total, n_train, n_total - n_train, n_bins))
    print("-" * 68)
    print("ECE before: %.3f | ECE after (temperature=%.2f): %.3f | "
          "reduction: %.0f%%"
          % (ece_before, temperature, ece_after, reduction_pct))
    print("ECE before: %.3f | ECE after (isotonic):        %.3f | "
          "reduction: %.0f%%"
          % (ece_before, ece_after_iso, reduction_iso_pct))
    print("-" * 68)
    print("Ensemble disagreement + conservative estimate:")
    print("  %-22s %-10s %-12s %-12s %-12s"
          % ("members", "mean", "disagree", "recalibrated", "conservative"))
    for i in range(members.shape[0]):
        print("  %-22s %-10.3f %-12.3f %-12.3f %-12.3f"
              % (np.array2string(members[i], precision=2),
                 member_mean[i], disagreement[i],
                 recal_mean[i], conservative[i]))
    print("-" * 68)
    print("Figures written:")
    print("  %s (exists=%s)" % (before_path, before_path.exists()))
    print("  %s (exists=%s)" % (after_path, after_path.exists()))
    print("=" * 68)

    return {
        "seed": SEED,
        "n_total": n_total,
        "n_train": n_train,
        "n_test": n_total - n_train,
        "n_bins": n_bins,
        "ece_before": ece_before,
        "ece_after": ece_after,
        "ece_after_isotonic": ece_after_iso,
        "temperature": temperature,
        "reduction_pct": reduction_pct,
        "reduction_isotonic_pct": reduction_iso_pct,
        "member_confidences": members,
        "member_mean": member_mean,
        "disagreement": disagreement,
        "recalibrated_mean": recal_mean,
        "conservative": conservative,
        "figure_before": str(before_path),
        "figure_after": str(after_path),
        "figures_written": before_path.exists() and after_path.exists(),
    }


if __name__ == "__main__":
    main()
