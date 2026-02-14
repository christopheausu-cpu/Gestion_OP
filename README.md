# Gestion_OP

Gestion_OP est maintenant un **outil CLI prêt à l'emploi** pour suivre des marchés publics et les situations commerciales associées.

## Axes d'amélioration livrés

- **Facilité d'utilisation**
  - Commandes courtes et structurées (`marche add`, `marche list`, `situation add`, `situation list`).
  - Génération automatique des identifiants (`M001`, `S001`).
  - Valeurs par défaut utiles (`statut`, `date`, `budget`).
- **Aide utilisateur**
  - Aide native via `--help` à tous les niveaux.
  - Commande dédiée `aide` avec un guide métier rapide.
  - Exemples concrets de commandes dans cette documentation.
- **Rendu**
  - Affichage en tableau Unicode lisible.
  - Couleurs terminal (désactivables via `--no-color`).
  - Filtres de liste pour lecture ciblée.

## Prérequis

- Python 3.9+

## Commandes principales

```bash
# Aide générale
./gestion_op.py --help

# Ajouter un marché
./gestion_op.py marche add \
  --titre "Accord-cadre IT" \
  --acheteur "Ville de Nantes" \
  --statut "en cours" \
  --budget "120000 EUR" \
  --date-limite "2026-04-20"

# Lister les marchés
./gestion_op.py marche list

# Lister uniquement les marchés en cours
./gestion_op.py marche list --statut "en cours"

# Ajouter une situation
./gestion_op.py situation add \
  --marche-id M001 \
  --action "Relance" \
  --commentaire "Message envoyé au service achat"

# Lister les situations
./gestion_op.py situation list

# Guide rapide orienté utilisateur
./gestion_op.py aide
```

## Stockage des données

Par défaut, l'outil utilise le fichier :

- `marches_export_2026-02-14.json`

Vous pouvez changer de base avec :

```bash
./gestion_op.py --db mon_export.json marche list
```
