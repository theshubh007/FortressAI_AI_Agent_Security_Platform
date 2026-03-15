"""Adversarial containment demo: blast radius as a security primitive.

Run with:  python -m examples.containment_demo

Demonstrates the headline §IV adversarial result: under telemetry-manipulation
confidence poisoning, full autonomy's catastrophic (R5) harm explodes while the
tiered architecture holds R5 harm at exactly 0 -- because R5 is never-autonomous
in the reversibility envelope, no confidence inflation can promote it to
autonomous execution. main() returns the metrics dict.
"""
from tiered_autonomy.security import run_containment


def main():
    res = run_containment(poison_frac=1.0)
    print("=" * 70)
    print("CONTAINMENT DEMO -- full vs tiered under maximal confidence poisoning")
    print("(poison_frac=1.0; mean over 40 seeds; only reported confidence spoofed)")
    print("=" * 70)
    print(f"{'Policy':<16}{'Total harm/100':>18}{'R5 (catastrophic)':>20}")
    print(f"{'Full autonomy':<16}{res['full_total_harm']:>18.1f}"
          f"{res['full_r5_harm']:>20.1f}")
    print(f"{'Tiered (ours)':<16}{res['tiered_total_harm']:>18.1f}"
          f"{res['tiered_r5_harm']:>20.1f}")
    print()
    print(f"  Catastrophic R5 harm under tiered : {res['tiered_r5_harm']:.1f} "
          f"(contained = {res['tiered_r5_contained']})")
    print(f"  Catastrophic R5 harm under full   : {res['full_r5_harm']:.1f}")
    print(f"  Total harm reduction (full/tiered): "
          f"{res['total_harm_reduction_x']:.1f}x")
    return res


if __name__ == "__main__":
    main()
