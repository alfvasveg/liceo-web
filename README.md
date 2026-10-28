# Sitio web — Liceo de Ciencias y Artes

Nueva página de [liceodecienciasyartes.com](https://liceodecienciasyartes.com), reconstruida desde el
WordPress actual como sitio estático y publicada en Cloudflare Pages.

## Estructura
```
index.html                  Página completa (todas las secciones)
assets/img/                 Imágenes
assets/docs/                PDFs (costos, código de convivencia)
_redirects                  Enlaces del sitio anterior → sitio nuevo
scripts/descargar-archivos.py   Copia imágenes y PDFs desde el WordPress
CLAUDE.md                   Instrucciones para dar mantenimiento con Claude
```

## Publicar en Cloudflare Pages
1. Entrar a dash.cloudflare.com → **Workers & Pages** → **Create** → **Pages** → **Connect to Git**.
2. Elegir este repositorio. Configuración de compilación:
   - Framework preset: **None**
   - Build command: *(vacío)*
   - Build output directory: `/`
3. **Save and Deploy**. Queda una dirección de prueba `….pages.dev` para revisar.
4. Cada cambio que se suba a `main` se publica solo.

## Checklist antes de cambiar el dominio
El WordPress dejará de responder cuando el dominio apunte a Cloudflare. Antes de eso:
- [ ] Correr `python3 scripts/descargar-archivos.py` y subir `assets/` al repositorio.
- [ ] Crear las páginas pendientes: Inscripciones, Trabaja con nosotros y los artículos del blog.
- [ ] Conectar el formulario de contacto a un servicio de envío.
- [ ] Revisar en el panel del dominio si hay registros de correo (MX) del `.com` que conservar.
- [ ] Hacer una copia de seguridad completa del WordPress.

## Conectar el dominio
En el proyecto de Pages → **Custom domains** → **Set up a custom domain** →
`liceodecienciasyartes.com` (y `www`). Cloudflare indica qué registros DNS cambiar.
