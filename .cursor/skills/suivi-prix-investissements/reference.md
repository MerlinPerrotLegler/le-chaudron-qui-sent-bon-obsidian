# Référence — schéma des fiches & requêtes Dataview

## Schéma de frontmatter d'une fiche d'achat

Champs interrogés par le tableau de bord Dataview. Respecter les noms exacts.

| Champ | Type | Valeurs / exemple |
|-------|------|-------------------|
| `type` | texte | **toujours** `achat` |
| `categorie` | texte | `labo` · `serre` · `vehicule` · `maraichage` · `communication` · `matiere-premiere` · `emballage` · `divers` |
| `poste` | texte | rattachement au plan (ex. `Équipements labo`) |
| `budget_estime` | nombre | € prévu au business plan (HT), sans symbole ni espace |
| `prix_constate` | nombre | € trouvé sur le web, sans symbole ni espace |
| `unite` | texte | `unité` · `lot` · `kg` · `m²`… |
| `fournisseur` | texte | nom du marchand retenu |
| `url_source` | texte | URL de la page du prix retenu |
| `date_verif` | date | `AAAA-MM-JJ` |
| `statut` | texte | `a-verifier` · `verifie` · `achete` · `abandonne` |
| `priorite` | texte | `haute` · `moyenne` · `basse` |

`budget_estime` et `prix_constate` sont des **nombres** (pas `15 000 €`) pour que
Dataview calcule les écarts. Mettre le symbole/format uniquement dans le corps.

## Template de fiche

```markdown
---
type: achat
categorie: labo
poste: Équipements labo
budget_estime: 3000
prix_constate: 3299
unite: unité
fournisseur: Materiel Horeca
url_source: https://www.materiel-horeca.com/fr/...
date_verif: 2026-07-08
statut: verifie
priorite: haute
tags:
  - achat
  - prix
  - labo
---

# Déshydrateur alimentaire pro 10 plateaux inox

> Poste : **Équipements labo** · Budget prévu : **3 000 € HT** · Constaté : **3 299 €**

## Prix relevés

| Date | Fournisseur | Prix | Source | Lien |
|------|-------------|-----:|--------|------|
| 2026-07-08 | Materiel Horeca | 3 299 € | json-ld | [page](https://www.materiel-horeca.com/fr/...) |
| 2026-07-08 | Matériels Cuisine | 2 990 € | meta | [page](https://materiels-cuisine.com/...) |

## Notes

- Prix TTC. Médiane retenue : ~3 150 €.
- Alternative reconditionnée à surveiller.

## Liens

- [[00 - Index et récapitulatif des budgets]]
- [[Labo PPAM]]
```

## Requêtes Dataview du tableau de bord

Vue synthèse par catégorie (budget vs constaté) :

````markdown
```dataview
TABLE WITHOUT ID
  categorie AS "Catégorie",
  sum(budget_estime) AS "Budget prévu (€)",
  sum(prix_constate) AS "Constaté (€)",
  sum(prix_constate) - sum(budget_estime) AS "Écart (€)"
FROM "08 Achats & Prix/Investissements"
WHERE type = "achat"
GROUP BY categorie
```
````

Détail de toutes les fiches, triées par écart :

````markdown
```dataview
TABLE
  poste AS "Poste",
  budget_estime AS "Budget",
  prix_constate AS "Constaté",
  (prix_constate - budget_estime) AS "Écart",
  fournisseur AS "Fournisseur",
  statut AS "Statut",
  date_verif AS "Vérifié le"
FROM "08 Achats & Prix/Investissements"
WHERE type = "achat"
SORT (prix_constate - budget_estime) DESC
```
````

Fiches encore à vérifier :

````markdown
```dataview
LIST
FROM "08 Achats & Prix/Investissements"
WHERE type = "achat" AND statut = "a-verifier"
```
````

## Notes Dataview

- Les requêtes `dataview` (DQL) ne nécessitent aucun réglage particulier ; elles
  fonctionnent dès que le plugin est activé.
- Ne pas utiliser `dataviewjs` (désactivé par défaut pour raisons de sécurité) :
  les requêtes DQL ci-dessus suffisent.
- Un champ vide (`prix_constate:` sans valeur) est traité comme `null` : il
  n'affecte pas les sommes.
