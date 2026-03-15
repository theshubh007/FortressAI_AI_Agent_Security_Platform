"""Regenerate Table III of the paper (the §IV-B control-allocation comparison).

Run with:  python -m experiments.reproduce_table3

Delegates to :func:`tiered_autonomy.simulator.main`, which runs the four
allocation policies (full / advisory / global-gate / tiered) with agent
capability held FIXED and reports mean +/- 95% CI over 40 seeds. The
global-gate threshold is tuned so its resolution matches the tiered policy,
making the harm comparison an apples-to-apples control-allocation contrast.
"""
from tiered_autonomy.simulator import main

if __name__ == "__main__":
    main()
