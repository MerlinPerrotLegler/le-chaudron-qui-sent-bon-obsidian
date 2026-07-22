---
type: spec
status: draft
created: 2026-07-22
updated: 2026-07-22
tags:
  - webapp
  - cahier-des-charges
  - cas-utilisation
  - brainstorming
source:
  - "Recettes et production - v19.xlsx"
  - "Description du classeur (base v18)"
  - "Planning Culture"
---

# WebApp Le Chaudron qui sent bon — Cas d'utilisation

> **But du document** : recenser *tout ce que l'application doit pouvoir faire*, avant tout choix technique. On brainstorme dessus, puis on découpe en sous-systèmes livrables un par un.
>
> **Forme retenue** : application web hébergée sur **Hostinger Business Web Hosting** (Node.js/Next.js ou Python, MySQL/MariaDB, système de fichiers persistant). Détails : [[Guide technique pour développeurs]]. Décisions : [[10 - Décisions & questions ouvertes]].
>
> **Statut** : brouillon vivant. `❓` = question ouverte à trancher pendant le brainstorming.

---

## 1. Vision & périmètre

L'app remplace/prolonge le classeur `Recettes et production - v19.xlsx` et les notes Obsidian de planning. Elle relie **le commercial** (ce qu'on veut vendre) → **la production** (ce qu'on transforme) → **la matière** (récoltée à la ferme **ou achetée à l'extérieur**) → **la culture** (ce qu'on sème et plante), avec la gestion de stock au milieu.

La matière entre en stock par **deux voies** : les **récoltes** de la ferme (matière fermière) et les **achats** — matières agricoles cultivées ailleurs (matière d'importation) et commodités non cultivables (consommables de base). Les achats/imports sont donc un maillon **à part entière** de la chaîne (coût de revient, stock, futur module compta via webhook).

Chaîne de valeur pilotée par l'app :

```
Intentions de vente  →  Besoins produits finis  →  Besoins matière
        ↓                        ↓                          ↓
   Ventes réalisées      Production (recette+lot)     Planning de culture
        ↓                        ↓                          ↓
   Stock produits  ←──  déstock/restock  ──→  Stock matière  ←  Récoltes (ferme)
                                                    ↑
                                          Achats (import + base)
```

### Vocabulaire (glossaire de référence)

Termes distincts imposés dans toute l'app pour lever l'ambiguïté du mot « produit » :

| Terme | Définition | Provenance | Exemples | Suivi stock |
|-------|-----------|-----------|----------|:-----------:|
| **Produit fini** | Ce que la ferme **vend** (recette × conditionnement, ou matière brute revendue) | — | Herbes de Provence 100 ml, Sirop 500 ml, Thym séché vrac | ✅ stock produits |
| **Matière fermière** 🟢 | Matière **cultivée sur la ferme** | Ferme | Thym, Romarin, Sureau (chez nous) | ✅ stock matière |
| **Matière d'importation** 🟠 | Matière agricole **cultivée hors ferme**, achetée | Hors ferme (achat) | Poivre, cannelle, curcuma acheté | ✅ stock matière |
| **Consommable de base** ⚪ | Commodité **non cultivable**, achetée | Hors ferme (achat) | Sel, sucre, vinaigre, alcool neutre, huile | ✅ stock matière |

- **Matière** = terme générique couvrant les 3 lignes vertes/oranges/blanches (ce qui compose une recette et se suit en stock). Chaque matière porte un champ **provenance** (fermière / importation / base).
- Une **Matière fermière** peut aussi être vendue telle quelle → elle devient un **Produit fini** (UC-A1.7).
- **Tout est suivi** : chaque catégorie a son stock, ses entrées et ses sorties.

### Acteurs

- **Exploitant (Merlin)** — utilisateur principal, saisit tout, pilote.
- **Employés / opérateurs** — **multi-utilisateur dès le V1** (D14), authentification simple (login + mot de passe). Le **nom de l'opérateur** est tracé sur les actions (ex. production → traçabilité UC-C1.3). `❓` Rôles/permissions différenciés = plus tard.

---

## 2. Domaines (sous-systèmes)

| # | Domaine | Rôle | Dépend de |
|---|---------|------|-----------|
| A | **Catalogue** | Matières, recettes, conditionnements, produits (SKU) | — (socle) |
| B | **Commercial** | Intentions de vente, ventes réalisées | A |
| C | **Production & transformation** | Transformations primaires (séchage, distillation…) + productions de produits (recette) | A, D |
| D | **Stock** | Stock produits finis + stock matière | A, C, E |
| E | **Culture** | Parcelles, lots, planning par semaines, récoltes | A |
| F | **Planification** | Proposer un planning de culture depuis les intentions & le stock | B, D, E |
| G | **Plateforme** | API, storefront, webhooks (extensibilité : compta, etc.) | tous |

---

## A. Catalogue

Le socle de données. Reprend la logique des onglets `Ingredients`, `Recette Epice`, `Conditionnement`, `Produit` du classeur v19.

### A1. Gérer les matières / ingrédients
> **Matière** = terme générique (voir glossaire §1). Chaque matière a une **provenance** : **Matière fermière** 🟢 / **Matière d'importation** 🟠 / **Consommable de base** ⚪.
- **UC-A1.1** — Créer une matière (nom, **nom latin**, **provenance** [fermière / importation / base], ratio de séchage frais→sec, **% eau**, prix d'achat au kg, fournisseur/lien, **besoin en eau** faible/modéré/élevé, **source** de la donnée). Champs alignés sur l'onglet `Ingredients` du classeur v19.
- **UC-A1.2** — Une **Matière fermière** 🟢 est reliée à une **espèce cultivée** (domaine Culture) ; son stock est alimenté par les récoltes.
- **UC-A1.3** — Modifier / archiver une matière (garder l'historique pour ne pas casser les recettes existantes).
- **UC-A1.4** — Lister/filtrer les matières (ferme vs achat, par prix, par disponibilité en stock).
- **UC-A1.5** — **Volet import / achats** : gérer les matières **achetées** (non issues de la ferme), en deux provenances distinctes :
  - **Matière d'importation** 🟠 — agricole, cultivée ailleurs (poivre, cannelle, curcuma acheté…).
  - **Consommable de base** ⚪ — commodité non cultivable (sel, sucre, vinaigre, **alcool neutre**, huile…).
  Champs communs : unité d'achat, **prix d'achat / kg (ou / L)**, fournisseur, lien, `❓` stock mini d'alerte. Ces matières **entrent dans les recettes avec leur quantité** (UC-A2.2) et sont **suivies en stock** (UC-D2) au même titre que les matières fermières.
- **UC-A1.6** — **Prix d'import → coût de revient recette** : le prix défini sur chaque matière est la **source du coût matière** pour estimer le **coût de production d'une recette** (UC-A2.5) et la **marge du produit** (UC-A4.2/A4.3). Une matière sans prix renseigné est **signalée** (coût de recette incomplet). **Historique de prix** (Q-A3) : conserver une **liste `{date (YYYY-MM-DD) : prix}`** ; le **dernier prix** sert au calcul ; l'historique complet est **exposé dans l'API**.
- **UC-A1.7** — **Revendre une matière brute** : une matière (ex. plante séchée en vrac) peut avoir un **prix de vente/kg** et être vendue telle quelle. **Modélisée comme un Produit fini dont la « recette » = la matière seule** (Q-A4) → uniformise stock, vente et webhooks. Débouché « vente en gros de plantes » du [[Labo PPAM]].

### A2. Gérer les recettes
- **UC-A2.1** — Créer une recette (nom, profil/description, tags, **type/famille de produit**). La famille dépasse les épices : **sec, sirop, sel aromatisé, sucre aromatisé, vinaigre, lactofermenté, moutarde, tabasco, tisane**, et à terme **cosmétique** (huile de massage, huile essentielle/distillation, savon, bougie, lessive, bonbon — voir [[Labo PPAM]]). Le modèle recette doit rester **générique** (pas « épice » en dur).
- **UC-A2.1b** — **Catégorie réglementaire** de la recette, reliée aux fiches de [[0 - Cadre général]] (Mélanges d'épices secs / Préparations en saumure et lactofermentées / Sels aromatisés / Sucres aromatisés / Sirops / Tisanes…) → sert à l'étiquetage et aux contraintes de sécurité alimentaire.
- **UC-A2.2** — Ajouter les **ingrédients** d'une recette — chacun est une **matière** de n'importe quelle provenance (**fermière** 🟢, **d'importation** 🟠 ou **consommable de base** ⚪ : sel, sucre, vinaigre, alcool…) — **avec leur quantité**. **Unités flexibles** : soit en *parts/proportions* (« Herbes de Provence » : Thym 4, Romarin 2… → fractions normalisées auto), soit en **quantités absolues** avec unité (Choucroute : 10 kg chou, 200 g **sel** ; Sirop : 15-20 ombelles, 1 L eau, 1,3 kg **sucre**). Gérer une **taille de lot de référence / rendement** (« pour ~1 L de sirop », « pour 10 kg de chou »). Le coût de chaque ligne = prix d'achat de la matière × quantité (UC-A2.5).
- **UC-A2.3** — Définir les **étapes** du procédé, chacune avec : ordre, description, **temps requis** (main d'œuvre + temps d'attente/repos), **équipements requis** (séchoir, batteuse, tamis, broyeur, réfractomètre, pH-mètre…), et **paramètres de contrôle** optionnels (température, durée, **pH cible**, **Brix**, taux de sel %…) — points critiques de sécurité/qualité.
- **UC-A2.4** — Définir les **équipements** nécessaires (hors conditionnement) au niveau recette.
- **UC-A2.5** — Calculer le **coût matière au kg** de mélange = Σ (prix d'achat de l'ingrédient × fraction), en agrégeant **plantes fermières et matières d'import** (UC-A1.5/A1.6). Sert de base au coût de revient et à la marge du produit.
- **UC-A2.6** — Gérer des **variantes** d'une recette (ex. « garrigue + ») via un **champ « notes de variante »** au V1 (Q-A1) ; pas d'objet variante dédié.
- **UC-A2.7** — Dupliquer une recette pour en créer une nouvelle rapidement.
- **UC-A2.8** — Gérer le **rendement / ratio de travail** (frais → produit fini, pertes de transformation).

### A3. Gérer les conditionnements
- **UC-A3.1** — Créer un conditionnement (nom ex. `Épice 100 ml`, `Sirop 500 ml`, `Sachet recharge`, `Boîte`, `Vrac`, `Bouteille`, `Flacon` ; contenance/poids net ; coûts : contenant, bouchon, étiquette, total).
- **UC-A3.2** — Modifier / archiver un conditionnement, avec liens d'achat fournisseur.
- **UC-A3.3** — Lister les conditionnements et leur coût unitaire.

### A4. Gérer les produits (SKU = recette × conditionnement)
- **UC-A4.1** — Créer un produit fini = **recette + conditionnement** + poids/unité.
- **UC-A4.2** — Voir le **prix de revient** (matière + conditionnement **+ main d'œuvre**, cf. UC-A4.6) et fixer le **prix de vente**.
- **UC-A4.3** — Voir la **marge** unitaire et au kg.
- **UC-A4.4** — Comparer aux **benchmarks concurrence** (onglet `Concurrence`) : **hors V1** (Q-A2), rebranchable plus tard.
- **UC-A4.5** — Activer/désactiver un produit (au catalogue de vente ou non).
- **UC-A4.6** — **Temps de travail & main d'œuvre** : agréger le **temps requis** des étapes de la recette (UC-A2.3) pour obtenir le **temps de main d'œuvre par lot / par unité** ; avec un **taux horaire** (paramètre), en déduire un **coût main d'œuvre** intégré (optionnellement) au prix de revient et à la marge. *« si possible »* — activable/désactivable.

---

## B. Commercial

### B1. Intentions de vente
- **UC-B1.1** — Déclarer une **intention de vente** par produit (recette × conditionnement) et par **année civile** (D2/D10) : nombre d'unités visé. (Répartition mensuelle/saisonnière = plus tard.)
- **UC-B1.2** — Associer une **importance/priorité** (P1/P2/P3) à une intention.
- **UC-B1.3** — Voir le **chiffre d'affaires prévisionnel** et la **marge prévisionnelle** agrégés.
- **UC-B1.4** — Dériver automatiquement les **besoins en produits finis** puis les **besoins matière (kg par espèce)** via les recettes et ratios de séchage.
- **UC-B1.5** — Les **intentions** ne sont **pas** rattachées à un point de vente au V1 (Q-B4 = non) ; elles sont globales par produit. Les **ventes réalisées**, elles, portent le point de vente (UC-B2.1).

### B2. Ventes réalisées
- **UC-B2.1** — Déclarer une **vente réalisée** (produit, quantité, date, prix, **point de vente / canal**). Saisie via le storefront interne (UC-G1.2) **ou via l'API** (Q-B3) — permet une déclaration programmatique.
- **UC-B2.2** — La vente **déstocke** automatiquement le produit fini (domaine Stock) et **émet le webhook** `vente réalisée`.
- **UC-B2.3** — Comparer **réalisé vs intention** (taux d'atteinte, reste à vendre).
- **UC-B2.4** — Saisie **agrégée par jour de vente / par produit** (marché) ; `❓` import en masse plus tard.
- **UC-B2.5** — **Historique des ventes** : consulter/filtrer toutes les ventes (par période, produit, point de vente), avec totaux (CA, quantités). Base des statistiques (UC-T8).

### B3. Points de vente & canaux
- **UC-B3.1** — Gérer les **points de vente / canaux** : vente à la ferme, marché, boutique de producteur, et **demi-gros** (parapharmacies, SPA, masseurs, herboristes, kinés — cf. [[Labo PPAM]] et [[Points de Vente]]). Champs : nom, type/canal, `❓` contact, notes.
- **UC-B3.2** — Rattacher chaque **vente** à un point de vente pour analyser les ventes **par canal**. Les **intentions** ne sont pas rattachées à un point de vente (Q-B4 = non).

---

## C. Production & transformation

> Deux natures d'opérations, toutes deux tracées :
> - **Transformation primaire** (C0) : convertit **une matière en une autre** (frais → sec, plante → huile essentielle, mondage…). N'assemble pas plusieurs ingrédients.
> - **Production / assemblage** (C1) : applique une **recette** (plusieurs matières) pour obtenir un **Produit fini**.

### C0. Déclarer une transformation (primaire)
- **UC-C0.1** — Déclarer une **transformation** : type (séchage, distillation, mondage, congélation, torréfaction…), **matière(s) entrante(s) + lot(s) consommés**, **matière sortante + nouveau lot**, **quantités** entrée/sortie et **rendement** effectif, opérateur, date, `❓` paramètres (température, durée…).
- **UC-C0.2** — La transformation **déstocke** la matière entrante et **restocke** la matière sortante (ex. sort du stock « frais », entre en stock « sec ») ; **émet le webhook** `transformation déclarée`. Le séchage frais→sec (ratio) devient ainsi un **événement tracé**, pas une simple conversion automatique.
- **UC-C0.3** — Une matière sortante (ex. **huile essentielle** distillée, plante séchée) peut être un **ingrédient d'autres recettes** et/ou un **Produit fini** vendable.

### C1. Déclarer une production (recette → produit fini)
- **UC-C1.1** — Déclarer une **production** = recette + quantité produite + conditionnement(s) obtenus + **date** + **n° de lot de production** + **nom de l'opérateur** + **date de péremption / DLUO**.
- **UC-C1.2** — La production **consomme la matière** en stock (déstockage) et **restocke le produit fini** (domaine Stock), et **émet le webhook** `production déclarée`.
- **UC-C1.3** — **Traçabilité complète — OBLIGATOIRE** (Q-C1). Chaîne remontable de bout en bout :
  - **Parcelle** : amendements, réf. de gaine (irrigation), phytos/traitements, réf. graine/plant, travail du sol…
  - → **Récolte** : date, **n° des sacs de stock**, quantité (frais), **qualité**, **date de péremption**…
  - → **Transformation** (séchage, distillation, mondage, congélation…) : intrant(s) + lot(s), procédé, **rendement** (frais → sec, plante → HE…), matière/lot **sortant**, opérateur, date.
  - → **Production / Produit** (recette) : date, **nom de l'opérateur**, réf., **n° de lot**, **date de péremption**.
  Depuis un produit fini, on doit pouvoir **remonter** jusqu'aux transformations, récoltes et parcelles d'origine (et redescendre). Alimente le futur cahier de culture / obligations sanitaires.
- **UC-C1.4** — Alerter si la matière en stock est **insuffisante** pour la production visée.

### C2. Suivre l'avancement des productions
- **UC-C2.1** — Voir l'**état d'avancement** d'une production par étapes (à faire / en cours / séchage en cours / terminé), avec l'étape courante et le temps restant estimé.
- **UC-C2.2** — Tableau de bord : productions en cours, goulots (équipement occupé, séchoir plein).
- **UC-C2.3** — Au V1 : **enregistrer** les productions + suivre l'avancement (Q-C2). Pas d'ordonnancement charge/semaine (la charge est agrégée dans les stats, UC-T8).

---

## D. Stock

### D1. Stock produits finis
- **UC-D1.1** — Voir le **stock de chaque produit** (unités disponibles), alimenté par la production et diminué par les ventes.
- **UC-D1.2** — Ajustement manuel d'inventaire (casse, offert, écart d'inventaire) avec motif.
- **UC-D1.3** — Alertes de **stock bas** vs intentions de vente restantes.
- **UC-D1.4** — Suivre les **DLUO / dates de péremption par lot** (Q-D1, dans le périmètre) — cohérent avec la traçabilité obligatoire (UC-C1.3). Alerte à l'approche de la DLUO.

### D2. Stock matière (toutes provenances)
- **UC-D2.1** — Voir le **stock matière** par matière (**fermière** 🟢, **d'importation** 🟠, **consommable de base** ⚪), en **frais** et/ou **sec** (conversion via ratio de séchage pour les végétaux).
- **UC-D2.2** — Entrées : **récoltes** (matière fermière, domaine Culture) et **achats** (matière d'importation + consommables de base). Un achat enregistre quantité, prix, fournisseur, date → alimente le stock et le futur module compta (webhook).
- **UC-D2.3** — Sorties : **productions** (consommation recette, toutes provenances confondues).
- **UC-D2.4** — Alertes : matière insuffisante vs besoins dérivés des intentions.
- **UC-D2.5** — Gérer les **emplacements de stockage** (Q-D2, dans le périmètre) : champ **select avec option « créer »** (séchoir, bocaux, chambre froide, **n° de sac**…). Relié aux n° de sacs de la récolte (UC-C1.3).

---

## E. Culture

### E1. Parcelles
> **Pas d'entité « espace »** (Q-E4) : la **parcelle** est l'unité de base, identifiée par son **numéro**. La vocation (serre, tunnel, plein champ, maraîchage…) est un simple **attribut** de la parcelle.
- **UC-E1.1** — **Déclarer une parcelle** (unité physique de terrain) avec :
  - **Nom/code** au format **`[A-Z]+-[0-9]{2,3}`** (ex. `A-01`, `ZC-123`) — validé à la saisie, unique.
  - **Surface**, **vocation** (attribut : serre semis / tunnel / frais / maraîchage / drainé ensoleillé / grande culture…).
  - **Particularités du sol** : type de sol, pH, drainage, pierrosité, exposition, pente…
  - **Particularités de culture** : ce qui pousse bien/mal, contraintes (ombre, vent, gel).
  - **Travail du sol** : journal des interventions (labour, faux-semis, paillage, couvert…) avec date.
  - **Entrants** : journal des apports (compost, amendements, fertilisation, **réf. de gaine d'irrigation**, phytos, **réf. graine/plant**…) avec date, produit, quantité — brique de la **traçabilité obligatoire** (UC-C1.3).
  - **Images annotées** : galerie/**carrousel** de plans et photos de la parcelle. Les images sont **annotées avant upload** (Q-E5) ; pas de géométrie/coordonnées SIG au V1. Stockage : voir [[Guide technique pour développeurs]].
- **UC-E1.2** — **Historique par semaine / rotation** (Q-E2) : suivre, semaine par semaine, ce qui occupe la parcelle (culture en place, travail du sol, amendements, phytos, réf. graine…). Permet de visualiser la **rotation** dans le temps.
- **UC-E1.3** — Voir la **fiche parcelle** consolidée : caractéristiques + historique hebdo (rotation) + travail du sol + entrants + lots de culture implantés + images.

### E2. Espèces & itinéraires techniques
- **UC-E2.1** — Gérer les **espèces cultivées** (reliées aux matières A1) avec leurs **données culturales** (cf. fiches type [[Thym]]) :
  - Identité & sol : nom latin, famille, **cycle** (vivace/annuelle + **renouvellement** tous les N ans), pH, **type de sol**, **exposition**.
  - Timing (alimente l'itinéraire E2.2 & la cascade) : **temps de levée min**, **temps de levée max**, **temps avant repiquage** (levée → plantation), puis durées jusqu'à récolte.
  - Eau : **besoin d'eau min par mois** et **besoin d'eau min par jour** (chiffrés), en plus du niveau qualitatif faible/modéré/élevé.
  - Rendement & densité : **densité/espacement** (ex. 30-40 cm ; 1 500 plants/ha), amendement, **rendement** (t/ha frais → kg/ha sec).
- **UC-E2.2** — Définir l'**itinéraire technique** : liste ordonnée d'**étapes personnalisables** (Semis S, Plantation P, Récolte R, Taille T, Division D…), **durées entre étapes** et **fenêtres calendaires** (mois/semaines possibles). Pilote la cascade (D4).
- **UC-E2.3** — **Associations de cultures** : consigner les associations **favorables** et **déconseillées** entre espèces (compagnonnage, allélopathie — cf. fiche [[Thym]]). Exploité par la planification (suggestions & alertes de conflit, UC-E3.6 / F).
- **UC-E2.4** — **Risques de culture** par espèce (ravageurs, maladies, aléas) avec prévention — champ de connaissance rattaché à l'espèce.

### E3. Lots de culture & planning par semaines
- **UC-E3.1** — Créer un **lot de culture** (espèce × **parcelle** × année) avec un **volume/surface** cible et une **importance/priorité**. Le lot **hérite** de l'itinéraire de l'espèce (D4) et peut ajuster ses durées **et ses données propres, qui varient d'une année à l'autre** (rendement réel, dates… — Q-E7).
- **UC-E3.2** — Afficher le **planning de culture par semaines** (calendrier hebdomadaire, une ligne par lot, étapes positionnées sur les semaines).
- **UC-E3.3** — **Décalage automatique en cascade** : si je change la **date de semis**, la plantation et les étapes suivantes se décalent d'autant (selon les durées de l'itinéraire). ⭐ Fonction clé.
- **UC-E3.4** — **Décalage inverse** : si je change une étape aval (ex. je veux récolter à telle semaine), les étapes amont (plantation, semis) se recalculent en remontant. ⭐ Fonction clé.
- **UC-E3.5** — **Modifier manuellement** le planning proposé (déplacer une étape, verrouiller une date pour qu'elle ne bouge plus, découpler une étape de la cascade).
- **UC-E3.6** — Détecter les **conflits** : deux lots sur la même **parcelle** en même temps, dépassement de surface, fenêtre calendaire hors saison.

### E4. Récoltes
- **UC-E4.1** — **Déclarer une récolte** (lot de culture, date, quantité récoltée en frais, **qualité**, **n° des sacs de stock**, **emplacement**, **date de péremption** — cf. traçabilité UC-C1.3).
- **UC-E4.2** — La récolte **entre en stock matière** (frais, matière fermière) et **émet le webhook** `récolte déclarée`. Le passage **frais → sec** se fait ensuite via une **transformation** tracée (UC-C0), pas une conversion automatique.
- **UC-E4.3** — **Suivi lot/parcelle** : de la récolte on remonte au lot de culture et à la **parcelle** (traçabilité obligatoire), et en aval on relie aux productions qui l'ont consommée.
- **UC-E4.4** — Suivre l'**état d'avancement des cultures** (semé / planté / en croissance / en récolte / terminé) par lot.

---

## F. Planification (moteur d'aide à la décision)

- **UC-F1.1** — **Proposer un planning de culture** dérivé automatiquement : intentions de vente → besoins produits → **besoins matière (kg sec/frais)** → **surfaces à cultiver** (= besoin kg ÷ **rendement** de l'espèce, cf. onglet `Besoins plantes` : `kg = unités × poids/unité × fraction`, `m² = kg ÷ rendement`), en tenant compte du **stock matière existant** (ne pas recultiver ce qu'on a déjà), du **cycle** (vivaces déjà en place = pas de replantation) et de l'**importance** des intentions.
- **UC-F1.2** — Affecter les besoins aux **parcelles adaptées** (faisabilité par espèce selon vocation/sol/exposition de la parcelle, 🟢🟡🔴) et signaler les besoins non plaçables.
- **UC-F1.6** — **Contrainte eau** : intégrer le **besoin en eau** par espèce et un budget eau (par parcelle / global, ex. ~420 m³/an) pour arbitrer et proposer une **sélection à faible besoin en eau** (cf. onglet `Selection faible eau`). Utiliser aussi les **associations** (UC-E2.3) pour suggérer/écarter des voisinages.
- **UC-F1.3** — Rendre la proposition **modifiable** : l'exploitant ajuste volumes, **parcelles**, dates ; l'app recalcule le reste (surfaces, besoins couverts, cascade de dates).
- **UC-F1.4** — Comparer **planifié vs besoin** : couverture des intentions par la culture + stock (manques / surplus).
- **UC-F1.5** — `❓` Prendre en compte les **rotations** et la **pérennité** (vivaces vs annuelles) dans la proposition.

---

## G. Plateforme (API, storefront, webhooks)

Choix d'architecture : **API-first**. Le cœur métier est exposé par une **API** ; les interfaces (back-office de gestion et **storefront**) la consomment. Chaque action métier significative **émet un webhook** documenté, pour brancher plus tard des modules externes (comptabilité en premier).

- **UC-G1.1** — **API REST** (Q-G2) documentée : expose les entités et actions du domaine (catalogue, stock, production, ventes, culture). Socle unique des interfaces et intégrations ; permet aussi de **déclarer une vente** (UC-B2.1) et d'exposer l'**historique de prix** (UC-A1.6).
- **UC-G1.2** — **Storefront** = **front de vente interne** (D8) : interface de **saisie rapide des ventes** (marché, vente directe, ferme). Sélection produit → quantité → prix → validation ; déstocke le produit fini et émet le webhook `vente réalisée`. Pas de compte client ni paiement en ligne au V1. Une boutique publique pourra se brancher plus tard sur la même API.
- **UC-G1.3** — **Webhooks configurables** (Q-G3) : chaque action clé (vente réalisée, production déclarée, **transformation déclarée**, récolte déclarée, mouvement de stock, création/màj produit…) émet un événement. Configuration par **JSON `nom.du.hook → [urls à appeler]`** dans l'app :
  ```json
  {
    "vente.realisee": ["https://url-a-appeler-1", "https://url-a-appeler-2"],
    "transformation.declaree": ["https://..."],
    "production.declaree": ["https://..."]
  }
  ```
  Chaque hook est **documenté** (payload, déclencheur) dans la **doc API + doc webhooks**. Payload versionné.
- **UC-G1.4** — **Module comptable (futur)** : consommateur des webhooks (ventes, achats/entrants, coûts) — **hors périmètre de développement V1** mais l'architecture doit le rendre possible sans refonte (contrats d'événements stables).
- **UC-G1.5** — **Authentification** : **clé d'API simple** (Q-G4) pour les intégrations externes ; **login/mot de passe** pour les utilisateurs de l'app (D14).

---

## 3. Fonctions transverses

- **UC-T1** — Recherche globale (produit, recette, plante, lot).
- **UC-T2** — Tableau de bord d'accueil (alertes stock, productions en cours, prochaines étapes de culture de la semaine).
- **UC-T3** — **Import initial souhaitable** (Q-T1) : reprendre matières/recettes/conditionnements/produits depuis `Recettes et production - v19.xlsx` (et fiches Obsidian) pour éviter la ressaisie. À cadrer.
- **UC-T4** — `❓` Historique / journal des modifications (onglet `Log`).
- **UC-T5** — **Export CSV basique** au V1 (Q-T2) ; étiquettes/compta plus tard.
- **UC-T6** — `❓` Sauvegarde / restauration des données.
- **UC-T7** — **Intégrité référentielle garantie** : l'app impose automatiquement les contrôles aujourd'hui manuels dans la « [[Méthode de contribution Recette Epice]] » — pas d'ingrédient de recette absent du référentiel matières, pas de produit orphelin, noms uniques/stables, propagation des renommages. Remplace la vérification manuelle du classeur.
- **UC-T8** — **Statistiques** : une **page statistique générale** (vue d'ensemble : CA, marges, stock, avancement cultures) **+ une page par topic** :
  - **Ventes** : CA par période / produit / point de vente, réalisé vs intentions.
  - **Production** : volumes produits, lots, avancement.
  - **Stock** : niveaux produits & matière, alertes, rotations.
  - **Culture** : surfaces, avancement des lots, récoltes, rendements réel vs prévu.
  - **Marges** : coûts de revient, marges par produit.
  - **Temps de travail / charge** : heures agrégées (production + culture) par semaine, goulots.
  Chaque page se nourrit des données du domaine correspondant.

---

## 4. Ordre de construction proposé

Le domaine **A. Catalogue** est le socle : tout en dépend. Séquence pressentie :

1. **A. Catalogue** (matières, recettes, conditionnements, produits) — fondation du modèle de données
2. **E. Culture** (espèces, lots, planning hebdo + cascade de dates, récoltes) — la partie la plus demandée et la plus interactive
3. **D. Stock** (matière + produits finis)
4. **C. Production** (déclaration + suivi, branche stock)
5. **B. Commercial** (intentions + ventes réalisées)
6. **F. Planification** (moteur de proposition) — arrive en dernier car il agrège tous les autres

**G. Plateforme** est **transverse** : l'orientation API-first et l'émission de webhooks sont posées **dès le domaine A** et enrichies à chaque domaine (chaque action ajoute ses événements). Le **storefront** se construit avec **B. Commercial**. Le module comptable reste hors périmètre (branché plus tard via webhooks).

> Chaque domaine fera l'objet de sa **propre spec** (`docs/superpowers/specs/…`) puis de son plan d'implémentation.

---

## Liens

- [[Description du classeur (base v18)]] · [[Analyse Recette Epice (base v18)]] · [[Méthode de contribution Recette Epice]]
- [[Planning Culture]] · [[Production PPAM]] · [[Labo PPAM]]
- [[0 - Index Recettes d'épices]] · [[0 - Index Plantes Aromatiques]]
