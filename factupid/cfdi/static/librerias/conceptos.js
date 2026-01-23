let plantillaFormularioConcepto = null;
    let plantillaRelacion = null;
    let plantillaManagementFormImpuestos = null;

    document.addEventListener("DOMContentLoaded", function () {
      if (typeof $.fn.select2 === "undefined") {
        console.error(" Select2 no se cargó correctamente.");
        return;
      }

      const primerConcepto = document.querySelector('.formulario-concepto');
      if (primerConcepto) {
        const mf = primerConcepto.querySelector('[id$="impuestos-TOTAL_FORMS"]')?.closest('div');
        if (mf) {
          plantillaManagementFormImpuestos = mf.cloneNode(true);
        }
      }

    
      // ⚙️ Guardamos plantilla del primer concepto
      const primerForm = document.querySelector(".formulario-concepto");
      if (primerForm) {
        plantillaFormularioConcepto = primerForm.cloneNode(true);
      }
    
      // ⚙️ Para CFDI Relacionados
      const totalFormsInput = document.getElementById('id_cfdirelacionados_set-TOTAL_FORMS');
      const initialFormsInput = document.getElementById('id_cfdirelacionados_set-INITIAL_FORMS');
      const primerFormRelacion = document.querySelector(".formulario-relacion");
    
      if (primerFormRelacion && totalFormsInput && initialFormsInput) {
        // 🔐 Siempre guarda la plantilla
        plantillaRelacion = primerFormRelacion.cloneNode(true);
    
        const total = parseInt(totalFormsInput.value);
        const initial = parseInt(initialFormsInput.value);
    
        // 🧹 Solo elimina el formulario si es nuevo (sin datos)
        if (initial === 0) {
          primerFormRelacion.remove();
          totalFormsInput.value = 0;
        }
      }
    });

    // <!-- Js para agregar conceptos dinámicamente -->
    function agregarConcepto() {
      const totalForms = document.getElementById("id_conceptos-TOTAL_FORMS");
      const contenedor = document.getElementById("contenedor-conceptos");
      
      if (!totalForms || !contenedor || !plantillaFormularioConcepto) {
          console.error("Elementos base no encontrados");
          return;
      }

      const currentCount = parseInt(totalForms.value);

      // 1. Clonar la plantilla
      const newForm = plantillaFormularioConcepto.cloneNode(true);
      newForm.style.display = 'block';

      // 2. Limpieza exhaustiva de campos
      newForm.querySelectorAll('input, select, textarea').forEach(el => {
          // Preservar campos de management forms
          if (el.name?.includes('TOTAL_FORMS') || el.name?.includes('INITIAL_FORMS') || 
              el.name?.includes('MIN_NUM_FORMS') || el.name?.includes('MAX_NUM_FORMS')) {
              return;
          }

          if (el.name?.includes('-id') || el.name?.includes('-comprobante')) {
              el.value = ''; // Limpiar IDs y relaciones
          } else if (el.type === 'checkbox' || el.type === 'radio') {
              el.checked = false;
          } else if (!el.classList.contains('descripcion-sat') && 
                    !el.classList.contains('nombreunidad-sat')) {
              el.value = '';
          }
      });

      // 3. Reemplazar índices
      newForm.querySelectorAll('[name], [id], [for]').forEach(el => {
          if (el.name) {
              el.name = el.name.replace(/conceptos-\d+-/g, `conceptos-${currentCount}-`)
                              .replace(/__prefix__/g, currentCount);
          }
          if (el.id) {
              el.id = el.id.replace(/id_conceptos-\d+-/g, `id_conceptos-${currentCount}-`)
                          .replace(/__prefix__/g, currentCount);
          }
          if (el.htmlFor) {
              el.htmlFor = el.htmlFor.replace(/id_conceptos-\d+-/g, `id_conceptos-${currentCount}-`)
                                  .replace(/__prefix__/g, currentCount);
          }
      });

      // 4. Configurar contenedor de impuestos vacío
      const contenedorImpuestos = newForm.querySelector('[id^="contenedor-impuestos"]');
      if (contenedorImpuestos) {
          contenedorImpuestos.innerHTML = `
              <div class="card-header bg-light py-2 px-3">
                  <strong class="text-dark text-sm">Impuestos</strong>
              </div>
              <input type="hidden" name="conceptos-${currentCount}-impuestos-TOTAL_FORMS" value="0" 
                    id="id_conceptos-${currentCount}-impuestos-TOTAL_FORMS">
              <input type="hidden" name="conceptos-${currentCount}-impuestos-INITIAL_FORMS" value="0" 
                    id="id_conceptos-${currentCount}-impuestos-INITIAL_FORMS">
              <input type="hidden" name="conceptos-${currentCount}-impuestos-MIN_NUM_FORMS" value="0" 
                    id="id_conceptos-${currentCount}-impuestos-MIN_NUM_FORMS">
              <input type="hidden" name="conceptos-${currentCount}-impuestos-MAX_NUM_FORMS" value="1000" 
                    id="id_conceptos-${currentCount}-impuestos-MAX_NUM_FORMS">
          `;
      }
      // 1.5. CORRECCIÓN CLAVE: Forzar data-concepto-id="None" en nuevos conceptos
      newForm.removeAttribute('data-concepto-id'); // Eliminar cualquier valor existente
      newForm.setAttribute('data-concepto-id', 'None'); // Establecer explícitamente None

      // 5. Añadir al DOM
      contenedor.appendChild(newForm);
      totalForms.value = currentCount + 1;

      // 6. Inicialización CRÍTICA para impuestos
      inicializarMenuImpuestos(newForm);
      
      // 7. Configurar eventos de eliminación
      newForm.querySelector('.eliminar-concepto').addEventListener('click', function() {
          eliminarConcepto(newForm);
      });

      // 8. Inicializar otros componentes
      inicializarAutocompletados();
      actualizarBotonesEliminar();
      actualizarTotalesCompletos();
    }

    // <!-- Script para eliminar conceptos dinámicamente -->

    function actualizarBotonesEliminar() {
        const formularios = document.querySelectorAll('.formulario-concepto');
        formularios.forEach(btn => {
            const botonEliminar = btn.querySelector('.eliminar-concepto');
            if (formularios.length <= 1) {
                botonEliminar.style.display = 'none';
            } else {
                botonEliminar.style.display = 'inline-block';
            }
        });
    }
    
    // escript para eliminar conceptos
    document.addEventListener('click', function (e) {
      if (e.target.closest('.eliminar-concepto')) {
          const formulario = e.target.closest('.formulario-concepto');
          const checkboxDelete = formulario.querySelector('input[type="checkbox"][name$="-DELETE"]');

          const totalFormsInput = document.getElementById("id_conceptos-TOTAL_FORMS");
          const initialFormsInput = document.getElementById("id_conceptos-INITIAL_FORMS");

          const totalForms = parseInt(totalFormsInput.value);
          const initialForms = parseInt(initialFormsInput.value);

          // Obtener índice del formulario actual
          const nameExample = formulario.querySelector('[name]').name;
          const match = nameExample.match(/conceptos-(\d+)-/);
          const index = match ? parseInt(match[1]) : null;

          // 1. Primero eliminar todos los impuestos asociados a este concepto
          const impuestos = formulario.querySelectorAll('.formulario-impuesto');
          impuestos.forEach(impuesto => {
              eliminarImpuesto(impuesto, formulario);
          });

          if (checkboxDelete && index < initialForms) {
              // 🔹 Caso 1: formulario ya existente (está dentro de los INITIAL_FORMS)
              checkboxDelete.checked = true;
              formulario.style.display = 'none';
          } else {
              // 🔹 Caso 2: formulario nuevo agregado dinámicamente
              formulario.remove();

              // ✅ Reindexar los formularios nuevos (solo los visibles, sin los ocultos)
              const contenedor = document.getElementById("contenedor-conceptos");
              const formularios = contenedor.querySelectorAll('.formulario-concepto');
              let nuevoIndex = initialForms; // Solo reindexamos los nuevos

              formularios.forEach((form, i) => {
                  const checkbox = form.querySelector('input[type="checkbox"][name$="-DELETE"]');
                  const isVisible = form.style.display !== 'none';

                  // Solo renombrar si es un nuevo formulario (índice >= initialForms) y está visible
                  const nameField = form.querySelector('[name]');
                  const match = nameField?.name.match(/conceptos-(\d+)-/);
                  const currentIndex = match ? parseInt(match[1]) : null;

                  if (currentIndex !== null && currentIndex >= initialForms && isVisible) {
                      form.querySelectorAll('[name], [id], label').forEach(el => {
                          if (el.name) el.name = el.name.replace(/conceptos-\d+-/, `conceptos-${nuevoIndex}-`);
                          if (el.id) el.id = el.id.replace(/conceptos-\d+-/, `conceptos-${nuevoIndex}-`);
                          if (el.htmlFor) el.htmlFor = el.htmlFor.replace(/conceptos-\d+-/, `conceptos-${nuevoIndex}-`);
                      });
                      nuevoIndex++;
                  }
              });

              // Actualizar TOTAL_FORMS
              totalFormsInput.value = nuevoIndex;
          }

          actualizarBotonesEliminar();
          actualizarTotalesCompletos();
      }
    });

    // Llamar también al iniciar la página
    document.addEventListener('DOMContentLoaded', actualizarBotonesEliminar);