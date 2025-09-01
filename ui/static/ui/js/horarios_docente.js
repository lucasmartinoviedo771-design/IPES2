/* static/ui/js/horarios_docente.js */
import { buildGrid, paintItem } from "./horarios_common.js";

const $doc = document.getElementById("hd_docente");
const $turno = document.getElementById("hd_turno");
const $grid  = document.getElementById("hd_grid");

document.getElementById("hd_btn_imprimir").addEventListener("click", () => window.print());

// Docentes
(async function loadDocentes(){
  const url = new URL(API_DOCENTES, location.origin);
  const data = await fetch(url).then(r => r.json()).catch(()=>({items:[]}));
  (data.results || data.items || []).forEach(d => $doc.add(new Option(d.nombre, d.id)));
})();

$doc.addEventListener("change", render);
$turno.addEventListener("change", render);

async function render(){
  const turno = $turno.value;
  if (!turno) { $grid.innerHTML=""; return; }
  buildGrid($grid, turno);

  if (!$doc.value) return;

  const url = new URL(API_HDOC, location.origin);
  url.searchParams.set("docente_id", $doc.value);
  url.searchParams.set("turno", turno);

  const data = await fetch(url).then(r=>r.json()).catch(()=>({items:[]}));
  (data.items || []).forEach(ev => paintItem($grid, ev));
}
