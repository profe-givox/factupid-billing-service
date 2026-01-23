  // Inicializa Select2 en los campos de autocompletado
   function inicializarAutocompletados() {
     $('.admin-autocomplete').each(function () {
       const $this = $(this);
       if (!$this.hasClass("select2-hidden-accessible")) {
         $this.select2({
           width: 'resolve',
           theme: 'admin-autocomplete',
           ajax: {
             url: $this.data('ajax--url'),
             dataType: 'json',
             delay: $this.data('ajax--delay') || 250,
             data: function (params) {
               return {
                 term: params.term,
                 app_label: $this.data('app-label'),
                 model_name: $this.data('model-name'),
                 field_name: $this.data('field-name'),
               };
             },
             processResults: function (data) {
               return {
                 results: data.results || []
               };
             },
             cache: true
           },
           placeholder: $this.data('placeholder') || '',
           allowClear: $this.data('allow-clear') === 'true'
         });
       }
     });
   }

   // inicializar Select2 en los campos de autocompletado
    document.addEventListener("DOMContentLoaded", function () {
      const formularios = document.querySelectorAll(".formulario-concepto");
  
      formularios.forEach((formulario) => {
          // Descripción del producto SAT
          const selectProdServ = formulario.querySelector('select[name$="c_ClaveProdServ"]');
          const descripcionSATInput = formulario.querySelector(".descripcion-sat");
  
          if (selectProdServ && descripcionSATInput) {
              const selectedOption = selectProdServ.options[selectProdServ.selectedIndex];
              if (selectedOption && selectedOption.text.includes(" - ")) {
                  descripcionSATInput.value = selectedOption.text.split(" - ")[1].trim();
              }
          }
  
          // Nombre unidad SAT
          const selectUnidad = formulario.querySelector('select[name$="c_ClaveUnidad"]');
          const nombreUnidadInput = formulario.querySelector(".nombreunidad-sat");
  
          if (selectUnidad && nombreUnidadInput) {
              const selectedOption = selectUnidad.options[selectUnidad.selectedIndex];
              if (selectedOption && selectedOption.text.includes(" - ")) {
                  nombreUnidadInput.value = selectedOption.text.split(" - ")[1].trim();
              }
          }
      });
  });

  (function($) {
      $(document).ready(function() {
        // ClaveProdServ → llena descripción
        $(document).on('select2:select', 'select[name$="c_ClaveProdServ"]', function(e) {
          const select = $(this);
          const texto = e.params.data.text;
          const partes = texto.split(" - ");
          const descripcion = partes[1] || '';
  
          // Encuentra el input correspondiente (dentro del mismo formulario)
          const form = select.closest(".formulario-concepto");
          form.find('input.descripcion-sat').val(descripcion);
        });
  
        // ClaveUnidad → llena nombre unidad
        $(document).on('select2:select', 'select[name$="c_ClaveUnidad"]', function(e) {
          const select = $(this);
          const texto = e.params.data.text;
          const partes = texto.split(" - ");
          const nombreUnidad = partes[1] || '';
  
          const form = select.closest(".formulario-concepto");
          form.find('input.nombreunidad-sat').val(nombreUnidad);
        });
      });
  })(django.jQuery);

  document.addEventListener("DOMContentLoaded", function () {
      function enlazarEventosDescripcionSAT() {
        document.querySelectorAll('.formulario-concepto').forEach(formulario => {
          const selectClaveProd = formulario.querySelector('select[name$="c_ClaveProdServ"]');
          const inputDescripcionSAT = formulario.querySelector('input[readonly]:not([name])');
    
          const selectClaveUnidad = formulario.querySelector('select[name$="c_ClaveUnidad"]');
          const inputNombreUnidadSAT = formulario.querySelectorAll('input[readonly]:not([name])')[1];
    
          if (selectClaveProd && inputDescripcionSAT) {
            $(selectClaveProd).on('select2:select', function (e) {
              const texto = e.params.data.text;
              const partes = texto.split(" - ");
              inputDescripcionSAT.value = partes[1] || '';
            });
          }
    
          if (selectClaveUnidad && inputNombreUnidadSAT) {
            $(selectClaveUnidad).on('select2:select', function (e) {
              const texto = e.params.data.text;
              const partes = texto.split(" - ");
              inputNombreUnidadSAT.value = partes[1] || '';
            });
          }
        });
      }
    
      // Llamar inicialmente
      enlazarEventosDescripcionSAT();
    
      // Observar DOM por nuevos formularios
      const observer = new MutationObserver(() => {
        enlazarEventosDescripcionSAT();
      });
    
      observer.observe(document.getElementById("contenedor-conceptos"), {
        childList: true,
        subtree: true
      });
  });