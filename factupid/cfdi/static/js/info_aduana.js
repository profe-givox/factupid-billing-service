const plantillasAduana = {};

function inicializarPlantillaInformacionAduanera(conceptoForm, index) {
    const container = conceptoForm.querySelector("#informacionaduanera-formset-container");
    const formulario = container?.querySelector(".formulario-informacionaduanera-item");
    if (formulario) {
        const prefix = `aduana-${index}`;
        plantillasAduana[prefix] = formulario.cloneNode(true);
    }
}

function agregarInformacionAduaneraDesdeBoton(boton) {
    const conceptoForm = boton.closest(".formulario-concepto");
    const index = [...document.querySelectorAll('.formulario-concepto')].indexOf(conceptoForm);
    const prefix = `aduana-${index}`;
    const contenedor = conceptoForm.querySelector("#informacionaduanera-formset-container");
    const totalFormsInput = conceptoForm.querySelector(`#id_${prefix}-TOTAL_FORMS`);

    if (!plantillasAduana[prefix]) return;

    const total = parseInt(totalFormsInput.value || 0);
    const nuevo = plantillasAduana[prefix].cloneNode(true);

    nuevo.querySelectorAll("[name], [id], label").forEach(el => {
        if (el.name) el.name = el.name.replace(/aduana-\d+-\d+-/, `${prefix}-${total}-`);
        if (el.id) el.id = el.id.replace(/id_aduana-\d+-\d+-/, `id_${prefix}-${total}-`);
        if (el.htmlFor) el.htmlFor = el.htmlFor.replace(/aduana-\d+-\d+-/, `${prefix}-${total}-`);
    });

    nuevo.querySelectorAll("input, select, textarea").forEach(el => {
        if (el.name.includes("-id")) el.remove();
        else if (!el.name.includes("DELETE")) el.value = "";
        else if (el.type === "checkbox") el.checked = false;
    });

    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "btn btn-sm btn-danger btn-delete-informacionaduanera";
    btn.style = "position:absolute; top:0.5rem; right:0.5rem;";
    btn.innerHTML = '<i class="fas fa-trash-alt"></i>';
    nuevo.appendChild(btn);

    contenedor.appendChild(nuevo);
    totalFormsInput.value = total + 1;
    actualizarBotonesEliminarInformacionAduanera(contenedor);
}

function actualizarBotonesEliminarInformacionAduanera(container) {
    const forms = container.querySelectorAll(".formulario-informacionaduanera-item");
    forms.forEach((form, i) => {
        const btn = form.querySelector(".btn-delete-informacionaduanera");
        if (btn) btn.style.display = i === 0 ? "none" : "inline-block";
    });
}

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".formulario-concepto").forEach((formulario, index) => {
        inicializarPlantillaInformacionAduanera(formulario, index);
    });
});

document.addEventListener("click", function (e) {
    if (e.target.closest("#btn-agregar-informacionaduanera")) {
        agregarInformacionAduaneraDesdeBoton(e.target);
    }

    if (e.target.closest(".btn-delete-informacionaduanera")) {
        const form = e.target.closest(".formulario-informacionaduanera-item");
        const container = form.closest("#informacionaduanera-formset-container");
        const conceptoForm = container.closest(".formulario-concepto");
        const totalFormsInput = conceptoForm.querySelector('[id$="-TOTAL_FORMS"]');
        const initialFormsInput = conceptoForm.querySelector('[id$="-INITIAL_FORMS"]');
        const deleteCheckbox = form.querySelector('input[type="checkbox"][name$="-DELETE"]');

        const total = parseInt(totalFormsInput?.value || 0);
        const initial = parseInt(initialFormsInput?.value || 0);

        const nameExample = form.querySelector('[name]')?.name;
        const match = nameExample?.match(/aduana-\d+-(\d+)-/);
        const index = match ? parseInt(match[1]) : null;

        if (deleteCheckbox && index < initial) {
            deleteCheckbox.checked = true;
            form.style.display = "none";
        } else {
            form.remove();

            const visibles = container.querySelectorAll(".formulario-informacionaduanera-item:not([style*='display: none'])");
            visibles.forEach((formulario, i) => {
                formulario.querySelectorAll("[name], [id], label").forEach(el => {
                    if (el.name) el.name = el.name.replace(/aduana-\d+-\d+-/, `aduana-${match[0].split('-')[1]}-${i}-`);
                    if (el.id) el.id = el.id.replace(/id_aduana-\d+-\d+-/, `id_aduana-${match[0].split('-')[1]}-${i}-`);
                    if (el.htmlFor) el.htmlFor = el.htmlFor.replace(/aduana-\d+-\d+-/, `aduana-${match[0].split('-')[1]}-${i}-`);
                });
            });

            totalFormsInput.value = visibles.length;
        }

        actualizarBotonesEliminarInformacionAduanera(container);
    }
});
