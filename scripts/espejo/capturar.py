#!/usr/bin/env python3
"""Copia exacta del sitio WordPress del Liceo, tal como lo ve un visitante.

Abre cada página del sitio actual en un navegador real (Chromium), en ancho de
computadora y de celular, baja hasta el final para que carguen las imágenes
diferidas y abre el menú móvil. Guarda cada archivo que el navegador recibe del
dominio (HTML, CSS, JS, tipografías, imágenes) con la misma ruta que tiene en el
servidor, dentro de la carpeta de salida.

Uso: python3 scripts/espejo/capturar.py <carpeta_salida>
Requiere: pip install playwright && playwright install --with-deps chromium
"""
import pathlib
import re
import sys
import time
from urllib.parse import urlsplit, unquote, urljoin

from playwright.sync_api import sync_playwright

HOST = "liceodecienciasyartes.com"
BASE = f"https://{HOST}"
PAGINAS = [
    "/", "/oferta-academica/", "/sobre-nosotros/", "/instalaciones/", "/preguntas-frecuentes/",
    "/blog/", "/contactanos/", "/inscripciones/", "/trabaja-con-nosotros/",
    "/2024/06/14/tareas-hechas-con-inteligencia-artificial/",
    "/2024/12/13/el-arte-como-eje-transversal-para-la-evaluacion-en-el-liceo-de-cienciasy-artes-de-quito/",
    "/2024/12/13/sistema-boletas-disciplina-liceo-ciencias-artes-quito/",
    "/author/liceodecienciasyartes/", "/category/uncategorized/",
]
VISTAS = [
    {"viewport": {"width": 1440, "height": 900}},
    {"viewport": {"width": 390, "height": 844}, "is_mobile": True, "has_touch": True, "device_scale_factor": 2},
]
OMITIR = re.compile(r"^/(wp-json|wp-admin|wp-login\.php|xmlrpc\.php|feed|comments)(/|$)|/feed/?$")


def ruta_local(salida: pathlib.Path, url: str, es_pagina: bool) -> pathlib.Path | None:
    partes = urlsplit(url)
    if partes.hostname not in (HOST, "www." + HOST):
        return None
    ruta = unquote(partes.path) or "/"
    if OMITIR.search(ruta):
        return None
    if es_pagina or ruta.endswith("/"):
        ruta = ruta.rstrip("/") + "/index.html"
    destino = (salida / ruta.lstrip("/")).resolve()
    if salida.resolve() not in destino.parents:
        return None
    return destino


def main() -> int:
    salida = pathlib.Path(sys.argv[1]).resolve()
    salida.mkdir(parents=True, exist_ok=True)
    guardados: dict[str, pathlib.Path] = {}
    css_vistos: set[pathlib.Path] = set()

    with sync_playwright() as pw:
        nav = pw.chromium.launch()
        for vista in VISTAS:
            ctx = nav.new_context(**vista, user_agent=None, locale="es-EC")
            pag = ctx.new_page()

            def al_responder(resp, pag=pag):
                try:
                    if resp.request.method != "GET" or resp.status != 200:
                        return
                    url = resp.url.split("#")[0]
                    es_pagina = resp.request.resource_type == "document"
                    destino = ruta_local(salida, url, es_pagina)
                    if destino is None:
                        return
                    clave = str(destino)
                    if clave in guardados and not es_pagina:
                        return
                    cuerpo = resp.body()
                    destino.parent.mkdir(parents=True, exist_ok=True)
                    destino.write_bytes(cuerpo)
                    guardados[clave] = destino
                    if destino.suffix == ".css":
                        css_vistos.add(destino)
                except Exception as e:  # noqa: BLE001
                    print("aviso:", resp.url, e)

            pag.on("response", al_responder)
            for p in PAGINAS:
                url = BASE + p
                print(f"[{vista['viewport']['width']}px] {url}")
                try:
                    pag.goto(url, wait_until="networkidle", timeout=90000)
                except Exception as e:  # noqa: BLE001
                    print("  no cargó del todo:", e)
                for _ in range(40):
                    pag.mouse.wheel(0, 700)
                    time.sleep(0.25)
                pag.wait_for_timeout(1500)
                if vista.get("is_mobile"):
                    for sel in (".ast-mobile-menu-trigger-minimal", ".menu-toggle", ".elementor-menu-toggle"):
                        try:
                            pag.locator(sel).first.click(timeout=1500)
                            pag.wait_for_timeout(800)
                            break
                        except Exception:  # noqa: BLE001
                            pass
                try:
                    pag.wait_for_load_state("networkidle", timeout=15000)
                except Exception:  # noqa: BLE001
                    pass
                time.sleep(1)
            ctx.close()

        # Recursos citados dentro de los CSS que el navegador no pidió (otros tamaños, :hover, fuentes)
        ctx = nav.new_context()
        pendientes = list(css_vistos)
        revisados = set()
        while pendientes:
            css = pendientes.pop()
            if css in revisados:
                continue
            revisados.add(css)
            rel = css.relative_to(salida).as_posix()
            url_css = f"{BASE}/{rel}"
            texto = css.read_text("utf-8", "replace")
            for ref in re.findall(r"url\(\s*['\"]?([^'\")]+)['\"]?\s*\)", texto) + re.findall(r"@import\s+['\"]([^'\"]+)['\"]", texto):
                if ref.startswith("data:"):
                    continue
                absoluta = urljoin(url_css, ref.split("#")[0])
                destino = ruta_local(salida, absoluta.split("?")[0], False)
                if destino is None or destino.exists():
                    continue
                try:
                    r = ctx.request.get(absoluta, timeout=30000)
                    if r.ok:
                        destino.parent.mkdir(parents=True, exist_ok=True)
                        destino.write_bytes(r.body())
                        if destino.suffix == ".css":
                            pendientes.append(destino)
                        print("  css ->", absoluta)
                except Exception as e:  # noqa: BLE001
                    print("aviso:", absoluta, e)
                time.sleep(0.3)
        nav.close()

    print(f"\n{len(guardados)} archivos guardados en {salida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
