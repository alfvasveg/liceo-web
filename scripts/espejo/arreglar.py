#!/usr/bin/env python3
"""Hace que la copia del WordPress funcione por sí sola.

- Cambia los enlaces a liceodecienciasyartes.com (normales, //, y escapados \\/ en JSON)
  por rutas relativas a los archivos copiados, para que el sitio funcione igual en
  alfvasveg.github.io/liceo-web/ y en el dominio.
- Descarga lo que falte (por ejemplo otros tamaños de imagen de un srcset).
- Deja intactos los metadatos que deben seguir apuntando al dominio (canonical, og:, JSON-LD).

Uso: python3 scripts/espejo/arreglar.py <carpeta_espejo>
"""
import os
import pathlib
import re
import sys
import time
import urllib.request
from urllib.parse import unquote

HOST = "liceodecienciasyartes.com"
BASE = f"https://{HOST}"
UA = {"User-Agent": "Mozilla/5.0 (copia del sitio del Liceo)"}

RUTA = r"(?:\\/|[^\"'\s<>()\\&])*"
ABSOLUTA = re.compile(r"(?:https?:)?(?:\\/\\/|//)(?:www\.)?liceodecienciasyartes\.com(?P<ruta>" + RUTA + r")")
RAIZ_REL = re.compile(r"(?<=[\"'(=\s,])(?P<ruta>(?:\\?/)(?:wp-content|wp-includes)(?:\\/|/)" + RUTA + r")")
PROTEGER_TAG = re.compile(r"canonical|og:|twitter:|shortlink|alternate|EditURI|pingback|dns-prefetch|preconnect|api\.w\.org")
LDJSON = re.compile(r"(?is)<script[^>]+application/ld\+json[^>]*>.*?</script>")

faltantes: list[str] = []
descargados = 0


def descargar(ruta: str, destino: pathlib.Path, query: str) -> bool:
    global descargados
    url = BASE + ruta + (("?" + query) if query else "")
    try:
        time.sleep(0.3)
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
            datos = r.read()
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(datos)
        descargados += 1
        return True
    except Exception as e:  # noqa: BLE001
        faltantes.append(f"{url}  ({e})")
        return False


def local_de(salida: pathlib.Path, ruta: str, query: str) -> tuple[pathlib.Path, bool] | None:
    """Devuelve (archivo o carpeta local, es_carpeta) o None si no hay copia local."""
    ruta = unquote(ruta) or "/"
    if re.match(r"^/(wp-content|wp-includes)/", ruta):
        destino = salida / ruta.lstrip("/")
        if ruta.endswith("/"):
            return destino, True  # carpeta base (p. ej. assets de Elementor)
        if destino.exists() or descargar(ruta, destino, query):
            return destino, False
        return None
    carpeta = salida / ruta.strip("/")
    if (carpeta / "index.html").exists():
        return carpeta, True
    return None


def relativa(desde: pathlib.Path, hacia: pathlib.Path, es_carpeta: bool) -> str:
    rel = os.path.relpath(hacia, desde).replace(os.sep, "/")
    if es_carpeta:
        rel = "./" if rel == "." else rel + "/"
    return rel


def procesar(salida: pathlib.Path, archivo: pathlib.Path) -> bool:
    texto = archivo.read_text("utf-8", "replace")
    original = texto
    protegidos: list[str] = []

    def guardar(m):
        protegidos.append(m.group(0))
        return f"\x00LDJSON{len(protegidos)-1}\x00"

    texto = LDJSON.sub(guardar, texto)

    def cambiar(m):
        inicio = texto.rfind("<", 0, m.start())
        etiqueta = texto[inicio:m.start()] if inicio != -1 and m.start() - inicio < 400 else ""
        if archivo.suffix == ".html" and PROTEGER_TAG.search(etiqueta):
            return m.group(0)
        bruta = m.group("ruta")
        escapada = "\\/" in m.group(0)
        ruta = bruta.replace("\\/", "/")
        ruta, _, query = ruta.partition("?")
        if re.match(r"^/(wp-json|wp-admin|xmlrpc\.php|wp-login\.php|feed)", ruta):
            return m.group(0)
        hallado = local_de(salida, ruta, query)
        if hallado is None:
            return m.group(0) if m.group(0).startswith(("http", "//", "\\/\\/")) else (BASE + ruta + ("?" + query if query else ""))
        rel = relativa(archivo.parent, *hallado)
        return rel.replace("/", "\\/") if escapada else rel

    texto = ABSOLUTA.sub(cambiar, texto)
    texto = RAIZ_REL.sub(cambiar, texto)
    texto = re.sub(r"\x00LDJSON(\d+)\x00", lambda m: protegidos[int(m.group(1))], texto)
    if texto != original:
        archivo.write_text(texto, "utf-8")
        return True
    return False


def main() -> int:
    salida = pathlib.Path(sys.argv[1]).resolve()
    archivos = [p for p in salida.rglob("*") if p.suffix in (".html", ".css", ".js") and p.is_file()]
    # Primero HTML y CSS (pueden descargar archivos nuevos), luego otra pasada para los recién bajados
    for ronda in range(2):
        cambiados = sum(procesar(salida, p) for p in archivos)
        print(f"ronda {ronda+1}: {cambiados} archivos ajustados")
        archivos = [p for p in salida.rglob("*") if p.suffix in (".html", ".css", ".js") and p.is_file()]
    restantes = sum(len(ABSOLUTA.findall(p.read_text("utf-8", "replace"))) for p in salida.rglob("*.html"))
    print(f"descargados: {descargados} · enlaces al dominio que quedan en HTML (metadatos incluidos): {restantes}")
    (salida / "_faltantes.txt").write_text("\n".join(faltantes) + "\n", "utf-8")
    print(f"no se pudieron bajar: {len(faltantes)} (ver _faltantes.txt)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
