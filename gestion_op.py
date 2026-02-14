#!/usr/bin/env python3
"""Outil CLI de gestion des opportunités publiques (marchés et situations)."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from datetime import date
from pathlib import Path
from textwrap import dedent
from typing import Any

DEFAULT_DB = Path("marches_export_2026-02-14.json")


@dataclass
class Marche:
    id: str
    titre: str
    acheteur: str
    statut: str
    budget: str
    date_limite: str


@dataclass
class Situation:
    id: str
    marche_id: str
    action: str
    commentaire: str
    date: str


def color(text: str, code: str, enabled: bool) -> str:
    if not enabled:
        return text
    return f"\033[{code}m{text}\033[0m"


def load_db(path: Path) -> dict[str, list[dict[str, Any]]]:
    if not path.exists():
        return {"marches": [], "situations": []}
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return {"marches": [], "situations": []}
    data.setdefault("marches", [])
    data.setdefault("situations", [])
    return data


def save_db(path: Path, data: dict[str, list[dict[str, Any]]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def render_table(rows: list[dict[str, Any]], columns: list[str], use_color: bool = True) -> str:
    if not rows:
        return "(aucune donnée)"

    col_sizes = {c: len(c) for c in columns}
    for row in rows:
        for c in columns:
            col_sizes[c] = max(col_sizes[c], len(str(row.get(c, ""))))

    def hline(left: str, sep: str, right: str, fill: str = "─") -> str:
        return left + sep.join(fill * (col_sizes[c] + 2) for c in columns) + right

    top = hline("┌", "┬", "┐")
    mid = hline("├", "┼", "┤")
    bot = hline("└", "┴", "┘")

    header_cells = [f" {color(c, '1;36', use_color):<{col_sizes[c] + (9 if use_color else 0)}} " for c in columns]
    header = "│" + "│".join(header_cells) + "│"

    lines = [top, header, mid]
    for row in rows:
        body_cells = [f" {str(row.get(c, '')):<{col_sizes[c]}} " for c in columns]
        lines.append("│" + "│".join(body_cells) + "│")
    lines.append(bot)
    return "\n".join(lines)


def next_id(prefix: str, existing: list[dict[str, Any]]) -> str:
    numeric = []
    for item in existing:
        value = item.get("id", "")
        if value.startswith(prefix):
            suffix = value[len(prefix):]
            if suffix.isdigit():
                numeric.append(int(suffix))
    return f"{prefix}{max(numeric, default=0) + 1:03d}"


def cmd_add_marche(args: argparse.Namespace) -> None:
    db = load_db(args.db)
    mid = next_id("M", db["marches"])
    marche = Marche(
        id=mid,
        titre=args.titre,
        acheteur=args.acheteur,
        statut=args.statut,
        budget=args.budget,
        date_limite=args.date_limite,
    )
    db["marches"].append(asdict(marche))
    save_db(args.db, db)
    print(f"✅ Marché ajouté: {mid}")


def cmd_list_marches(args: argparse.Namespace) -> None:
    db = load_db(args.db)
    marches = db["marches"]
    if args.statut:
        marches = [m for m in marches if m.get("statut", "").lower() == args.statut.lower()]
    print(render_table(marches, ["id", "titre", "acheteur", "statut", "budget", "date_limite"], use_color=not args.no_color))


def cmd_add_situation(args: argparse.Namespace) -> None:
    db = load_db(args.db)
    if not any(m["id"] == args.marche_id for m in db["marches"]):
        raise SystemExit(f"Marché introuvable: {args.marche_id}")
    sid = next_id("S", db["situations"])
    situation = Situation(
        id=sid,
        marche_id=args.marche_id,
        action=args.action,
        commentaire=args.commentaire,
        date=args.date,
    )
    db["situations"].append(asdict(situation))
    save_db(args.db, db)
    print(f"✅ Situation ajoutée: {sid}")


def cmd_list_situations(args: argparse.Namespace) -> None:
    db = load_db(args.db)
    situations = db["situations"]
    if args.marche_id:
        situations = [s for s in situations if s.get("marche_id") == args.marche_id]
    print(render_table(situations, ["id", "marche_id", "action", "commentaire", "date"], use_color=not args.no_color))


def cmd_aide(_: argparse.Namespace) -> None:
    print(
        dedent(
            """
            Guide rapide:
              1) Ajouter un marché:
                 ./gestion_op.py marche add --titre "Accord-cadre IT" --acheteur "Ville de X"
              2) Lister les marchés:
                 ./gestion_op.py marche list
              3) Ajouter une situation:
                 ./gestion_op.py situation add --marche-id M001 --action "Relance" --commentaire "Email envoyé"

            Astuces d'utilisation:
              - Utilisez --db chemin/fichier.json pour travailler sur un autre export.
              - Utilisez --no-color si votre terminal gère mal les couleurs.
              - Filtrez vite avec --statut sur la liste des marchés.
            """
        ).strip()
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gestion_op.py",
        description="Gestion OP: outil terminal pour suivre marchés publics et situations commerciales.",
        epilog="Exemple: ./gestion_op.py marche add --titre 'Maintenance SI' --acheteur 'CHU Lyon'",
    )
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="Chemin du fichier JSON de stockage.")

    sub = parser.add_subparsers(dest="entity", required=True)

    marche = sub.add_parser("marche", help="Actions sur les marchés.")
    marche_sub = marche.add_subparsers(dest="action", required=True)

    marche_add = marche_sub.add_parser("add", help="Ajouter un marché.")
    marche_add.add_argument("--titre", required=True)
    marche_add.add_argument("--acheteur", required=True)
    marche_add.add_argument("--statut", default="à qualifier", help="Ex: à qualifier, en cours, attribué, perdu")
    marche_add.add_argument("--budget", default="n/a")
    marche_add.add_argument("--date-limite", default=str(date.today()))
    marche_add.set_defaults(func=cmd_add_marche)

    marche_list = marche_sub.add_parser("list", help="Afficher les marchés.")
    marche_list.add_argument("--statut", help="Filtrer par statut")
    marche_list.add_argument("--no-color", action="store_true", help="Désactiver les couleurs du tableau")
    marche_list.set_defaults(func=cmd_list_marches)

    situation = sub.add_parser("situation", help="Actions sur les situations.")
    situation_sub = situation.add_subparsers(dest="action", required=True)

    sit_add = situation_sub.add_parser("add", help="Ajouter une situation liée à un marché.")
    sit_add.add_argument("--marche-id", required=True)
    sit_add.add_argument("--action", required=True)
    sit_add.add_argument("--commentaire", default="")
    sit_add.add_argument("--date", default=str(date.today()))
    sit_add.set_defaults(func=cmd_add_situation)

    sit_list = situation_sub.add_parser("list", help="Afficher les situations.")
    sit_list.add_argument("--marche-id", help="Filtrer par identifiant marché")
    sit_list.add_argument("--no-color", action="store_true")
    sit_list.set_defaults(func=cmd_list_situations)

    aide = sub.add_parser("aide", help="Afficher un guide d'utilisation orienté métier.")
    aide.set_defaults(func=cmd_aide)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
