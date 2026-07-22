# Recettes et production — gouvernance Excel

Ce dossier centralise la documentation et la méthode de travail pour contribuer au classeur **`Recettes et production - v18.xlsx`** (et versions dérivées : v19, etc.).

## Contenu

| Fichier | Rôle |
|---------|------|
| [[Description du classeur (base v18)]] | Vue d'ensemble détaillée du workbook, rôle de chaque onglet, flux de données |
| [[Analyse Recette Epice (base v18)]] | État des lieux technique de la feuille **Recette Epice** (défauts, risques) |
| [[Méthode de contribution Recette Epice]] | Procédure obligatoire avant / pendant / après toute modification |

## Portée

- **Cœur calculatoire** : `Recette Epice`, `Produit`, `Ingredients`, `Conditionnement`, `Concurrence`
- **Planification** : `Besoins plantes`, `Production`, `Planning Culture`, `Calendrier culture`
- **Utilitaires** : `Temporaire`, `Log`

## Objectif

Fiabiliser les contributions, éviter les régressions de formules et garder une structure cohérente entre les versions du fichier.

## Règle Cursor associée

`.cursor/rules/recette-epice-contribution.mdc` — impose le respect de la méthode de contribution lors de toute modification des fichiers `Recettes et production*.xlsx`.
