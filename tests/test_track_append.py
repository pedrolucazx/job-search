"""Tests for scripts/track_append.py — stdlib unittest only, zero deps.

Runs the script as a subprocess (matches how workflows/confirm.md actually
calls it) against a temp CSV file.

Run with: python3 -m unittest discover -s tests
"""
import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "track_append.py"


def run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True,
    )


class TestTrackAppend(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.csv_path = str(Path(self.tmpdir.name) / "applications.csv")

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_write_creates_file_with_header_and_row(self):
        result = run(
            "--path", self.csv_path,
            "--empresa", "Acme Corp", "--cargo", "Backend Engineer",
            "--url", "https://example.com/job", "--data", "2026-01-01",
            "--fonte", "LinkedIn", "--nivel", "Mid-level",
            "--stack", "Node.js,TypeScript", "--gaps", "AWS",
            "--versao-cv", "main_acme.tex", "--feedback", "gap in AWS",
        )
        self.assertEqual(result.returncode, 0, result.stderr)

        with open(self.csv_path, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["empresa"], "Acme Corp")
        self.assertEqual(rows[0]["status"], "Applied")
        self.assertEqual(rows[0]["stack"], "Node.js,TypeScript")

    def test_fields_with_commas_are_escaped_correctly(self):
        run(
            "--path", self.csv_path,
            "--empresa", "Comma, Inc.", "--cargo", "Dev, Senior",
            "--data", "2026-01-01",
        )
        with open(self.csv_path, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(rows[0]["empresa"], "Comma, Inc.")
        self.assertEqual(rows[0]["cargo"], "Dev, Senior")

    def test_check_duplicate_exits_zero_when_absent(self):
        result = run(
            "--check-duplicate", "--path", self.csv_path,
            "--empresa", "Nobody Yet", "--cargo", "x", "--data", "2026-01-01",
        )
        self.assertEqual(result.returncode, 0)

    def test_check_duplicate_exits_one_when_present(self):
        run(
            "--path", self.csv_path,
            "--empresa", "Already Here", "--cargo", "Dev", "--data", "2026-01-01",
        )
        result = run(
            "--check-duplicate", "--path", self.csv_path,
            "--empresa", "already here", "--cargo", "x", "--data", "2026-01-01",
        )
        self.assertEqual(result.returncode, 1)

    def test_second_write_appends_without_duplicate_header(self):
        run("--path", self.csv_path, "--empresa", "First", "--cargo", "A", "--data", "2026-01-01")
        run("--path", self.csv_path, "--empresa", "Second", "--cargo", "B", "--data", "2026-01-02")
        with open(self.csv_path, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 2)
        self.assertEqual([r["empresa"] for r in rows], ["First", "Second"])


if __name__ == "__main__":
    unittest.main()
