#!/usr/bin/env python3
"""Descarga las imágenes y PDFs que hoy viven en el WordPress del Liceo
y cambia las rutas de index.html para que apunten a las copias locales.

Hay que correrlo UNA vez, ANTES de apuntar el dominio a GitHub Pages
(después de cambiarlo, el WordPress deja de responder y los archivos se pierden).

Uso (desde la carpeta del repositorio):
    python3 scripts/descargar-archivos.py
"""
import pathlib
import re
import sys
import urllib.request

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PAGINAS = sorted(RAIZ.glob("*.html"))
PATRON = re.compile(r"https://liceodecienciasyartes\.com/wp-content/uploads/[^\"')\s]+")
DESTINOS = {".pdf": "assets/docs", ".docx": "assets/docs", ".doc": "assets/docs"}  # el resto va a assets/img


def main() -> int:
    urls = sorted({u for p in PAGINAS for u in PATRON.findall(p.read_text(encoding="utf-8"))})
    if not urls:
        print("No quedan enlaces al WordPress. Nada que hacer.")
        return 0

    reemplazos, fallos = {}, []
    for url in urls:
        nombre = url.rsplit("/", 1)[-1]
        carpeta = DESTINOS.get(pathlib.Path(nombre).suffix.lower(), "assets/img")
        destino = RAIZ / carpeta / nombre
        destino.parent.mkdir(parents=True, exist_ok=True)
        try:
            if not destino.exists():
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=30) as r:
                    destino.write_bytes(r.read())
            reemplazos[url] = f"{carpeta}/{nombre}"
            print("ok   ", nombre)
        except Exception as e:  # noqa: BLE001
            fallos.append((url, e))
            print("FALLO", nombre, "->", e)

    for p in PAGINAS:
        texto = p.read_text(encoding="utf-8")
        for viejo, nuevo in reemplazos.items():
            texto = texto.replace(viejo, nuevo)
        p.write_text(texto, encoding="utf-8")

    print(f"\n{len(reemplazos)} archivos descargados y enlazados, {len(fallos)} fallos.")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
