# Méthode de contribution Recette Epice

Cette méthode est la référence pour toute modification de **`Recettes et production - v18.xlsx`** (et ses dérivés).

Voir aussi : [[Description du classeur (base v18)]] pour l'architecture complète.

## 1) Règles de base

1. Ne jamais modifier uniquement `Recette Epice` sans vérifier aussi :
   - `Produit`
   - `Ingredients`
   - `Conditionnement`
2. Conserver les tables Excel structurées :
   - `TableauRecette`
   - `TableauProduit`
   - `TableauIngredients`
3. Toujours ajouter des lignes **dans la table** (pas hors tableau).
4. Ne pas renommer les colonnes internes des tables sans migration complète.

## 2) Processus d'ajout d'une recette

1. Créer / vérifier la recette dans `Produit` :
   - Nom recette
   - Conditionnement
   - Poids unité
   - Prix de vente
   - Objectifs N1..N9
2. Ajouter les ingrédients dans `Recette Epice` (1 ligne par ingrédient).
3. Vérifier que chaque ingrédient existe dans `Ingredients` (orthographe identique).
4. Vérifier / corriger les formules de la ligne :
   - `ID`
   - fraction du mélange
   - prix achat/kg composant
   - total proportion
   - prix/kg mélange
   - kg/an N1..N9

## 3) Formules cibles (logique)

- `ID` : concaténation `Recette & Conditionnement`
- `fraction mélange` : `Proportion / somme des proportions` (même Recette + Conditionnement)
- `Prix d'achat / kg` : lookup ingredient price × fraction
- `kg / année N` : `fraction mélange × Total (kg) N` (depuis `TableauProduit`)

> Important : les noms internes des colonnes de `TableauRecette` ne sont pas toujours identiques aux en-têtes visibles.  
> Toujours s'aligner sur les noms internes réels lors de l'écriture de formules.

## 4) Contrôles obligatoires avant validation

- 0 occurrence de `#REF!` sur les colonnes clés de `Recette Epice`
- 0 recette orpheline entre `Produit` et `Recette Epice`
- 0 ingrédient manquant entre `Recette Epice` et `Ingredients`
- recalcul Excel effectué après modifications

## 5) Politique de nommage

- Utiliser un nom de recette unique, stable et accentué de façon cohérente.
- Éviter les variantes ambiguës (`Sucre` vs `Sucre Blanc`, etc.) sans normalisation.
- Si renommage recette : propager dans `Produit`, `Recette Epice`, `Concurrence`, vues Obsidian.

## 6) Onglets aval à mettre à jour si besoin

Après modification des objectifs ou des recettes, vérifier la cohérence avec :

- `Besoins plantes`
- `Production`
- `Planning Culture`

Ces onglets ne sont pas toujours reliés par formules — une mise à jour manuelle ou script peut être nécessaire.
