#!/usr/bin/env python3
"""validate_profile.py — carrega e valida profile/candidate.yaml.

Zero dependência externa além de PyYAML (pré-instalado na maioria das
distros/imagens Python; senão: pip install pyyaml).

Uso:
  python3 scripts/validate_profile.py                  # valida e imprime resumo
  python3 scripts/validate_profile.py --get personal.email
  python3 scripts/validate_profile.py --path outro/candidate.yaml
"""
import sys
import argparse
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERRO: PyYAML não encontrado. Instale com: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

REQUIRED_TOP_LEVEL = [
    "profile_version", "personal", "education", "languages",
    "skills", "professional_experience", "soft_skills", "preferences", "tracker",
]
REQUIRED_PERSONAL = ["name", "email", "phone", "location"]
VALID_TRACKER_BACKENDS = ["csv", "notion", "none"]


def load_profile(path: Path) -> dict:
    if not path.exists():
        print(f"ERRO: {path} não existe. Copie profile/candidate.example.yaml e preencha.", file=sys.stderr)
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        print(f"ERRO: {path} não parseou como um mapa YAML válido.", file=sys.stderr)
        sys.exit(1)
    return data


def validate(data: dict) -> list[str]:
    errors = []

    for key in REQUIRED_TOP_LEVEL:
        if key not in data:
            errors.append(f"campo obrigatório ausente: {key}")

    personal = data.get("personal", {})
    for key in REQUIRED_PERSONAL:
        if not personal.get(key):
            errors.append(f"personal.{key} ausente ou vazio")

    if not data.get("soft_skills"):
        errors.append("soft_skills vazio — precisa de ao menos 1 (recomendado: exatamente 6)")
    else:
        for i, s in enumerate(data["soft_skills"]):
            if not s.get("pt") or not s.get("en"):
                errors.append(f"soft_skills[{i}] precisa de 'pt' e 'en' (formato bilíngue)")

    if not data.get("professional_experience") and not data.get("personal_projects"):
        errors.append("nem professional_experience nem personal_projects preenchidos — CV ficaria vazio")

    tracker = data.get("tracker", {})
    backend = tracker.get("backend")
    if backend not in VALID_TRACKER_BACKENDS:
        errors.append(f"tracker.backend inválido: {backend!r} (esperado: {VALID_TRACKER_BACKENDS})")
    elif backend == "notion":
        notion = tracker.get("notion", {})
        if not notion.get("database_id") or not notion.get("data_source_id"):
            errors.append("tracker.backend=notion mas notion.database_id/data_source_id ausentes")
    elif backend == "csv":
        if not tracker.get("csv", {}).get("path"):
            errors.append("tracker.backend=csv mas tracker.csv.path ausente")

    for i, proj in enumerate(data.get("personal_projects", [])):
        if not proj.get("link") and not proj.get("include_only_if"):
            # link vazio é aceitável (repo não confirmado), só avisa
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
        f"Experiências profissionais: {n_exp} | Projetos pessoais: {n_proj}\n"
        f"Skills catalogadas: {n_skills}\n"
        f"Tracker backend: {tracker_backend}\n"
        f"Deal breakers: {data.get('preferences', {}).get('deal_breakers', [])}"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", default=str(Path(__file__).resolve().parent.parent / "profile" / "candidate.yaml"))
    parser.add_argument("--get", help="dotted path do campo a extrair, ex: personal.email")
    args = parser.parse_args()

    data = load_profile(Path(args.path))

    if args.get:
        value = get_field(data, args.get)
        if value is None:
            print(f"ERRO: campo '{args.get}' não encontrado", file=sys.stderr)
            sys.exit(1)
        if isinstance(value, (list, dict)):
            print(yaml.safe_dump(value, allow_unicode=True, sort_keys=False).strip())
        else:
            print(value)
        return

    errors = validate(data)
    if errors:
        print(f"❌ {len(errors)} problema(s) em {args.path}:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    print(f"✅ Profile válido: {args.path}\n")
    print(summarize(data))


if __name__ == "__main__":
    main()
