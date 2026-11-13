#!/usr/bin/env python3
"""inhire_search.py — remote jobs from InHire career pages, in the linkedin-search JSON shape.

InHire has no central job board like Gupy's (vagas.inhire.app is just a
tenant lookup that answers "company not found"). Each company has its own
<tenant>.inhire.app, served by a public API that works outside a browser as
long as the tenant goes in the X-Tenant header:

  GET https://api.inhire.app/job-posts/public/pages          -> jobsPage list
  GET https://api.inhire.app/job-posts/public/pages/<jobId>  -> full posting

The list carries workplaceType (Remote/Hybrid/On-site); the detail carries
the description and publishedAt. So the only unknown is which tenants exist:
the list is documents/inhire_tenants.txt plus every *.inhire.app seen in our
own history (daily/*.json, documents/applications/*/metadata.json), and new
ones found in history are appended to the file, so it grows by itself.

Usage:
  python3 scripts/inhire_search.py              # 14 days
  python3 scripts/inhire_search.py --days 7 --tenant radix --tenant db1
Prints {"meta": {...}, "results": [{id, title, company, location, date, url,
workplaceType, description, source}]}.
"""
import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gupy_search import above_ceiling, plain

ROOT = Path(__file__).resolve().parent.parent
TENANTS_FILE = ROOT / "documents" / "inhire_tenants.txt"
API = "https://api.inhire.app/job-posts/public/pages"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
DEV_TITLE = re.compile(r"desenvolv|\bdev\b|developer|engenheir|engineer|programador|full ?stack|back-?end|front-?end|"
                       r"software", re.I)
TENANT_IN_TEXT = re.compile(r"\b([a-z0-9-]+)\.inhire\.app\b")
NOT_TENANTS = {"api", "files", "vagas", "www", "ses-mail", "app"}


def known_tenants(tenants_file=TENANTS_FILE, root=ROOT):
    """Tenants from the file plus any seen in our history; new ones are saved back."""
    listed = set(tenants_file.read_text(encoding="utf-8").split()) if tenants_file.exists() else set()
    seen = set()
    for path in list(root.glob("daily/*/*.json")) + list(root.glob("documents/applications/*/metadata.json")):
        try:
            seen |= set(TENANT_IN_TEXT.findall(path.read_text(encoding="utf-8")))
        except OSError:
            continue
    tenants = (listed | seen) - NOT_TENANTS
    if tenants != listed and tenants_file.parent.exists():
        tenants_file.write_text("\n".join(sorted(tenants)) + "\n", encoding="utf-8")
    return sorted(tenants)


def _get(url, tenant, opener=urllib.request.urlopen):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "X-Tenant": tenant})
    with opener(req, timeout=20) as resp:
        return json.load(resp)


def candidate_jobs(page):
    """Remote dev postings within the title ceiling, from a tenant's list."""
    return [j for j in page.get("jobsPage", [])
            if j.get("status") == "published" and j.get("workplaceType") == "Remote"
            and DEV_TITLE.search(j.get("displayName") or "") and not above_ceiling(j.get("displayName") or "")]


def to_result(tenant, detail):
    title = " ".join(re.sub(r"[^\w\s|/()+.,&#-]", " ", detail.get("displayName") or "").split()).strip(" |")
    return {
        "id": detail["jobId"],
        "title": title,
        "company": detail.get("tenantName") or tenant,
        "location": detail.get("location") or "Brasil",
        "date": (detail.get("publishedAt") or detail.get("lastPublishedAt") or "")[:10],
        # Any slug works after the id; without one the page says "invalid link".
        "url": f"https://{tenant}.inhire.app/vagas/{detail['jobId']}/vaga",
        "workplaceType": "remote",
        "description": plain(detail.get("description")),
        "source": "inhire",
    }


def search(tenants, days, today=None, get=_get):
    since = ((today or date.today()) - timedelta(days=days)).isoformat()
    results, failed, scanned = [], [], 0
    for tenant in tenants:
        try:
            page = get(API, tenant)
            scanned += len(page.get("jobsPage", []))
            for job in candidate_jobs(page):
                result = to_result(tenant, get(f"{API}/{job['jobId']}", tenant))
                if result["date"] >= since:
                    results.append(result)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError) as exc:
            failed.append(tenant)  # one company down must not cost the others
            print(f"InHire: {tenant} falhou ({exc}), seguindo", file=sys.stderr)
    results.sort(key=lambda r: r["date"], reverse=True)
    return {"meta": {"source": "inhire", "tenants": len(tenants), "days": days, "scanned": scanned,
                     "count": len(results), "failed_tenants": failed}, "results": results}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tenant", action="append", help="only these tenants (repeatable)")
    ap.add_argument("--days", type=int, default=14)
    args = ap.parse_args(argv)
    tenants = args.tenant or known_tenants()
    out = search(tenants, args.days)
    if out["meta"]["failed_tenants"] and len(out["meta"]["failed_tenants"]) == len(tenants):
        print("InHire indisponível: todas as empresas falharam.", file=sys.stderr)
        return 1
    json.dump(out, sys.stdout, ensure_ascii=False, indent=1)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
