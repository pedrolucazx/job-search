#!/usr/bin/env python3
"""check_setup.py — environment doctor. Run this first if you're new here.

Checks every external dependency this pipeline needs and tells you exactly
what's missing and how to install it — instead of finding out midway
through /daily with a confusing shell error.

Usage:
  python3 scripts/check_setup.py
  python3 scripts/check_setup.py --install
  python3 scripts/check_setup.py --no-prompt
"""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INSTALL_SCRIPT = REPO_ROOT / "scripts" / "install-dependencies.sh"

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


def check_dependencies():
    results = [check_pyyaml()]
    for name, binary, install_hint, why in CHECKS:
        results.append(check_command(name, binary, install_hint, why))
    return results


def should_offer_install(no_prompt=False):
    return not no_prompt and sys.stdin.isatty()


def ask_to_install():
    try:
        answer = input("\nInstall all missing dependencies now? [y/N] ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return False
    return answer in {"y", "yes"}


def run_installer():
    if not INSTALL_SCRIPT.exists():
        print(f"❌ Installer not found: {INSTALL_SCRIPT.relative_to(REPO_ROOT)}")
        return False

    print(f"\nRunning {INSTALL_SCRIPT.relative_to(REPO_ROOT)}...\n")
    completed = subprocess.run([str(INSTALL_SCRIPT)], cwd=REPO_ROOT, check=False)

    # Bun's installer updates shell startup files, but it cannot update this
    # already-running Python process. Add its default bin directory so the
    # immediate post-install recheck can still find it.
    bun_bin = Path.home() / ".bun" / "bin"
    if bun_bin.is_dir():
        os.environ["PATH"] = f"{bun_bin}{os.pathsep}{os.environ.get('PATH', '')}"

    return completed.returncode == 0


def print_summary(results, profile_ok):
    if all(results):
        print("✅ All dependencies installed.")
        if not profile_ok:
            print("   Just set up your profile (see above) and you're ready for /daily.")
        else:
            print("   You're ready for /daily.")
        return 0

    missing = sum(1 for result in results if not result)
    print(f"❌ {missing} dependency/dependencies missing.")
    return 1


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Check the job-search environment and optionally install missing dependencies."
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help="install missing dependencies without asking first",
    )
    parser.add_argument(
        "--no-prompt",
        action="store_true",
        help="only report the environment status; never offer installation",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    print("Checking your environment for the job search pipeline...\n")

    results = check_dependencies()

    print()
    profile_ok = check_profile()

    print()
    status = print_summary(results, profile_ok)
    if status == 0:
        return 0

    wants_install = args.install
    if not wants_install and should_offer_install(args.no_prompt):
        wants_install = ask_to_install()

    if not wants_install:
        print("   Run again with --install to install everything now.")
        return status

    if not run_installer():
        print("\n❌ Installation did not complete. Review the error above, then run this check again.")
        return 1

    print("\nRechecking your environment...\n")
    results = check_dependencies()
    print()
    profile_ok = check_profile()
    print()
    return print_summary(results, profile_ok)


if __name__ == "__main__":
    sys.exit(main())
