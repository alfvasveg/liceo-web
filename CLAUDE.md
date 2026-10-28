# Instrucciones para Claude: sitio web del Liceo de Ciencias y Artes

Sitio público de la Unidad Educativa Liceo de Ciencias y Artes (Quito, Ecuador).
Dominio: liceodecienciasyartes.com · Hosting: GitHub Pages (se publica solo al hacer push a `main`, vía `.github/workflows/pages.yml`).
Vista actual: https://alfvasveg.github.io/liceo-web/

## Cómo está hecho
- Sitio estático, sin compilación: HTML, CSS y JavaScript en `index.html`.
- Las secciones (Inicio, Oferta Académica, Sobre nosotros, Instalaciones, Preguntas frecuentes,
  Blog, Contáctanos) son bloques `<div class="view" id="v-...">` que se muestran según el `#` de la URL.
  Para agregar una sección: crear su bloque, sumar su nombre a `routes` en el script y al menú y pie.
- Colores y tipografías: variables en el `:root` del `<style>`. Mantener modo claro y oscuro.
- Imágenes en `assets/img/`, documentos (PDF) en `assets/docs/`. Rutas relativas (`assets/...`), para que funcionen igual en github.io/liceo-web y en el dominio.
- Si se agregan carpetas o archivos al sitio, sumarlos al paso "Preparar archivos del sitio" del workflow.
- `_redirects` queda de referencia para un posible paso a Cloudflare; GitHub Pages no lo usa.

## Al hacer cambios
- Todo el contenido en español de Ecuador; teléfonos con el formato que ya usa el sitio.
- Probar en ancho de celular (unos 380 px): nada debe desbordar hacia los lados.
- No subir datos de estudiantes a este repositorio: es público. Los datos viven en el
  sistema de gestión de estudiantes, que se integrará aparte (por ejemplo, un enlace
  o subdominio tipo `sistema.liceodecienciasyartes.com`).
