// --- Lógica para cargar Planes de Estudio dinámicamente ---
(function () {
  const form = document.querySelector('form[data-planes-url]');
  if (!form) return;

  const urlPlanes = form.dataset.planesUrl;
  const planSelect = document.getElementById('id_plan');
  const profSelect = document.getElementById('id_profesorado');
  const planErrEl  = document.getElementById('plan-error');

  function resetPlanSelect(sel) {
    sel.innerHTML = "";
    const opt = document.createElement("option");
    opt.value = "";
    opt.textContent = "— Seleccioná un plan —";
    sel.appendChild(opt);
    sel.value = "";
  }

  function populatePlanes(sel, items) {
    resetPlanSelect(sel);
    for (const it of items) {
      const opt = document.createElement("option");
      opt.value = it.id;
      opt.textContent = it.label;
      sel.appendChild(opt);
    }
    if (items.length === 1) {
      sel.value = String(items[0].id);
      sel.dispatchEvent(new Event("change"));
    }
  }

  async function fetchPlanes(url) {
    try {
      const r = await fetch(url, {credentials: "same-origin"});
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const data = await r.json();
      return data.items || [];
    } catch (err) {
      console.error("Error cargando planes:", err);
      alert("No pudimos cargar los planes. Probá recargar la página.");
      return [];
    }
  }

  async function loadPlanesFor(profId) {
    planSelect.disabled = true;
    resetPlanSelect(planSelect);
    if (!profId) return;

    const url = `${urlPlanes}?prof_id=${encodeURIComponent(profId)}`;
    const items = await fetchPlanes(url);
    populatePlanes(planSelect, items);
    planSelect.disabled = items.length === 0;
  }

  if (profSelect && profSelect.value) loadPlanesFor(profSelect.value);
  if (profSelect) profSelect.addEventListener('change', () => loadPlanesFor(profSelect.value));

})();

// --- Lógica de visibilidad de requisitos de inscripción ---
(function () {
    const form = document.querySelector('form[data-planes-url]');
    if (!form) return;

    const carreraSelect = form.querySelector('[name="profesorado"]');

    // Nuevos IDs de los grupos de campos
    const grupoTituloSecundario = document.getElementById('id_grupo_titulo_secundario');
    const grupoTituloSuperior = document.getElementById('id_grupo_titulo_superior');
    const grupoAdeudaMaterias = document.getElementById('id_grupo_adeuda_materias');

    // Checkboxes
    const checkTituloSec = form.querySelector('[name="req_titulo_sec"]');
    const checkTituloTramite = form.querySelector('[name="req_titulo_tramite"]');
    const checkAdeuda = form.querySelector('[name="req_adeuda"]');
    const mutualExclusionGroup = [checkTituloSec, checkTituloTramite, checkAdeuda];

    function handleCarreraChange() {
        if (!carreraSelect) return;

        const selectedOption = carreraSelect.options[carreraSelect.selectedIndex];
        const isCertDocente = selectedOption.text.includes(window.CERT_DOCENTE_LABEL || 'Certificación Docente');

        if (isCertDocente) {
            // Ocultar grupo secundario y mostrar superior
            if (grupoTituloSecundario) grupoTituloSecundario.style.display = 'none';
            if (grupoTituloSuperior) grupoTituloSuperior.style.display = 'block';

            // Desmarcar checkboxes ocultos para que no se envíen
            mutualExclusionGroup.forEach(chk => { if(chk) chk.checked = false; });

        } else {
            // Mostrar grupo secundario y ocultar superior
            if (grupoTituloSecundario) grupoTituloSecundario.style.display = 'block';
            if (grupoTituloSuperior) grupoTituloSuperior.style.display = 'none';

            // Desmarcar checkboxes ocultos
            const checkTituloSup = form.querySelector('[name="req_titulo_sup"]');
            const checkIncumbencias = form.querySelector('[name="req_incumbencias"]');
            if (checkTituloSup) checkTituloSup.checked = false;
            if (checkIncumbencias) checkIncumbencias.checked = false;
        }
        // Forzar la reevaluación de los detalles de materias adeudadas
        toggleAdeudaMateriasDetails();
    }

    function handleMutualExclusion(event) {
        const currentCheckbox = event.target;
        if (currentCheckbox.checked) {
            mutualExclusionGroup.forEach(checkbox => {
                if (checkbox !== currentCheckbox) checkbox.checked = false;
            });
        }
        toggleAdeudaMateriasDetails();
    }

    function toggleAdeudaMateriasDetails() {
        if (grupoAdeudaMaterias) {
            const shouldShow = checkAdeuda && checkAdeuda.checked;
            grupoAdeudaMaterias.style.display = shouldShow ? 'block' : 'none';
            if (!shouldShow) {
                const matInput = form.querySelector('[name="req_adeuda_mats"]');
                const instInput = form.querySelector('[name="req_adeuda_inst"]');
                if (matInput) matInput.value = '';
                if (instInput) instInput.value = '';
            }
        }
    }

    // --- Inicialización y Event Listeners ---
    mutualExclusionGroup.forEach(checkbox => {
        if (checkbox) checkbox.addEventListener('change', handleMutualExclusion);
    });

    if (carreraSelect) carreraSelect.addEventListener('change', handleCarreraChange);

    // Estado inicial al cargar la página
    document.addEventListener('DOMContentLoaded', () => {
        handleCarreraChange();
        toggleAdeudaMateriasDetails();
    });
})();