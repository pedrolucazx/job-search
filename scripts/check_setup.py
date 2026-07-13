#!/usr/bin/env python3
"""check_setup.py — environment doctor. Run this first if you're new here.

Checks every external dependency this pipeline needs and tells you exactly
what's missing and how to install it — instead of finding out midway
through /daily with a confusing shell error.

Usage:
  python3 scripts/check_setup.py
"""
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

CHECKS = [
    ("bun", "bun", "curl -fsSL https://bun.sh/install | bash", "runs the job search CLIs (linkedin-search, freehire-search)"),
    ("pdflatex", "pdflatex", "sudo apt install texlive-latex-base texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended texlive-fonts-extra", "compiles the CV .tex into a .pdf"),
    ("pdftotext", "pdftotext", "sudo apt install poppler-utils", "extracts text from the PDF for the ATS check"),
    ("pdfinfo", "pdfinfo", "sudo apt install poppler-utils", "confirms the CV is exactly 1 page"),
    ("jq", "jq", "sudo apt install jq", "reads fields out of daily/*/*.json without guessing filenames"),
]


def check_command(name, binary, install_hint, why):
    found = shutil.which(binary) is not None
    status = "✅" if found else "❌"
    print(f"{status} {name:<10} — {why}")
    if not found:
        print(f"   Install: {install_hint}")
    return found


def check_pyyaml():
    try:
        import yaml  # noqa: F401
        print(f"✅ {'PyYAML':<10} — parses profile/candidate.yaml")
        return True
    except ImportError:
        print(f"❌ {'PyYAML':<10} — parses profile/candidate.yaml")
        print("   Install: pip install pyyaml")
        return False


def check_profile():
    candidate = REPO_ROOT / "profile" / "candidate.yaml"
    example = REPO_ROOT / "profile" / "candidate.example.yaml"
    if candidate.exists():
        print(f"✅ {'profile':<10} — profile/candidate.yaml exists")
        return True
    print(f"⚠️  {'profile':<10} — profile/candidate.yaml doesn't exist yet")
    print(f"   Run: cp {example.relative_to(REPO_ROOT)} {candidate.relative_to(REPO_ROOT)}")
    print("   Then fill it in with your real data and run: python3 scripts/validate_profile.py")
    return False


def main():
    print("Checking your environment for the job search pipeline...\n")

    results = [check_pyyaml()]
    for name, binary, install_hint, why in CHECKS:
        results.append(check_command(name, binary, install_hint, why))

    print()
    profile_ok = check_profile()

    print()
    if all(results):
        print("✅ All dependencies installed.")
        if not profile_ok:
            print("   Just set up your profile (see above) and you're ready for /daily.")
        else:
            print("   You're ready for /daily.")
        sys.exit(0)
    else:
        missing = sum(1 for r in results if not r)
        print(f"❌ {missing} dependency/dependencies missing — install them above, then run this again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
