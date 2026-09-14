"""Build the portable static guide from its catalog and preserved components."""
from pathlib import Path
from html import escape
import json
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
NAV = [('index.html', 'Inicio'), ('explora.html', 'Explora el Cajón'), ('planifica.html', 'Planifica tu visita'), ('condiciones.html', 'Estado de accesos'), ('mapa.html', 'Mapa'), ('naturaleza.html', 'Naturaleza y cultura'), ('acerca.html', 'Acerca de la guía')]


def slug(value: str) -> str:
    """Return a stable ASCII URL component."""
    text = unicodedata.normalize('NFD', value).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', text).strip('-')


def page(title: str, body: str, active: str, scripts: str = '', prefix: str = '') -> str:
    """Wrap content in the shared accessible navigation and footer."""
    links = ''.join(f'<a href="{prefix}{url}"' + (' aria-current="page"' if url == active else '') + f'>{label}</a>' for url, label in NAV)
    return f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)} · Explora San José de Maipo</title><meta name="description" content="Localidades, mapa territorial y planificación responsable de visitas a San José de Maipo.">
<meta name="theme-color" content="#102e2a"><link rel="icon" href="{prefix}assets/icon.svg"><link rel="manifest" href="{prefix}manifest.webmanifest">
<link rel="preload" href="{prefix}assets/fonts/alegreya.ttf" as="font" type="font/ttf" crossorigin><link rel="preload" href="{prefix}assets/fonts/chivo.ttf" as="font" type="font/ttf" crossorigin>
<link rel="stylesheet" href="{prefix}styles.css"><link rel="stylesheet" href="{prefix}visitor-guide.css"><link rel="stylesheet" href="{prefix}assets/vendor/maplibre-gl.css"><link rel="stylesheet" href="{prefix}territory-map.css"><link rel="stylesheet" href="{prefix}guide.css"><link rel="stylesheet" href="{prefix}editorial.css"></head>
<body class="{'page-home' if active == 'index.html' else 'page-interior'}"><a class="skip-link" href="#contenido">Saltar al contenido</a><header class="guide-header"><div class="container masthead"><a class="guide-brand" href="{prefix}index.html">EXPLORA <span>San José de Maipo</span></a><span class="guide-label">GUÍA DEL TERRITORIO</span><button id="guide-menu" aria-controls="guide-nav" aria-expanded="false" type="button">Menú</button></div><nav id="guide-nav" class="container guide-nav" aria-label="Navegación principal">{links}</nav></header>
<div class="guide-notice"><div class="container">Antes de viajar: consulta las condiciones de tu destino. <a href="{prefix}condiciones.html">Revisar accesos →</a></div></div>
<main id="contenido">{body}</main><footer class="guide-footer"><div class="container"><strong>Explora San José de Maipo</strong><p>Guía independiente en desarrollo. No es un canal oficial de emergencias.</p><nav aria-label="Enlaces del pie">{links}</nav><p>Los datos territoriales no acreditan apertura ni acceso público. <a href="{prefix}acerca.html#fuentes">Fuentes y fechas</a></p></div></footer><script src="{prefix}guide.js" defer></script>{scripts}</body></html>'''


def heading(title: str, description: str) -> str:
    """Render a section heading."""
    return f'<div class="container page-heading"><p class="eyebrow">San José de Maipo</p><h1>{title}</h1><p>{description}</p></div>'


def build() -> None:
    """Generate public pages without modifying territorial data."""
    legacy = (ROOT / 'templates/legacy.html').read_text(encoding='utf-8')
    features = json.loads((ROOT / 'data/map/localities.geojson').read_text(encoding='utf-8'))['features']
    features.sort(key=lambda item: item['properties']['number'])
    places = json.loads((ROOT / 'data/places.json').read_text(encoding='utf-8'))

    def section(identifier: str) -> str:
        match = re.search(r'<section\b[^>]*\bid="' + identifier + r'"[^>]*>.*?</section>', legacy, re.S)
        if match is None:
            raise ValueError(f'Missing legacy section: {identifier}')
        return match.group()

    def write(name: str, title: str, content: str, active: str, scripts: str = '', prefix: str = '') -> None:
        target = ROOT / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(page(title, content, active, scripts, prefix), encoding='utf-8')

    def cards(items: list[dict]) -> str:
        result = ''
        for feature in items:
            p = feature['properties']
            kind = 'Hito territorial' if p['kind'] == 'hito' else 'Localidad'
            result += f'<article class="directory-card" data-name="{escape(p["name"])}" data-sector="{escape(p["sector"])}" data-kind="{p["kind"]}"><span class="directory-number" aria-label="Referencia en el mapa {p["number"]}">{p["number"]:02d}</span><p class="eyebrow">{escape(p["sector"])}</p><h3><a href="localidades/{slug(p["name"])}.html">{escape(p["name"])}</a></h3><p>{kind}</p><div class="card-links"><a href="localidades/{slug(p["name"])}.html">Ver ficha →</a><a href="mapa.html?localidad={p["id"]}#mapa">Ver en mapa</a></div></article>'
        return result

    search = '<form action="explora.html" class="home-search"><label for="home-search">¿Qué localidad quieres conocer?</label><div><input id="home-search" name="q" type="search" placeholder="San Alfonso, El Canelo, Baños Morales…"><button class="button button-primary">Buscar</button></div></form>'
    home = '<section class="guide-hero"><div class="container hero-columns"><div><p class="eyebrow">Cordillera · Comunidades · Naturaleza</p><h1>Encuentra tu lugar<br>en el <em>Cajón del Maipo.</em></h1><p>Explora sus localidades y prepara tu visita con información del territorio.</p>' + search + '</div><figure class="hero-photo"><img src="assets/embalse-el-yeso.jpg" width="2000" height="1331" alt="Embalse El Yeso, montañas nevadas y cielo al atardecer" fetchpriority="high"><figcaption>Embalse El Yeso · <a href="https://commons.wikimedia.org/wiki/File:Embalse_el_Yeso_3.jpg">Chang Hyon Lee</a> · <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a>. Encuadre adaptado en pantalla; fotografía de 2016, no representa las condiciones actuales.</figcaption></figure></div></section>'
    home += '<section class="container home-section"><div class="section-heading"><p class="eyebrow">Comienza por un lugar</p><h2>Localidades para explorar</h2></div><div class="directory-grid">' + cards([f for f in features if f['properties']['number'] in [7,11,20]]) + '</div><a class="text-link" href="explora.html">Explorar todo el catálogo →</a></section>'
    home += '<section class="container home-section gateway-grid"><article><p class="eyebrow">01 · Explora</p><h2>Lee el territorio</h2><p>Localidades, límite comunal y áreas protegidas en un mismo mapa.</p><a href="mapa.html">Abrir el mapa →</a></article><article><p class="eyebrow">02 · Comprueba</p><h2>Antes de salir</h2><p>Consulta fuentes y condiciones. Una ubicación no es una confirmación de acceso.</p><a href="condiciones.html">Estado de accesos →</a></article><article><p class="eyebrow">03 · Planifica</p><h2>Prepara tu recorrido</h2><p>Actividades, orientación para tu visita y recomendaciones de seguridad.</p><a href="planifica.html">Planificar visita →</a></article></section><section class="container home-section"><h2>Un paisaje con historias</h2><p>Conoce las fuentes para explorar el patrimonio y la conservación del Cajón.</p><a href="naturaleza.html">Naturaleza y cultura →</a></section>'
    write('index.html', 'Inicio', home, 'index.html')

    sectors = sorted({f['properties']['sector'] for f in features})
    filters = '<div class="directory-tools"><label>Buscar por nombre<input id="directory-search" type="search" placeholder="Nombre de una localidad"></label><label>Valle o sector<select id="directory-sector"><option value="">Todos los sectores</option>' + ''.join(f'<option>{escape(s)}</option>' for s in sectors) + '</select></label><label>Tipo de lugar<select id="directory-kind"><option value="">Todos</option><option value="localidad">Localidades</option><option value="hito">Hitos territoriales</option></select></label></div><p id="directory-count" role="status">25 lugares de referencia</p>'
    directory = heading('Explora el Cajón', 'Encuentra una localidad, revisa su ficha y ubícala en el mapa. Los hitos turísticos se distinguen de los asentamientos.') + '<section class="container home-section" id="localidades">' + filters + '<div class="directory-grid">' + cards(features) + '</div><p id="directory-empty" hidden>No encontramos coincidencias. Prueba otro nombre o cambia los filtros.</p></section>'
    directory += '<section class="container home-section"><h2>Otras formas de explorar</h2><div class="gateway-grid"><article><h3>Valles y sectores</h3><p>Utiliza el selector de valle para agrupar los lugares del catálogo.</p><a href="#localidades">Explorar por valle ↑</a></article><article><h3>Áreas protegidas</h3><p>Consulta las coberturas MMA, sus categorías y fechas de referencia.</p><a href="naturaleza.html#areas">Ver áreas protegidas →</a></article><article><h3>Atractivos y patrimonio</h3><p>Una selección piloto de lugares y recorridos.</p><a href="planifica.html#explorar">Ver atractivos →</a></article></div></section>'
    write('explora.html', 'Explora el Cajón', directory, 'explora.html')

    conditions = heading('Estado de accesos', 'Sin información verificada no significa cerrado ni habilitado. El estado debe confirmarse para cada camino, sendero o recinto.') + section('condiciones')
    conditions = conditions.replace('Por confirmar', 'Sin información verificada').replace('por confirmar', 'sin información verificada')
    conditions += '<section class="container home-section"><h2>Qué debe indicar un reporte</h2><p>Camino, sendero o recinto afectado; estado; restricciones; fuente responsable; fecha de verificación y vigencia. Actualmente no hay reportes operativos incorporados.</p><p>Un cierre puntual no implica el cierre de una localidad completa.</p><a href="explora.html">Consultar fichas de localidades →</a></section>'
    write('condiciones.html', 'Estado de accesos', conditions, 'condiciones.html', '<script src="visitor-guide.js" defer></script>')
    write('mapa.html', 'Mapa del territorio', heading('Mapa del territorio', 'Explora los lugares del catálogo y las coberturas de referencia. El color de las áreas protegidas no representa su estado de apertura.') + section('mapa').replace('href="#condiciones"', 'href="condiciones.html"'), 'mapa.html', '<script src="assets/vendor/maplibre-gl.js" defer></script><script src="territory-map.js" defer></script>')

    dialog = re.search(r'<dialog\b.*?</dialog>', legacy, re.S).group()
    planning = heading('Planifica tu visita', 'Elige actividades y revisa lo necesario para viajar. Los recorridos son orientaciones piloto, no rutas operativas verificadas.')
    planning += '<section class="container home-section gateway-grid"><article id="transporte"><h2>Cómo llegar</h2><p>Ubica tu destino antes de organizar el transporte. El punto del catálogo no representa una ruta vehicular ni el acceso autorizado.</p><a href="mapa.html">Ubicar destino →</a></article><article id="servicios"><h2>Servicios turísticos</h2><p>Consulta información local y confirma directamente horarios, reservas y disponibilidad. Esta guía aún no tiene un directorio verificado de prestadores.</p><a href="https://sanjosedemaipo.cl/turismo/" target="_blank" rel="noopener">Turismo municipal ↗</a></article><article id="accesibilidad"><h2>Accesibilidad</h2><p>Consulta con el administrador las condiciones de movilidad, baños y estacionamiento. No contamos con una evaluación de accesibilidad por recinto.</p></article></section>'
    planning += section('explorar') + section('rutas') + section('planifica') + section('alertas') + dialog
    write('planifica.html', 'Planifica tu visita', planning, 'planifica.html', '<script src="app.js" defer></script>')

    protected = json.loads((ROOT / 'data/map/protected.geojson').read_text(encoding='utf-8'))['features']
    area_list = ''.join(f'<li><strong>{escape(f["properties"]["name"])}</strong> — {escape(f["properties"]["category"])} · {escape(str(f["properties"]["edition"]))}</li>' for f in protected)
    nature = heading('Naturaleza y cultura', 'Un punto de partida para conocer el territorio, su patrimonio y las fuentes de conservación.') + f'<section class="container home-section" id="areas"><h2>Áreas protegidas en la cartografía</h2><p>Estas coberturas intersectan el límite comunal de referencia. Algunas se extienden fuera de la comuna. Las categorías corresponden a las ediciones indicadas, no a una validación normativa actual.</p><ul class="area-list">{area_list}</ul><a href="mapa.html">Explorar las coberturas →</a></section>'
    nature += '<section class="container home-section gateway-grid"><article><h2>Biodiversidad y conservación</h2><p>Consulta los recursos del Ministerio del Medio Ambiente para profundizar en la biodiversidad regional.</p><a href="https://biodiversidadrm.mma.gob.cl/">Biodiversidad RM ↗</a></article><article><h2>Historia y comunidades</h2><p>Explora las localidades y los contenidos piloto de patrimonio. Sus fichas distinguen la ubicación documentada de la información pendiente de validar.</p><a href="planifica.html#explorar">Explorar patrimonio →</a></article></section>'
    nature += section('zoit')
    write('naturaleza.html', 'Naturaleza y cultura', nature, 'naturaleza.html')
    about = heading('Acerca de esta guía', 'Información territorial abierta para descubrir y planificar, con sus límites y fuentes a la vista.') + '<section class="container home-section prose" id="fuentes"><h2>Fuentes y actualización</h2><p>Localidades: catálogo municipal complementado con puntos de OpenStreetMap y topónimos BCN. Cada ficha identifica la fuente de sus coordenadas.</p><p>Límite comunal: <a href="https://www.bcn.cl/siit/mapas_vectoriales">BCN</a>, cartografía referencial, ediciones 2014–2018.</p><p>Áreas protegidas: <a href="https://biodiversidadrm.mma.gob.cl/wp-content/uploads/2024/01/AP_descarga_kmz.zip">MMA RM</a>, SNASPE 2023 y Santuarios 2024. No se han actualizado sus categorías legales en este rediseño.</p><p><a href="data/map/manifest.json">Ver procedencia y controles de datos</a> · <a href="mapa.html#map-sources">Fuentes cartográficas detalladas</a></p><h2>Condiciones de visita</h2><p>No hay un flujo de alertas en vivo conectado. La fecha de construcción de la web no es una fecha de verificación de accesos. Nunca interpretamos la ausencia de reporte como apertura.</p><h2>Contacto y correcciones</h2><p>Puedes comunicar errores de esta guía en el <a href="https://github.com/geofotodata/explora-san-jose-de-maipo/issues">repositorio del proyecto</a>. No uses ese canal para emergencias ni confirmaciones urgentes de acceso.</p></section>'
    write('acerca.html', 'Acerca de esta guía', about, 'acerca.html')

    for feature in features:
        p = feature['properties']
        related = next((item for item in places if slug(item['name']) == slug(p['name'])), None)
        description = related['description'] if related else f'{p["name"]} es un punto de referencia del catálogo territorial en {p["sector"]}. La información turística detallada está pendiente de validación.'
        detail = '<div class="container breadcrumbs"><a href="../explora.html">Explora el Cajón</a> / ' + escape(p['name']) + '</div>' + heading(escape(p['name']), escape(p['sector']))
        detail += '<section class="container detail-layout"><article><p class="eyebrow">' + ('Hito territorial' if p['kind'] == 'hito' else 'Localidad') + '</p><h2>Conoce este lugar</h2><p>' + escape(description) + '</p><p>' + escape(p.get('note') or 'La ubicación es referencial: no delimita la localidad ni identifica un acceso autorizado.') + '</p>'
        detail += f'<a class="button button-primary" href="../mapa.html?localidad={p["id"]}#mapa">Ver {escape(p["name"])} en el mapa →</a><h2>Qué conocer y cómo prepararte</h2>'
        if related:
            detail += '<ul>' + ''.join(f'<li>{escape(t)}</li>' for t in related['before']) + '</ul><p>Orientaciones del contenido piloto; confirma la información operativa antes de viajar.</p>'
        else:
            detail += '<p>Consulta las actividades del valle y confirma con el responsable del recinto los horarios, permisos y servicios antes de organizar una visita.</p>'
        detail += '<p><a href="../planifica.html">Actividades, transporte y servicios →</a></p><h2>Ubicación y procedencia</h2>'
        lon, lat = feature['geometry']['coordinates']
        detail += f'<p>Coordenadas de referencia: {lat:.5f}, {lon:.5f} · WGS84.</p><p>Fuente: <a href="{escape(p["source_url"])}">{escape(p["source"])}</a>. <a href="../acerca.html#fuentes">Fechas y alcance de los datos</a>.</p></article><aside class="access-panel"><p class="eyebrow">Antes de viajar</p><h2>Sin información verificada</h2><p>No hay un reporte operativo vigente asociado a esta ficha. Esto no significa que la localidad esté cerrada.</p><dl><dt>Verificación de acceso</dt><dd>Pendiente</dd><dt>Vigencia</dt><dd>No disponible</dd><dt>Fuente operativa</dt><dd>No incorporada</dd></dl><a href="../condiciones.html">Consultar fuentes de acceso →</a></aside></section>'
        write(f'localidades/{slug(p["name"])}.html', p['name'], detail, 'explora.html', prefix='../')


if __name__ == '__main__':
    build()
