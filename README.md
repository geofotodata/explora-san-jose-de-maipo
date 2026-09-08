# Explora San José de Maipo

Prototipo de guía digital para la ZOIT San José de Maipo.

## Funciones

- Portada adaptable a celulares.
- Organización por cuatro valles.
- Fichas piloto de lugares.
- Mapa territorial esquemático.
- Rutas autoguiadas iniciales.
- Planificador basado en reglas.
- Favoritos locales.
- PWA y caché offline del contenido esencial.

## Advertencia

El contenido operativo es piloto. Antes de una publicación institucional deben validarse accesos, horarios, tarifas, condiciones, coordenadas, accesibilidad, derechos de imágenes y fuentes responsables.

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
