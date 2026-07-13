#!/usr/bin/env python3
"""validate_profile.py — loads and validates profile/candidate.yaml.

Zero external dependency besides PyYAML (pre-installed on most Python
distros/images; otherwise: pip install pyyaml).

Usage:
  python3 scripts/validate_profile.py                  # validate and print summary
  python3 scripts/validate_profile.py --get personal.email
  python3 scripts/validate_profile.py --path other/candidate.yaml
"""
import sys
import argparse
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not found. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

REQUIRED_TOP_LEVEL = [
    "profile_version", "personal", "education", "languages",
    "skills", "professional_experience", "soft_skills", "preferences", "tracker",
]
REQUIRED_PERSONAL = ["name", "email", "phone", "location"]
VALID_TRACKER_BACKENDS = ["csv", "notion", "none"]

# Values shipped in profile/candidate.example.yaml. If any of these are still
# present, the dev copied the template but never actually edited it — this
# must hard-block, not just warn, because plenty of people never read setup
# instructions and would otherwise ship a CV with someone else's contact info.
PLACEHOLDER_NAME = "Alex Devsson"
PLACEHOLDER_EMAIL_DOMAIN = "@example.com"
PLACEHOLDER_HANDLES = ["alexdevsson"]


def load_profile(path: Path) -> dict:
    if not path.exists():
        print(f"ERROR: {path} does not exist. Copy profile/candidate.example.yaml and fill it in.", file=sys.stderr)
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        print(f"ERROR: {path} did not parse as a valid YAML map.", file=sys.stderr)
        sys.exit(1)
    return data


def validate(data: dict) -> list[str]:
    errors = []

    for key in REQUIRED_TOP_LEVEL:
        if key not in data:
            errors.append(f"missing required field: {key}")

    personal = data.get("personal", {})
    for key in REQUIRED_PERSONAL:
        if not personal.get(key):
            errors.append(f"personal.{key} is missing or empty")

    email = str(personal.get("email", ""))
    if email.lower().endswith(PLACEHOLDER_EMAIL_DOMAIN):
        errors.append(
            f"personal.email ({email}) is still the example profile's placeholder — "
            "this file is YOUR data, not the template's. Put your real email in profile/candidate.yaml."
        )
    if personal.get("name") == PLACEHOLDER_NAME:
        errors.append(
            f"personal.name is still '{PLACEHOLDER_NAME}', the example profile's placeholder name — "
            "put your real name in profile/candidate.yaml."
        )
    for field in ("linkedin", "github", "portfolio"):
        value = str(personal.get(field, "")).lower()
        if any(handle in value for handle in PLACEHOLDER_HANDLES):
            errors.append(
                f"personal.{field} ({personal.get(field)}) still points to the example profile's "
                "placeholder handle — replace it with your own."
            )

    if not data.get("soft_skills"):
        errors.append("soft_skills is empty — needs at least 1 (recommended: exactly 6)")
    else:
        for i, s in enumerate(data["soft_skills"]):
            if not s.get("pt") or not s.get("en"):
                errors.append(f"soft_skills[{i}] needs 'pt' and 'en' (bilingual format)")

    if not data.get("professional_experience") and not data.get("personal_projects"):
        errors.append("neither professional_experience nor personal_projects is filled in — the CV would be empty")

    tracker = data.get("tracker", {})
    backend = tracker.get("backend")
    if backend not in VALID_TRACKER_BACKENDS:
        errors.append(f"invalid tracker.backend: {backend!r} (expected: {VALID_TRACKER_BACKENDS})")
    elif backend == "notion":
        notion = tracker.get("notion", {})
        if not notion.get("database_id") or not notion.get("data_source_id"):
            errors.append("tracker.backend=notion but notion.database_id/data_source_id is missing")
    elif backend == "csv":
        if not tracker.get("csv", {}).get("path"):
            errors.append("tracker.backend=csv but tracker.csv.path is missing")

    for i, proj in enumerate(data.get("personal_projects", [])):
        if not proj.get("link") and not proj.get("include_only_if"):
            # empty link is acceptable (unconfirmed repo), just a no-op check
            pass

    return errors


def get_field(data: dict, dotted_path: str):
    node = data
    for part in dotted_path.split("."):
        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            return None
    return node


def summarize(data: dict) -> str:
    personal = data.get("personal", {})
    n_exp = len(data.get("professional_experience", []))
    n_proj = len(data.get("personal_projects", []))
    n_skills = sum(len(v) for v in data.get("skills", {}).values())
    tracker_backend = data.get("tracker", {}).get("backend", "?")
    return (
        f"Profile: {personal.get('name', '?')} <{personal.get('email', '?')}>\n"
        f"Track: {data.get('track', '?')}\n"
        f"Professional experiences: {n_exp} | Personal projects: {n_proj}\n"
        f"Skills catalogued: {n_skills}\n"
        f"Tracker backend: {tracker_backend}\n"
        f"Deal breakers: {data.get('preferences', {}).get('deal_breakers', [])}"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", default=str(Path(__file__).resolve().parent.parent / "profile" / "candidate.yaml"))
    parser.add_argument("--get", help="dotted path of the field to extract, e.g. personal.email")
    args = parser.parse_args()

    data = load_profile(Path(args.path))

    if args.get:
        value = get_field(data, args.get)
        if value is None:
            print(f"ERROR: field '{args.get}' not found", file=sys.stderr)
            sys.exit(1)
        if isinstance(value, (list, dict)):
            print(yaml.safe_dump(value, allow_unicode=True, sort_keys=False).strip())
        else:
            print(value)
        return

    errors = validate(data)
    if errors:
        print(f"❌ {len(errors)} problem(s) in {args.path}:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    print(f"✅ Valid profile: {args.path}\n")
    print(summarize(data))


if __name__ == "__main__":
    main()
