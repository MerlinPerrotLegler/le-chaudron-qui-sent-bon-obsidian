# Analyse Recette Epice (base v18)

Base d'analyse : **`Recettes et production - v18.xlsx`**

Voir aussi : [[Description du classeur (base v18)]] pour le contexte global et le diagramme des onglets.

## Structure observée

- Feuille : `Recette Epice`
- Tableau : `TableauRecette`
- Plage : `A1:T458`
- Lignes ingrédients : **457**
- Recettes uniques : **71**

## Défauts critiques observés dans v18

1. **Formules cassées `#REF!`**
   - Colonne G (`Prix d'achat / kg`) : 457 lignes impactées
   - Colonnes N→T (`kg / année 3` à `kg / année 9`) : références cassées

2. **Formules de besoins annuels incohérentes**
   - Colonne L (`kg / année 1`) : multiplication `N1 × N1` (au lieu de `fraction × Total kg N1`)
   - Colonne M (`kg / année 2`) : multiplication `N1 × N2`
   - Attendu : `fraction mélange × Total (kg) Ny` depuis `TableauProduit`

3. **Noms internes de colonnes différents des en-têtes affichés**

   | En-tête affiché | Nom interne table |
   |-----------------|-------------------|
   | `fraction mélange` | `poids / unite` |
   | `Total proportion` | `Total Proportion` |
   | `Prix pour kg de mélange` | `Prix pour kg/ de melange` |
   | `kg / année n` | `kg / annee n` |

   Risque : formules écrites avec les mauvais noms de colonne.

4. **Ingrédients non retrouvés dans `TableauIngredients`**
   - Exemples fréquents : `Sel`, `Poivre Noir`, `Gingembre Sec`, `Coriandre Graine`, etc.
   - Impact : coût matière faux ou nul.

## Contraintes de cohérence

- La clé logique d'une ligne recette est : **`Recette + Conditionnement + Ingredient`**
- La clé de liaison Produit ↔ Recette est : **`ID = Recette & Conditionnement`**
- Toute recette active dans `Recette Epice` doit exister dans `Produit` (et inversement).

## Risques opérationnels

- Sous-estimation des coûts matière.
- Besoins plantes annuels faux.
- Décisions de volume / marge faussées.
- Régressions silencieuses si table ou colonnes sont renommées sans contrôle.

## Décision de méthode

La contribution se fait uniquement via la procédure décrite dans :  
[[Méthode de contribution Recette Epice]]
