const plantillasPredial = {};

function inicializarPlantillaCuentaPredial(conceptoForm, index) {
    const container = conceptoForm.querySelector("#cuentapredial-formset-container");
    const formulario = container?.querySelector(".formulario-cuentapredial-item");
    if (formulario) {
        const prefix = `predial-${index}`;
        plantillasPredial[prefix] = formulario.cloneNode(true);
    }
}

function agregarCuentaPredialDesdeBoton(boton) {
    const conceptoForm = boton.closest(".formulario-concepto");
    const index = [...document.querySelectorAll('.formulario-concepto')].indexOf(conceptoForm);
    const prefix = `predial-${index}`;
    const contenedor = conceptoForm.querySelector("#cuentapredial-formset-container");
    const totalFormsInput = conceptoForm.querySelector(`#id_${prefix}-TOTAL_FORMS`);

    if (!plantillasPredial[prefix]) return;

    const total = parseInt(totalFormsInput.value || 0);
    const nuevo = plantillasPredial[prefix].cloneNode(true);

    nuevo.querySelectorAll("[name], [id], label").forEach(el => {
        if (el.name) el.name = el.name.replace(/predial-\d+-\d+-/, `${prefix}-${total}-`);
        if (el.id) el.id = el.id.replace(/id_predial-\d+-\d+-/, `id_${prefix}-${total}-`);
        if (el.htmlFor) el.htmlFor = el.htmlFor.replace(/predial-\d+-\d+-/, `${prefix}-${total}-`);
    });

    nuevo.querySelectorAll("input, select, textarea").forEach(el => {
        if (el.name.includes("-id")) el.remove();
        else if (!el.name.includes("DELETE")) el.value = "";
        else if (el.type === "checkbox") el.checked = false;
    });

    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "btn btn-sm btn-danger btn-delete-cuentapredial";
    btn.style = "position:absolute; top:0.5rem; right:0.5rem;";
    btn.innerHTML = '<i class="fas fa-trash-alt"></i>';
    nuevo.appendChild(btn);

    contenedor.appendChild(nuevo);
    totalFormsInput.value = total + 1;
    actualizarBotonesEliminarCuentaPredial(contenedor);
}

function actualizarBotonesEliminarCuentaPredial(container) {
    const forms = container.querySelectorAll(".formulario-cuentapredial-item");
    forms.forEach((form, i) => {
        const btn = form.querySelector(".btn-delete-cuentapredial");
        if (btn) btn.style.display = i === 0 ? "none" : "inline-block";
    });
}

document.addEventListener("click", function (e) {
    if (e.target.closest("#btn-agregar-cuentapredial")) {
        agregarCuentaPredialDesdeBoton(e.target);
    }

    if (e.target.closest(".btn-delete-cuentapredial, .btn-delete-formulario")) {
        const form = e.target.closest(".formulario-cuentapredial-item");
        const container = form.closest("#cuentapredial-formset-container");
        const conceptoForm = container.closest(".formulario-concepto");
        const totalFormsInput = conceptoForm.querySelector('[id$="-TOTAL_FORMS"]');
        const initialFormsInput = conceptoForm.querySelector('[id$="-INITIAL_FORMS"]');
        const deleteCheckbox = form.querySelector('input[type="checkbox"][name$="-DELETE"]');

        const total = parseInt(totalFormsInput?.value || 0);
        const initial = parseInt(initialFormsInput?.value || 0);

        const nameExample = form.querySelector('[name]')?.name;
        const match = nameExample?.match(/predial-\d+-(\d+)-/);
        const index = match ? parseInt(match[1]) : null;

        if (deleteCheckbox && index < initial) {
            deleteCheckbox.checked = true;
            form.style.display = "none";
        } else {
            form.remove();

            // 🔁 Reindexar todos los formularios visibles (solo los creados)
            const visibles = container.querySelectorAll(".formulario-cuentapredial-item:not([style*='display: none'])");
            visibles.forEach((formulario, i) => {
                formulario.querySelectorAll("[name], [id], label").forEach(el => {
                    if (el.name) el.name = el.name.replace(/predial-\d+-\d+-/, `predial-${match[0].split('-')[1]}-${i}-`);
                    if (el.id) el.id = el.id.replace(/id_predial-\d+-\d+-/, `id_predial-${match[0].split('-')[1]}-${i}-`);
                    if (el.htmlFor) el.htmlFor = el.htmlFor.replace(/predial-\d+-\d+-/, `predial-${match[0].split('-')[1]}-${i}-`);
                });
            });

            totalFormsInput.value = visibles.length;
        }

        actualizarBotonesEliminarCuentaPredial(container);
    }
});
