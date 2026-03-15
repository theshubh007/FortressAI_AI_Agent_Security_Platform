"""Tests for the adversarial containment primitive (confidence poisoning).

The security claim is a *containment* property, not merely a harm-reduction one:
under maximal confidence poisoning, tiered catastrophic (R5) harm must be
exactly 0, because R5 is never-autonomous and no confidence inflation can
promote it. Total tiered harm must also stay strictly below full autonomy.
"""
import pytest

from tiered_autonomy.security import run_containment

# Keep tests fast: smaller N and fewer seeds than the demo entrypoint.
TEST_N = 20_000
TEST_SEEDS = range(6)


def test_tiered_r5_harm_zero_under_maximal_poisoning():
    """R5 is never-autonomous -> catastrophic harm stays 0 even at frac=1.0."""
    res = run_containment(poison_frac=1.0, seeds=TEST_SEEDS, n=TEST_N)
    assert res["tiered_r5_harm"] == 0.0
    assert res["tiered_r5_contained"] is True


def test_full_autonomy_r5_harm_explodes_under_poisoning():
    """Full autonomy executes R5 regardless of confidence -> nonzero R5 harm."""
    res = run_containment(poison_frac=1.0, seeds=TEST_SEEDS, n=TEST_N)
    assert res["full_r5_harm"] > 0.0


def test_tiered_total_harm_below_full_under_poisoning():
    """Even with R2-R4 poisoned through their gates, tiered total < full."""
    res = run_containment(poison_frac=1.0, seeds=TEST_SEEDS, n=TEST_N)
    assert res["tiered_total_harm"] < res["full_total_harm"]


def test_tiered_r5_contained_across_poison_levels():
    """R5 containment holds at every poison level, not just the maximum."""
    for frac in (0.25, 0.5, 0.75, 1.0):
        res = run_containment(poison_frac=frac, seeds=range(4), n=TEST_N)
        assert res["tiered_r5_harm"] == 0.0, f"leak at poison_frac={frac}"


def test_containment_reports_benign_baseline():
    """The result carries a benign (no-poison) baseline for context."""
    res = run_containment(poison_frac=1.0, seeds=TEST_SEEDS, n=TEST_N)
    assert res["tiered_r5_harm_benign"] == 0.0
    # Poisoning should not reduce full autonomy's total harm below benign.
    assert res["full_total_harm"] >= res["full_total_harm_benign"] - 1e-6
