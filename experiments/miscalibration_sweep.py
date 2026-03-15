"""Miscalibration sweep: does tiered's harm benefit survive overconfidence?

Run with:  python -m experiments.miscalibration_sweep

Sweeps a systematic overconfidence bias in {0.0, 0.10, 0.20} (confidence shifted
up before clipping) and reports, at each bias, the tiered harm/100 and its
reduction factor vs full autonomy. Overconfidence is the condition the paper
argues real LLM agents suffer; the point is that reversibility-typed gating
degrades gracefully because R5 stays never-autonomous regardless of confidence.
"""
from tiered_autonomy.simulator import agg


def main():
    print("=" * 70)
    print("MISCALIBRATION SWEEP (overconfidence bias); harm vs full autonomy")
    print("(mean over 40 seeds; capability fixed)")
    print("=" * 70)
    full_h = agg("full")[0][1]
    print(f"{'bias':>6}{'tiered harm/100':>18}{'reduction vs full':>20}"
          f"{'tiered resolved %':>20}")
    results = {}
    for b in (0.0, 0.10, 0.20):
        m, _ = agg("tiered", bias=b)
        red = full_h / m[1] if m[1] > 0 else float("inf")
        print(f"{b:>6.2f}{m[1]:>18.1f}{red:>19.1f}x{m[0]:>20.1f}")
        results[b] = {"tiered_harm": float(m[1]), "reduction_x": float(red),
                      "tiered_resolved": float(m[0])}
    results["full_harm"] = float(full_h)
    return results


if __name__ == "__main__":
    main()
