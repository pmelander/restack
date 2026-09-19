#!/usr/bin/env python3
"""Score impact-matrix cells with TypeSafe's Jev, one request per stressor.

The matrix is the one genuinely mechanical judgement in the stressor method: a
narrow, repeated yes/no about whether a stressor reaches an actor, made a few
hundred times. A decision model that returns a calibrated probability is a
better instrument for that than the same model that generated the stressors and
will read the result.

This script does the transport and nothing else. It decides no cells: it returns
probabilities, and the protocol in scripts/shared/jev-scoring.md decides what a
probability means, which band escalates, and what a failed row falls back to.

Standard library only: the script ships inside the skill and must run wherever
the skill is installed, with no install step of its own.

Scoring is optional and never a gate. Without TYPESAFE_API_KEY this script is
simply not run, and the matrix is built exactly as it always was.

Usage:
    jev_score.py --in request.json
    jev_score.py --in request.json --out matrix-2026-09-19.jev.json
    cat request.json | jev_score.py
    jev_score.py --in request.json --dry-run     # budget check, no network

Input JSON:
    {
      "path_map":  <string | object | array>,   the walked path map(s), TRIMMED
                                                to the actors on those paths
      "actors":    [ {"id": "order-service",
                      "name": "Order Service",
                      "description": "optional, one line"} ],
      "stressors": [ {"id": "s01",
                      "statement": "the stressor as the architect wrote it",
                      "source": "generated"} ]
    }

    Anonymise before you get here, if you are anonymising. Every name in
    "actors" and every word of "statement" leaves this machine.

Output JSON:
    {
      "model": "jev-1.13.0",
      "thresholds": {"high": 0.8, "low": 0.2},
      "requests": 30, "failed": 1,
      "rows": [
        {"stressor": "s01", "status": "ok", "model": "jev-1.13.0",
         "cells": {"order-service": 0.92, "auth": 0.04},
         "usage": {"input_tokens": 312, "output_tokens": 48}},
        {"stressor": "s02", "status": "failed",
         "reason": "HTTP 429 after one retry", "cells": {}}
      ]
    }

    A row with "status": "failed" carries no cells and is scored by the model
    instead. Never partially accept a row - a row scored half by Jev and half by
    the model, with no record of which half, makes the matrix's provenance line
    claim something untrue.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
import urllib.error
import urllib.request
from typing import Any

# --- the API shape -----------------------------------------------------------
# Pinned against the TypeSafe System One HTTP API as published at launch,
# September 2026 (https://docs.typesafe.ai/api, https://docs.typesafe.ai/models).
# Everything that would change if they moved the endpoint, renamed the envelope
# or shipped a new model lives in this one dict, so the edit is one place rather
# than a search through request-building code.
#
# The model is PINNED to a version rather than the "jev-latest" alias on
# TypeSafe's own advice: an alias moves when a release ships, and the 0.8/0.2
# bands in jev-scoring.md are thresholds tuned against this version's
# calibration. A silently-moved model would change scoring without changing
# anything in this repository, and ADR-014's validation would stop describing
# the model actually in use. Move this deliberately, and re-validate when you do.
JEV_API = {
    "endpoint": "https://api.typesafe.ai/v1/systemone",
    "auth_header": "Authorization",
    "auth_scheme": "Bearer",
    "model": "jev-1.13.0",          # alias "jev-latest" resolved here at launch
    "question_type": "noul",
    "answer_field": "noul",
    "request_state_key": "state",
    "request_model_key": "model",
    "request_questions_key": "questions",
    "response_answers_key": "answers",
    "response_model_key": "model",
    "response_usage_key": "usage",
}

ENV_KEY = "TYPESAFE_API_KEY"

# Context budgets for jev-1.13, from the Models page. These are two limits, not
# one, and conflating them is how you discover the real ceiling in production:
# a wide actor set trips BUDGET_ALL long before any single question approaches
# BUDGET_LONGEST.
BUDGET_ALL = 64_000        # state + every question in the request
BUDGET_LONGEST = 32_000    # state + the single longest question

# There is no tokenizer in the standard library, so the budget check is an
# ESTIMATE - roughly four characters per token - held back from the real ceiling
# so that an under-count does not become a 422. It refuses early rather than
# late, which is the right way round for a check whose job is to stop silent
# truncation.
CHARS_PER_TOKEN = 4
BUDGET_HEADROOM = 0.90

# "Affects", word for word from the matrix-construction section. The whole point
# of Jev scoring a cell is that it scores the SAME question the architect would;
# paraphrasing here would quietly make the two incomparable.
AFFECTS = (
    "fail, degrade materially, lose correctness, or propagate the damage onward"
)
CRITERION_TRUE = (
    "The actor fails, degrades materially, loses correctness, or propagates "
    "the damage onward."
)
CRITERION_FALSE = (
    "The actor is unaffected, or notices the stressor and handles it correctly."
)

RETRY_STATUSES = (429, 529)     # "later", so worth exactly one retry
RETRY_DELAY_S = 2.0
TIMEOUT_S = 60


class JevError(Exception):
    """Fatal: the whole matrix falls back to model scoring."""


class RowError(Exception):
    """This row falls back to model scoring; the rest of the matrix continues."""


def api_key() -> str:
    """The key, from the environment and nowhere else.

    Never a flag, never a file, never an argument: a key on the command line is
    a key in the shell history and in every process listing on the machine.
    """
    key = os.environ.get(ENV_KEY, "").strip()
    if not key:
        raise JevError(
            f"{ENV_KEY} is not set. This script is optional - score the matrix "
            f"with the model instead."
        )
    return key


def estimate_tokens(obj: Any) -> int:
    """Rough token count for a JSON-serialisable value. An estimate, not a measure."""
    text = obj if isinstance(obj, str) else json.dumps(obj, ensure_ascii=False)
    return math.ceil(len(text) / CHARS_PER_TOKEN)


def build_questions(actors: list[dict], stressor: dict) -> dict[str, dict]:
    """One noul per actor, each naming its actor in the instructions.

    The question id is how an answer finds its way back to a cell and nothing
    more - TypeSafe state that the key is not used in inference. So the actor
    has to be named in the instruction text; leave it implicit and every
    question in the request is identical, and the probabilities describe the
    path rather than the actor.
    """
    questions: dict[str, dict] = {}
    for actor in actors:
        label = actor.get("name") or actor["id"]
        detail = actor.get("description", "").strip()
        subject = f"`{label}`" + (f" ({detail})" if detail else "")
        questions[actor["id"]] = {
            "type": JEV_API["question_type"],
            "instructions": (
                f"Under the stressor described in the state, does {subject} "
                f"{AFFECTS}?"
            ),
            "criteria": {"true": CRITERION_TRUE, "false": CRITERION_FALSE},
        }
    return questions


def build_request(path_map: Any, actors: list[dict], stressor: dict) -> dict:
    """The request body for one stressor row."""
    return {
        JEV_API["request_state_key"]: {
            "stressor": stressor["statement"],
            "path_map": path_map,
        },
        JEV_API["request_model_key"]: JEV_API["model"],
        JEV_API["request_questions_key"]: build_questions(actors, stressor),
    }


def check_budget(body: dict, stressor_id: str) -> None:
    """Refuse an over-budget request rather than truncating it.

    Truncation is the failure worth engineering against here: a trimmed path map
    scores cells against a system missing its last three actors, produces a
    plausible column of zeros, and says nothing. Refusing is loud, and the
    honest fixes - split the actor set, or trim the state deliberately - are
    both available to whoever reads the error.
    """
    state_tokens = estimate_tokens(body[JEV_API["request_state_key"]])
    questions = body[JEV_API["request_questions_key"]]
    per_question = {qid: estimate_tokens(q) for qid, q in questions.items()}

    all_tokens = state_tokens + sum(per_question.values())
    if all_tokens > BUDGET_ALL * BUDGET_HEADROOM:
        raise JevError(
            f"stressor '{stressor_id}': estimated {all_tokens} tokens for state "
            f"plus {len(questions)} questions, over the {BUDGET_ALL} budget. "
            f"Split the actor set across two requests, or trim the path map to "
            f"fewer actors. Not truncating."
        )

    if per_question:
        longest_id = max(per_question, key=lambda q: per_question[q])
        longest = state_tokens + per_question[longest_id]
        if longest > BUDGET_LONGEST * BUDGET_HEADROOM:
            raise JevError(
                f"stressor '{stressor_id}': estimated {longest} tokens for state "
                f"plus the longest question ('{longest_id}'), over the "
                f"{BUDGET_LONGEST} budget. Trim the path map. Not truncating."
            )


def post(body: dict, key: str, show_error_body: bool) -> dict:
    """One POST, with a single retry on the two statuses that mean 'later'."""
    payload = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        JEV_API["endpoint"],
        data=payload,
        headers={
            JEV_API["auth_header"]: f"{JEV_API['auth_scheme']} {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    for attempt in (1, 2):
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT_S) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code in RETRY_STATUSES and attempt == 1:
                time.sleep(retry_after(exc))
                continue
            raise classify(exc, show_error_body) from None
        except urllib.error.URLError as exc:
            raise RowError(f"connection failed: {exc.reason}") from None
        except json.JSONDecodeError:
            raise RowError("response was not JSON") from None

    raise RowError("retry exhausted")


def retry_after(exc: urllib.error.HTTPError) -> float:
    header = exc.headers.get("retry-after") if exc.headers else None
    try:
        return min(float(header), 30.0) if header else RETRY_DELAY_S
    except (TypeError, ValueError):
        return RETRY_DELAY_S


def classify(exc: urllib.error.HTTPError, show_error_body: bool) -> Exception:
    """Turn an HTTP status into the right kind of failure.

    401 is fatal for the whole matrix - the key is wrong and the next 29
    requests will fail the same way. Everything else is this row's problem.

    The response body is withheld by default. A 422 body names the offending
    field, and that field's value may be a fragment of the path map; printing it
    would put state into a terminal, a CI log, or a pasted bug report. Pass
    --show-error-body when you are debugging the script against synthetic data.
    """
    detail = ""
    if show_error_body:
        try:
            detail = f": {exc.read().decode('utf-8', 'replace')[:400]}"
        except Exception:  # noqa: BLE001 - diagnostics must never mask the real error
            detail = ""
    elif exc.code == 422:
        detail = " (body withheld - it can quote the state; --show-error-body to see it)"

    if exc.code == 401:
        return JevError(f"HTTP 401: {ENV_KEY} was rejected. Not retrying.")
    if exc.code == 422:
        return RowError(f"HTTP 422: the request failed validation{detail}")
    if exc.code in RETRY_STATUSES:
        return RowError(f"HTTP {exc.code} after one retry")
    return RowError(f"HTTP {exc.code}{detail}")


def read_cells(response: dict, actors: list[dict]) -> dict[str, float]:
    """Pull one probability per actor, or reject the whole row.

    Strict on purpose. A row that is missing an actor, or carries an answer with
    no noul, or a noul outside 0..1, is a row whose provenance cannot honestly
    be recorded as `jev` - so it is not accepted at all.
    """
    answers = response.get(JEV_API["response_answers_key"])
    if not isinstance(answers, dict):
        raise RowError("response carried no answers map")

    cells: dict[str, float] = {}
    for actor in actors:
        answer = answers.get(actor["id"])
        if not isinstance(answer, dict):
            raise RowError(f"no answer for actor '{actor['id']}'")
        value = answer.get(JEV_API["answer_field"])
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise RowError(f"actor '{actor['id']}': no numeric "
                           f"'{JEV_API['answer_field']}' in the answer")
        if not 0.0 <= float(value) <= 1.0:
            raise RowError(f"actor '{actor['id']}': probability {value} outside 0..1")
        cells[actor["id"]] = float(value)
    return cells


def validate(document: dict) -> tuple[Any, list[dict], list[dict]]:
    for field in ("path_map", "actors", "stressors"):
        if field not in document:
            raise JevError(f"input is missing '{field}' - see --help for the shape")

    actors = document["actors"]
    stressors = document["stressors"]
    if not isinstance(actors, list) or not actors:
        raise JevError("'actors' must be a non-empty list")
    if not isinstance(stressors, list) or not stressors:
        raise JevError("'stressors' must be a non-empty list")

    seen: set[str] = set()
    for actor in actors:
        if not isinstance(actor, dict) or not actor.get("id"):
            raise JevError(f"every actor needs an 'id': {actor!r}")
        if actor["id"] in seen:
            raise JevError(f"duplicate actor id '{actor['id']}' - answers would collide")
        seen.add(actor["id"])

    for stressor in stressors:
        if not isinstance(stressor, dict) or not stressor.get("id"):
            raise JevError(f"every stressor needs an 'id': {stressor!r}")
        if not stressor.get("statement"):
            raise JevError(
                f"stressor '{stressor['id']}' has no 'statement'. Send the "
                f"stressor as the architect wrote it, not a label."
            )

    return document["path_map"], actors, stressors


def score(document: dict, dry_run: bool, show_error_body: bool) -> dict:
    path_map, actors, stressors = validate(document)
    key = "" if dry_run else api_key()

    rows: list[dict] = []
    requests = 0
    failed = 0

    for stressor in stressors:
        body = build_request(path_map, actors, stressor)
        row: dict[str, Any] = {"stressor": stressor["id"]}

        try:
            check_budget(body, stressor["id"])
            if dry_run:
                row.update(status="skipped", reason="--dry-run", cells={})
                rows.append(row)
                continue
            requests += 1
            response = post(body, key, show_error_body)
            row.update(
                status="ok",
                model=response.get(JEV_API["response_model_key"], JEV_API["model"]),
                cells=read_cells(response, actors),
                usage=response.get(JEV_API["response_usage_key"], {}),
            )
        except RowError as exc:
            failed += 1
            row.update(status="failed", reason=str(exc), cells={})
            print(f"  row '{stressor['id']}' falls back to model scoring: {exc}",
                  file=sys.stderr)

        rows.append(row)

    return {
        "model": JEV_API["model"],
        "endpoint": JEV_API["endpoint"],
        "thresholds": {"high": 0.8, "low": 0.2},
        "requests": requests,
        "failed": failed,
        "rows": rows,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--in", dest="infile", help="input JSON (default: stdin)")
    parser.add_argument("--out", help="write output JSON here (default: stdout)")
    parser.add_argument("--dry-run", action="store_true",
                        help="validate and check budgets; send nothing")
    parser.add_argument("--show-error-body", action="store_true",
                        help="print API error bodies, which can quote your state")
    args = parser.parse_args(argv)

    try:
        if args.infile:
            with open(args.infile, encoding="utf-8") as handle:
                raw = handle.read()
        else:
            raw = sys.stdin.read()
        document = json.loads(raw)
    except OSError as exc:
        print(f"error: cannot read input: {exc}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"error: input is not valid JSON: {exc}", file=sys.stderr)
        return 1

    try:
        result = score(document, args.dry_run, args.show_error_body)
    except JevError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    output = json.dumps(result, indent=2, ensure_ascii=False)
    if args.out:
        try:
            with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(output + "\n")
        except OSError as exc:
            print(f"error: cannot write {args.out}: {exc}", file=sys.stderr)
            return 1
        print(f"{result['requests']} request(s), {result['failed']} fell back "
              f"to model scoring -> {args.out}", file=sys.stderr)
    else:
        print(output)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
