/* MapLibre 5.6.2. Static, traceable coverages; no operational access inference. */
(() => {
  'use strict';
  const byId = id => document.getElementById(id);
  const normalize = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase('es');
  const osmAttribution = '© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors';
  let map, points, boundary, protectedAreas, selectedId, popup;
  let ready = false;
  const markers = new Map();
  const controls = ['map-basemap', 'map-fit-places', 'map-fit-boundary', 'layer-localities', 'layer-boundary', 'layer-snaspe', 'layer-sanctuaries'];
  controls.forEach(id => { byId(id).disabled = true; });

  function notice(message) {
    byId('map-load-status').textContent = message;
    byId('map-load-status').hidden = !message;
  }

  function safeLink(url, label) {
    const link = document.createElement('a');
    const parsed = new URL(url, location.href);
    if (!['http:', 'https:'].includes(parsed.protocol)) throw new Error('Protocolo de fuente no permitido');
    link.href = parsed.href; link.target = '_blank'; link.rel = 'noopener'; link.textContent = label;
    return link;
  }

  function paragraph(text) {
    const node = document.createElement('p'); node.textContent = text; return node;
  }

  function localityContent(feature) {
    const p = feature.properties;
    const content = document.createElement('div');
    const title = document.createElement('h3'); title.textContent = `${p.number}. ${p.name}`;
    content.append(title, paragraph(`${p.sector} · ${p.kind === 'hito' ? 'Hito territorial' : 'Localidad'}`));
    content.append(paragraph(p.note || 'Punto de referencia del asentamiento; no delimita su extensión.'));
    const sourceLine = paragraph('Coordenadas: ');
    sourceLine.append(safeLink(p.source_url, p.source)); content.append(sourceLine);
    if (p.provider === 'bcn') content.append(paragraph('Cartografía BCN referencial; posición aproximada.'));
    content.append(paragraph('Acceso: por confirmar. Esta ubicación no acredita apertura para visitas.'));
    const slug = normalize(p.name).replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
    const detailLink = document.createElement('a');
    detailLink.href = `localidades/${slug}.html`;
    detailLink.textContent = 'Ver ficha completa →';
    content.append(detailLink);
    return content;
  }

  function selectLocality(feature, fly = true) {
    selectedId = feature.properties.id;
    byId('map-detail').replaceChildren(localityContent(feature));
    document.querySelectorAll('.locality-item').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.id === selectedId)));
    markers.forEach(({button}, id) => button.setAttribute('aria-pressed', String(id === selectedId)));
    if (!map || !ready) return;
    byId('layer-localities').checked = true;
    // The list remains authoritative and searchable even when map layers are hidden.
    updateMarkers();
    if (popup) popup.remove();
    popup = new maplibregl.Popup({offset: 20, maxWidth: '300px'}).setLngLat(feature.geometry.coordinates).setDOMContent(localityContent(feature)).addTo(map);
    if (fly) map.flyTo({center: feature.geometry.coordinates, zoom: 12, duration: matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : 650});
    updateLabels();
  }

  function visibleFeatures() {
    const query = normalize(byId('locality-search').value.trim());
    return points.features.filter(feature => normalize(`${feature.properties.name} ${feature.properties.sector}`).includes(query));
  }

  function renderList() {
    const visible = visibleFeatures();
    const list = byId('locality-list'); list.replaceChildren();
    byId('locality-count').textContent = `${visible.length} de ${points.features.length} lugares · 23 del listado municipal + 2 complementarios`;
    if (!visible.length) list.append(paragraph('No encontramos ese nombre. Prueba con otra localidad o valle.'));
    for (const feature of visible) {
      const p = feature.properties;
      const button = document.createElement('button'); button.type = 'button'; button.className = 'locality-item'; button.dataset.id = p.id;
      button.setAttribute('aria-pressed', String(p.id === selectedId));
      const number = document.createElement('span'); number.className = 'locality-number'; number.textContent = p.number;
      const name = document.createElement('span'); name.textContent = p.name;
      const subtitle = document.createElement('small'); subtitle.textContent = `${p.sector}${p.kind === 'hito' ? ' · Hito' : ''}`;
      name.append(subtitle); button.append(number, name);
      button.addEventListener('click', () => selectLocality(feature)); list.append(button);
    }
    updateMarkers();
  }

  function updateMarkers() {
    const visible = new Set(visibleFeatures().map(feature => feature.properties.id));
    markers.forEach(({button}, id) => { button.style.display = byId('layer-localities').checked && visible.has(id) ? '' : 'none'; });
    updateLabels();
  }

  function updateLabels() {
    if (!map || !ready) return;
    const occupied = [];
    const ordered = [...markers.values()].sort((a, b) => Number(b.feature.properties.id === selectedId) - Number(a.feature.properties.id === selectedId) || Number(!!b.feature.properties.capital) - Number(!!a.feature.properties.capital));
    for (const {feature, label, button} of ordered) {
      const p = feature.properties;
      const xy = map.project(feature.geometry.coordinates);
      const width = p.name.length*7+18;
      const alignLeft = xy.x+32+width > map.getContainer().clientWidth;
      label.style.left = alignLeft ? 'auto' : '32px';
      label.style.right = alignLeft ? '32px' : 'auto';
      const rect = {x: alignLeft ? xy.x-32-width : xy.x+20, y: xy.y-12, w: width, h: 28};
      const collides = occupied.some(other => rect.x < other.x+other.w && rect.x+rect.w > other.x && rect.y < other.y+other.h && rect.y+rect.h > other.y);
      const visible = button.style.display !== 'none' && xy.x > 0 && xy.y > 0 && xy.x < map.getContainer().clientWidth && xy.y < map.getContainer().clientHeight;
      label.hidden = !(visible && (!collides || p.id === selectedId) && (map.getZoom() >= 8.5 || p.capital || p.id === selectedId));
      if (!label.hidden) occupied.push(rect);
    }
  }

  function fitBox(bbox) {
    map.fitBounds([[bbox[0], bbox[1]], [bbox[2], bbox[3]]], {padding: {top:50, bottom:70, left:45, right:65}, maxZoom:11, duration:0});
  }

  function setBasemap() {
    if (!ready) return;
    const value = byId('map-basemap').value;
    notice('');
    map.setLayoutProperty('osm-base', 'visibility', ['soft','osm'].includes(value) ? 'visible' : 'none');
    map.setLayoutProperty('topo-base', 'visibility', value === 'topo' ? 'visible' : 'none');
    map.setPaintProperty('osm-base', 'raster-saturation', value === 'soft' ? -0.85 : 0);
    map.setPaintProperty('osm-base', 'raster-opacity', value === 'soft' ? 0.75 : 1);
  }

  function showProtected(feature, lngLat) {
    const p = feature.properties;
    const content = document.createElement('div');
    const title = document.createElement('h3'); title.textContent = p.name;
    content.append(title, paragraph(`${p.category} · Capa ${p.edition}`), paragraph('La cobertura intersecta el límite BCN. Puede incluir sectores fuera de la comuna.'), paragraph('La figura de protección no confirma acceso público ni apertura.'), safeLink(p.source_url, p.source));
    byId('map-detail').replaceChildren(content.cloneNode(true));
    if (popup) popup.remove();
    popup = new maplibregl.Popup({maxWidth:'320px'}).setLngLat(lngLat).setDOMContent(content).addTo(map);
  }

  async function fetchGeoJSON(file) {
    const response = await fetch(`data/map/${file}.geojson`, {signal: AbortSignal.timeout(15000)});
    if (!response.ok) throw new Error(`No se pudo cargar ${file}`);
    const data = await response.json();
    if (data.type !== 'FeatureCollection' || !data.features.length || !Array.isArray(data.bbox)) throw new Error(`Cobertura inválida: ${file}`);
    return data;
  }

  async function initialize() {
    try {
      [points, boundary, protectedAreas] = await Promise.all(['localities','boundary','protected'].map(fetchGeoJSON));
      points.features.sort((a,b) => a.properties.number-b.properties.number);
      renderList();
      byId('locality-search').addEventListener('input', renderList);
      if (!window.maplibregl) throw new Error('No se pudo cargar el visor. El listado y las fichas siguen disponibles.');
      map = new maplibregl.Map({container: 'territory-map', center: [-70.26,-33.7], zoom:9.5, minZoom:7, maxZoom:18, renderWorldCopies:false,
        locale:{'NavigationControl.ZoomIn':'Acercar','NavigationControl.ZoomOut':'Alejar','FullscreenControl.Enter':'Pantalla completa','FullscreenControl.Exit':'Salir de pantalla completa','Popup.Close':'Cerrar ficha','AttributionControl.ToggleAttribution':'Mostrar atribuciones'},
        cooperativeGestures:true, attributionControl:false,
        style:{version:8, sources:{
          osm:{type:'raster', tiles:['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],tileSize:256,maxzoom:19,attribution:osmAttribution},
          topo:{type:'raster',tiles:['https://a.tile.opentopomap.org/{z}/{x}/{y}.png'],tileSize:256,maxzoom:17,attribution:`${osmAttribution} · SRTM · <a href="https://opentopomap.org/about" target="_blank" rel="noopener">OpenTopoMap (CC-BY-SA)</a>`},
        },layers:[{id:'background',type:'background',paint:{'background-color':'#f1f2eb'}},
          {id:'osm-base',type:'raster',source:'osm',paint:{'raster-saturation':-0.85,'raster-opacity':0.75}},
          {id:'topo-base',type:'raster',source:'topo',layout:{visibility:'none'}}]}});
      map.addControl(new maplibregl.NavigationControl({showCompass:false}), 'top-right');
      map.addControl(new maplibregl.FullscreenControl({container:byId('territory-workspace')}), 'top-right');
      map.addControl(new maplibregl.ScaleControl({unit:'metric',maxWidth:100}), 'bottom-left');
      map.addControl(new maplibregl.AttributionControl({compact:true,customAttribution:'Límite: BCN · AP: MMA RM 2023/24'}), 'bottom-right');
      map.scrollZoom.disable();
      map.on('error', event => {
        console.warn('Mapa territorial:', event.error?.message || event);
        notice('No se pudo cargar un recurso del mapa. Prueba otro mapa base; el listado de localidades sigue disponible.');
      });
      map.once('load', () => {
        map.addSource('boundary',{type:'geojson',data:boundary});
        map.addSource('protected',{type:'geojson',data:protectedAreas});
        map.addLayer({id:'boundary-fill',type:'fill',source:'boundary',paint:{'fill-color':'#78529b','fill-opacity':0.035}});
        for (const [id,group,color] of [['snaspe','snaspe','#007c65'],['sanctuaries','santuario','#ad7028']]) {
          const filter = ['==',['get','group'],group];
          map.addLayer({id:`${id}-fill`,type:'fill',source:'protected',filter,paint:{'fill-color':color,'fill-opacity':0.22}});
          map.addLayer({id:`${id}-line`,type:'line',source:'protected',filter,paint:{'line-color':color,'line-width':1.8}});
          map.on('click',`${id}-fill`,event => showProtected(event.features[0],event.lngLat));
          map.on('mouseenter',`${id}-fill`,() => { map.getCanvas().style.cursor='pointer'; });
          map.on('mouseleave',`${id}-fill`,() => { map.getCanvas().style.cursor=''; });
        }
        map.addLayer({id:'boundary-halo',type:'line',source:'boundary',paint:{'line-color':'#fff','line-width':5}});
        map.addLayer({id:'boundary-line',type:'line',source:'boundary',paint:{'line-color':'#75479c','line-width':2.8,'line-dasharray':[3,2]}});
        for (const feature of points.features) {
          const p = feature.properties;
          const button = document.createElement('button'); button.type='button'; button.className='locality-pin';
          button.dataset.kind=p.kind; button.dataset.capital=String(!!p.capital); button.textContent=p.number;
          button.setAttribute('aria-label', `${p.number}. ${p.name}, ${p.kind === 'hito' ? 'hito territorial' : 'localidad'}`); button.setAttribute('aria-pressed','false');
          const label=document.createElement('span'); label.className='locality-pin-label'; label.textContent=p.name; label.hidden=true; button.append(label);
          button.addEventListener('click', event => {event.stopPropagation(); selectLocality(feature);});
          const marker=new maplibregl.Marker({element:button}).setLngLat(feature.geometry.coordinates).addTo(map);
          markers.set(p.id,{marker,button,label,feature});
        }
        ready=true; controls.forEach(id => {byId(id).disabled=false;});
        notice(''); fitBox(points.bbox); updateMarkers();
        const requested = new URLSearchParams(location.search).get('localidad');
        const feature = points.features.find(item => item.properties.id === requested);
        if (feature) selectLocality(feature);
        map.on('move',updateLabels);
        new ResizeObserver(() => {map.resize(); updateLabels();}).observe(byId('territory-map'));
      });
      byId('map-basemap').addEventListener('change',setBasemap);
      byId('map-fit-places').addEventListener('click',() => { if(popup) popup.remove(); fitBox(points.bbox); });
      byId('map-fit-boundary').addEventListener('click',() => { if(popup) popup.remove(); fitBox(boundary.bbox); });
      byId('layer-localities').addEventListener('change',updateMarkers);
      for (const [id,layers] of [['boundary',['boundary-fill','boundary-halo','boundary-line']],['snaspe',['snaspe-fill','snaspe-line']],['sanctuaries',['sanctuaries-fill','sanctuaries-line']]]) {
        byId(`layer-${id}`).addEventListener('change',event => layers.forEach(layer => map.setLayoutProperty(layer,'visibility',event.target.checked?'visible':'none')));
      }
    } catch (error) {
      console.error('No fue posible iniciar el mapa territorial',error);
      notice(`${error.message} Puedes consultar las fuentes y descargar las coberturas debajo del mapa.`);
      if (!points) byId('locality-count').textContent='No se cargaron las localidades. Recarga la página para volver a intentarlo.';
    }
  }
  initialize();
})();
