# Sitio web — Liceo de Ciencias y Artes

Nueva página de [liceodecienciasyartes.com](https://liceodecienciasyartes.com), copia exacta del
WordPress actual como sitio estático y publicada en GitHub Pages.

## Estructura
```
index.html, oferta-academica/, sobre-nosotros/, …   Páginas (copia exacta del WordPress)
wp-content/, wp-includes/                           Estilos, scripts, tipografías e imágenes
respaldo/                                           Contenido original del WordPress (no se publica)
scripts/espejo/                                     Herramienta que hizo la copia exacta
CLAUDE.md                                           Instrucciones para dar mantenimiento con Claude
```

## Publicación
GitHub Pages publica el sitio solo cada vez que se sube un cambio a `main`
(ver `.github/workflows/pages.yml`). Dirección actual: https://alfvasveg.github.io/liceo-web/

## Checklist antes de cambiar el dominio
El WordPress dejará de responder cuando el dominio apunte a GitHub Pages. Antes de eso:
- [x] Copia exacta de todas las páginas, imágenes y documentos.
- [ ] Conectar los formularios de Contáctanos y Trabaja con nosotros a un servicio de envío.
- [ ] Revisar en el panel del dominio si hay registros de correo (MX) del `.com` que conservar.
- [ ] Hacer una copia de seguridad completa del WordPress.

## Conectar el dominio
En el repositorio: **Settings → Pages → Custom domain** → `liceodecienciasyartes.com`.
Luego, en el panel donde está registrado el dominio, crear los registros DNS que indica GitHub
(cuatro registros A del dominio raíz y un CNAME de `www` hacia `alfvasveg.github.io`).
Al final, activar **Enforce HTTPS**.
