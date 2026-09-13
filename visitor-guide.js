// Preview: unknown until a dated operational report is supplied by the responsible source.
const sectors = [
  {name: 'San José de Maipo y localidades', valley: 'VALLE DEL MAIPO', description: 'Patrimonio, plazas y vida de pueblo. Explora el centro histórico, El Melocotón y San Alfonso.', source: 'Municipalidad', url: 'https://sanjosedemaipo.cl/turismo/'},
  {name: 'Embalse El Yeso', valley: 'VALLE DEL YESO', description: 'Paisaje de agua y alta montaña. Confirma la regulación vehicular y el estado del camino antes de subir.', source: 'Delegación de Cordillera', url: 'https://dppcordillera.dpp.gob.cl/'},
  {name: 'Monumento Natural El Morado', valley: 'VALLE DEL VOLCÁN', description: 'Paisaje glaciar y senderismo de montaña. Consulta condiciones de ingreso y reserva con CONAF.', source: 'CONAF · El Morado', url: 'https://www.conaf.cl/parque_nacionales/monumento-natural-el-morado/'},
  {name: 'Valle del Colorado', valley: 'VALLE DEL COLORADO', description: 'Paisajes cordilleranos y tradición arriera. Verifica el acceso específico de cada sendero con su administrador.', source: 'Municipalidad', url: 'https://sanjosedemaipo.cl/turismo/'}
].map(sector => ({...sector, status: 'unknown'}));

function renderConditions(filter = 'all') {
  const list = document.querySelector('#conditions-list');
  const visible = sectors.filter(sector => filter === 'all' || sector.status === filter);
  list.replaceChildren();
  if (!visible.length) {
    const message = document.createElement('p');
    message.className = 'conditions-empty';
    message.textContent = 'No hay sectores con este estado confirmado. Revisa “Por confirmar” y consulta la fuente responsable.';
    list.append(message);
  }
  for (const sector of visible) {
    const card = document.createElement('article');
    card.className = 'condition-card';
    const meta = document.createElement('p'); meta.className = 'eyebrow'; meta.textContent = sector.valley;
    const title = document.createElement('h3'); title.textContent = sector.name;
    const status = document.createElement('span'); status.className = 'condition-status'; status.textContent = '○ Por confirmar';
    const description = document.createElement('p'); description.textContent = sector.description;
    const date = document.createElement('small'); date.textContent = 'Última verificación de acceso: pendiente';
    const link = document.createElement('a'); link.href = sector.url; link.target = '_blank'; link.rel = 'noopener'; link.textContent = sector.source + ' ↗';
    card.append(meta, title, status, description, date, link); list.append(card);
  }
}
document.querySelectorAll('[data-condition]').forEach(button => button.addEventListener('click', () => {
  document.querySelectorAll('[data-condition]').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
  renderConditions(button.dataset.condition);
}));
renderConditions();
