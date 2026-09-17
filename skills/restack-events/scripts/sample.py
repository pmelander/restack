#!/usr/bin/env python3
"""Sample event-statement specs for use as stressors.

Randomness lives here, not in the model. Asked directly for "random events" an
LLM collapses onto a narrow mode - the same few regions, the same institutional
actors, the same register. Fixing the distribution combinatorially, before the
model sees anything, is the whole point of the two-stage design.

Standard library only: the sampler ships inside the skill and must run wherever
the skill is installed, with no install step of its own.

Usage:
    sample.py --n 30 --seed 41337
    sample.py --n 30 --seed 41337 --balance grounding,plausibility
    sample.py --n 30 --seed 41337 --out specs.jsonl
"""

from __future__ import annotations

import argparse
import itertools
import json
import random
import sys
from pathlib import Path

DEFAULT_TAXONOMY = Path(__file__).resolve().parent.parent / "reference" / "taxonomy.json"
DEFAULT_BALANCE = "grounding,plausibility"


class SamplerError(Exception):
    pass


def load_taxonomy(path: Path) -> dict:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SamplerError(f"taxonomy not found: {path}")
    except json.JSONDecodeError as exc:
        raise SamplerError(f"{path}: invalid JSON - {exc}")

    dims = raw.get("dimensions")
    if not dims:
        raise SamplerError(f"{path}: no 'dimensions' object")

    seen: list[str] = []
    for name, spec in dims.items():
        if "conditional_on" in spec:
            parent = spec["conditional_on"]
            if parent not in seen:
                raise SamplerError(
                    f"{path}: '{name}' is conditional on '{parent}', which must be "
                    f"declared before it - reorder the dimensions"
                )
            if not spec.get("by"):
                raise SamplerError(f"{path}: '{name}' is conditional but has no 'by' map")
            for parent_value, weights in spec["by"].items():
                _check_weights(path, f"{name}.by.{parent_value}", weights)
        else:
            _check_weights(path, name, spec.get("weights"))
        seen.append(name)
    return dims


def _check_weights(path: Path, label: str, weights) -> None:
    if not weights:
        raise SamplerError(f"{path}: '{label}' has no weights")
    for value, weight in weights.items():
        if not isinstance(weight, int) or weight <= 0:
            raise SamplerError(
                f"{path}: '{label}.{value}' weight must be a positive integer (got {weight!r})"
            )


def values_for(dims: dict, name: str, drawn: dict) -> dict:
    """The weight map in force for one dimension, given what is already drawn."""
    spec = dims[name]
    if "conditional_on" not in spec:
        return spec["weights"]
    parent_value = drawn[spec["conditional_on"]]
    weights = spec["by"].get(parent_value)
    if weights is None:
        raise SamplerError(
            f"'{name}' has no weights for {spec['conditional_on']}={parent_value!r}"
        )
    return weights


def weighted_choice(rng: random.Random, weights: dict) -> str:
    # Sorted keys, so a draw never depends on dict insertion order.
    keys = sorted(weights)
    return rng.choices(keys, weights=[weights[k] for k in keys], k=1)[0]


def balance_cells(dims: dict, balanced: list[str], n: int, rng: random.Random) -> list[dict]:
    """Assign the balanced dimensions round-robin over their product, then shuffle.

    Stratifying rather than drawing is what guarantees every batch carries blind
    draws as well as aimed ones. Left probabilistic, a batch of 30 can plausibly
    come back with two uncoupled specs, and the track that finds the cracks
    nobody was looking for is the one that goes missing.
    """
    axes = []
    for name in balanced:
        spec = dims[name]
        if "conditional_on" in spec:
            raise SamplerError(
                f"--balance cannot name '{name}': it is conditional on "
                f"'{spec['conditional_on']}' and has no single value set"
            )
        axes.append(sorted(spec["weights"]))

    cells = [dict(zip(balanced, combo)) for combo in itertools.product(*axes)]
    if n < len(cells):
        print(
            f"warning: --n {n} is smaller than the {len(cells)} "
            f"{' x '.join(balanced)} cells, so some will be empty",
            file=sys.stderr,
        )
    assigned = [dict(cells[i % len(cells)]) for i in range(n)]
    rng.shuffle(assigned)
    return assigned


def draw_spec(dims: dict, rng: random.Random, fixed: dict) -> dict:
    drawn: dict = {}
    for name in dims:
        if name in fixed:
            drawn[name] = fixed[name]
            continue
        drawn[name] = weighted_choice(rng, values_for(dims, name, drawn))
    return drawn


def sample(dims: dict, n: int, seed: int, balanced: list[str]) -> list[dict]:
    master = random.Random(seed)
    assigned = balance_cells(dims, balanced, n, master) if balanced else [{} for _ in range(n)]

    specs = []
    for i, fixed in enumerate(assigned):
        draw_seed = master.getrandbits(32)
        rng = random.Random(draw_seed)
        spec = {"id": f"s-{i:04d}", "seed": draw_seed}
        spec.update(draw_spec(dims, rng, fixed))

        # A coupled draw carries a second event arriving with the first.
        # Grounding and plausibility are inherited so the pair renders from one
        # brief; everything else is drawn again. How the two relate is not
        # supplied - working that out is the walk's job, not the generator's.
        if spec.get("correlation") == "coupled":
            inherited = {k: spec[k] for k in ("grounding", "plausibility") if k in spec}
            inherited["correlation"] = "isolated"
            second = draw_spec(dims, rng, inherited)
            spec["second"] = {k: v for k, v in second.items() if k not in inherited}
        specs.append(spec)
    return specs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Sample event-statement specs for use as stressors."
    )
    parser.add_argument("--n", type=int, default=20, help="number of specs (default 20)")
    parser.add_argument("--seed", type=int, required=True, help="batch seed")
    parser.add_argument("--taxonomy", type=Path, default=DEFAULT_TAXONOMY)
    parser.add_argument(
        "--balance",
        default=DEFAULT_BALANCE,
        help="comma-separated dimensions forced to even coverage "
             "(default 'grounding,plausibility'; pass an empty string to draw everything)",
    )
    parser.add_argument("--out", type=Path, help="write JSONL here instead of stdout")
    args = parser.parse_args(argv)

    if args.n < 1:
        print("error: --n must be at least 1", file=sys.stderr)
        return 2

    try:
        dims = load_taxonomy(args.taxonomy)
        balanced = [d.strip() for d in args.balance.split(",") if d.strip()]
        unknown = [d for d in balanced if d not in dims]
        if unknown:
            print(
                f"error: --balance names unknown dimension(s): {', '.join(unknown)}",
                file=sys.stderr,
            )
            return 2
        specs = sample(dims, args.n, args.seed, balanced)
    except SamplerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    lines = "".join(json.dumps(s, ensure_ascii=False) + "\n" for s in specs)
    if args.out:
        args.out.write_text(lines, encoding="utf-8", newline="\n")
        print(f"{len(specs)} specs -> {args.out}", file=sys.stderr)
    else:
        sys.stdout.write(lines)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
