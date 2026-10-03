#!/usr/bin/env python3
"""Tests for skills/restack-stressor/scripts/matrix.py (ADR-025).

The fixtures in tests/fixtures/matrix/ are two iterations of a synthetic
engagement and the residuals proposed between them, with the arithmetic known:

- iteration 1: 5 stressors × 4 actors, total 11, two unknown cells, one cluster
  (S-2 and S-4 hit RS and LC);
- iteration 2: two stressors added, NS removed, PR added; 4 cells cleared on
  the shared actors, 1 cell newly 1, 2 cells gone with NS;
- residuals: R1 is right; R2 states 3 cells and lists 4, claims a cell that
  was 0, shares S-1 × RS with R1, and claims a cell in the removed NS column;
- broken.md is scored on a scale; unfinished.md has margins nobody filled in.

The script must never change a score: only `totals --write` writes, and only
the margins.

    python -m unittest discover -s tests -v
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "skills" / "restack-stressor" / "scripts" / "matrix.py"
TRACE = ROOT / "skills" / "restack-trace" / "scripts" / "trace.py"
FIXTURES = ROOT / "tests" / "fixtures" / "matrix"


def run(*args: str) -> tuple[int, str]:
    done = subprocess.run([sys.executable, "-B", str(SCRIPT), *args], cwd=FIXTURES,
                          capture_output=True, timeout=60)
    return done.returncode, (done.stdout + done.stderr).decode("utf-8").replace("\r\n", "\n")


class Totals(unittest.TestCase):

    def test_consistent_matrix(self):
        code, out = run("totals", "matrix-iter1.md")
        self.assertEqual(code, 0, out)
        self.assertIn("5 stressors × 4 actors, total system impact 11 (2 unknown cells counted as 1)", out)
        self.assertIn("S-5 × LC, S-5 × NS", out)
        self.assertNotIn("Margins", out)

    def test_reading_aids(self):
        out = run("totals", "matrix-iter1.md")[1]
        self.assertIn("1. Concentration: RS 4, LC 3, CA 2 carry 82% of the total", out)
        self.assertIn("- S-2, S-4 → LC, RS", out)
        self.assertIn("3. Flatness:", out)
        self.assertIn("4. Zero columns: none", out)

    def test_severity_scale_and_wrong_margins(self):
        code, out = run("totals", "broken.md")
        self.assertEqual(code, 1)
        self.assertIn("line 5: 1 × Locker = 2", out)
        self.assertIn("line 6: 2 cells sum to 1, the row says 2", out)
        self.assertIn("no totals row", out)

    def test_write_fills_the_margins_and_changes_no_score(self):
        tmp = Path(tempfile.mkdtemp(prefix="restack-matrix-"))
        try:
            target = tmp / "unfinished.md"
            shutil.copy(FIXTURES / "unfinished.md", target)
            before = target.read_text(encoding="utf-8")
            code, out = run("totals", str(target), "--write")
            self.assertIn("No score was changed", out)
            after = target.read_text(encoding="utf-8")
            self.assertIn("| 1 | Courier strike | 1 | 1 | **2** |", after)
            self.assertIn("| 2 | Heatwave | 0 | 1 | 1 |", after)
            self.assertIn("| **Total** |  | **1** | **3** | **4** |", after)
            for row in ("| 1 | Courier strike | 1 | 1 |", "| 3 | Vandalism | · | 1? |"):
                self.assertIn(row, before)
                self.assertIn(row, after)
            self.assertEqual(run("totals", str(target))[0], 0)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_write_refuses_a_non_binary_matrix(self):
        tmp = Path(tempfile.mkdtemp(prefix="restack-matrix-"))
        try:
            target = tmp / "broken.md"
            shutil.copy(FIXTURES / "broken.md", target)
            out = run("totals", str(target), "--write")[1]
            self.assertIn("Not written", out)
            self.assertEqual(target.read_bytes(), (FIXTURES / "broken.md").read_bytes())
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class Compare(unittest.TestCase):

    def setUp(self):
        self.code, self.out = run("compare", "matrix-iter1.md", "matrix-iter2.md")

    def test_both_totals(self):
        self.assertIn("Stressor set: 5 shared, 2 added (S-6, S-7)", self.out)
        self.assertIn("Total against the shared stressor set: 11 → 7 (-4)", self.out)
        self.assertIn("on the actors in both, 9 → 6 (-3)", self.out)
        self.assertIn("Total against the expanded set: 11 (the 2 added stressors carry 4)", self.out)

    def test_per_actor_table(self):
        for row in ("| RS | 4 | 1 | -3 |", "| CA | 2 | 3 | +1 |", "| NS (removed) | 2 | — | -2 |",
                    "| PR (added) | — | 1 | +1 |", "| **Total** | **11** | **7** | **-4** |"):
            self.assertIn(row, self.out)

    def test_cells_cleared_raised_and_gone(self):
        self.assertIn("(4): S-1 × RS, S-2 × RS, S-4 × RS, S-5 × LC", self.out)
        self.assertIn("Cells that left with a removed actor (2)", self.out)
        self.assertIn("became 1 on shared stressors (1), worth a look: S-3 × CA", self.out)
        self.assertEqual(self.code, 1)


class Claims(unittest.TestCase):

    def test_claims_before_and_after(self):
        code, out = run("claims", "residuals-iter1.md", "matrix-iter1.md", "--after", "matrix-iter2.md")
        self.assertEqual(code, 1)
        self.assertIn("R1 (Event-sourced reservations): claims 3 cell(s) (1 outside the cluster)\n"
                      "  - every claimed cell is 0 in matrix-iter2.md", out)
        self.assertIn("R2 (Depot battery backup): claims 4 cell(s); the text says 3, the list has 4", out)
        self.assertIn("claimed but not 1 before the residual (nothing to clear): S-3 × CA", out)
        self.assertIn("still 1 in matrix-iter2.md: S-3 × CA", out)
        self.assertIn("Distinct cells claimed across residuals: 6 (7 listed, 1 claimed by more than one)", out)
        self.assertIn("S-1 × RS: R1, R2", out)

    def test_claims_before_only(self):
        code, out = run("claims", "residuals-iter1.md", "matrix-iter1.md")
        self.assertNotIn("still 1", out)
        self.assertIn("nothing to clear): S-3 × CA", out)

    def test_cleared_with_no_claim(self):
        tmp = Path(tempfile.mkdtemp(prefix="restack-matrix-"))
        try:
            text = (FIXTURES / "residuals-iter1.md").read_text(encoding="utf-8")
            (tmp / "r.md").write_text(text.replace("- S-5: LC, NS.\n", ""), encoding="utf-8")
            out = run("claims", str(tmp / "r.md"), "matrix-iter1.md", "--after", "matrix-iter2.md")[1]
            self.assertIn("Cleared with no residual claiming them (1): S-5 × LC", out)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_removed_actor_is_named_not_counted_as_cleared(self):
        tmp = Path(tempfile.mkdtemp(prefix="restack-matrix-"))
        try:
            text = (FIXTURES / "residuals-iter1.md").read_text(encoding="utf-8")
            (tmp / "r.md").write_text(text.replace("- S-3: CA.\n", "").replace("- S-1: RS.\n", "")
                                      .replace("**Clears 3 cells:**\n- S-5", "**Clears 2 cells:**\n- S-5"),
                                      encoding="utf-8")
            out = run("claims", str(tmp / "r.md"), "matrix-iter1.md", "--after", "matrix-iter2.md")[1]
            self.assertIn("except 1 whose actor was removed: S-5 × NS", out)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class Usage(unittest.TestCase):

    def test_errors_exit_two(self):
        self.assertEqual(run("totals", "missing.md")[0], 2)
        self.assertEqual(run("totals", "residuals-iter1.md")[0], 2)      # no matrix in it
        self.assertEqual(run("claims", "matrix-iter1.md", "matrix-iter1.md")[0], 2)
        self.assertEqual(run("bogus")[0], 2)

    def test_trace_agrees_on_unknown_cells(self):
        # trace 1.0.3 counts a bare `?` as 1, as the method and matrix.py do.
        tmp = Path(tempfile.mkdtemp(prefix="restack-matrix-"))
        try:
            docs = tmp / "docs" / "stressor-analysis"
            docs.mkdir(parents=True)
            shutil.copy(FIXTURES / "matrix-iter1.md", docs / "matrix-iter1.md")
            done = subprocess.run([sys.executable, "-B", str(TRACE), str(tmp / "docs"), "--only", "MX"],
                                  capture_output=True, timeout=60)
            self.assertEqual(done.returncode, 0, done.stdout.decode("utf-8", "replace"))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
