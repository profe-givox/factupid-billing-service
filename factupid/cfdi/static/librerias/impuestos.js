  const tasasPorImpuesto = window.tasasPorImpuesto || {};

  let plantillaFormularioImpuesto = null;

  document.body.addEventListener('click', function (e) {
    if (e.target.classList.contains('tipo-icono') && !e.target.classList.contains('text-muted')) {
      const icono = e.target;

      // Encontrar el formulario actual de impuesto
      const formulario = icono.closest('.formulario-impuesto');
      if (!formulario) return;

      const tipoSelect = formulario.querySelector('[name$="tipo"]');
      const impuestoInput = formulario.querySelector('[name$="c_Impuesto"]');
      const etiqueta = formulario.querySelector('.label-impuesto-tipo');

      if (!tipoSelect || tipoSelect.disabled || tipoSelect.options.length < 2) return;

      // Alternar valor
      const nuevoValor = tipoSelect.value === 'Traslado' ? 'Retención' : 'Traslado';
      tipoSelect.value = nuevoValor;

      // Actualizar icono
      icono.textContent = nuevoValor === 'Retención' ? 'reply_all' : 'forward';

      // Actualizar badge
      let textoImpuesto = '';
      const cod = impuestoInput?.value;
      if (cod === '001') textoImpuesto = 'ISR';
      else if (cod === '002') textoImpuesto = 'IVA';
      else if (cod === '003') textoImpuesto = 'IEPS';

      textoImpuesto += nuevoValor === 'Retención' ? ' Ret.' : ' Tras.';
      if (etiqueta) etiqueta.textContent = textoImpuesto;

      // Recalcular
      actualizarTotalesCompletos();
    }
  });



  document.addEventListener('DOMContentLoaded', function () {
      // Guardar plantilla del formulario de impuesto
      const primerFormImpuesto = document.querySelector('.formulario-impuesto');
      if (primerFormImpuesto) {
          plantillaFormularioImpuesto = primerFormImpuesto.cloneNode(true);
          
          document.querySelectorAll('.formulario-concepto').forEach(concepto => {
              const contenedor = concepto.querySelector('[id^="contenedor-impuestos"]');
              const totalFormsInput = concepto.querySelector('input[id$="impuestos-TOTAL_FORMS"]');
              const initialFormsInput = concepto.querySelector('input[id$="impuestos-INITIAL_FORMS"]');
              
              if (contenedor && totalFormsInput && initialFormsInput) {
                  const initialForms = parseInt(initialFormsInput.value);
                  
                  // Solo resetear si no hay impuestos existentes
                  if (initialForms === 0) {
                      contenedor.innerHTML = `
                          <div class="card-header bg-light py-2 px-3">
                              <strong class="text-dark text-sm">Impuestos</strong>
                          </div>
                          <input type="hidden" name="${totalFormsInput.name}" value="0" id="${totalFormsInput.id}">
                          <input type="hidden" name="${initialFormsInput.name}" value="0" id="${initialFormsInput.id}">
                          <input type="hidden" name="${concepto.querySelector('input[id$="impuestos-MIN_NUM_FORMS"]').name}" value="0" id="${concepto.querySelector('input[id$="impuestos-MIN_NUM_FORMS"]').id}">
                          <input type="hidden" name="${concepto.querySelector('input[id$="impuestos-MAX_NUM_FORMS"]').name}" value="1000" id="${concepto.querySelector('input[id$="impuestos-MAX_NUM_FORMS"]').id}">
                      `;
                  }
              }
          });
      }

      // Inicializar menús de impuestos y valores existentes
      document.querySelectorAll('.formulario-concepto').forEach(f => {
          inicializarMenuImpuestos(f);
          
          // Configurar botones eliminar existentes
          f.querySelectorAll('.btn-delete-impuesto').forEach(btn => {
              btn.addEventListener('click', function() {
                  eliminarImpuesto(btn.closest('.formulario-impuesto'), f);
              });
          });
          
          // Inicializar valores de tasas para impuestos existentes
          f.querySelectorAll('.formulario-impuesto').forEach(impuesto => {
          inicializarValorTasa(impuesto);

          const tipoSelect = impuesto.querySelector('[name$="tipo"]');
          const impuestoInput = impuesto.querySelector('[name$="c_Impuesto"]');
          const tasaInput = impuesto.querySelector('[name$="c_TasaOCuota"]');
          const factorInput = impuesto.querySelector('[name$="c_TipoFactor"]');

          if (tipoSelect && impuestoInput && tasaInput && factorInput) {
            const cod = impuestoInput.value;
            const idTasa = tasaInput.value;
            const factor = factorInput.value;

            const tasas = tasasPorImpuesto[cod] || [];
            const tasa = tasas.find(t => t.id == idTasa && t.factor === factor);

            const puedeAmbos = tasa?.traslado === true && tasa?.retencion === true;

            console.log(`Inicializando impuesto ${cod} con tasa ${idTasa} y factor ${factor}`, tasa, puedeAmbos);

            actualizarIconoYTipo(impuesto, tipoSelect.value, puedeAmbos);
          }
        });

      });
  });

  function agregarImpuesto(formularioConcepto, tasaData) {
    if (!plantillaFormularioImpuesto) {
        console.error("Plantilla de impuesto no encontrada");
        return;
    }

    const contenedorImpuestos = formularioConcepto.querySelector('[id^="contenedor-impuestos"]');
    const totalFormsInput = formularioConcepto.querySelector('input[id$="impuestos-TOTAL_FORMS"]');
    const initialFormsInput = formularioConcepto.querySelector('input[id$="impuestos-INITIAL_FORMS"]');

    if (!contenedorImpuestos || !totalFormsInput || !initialFormsInput) {
        console.error("Elementos requeridos no encontrados");
        return;
    }

    const total = parseInt(totalFormsInput.value || 0);
    const ejemploNombre = formularioConcepto.querySelector('[name*="conceptos-"]')?.name;
    const prefixMatch = ejemploNombre?.match(/conceptos-(\d+)-/);
    const prefix = prefixMatch ? prefixMatch[1] : '0';


    const nuevoForm = plantillaFormularioImpuesto.cloneNode(true);
    nuevoForm.style.display = 'block';

    // Limpiar valores
    nuevoForm.querySelectorAll('input, select, textarea').forEach(el => {
        if (el.name?.includes('-id')) return;
        if (el.type === 'checkbox' || el.type === 'radio') {
            el.checked = false;
        } else if (!el.classList.contains('label-tasa-cuota')) {
            el.value = '';
        }
    });

    // Reemplazar atributos con el índice correcto del concepto e impuesto
    nuevoForm.querySelectorAll('[name], [id], [for]').forEach(el => {
        const conceptoIndex = prefix;

        if (el.name) {
            el.name = el.name
                .replace(/conceptos-\d+-impuestos-\d+/, `conceptos-${conceptoIndex}-impuestos-${total}`)
                .replace(/__prefix__/g, total);
        }
        if (el.id) {
            el.id = el.id
                .replace(/id_conceptos-\d+-impuestos-\d+/, `id_conceptos-${conceptoIndex}-impuestos-${total}`)
                .replace(/__prefix__/g, total);
        }
        if (el.getAttribute('for')) {
            el.setAttribute(
                'for',
                el.getAttribute('for')
                    .replace(/id_conceptos-\d+-impuestos-\d+/, `id_conceptos-${conceptoIndex}-impuestos-${total}`)
                    .replace(/__prefix__/g, total)
            );
        }
    });

    // Campo oculto DELETE e ID
    const deleteDiv = nuevoForm.querySelector('.d-none');
    if (deleteDiv) {
        deleteDiv.innerHTML = `
            <input type="checkbox" name="conceptos-${prefix}-impuestos-${total}-DELETE" 
                  id="id_conceptos-${prefix}-impuestos-${total}-DELETE">
            <input type="hidden" name="conceptos-${prefix}-impuestos-${total}-id" 
                  id="id_conceptos-${prefix}-impuestos-${total}-id">
        `;
    }

    // Cálculo
    const base = parseFloat(formularioConcepto.querySelector('[name$="-importe"]')?.value || 0);
    const porcentaje = parseFloat(tasaData.representacion.replace('%', '')) || 0;
    const importe = (base * (porcentaje / 100)).toFixed(2);

    nuevoForm.querySelector('[name$="c_Impuesto"]').value = tasaData.impuesto;
    nuevoForm.querySelector('[name$="c_TipoFactor"]').value = tasaData.factor;

    const tasaInput = nuevoForm.querySelector('[name$="c_TasaOCuota"]');
    if (tasaInput) {
        tasaInput.innerHTML = '';
        const option = new Option(`${tasaData.representacion} (${tasaData.factor})`, tasaData.id);
        option.selected = true;
        tasaInput.appendChild(option);
    }

    const tipoSelect = nuevoForm.querySelector('[name$="tipo"]');
    if (tipoSelect) {
        tipoSelect.innerHTML = '';
        if (tasaData.traslado === 'true') tipoSelect.add(new Option('Traslado', 'Traslado'));
        if (tasaData.retencion === 'true') tipoSelect.add(new Option('Retención', 'Retención'));
        tipoSelect.value = tasaData.traslado === 'true' ? 'Traslado' : 'Retención';
    }

    if (nuevoForm.querySelector('[name$="base"]')) nuevoForm.querySelector('[name$="base"]').value = base.toFixed(2);
    if (nuevoForm.querySelector('[name$="importe"]')) nuevoForm.querySelector('[name$="importe"]').value = importe;
    if (nuevoForm.querySelector('.label-tasa-cuota')) nuevoForm.querySelector('.label-tasa-cuota').value = `${tasaData.representacion} (${tasaData.factor})`;

    const btnEliminar = nuevoForm.querySelector('.btn-delete-impuesto');
    if (btnEliminar) {
        btnEliminar.onclick = () => eliminarImpuesto(nuevoForm, formularioConcepto);
    }

    contenedorImpuestos.appendChild(nuevoForm);
    totalFormsInput.value = total + 1;

    actualizarIconoYTipo(nuevoForm, tipoSelect?.value || 'Traslado',
        tasaData.traslado === 'true' && tasaData.retencion === 'true');
    actualizarTotalesCompletos();
  }


  function eliminarImpuesto(formularioImpuesto, formularioConcepto) {
      if (!formularioImpuesto || !formularioConcepto) return;

      const totalFormsInput = formularioConcepto.querySelector('input[id$="impuestos-TOTAL_FORMS"]');
      const initialFormsInput = formularioConcepto.querySelector('input[id$="impuestos-INITIAL_FORMS"]');
      const deleteInput = formularioImpuesto.querySelector('input[name$="-DELETE"]');
      const idInput = formularioImpuesto.querySelector('input[name$="-id"]');
      
      if (!totalFormsInput || !initialFormsInput) return;

      // Obtener índice del formulario actual
      const nameExample = formularioImpuesto.querySelector('[name]')?.name;
      const match = nameExample?.match(/impuestos-(\d+)-/);
      const index = match ? parseInt(match[1]) : null;
      const initialForms = parseInt(initialFormsInput.value);

      // Verificar si es un impuesto existente (índice < initialForms)
      if (index !== null && index < initialForms && deleteInput) {
          // Caso 1: Impuesto existente (marcar para borrado y ocultar)
          deleteInput.checked = true;
          formularioImpuesto.style.display = 'none';
      } else {
          // Caso 2: Impuesto nuevo (eliminar y reindexar)
          formularioImpuesto.remove();

          // Reindexar solo los formularios nuevos (índices >= initialForms)
          const contenedor = formularioConcepto.querySelector('[id^="contenedor-impuestos"]');
          const formularios = contenedor.querySelectorAll('.formulario-impuesto');
          let nuevoIndex = initialForms;

          formularios.forEach((form, i) => {
              const isVisible = form.style.display !== 'none';
              const nameField = form.querySelector('[name]');
              const match = nameField?.name.match(/impuestos-(\d+)-/);
              const currentIndex = match ? parseInt(match[1]) : null;

              if (currentIndex !== null && currentIndex >= initialForms && isVisible) {
                  form.querySelectorAll('[name], [id], [for]').forEach(el => {
                      if (el.name) el.name = el.name.replace(/impuestos-\d+-/, `impuestos-${nuevoIndex}-`);
                      if (el.id) el.id = el.id.replace(/id_impuestos-\d+-/, `id_impuestos-${nuevoIndex}-`);
                      if (el.htmlFor) el.htmlFor = el.htmlFor.replace(/id_impuestos-\d+-/, `id_impuestos-${nuevoIndex}-`);
                  });
                  nuevoIndex++;
              }
          });

          // Actualizar TOTAL_FORMS
          totalFormsInput.value = nuevoIndex;
      }

      actualizarTotalesCompletos();
  }

  // Resto de funciones (inicializarMenuImpuestos, actualizarIconoYTipo, inicializarValorTasa) permanecen igual

  // Resto de funciones permanecen igual...

  function inicializarMenuImpuestos(formulario) {
      const btnImpuestos = formulario.querySelector('.btn-impuestos');
      const menuImpuestos = formulario.querySelector('.menu-impuestos');

      if (btnImpuestos && menuImpuestos) {
          btnImpuestos.addEventListener('click', function (e) {
              e.preventDefault();
              e.stopPropagation();
              const visible = menuImpuestos.style.display === 'block';
              document.querySelectorAll('.menu-impuestos, .dropdown-submenu-list').forEach(m => {
                  m.style.display = 'none';
              });
              if (!visible) menuImpuestos.style.display = 'block';
          });
      }

      formulario.querySelectorAll('.impuesto-item').forEach(item => {
          item.addEventListener('click', function (e) {
              e.preventDefault();
              const codigo = this.dataset.codigo;
              const submenu = formulario.querySelector(`#submenu-${codigo}`);
              if (!submenu) return;

              submenu.innerHTML = '';
              const tasas = tasasPorImpuesto[codigo] || [];
              tasas.forEach(tasa => {
                  submenu.innerHTML += `
                  <li>
                      <a href="#" class="dropdown-item seleccionar-tasa"
                      data-impuesto="${codigo}"
                      data-id="${tasa.id}"
                      data-representacion="${tasa.representacionporcentual}"
                      data-factor="${tasa.factor}"
                      data-traslado="${tasa.traslado}"
                      data-retencion="${tasa.retencion}">
                      ${tasa.representacionporcentual} (${tasa.factor})
                      </a>
                  </li>`;
              });
              submenu.style.display = 'block';
          });
      });

      // Manejador para selección de tasas
      formulario.addEventListener('click', function (e) {
          if (e.target.classList.contains('seleccionar-tasa')) {
              e.preventDefault();
              const tasa = e.target.dataset;
              agregarImpuesto(formulario, tasa);
              
              // Cerrar menús
              document.querySelectorAll('.menu-impuestos, .dropdown-submenu-list').forEach(m => {
                  m.style.display = 'none';
              });
          }
      });
  }

  // Funciones originales sin cambios
  function actualizarIconoYTipo(formulario, tipoActual, esDoble) {
      const iconoTipo = formulario.querySelector('.tipo-icono');
      const tipoSelect = formulario.querySelector('[name$="tipo"]');
      const etiqueta = formulario.querySelector('.label-impuesto-tipo');
      const impuestoInput = formulario.querySelector('[name$="c_Impuesto"]');

      if (!iconoTipo || !tipoSelect) return;

      iconoTipo.textContent = tipoActual === 'Retención' ? 'reply_all' : 'forward';
      iconoTipo.style.cursor = esDoble ? 'pointer' : 'not-allowed';
      iconoTipo.classList.toggle('text-muted', !esDoble);
      //iconoTipo.disabled = !esDoble;

      let textoImpuesto = '';
      const cod = impuestoInput?.value;
      if (cod === '001') textoImpuesto = 'ISR';
      else if (cod === '002') textoImpuesto = 'IVA';
      else if (cod === '003') textoImpuesto = 'IEPS';

      textoImpuesto += tipoActual === 'Retención' ? ' Ret.' : ' Tras.';
      if (etiqueta) etiqueta.textContent = textoImpuesto;
      actualizarTotalesCompletos();
  }

  function inicializarValorTasa(formulario) {
      const impuestoInput = formulario.querySelector('[name$="c_Impuesto"]');
      const tasaInput = formulario.querySelector('[name$="c_TasaOCuota"]');
      const tipoFactorInput = formulario.querySelector('[name$="c_TipoFactor"]');
      const tipoSelect = formulario.querySelector('[name$="tipo"]');
      const tasaLabel = formulario.querySelector('.label-tasa-cuota');
      const etiquetaTipo = formulario.querySelector('.label-impuesto-tipo');

      if (!impuestoInput || !tasaInput || !tipoFactorInput || !tasaLabel) return;

      const codImpuesto = impuestoInput.value;
      const idTasa = tasaInput.value;
      const factor = tipoFactorInput.value;
      const tipo = tipoSelect ? tipoSelect.value : 'Traslado';

      const tasas = tasasPorImpuesto[codImpuesto];
      if (!tasas) return;

      const tasa = tasas.find(t => String(t.id) === String(idTasa) && String(t.factor) === String(factor));
      if (!tasa) return;

      // Actualizar label de tasa
      tasaLabel.value = `${tasa.representacionporcentual} (${tasa.factor})`;
      
      // Actualizar badge de tipo de impuesto
      if (etiquetaTipo) {
          let textoImpuesto = '';
          if (codImpuesto === '001') textoImpuesto = 'ISR';
          else if (codImpuesto === '002') textoImpuesto = 'IVA';
          else if (codImpuesto === '003') textoImpuesto = 'IEPS';

          textoImpuesto += tipo === 'Retención' ? ' Ret.' : ' Tras.';
          etiquetaTipo.textContent = textoImpuesto;
      }
  }