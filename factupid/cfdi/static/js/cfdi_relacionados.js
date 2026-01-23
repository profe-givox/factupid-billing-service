    function agregarRelacion() {
        const contenedor = document.getElementById('contenedor-relaciones');
        const totalFormsInput = document.getElementById('id_cfdirelacionados_set-TOTAL_FORMS');
        const initialFormsInput = document.getElementById('id_cfdirelacionados_set-INITIAL_FORMS');
        

        const total = parseInt(totalFormsInput.value || 0);
        const initial = parseInt(initialFormsInput.value || 0);

        if (!plantillaRelacion) {
            console.error("❌ No se encontró la plantilla de relación.");
            return;
        }

        // Clona la plantilla del formulario
        
        const nuevoForm = plantillaRelacion.cloneNode(true);

        // Limpia valores del formulario clonado
        nuevoForm.querySelectorAll('input, select, textarea').forEach(el => {
            if (el.name?.includes('-id')) return;
            if (el.type === 'checkbox' || el.type === 'radio') {
                el.checked = false;
            } else {
                el.value = '';
            }
        });

        // Reemplaza índices antiguos (como -0-) y también __prefix__
        nuevoForm.querySelectorAll('[name], [id], label').forEach(el => {
            if (el.name) {
                el.name = el.name.replace(/cfdirelacionados_set-\d+-/g, `cfdirelacionados_set-${total}-`);
                el.name = el.name.replace(/__prefix__/g, total);
            }
            if (el.id) {
                el.id = el.id.replace(/cfdirelacionados_set-\d+-/g, `cfdirelacionados_set-${total}-`);
                el.id = el.id.replace(/__prefix__/g, total);
            }
            if (el.htmlFor) {
                el.htmlFor = el.htmlFor.replace(/cfdirelacionados_set-\d+-/g, `cfdirelacionados_set-${total}-`);
                el.htmlFor = el.htmlFor.replace(/__prefix__/g, total);
            }
        });

        // Agrega el nuevo formulario al contenedor
        contenedor.appendChild(nuevoForm);

        // Actualiza TOTAL_FORMS
        totalFormsInput.value = total + 1;
    }

    document.addEventListener('click', function (e) {
        if (e.target.closest('.eliminar-relacion')) {
            const formulario = e.target.closest('.formulario-relacion');
            const checkboxDelete = formulario.querySelector('input[type="checkbox"][name$="-DELETE"]');

            const totalFormsInput = document.getElementById("id_cfdirelacionados_set-TOTAL_FORMS");
            const initialFormsInput = document.getElementById("id_cfdirelacionados_set-INITIAL_FORMS");

            const totalForms = parseInt(totalFormsInput.value);
            const initialForms = parseInt(initialFormsInput.value);

            // Obtener índice del formulario actual
            const nameExample = formulario.querySelector('[name]')?.name;
            const match = nameExample?.match(/cfdirelacionados_set-(\d+)-/);
            const index = match ? parseInt(match[1]) : null;

            if (checkboxDelete && index < initialForms) {
                // 🔹 Caso 1: formulario existente (editando)
                checkboxDelete.checked = true;
                formulario.style.display = 'none';
            } else {
                // 🔹 Caso 2: formulario nuevo agregado dinámicamente
                formulario.remove();

                // ✅ Reindexar los formularios nuevos
                const contenedor = document.getElementById("contenedor-relaciones");
                const formularios = contenedor.querySelectorAll('.formulario-relacion');
                let nuevoIndex = initialForms; // solo reindexa los nuevos visibles

                formularios.forEach((form, i) => {
                    const isVisible = form.style.display !== 'none';
                    const nameField = form.querySelector('[name]');
                    const match = nameField?.name.match(/cfdirelacionados_set-(\d+)-/);
                    const currentIndex = match ? parseInt(match[1]) : null;

                    if (currentIndex !== null && currentIndex >= initialForms && isVisible) {
                        form.querySelectorAll('[name], [id], label').forEach(el => {
                            if (el.name) el.name = el.name.replace(/cfdirelacionados_set-\d+-/, `cfdirelacionados_set-${nuevoIndex}-`);
                            if (el.id) el.id = el.id.replace(/cfdirelacionados_set-\d+-/, `cfdirelacionados_set-${nuevoIndex}-`);
                            if (el.htmlFor) el.htmlFor = el.htmlFor.replace(/cfdirelacionados_set-\d+-/, `cfdirelacionados_set-${nuevoIndex}-`);
                        });
                        nuevoIndex++;
                    }
                });

                // Actualizar TOTAL_FORMS
                totalFormsInput.value = nuevoIndex;
            }

            actualizarBotonesEliminarRelacion();
        }
    });



  function actualizarBotonesEliminarRelacion() {
    const formularios = document.querySelectorAll('.formulario-relacion');
    formularios.forEach((form, i) => {
        const btn = form.querySelector('.eliminar-relacion');
        if (btn) {
            btn.disabled = false;
        }
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
      const uuidInput = document.querySelector('#id_uuid');
      if (!uuidInput) return;  // ← evita el error si no existe
    
      uuidInput.addEventListener('change', function () {
        const uuid = this.value;
    
        fetch(`/api/comprobante_detalle/${uuid}/`)
          .then(res => res.json())
          .then(data => {
            document.getElementById('detalle-uuid').textContent = data.uuid;
            document.getElementById('detalle-fecha').textContent = data.fecha;
            document.getElementById('detalle-folio').textContent = data.folio;
            document.getElementById('detalle-emisor-rfc').textContent = data.emisor_rfc;
            document.getElementById('detalle-emisor-razon').textContent = data.emisor_razon;
            document.getElementById('detalle-receptor-rfc').textContent = data.receptor_rfc;
            document.getElementById('detalle-receptor-razon').textContent = data.receptor_razon;
          });
      });
    });