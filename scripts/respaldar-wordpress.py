#!/usr/bin/env python3
"""Guarda una copia del contenido del WordPress actual en respaldo/:
- páginas y entradas del blog en JSON (API de WordPress), con su texto completo
- el HTML de cada dirección del sitemap

Sirve para reconstruir en el sitio nuevo las páginas que faltan y como respaldo.
Uso: python3 scripts/respaldar-wordpress.py
"""
import json
import pathlib
import re
import sys
import time
import urllib.request

BASE = "https://liceodecienciasyartes.com"
RAIZ = pathlib.Path(__file__).resolve().parent.parent
DEST = RAIZ / "respaldo"
UA = {"User-Agent": "Mozilla/5.0 (respaldo del sitio del Liceo)"}


def get(url: str) -> bytes:
    time.sleep(1.5)  # el sitio limita consultas seguidas
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
        return r.read()


def api(tipo: str) -> list:
    items, pagina = [], 1
    while True:
        try:
            lote = json.loads(get(f"{BASE}/wp-json/wp/v2/{tipo}?per_page=100&page={pagina}"))
        except Exception as e:  # noqa: BLE001
            if pagina == 1:
                print(f"API {tipo}: {e}")
            break
        if not lote:
            break
        items += lote
        pagina += 1
    return items


def sitemap_urls() -> list:
    pendientes = [f"{BASE}/wp-sitemap.xml", f"{BASE}/sitemap_index.xml", f"{BASE}/sitemap.xml"]
    vistos, paginas = set(), []
    while pendientes:
        u = pendientes.pop(0)
        if u in vistos:
            continue
        vistos.add(u)
        try:
            xml = get(u).decode("utf-8", "replace")
        except Exception:  # noqa: BLE001
            continue
        for loc in re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", xml):
            (pendientes if loc.endswith(".xml") else paginas).append(loc)
    return sorted(set(paginas))


def main() -> int:
    DEST.mkdir(exist_ok=True)
    for tipo in ("pages", "posts"):
        items = api(tipo)
        simple = [{
            "titulo": i.get("title", {}).get("rendered", ""),
            "slug": i.get("slug"),
            "fecha": i.get("date"),
            "enlace": i.get("link"),
            "extracto": i.get("excerpt", {}).get("rendered", ""),
            "contenido": i.get("content", {}).get("rendered", ""),
        } for i in items]
        (DEST / f"{tipo}.json").write_text(json.dumps(simple, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{tipo}: {len(simple)}")

    urls = sitemap_urls() or [f"{BASE}/{s}/" for s in (
        "inscripciones", "trabaja-con-nosotros", "oferta-academica", "sobre-nosotros",
        "instalaciones", "preguntas-frecuentes", "contactanos", "blog")]
    html_dir = DEST / "html"
    html_dir.mkdir(exist_ok=True)
    for u in urls:
        nombre = u.replace(BASE, "").strip("/").replace("/", "_") or "inicio"
        try:
            (html_dir / f"{nombre}.html").write_bytes(get(u))
            print("ok   ", u)
        except Exception as e:  # noqa: BLE001
            print("FALLO", u, e)
    (DEST / "direcciones.txt").write_text("\n".join(urls) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
