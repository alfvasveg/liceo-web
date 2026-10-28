# Instrucciones para Claude: sitio web del Liceo de Ciencias y Artes

Sitio público de la Unidad Educativa Liceo de Ciencias y Artes (Quito, Ecuador).
Dominio: liceodecienciasyartes.com · Hosting: GitHub Pages (se publica solo al hacer push a `main`,
vía `.github/workflows/pages.yml`). Vista actual: https://alfvasveg.github.io/liceo-web/

## Cómo está hecho
- Es una **copia exacta** del WordPress anterior (tema Astra + Elementor + Smart Slider), sin WordPress
  detrás: HTML, CSS, JS, tipografías e imágenes estáticos. El dueño pidió que se vea idéntico al original.
- Cada página es `<ruta>/index.html` con la misma dirección que tenía en WordPress
  (`oferta-academica/`, `sobre-nosotros/`, `2024/12/13/<artículo>/`, etc.). El inicio es `index.html`.
- Estilos, scripts e imágenes viven en `wp-content/` y `wp-includes/`, con las mismas rutas del servidor.
  Imágenes subidas: `wp-content/uploads/AAAA/MM/`. Documentos (PDF, hoja de inscripción) también ahí.
- Todos los enlaces internos son **relativos** (`../oferta-academica/`, `wp-content/...`), para que funcionen
  igual en github.io/liceo-web y en el dominio. Al editar, mantenerlos relativos.
- Los metadatos (`canonical`, `og:`, JSON-LD) siguen apuntando a https://liceodecienciasyartes.com a propósito.
- `respaldo/` guarda el contenido original del WordPress (JSON de páginas y artículos, HTML); no se publica.
- `scripts/espejo/` y `.github/workflows/espejo-wordpress.yml` rehacen la copia desde el WordPress.
  **No volver a correrlos** después de cambiar el dominio ni después de editar el sitio: borrarían los cambios.
- La rama `diseno-nuevo` guarda un rediseño propio que el dueño descartó por ahora.

## Al hacer cambios
- Para cambiar un texto: buscarlo en el `index.html` de esa página y reemplazarlo ahí. Si aparece en el menú
  o el pie, está repetido en todas las páginas: cambiarlo en todas.
- No alterar las clases de Elementor (`elementor-*`, `e-con`, `data-id`, `data-settings`): de ellas depende el diseño.
- Todo el contenido en español de Ecuador; teléfonos con el formato que ya usa el sitio.
- Revisar en ancho de celular (unos 390 px) además de computadora.
- Los formularios de Elementor (Contáctanos, Trabaja con nosotros) ya no envían: dependían de WordPress.
  Hay que conectarlos a un servicio externo.
- No subir datos de estudiantes a este repositorio: es público. Los datos viven en el sistema de gestión
  de estudiantes, que se integrará aparte (por ejemplo, `sistema.liceodecienciasyartes.com`).
