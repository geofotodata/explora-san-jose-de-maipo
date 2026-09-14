# Explora San José de Maipo

Prototipo de guía digital para la ZOIT San José de Maipo.

[Abrir la guía publicada](https://geofotodata.github.io/explora-san-jose-de-maipo/) · [Historial de cambios](CHANGELOG.md)

## Estructura del sitio

| Página | Contenido |
| --- | --- |
| `index.html` | Portada editorial y búsqueda de localidades. |
| `explora.html` | Catálogo filtrable por nombre, sector y tipo de lugar. |
| `planifica.html` | Atractivos, recorridos piloto, servicios y seguridad. |
| `condiciones.html` | Fuentes de consulta y estados pendientes de verificación. |
| `mapa.html` | Localidades, límite comunal y coberturas de áreas protegidas. |
| `naturaleza.html` | Conservación, patrimonio y contexto territorial. |
| `acerca.html` | Procedencia, limitaciones y contacto del proyecto. |

Las 25 fichas de `localidades/` tienen direcciones propias y enlazan al punto correspondiente del mapa. El catálogo distingue localidades de hitos territoriales.

## Funciones

- Portada adaptable a celulares.
- Organización por cuatro valles.
- Fichas piloto de lugares.
- Mapa MapLibre con localidades, límite BCN y áreas protegidas MMA.
- Siete páginas principales y 25 fichas estáticas de localidades e hitos.
- Buscador por nombre, valle y tipo; enlaces bidireccionales ficha–mapa.
- Rutas autoguiadas iniciales.
- Planificador basado en reglas.
- Favoritos locales.
- PWA y caché offline del contenido esencial.

## Advertencia

El contenido operativo es piloto. Antes de una publicación institucional deben validarse accesos, horarios, tarifas, condiciones, coordenadas, accesibilidad, derechos de imágenes y fuentes responsables.

## Editar y verificar la estructura

El sitio sigue siendo HTML/CSS/JavaScript estático y compatible con GitHub Pages. No requiere un servidor de aplicación ni servicios de pago.

- `scripts/build_site.py`: plantilla compartida, portada, navegación y fichas.
- `templates/legacy.html`: componentes preservados de planificación, condiciones y mapa.
- `guide.css` y `guide.js`: presentación, navegación móvil y filtros.
- `editorial.css`: dirección visual Cordillera, tokens de color, tipografías locales y animación de entrada con alternativa de movimiento reducido.
- `data/map/localities.geojson`: catálogo geográfico utilizado para generar fichas, sin alterar sus coordenadas.
- Las páginas HTML generadas se incluyen en Git para publicarlas sin compilación en GitHub Pages. No editarlas directamente: regenerarlas desde sus fuentes.

Con Python 3.11 o posterior, desde la raíz:

```sh
python scripts/build_site.py
python -m unittest discover -s scripts -p test_site.py -v
python -m unittest discover -s scripts -p test_marker_style.py -v
```

Estas cinco pruebas no necesitan dependencias geográficas: revisan enlaces y anclas locales, una ficha por punto, un título principal por página, IDs únicos, generación reproducible y el contrato CSS de posicionamiento de los marcadores.

Para ejecutar también las seis pruebas geográficas, prepara un entorno con `scripts/requirements-geo-lock.txt` y ejecuta `python -m unittest discover -s scripts -p 'test_*.py' -v`. La comparación contra la captura OSM requiere `data/raw/localidades_osm.json`, un insumo local del procesamiento geográfico que no se incluye en Git; en un clon nuevo esa prueba no puede ejecutarse hasta disponer de dicho insumo. No se necesita para servir el sitio ni para las cinco pruebas anteriores.

### Corrección del desplazamiento de localidades

Los marcadores personalizados comparten elemento con `.maplibregl-marker`. Una regla `position: relative` agregaba la posición del elemento dentro del flujo HTML al desplazamiento geográfico calculado por MapLibre, haciendo que los puntos aparecieran separados hacia el este.

La regla `.locality-pin.maplibregl-marker` conserva `position: absolute`, `top: 0`, `left: 0` y `margin: 0`, sin sobrescribir el `transform` que controla MapLibre. No se alteraron coordenadas, proyecciones ni polígonos. `scripts/test_marker_style.py` protege este contrato frente a futuras modificaciones visuales.

La caché pasa a `explora-maipo-v6-marker-position`. Si se conserva una pestaña antigua después de publicar, recargar para obtener los nuevos estilos; esto no actualiza ni verifica los estados operativos de acceso.

Los enlaces antiguos como `index.html#mapa` se redirigen a su nueva página. Las fichas visitadas pueden quedar en caché; si una ficha no fue guardada, el modo sin conexión indica que no está disponible, en vez de mostrar otra página. Nunca se consideran los datos guardados como confirmación de acceso.

### Fotografía

`assets/embalse-el-yeso.jpg`: [Embalse el Yeso 3](https://commons.wikimedia.org/wiki/File:Embalse_el_Yeso_3.jpg), Chang Hyon Lee, 2016, [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Archivo original conservado, encuadre de presentación mediante CSS; la adaptación visual mantiene esa licencia. No representa condiciones actuales.

### Tipografía y accesibilidad visual

Alegreya (normal e itálica) y Chivo se sirven desde `assets/fonts/`, sin solicitudes a Google Fonts durante la visita. Procedencia: repositorio oficial [google/fonts](https://github.com/google/fonts), familias `ofl/alegreya` y `ofl/chivo`. Se conservan sus licencias SIL Open Font License junto a los archivos descargados; no se han modificado las fuentes.

Los números del catálogo corresponden a las referencias del mapa, no a una clasificación turística. La entrada animada utiliza solo CSS, no oculta contenido mediante JavaScript y respeta `prefers-reduced-motion`. El menú móvil sigue accesible si JavaScript no está disponible. La capa visual no cambia colores temáticos, coordenadas, estados operativos ni datos cartográficos.

### Publicación y reversión

Antes de publicar, regenerar y ejecutar las pruebas. Revisar `git diff` y subir los cambios al repositorio autorizado. El rediseño no modifica las coberturas originales ni sus clasificaciones. Para volver a una versión anterior publicada, revertir el commit del rediseño en Git y publicar esa reversión; no borrar los datos ni restablecer el repositorio de forma destructiva.

## Trabajar desde cualquier equipo

El código fuente vive en GitHub. Cada equipo usa su propio clon local y se sincroniza con `git pull` y `git push`; no copies carpetas manualmente entre computadores.

### Opción recomendada: GitHub Codespaces

Codespaces permite editar y ejecutar el sitio desde el navegador, sin instalar el proyecto en el equipo.

1. Abre el repositorio en GitHub: <https://github.com/geofotodata/explora-san-jose-de-maipo>.
2. Selecciona **Code** → **Codespaces** → **Create codespace on main**.
3. En la terminal del Codespace ejecuta `python3 -m http.server 8080`.
4. Abre el puerto 8080 en la vista previa. Al terminar, confirma tus cambios con Git desde el panel de control de código fuente o con los comandos de abajo.

El archivo `.devcontainer/devcontainer.json` incluido configura automáticamente ese entorno y también funciona al abrir el repositorio con Dev Containers en VS Code.

### Desarrollo local

Primero instala [Git](https://git-scm.com/downloads) y [Python 3](https://www.python.org/downloads/) en cada equipo. Luego clona una sola vez:

```sh
git clone https://github.com/geofotodata/explora-san-jose-de-maipo.git
cd explora-san-jose-de-maipo
```

Inicia el servidor HTTP y abre <http://localhost:8080>:

```powershell
# Windows PowerShell
.\scripts\serve.ps1
```

```sh
# macOS, Linux o terminal de Codespaces
sh ./scripts/serve.sh
```

Puedes indicar otro puerto si el 8080 está ocupado: `./scripts/serve.ps1 -Port 8081` en Windows o `sh ./scripts/serve.sh 8081` en macOS/Linux.

### Sincronizar cambios entre equipos

Antes de empezar a trabajar en un equipo, actualiza su copia:

```sh
git pull --ff-only
```

Cuando termines una tarea, guarda tus cambios en GitHub:

```sh
git status
git add .
git commit -m "Describe el cambio"
git push origin main
```

Si trabajas en más de un computador al mismo tiempo, crea una rama por tarea para evitar conflictos:

```sh
git switch -c nombre-de-la-tarea
git push -u origin nombre-de-la-tarea
```

Después crea un Pull Request en GitHub para integrar esa rama a `main`. No subas archivos con contraseñas, claves API ni configuraciones personales: `.gitignore` ya descarta los archivos locales más habituales.
