document.addEventListener("DOMContentLoaded", function () {
    const contenedorAddenda = document.getElementById("contenedor-addenda");
    const botonAgregar = document.getElementById("btn-addenda");
    const botonEliminar = document.getElementById("btn-remove-addenda");
    const selectAddenda = document.getElementById("id_addenda_set-0-addenda");
    const idAddendaInput = document.getElementById("id_addenda_set-0-id");
  
    function cargarFormulario(tipo) {
      const idAddenda = idAddendaInput?.value || "";
      fetch(`/cfdi/ajax/addenda-form/?tipo=${tipo}&id_addenda=${idAddenda}`)
        .then(response => response.json())
        .then(data => {
          document.getElementById("formulario-tipo-addenda").innerHTML = data.html;
        });
    }
  
    botonAgregar?.addEventListener("click", function () {
      contenedorAddenda.style.display = "block";
      botonAgregar.classList.add("d-none");
      botonEliminar.classList.remove("d-none");
    });
  
    botonEliminar?.addEventListener("click", function () {
      contenedorAddenda.style.display = "none";
      botonAgregar.classList.remove("d-none");
      botonEliminar.classList.add("d-none");
  
      // Vacía el tipo de addenda y el formulario cargado
      if (selectAddenda) {
        selectAddenda.selectedIndex = 0;
      }
      document.getElementById("formulario-tipo-addenda").innerHTML = "";
    });
  
    selectAddenda?.addEventListener("change", function () {
      if (this.value) {
        cargarFormulario(this.value);
      } else {
        document.getElementById("formulario-tipo-addenda").innerHTML = "";
      }
    });
  
    // Mostrar automáticamente si ya hay una addenda seleccionada
    if (selectAddenda?.value) {
      contenedorAddenda.style.display = "block";
      botonAgregar.classList.add("d-none");
      botonEliminar.classList.remove("d-none");
      cargarFormulario(selectAddenda.value);
    }
  });