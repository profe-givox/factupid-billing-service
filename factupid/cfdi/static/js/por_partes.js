const plantillasParte = {};

function inicializarPlantillaParte(conceptoForm, index) {
    console.log("Inicializando plantilla parte para el concepto:", index);
    const container = conceptoForm.querySelector("#parte-formset-container");
    const formulario = container?.querySelector(".formulario-parte-item");
    if (formulario) {
        const prefix = `parte-${index}`;
        plantillasParte[prefix] = formulario.cloneNode(true);
    }
}

function agregarParteDesdeBoton(boton) {
    const conceptoForm = boton.closest(".formulario-concepto");
    const index = [...document.querySelectorAll('.formulario-concepto')].indexOf(conceptoForm);
    const prefix = `parte-${index}`;
    const contenedor = conceptoForm.querySelector("#parte-formset-container");
    const totalFormsInput = conceptoForm.querySelector(`#id_${prefix}-TOTAL_FORMS`);

    if (!plantillasParte[prefix]) return;

    const total = parseInt(totalFormsInput.value || 0);
    const nuevo = plantillasParte[prefix].cloneNode(true);

    nuevo.querySelectorAll("[name], [id], label").forEach(el => {
        if (el.name) el.name = el.name.replace(/parte-\d+-\d+-/, `${prefix}-${total}-`);
        if (el.id) el.id = el.id.replace(/id_parte-\d+-\d+-/, `id_${prefix}-${total}-`);
        if (el.htmlFor) el.htmlFor = el.htmlFor.replace(/parte-\d+-\d+-/, `${prefix}-${total}-`);
    });

    nuevo.querySelectorAll("input, select, textarea").forEach(el => {
        if (el.name.includes("-id")) el.remove();
        else if (!el.name.includes("DELETE")) el.value = "";
        else if (el.type === "checkbox") el.checked = false;
    });

    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "btn btn-sm btn-danger btn-delete-parte";
    btn.style = "position:absolute; top:0.5rem; right:0.5rem;";
    btn.innerHTML = '<i class="fas fa-trash-alt"></i>';
    nuevo.appendChild(btn);

    contenedor.appendChild(nuevo);
    totalFormsInput.value = total + 1;
    actualizarBotonesEliminarParte(contenedor);
}

function actualizarBotonesEliminarParte(container) {
    const forms = container.querySelectorAll(".formulario-parte-item");
    forms.forEach(form => {
        const btn = form.querySelector(".btn-delete-parte");
        if (btn) btn.style.display = "inline-block";
    });
}

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".formulario-concepto").forEach((formulario, index) => {
        inicializarPlantillaParte(formulario, index);
    });
});

document.addEventListener("click", function (e) {
    if (e.target.closest("#btn-agregar-parte")) {
        agregarParteDesdeBoton(e.target);
    }

    if (e.target.closest(".btn-delete-parte")) {
        const form = e.target.closest(".formulario-parte-item");
        const container = form.closest("#parte-formset-container");
        const conceptoForm = container.closest(".formulario-concepto");
        const totalFormsInput = conceptoForm.querySelector('[id$="-TOTAL_FORMS"]');
        const initialFormsInput = conceptoForm.querySelector('[id$="-INITIAL_FORMS"]');
        const deleteCheckbox = form.querySelector('input[type="checkbox"][name$="-DELETE"]');

        const total = parseInt(totalFormsInput?.value || 0);
        const initial = parseInt(initialFormsInput?.value || 0);

        const nameExample = form.querySelector('[name]')?.name;
        const match = nameExample?.match(/parte-\d+-(\d+)-/);
        const index = match ? parseInt(match[1]) : null;

        if (deleteCheckbox && index < initial) {
            deleteCheckbox.checked = true;
            form.style.display = "none";
        } else {
            form.remove();

            const visibles = container.querySelectorAll(".formulario-parte-item:not([style*='display: none'])");
            visibles.forEach((formulario, i) => {
                formulario.querySelectorAll("[name], [id], label").forEach(el => {
                    if (el.name) el.name = el.name.replace(/parte-\d+-\d+-/, `parte-${match[0].split('-')[1]}-${i}-`);
                    if (el.id) el.id = el.id.replace(/id_parte-\d+-\d+-/, `id_parte-${match[0].split('-')[1]}-${i}-`);
                    if (el.htmlFor) el.htmlFor = el.htmlFor.replace(/parte-\d+-\d+-/, `parte-${match[0].split('-')[1]}-${i}-`);
                });
            });

            totalFormsInput.value = visibles.length;
        }

        actualizarBotonesEliminarParte(container);
    }
});
