"""Parameter sensitivity sweep: is the harm-reduction *sign* robust?

Run with:  python -m experiments.sensitivity_sweep

The paper claims the *magnitude* of tiered's harm advantage is parameter
dependent but its *sign* (tiered harm < full-autonomy harm) is robust. This
sweep stresses the three most load-bearing assumptions:
  * action mix -> heavy-irreversible (more R4/R5 traffic),
  * harm weights -> linear (0..4 instead of the convex 0,1,5,25,100),
  * operator bandwidth -> {0.15, 0.60} (scarce vs abundant human capacity).
For every config it prints tiered vs full harm and the reduction factor.
"""
import numpy as np

from tiered_autonomy.simulator import agg


def main():
    print("=" * 70)
    print("PARAMETER SENSITIVITY (does the harm benefit survive?)")
    print("(mean over 40 seeds; capability fixed)")
    print("=" * 70)
    configs = {
        "base":                 {},
        "heavy-irreversible":   {"mix": np.array([0.10, 0.15, 0.20, 0.25, 0.30])},
        "linear harm weights":  {"harm": np.array([0., 1., 2., 3., 4.])},
        "low bandwidth (0.15)": {"capacity": 0.15},
        "high bandwidth (0.60)": {"capacity": 0.60},
    }
    print(f"{'config':<24}{'tiered res %':>14}{'tiered harm':>13}"
          f"{'full harm':>12}{'reduction':>12}")
    results = {}
    for name, kw in configs.items():
        tm, _ = agg("tiered", **kw)
        fm, _ = agg("full", **kw)
        red = fm[1] / tm[1] if tm[1] > 0 else float("inf")
        print(f"{name:<24}{tm[0]:>14.1f}{tm[1]:>13.1f}{fm[1]:>12.1f}{red:>11.1f}x")
        results[name] = {"tiered_harm": float(tm[1]), "full_harm": float(fm[1]),
                         "reduction_x": float(red), "tiered_resolved": float(tm[0])}
    all_reduce = all(v["tiered_harm"] < v["full_harm"] for v in results.values())
    print(f"\nHarm-reduction sign robust across all configs: {all_reduce}")
    results["sign_robust"] = all_reduce
    return results


if __name__ == "__main__":
    main()
