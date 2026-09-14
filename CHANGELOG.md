# Historial de cambios

## Rediseño Cordillera y corrección de marcadores

### Presentación

- Capa editorial compartida en `editorial.css`: verde profundo, acentos cobre, composición asimétrica y fotografía existente del embalse.
- Tipografías Alegreya y Chivo servidas desde el proyecto, con sus licencias SIL OFL.
- Entrada animada mediante CSS y respeto de la preferencia de movimiento reducido.
- Menú móvil disponible también sin JavaScript.
- Números del catálogo vinculados a las referencias del mapa.

### Corrección del mapa

- Eliminado el desfase visual causado por el posicionamiento relativo de los marcadores HTML.
- Posicionamiento absoluto desde el origen del mapa, preservando las transformaciones de MapLibre.
- Datos territoriales y coordenadas originales conservados.
- Nueva prueba de regresión del contrato CSS y actualización de la caché del sitio.

### Documentación y verificación

- README actualizado con páginas, edición, pruebas, procedencia de fuentes tipográficas y explicación de la corrección.
- Once pruebas automatizadas verificadas en el entorno local: seis geográficas, cuatro de estructura y una de marcadores.
- La comprobación geográfica contra OSM depende de una captura local no versionada; el README distingue esta condición de las pruebas ejecutables en cualquier clon.
- La revisión automatizada no equivale a una validación institucional de los datos ni a una comprobación exhaustiva en todos los navegadores.

## Estructura de guía territorial — `a589536`

- Siete páginas principales y 25 fichas individuales de localidades e hitos.
- Filtros por localidad, valle y tipo, con enlaces bidireccionales entre fichas y mapa.
- Generación estática reproducible y compatibilidad con GitHub Pages.
- Redirección de los antiguos enlaces por ancla hacia las páginas correspondientes.

## Interfaz de visita y cartografía — `53ec900`

- Mapa MapLibre con OpenStreetMap y OpenTopoMap.
- Límite comunal BCN y áreas protegidas de las ediciones MMA 2023/2024.
- Fuentes y descargas de coberturas disponibles en la guía.

## Limitaciones vigentes

- No hay un flujo de alertas operativas en tiempo real conectado.
- “Sin información verificada” no significa habilitado ni cerrado.
- Los puntos son referencias territoriales, no límites de localidades ni accesos autorizados.
- La cartografía conserva sus fechas de origen; esta actualización no revisa categorías legales de protección ni condiciones de terreno.
