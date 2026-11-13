#!/usr/bin/env python3
"""outcome.py — the single owner of the documents/applications/*/outcome.md format.

compile-all.sh writes one of these when it archives an application, workflows/
confirm.md edits the Status line by hand, and build_dashboard.py reads them back
to derive each application's state. Keeping render() and parse() in one module
means renaming a stage breaks the tests instead of silently breaking the
dashboard.

Status vocabulary: STATES below is the one canonical lifecycle, shared by the
dashboard and analyze_outcomes.py. normalize() maps free text onto it, both the
Status line of an outcome.md (written by hand, in English or Portuguese) and the
Status select of the Notion tracker. Add an alias to ALIASES rather than teaching
a reader to substring-match.

Usage:
  python3 scripts/outcome.py --write documents/applications/<slug>
      writes <folder>/outcome.md from <folder>/metadata.json
      refuses (exit 1) if outcome.md already exists
  python3 scripts/outcome.py --write documents/applications/<slug> --force
      overwrites it, discarding any manual Status/stage edits
"""
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

STAGES = ["Phone screen", "Technical interview", "System design", "Final round", "Offer received"]
DEFAULT_STATUS = "waiting for send confirmation (run workflows/confirm.md)"
DISCARDED_STATUS = "Discarded"
DASH = "—"

# Lifecycle order. "unknown" is not a state, it's normalize()'s miss signal.
STATES = [
    "compiled",   # CV ready, not sent yet
    "applied",    # sent, no answer yet
    "screening",  # recruiter / cultural interview
    "technical",  # technical test or interview
    "offer",
    "hired",
    "rejected",
    "closed",     # position closed / posting removed by the company
    "frozen",     # process frozen by the company
    "ghosted",    # no answer for long enough to give up
    "withdrew",   # candidate gave up
    "discarded",  # CV generated but never sent
]
ADVANCED = {"screening", "technical", "offer", "hired"}
# A decision that came from the company. Not "withdrew" (candidate's own call)
# nor "frozen" (on hold, no verdict).
COMPANY_ANSWER = ADVANCED | {"rejected", "closed"}
ENDED = {"rejected", "closed", "ghosted", "withdrew"}
NOT_SENT = {"compiled", "discarded"}

# Substring match, first rule wins, so write the Status line starting with the
# state ("Applied — waiting", not "Waiting, no interview yet"). The more specific
# prefixes come first: "Discarded
# (rejected: ...)" is discarded, not rejected; "Applied (vaga congelada ...)" is
# frozen, not applied. Matched against lowercased, accent-free text.
ALIASES = [
    ("discarded", ("discarded", "not applied", "descartad")),
    ("compiled", ("waiting for send",)),
    ("hired", ("aceito", "hired", "contratad")),
    ("offer", ("offer", "oferta")),
    # Notion's "Referência para colega": the candidate passed it to a colleague.
    ("withdrew", ("desisti", "withdrew", "referencia para colega")),
    ("rejected", ("rejeitad", "rejected", "reprovad")),
    ("closed", ("posicao fechada", "position closed", "posting removed", "vaga finalizada")),
    ("frozen", ("congelad", "frozen")),
    ("ghosted", ("sumiu", "ghosted")),
    ("technical", ("teste tecnico", "technical")),
    ("screening", ("entrevista", "screening", "interview")),
    ("applied", ("applied", "aplicad")),
]


def normalize(status):
    text = unicodedata.normalize("NFKD", str(status or "")).encode("ascii", "ignore").decode().lower()
    for state, needles in ALIASES:
        if any(needle in text for needle in needles):
            return state
    return "unknown"


def render(record, status=None, stages_done=(), resolution="", notes=""):
    done = set(stages_done)
    lines = [
        f"# Outcome: {record.get('empresa', '')} {DASH} {record.get('cargo', '')}",
        "",
        f"**URL:** {record.get('url', '')} {DASH} submit the CV manually here",
        f"**Status:** {status or DEFAULT_STATUS}",
        f"**Compilation date:** {record.get('data', '')}",
        f"**Resolution date:** {resolution or DASH}",
        "",
        "## Interview stages reached",
    ]
    lines += [f"- [{'x' if stage in done else ' '}] {stage}" for stage in STAGES]
    lines += ["", "## Notes"]
    if notes:
        lines.append(notes.strip("\n"))
    return "\n".join(lines) + "\n"


def parse(text):
    status = re.search(r"\*\*Status:\*\*\s*(.+)", text)
    resolution = re.search(r"\*\*Resolution date:\*\*\s*(.+)", text)
    stages_done = [s for s in STAGES if re.search(r"- \[x\]\s*" + re.escape(s), text, re.I)]
    return {
        "status": status.group(1).strip() if status else "",
        "furthest": stages_done[-1] if stages_done else None,
        "resolution": (resolution.group(1).strip() if resolution else "").replace(DASH, "").strip(),
        "stages_done": stages_done,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Write an application's outcome.md from its metadata.json.")
    parser.add_argument("--write", required=True, metavar="FOLDER",
                        help="application folder holding metadata.json")
    parser.add_argument("--force", action="store_true",
                        help="overwrite an existing outcome.md, discarding manual status and stage edits")
    args = parser.parse_args(argv)

    folder = Path(args.write)
    metadata = folder / "metadata.json"
    target = folder / "outcome.md"

    if target.exists() and not args.force:
        print(f"refusing to overwrite {target} without --force", file=sys.stderr)
        return 1
    try:
        record = json.loads(metadata.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"cannot read {metadata}: {exc}", file=sys.stderr)
        return 1

    target.write_text(render(record), encoding="utf-8")
    print(target)
    return 0


if __name__ == "__main__":
    sys.exit(main())
