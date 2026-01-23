    document.addEventListener("DOMContentLoaded", function () {
      function calcularImporte(index) {
        const cantidadInput = document.getElementById(`id_conceptos-${index}-cantidad`);
        const valorUnitarioInput = document.getElementById(`id_conceptos-${index}-valorUnitario`);
        const importeInput = document.getElementById(`id_conceptos-${index}-importe`);
    
        if (!cantidadInput || !valorUnitarioInput || !importeInput) return;
    
        const cantidad = parseFloat(cantidadInput.value) || 0;
        const valorUnitario = parseFloat(valorUnitarioInput.value) || 0;
        const nuevoImporte = cantidad * valorUnitario; // ✅ AQUÍ defines la variable
        importeInput.value = (cantidad * valorUnitario).toFixed(2);


        // NUEVO: Actualizar impuestos ligados a este concepto
        actualizarImpuestosDelConcepto(index, nuevoImporte);

        actualizarTotalesCompletos(); // Añadir esta línea
      }
    
      function conectarCampo(input) {
        const match = input.id.match(/^id_conceptos-(\d+)-cantidad$/);
        if (!match) return;
        const index = match[1];
        const cantidadInput = input;
        const valorUnitarioInput = document.getElementById(`id_conceptos-${index}-valorUnitario`);
    
        if (cantidadInput && valorUnitarioInput) {
          cantidadInput.addEventListener('input', () => calcularImporte(index));
          valorUnitarioInput.addEventListener('input', () => calcularImporte(index));
        }
      }
    
      // Inicializa todos los existentes al cargar
      document.querySelectorAll("input[id^='id_conceptos-'][id$='-cantidad']").forEach(input => {
        conectarCampo(input);
      });
    
      // Observador para nuevos campos
      const observer = new MutationObserver(mutations => {
        for (const mutation of mutations) {
          for (const node of mutation.addedNodes) {
            if (node.nodeType === 1) {
              // Verifica si el nodo o alguno de sus hijos tiene campos de cantidad
              const inputs = node.matches("input") ? [node] : node.querySelectorAll("input");
              inputs.forEach(input => {
                if (/^id_conceptos-\d+-cantidad$/.test(input.id)) {
                  conectarCampo(input);
                }
              });
            }
          }
        }
      });
    
      // Observa el cuerpo del documento en busca de cambios
      observer.observe(document.body, { childList: true, subtree: true });
    });

    function numeroALetras(num) {
    function unidades(n) {
      const u = ['', 'UN', 'DOS', 'TRES', 'CUATRO', 'CINCO', 'SEIS', 'SIETE', 'OCHO', 'NUEVE'];
      return u[n];
    }

    function decenas(n) {
      const d = ['DIEZ', 'ONCE', 'DOCE', 'TRECE', 'CATORCE', 'QUINCE', 'DIECISÉIS', 'DIECISIETE', 'DIECIOCHO', 'DIECINUEVE'];
      const dec = ['', '', 'VEINTE', 'TREINTA', 'CUARENTA', 'CINCUENTA', 'SESENTA', 'SETENTA', 'OCHENTA', 'NOVENTA'];
      if (n < 10) return unidades(n);
      if (n < 20) return d[n - 10];
      const u = n % 10;
      const t = Math.floor(n / 10);
      return dec[t] + (u > 0 ? ' Y ' + unidades(u) : '');
    }

    function centenas(n) {
      if (n < 100) return decenas(n);
      const c = Math.floor(n / 100);
      const resto = n % 100;
      const centenasArr = ['', 'CIENTO', 'DOSCIENTOS', 'TRESCIENTOS', 'CUATROCIENTOS', 'QUINIENTOS', 'SEISCIENTOS', 'SETECIENTOS', 'OCHOCIENTOS', 'NOVECIENTOS'];
      if (n === 100) return 'CIEN';
      return centenasArr[c] + (resto > 0 ? ' ' + decenas(resto) : '');
    }

    function miles(n) {
      if (n < 1000) return centenas(n);
      const mil = Math.floor(n / 1000);
      const resto = n % 1000;
      const milTexto = mil === 1 ? 'MIL' : centenas(mil) + ' MIL';
      return milTexto + (resto > 0 ? ' ' + centenas(resto) : '');
    }

    function millones(n) {
      if (n < 1000000) return miles(n);
      const millon = Math.floor(n / 1000000);
      const resto = n % 1000000;
      const millonTexto = millon === 1 ? 'UN MILLÓN' : miles(millon) + ' MILLONES';
      return millonTexto + (resto > 0 ? ' ' + miles(resto) : '');
    }

    const partes = num.toFixed(2).split('.');
    const entero = parseInt(partes[0]);
    const decimales = partes[1];
    return `${millones(entero)} PESOS ${decimales}/100 M.N.`;
  }

  function actualizarImpuestosDelConcepto(index, nuevoImporte) {
    const concepto = document.querySelector(`#id_conceptos-${index}-importe`)?.closest('.formulario-concepto');
    if (!concepto) return;

    const impuestos = concepto.querySelectorAll(".formulario-impuesto");
    impuestos.forEach(impuesto => {
      const eliminado = impuesto.querySelector("[name$='-DELETE']")?.checked;
      if (eliminado) return;

      const baseInput = impuesto.querySelector('[name$="base"]');
      const porcentajeInput = impuesto.querySelector('[name$="porcentaje"]');
      const importeInput = impuesto.querySelector('[name$="importe"]');

      if (!baseInput || !porcentajeInput || !importeInput) return;

      // Actualizar base con nuevo importe
      baseInput.value = nuevoImporte.toFixed(2);

      // Calcular importe del impuesto si tiene porcentaje
      const porcentaje = parseFloat(porcentajeInput.value || 0);
      const nuevoImporteImpuesto = nuevoImporte * porcentaje;
      importeInput.value = nuevoImporteImpuesto.toFixed(2);
    });
  }


  function actualizarTotalesCompletos() {
    let subtotal = 0.0;
    let totalDescuentos = 0.0;
    let totalImpuestos = 0.0;

    const conceptos = document.querySelectorAll(".formulario-concepto");

    conceptos.forEach(concepto => {
        const inputImporte = concepto.querySelector("input[id$='-importe']");
        const importe = parseFloat(inputImporte?.value || 0);
        subtotal += importe;

        // Calcular descuentos
        const inputDescuento = concepto.querySelector("input[name$='descuento']");
        const descuento = parseFloat(inputDescuento?.value || 0);
        totalDescuentos += descuento;

        const impuestos = concepto.querySelectorAll(".formulario-impuesto");
        impuestos.forEach(imp => {
            const eliminado = imp.querySelector("[name$='-DELETE']")?.checked;
            if (eliminado) return;

            const importe = parseFloat(imp.querySelector("[name$='importe']")?.value || 0);
            const tipo = imp.querySelector("[name$='tipo']")?.value;
            const incluido = imp.querySelector("[name$='incluido']")?.checked;

            if (incluido) {
                subtotal -= importe;
            }

            if (tipo === 'Traslado') {
                totalImpuestos += importe;
            } else if (tipo === 'Retención') {
                totalImpuestos -= importe;
            }
        });
    });

    const tablaResumen = document.getElementById('tabla-impuestos-desglosados');
    if (tablaResumen) {
        tablaResumen.innerHTML = '';

        // Mostrar descuento si existe
        if (totalDescuentos > 0) {
            const filaDescuento = document.createElement('tr');
            filaDescuento.innerHTML = `
                <td class="text-end">Descuento</td>
                <td class="text-end">-$${totalDescuentos.toFixed(2)}</td>
            `;
            tablaResumen.appendChild(filaDescuento);
        }

        // Mostrar impuestos
        conceptos.forEach(concepto => {
            const impuestos = concepto.querySelectorAll(".formulario-impuesto");
            impuestos.forEach(imp => {
                const eliminado = imp.querySelector("[name$='-DELETE']")?.checked;
                if (eliminado) return;

                const importe = parseFloat(imp.querySelector("[name$='importe']")?.value || 0);
                const tipo = imp.querySelector("[name$='tipo']")?.value;
                const etiqueta = imp.querySelector(".label-impuesto-tipo")?.textContent || imp.querySelector("[name$='c_Impuesto']")?.value || "---";

                const signo = tipo === 'Retención' ? '-' : '';
                const fila = document.createElement('tr');
                fila.innerHTML = `
                    <td class="text-end">${etiqueta}</td>
                    <td class="text-end">${signo}$${importe.toFixed(2)}</td>
                `;
                tablaResumen.appendChild(fila);
            });
        });
    }

    const total = subtotal - totalDescuentos + totalImpuestos;

    document.getElementById('subtotal-general').textContent = `$${subtotal.toFixed(2)}`;
    document.getElementById('total-impuestos').textContent = `$${totalImpuestos.toFixed(2)}`;
    document.getElementById('total-general').textContent = `$${total.toFixed(2)}`;
    document.getElementById('cantidad-letra').textContent = `(${numeroALetras(total)})`;
  }

  document.addEventListener("DOMContentLoaded", function () {
    actualizarTotalesCompletos();

    // Recalcular cuando cambian campos relacionados
    document.body.addEventListener('input', function (e) {
      const name = e.target.name || '';
      if (
        name.includes('cantidad') || name.includes('valorUnitario') ||
        name.includes('importe') || name.includes('tipo') ||
        name.includes('base') || name.includes('incluido')
      ) {
        setTimeout(actualizarTotalesCompletos, 100);
      }
    });

    // También cuando el tipo de impuesto cambia por clic en la flecha
    document.body.addEventListener('change', function (e) {
      if (e.target.name?.endsWith('tipo')) {
        setTimeout(actualizarTotalesCompletos, 100);
      }
    });
  });

  document.body.addEventListener('input', function (e) {
    const input = e.target;
    const name = input.name || '';

    if (name.endsWith('porcentaje')) {
      const formularioImpuesto = input.closest('.formulario-impuesto');
      if (!formularioImpuesto) return;

      const base = parseFloat(formularioImpuesto.querySelector('[name$="base"]')?.value || 0);
      const porcentaje = parseFloat(input.value || 0);
      const tipo = formularioImpuesto.querySelector('[name$="tipo"]')?.value;

      const importeField = formularioImpuesto.querySelector('[name$="importe"]');
      if (importeField) {
        const importe = (base * porcentaje).toFixed(2);
        importeField.value = importe;
      }

      actualizarTotalesCompletos();
    }
  });
