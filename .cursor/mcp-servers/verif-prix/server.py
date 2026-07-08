#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "mcp>=1.2.0",
#   "httpx>=0.27",
#   "beautifulsoup4>=4.12",
#   "lxml>=5.0",
#   "ddgs>=6.0",
# ]
# ///
"""Serveur MCP « verif-prix ».

Deux outils pour aider Cursor a verifier le prix reel des investissements /
achats du projet (materiel labo, serre, vehicule, matieres premieres...) :

  - rechercher_prix(produit, ...)  -> liste de pages marchandes candidates
  - extraire_prix(url)             -> prix detecte sur une page donnee

Aucune cle d'API : recherche via le endpoint HTML de DuckDuckGo, extraction
via les donnees structurees schema.org (JSON-LD / microdata / OpenGraph) avec
repli sur une detection par expression reguliere.

Lancement direct pour test :
    uv run --script server.py --selftest "deshydrateur alimentaire pro"
"""

from __future__ import annotations

import json
import re
import sys
import time
from dataclasses import dataclass, asdict
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

import httpx
from bs4 import BeautifulSoup

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
HEADERS = {
    "User-Agent": UA,
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.5",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}
TIMEOUT = httpx.Timeout(20.0, connect=10.0)

# Motif de prix EUR : 12,50 € / 12.50€ / 1 299,00 € / € 12,50 / EUR 12.50
_PRICE_RE = re.compile(
    r"(?:(?P<sym1>€|EUR)\s*)?"
    r"(?P<num>\d{1,3}(?:[ \u00a0.]\d{3})*(?:[.,]\d{1,2})?|\d+(?:[.,]\d{1,2})?)"
    r"(?:\s*(?P<sym2>€|EUR|euros?))?",
    re.IGNORECASE,
)


@dataclass
class ResultatRecherche:
    titre: str
    url: str
    extrait: str


@dataclass
class Prix:
    valeur: float | None
    devise: str
    texte_brut: str
    source: str  # json-ld | microdata | meta | regex


@dataclass
class RapportPrix:
    url: str
    produit: str | None
    prix: list[dict[str, Any]]
    methode: str
    erreur: str | None = None


def _normaliser_nombre(brut: str) -> float | None:
    """Convertit '1 299,00' / '1,299.00' / '12.50' en float."""
    s = brut.strip().replace("\u00a0", " ").replace(" ", "")
    if "," in s and "." in s:
        # Le dernier separateur est le decimal.
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s:
        # Virgule = decimale FR si 1-2 chiffres apres, sinon millier.
        if re.search(r",\d{1,2}$", s):
            s = s.replace(",", ".")
        else:
            s = s.replace(",", "")
    try:
        val = float(s)
    except ValueError:
        return None
    return round(val, 2)


def _client() -> httpx.Client:
    return httpx.Client(
        headers=HEADERS, timeout=TIMEOUT, follow_redirects=True, http2=False
    )


# --------------------------------------------------------------------------- #
# Recherche web (sans cle d'API) : DuckDuckGo puis repli Bing
# --------------------------------------------------------------------------- #
def _rechercher(produit: str, nb_resultats: int) -> list[ResultatRecherche]:
    """Interroge plusieurs moteurs jusqu'a obtenir des resultats.

    Priorite a la librairie `ddgs` (client navigateur + gestion du token, robuste
    face au rate-limiting). Replis : scraping DuckDuckGo HTML, puis Bing.
    """
    requete = produit.strip()
    # 1) ddgs (le plus fiable)
    try:
        res = _rechercher_ddgs(requete, nb_resultats)
        if res:
            return res
    except Exception:  # noqa: BLE001 - on tente les replis
        pass
    # 2) replis par scraping direct
    with _client() as client:
        for moteur in (_rechercher_ddg, _rechercher_bing):
            for tentative in range(2):
                try:
                    res = moteur(client, requete, nb_resultats)
                except Exception:  # noqa: BLE001 - moteur suivant
                    res = []
                if res:
                    return res
                time.sleep(0.8 * (tentative + 1))
    return []


def _rechercher_ddgs(requete: str, nb_resultats: int) -> list[ResultatRecherche]:
    from ddgs import DDGS

    resultats: list[ResultatRecherche] = []
    with DDGS() as ddg:
        for item in ddg.text(requete, region="fr-fr", max_results=nb_resultats * 2):
            url = item.get("href") or ""
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https"):
                continue
            if "duckduckgo.com" in parsed.netloc:
                continue
            resultats.append(
                ResultatRecherche(
                    titre=item.get("title", ""),
                    url=url,
                    extrait=item.get("body", ""),
                )
            )
            if len(resultats) >= nb_resultats:
                break
    return resultats


def _rechercher_ddg(
    client: httpx.Client, requete: str, nb_resultats: int
) -> list[ResultatRecherche]:
    resp = client.post(
        "https://html.duckduckgo.com/html/", data={"q": requete, "kl": "fr-fr"}
    )
    if resp.status_code == 202:  # page anti-bot DuckDuckGo
        return []
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    resultats: list[ResultatRecherche] = []
    for bloc in soup.select("div.result, div.web-result"):
        lien = bloc.select_one("a.result__a")
        if not lien or not lien.get("href"):
            continue
        url = _decoder_lien_ddg(lien["href"])
        if not url:
            continue
        extrait_el = bloc.select_one(".result__snippet")
        resultats.append(
            ResultatRecherche(
                titre=lien.get_text(" ", strip=True),
                url=url,
                extrait=extrait_el.get_text(" ", strip=True) if extrait_el else "",
            )
        )
        if len(resultats) >= nb_resultats:
            break
    return resultats


def _rechercher_bing(
    client: httpx.Client, requete: str, nb_resultats: int
) -> list[ResultatRecherche]:
    resp = client.get(
        "https://www.bing.com/search",
        params={"q": requete, "setlang": "fr", "cc": "FR", "count": 20},
    )
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    resultats: list[ResultatRecherche] = []
    for bloc in soup.select("li.b_algo"):
        lien = bloc.select_one("h2 a[href]")
        if not lien:
            continue
        url = lien["href"]
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            continue
        if "bing.com" in parsed.netloc:  # publicites / redirections
            continue
        extrait_el = bloc.select_one(".b_caption p, p")
        resultats.append(
            ResultatRecherche(
                titre=lien.get_text(" ", strip=True),
                url=url,
                extrait=extrait_el.get_text(" ", strip=True) if extrait_el else "",
            )
        )
        if len(resultats) >= nb_resultats:
            break
    return resultats


def _decoder_lien_ddg(href: str) -> str | None:
    if href.startswith("//"):
        href = "https:" + href
    parsed = urlparse(href)
    if "duckduckgo.com" in parsed.netloc:
        # Redirection organique /l/?uddg=... : on decode la vraie cible.
        if parsed.path.startswith("/l/"):
            qs = parse_qs(parsed.query)
            if "uddg" in qs:
                return unquote(qs["uddg"][0])
        # Tout le reste (y.js = publicites/tracking) est ignore.
        return None
    if parsed.scheme in ("http", "https"):
        return href
    return None


# --------------------------------------------------------------------------- #
# Extraction de prix sur une page
# --------------------------------------------------------------------------- #
def _iter_offres_jsonld(obj: Any):
    """Parcourt un objet JSON-LD et rend les couples (nom_produit, offre)."""
    if isinstance(obj, list):
        for x in obj:
            yield from _iter_offres_jsonld(x)
        return
    if not isinstance(obj, dict):
        return
    if "@graph" in obj:
        yield from _iter_offres_jsonld(obj["@graph"])
    types = obj.get("@type", "")
    types = types if isinstance(types, list) else [types]
    nom = obj.get("name")
    if any("product" in str(t).lower() for t in types):
        offres = obj.get("offers")
        if offres is not None:
            for off in offres if isinstance(offres, list) else [offres]:
                if isinstance(off, dict):
                    yield nom, off
    if any("offer" in str(t).lower() for t in types):
        yield nom, obj


def _prix_depuis_jsonld(soup: BeautifulSoup) -> tuple[list[Prix], str | None]:
    prix: list[Prix] = []
    produit: str | None = None
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = script.string or script.get_text()
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            continue
        for nom, offre in _iter_offres_jsonld(data):
            valeur_brute = (
                offre.get("price")
                or offre.get("lowPrice")
                or (offre.get("priceSpecification") or {}).get("price")
                if isinstance(offre, dict)
                else None
            )
            if valeur_brute is None:
                continue
            devise = (
                offre.get("priceCurrency")
                or (offre.get("priceSpecification") or {}).get("priceCurrency")
                or "EUR"
            )
            prix.append(
                Prix(
                    valeur=_normaliser_nombre(str(valeur_brute)),
                    devise=str(devise),
                    texte_brut=str(valeur_brute),
                    source="json-ld",
                )
            )
            if nom and not produit:
                produit = nom
    return prix, produit


def _prix_depuis_meta(soup: BeautifulSoup) -> list[Prix]:
    prix: list[Prix] = []
    props = [
        ("meta", {"property": "product:price:amount"}, "content"),
        ("meta", {"property": "og:price:amount"}, "content"),
        ("meta", {"itemprop": "price"}, "content"),
        ("meta", {"name": "twitter:data1"}, "content"),
    ]
    devise = "EUR"
    for sel in (
        {"property": "product:price:currency"},
        {"property": "og:price:currency"},
        {"itemprop": "priceCurrency"},
    ):
        el = soup.find("meta", attrs=sel)
        if el and el.get("content"):
            devise = el["content"]
            break
    for tag, attrs, champ in props:
        el = soup.find(tag, attrs=attrs)
        if el and el.get(champ):
            brut = el[champ]
            val = _normaliser_nombre(brut)
            if val is not None:
                prix.append(Prix(val, devise, brut, "meta"))
    # microdata itemprop=price sur un element non-meta
    for el in soup.select('[itemprop="price"]'):
        brut = el.get("content") or el.get_text(" ", strip=True)
        val = _normaliser_nombre(brut) if brut else None
        if val is not None:
            prix.append(Prix(val, devise, brut, "microdata"))
    return prix


def _prix_depuis_regex(soup: BeautifulSoup) -> list[Prix]:
    texte = soup.get_text(" ", strip=True)
    trouves: list[Prix] = []
    vus: set[float] = set()
    for m in _PRICE_RE.finditer(texte):
        if not (m.group("sym1") or m.group("sym2")):
            continue  # pas de symbole monetaire -> on ignore
        val = _normaliser_nombre(m.group("num"))
        if val is None or val <= 0 or val in vus:
            continue
        vus.add(val)
        trouves.append(Prix(val, "EUR", m.group(0).strip(), "regex"))
        if len(trouves) >= 12:
            break
    return trouves


def _extraire_prix(url: str) -> RapportPrix:
    try:
        with _client() as client:
            resp = client.get(url)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "lxml")
    except Exception as exc:  # noqa: BLE001 - on renvoie l'erreur au client MCP
        return RapportPrix(url=url, produit=None, prix=[], methode="aucune", erreur=str(exc))

    for methode, fn in (
        ("json-ld", _prix_depuis_jsonld),
        ("meta/microdata", _prix_depuis_meta),
        ("regex", _prix_depuis_regex),
    ):
        if methode == "json-ld":
            liste, produit = fn(soup)
        else:
            liste, produit = fn(soup), None
        if liste:
            titre = None
            if not produit:
                og = soup.find("meta", attrs={"property": "og:title"})
                titre_el = soup.find("title")
                produit = (og["content"] if og and og.get("content") else None) or (
                    titre_el.get_text(strip=True) if titre_el else None
                )
            return RapportPrix(
                url=url,
                produit=produit,
                prix=[asdict(p) for p in liste],
                methode=methode,
            )

    titre_el = soup.find("title")
    return RapportPrix(
        url=url,
        produit=titre_el.get_text(strip=True) if titre_el else None,
        prix=[],
        methode="aucune",
        erreur="Aucun prix detecte sur la page.",
    )


# --------------------------------------------------------------------------- #
# Serveur MCP
# --------------------------------------------------------------------------- #
def _build_server():
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("verif-prix")

    @mcp.tool()
    def rechercher_prix(produit: str, nb_resultats: int = 8) -> dict[str, Any]:
        """Recherche des pages marchandes pour un produit et renvoie les URLs candidates.

        Args:
            produit: description du produit a chercher (ex : "deshydrateur alimentaire
                inox 10 plateaux professionnel"). Ajouter la marque/le modele affine.
            nb_resultats: nombre de resultats a renvoyer (defaut 8, max 20).

        Renvoie une liste {titre, url, extrait}. Appeler ensuite extraire_prix(url)
        sur les resultats pertinents pour obtenir le prix reel.
        """
        nb = max(1, min(int(nb_resultats), 20))
        res = _rechercher(produit, nb)
        return {"requete": produit, "nb": len(res), "resultats": [asdict(r) for r in res]}

    @mcp.tool()
    def extraire_prix(url: str) -> dict[str, Any]:
        """Recupere une page produit et en extrait le(s) prix detecte(s) en euros.

        Args:
            url: URL complete d'une page produit marchande.

        Renvoie {url, produit, prix:[{valeur, devise, texte_brut, source}], methode}.
        Priorite : donnees structurees schema.org (json-ld), puis meta/microdata,
        puis detection par motif. Verifier "source" pour juger de la fiabilite
        (json-ld/meta = fiable, regex = a confirmer).
        """
        return asdict(_extraire_prix(url))

    return mcp


def _selftest(argv: list[str]) -> int:
    # Si l'argument est une URL, on teste directement l'extraction.
    if argv and argv[0].startswith("http"):
        print(f"[selftest] extraction directe : {argv[0]}", file=sys.stderr)
        print(json.dumps(asdict(_extraire_prix(argv[0])), ensure_ascii=False, indent=2))
        return 0
    requete = argv[0] if argv else "deshydrateur alimentaire professionnel inox"
    print(f"[selftest] recherche : {requete!r}", file=sys.stderr)
    res = _rechercher(requete, 5)
    print(json.dumps([asdict(r) for r in res], ensure_ascii=False, indent=2))
    if res:
        print(f"\n[selftest] extraction sur : {res[0].url}", file=sys.stderr)
        rapport = _extraire_prix(res[0].url)
        print(json.dumps(asdict(rapport), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        args = [a for a in sys.argv[1:] if a != "--selftest"]
        raise SystemExit(_selftest(args))
    _build_server().run()
