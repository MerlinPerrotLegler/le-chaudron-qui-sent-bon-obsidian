---
type: spec
status: draft
created: 2026-07-22
updated: 2026-07-22
tags:
  - webapp
  - decisions
  - brainstorming
source:
  - "00 - Cas d'utilisation"
---

# WebApp — Décisions & questions ouvertes

Journal des décisions prises pendant le brainstorming, et liste des points encore à trancher. Complète [[00 - Cas d'utilisation]].

---

## ✅ Décisions prises

| # | Décision | Détail |
|---|----------|--------|
| D1 | **Forme** | Application **web hébergée sur Hostinger** (type d'hébergement précis à confirmer : mutualisé PHP/MySQL vs VPS Node). |
| D2 | **Modèle du temps** | **Calendrier réel par année civile** (2026, 2027…), chaque année découpée en **52 semaines**. Le planning de culture, la production et le stock vivent sur des semaines réelles. |
| D3 | **Méthode** | On capture d'abord tous les cas d'usage, puis on découpe en sous-systèmes ; chaque domaine aura sa propre spec + plan. |
| D4 | **Itinéraire technique** | **Modèle par espèce, ajustable par lot** : chaque espèce porte un itinéraire type (étapes + durées), chaque lot en hérite et peut ajuster ses durées. Pilote le moteur de cascade (UC-E3.3/E3.4). |
| D5 | **Architecture** | **API-first** : cœur métier exposé par une API, consommée par le back-office et le **storefront**. Chaque action clé **émet un webhook documenté** (contrats versionnés) pour brancher un **module comptable** plus tard, sans refonte. Compta = hors périmètre V1. |
| D6 | **Nommage parcelles** | ✅ Confirmé : code au format **`[A-Z]+-[0-9]{2,3}`** (1+ lettres majuscules, tiret, **2 à 3 chiffres** ; ex. `A-01`, `ZC-123`), unique, validé à la saisie. |
| D7 | **Volet import / achats** | Matières achetées (hors ferme), en **deux provenances** : **Matière d'importation** 🟠 (agricole, cultivée ailleurs — poivre, cannelle…) et **Consommable de base** ⚪ (non cultivable — sel, sucre, vinaigre, alcool neutre, huile…). Prix d'achat/kg (ou /L) → **coût de revient recette** (UC-A1.5/A1.6 → A2.5 → marge A4). Entrées via **achats**, suivies en stock matière. |
| D13 | **Vocabulaire** | Termes distincts imposés partout : **Produit fini** (vendu) · **Matière fermière** 🟢 (cultivée ferme) · **Matière d'importation** 🟠 (cultivée hors ferme, achetée) · **Consommable de base** ⚪ (non cultivable, achetée). « Matière » = générique des 3, avec un champ **provenance**. Glossaire = §1 de [[00 - Cas d'utilisation]]. |
| D8 | **Storefront** | = **front de vente interne** (saisie rapide des ventes, déstockage, webhooks). Pas de boutique publique / paiement en ligne au V1. Une boutique publique pourra se brancher plus tard sur la même API. |
| D9 | **Points de vente & historique** | **Au V1** : gérer les points de vente / canaux (ferme, marché, demi-gros : parapharmacies, SPA, masseurs, herboristes, kinés) et un **historique des ventes** filtrable, rattaché aux points de vente (UC-B2.5, UC-B3). |
| D10 | **Pas de vue pluriannuelle** | L'app raisonne **en année civile** (D2) ; la vue business-plan N1→N9 (revenu brut/net par année de l'onglet `Produit`) **reste dans Excel**, hors app. |
| D11 | **Temps de travail** | Agréger le **temps requis** des étapes (recette + culture) → temps main d'œuvre par lot/unité ; **taux horaire** paramétrable → coût main d'œuvre **optionnel** dans le prix de revient (UC-A4.6) et vue charge (UC-T8). |
| D12 | **Statistiques** | Une **page stats générale** + **une page par topic** (ventes, production, stock, culture, marges, charge de travail) (UC-T8). |

---

## ❓ Questions ouvertes — avec proposition de défaut V1

> Défauts proposés pour rester **simple au V1**. À confirmer / corriger.

### Cadrage
| # | Question | Défaut V1 proposé |
|---|----------|-------------------|
| Q-U1 | Mono ou multi-utilisateur ? | **Mono-utilisateur** (Merlin), auth simple. Multi plus tard. |
| Q-H1 | Hébergement Hostinger : mutualisé PHP/MySQL ou VPS ? | **À confirmer** (question technique, tranchée au moment de la spec technique). |

### Catalogue (A)
| # | Question | Défaut V1 proposé |
|---|----------|-------------------|
| Q-A1 | Variantes de recette (UC-A2.6) | Champ « notes de variante » sur la recette ; pas d'objet variante dédié au V1. |
| Q-A2 | Benchmarks concurrence (UC-A4.4) | **Hors V1** (données de veille, pas bloquant pour piloter). |
| Q-A3 | Historiser les prix matière (UC-A1.6) | V1 : **dernier prix saisi**. Prix moyen / historique plus tard. |
| Q-A4 | Revente matière brute (UC-A1.7) | Modéliser comme **produit** dont la « recette » = matière seule (uniformise le stock/vente). À valider. |
| Q-A5 | Unités de recette (UC-A2.2) | Supporter **proportions ET quantités absolues** + taille de lot de référence. Non négociable (l'existant a les deux). |
| Q-A6 | Familles cosmétiques (huile, HE, savon…) au V1 ? | **Modèle générique** dès le V1, mais **données V1 = alimentaire** (épices/sirops/sels/…). Cosmétique alimenté plus tard. |
| Q-A7 | Catégorie réglementaire (UC-A2.1b) au V1 ? | **Oui, en champ** (simple référence à la fiche régl.) ; contraintes/étiquetage détaillés plus tard. |

### Commercial (B)
| # | Question | Défaut V1 proposé |
|---|----------|-------------------|
| Q-B1 | Granularité intentions (UC-B1.1) | **Par année civile** (cohérent D2) ; répartition mensuelle plus tard. |
| Q-B2 | Canaux / points de vente (UC-B3) | ✅ Résolu → D9 : **points de vente gérés au V1**. Gestion **clients** (nominatifs) = hors V1. |
| Q-B3 | Ventes marché (UC-B2.4) | **Saisie agrégée** par jour de vente / par produit. |
| Q-B4 | Rattacher les **intentions** aussi à un point de vente ? | Optionnel au V1 (intentions globales par produit) ; ventes réalisées oui. |
| Q-B5 | Taux horaire main d'œuvre (UC-A4.6/D11) | Un **taux global** paramétrable au V1 ; taux par tâche plus tard. |

### Production (C)
| # | Question | Défaut V1 proposé |
|---|----------|-------------------|
| Q-C1 | Traçabilité lot (UC-C1.3) | Lien lot de récolte → production **enregistré mais optionnel** au V1. |
| Q-C2 | Planifier les productions (UC-C2.3) | **Enregistrer** + suivre l'avancement ; pas d'ordonnancement charge/semaine au V1. |

### Stock (D)
| # | Question | Défaut V1 proposé |
|---|----------|-------------------|
| Q-D1 | DLUO / péremption (UC-D1.4) | **Hors V1** (à rajouter avec la traçabilité fine). |
| Q-D2 | Emplacements de stockage (UC-D2.5) | **Hors V1** (stock global par espèce / par produit). |

### Plateforme (G)
| # | Question | Défaut V1 proposé |
|---|----------|-------------------|
| Q-G1 | Storefront = boutique publique ou front interne ? | ✅ Résolu → D8 : **front de vente interne** au V1. |
| Q-G2 | Style d'API : REST | **REST** par défaut (simple, bien outillé, compatible Hostinger). |
| Q-G3 | Webhooks : rejeu/retry en cas d'échec au V1 ? | Journal des livraisons au V1 ; retry auto plus tard. |
| Q-G4 | Auth API pour intégrations externes | Clé d'API simple ; à durcir avec la compta. |

### Culture (E)
| # | Question | Défaut V1 proposé |
|---|----------|-------------------|
| Q-E1 | Itinéraire technique | ✅ Résolu → D4. |
| Q-E2 | Blocs/planches (UC-E1.4) | Parcelle = unité de base au V1 ; blocs/rotation plus tard. |
| Q-E3 | Étapes de culture (S/P/R/T/D) | **Personnalisables par espèce** (liste d'étapes ordonnée dans l'itinéraire), avec S/P/R/T/D comme modèles de départ. |
| Q-E4 | Relation espace ↔ parcelle | Une **parcelle appartient à un espace** (vocation) ; à confirmer. |
| Q-E5 | Géométrie/coordonnées des parcelles | **Hors V1** : images + surface suffisent (carrousel de plans). |
| Q-E6 | Stockage des images du carrousel parcelle | Upload fichiers ; `❓` où (serveur Hostinger / dossier). À cadrer à la spec technique. |
| Q-E7 | Rendement (t/ha) par espèce pour dériver les surfaces (F) | **Oui** : attribut espèce, ajustable par lot. Base du calcul surface ↔ volume. |
| Q-E8 | Associations de cultures (UC-E2.3) exploitées par la planif au V1 ? | Consignées au V1 (données) ; **alertes/suggestions** automatiques plus tard. |
| Q-E9 | Contrainte eau dans la planif (UC-F1.6) au V1 ? | Besoin en eau **affiché/filtrable** au V1 ; arbitrage automatique par budget eau plus tard. |

### Transverse (T)
| # | Question | Défaut V1 proposé |
|---|----------|-------------------|
| Q-T1 | Import initial (UC-T3) | **Oui, souhaitable** : import des matières/recettes/conditionnements/produits depuis v19.xlsx pour ne pas ressaisir. À cadrer. |
| Q-T2 | Exports (UC-T5) | Export CSV basique ; étiquettes/compta plus tard. |

---

## Liens

- [[00 - Cas d'utilisation]]
