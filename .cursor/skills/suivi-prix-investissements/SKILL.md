---
name: suivi-prix-investissements
description: >-
  Vérifie sur le web le prix des investissements et achats du projet (matériel
  labo, serre, véhicule, matériel maraîchage, matières premières, emballages),
  compare au budget prévu, et range le tout dans Obsidian sous forme de tableaux
  Dataview. Utiliser quand l'utilisateur demande de vérifier / comparer / mettre
  à jour des prix, chiffrer un investissement, faire un tableur de prix
  fournisseurs, ou actualiser le budget d'un poste du business plan.
---

# Suivi des prix d'investissement — Le Chaudron qui sent bon

Chaîne complète : **chercher le prix réel sur le web → comparer au budget →
écrire une fiche Obsidian interrogeable par Dataview**.

## Outils utilisés

| Besoin | Outil (MCP) | Fonction |
|--------|-------------|----------|
| Trouver des pages marchandes | `verif-prix` | `rechercher_prix(produit, nb_resultats)` |
| Lire le prix d'une page | `verif-prix` | `extraire_prix(url)` |
| Écrire / lire une note | `user-obsidian` | `create-note`, `edit-note`, `read-note`, `search-vault` |

Si `verif-prix` n'apparaît pas dans les outils MCP, demander à l'utilisateur de
recharger la fenêtre Cursor (le serveur est déclaré dans `.cursor/mcp.json`).

## Où vivent les données

- Fiches : `08 Achats & Prix/Investissements/<Nom du poste>.md` (une par poste).
- Tableau de bord : `08 Achats & Prix/0 - Tableau de bord Prix.md` (Dataview, ne pas
  éditer à la main — il se recalcule seul).
- Budgets de référence : `02 Projects/Plan Entreprise/Business Plan par Étapes/00 - Index et récapitulatif des budgets.md`
  (§5 « Plan de financement initial »).

Le schéma de frontmatter et les requêtes Dataview sont dans
[reference.md](reference.md). **Lire ce fichier avant d'écrire une fiche.**

## Workflow

Copier cette checklist et la suivre :

```
- [ ] 1. Lister les postes à vérifier
- [ ] 2. Pour chaque poste : chercher le prix web (rechercher_prix + extraire_prix)
- [ ] 3. Retenir un prix représentatif + sa source
- [ ] 4. Écrire / mettre à jour la fiche Obsidian (frontmatter + tableau)
- [ ] 5. Présenter la synthèse comparée budget vs constaté
```

### 1. Lister les postes

Si l'utilisateur ne donne pas de liste, proposer les postes du plan de
financement Installation : serre double tunnel, équipements labo (déshydrateur,
stérilisateur/autoclave, étiqueteuse, machine sous vide, broyeur/moulin, balance,
plan de travail inox), véhicule utilitaire, matériel maraîchage/irrigation,
communication (étiquettes, PLV, site). Reformuler chaque poste en requête
produit précise (marque/capacité/pro) pour de meilleurs résultats.

### 2. Chercher le prix web

Pour chaque poste :

1. `rechercher_prix(produit="…", nb_resultats=8)`.
2. Choisir 2 à 4 URLs qui sont de **vraies pages produit** (écarter annuaires,
   pages catégorie, marketplaces d'occasion sauf si pertinent).
3. `extraire_prix(url)` sur chacune.
4. Privilégier les prix `source = json-ld` ou `meta` (fiables) ; un prix
   `source = regex` doit être confirmé par une 2ᵉ source ou signalé « à confirmer ».

Alterner la requête si aucun prix (ajouter « acheter », « prix », marque, « pro »,
retirer les mots trop spécifiques). Ne pas boucler plus de ~3 essais par poste :
si rien de fiable, écrire `statut: a-verifier` et noter la difficulté.

### 3. Retenir un prix représentatif

- Plusieurs prix cohérents → prendre la **médiane** (ou une fourchette min–max).
- Toujours conserver `url_source` + `fournisseur` + `date_verif` du prix retenu.
- Prix HT ou TTC : préciser dans `note` si l'info est disponible (le budget du
  plan est en **HT**).

### 4. Écrire la fiche

Utiliser le template de [reference.md](reference.md). Vérifier d'abord si la
fiche existe (`search-vault` ou `read-note`) :
- absente → `create-note` dans `08 Achats & Prix/Investissements/`.
- présente → `edit-note` (mettre à jour `prix_constate`, `fournisseur`,
  `url_source`, `date_verif`, `statut`, et ajouter une ligne à l'historique).

Renseigner `budget_estime` depuis le plan de financement pour permettre le calcul
d'écart. Mettre `statut: verifie` quand un prix fiable est trouvé.

### 5. Synthèse

Présenter à l'utilisateur un tableau Markdown : Poste · Budget · Prix constaté ·
Écart · Fournisseur · Source. Signaler les écarts importants (> ±20 %) et rappeler
que le tableau de bord Dataview est à jour dans `08 Achats & Prix/`.

## Règles

- Toujours citer la **source** (URL + date) d'un prix — pas de prix « de mémoire ».
- Ne jamais inventer un prix : si l'extraction échoue, le dire.
- Respecter les conventions du vault : frontmatter YAML, français, dates ISO
  `AAAA-MM-JJ`, liens `[[…]]`, montants en euros.
- Ne pas modifier `0 - Tableau de bord Prix.md` (généré par Dataview).
