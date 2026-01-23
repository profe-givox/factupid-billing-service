let plantillaFormularioTerra = null;
  
  function inicializarPlantillaTerra() {
    const primeraTerra = document.querySelector("#terra-formset-container .formulario-terra");
    if (primeraTerra && !plantillaFormularioTerra) {
      plantillaFormularioTerra = primeraTerra.cloneNode(true);
      console.log("✅ Plantilla Terra guardada.");
    }
  }
  
  function agregarFormularioTerra() {
    if (!plantillaFormularioTerra) {
      console.error("❌ No se encontró la plantilla de Terra.");
      return;
    }
  
    const container = document.getElementById("terra-formset-container");
    const totalFormsInput = document.getElementById("id_terra-TOTAL_FORMS");
    const total = parseInt(totalFormsInput.value || 0);
  
    const newForm = plantillaFormularioTerra.cloneNode(true);

    // Dentro de agregarFormularioTerra()
    const inputAddenda = newForm.querySelector('input[name$="-addenda"]');
    const idAddenda = document.querySelector('input[name="terra-0-addenda"]')?.value;
    if (inputAddenda && idAddenda) {
      inputAddenda.value = idAddenda;
    }


  
    // Actualiza los nombres y IDs
    newForm.querySelectorAll("[name], [id], label").forEach(el => {
      if (el.name) el.name = el.name.replace(/terra-\d+-/g, `terra-${total}-`);
      if (el.id) el.id = el.id.replace(/terra-\d+-/g, `terra-${total}-`);
      if (el.htmlFor) el.htmlFor = el.htmlFor.replace(/terra-\d+-/g, `terra-${total}-`);
    });
  
    // Limpia valores y elimina input ID si existe (para evitar conflictos)
    newForm.querySelectorAll("input, select, textarea").forEach(el => {
      if (el.name.includes("-id")) {
        el.remove();  // Elimina completamente el campo 'id'
        return;
      }

      if (el.type === "checkbox") {
        el.checked = false;
      } else if (!el.name.includes("DELETE")) {
        el.value = "";
      }
    });

  
    // Agrega botón eliminar
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "btn btn-sm btn-danger btn-delete-terra";
    btn.style = "position:absolute; top:0.5rem; right:0.5rem;";
    btn.innerHTML = '<i class="fas fa-trash-alt"></i>';
    newForm.appendChild(btn);
  
    container.appendChild(newForm);
    totalFormsInput.value = total + 1;
  
    actualizarBotonesEliminarTerra();
  }
  
  function actualizarBotonesEliminarTerra() {
    const formularios = document.querySelectorAll(".formulario-terra");
    formularios.forEach((form, i) => {
      const btn = form.querySelector(".btn-delete-terra");
      if (btn) {
        btn.style.display = i === 0 ? "none" : "inline-block";
      }
    });
  }
  
  document.addEventListener("click", function (e) {
    if (e.target.closest(".btn-delete-terra")) {
      const formulario = e.target.closest(".formulario-terra");
      const checkboxDelete = formulario.querySelector('input[type="checkbox"][name$="-DELETE"]');
  
      const totalFormsInput = document.getElementById("id_terra-TOTAL_FORMS");
      const initialFormsInput = document.getElementById("id_terra-INITIAL_FORMS");
  
      const total = parseInt(totalFormsInput.value);
      const initial = parseInt(initialFormsInput.value);
  
      const nameExample = formulario.querySelector('[name]').name;
      const match = nameExample.match(/terra-(\d+)-/);
      const index = match ? parseInt(match[1]) : null;
  
      if (checkboxDelete && index < initial) {
        checkboxDelete.checked = true;
        formulario.style.display = "none";
      } else {
        formulario.remove();
  
        const container = document.getElementById("terra-formset-container");
        const formularios = container.querySelectorAll(".formulario-terra");
        let nuevoIndex = initial;
  
        formularios.forEach((form, i) => {
          const checkbox = form.querySelector('input[type="checkbox"][name$="-DELETE"]');
          const isVisible = form.style.display !== "none";
  
          const nameField = form.querySelector('[name]');
          const match = nameField?.name.match(/terra-(\d+)-/);
          const currentIndex = match ? parseInt(match[1]) : null;
  
          if (currentIndex !== null && currentIndex >= initial && isVisible) {
            form.querySelectorAll('[name], [id], label').forEach(el => {
              if (el.name) el.name = el.name.replace(/terra-\d+-/, `terra-${nuevoIndex}-`);
              if (el.id) el.id = el.id.replace(/terra-\d+-/, `terra-${nuevoIndex}-`);
              if (el.htmlFor) el.htmlFor = el.htmlFor.replace(/terra-\d+-/, `terra-${nuevoIndex}-`);
            });
            nuevoIndex++;
          }
        });
  
        totalFormsInput.value = nuevoIndex;
      }
  
      actualizarBotonesEliminarTerra();
    }
  });
  
  document.addEventListener("DOMContentLoaded", actualizarBotonesEliminarTerra);
  
  const observer = new MutationObserver(() => {
    inicializarPlantillaTerra();
  });
  observer.observe(document.getElementById("formulario-tipo-addenda"), { childList: true, subtree: true });