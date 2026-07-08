---
type: dashboard
status: active
created: 2026-07-08
updated: 2026-07-08
tags:
  - dashboard
  - achat
  - prix
  - budget
---

# 0 — Tableau de bord Prix & Investissements

> Suivi des prix réels des investissements/achats, comparés au budget du
> [[00 - Index et récapitulatif des budgets|plan de financement]].
> Les tableaux ci-dessous sont **calculés automatiquement par Dataview** à partir
> des fiches de `08 Achats & Prix/Investissements/`. Ne pas éditer à la main.

*Prix vérifiés sur le web via le MCP `verif-prix` + Skill `suivi-prix-investissements`.*

---

## Synthèse par catégorie

```dataview
TABLE WITHOUT ID
  categorie AS "Catégorie",
  sum(budget_estime) AS "Budget prévu (€)",
  sum(prix_constate) AS "Constaté (€)",
  (sum(prix_constate) - sum(budget_estime)) AS "Écart (€)"
FROM "08 Achats & Prix/Investissements"
WHERE type = "achat"
GROUP BY categorie
```

---

## Détail des postes (trié par écart)

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

---

## Encore à vérifier

```dataview
LIST
FROM "08 Achats & Prix/Investissements"
WHERE type = "achat" AND statut = "a-verifier"
```

---

## Comment ça marche

1. Demander (en langage naturel) : *« vérifie le prix de la serre double tunnel »*
   ou *« actualise tous les prix du labo »*.
2. Cursor cherche les prix sur le web (MCP `verif-prix`), les compare au budget et
   met à jour / crée les fiches dans `Investissements/`.
3. Ce tableau de bord se recalcule tout seul.

> Voir le Skill `suivi-prix-investissements` et le serveur MCP `verif-prix`
> (dossier `.cursor/` du dépôt) pour les détails techniques.

## Liens

- [[00 - Index et récapitulatif des budgets]] · [[02 - Installation]]
- [[Dashboard Le Chaudron qui sent bon]] · [[Labo PPAM]]
