/* ui/static/ui/js/armar_horarios.js
   Arma la grilla de horarios y aplica todos los estilos visuales directamente
   para evitar conflictos con hojas de estilo externas.
*/
(() => {
  // --- Definición de Estilos --- (Aplicados directamente a los elementos)
  const styleBase = `height: 46px; border-radius: 12px; text-align: center; vertical-align: middle; padding: 0; transition: background .12s ease, border-color .12s ease;`;
  const styleClickable = `background: #F7F4EE; border: 1px solid #E6E2D8; cursor: pointer;`;
  const styleBreak = `background: #F4F1E9; border: 1px solid #E6E2D8; color: #6E6A60; font-style: italic; pointer-events: none;`;
  const styleSelected = `background: #E6F6EE; border: 1px solid #6DC597; cursor: pointer; box-shadow: inset 0 0 0 2px rgba(109,197,151,.25);`;

  // --- Configuración de turnos y recreos (formato HH:MM) ---
  const GRILLAS = {
    manana: { label: "Mañana", start: "07:45", end: "12:45", breaks: [["09:05","09:15"], ["10:35","10:45"]], },
    tarde: { label: "Tarde", start: "13:00", end: "18:00", breaks: [["14:20","14:30"], ["15:50","16:00"]], },
    vespertino: { label: "Vespertino", start: "18:10", end: "23:10", breaks: [["19:30","19:40"], ["21:00","21:10"]], },
    sabado: { label: "Sábado (Mañana)", start: "09:00", end: "14:00", breaks: [["10:20","10:30"], ["11:50","12:00"]], },
  };

  const BLOCK_MIN = 40;
  const DAYS = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado"];

  let currentSlots = [];
  let maxSelectable = 0;

  const toMinutes = (hhmm) => { const [h, m] = hhmm.split(":").map(Number); return h*60 + m; };
  const fmt = (min) => { const h = Math.floor(min/60); const m = min % 60; return `${String(h).padStart(2,"0")}:${String(m).padStart(2,"0")}`; };

  function buildSlots(turnoCfg) {
    const start = toMinutes(turnoCfg.start), end = toMinutes(turnoCfg.end);
    const breaks = turnoCfg.breaks.map(([a,b]) => [toMinutes(a), toMinutes(b)]).sort((x,y)=>x[0]-y[0]);
    const slots = [];
    let cur = start;
    for (const [bStart, bEnd] of breaks) {
      while (cur + BLOCK_MIN <= bStart) { slots.push({from: cur, to: cur + BLOCK_MIN, isBreak: false}); cur += BLOCK_MIN; }
      if (cur < bStart) cur = bStart;
      slots.push({from: bStart, to: bEnd, isBreak: true});
      cur = bEnd;
    }
    while (cur + BLOCK_MIN <= end) { slots.push({from: cur, to: cur + BLOCK_MIN, isBreak: false}); cur += BLOCK_MIN; }
    return slots;
  }

  function ensureInfoAndTable() {
    let host = document.getElementById("ah-grid");
    if (!host) { host = document.body; }

    let info = document.getElementById("ah-info");
    if (!info) {
      info = document.createElement("div");
      info.id = "ah-info";
      info.style.margin = "6px 0 12px";
      info.innerHTML = `Bloques seleccionados: <strong id="ah-count">0</strong> / <span id="ah-max">0</span>`;
      host.appendChild(info);
    }

    let table = document.getElementById("ah-grid-table");
    if (!table) {
      table = document.createElement("table");
      table.id = "ah-grid-table";
      table.style.width = "100%";
      table.style.tableLayout = "fixed";
      table.style.borderCollapse = "separate";
      table.style.borderSpacing = "10px 8px";

      const thead = document.createElement("thead");
      const hr = document.createElement("tr");
      const th0 = document.createElement("th");
      th0.textContent = "Hora";
      th0.style.width = "150px";
      th0.style.textAlign = "left";
      hr.appendChild(th0);
      for (const d of DAYS) { const th = document.createElement("th"); th.textContent = d; th.style.textAlign = "center"; hr.appendChild(th); }
      thead.appendChild(hr);

      const tbody = document.createElement("tbody");
      tbody.id = "ah-grid-body";
      tbody.addEventListener("click", onCellClick);

      table.appendChild(thead);
      table.appendChild(tbody);
      host.appendChild(table);
    }
    return {tbody: document.getElementById("ah-grid-body")};
  }

  function clearNode(n){ while(n && n.firstChild) n.removeChild(n.firstChild); }

  function renderGrid(turnoKey) {
    const cfg = GRILLAS[turnoKey];
    if (!cfg) return;

    const {tbody} = ensureInfoAndTable();
    clearNode(tbody);

    currentSlots = buildSlots(cfg);
    maxSelectable = currentSlots.filter(s => !s.isBreak).length * DAYS.length;
    document.getElementById("ah-max").textContent = maxSelectable;
    updateCount();

    for (const slot of currentSlots) {
      const tr = document.createElement("tr");
      const tdTime = document.createElement("td");
      tdTime.textContent = `${fmt(slot.from)} – ${fmt(slot.to)}`;
      tdTime.style.cssText = `font-weight: 600; color: #5B5141; border: 0; background: transparent;`;
      tr.appendChild(tdTime);

      for (let dayIdx=0; dayIdx<DAYS.length; dayIdx++) {
        const td = document.createElement("td");
        td.className = "ah-cell";
        if (slot.isBreak) {
          td.textContent = "Recreo";
          td.classList.add("ah-break");
          td.style.cssText = styleBase + styleBreak;
        } else {
          td.dataset.day  = String(dayIdx);
          td.classList.add("ah-clickable");
          td.style.cssText = styleBase + styleClickable;
        }
        tr.appendChild(td);
      }
      tbody.appendChild(tr);
    }
  }

  function updateCount() {
    const countEl = document.getElementById("ah-count");
    if (!countEl) return;
    countEl.textContent = document.querySelectorAll("#ah-grid-body td.is-selected").length;
  }

  function onCellClick(ev) {
    const cell = ev.target.closest("td.ah-clickable");
    if (!cell) return;
    const isSelected = cell.classList.toggle("is-selected");
    cell.style.cssText = styleBase + (isSelected ? styleSelected : styleClickable);
    updateCount();
  }

  function seedTurnoOptions() {
    const sel = document.getElementById("id_turno");
    if (!sel) return null;
    if (sel.options.length > 1) return sel;
    sel.innerHTML = "";
    const opt0 = document.createElement("option");
    opt0.value = ""; opt0.textContent = "--------"; sel.appendChild(opt0);
    for (const [key, cfg] of Object.entries(GRILLAS)) { const opt = document.createElement("option"); opt.value = key; opt.textContent = cfg.label; sel.appendChild(opt); }
    return sel;
  }

  function turnoKeyFromSelectValue(val) {
    if (!val) return null;
    if (GRILLAS[val]) return val;
    const entry = Object.entries(GRILLAS).find(([,cfg]) => cfg.label === val);
    return entry ? entry[0] : null;
  }

  document.addEventListener("DOMContentLoaded", () => {
    const selTurno = seedTurnoOptions();
    if (!selTurno) return;
    const key0 = turnoKeyFromSelectValue(selTurno.value);
    if (key0) renderGrid(key0);
    selTurno.addEventListener("change", (e) => {
      const key = turnoKeyFromSelectValue(e.target.value);
      if (!key) { const {tbody} = ensureInfoAndTable(); clearNode(tbody); currentSlots = []; maxSelectable = 0; document.getElementById("ah-max").textContent = "0"; updateCount(); return; }
      renderGrid(key);
    });
  });
})();