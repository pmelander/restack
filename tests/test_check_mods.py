#!/usr/bin/env python3
"""Tests for scripts/check_mods.py's reading of `claude plugin validate` (ADR-029).

The check itself needs the Claude Code CLI and runs in CI. What it reads from
the report is plain text, and that reading is tested here: a contract check
that misreads its input either cries wolf or lets a call through.

    python -m unittest discover -s tests -v
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("check_mods", ROOT / "scripts" / "check_mods.py")
check_mods = importlib.util.module_from_spec(spec)
sys.modules["check_mods"] = check_mods
spec.loader.exec_module(check_mods)


class Listed(unittest.TestCase):

    def test_a_call_reached_through_two_functions_is_one_call(self):
        # The line that broke the first version: the comma inside `(via ...)`.
        line = "./register.tsx calls: $.clock.now, $.fs.read (via matrixState, readOnce), $.ui.open"
        self.assertEqual(check_mods.listed([line], "calls"), ["$.clock.now", "$.fs.read", "$.ui.open"])

    def test_hooks_keep_their_filters(self):
        line = "./register.tsx hooks: session.start, ui.render{component=Pane}, command.run{command=x}"
        self.assertEqual(check_mods.listed([line], "hooks"),
                         ["session.start", "ui.render{component=Pane}", "command.run{command=x}"])

    def test_other_labels_are_not_read(self):
        lines = ["./register.tsx state reads: restack-view.view", "./register.tsx calls: $.ui.toast"]
        self.assertEqual(check_mods.listed(lines, "calls"), ["$.ui.toast"])
        self.assertEqual(check_mods.listed(lines, "env reads"), [])

    def test_every_allowed_call_passes_and_a_write_does_not(self):
        allowed = [c for c in sorted(check_mods.ALLOWED_CALLS)] + ["$.ui.anything"]
        for call in allowed:
            self.assertTrue(call in check_mods.ALLOWED_CALLS or call.startswith(check_mods.ALLOWED_PREFIXES), call)
        for call in ("$.fs.write", "$.process.run", "$.http.fetch", "$.prompt.submit", "$.env.get"):
            self.assertFalse(call in check_mods.ALLOWED_CALLS or call.startswith(check_mods.ALLOWED_PREFIXES), call)


if __name__ == "__main__":
    unittest.main()
