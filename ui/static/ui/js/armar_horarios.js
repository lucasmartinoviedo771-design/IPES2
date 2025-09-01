(() => {
  // ========= helpers =========
  const $ = (sel, ctx = document) => ctx.querySelector(sel);
  const $$ = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel));
  const on = (el, ev, cb) => el && el.addEventListener(ev, cb);

  const fmt = (m) => `${String(Math.floor(m/60)).padStart(2,'0')}:${String(m%60).padStart(2,'0')}`;
  const mins = (hhmm) => { const [h,m] = hhmm.split(':').map(Number); return h*60+m };

  // ========= Turnos / grillas =========
  const TURNO_CANON_MAP = {
    m: 'm',        manana: 'm',    'mañana': 'm',
    t: 't',        tarde: 't',
    v: 'v',        vespertino: 'v', noche: 'v',
    s: 's',        sabado: 's',     'sábado': 's', 'sabado (manana)': 's'
  };

  const TURNO_LABEL = {
    m: 'Mañana',
    t: 'Tarde',
    v: 'Vespertino',
    s: 'Sábado (Mañana)',
  };

  const GRILLAS = {
    manana:     { start: mins('07:45'), end: mins('12:45'),
                  breaks:[[mins('09:05'),mins('09:15')],[mins('10:35'),mins('10:45')]] },
    tarde:      { start: mins('13:00'), end: mins('18:00'),
                  breaks:[[mins('14:20'),mins('14:30')],[mins('15:50'),mins('16:00')]] },
    vespertino: { start: mins('18:10'), end: mins('23:10'),
                  breaks:[[mins('19:30'),mins('19:40')],[mins('21:00'),mins('21:10')]] },
    sabado:     { start: mins('09:00'), end: mins('14:00'),
                  breaks:[[mins('10:20'),mins('10:30')],[mins('11:50'),mins('12:00')]] },
  };
  const BLOCK_MIN = 40;

  // ========= buscar elementos =========
  const selTurno = document.querySelector(
    '#id_turno, select[name="turno"], select[name*="turno" i], select[data-role="turno"]');
  let tbody = $('#grid-body');
  let selCount = $('#sel-count');
  let selTotal = $('#sel-total');

  (function ensureTable(){
    if (tbody) return;
    console.warn('[grid] No encontré #grid-body; genero tabla automáticamente');
    const target = $('#grid-auto-anchor') || $('.panel, .container, main') || document.body;
    const wrap = document.createElement('div');
    wrap.innerHTML = `
        <table id="grid-table" class="tabla grid">
          <thead>
            <tr>
              <th style="width:110px">Hora</th>
              <th>Lunes</th><th>Martes</th><th>Miércoles</th>
              <th>Jueves</th><th>Viernes</th><th>Sábado</th>
            </tr>
          </thead>
          <tbody id="grid-body"></tbody>
        </table>
        <div class="muted" style="margin-top:8px">
          Bloques seleccionados: <b id="sel-count">0</b> / <b id="sel-total">0</b>
        </div>`;
    target.appendChild(wrap);
    tbody = $('#grid-body');
    selCount = $('#sel-count');
    selTotal = $('#sel-total');
  })();

  // ========= sembrar/limpiar opciones de turno =========
  // normaliza texto: minúsculas, sin tildes, sin paréntesis/espacios
  function normKey(s) {
    return String(s ?? '')
      .toLowerCase()
      .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
      .replace(/[()]/g, '')
      .replace(/\s+/g, ' ')
      .trim();
  }

  // obtiene el código canónico a partir de item de API o string
  function turnoCanonCode(item) {
    const raw = (item?.slug ?? item?.id ?? item?.value ?? item ?? '').toString();
    const k = normKey(raw);
    return TURNO_CANON_MAP[k] ?? k;
  }

  function populateTurnos(selectEl, items) {
    selectEl.innerHTML = '';
    selectEl.add(new Option('---------', ''));

    const seen = new Set();
    for (const it of (items || [])) {
      const code = turnoCanonCode(it);
      if (!code || seen.has(code)) continue;
      seen.add(code);

      const label = TURNO_LABEL[code] ?? (it?.nombre ?? String(it));
      selectEl.add(new Option(label, code)); // Usamos el código canónico como value
    }
  }

  function loadTurnosOnce(itemsFromApi) {
    if (!selTurno || selTurno.dataset.loaded === '1') return;

    const fallback = [{id: 'm'}, {id: 't'}, {id: 'v'}, {id: 's'}];
    const items = Array.isArray(itemsFromApi) && itemsFromApi.length ? itemsFromApi : fallback;

    populateTurnos(selTurno, items);
    selTurno.dataset.loaded = '1';
  }

  // ========= construir filas =========
  function buildRows(turnoKey) {
    const g = GRILLAS[turnoKey];
    if (!g) return [];
    const rows = [];
    let t = g.start;

    const inBreak = (m) => g.breaks.find(([b]) => b === m);
    const nextBreak = (m) => g.breaks.find(([b]) => b > m);

    while (t < g.end) {
      const br = inBreak(t);
      if (br) { rows.push({type:'break', start:br[0], end:br[1]}); t = br[1]; continue; }
      const nb = nextBreak(t);
      const end = Math.min(t + BLOCK_MIN, nb ? nb[0] : g.end);
      rows.push({type:'block', start:t, end:end});
      t = end;
    }
    return rows;
  }

  function clearGrid(){ if (tbody) tbody.innerHTML = ''; }

  function renderGrid(rows){
    clearGrid();
    if (!tbody) return;
    let total = 0;

    rows.forEach(r => {
      const tr = document.createElement('tr');

      const tdL = document.createElement('td');
      tdL.className = r.type === 'break' ? 'recreo' : 'hora';
      tdL.textContent = r.type === 'break'
        ? `Recreo ${fmt(r.start)} - ${fmt(r.end)}`
        : `${fmt(r.start)} - ${fmt(r.end)}`;
      tr.appendChild(tdL);

      for (let day=1; day<=6; day++){
        const td = document.createElement('td');
        if (r.type === 'break') {
          td.className = 'celda recreo';
          td.style.opacity = .45;
          td.style.pointerEvents = 'none';
        } else {
          td.className = 'celda slot';
          td.dataset.day   = String(day);
          td.dataset.start = String(r.start);
          td.dataset.end   = String(r.end);
          td.addEventListener('click', () => { td.classList.toggle('sel'); updateCounter(); });
          total++;
        }
        tr.appendChild(td);
      }
      tbody.appendChild(tr);
    });

    if (selTotal) selTotal.textContent = String(total);
    updateCounter();
  }

  function updateCounter(){
    if (!selCount) return;
    selCount.textContent = String($$('.celda.slot.sel').length);
  }

  function selectedTurnoKey(){
    if (!selTurno) return null;
    const opt = selTurno.options[selTurno.selectedIndex];
    const val = (opt?.value || '').trim();
    if (val && GRILLAS[val]) return val;
    const label = (opt?.text || '').trim();
    return LABEL2KEY[label] || null;
  }

  function refreshGrid(){
    const key = selectedTurnoKey();
    if (!key) { clearGrid(); if (selTotal) selTotal.textContent = '0'; updateCounter(); return; }
    const rows = buildRows(key);
    renderGrid(rows);
  }

  // estilos mínimos
  (function injectStyles(){
    if (document.getElementById('grid-inline-css')) return;
    const style = document.createElement('style');
    style.id = 'grid-inline-css';
    style.textContent = `
      #grid-table{width:100%;border-collapse:separate;border-spacing:0 6px} 
      #grid-table thead th{text-align:center;font-weight:600;color:#5b5b5b} 
      #grid-table td.hora{font-weight:600;color:#5d5d3a;white-space:nowrap} 
      #grid-table td.celda{height:44px;border:1px dashed #e1d7c5;border-radius:10px;background:#fffdfa} 
      #grid-table td.celda.slot:hover{outline:2px solid rgba(197,119,60,.35);cursor:pointer} 
      #grid-table td.celda.sel{background:#f2e4d8;border-color:#cc8a54;box-shadow:inset 0 0 0 2px rgba(204,138,84,.55)} 
      #grid-table td.recreo{color:#9a7d5c;font-style:italic} 
    `;
    document.head.appendChild(style);
  })();

  // ========= init =========
  document.addEventListener('DOMContentLoaded', () => {
    seedTurnoOptionsIfNeeded();
    on(selTurno, 'change', refreshGrid);
    refreshGrid();
  });
})();
