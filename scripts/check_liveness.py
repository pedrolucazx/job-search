#!/usr/bin/env python3
"""check_liveness.py — is this job posting still open? Run before writing a CV.

Adapted from career-ops' liveness-core.mjs (closure phrases), plus the two
signals measured on our own sources on 2026-11-13:
  - LinkedIn removes an expired job by redirecting /jobs/view/<id> to a search
    page with trk=expired_jd_redirect. The guest page itself never says
    "closed", so the redirect is the signal.
  - Gupy keeps the closed page up but embeds "status":"closed" in the job JSON
    ("published" while open).

Usage:
  python3 scripts/check_liveness.py <url> [<url> ...]
  python3 scripts/check_liveness.py --daily 2026-11-13     # every url in daily/<date>/*.json
Prints "<verdict>  <reason>  <url>" per job. Exit 2 if any is closed, else 0.
Verdicts: live, closed, uncertain (fetch failed; check by hand).
"""
import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"

CLOSED_TEXT = [re.compile(p, re.I) for p in (
    # from career-ops liveness-core.mjs
    r"job (?:is )?no longer available",
    r"no longer accepting applications",
    r"this (?:position|role|job) is no longer (?:available|accepting|open)",
    r"this (?:job|role|position)(?: listing)? is closed\b(?!-)",
    r"\b(?:job|position|role|posting|opening|vacancy)\b[\s\S]{0,60}?(?<!application )(?<!form )has been filled\b(?!\s+out)",
    r"\bsorry,? this job was removed\b",
    # Portuguese job boards
    # "esta/essa" is required: "a vaga preenchida por PCD..." is ordinary JD prose.
    r"n[ãa]o (?:est[áa] mais )?aceita(?:ndo)? mais candidaturas",
    r"(?:esta|essa) vaga (?:foi )?(?:encerrada|expirada|finalizada|preenchida)",
    r"(?:esta|essa) vaga n[ãa]o est[áa] mais dispon[íi]vel",
    r"(?:este|esse) processo seletivo (?:foi )?encerrado",
)]
GUPY_STATUS = re.compile(r'"status":"([a-z_]+)","code"')
NON_TEXT = re.compile(r"<(script|style)\b.*?</\1>", re.S | re.I)


def classify(http_status, final_url, text):
    if http_status in (404, 410):
        return "closed", f"HTTP {http_status}"
    if "expired_jd_redirect" in final_url:
        return "closed", "LinkedIn expired_jd_redirect"
    if http_status != 200:  # 999/429 anti-bot, 403, 5xx: nothing was actually checked
        return "uncertain", f"HTTP {http_status}"
    gupy = GUPY_STATUS.search(text)  # lives in a <script> JSON blob, so before stripping
    if gupy:
        status = gupy.group(1)
        if status == "published":
            return "live", "Gupy status published"
        if status in ("closed", "canceled", "frozen"):
            return "closed", f"Gupy status {status}"
        return "uncertain", f"Gupy status {status}"
    visible = NON_TEXT.sub(" ", text)
    for pattern in CLOSED_TEXT:
        match = pattern.search(visible)
        if match:
            return "closed", f'texto: "{match.group(0)[:60]}"'
    return "live", "nenhum sinal de encerramento"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, resp.geturl(), resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, url, ""


def check(url):
    if not url.startswith("http"):
        return "uncertain", "não é URL http (e-mail, post colado)"
    try:
        return classify(*fetch(url))
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        return "uncertain", f"falha ao buscar: {exc}"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("urls", nargs="*")
    ap.add_argument("--daily", help="check every url in daily/<date>/*.json")
    args = ap.parse_args(argv)
    urls = list(args.urls)
    if args.daily:
        for f in sorted((ROOT / "daily" / args.daily).glob("*.json")):
            url = json.loads(f.read_text(encoding="utf-8")).get("url")
            if url:
                urls.append(url)
    if not urls:
        ap.error("nenhuma URL")
    any_closed = False
    for url in urls:
        verdict, reason = check(url)
        any_closed |= verdict == "closed"
        print(f"{verdict:<9}  {reason}  {url}")
    return 2 if any_closed else 0


if __name__ == "__main__":
    sys.exit(main())
