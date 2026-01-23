document.addEventListener("DOMContentLoaded", function () {
    document.addEventListener("click", function (e) {
        const opcionComplemento = e.target.closest(".complemento-opcion");
        if (opcionComplemento) {
            const tipo = opcionComplemento.dataset.tipo;
            const conceptoForm = opcionComplemento.closest(".formulario-concepto");
            const conceptosForms = document.querySelectorAll('.formulario-concepto');
            const index = Array.from(conceptosForms).indexOf(conceptoForm);

            if (index === -1) return;

            const contenedor = conceptoForm.querySelector(".contenedor-complementos");
            const inputComplemento = conceptoForm.querySelector('input[name$="-complemento_tipo"]');
            if (inputComplemento) inputComplemento.value = tipo;

            const conceptoId = conceptoForm.dataset.conceptoId || null;
            const url = conceptoId
                ? `/cfdi/concepto/obtener_formulario_complemento_concepto/?tipo=${tipo}&index=${index}&concepto_id=${conceptoId}`
                : `/cfdi/concepto/obtener_formulario_complemento_concepto/?tipo=${tipo}&index=${index}`;

            fetch(url)
                .then(r => r.json())
                .then(data => {
                    contenedor.innerHTML = data.html;
                    actualizarIdsConcepto(conceptoForm, index);
                    // Inicializar script específico de Cuenta Predial si aplica
                    if (tipo === "cuenta_predial") {
                        inicializarPlantillaCuentaPredial(conceptoForm, index);
                    }
                    if (tipo === "informacion_aduanera") {
                        inicializarPlantillaInformacionAduanera(conceptoForm, index);
                    }
                    if (tipo === "parte") {
                        inicializarPlantillaParte(conceptoForm, index);
                    }
                })
                .catch(error => {
                    contenedor.innerHTML = "<p class='text-danger'>Error al cargar el complemento</p>";
                });
        }

        // Eliminar complemento
        if (e.target.closest(".btn-eliminar-complemento")) {
            const conceptoForm = e.target.closest(".formulario-concepto");
            const contenedor = conceptoForm.querySelector(".contenedor-complementos");
            if (contenedor) contenedor.innerHTML = "";
            const tipoInput = conceptoForm.querySelector('[name$="-complemento_tipo"]');
            if (tipoInput) tipoInput.value = "";
        }
    });

    // Mostrar automáticamente complemento en modo edición
    document.querySelectorAll(".formulario-concepto").forEach((conceptoForm, index) => {
        conceptoForm.id = `concepto-${index}`;
        const tipoInput = conceptoForm.querySelector('input[name$="-complemento_tipo"]');
        const tipo = tipoInput?.value;
        if (!tipo) return;

        const contenedor = conceptoForm.querySelector(".contenedor-complementos");
        const conceptoId = conceptoForm.dataset.conceptoId || null;
        const url = conceptoId
            ? `/cfdi/concepto/obtener_formulario_complemento_concepto/?tipo=${tipo}&index=${index}&concepto_id=${conceptoId}`
            : `/cfdi/concepto/obtener_formulario_complemento_concepto/?tipo=${tipo}&index=${index}`;

        fetch(url)
            .then(r => r.json())
            .then(data => {
                contenedor.innerHTML = data.html;
                actualizarIdsConcepto(conceptoForm, index);
                if (tipo === "cuenta_predial") {
                    inicializarPlantillaCuentaPredial(conceptoForm, index);
                }
                if (tipo === "informacion_aduanera") {
                    inicializarPlantillaInformacionAduanera(conceptoForm, index);
                }
                if (tipo === "parte") {
                    inicializarPlantillaParte(conceptoForm, index);
                }
            });
    });

    function actualizarIdsConcepto(conceptoForm, index) {
        conceptoForm.querySelectorAll('[name^="conceptos-"], [id^="id_conceptos-"]').forEach(el => {
            if (el.name) el.name = el.name.replace(/conceptos-\d+/, `conceptos-${index}`);
            if (el.id) el.id = el.id.replace(/id_conceptos-\d+/, `id_conceptos-${index}`);
        });
    }
});