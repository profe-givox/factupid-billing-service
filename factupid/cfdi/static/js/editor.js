let editor;
const factura = {
  "factura": {
    "fVersion": "XXXXXXX",
    "fSerie": "XXXXXXX",
    "fFolio": "XXXXXXX",
    "fFecha_emision": "XXXXXXX",
    "fFecha_certificacion": "XXXXXXX",
    "fSello_SAT": "XXXXXXX",
    "fForma_pago": "XXXXXXX",
    "fNo_certificado": "XXXXXXX",
    "fCertificado_SAT": "XXXXXXX",
    "fCondicion_pago": "XXXXXXX",
    "fSubtotal": "XXXXXXX",
    "fDescuento": "XXXXXXX",
    "fMoneda": "XXXXXXX",
    "fTipo_cambio": "XXXXXXX",
    "fTotal": "XXXXXXX",
    "fTipo_de_comprobante": "XXXXXXX",
    "fExportacion": "XXXXXXX",
    "fMetodo_pago": "XXXXXXX",
    "fLugar_expedicion": "XXXXXXX",
    "fConfirmacion": "XXXXXXX",
    "fCveRetencion": "XXXX",
    "fDescRetencion": "XXXX",

    "fSerie_CSD_SAT": "XXXXXXX",
    "fFolio_fiscal": "XXXXXXX",
    "fTotal_con_letra": "XXXXXXX"
    
  },
  "info_global": {
    "iPeriodicidad": "XXXXXXX",
    "iMeses": "XXXXXXX",
    "iYear": "XXXXXXX"
  },
  "cfdi_relacionados": {
    "cfTipo_relacion": "XXXXXXX",
    "cfUUIDs_relacionados": "XXXXXXX"
  },
  "emisor": {
    "eRFC": "XXXXXXX",
    "eRazon_social": "XXXXXXX",
    "eRegimen_fiscal": "XXXXXXX",
    "eFac_Atr_adquiriente": "XXXXXXX",
    

    "eDomicilio_fiscal": "XXXXXXX",
    "eCurp": "XXXXXXX"
  },
  "receptor": {
    "rRFC": "XXXXXXX",
    "rRazon_social": "XXXXXXX",
    "rDomicilio_fiscal": "XXXXXXX",
    "rResidencia_fiscal": "XXXXXXX",
    "rNum_Reg_id_Trib": "XXXXXXX",
    "rRegimen_fiscal": "XXXXXXX",
    "rUso_CFDI": "XXXXXXX",
    "rNacionalidad": "XXXXXXX",
    "rCURP": "XXXXXXX",
  },
  "conceptos":[
    {
      "cCve_prod": "XXXXXXX",
      "cNum_id": "XXXXXXX",
      "cCantidad": "XXXXXXX",
      "cCve_Unidad": "XXXXXXX",   /* esta se agrego*/
      "cUnidad": "XXXXXXX",
      "cDescripcion": "XXXXXXX",
      "cValor_unitario": "XXXXXXX",
      "cImporte": "XXXXXXX",
      "cDescuento": "XXXXXXX",   /* esta se agrego*/
      "cObjeto_impuesto": "XXXXXXX",
      /* traslados*/
      "ctBase": "XXXXXXX",
      "ctImpuesto": "XXXXXXX",
      "ctTipoFactor": "XXXXXXX",
      "ctTasaOcuota": "XXXXXXX",
      "ctImporte": "XXXXXXX",
      /* retencion*/
      "crBase": "XXXXXXX",
      "crImpuesto": "XXXXXXX",
      "crTipoFactor": "XXXXXXX",
      "crTasaOcuota": "XXXXXXX",
      "crImporte": "XXXXXXX",
      /* ACuentaTerceros */
      "caRFC": "XXXXXXX",
      "caRazonSocial": "XXXXXXX",
      "caRegimenFiscal": "XXXXXXX",
      "caDomicilioFiscal": "XXXXXXX",
      /*Informacion Aduanera */
      "ciNumeroPedimento": "XXXXXXX",
      /*Cuenta predial*/
      "ccNumero": "XXXXXXX",
      /*Parte*/
      "cpCve_prod": "XXXXXXX",
      "cpNum_id": "XXXXXXX",
      "cpCantidad": "XXXXXXX",
      "cpUnidad": "XXXXXXX",
      "cpDescripcion": "XXXXXXX",
      "cpValor_unitario": "XXXXXXX",
      "cpImporte": "XXXXXXX",
      /* informacipon aduanera (parte)*/
      "cpNum_pedi": "XXXXXXX",
      
    }
  ],
  "impuesto": {
    "imTot_imp_Ret": "XXXXXXX",
    "imTot_imp_Tras": "XXXXXXX",
    /* retencion*/
    "imrImpuesto": "XXXXXXX",
    "imrImporte": "XXXXXXX",
    /* traslados*/
    "imBase": "XXXXXXX",
    "imtImpuesto": "XXXXXXX",
    "imMonto": "XXXXXXX",
    "imTipoFactor": "XXXXXXX",
    "imTasaOcuota": "XXXXXXX",
    "imtImporte": "XXXXXXX",

    "imImpuestos_Equiq": "XXXXXXX",    
  },
  "periodo":{
    "peMes_ini":"xxxxx",
    "peMes_fin":"xxxxx",
    "peEjercicio":"xxxxx"
  },
  "total_retenciones":{
    "trTotal_Operacion":"xxxxx",
    "trTotal_Grav":"xxxxx",
    "trTotal_Exent":"xxxxx",
    "trTotal_Renten":"xxxxx",
    "trUtilidadBimestral":"xxxxx",
    "trISR":"xxxxx",
    /* ImpRetenidos*/
    "trBase":"xxxxx",
    "trImpuesto":"xxxxx",
    "trMonto":"xxxxx",
    "trTipoPago":"xxxxx"
  },
  "notas": {
    
    "nSello_digital_contribuyente": "XXXXXXX",
    "nNota": "XXXXXXX",
    "nDisposicion_fiscal": "XXXXXXX",
    "nNorma": "XXXXXXX",
    "nLeyenda": "XXXXXXX",
    "nEfectos_fiscales_al_pago": "XXXXXXX"
  },
  "sncf":{
    "sMonto_Recurso": "XXXXXXX",
    "sOrigen_Recurso": "XXXXXXX"
  },
  "subcontratacion":{
    "suRFC": "XXXXXXX",
    "suTiempo": "XXXXXXX"
  },
  "empleado":{
    "emEmpleado": "XXXXXXX",
    "emRFC": "XXXXXXX",
    "emCURP": "XXXXXXX",
    "emDepartamento": "XXXXXXX",
    "emPuesto": "XXXXXXX",
    "emContrato": "XXXXXXX",
    "emRegimen": "XXXXXXX",
    "emAntiguedad": "XXXXXXX",
    "emNo_Empleado": "XXXXXXX",
    "emEntidad": "XXXXXXX",
    "emNSS": "XXXXXXX",
    "emPeriodicidad": "XXXXXXX",
    "emSindicalizado": "XXXXXXX",
    "emCodPostal": "XXXXXXX",
    "emInicio_rel_lab": "XXXXXXX",
    "emReg_patronal": "XXXXXXX",
    "emRiesgo": "XXXXXXX",
    "emJornada": "XXXXXXX",
    "emBanco": "XXXXXXX",
    "emClaBe": "XXXXXXX",
  },
  "nomina":{
    "noFecha_inicial_pago": "XXXXXXX",
    "noSalario_base": "XXXXXXX",
    "noFecha_final_pago": "XXXXXXX",
    "noSalario_diario_integrado": "XXXXXXX",
    "noFecha_pago": "XXXXXXX",
    "noDias_pagados": "XXXXXXX",
  },
  "percepciones":{
    "pClave": "XXXXXXX",
    "pConcepto": "XXXXXXX",
    "pImporte_exento": "XXXXXXX",
    "pImporte_gravado": "XXXXXXX", 
    "pTipo_percepcion": "XXXXXXX"
  },
  "horasExtra":{
    "hHoras_extra": "XXXXXXX",
    "hDias": "XXXXXXX",
    "hTipo_horas": "XXXXXXX",
    "hImporte_pagado": "XXXXXXX"
  },
  "accion":{
    "aPrecio_otorgarse": "XXXXXXX",
    "aValor_mercado": "XXXXXXX"
  },
  "indemnizaciones":{
    "inTotal": "XXXXXXX",
    "inAnios_Serv": "XXXXXXX",
    "inSueldo": "XXXXXXX",
    "inAcumulable": "XXXXXXX",
    "inNo_acumulable": "XXXXXXX"
  },
  "Deducciones":{
    "dClabe": "XXXXXXX",
    "dConcepto": "XXXXXXX",
    "dImporte": "XXXXXXX",
    "dTipo_deduccion": "XXXXXXX"
  },
  "otros_pagos":{
    "oClave":"xxxxx",
    "oConcepto":"xxxxx",
    "oImporte":"xxxxx",
    "oTipo_pago":"xxxxx"
  },
  "incapacidades":{
    "icDias_incapacidad":"xxxxx",
    "icImporte_Monetario":"xxxxx",
    "icTipo_Incapacidad":"xxxxx"
  },
  "total_deducciones":{
    "toTotal_Imp_Retenidos":"xxxxx",
    "toTotal_Otras_Deducciones": "xxxxx"
  },
  "total_percepciones":{
    "tpTotal_Exento":"xxxxx",
    "tpTotal_Grabado":"xxxxx",
    "tpTotal_JPR":"xxxxx",
    "tpTotal_Sep_Indemnizacion":"xxxxx",
    "tpTotal_percepciones":"xxxxx",
    "tpTotal_otros_pagos":"xxxxx",
    "tpTotal_deducciones":"xxxxx",
    "tpTotal":"xxxxx"
  },/* Campos de CFDI Traslado */
  "DetalleMercancia":{
    "dmCantidad":"xxxxx",
    "dmUnidad":"xxxxx",
    "dmClve":"xxxxx",
    "dmValor":"xxxxx",
    "dmTipo_material":"xxxxx",
    "dmEmbalaje":"xxxxx",
    "dmPeso":"xxxxx"
  },
  "CartaPorte":{
    "cpMotivo":"xxxxx",
    "cpMedio_transporte":"xxxxx",
    "cpTransporteInter":"xxxxx",
    "cpTipo_transporte":"xxxxx",
    "cpVia_transporte":"xxxxx",
  },
  "Trasporte":{
    "tPermisoSCT":"xxxxx",
    "tNumPermisoSCT":"xxxxx",
    "tAseguradora":"xxxxx",
    "tNumPoliza":"xxxxx",
    "tCont_Vehicular":"xxxxx",
    "tPlaca":"xxxxx",
    "tAnio":"xxxxx",
  },
  "Dir_Origen":{
    "doDomicilio":"xxxxx",
    "doRfc":"xxxxx",
    "doNombre":"xxxxx",
    "doResidencia_fiscal":"xxxxx",
    "doId_Trib":"xxxxx",
    "doFecha":"xxxxx",
  },
  "Dir_Destino":{
    "ddDomicilio":"xxxxx",
    "ddRfc":"xxxxx",
    "ddNombre":"xxxxx",
    "ddResidencia_fiscal":"xxxxx",
    "ddId_Trib":"xxxxx",
    "ddFecha":"xxxxx",
  },
  "Figura_Transporte":{
    "ftCargo":"xxxxx",
    "ftRFC":"xxxxx",
    "ftNombre":"xxxxx",
    "ftLicencia":"xxxxx",
    "ftResidencia_fiscal":"xxxxx",
    "ftId_Trib":"xxxxx",
  }

};

document.addEventListener("DOMContentLoaded", function () {
  
  editor = grapesjs.init({
    container: '#gjs',
    fromElement: true,
    height: '500px',
    width: 'auto',
    storageManager: false,
    panels: {
      defaults: [],
    },
    blockManager: {
        appendTo: '#blocks-collapse',
        blocks: [],
    },
    selectorManager: {
      appendTo: "#styles-collapse",
      //es para que sea general
      componentFirst: true,
      custom:true,
    },    
    styleManager: {
      appendTo: '#styles-collapse',
      sectors: [
        {
          name: 'Estilos globales',
          open: false,
          buildProps: ['background-color', 'color', 'font-family', 'font-size','font-weight','font-style','text-align'],
          properties: [
            {
              property: 'background-color',
              name: 'Color de fondo',
              type: 'color',
              defaults: '#ffffff',
            },
            {
              property: 'color',
              name: 'Color de fuente',
              type: 'color',
              defaults: '#000000',
            },
            {
              property: 'font-family',
              type: 'select',
              defaults: 'Arial, sans-serif',
              name: 'Fuente',
              options: [
                { value: 'Arial, sans-serif', name: 'Arial' },
                { value: 'Times New Roman, serif', name: 'Times New Roman' },
                { value: 'Courier New, monospace', name: 'Courier New' },
                { value: 'Georgia, serif', name: 'Georgia' },
              ],
            },
            {
              property: 'font-size',
              type: 'integer',
              name: 'Tamaño de letra',
              units: ['px'],
              unit: 'px',
              min: 1,
              max: 100,
            },
            {
              property: 'font-weight',
              type: 'radio',
              name: 'Negrita',
              defaults: '400',
              options: [
                { value: '400', name: 'Normal' },
                { value: 'bold', name: 'Negrita' },
              ],
            },
            
            {
              property: 'font-style',
              type: 'radio',
              name: 'Estilo de fuente',
              defaults: 'normal',
              options: [
                { value: 'normal', name: 'Normal' },
                { value: 'italic', name: 'Cursiva' }
              ],
            },
            {
              property: 'text-align',
              type: 'radio',
              name: 'Alineación',
              defaults: 'left',
              options: [
                { value: 'left', name: 'Izquierda' },
                { value: 'center', name: 'Centro' },
                { value: 'right', name: 'Derecha' },
                { value: 'justify', name: 'Justificado' },
              ],
            },
          ],
        },        
        {
          name: 'Estilos de tabla',
          open: true,
          selectors: ['td', 'th'],
          buildProps: [],
          properties: [
            {
              property: 'border-style',
              type: 'radio',
              name: 'Estilo de borde',
              defaults: 'none',
              options: [
                { value: 'none', name: 'Ninguno' },
                { value: 'solid', name: 'Sólido' },
                { value: 'dashed', name: 'Guiones' },
                { value: 'dotted', name: 'Punteado' },
                { value: 'double', name: 'Doble' },
              ],
            },
            {
              property: 'border-width',
              type: 'integer',
              name: 'Grosor del borde',
              units: ['px'],
              defaults: 1,
              min: 0,
              max: 4,
            },
            {
              property: 'border-color',
              type: 'color',
              name: 'Color del borde',
              defaults: '#000000',
            },
            {
              property: 'border-collapse',
              type: 'radio',
              name: 'Unión de celdas',
              defaults: 'collapse',
              options: [
                { value: 'none', name: 'Ninguno' },
                { value: 'collapse', name: 'Unir celdas' },
                { value: 'separate', name: 'Separar celdas' },
              ],
            },
            {
              name: 'Combinar columnas',
              property: 'attributes:colspan',
              type: 'integer',
              defaults: 1,
              min: 1,
              max: 6
            },
            {
              name: 'Combinar filas',
              property: 'attributes:rowspan',
              type: 'integer',
              defaults: 1,
              min: 1,
              max: 6
            }
          ],
        }
      ],
    },
    
    canvas:{
      styles:[
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css",
        "https://cdn.jsdelivr.net/npm/bootstrap-icons/font/bootstrap-icons.css"
      ],
      scripts:[
       "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"
      ]
    }
   });
  // Obtiene los tipos de modelos y los carga en el selector de modelos
  fetch('get-modelos/')
          .then(response => response.json())
          .then(data => {
              let select = document.getElementById("modeloSelect");
              data.forEach(modelo => {
                  let option = document.createElement("option");
                  option.value = modelo.id;
                  option.textContent = modelo.name;
                  select.appendChild(option);
              });
              let optionNuevo = document.createElement("option");
        optionNuevo.value = "nuevo";
        optionNuevo.textContent = "<< Crear nuevo modelo >>";
        select.appendChild(optionNuevo);
          })
          .catch(error => console.error("Error cargando modelos:", error));
  
  //################### APARTADO DE TABLAS##########################################
  //Agregar un contenedor de la factura Básica
  editor.BlockManager.add('FacturaBasica',{
    label: 'Factura básica',
    category: 'Facturas',
    attributes: { class: '' },
    content: `
      <style>
        .encabezado-resaltado{
          display: block;
          background-color: #c6ffb4;
          font-weight: bold;
          text-align: center;
          padding: 0px;
          border: 1px solid #dee2e6;
          
        }

        .encabezado-tabla{
          background-color: #c6ffb4;          
          text-align: center;
        }
        .etiqueta-encabezado{
          display: block;
          font-family: 'Arial', sans-serif; 
          font-size: 12px; 
          font-weight: bold;
          margin:0%;
          padding:0%;
        }
        .etiqueta{
          display: block;
          font-family: 'Arial', sans-serif; 
          font-size: 11px; 
          font-weight: bold;
          margin:0%;
          padding:0%;
        }
        .dato{
          display: block;
          word-wrap: break-word;     /* Esto permite que el texto largo se ajuste */
          overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
          white-space: normal;   /* Establece que el texto no se ajuste a la línea */
          font-family: 'Arial', sans-serif;
          font-size: 10px; 
          margin:0%;
          padding:0%;
          }
        .renglon {
            border: 1px solid #dee2e6;
        }
        .espacio-horizontal{
          height: 30px;
        }
        .espacio-vertical {
          width: 30px;
        }
        .textox {
          font-family: 'Arial', sans-serif;
          font-size: 11px;
        }
        .table th, .table td {
          padding: 0px;
          height: auto !important;
          vertical-align: top; 
        }
        
      </style>
      <section>
        <div class="row">
          <div class="col-12">
            <table class="table table-sm ">
              <tbody>
                <tr class="d-flex">
                  <td class="col-2 d-flex align-items-center">
                    <p class="etiqueta me-2">Folio:</p>
                    <p class="dato">[fFolio]</p>
                  </td>
                  <td class="col-2 d-flex align-items-center">
                    <p class="etiqueta me-2">Serie:</p>
                    <p class="dato">[fSerie]</p>
                  </td>
                  <td class="col-5 d-flex align-items-center">
                    <p class="etiqueta me-2">No. Certificado:</p>
                    <p class="dato">[fNo_certificado]</p>  
                  </td>
                  <td class="col-3 d-flex align-items-center">
                    <p class="etiqueta me-2">Versión CFDI:</p>
                    <p class="dato">[fVersion]</p>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="row">
          <div class="col-2">
            <img src="https://via.placeholder.com/150" id="Logo" alt="Logo" class="img-fluid" style="Border: 1px solid black; width: 147px; height: 110px;"/>
          </div>
          <div class="col-10 d-flex justify-content-between">
            <div class="col-5">
              <div class="row">
                
                  <table class="table table-sm">
                    <thead class="encabezado-tabla">
                      <tr>
                        <th colspan="2">Emisor</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <th class="col-4"><p class="etiqueta">Razón social: </p></th>
                        <td ><p class="dato">[eRazon_social]</p></td>
                      </tr>
                      <tr>
                        <th ><p class="etiqueta">RFC:</p></th>
                        <td ><p class="dato">[eRFC]</p></td>
                      </tr>
                      <tr>
                        <th ><p class="etiqueta">Domicio Fiscal:</p></th>
                        <td ><p class="dato">[eDomicilio_fiscal]</p></td>
                      </tr>
                      <tr>
                        <th ><p class="etiqueta">Fac. Atr. adquiriente:</p></th>
                        <td ><p class="dato">[eFac_Atr_adquiriente]</p></td>
                      </tr>
                      <tr>
                        <th ><p class="etiqueta">Lugar de expedición:</p></th>
                        <td ><p class="dato">[fLugar_expedicion]</p></td>
                      </tr>
                    </tbody>
                  </table>
                
              </div>
            </div>
            <div class="col-5">
              <div class="row">
                
                  <table class="table table-sm table-bordered">
                    <thead class="encabezado-tabla">
                      <tr>
                        <th colspan="2">Factura</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <th><p class="etiqueta">Folio fiscal:</p></th>
                        <td><p class="dato">[fFolio_fiscal]</p></td>
                      </tr>
                      <tr>
                        <th><p class="etiqueta">Serie CSD del SAT:</p></th>
                        <td><p class="dato">[fSerie_CSD_SAT]</p></td>
                      </tr>
                      <tr>
                        <th><p class="etiqueta">Tipo de comprobante:</p></th>
                        <td><p class="dato">[fTipo_de_comprobante]</p></td>
                      </tr>
                      <tr>
                        <th><p class="etiqueta">Fecha Certificación:</p></th>
                        <td><p class="dato">[fFecha_certificacion]</p></td>
                      </tr>
                      <tr>
                        <th><p class="etiqueta">Fecha emisión:</p></th>
                        <td><p class="dato">[fFecha_emision]</p></td>
                      </tr>
                    </tbody>
                  </table>
                
              </div>
            </div>
          </div>                  
        </div>

        <div class="row">
          <div class="col-4">
            <table class="table table-sm table-bordered text-center">
              <thead class="encabezado-tabla">
                <tr>
                  <th colspan="3">Información Global</th>
                </tr>
              </thead>
              <tbody>
                <tr >
                  <th><p class="etiqueta">Periodicidad</p></th>
                  <th><p class="etiqueta">Meses</p></th>
                  <th><p class="etiqueta">Año</p></th>
                </tr>
                <tr>
                  <td><p class="dato">[iPeriodicidad]</p></td>
                  <td><p class="dato">[iMeses]</p></td>
                  <td><p class="dato">[iYear]</p></td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="col-8">
            <div class="row">
              
                <table class="table table-sm table-bordered">
                  <thead class="encabezado-tabla">
                    <tr>
                      <th colspan="2">CFDIs Relacionados</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td class="col-3"><p class="etiqueta">Tipo de relación</p></td>
                      <td><p class="etiqueta">UUID(s) Relacionados</p></td>
                    </tr>
                    <tr>
                      <td ><p class="dato">[cfTipo_relacion]</p></td>
                      <td><p class="dato">[cfUUIDs_relacionados]</p></td>
                    </tr>
                  </tbody>
                </table>
              
            </div>
          </div>
        </div>

        <div class="row">
          <div class="col-12">
            <table class="table table-sm table-bordered">
              <thead class="encabezado-tabla">
                <tr>
                  <th colspan="6">Receptor</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td class="col-1"><p class="etiqueta">RFC:</p></td>
                  <td><p class="dato">[rRFC]</p></td>
                  <td><p class="etiqueta">Domicilio fiscal:</p></td>
                  <td><p class="dato">[rDomicilio_fiscal]</p></td>
                  <td><p class="etiqueta">Num. Reg. id. Trib.:</p></td>
                  <td><p class="dato">[rNum_Reg_id_Trib]</p></td>
                </tr>
                <tr>
                  <td><p class="etiqueta">Uso de CFDI:</p></td>
                  <td><p class="dato">[rUso_CFDI]</p></td>
                  <td><p class="etiqueta">Régimen fiscal:</p></td>
                  <td colspan="3"><p class="dato">[rRegimen_fiscal]</p></td>
                </tr>
                <tr>
                  
                  <td><p class="etiqueta">Razón social:</p></td>
                  <td><p class="dato">[rRazon_social]</p></td>
                  <td><p class="etiqueta">Residencia fiscal:</p></td>
                  <td colspan="3"><p class="dato">[rResidencia_fiscal]</p></td>
                  
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="row">
          <div class="col-12">
            <table class="table table-sm table-bordered">
              <thead class="encabezado-tabla">
                <tr>
                  <th colspan="8">Conceptos</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <th scope="col"><p class="etiqueta">Cve prod.</p></th>
                  <th scope="col"><p class="etiqueta">Num. de id</p></th>
                  <th scope="col"><p class="etiqueta">Cant.</p></th>
                  <th scope="col"><p class="etiqueta">Unidad</p></th>
                  <th scope="col"><p class="etiqueta">Descripción</p></th>
                  <th scope="col"><p class="etiqueta">Valor unitario</p></th>
                  <th scope="col"><p class="etiqueta">Objeto impuesto</p></th>
                  <th scope="col"><p class="etiqueta">Importe</p></th>
                </tr>
                <tr class="d-none">
                  <td>{% for conceptos in CFDI.conceptos %}</td>
                </tr>
                <tr>
                  <td><p class="dato">[cCve_prod]</p></td>
                  <td><p class="dato">[cNum_id]</p></td>
                  <td><p class="dato">[cCantidad]</p></td>
                  <td><p class="dato">[cUnidad]</p></td>
                  <td><p class="dato">[cDescripcion]</p></td>
                  <td><p class="dato">[cValor_unitario]</p></td>
                  <td><p class="dato">[cObjeto_impuesto]</p></td>
                  <td><p class="dato">[cImporte]</p></td>
                </tr>
                <tr class="d-none">
                  <td>{% endfor %}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="row d-flex justify-content-between">
          <div class="col-2">
              <img src="https://via.placeholder.com/150" id="QR" alt="Logo" class="img-fluid" style="Border: 1px solid black; width: 147px; height: 110px;"/>
          </div>
          <div class="col-7">
            <div class="row">
              
                <table class="table table-sm table-bordered">
                  <tbody>
                    <tr>
                      <td colspan="4" class="text-center"><p class="dato">[fTotal_con_letra]</p></td>
                    </tr>
                    <tr>
                      <td colspan="4" class="text-center"><p class="etiqueta">Total con letra</p></td>
                    </tr>
                    <tr>
                      <th class="col-3"><p class="etiqueta">Método de pago:</p></th>
                      <td><p class="dato">[fMetodo_pago]</p></td>
                      <th class="col-2"><p class="etiqueta">Moneda:</p></th>
                      <td><p class="dato">[fMoneda]</p></td>
                    </tr>
                    <tr>
                      <th><p class="etiqueta">Forma de pago:</p></th>
                      <td><p class="dato">[fForma_pago]</p></td>
                      <th><p class="etiqueta">Tipo-cambio:</p></th>
                      <td><p class="dato">[fTipo_cambio]</p></td>
                    </tr>
                    <tr>
                      <th><p class="etiqueta">Condición de pago:</p></th>
                      <td colspan="3"><p class="dato">[fCondicion_pago]</p></td>
                    </tr>
                  </tbody>
                </table>
              
            </div>
          </div>

          <div class="col-3">
            <div class="row">
              <div class="col-12">
                <table class="table table-sm table-bordered">
                  <tbody>
                    <tr>
                      <th><p class="etiqueta">Subtotal:</p></th>
                      <td><p class="dato">[fSubtotal]</p></td>
                    </tr>
                    <tr>
                      <th><p class="etiqueta">Impuestos Equiq.:</p></th>
                      <td><p class="dato">[imImpuestos_Equiq]</p></td>
                    </tr>
                    <tr>
                      <th><p class="etiqueta">Total Imp. Trasladados:</p></th>
                      <td><p class="dato">[imTot_imp_Tras]</p></td>
                    </tr>
                    <tr>
                      <th><p class="etiqueta">Total Imp. Retenidos:</p></th>
                      <td><p class="dato">[imTot_imp_Ret]</p></td>
                    </tr>
                    <tr>
                      <th><p class="etiqueta">Descuento:</p></th>
                      <td><p class="dato">[fDescuento]</p></td>
                    </tr>
                    <tr>
                      <th><p class="etiqueta">Total:</p></th>
                      <td><p class="dato">[fTotal]</p></td>
                    </tr>
                </table>
              </div>
            </div>
          </div>
        </div>

        

        <div class="row">
          <div class="col-12">    
            <table class="table table-sm table-bordered">
              <tr class="encabezado-tabla">
                <th  colspan="6">Notas</th>
              </tr>
              <tr>
                <td colspan="6"><p class="dato">[nNota]</p></td>
              </tr>
              <tr class="encabezado-tabla">
                <th colspan="6">LEYENDAS FISCALES</th>
              </tr>
              <tr>
                <th class="col-2"><p class="etiqueta">DISPOSICIÓN FISCAL:</p></th>
                <td><p class="dato">[nDisposicion_fiscal]</p></td>
                <th class="col-1"><p class="etiqueta">NORMA:</p></th>
                <td><p class="dato">[nNorma]</p></td>
                <th class="col-1"><p class="etiqueta">LEYENDA:</p></th>
                <td><p class="dato">[nLeyenda]</p></td>
              </tr>

            </table>
          </div>
        </div>
              

        <div class="row">
          <div class="col-12">
            <div class="row">
              <div class="col-12 encabezado-resaltado">Cadena original del complemento de certificación del SAT</div>
            </div>
            <div class="row">
              <div class="col-12 "><p class="dato renglon">[fCertificado_SAT]</p></div>
            </div>
            <div class="row">
              <div class="col-12 encabezado-resaltado">SELLO DIGITAL DEL SAT</div>
            </div>
            <div class="row">
              <div class="col-12 "><p class="dato renglon">[fSello_SAT]</p></div>
            </div>
            <div class="row">
              <div class="col-12 encabezado-resaltado">SELLO DIGITAL DEL CONTRIBUYENTE QUE LO EXPIDE</div>
            </div>
            <div class="row">
              <div class="col-12 "><p class="dato renglon">[nSello_digital_contribuyente]</p></div>
            </div>
          </div>
        </div>
        
      </section>
    `,
  });  
  //Agregar un contenedor de la factura Nomina
  editor.BlockManager.add('FacturaNomina',{
    label: 'Factura Nomina',
    category: 'Facturas',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        display: block;
        background-color: #b3eeda;
        font-weight: bold;
        text-align: center;
        padding: 0px;
        border: 1px solid #dee2e6;
        
      }
      .encabezado-tabla{
        background-color: #b3eeda;          
        text-align: center;
      }
      .etiqueta-encabezado{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 12px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .etiqueta{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        display: block;
        word-wrap: break-word;     /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        white-space: normal;   /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
        }
      .renglon {
          border: 1px solid #dee2e6;
      }
      .espacio-horizontal{
        height: 30px;
      }
      .espacio-vertical {
        width: 30px;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        
        vertical-align: top; 
      }
        
    </style>
    <section>

      <div class="row">
        <div class="col-12">
          <table class="table table-sm ">
            <tbody>
              <tr class="d-flex">
                <td class="col-2 d-flex align-items-center">
                  <p class="etiqueta me-2">Folio:</p>
                  <p class="dato">[fFolio]</p>
                </td>
                <td class="col-2 d-flex align-items-center">
                  <p class="etiqueta me-2">Serie:</p>
                  <p class="dato">[fSerie]</p>
                </td>
                <td class="col-5 d-flex align-items-center">
                  <p class="etiqueta me-2">No. Certificado:</p>
                  <p class="dato">[fNo_certificado]</p>  
                </td>
                <td class="col-3 d-flex align-items-center">
                  <p class="etiqueta me-2">Versión CFDI:</p>
                  <p class="dato">[fVersion]</p>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="row">
        <div class="col-2">
          <img src="https://via.placeholder.com/150" id="Logo" alt="Logo" class="img-fluid" style="Border: 1px solid black; width: 147px; height: 110px;"/>
        </div>
        <div class="col-10 d-flex justify-content-between">
          <div class="col-5">
            <div class="row">
              <table class="table table-sm">
                <thead class="encabezado-tabla">
                  <tr>
                    <th colspan="2">Emisor</th>
                  </tr>
                </thead>
                <tbody>
                  <tr >
                    <th><p class="etiqueta">Razón social:</p></th>
                    <td><p class="dato">[eRazon_social]</p></td>
                  </tr>
                  <tr>
                    <th><p class="etiqueta">RFC:</p></th>
                    <td><p class="dato">[eRFC]</p></td>
                  </tr>
                  <tr>
                    <th><p class="etiqueta">Curp:</p></th>
                    <td><p class="dato">[eCurp]</p></td>
                  </tr>
                  <tr>
                    <th><p class="etiqueta">Régimen fiscal:</p></th>
                    <td><p class="dato">[eRegimen_fiscal]</p></td>
                  </tr>
                  <tr>
                    <th><p class="etiqueta">Domicio Fiscal:</p></th>
                    <td><p class="dato">[eDomicilio_fiscal]</p></td>
                  </tr>
                  <tr>
                    <th><p class="etiqueta">Fac. Atr. adquiriente:</p></th>
                    <td><p class="dato">[eFac_Atr_adquiriente]</p></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          <div class="col-5">
            <div class="row">
              <table class="table table-sm table-bordered">
                <thead class="encabezado-tabla">
                  <tr>
                    <th colspan="2">Factura</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <th><p class="etiqueta">Folio fiscal:</p></th>
                    <td><p class="dato">[fFolio_fiscal]</p></td>
                  </tr>
                  <tr>
                    <th><p class="etiqueta">Serie CSD del SAT:</p></th>
                    <td><p class="dato">[fSerie_CSD_SAT]</p></td>
                  </tr>
                  <tr>
                    <th><p class="etiqueta">Tipo de comprobante:</p></td>
                    <td><p class="dato">[fTipo_de_comprobante]</p></th>
                  </tr>
                  <tr>
                    <th><p class="etiqueta">Fecha Certificación:</p></th>
                    <td><p class="dato">[fFecha_certificacion]</p></td>
                  </tr>
                  <tr>
                    <th><p class="etiqueta">Fecha emisión:</p></th>
                    <td><p class="dato">[fFecha_emision]</p></td>
                  </tr>
                  <tr>
                    <th><p class="etiqueta">Lugar de expedición:</p></th>
                    <td><p class="dato">[fLugar_expedicion]</p></td>
                  </tr>
                </tbody>
                </table>
            </div>
          </div>
        </div>                  
      </div>

      <div class="row">
        <div class="col-7">          
          <table class="table table-sm table-bordered">
            <thead class="encabezado-tabla">
              <tr>
                <th colspan="2">Entidad SNCF</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <th scope="col"><p class="etiqueta">Monto recurso</p></th>
                <th scope="col"><p class="etiqueta">Origen Recurso</p></th>
              </tr>
              <tr>
                <td><p class="dato">[sMonto_Recurso]</p></td>
                <td><p class="dato">[sOrigen_Recurso]</p></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="row">
        <div class="col-12">
          <table class="table table-sm table-bordered">
            <thead class="encabezado-tabla">
              <tr>
                <th colspan="6">Empleado</th>
              </tr>
            </thead>
            <tbody>                
                
              <tr>
                <th class="col-1"><p class="etiqueta">Empleado:</p></th>
                <td><p class="dato">[emEmpleado]</p></td>
                <th class="col-1"><p class="etiqueta">Puesto:</p></th>
                <td><p class="dato">[emPuesto]</p></td>
                <th class="col-1"><p class="etiqueta">Antigüedad:</p></th>
                <td><p class="dato">[emAntiguedad]</p></td>
              </tr>
              <tr>
                <th><p class="etiqueta">NSS:</p></th>
                <td><p class="dato">[emNSS]</p></td>
                <th><p class="etiqueta">Contrato:</p></th>
                <td><p class="dato">[emContrato]</p></td>
                <th><p class="etiqueta">Periodicidad:</p></th>
                <td><p class="dato">[emPeriodicidad]</p></td>
              </tr>
              <tr>
                <th><p class="etiqueta">CURP:</p></th>
                <td><p class="dato">[emCURP]</p></td>
                <th><p class="etiqueta">Entidad:</p></th>
                <td><p class="dato">[emEntidad]</p></td>
                <th><p class="etiqueta">Sindicalizado:</p></th>
                <td><p class="dato">[emSindicalizado]</p></td>
              </tr>
              <tr>
                <th><p class="etiqueta">RFC:</p></th>
                <td><p class="dato">[emRFC]</p></td>
                <th><p class="etiqueta">Régimen:</p></th>
                <td><p class="dato">[emRegimen]</p></td>
                <th><p class="etiqueta">Régimen pat.:</p></th>
                <td><p class="dato">[emReg_patronal]</p></td>
              </tr>
              <tr>
                <th><p class="etiqueta">Jornada:</p></th>
                <td><p class="dato">[emJornada]</p></td>
                <th><p class="etiqueta">CP:</p></th>
                <td><p class="dato">[emCodPostal]</p></td>
                <th><p class="etiqueta">Departamento:</p></th>
                <td><p class="dato">[emDepartamento]</p></td>

              </tr>
              <tr>
                <th><p class="etiqueta">Banco:</p></th>
                <td><p class="dato">[emBanco]</p></td>
                <th><p class="etiqueta">Riesgo:</p></th>
                <td><p class="dato">[emRiesgo]</p></td>
                <th><p class="etiqueta">Inicio rel. lab.:</p></th>
                <td><p class="dato">[emInicio_rel_lab]</p></td>
              </tr>
              <tr>
                <th><p class="etiqueta">ClaBe:</p></th>
                <td><p class="dato">[emClaBe]</p></td>
                <th><p class="etiqueta">No. Empleado:</p></th>
                <td><p class="dato">[emNo_Empleado]</p></td>
              </tr>
            </tbody>
          </table>    
        </div>
      </div>

      <div class="row d-flex justify-content-between">

        <div class="col-6">
          <table class="table table-sm table-bordered">
            <thead class="encabezado-tabla">
              <tr>
                <th colspan="2">CFDIs Relacionados</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <th scope="col"><p class="etiqueta">Tipo de relación</p></th>
                <th scope="col"><p class="etiqueta">UUID(s) Relacionados</p></th>
              </tr>
              <tr>
                <td><p class="dato">[cfTipo_relacion]</p></td>
                <td><p class="dato">[cfUUIDs_relacionados]</p></td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="col-5">
          <table class="table table-sm table-bordered">
            <thead class="encabezado-tabla">
              <tr>
                <th colspan="2">Subcontratación</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <th scope="col"><p class="etiqueta">RFC Laboral</p></th>
                <th scope="col"><p class="etiqueta">Tiempo(%)</p></th>
              </tr>
              <tr>
                <td><p class="dato">[suRFC]</p></td>
                <td><p class="dato">[suTiempo]</p></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="row">
        <div class="col-12">
          <table class="table table-sm table-bordered">
            <thead class="encabezado-tabla">
              <tr>
                <th colspan="6">Nómina</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <th scope="col"><p class="etiqueta">Fecha inicial del pago</p></th>
                <th scope="col"><p class="etiqueta">Salario base</p></th>
                <th scope="col"><p class="etiqueta">Fecha final del pago</p></th>
                <th scope="col"><p class="etiqueta">Salario diario integrado</p></th>
                <th scope="col"><p class="etiqueta">Fecha de pago</p></th>
                <th scope="col"><p class="etiqueta">Días pagados</p></th>
              </tr>
              <tr>
                <td><p class="dato">[noFecha_inicial_pago]</p></td>
                <td><p class="dato">[noSalario_base]</p></td>
                <td><p class="dato">[noFecha_final_pago]</p></td>
                <td><p class="dato">[noSalario_diario_integrado]</p></td>
                <td><p class="dato">[noFecha_pago]</p></td>
                <td><p class="dato">[noDias_pagados]</p></td>
              </tr>
            </tbody>
          </table>
          
        </div>
      </div>

      <div class="row">
        <div class="col-12">
          <table class="table table-sm table-bordered">
            <thead class="encabezado-tabla">
              <tr>
                <th colspan="5">Percepciones</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <th scope="col"><p class="etiqueta">Clave</p></th>
                <th scope="col"><p class="etiqueta">Concepto</p></th>
                <th scope="col"><p class="etiqueta">Importe exento</p></th>
                <th scope="col"><p class="etiqueta">Importe gravado</p></th>
                <th scope="col"><p class="etiqueta">Tipo de percepción</p></th>
              </tr>
              <tr>
                <td><p class="dato">[pClave]</p></td>
                <td><p class="dato">[pConcepto]</p></td>
                <td><p class="dato">[pImporte_exento]</p></td>
                <td><p class="dato">[pImporte_gravado]</p></td>
                <td><p class="dato">[pTipo_percepcion]</p></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="row">
        <div class="col-12">
          <table class="table table-sm table-bordered">
            <thead class="encabezado-tabla">
              <tr>
                <th colspan="4">Deducciones</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <th scope="col"><p class="etiqueta">Clave</p></th>
                <th scope="col"><p class="etiqueta">Concepto</p></th>
                <th scope="col"><p class="etiqueta">Importe</p></th>
                <th scope="col"><p class="etiqueta">Tipo de deducción</p></th>
              </tr>
              <tr>
                <td><p class="dato">[dClabe]</p></td>
                <td><p class="dato">[dConcepto]</p></td>
                <td><p class="dato">[dImporte]</p></td>
                <td><p class="dato">[dTipo_deduccion]</p></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="row d-flex justify-content-between">
        <div class="col-5">
          <table class="table table-sm table-bordered">
            <thead class="encabezado-tabla">
              <tr>
                <th colspan="4">Horas extra</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <th scope="col"><p class="etiqueta">Horas extra</p></th>
                <th scope="col"><p class="etiqueta">Días</p></th>
                <th scope="col"><p class="etiqueta">Tipo de horas</p></th>
                <th scope="col"><p class="etiqueta">Importe pagado</p></th>
              </tr>
              <tr>
                <td><p class="dato">[hHoras_extra]</p></td>
                <td><p class="dato">[hDias]</p></td>
                <td><p class="dato">[hTipo_horas]</p></td>
                <td><p class="dato">[hImporte_pagado]</p></td>
              </tr>
            </tbody>
          </table>
        </div>

        
        <div class="col-6">
          <table class="table table-sm table-bordered">
            <thead class="encabezado-tabla">
              <tr>
                <th colspan="5">Separaciones e indemnizaciones</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <th scope="col"><p class="etiqueta">Total</p></th>
                <th scope="col"><p class="etiqueta">Años de Serv.</p></th>
                <th scope="col"><p class="etiqueta">Sueldo</p></th>
                <th scope="col"><p class="etiqueta">Acumulable</p></th>
                <th scope="col"><p class="etiqueta">No acumulable</p></th>
              </tr>
              <tr>
                <td><p class="dato">[inTotal]</p></td>
                <td><p class="dato">[inAnios_Serv]</p></td>
                <td><p class="dato">[inSueldo]</p></td>
                <td><p class="dato">[inAcumulable]</p></td>
                <td><p class="dato">[inNo_acumulable]</p></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="row">
        <div class="col-8">
          <div class="row">
            
            <div class="col-6">
              <table class="table table-sm table-bordered">
                <thead class="encabezado-tabla">
                  <tr>
                    <th colspan="2">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <th scope="col"><p class="etiqueta">Precio al otorgarse</p></th>
                    <th scope="col"><p class="etiqueta">Valor del mercado</p></th>
                  </tr>
                  <tr>
                    <td><p class="dato">[aPrecio_otorgarse]</p></td>
                    <td><p class="dato">[aValor_mercado]</p></td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div class="col-6">
              <table class="table table-sm table-bordered">
                <thead class="encabezado-tabla">
                  <tr>
                    <th colspan="3">Incapacidad</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <th scope="col"><p class="etiqueta">Días</p></th>
                    <th scope="col"><p class="etiqueta">Importe monetario</p></th>
                    <th scope="col"><p class="etiqueta">Tipo</p></th>
                  </tr>
                  <tr>
                    <td><p class="dato">[icDias_incapacidad]</p></td>
                    <td><p class="dato">[icImporte_Monetario]</p></td>
                    <td><p class="dato">[icTipo_Incapacidad]</p></td>
                  </tr>
                </tbody>
              </table>
            </div>
            
          </div>
          
          <div class="row">
            <div class="col-12">
              <table class="table table-sm table-bordered">
                <thead class="encabezado-tabla">
                  <tr>
                    <th colspan="4">Otros pagos</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <th scope="col"><p class="etiqueta">Clave</p></th>
                    <th scope="col"><p class="etiqueta">Concepto</p></th>
                    <th scope="col"><p class="etiqueta">Importe</p></th>
                    <th scope="col"><p class="etiqueta">Tipo de pago</p></th>
                  </tr>
                  <tr>
                    <td><p class="dato">[oClave]</p></td>
                    <td><p class="dato">[oConcepto]</p></td>
                    <td><p class="dato">[oImporte]</p></td>
                    <td><p class="dato">[oTipo_pago]</p></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          
          <div class="row">
            <div class="col-2">
              <img src="https://via.placeholder.com/150" id="QR" alt="QR" class="img-fluid" style="Border: 1px solid black; width: 110px; height: 110px;"/>
            </div>
            <div class="col-10">
              <table class="table table-sm table-bordered">
                <thead class="encabezado-tabla">
                  <tr>
                    <th ></th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td colspan="4" class="text-center"><p class="dato">[fTotal_con_letra]</p></td>
                  </tr>
                  <tr>
                    <th colspan="4" class="text-center"><p class="etiqueta">Cantidad con letra</p></th>
                  </tr>
                  <tr>
                    <th><p class="etiqueta">Método de pago:</p></th>
                    <td><p class="dato">[fMetodo_pago]</p></td>
                    <th><p class="etiqueta">Moneda:</p></th>
                    <td><p class="dato">[fMoneda]</p></td>
                  </tr>
                  <tr>
                    <th><p class="etiqueta">Forma de pago:</p></th>
                    <td><p class="dato">[fForma_pago]</p></td>
                    <th><p class="etiqueta">Condición de pago:</p></th>
                    <td><p class="dato">[fCondicion_pago]</p></td>

                  </tr>
                </tbody>
              </table>
            
            </div>
          </div>
          
        </div>
        <div class="col-4">
          <table class="table table-sm table-bordered">
            <thead class="encabezado-tabla">
              <tr>
                <th colspan="2">Total Percepciones</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <th><p class="etiqueta">Total exento:</p></th>
                <td><p class="dato">[tpTotal_Exento]</p></td>
              </tr>
              <tr>
                <th><p class="etiqueta">Total grabado:</p></th>
                <td><p class="dato">[tpTotal_Grabado]</p></td>
              </tr>
              <tr>
                <th><p class="etiqueta">Total Jub, pensión, retiro:</p></th>
                <td><p class="dato">[tpTotal_JPR]</p></td>
              </tr>
              <tr>
                <th><p class="etiqueta">Total Sep. indemnización:</p></th>
                <td><p class="dato">[tpTotal_Sep_Indemnizacion]</p></td>
              </tr>
              <tr>
                <th><p class="etiqueta">Total percepciones:</p></th>
                <td><p class="dato">[tpTotal_percepciones]</p></td>
              </tr>
              <tr>
                <th><p class="etiqueta">Total otros pagos:</p></th>
                <td><p class="dato">[tpTotal_otros_pagos]</p></td>
              </tr>
              <tr>
                <th><p class="etiqueta">Total deducciones:</p></th>
                <td><p class="dato">[tpTotal_deducciones]</p></td>
              </tr>
              <tr>
                <th><p class="etiqueta">Total:</p></th>
                <td><p class="dato">[tpTotal]</p></td>
              </tr>
            </tbody>
          </table>
          
          <table class="table table-sm table-bordered">
            <thead class="encabezado-tabla">
              <tr>
                <th colspan="2">Total Deducciones</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <th><p class="etiqueta">Total Imp. retenidos:</p></th>
                <td><p class="dato">[toTotal_Imp_Retenidos]</p></td>
              </tr>
              <tr>
                <th><p class="etiqueta">Total otras deducciones:</p></th>
                <td><p class="dato">[toTotal_Otras_Deducciones]</p></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
      <div class="row">
        <div class="col-12">
          <div class="row">
            <div class="col-12 renglo encabezado-resaltado">Cadena original del complemento de certificación del SAT</div>
          </div>
          <div class="row">
            <div class="col-12 renglo"><p class="dato">[fCertificado_SAT]</p></div>
          </div>
          <div class="row">
            <div class="col-12 renglo encabezado-resaltado">Sello digital del SAT</div>
          </div>
          <div class="row">
            <div class="col-12 renglo"><p class="dato">[fSello_SAT]</p></div>
          </div>
          <div class="row">
            <div class="col-12 renglo encabezado-resaltado">Sello digital del contribuyente que lo expide</div> 
          </div>
          <div class="row">
            <div class="col-12 renglo"><p class="dato">[nSello_digital_contribuyente]</p></div>
          </div>    
          <div class="row">
            <div class="col-12 renglo encabezado-resaltado">Notas</div>
          </div>
          <div class="row">
            <div class="col-12 renglo"><p class="dato">[nNota]</p></div>
          </div>
          <div class="row">
            <div class="col-3 renglon" ><p class="etiqueta">Efectos fiscales al pago:</p></div>
            <div class="col-9 renglon" ><p class="dato">[nEfectos_fiscales_al_pago]</p></div>
          </div>
        </div>
      </div>
    </section>
    `,
  });
  //Agregar un contenedor de la factura Egreso
  editor.BlockManager.add('FacturaEgreso',{
    label: 'Factura Egreso',
    category: 'Facturas',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        background-color: #ffe4ca;
        font-weight: bold;
        text-align: center;
        padding: 4px 0;
        border: 1px solid #dee2e6;
        
      }
      .encabezado-tabla{
        background-color: #ffe4ca;          
        text-align: center;
      }
      .etiqueta{
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        word-wrap: break-word; /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        word-break: break-word; /* Alternativa para navegadores antiguos */
        white-space: normal; /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
      }
      .renglon {
          border: 1px solid #dee2e6;
      }
      .espacio-horizontal{
        height: 30px;
      }
      .espacio-vertical {
        width: 30px;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        vertical-align: top; 
      }
        
    </style>
      <section>
        <div class="row">
          <div class="col-12">
            <table class="table table-sm ">
              <tbody class="encabezado-tabla">
                <tr class="d-flex">
                  <td class="col-2 d-flex align-items-center">
                    <p class="etiqueta me-2">Folio:</p>
                    <p class="dato">[fFolio]</p>
                  </td>
                  <td class="col-2 d-flex align-items-center">
                    <p class="etiqueta me-2">Serie:</p>
                    <p class="dato">[fSerie]</p>
                  </td>
                  <td class="col-5 d-flex align-items-center">
                    <p class="etiqueta me-2">No. Certificado:</p>
                    <p class="dato">[fNo_certificado]</p>  
                  </td>
                  <td class="col-3 d-flex align-items-center">
                    <p class="etiqueta me-2">Versión CFDI:</p>
                    <p class="dato">[fVersion]</p>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="row">
          <div class="col-2">
            <img src="https://via.placeholder.com/150" id="Logo" alt="Logo" class="img-fluid" style="Border: 1px solid black; width: 147px; height: 110px;"/>
          </div>
          <div class="col-10 d-flex justify-content-between">
            <div class="col-5">
              <div class="row">
                <div class="col-12">
                  <table class="table table-sm table-bordered">
                    <thead class="encabezado-tabla">
                      <tr>
                        <th colspan="2">Emisor</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <th><p class="etiqueta">Razón social:</p></th>
                        <td><p class="dato">[eRazon_social]</p></td>
                      </tr>
                      <tr>
                        <th><p class="etiqueta">RFC:</p></th>
                        <td><p class="dato">[eRFC]</p></td>
                      </tr>
                      <tr>
                        <th><p class="etiqueta">Domicio Fiscal:</p></th>
                        <td><p class="dato">[eDomicilio_fiscal]</p></td>
                      </tr>
                      <tr>
                        <th><p class="etiqueta">Fac. Atr. adquiriente:</p></th>
                        <td><p class="dato">[eFac_Atr_adquiriente]</p></td>
                      </tr>
                      <tr>
                        <th><p class="etiqueta">Lugar de expedición:</p></th>
                        <td><p class="dato">[fLugar_expedicion]</p></td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
            <div class="col-5">
              <div class="row">
                <div class="col-12">
                  <table class="table table-sm table-bordered">
                    <thead class="encabezado-tabla">
                      <tr>
                        <th colspan="2">Factura</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <th><p class="etiqueta">Folio fiscal:</p></th>
                        <td><p class="dato">[fFolio_fiscal]</p></td>
                      </tr>
                      <tr>
                        <th><p class="etiqueta">Serie CSD del SAT:</p></th>
                        <td><p class="dato">[fSerie_CSD_SAT]</p></td>
                      </tr>
                      <tr>
                        <th><p class="etiqueta">Tipo de comprobante:</p></th>
                        <td><p class="dato">[fTipo_de_comprobante]</p></td>
                      </tr>
                      <tr>
                        <th><p class="etiqueta">Fecha Certificación:</p></th>
                        <td><p class="dato">[fFecha_certificacion]</p></td>
                      </tr>
                      <tr>
                        <th><p class="etiqueta">Fecha emisión:</p></th>
                        <td><p class="dato">[fFecha_emision]</p></td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>                  
        </div>

        <div class="row">
          <div class="col-6">
            <table class="table table-sm table-bordered text-center">
                <thead class="encabezado-tabla">
                  <tr>
                    <th colspan="3">Información Global</th>
                  </tr>
                </thead>
               <tbody>
                  <tr >
                    <th><p class="etiqueta">Periodicidad</p></th>
                    <th><p class="etiqueta">Meses</p></th>
                    <th><p class="etiqueta">Año</p></th>
                  </tr>
                  <tr>
                    <td><p class="dato">[iPeriodicidad]</p></td>
                    <td><p class="dato">[iMeses]</p></td>
                    <td><p class="dato">[iYear]</p></td>
                  </tr>
                </tbody>
              </table>
          </div>
        </div>

        <div class="row">
          <div class="col-12">
            <table class="table table-sm table-bordered">
              <thead class="encabezado-tabla">
                <tr>
                  <th colspan="2">CFDIs Relacionados</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td class="col-3"><p class="etiqueta">Tipo de relación</p></td>
                  <td><p class="etiqueta">UUID(s) Relacionados</p></td>
                </tr>
                <tr>
                  <td class="col-3"><p class="dato">[cfTipo_relacion]</p></td>
                  <td><p class="dato">[cfUUIDs_relacionados]</p></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="row">
          <div class="col-12">
            <table class="table table-sm table-bordered">
              <thead class="encabezado-tabla">
                <tr>
                  <th colspan="6">Receptor</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><p class="etiqueta">RFC:</p></td>
                  <td><p class="dato">[rRFC]</p></td>
                  <td><p class="etiqueta">Razón social:</p></td>
                  <td><p class="dato">[rRazon_social]</p></td>
                  <td><p class="etiqueta">Num. Reg. id. Trib.:</p></td>
                  <td><p class="dato">[rNum_Reg_id_Trib]</p></td>
                </tr>
                <tr>
                  <td><p class="etiqueta">Uso de CFDI:</p></td>
                  <td><p class="dato">[rUso_CFDI]</p></td>
                  <td><p class="etiqueta">Régimen fiscal:</p></td>
                  <td colspan="3"><p class="dato">[rRegimen_fiscal]</p></td>
                </tr>
                <tr>
                  <td><p class="etiqueta">Residencia fiscal:</p></td>
                  <td><p class="dato">[rResidencia_fiscal]</p></td>
                  <td><p class="etiqueta">Domicilio fiscal:</p></td>
                  <td colspan="3"><p class="dato">[rDomicilio_fiscal]</p></td>
                </tr>
              </tbody>
          </table>
          </div>
        </div>

        <div class="row">
          <div class="col-12">
            <table class="table table-sm table-bordered">
              <thead class="encabezado-tabla">
                <tr>
                  <th colspan="8">Conceptos</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <th scope="col"><p class="etiqueta">Cve prod.</p></th>
                  <th scope="col"><p class="etiqueta">Num. de id</p></th>
                  <th scope="col"><p class="etiqueta">Cant.</p></th>
                  <th scope="col"><p class="etiqueta">Unidad</p></th>
                  <th scope="col"><p class="etiqueta">Descripción</p></th>
                  <th scope="col"><p class="etiqueta">Valor unitario</p></th>
                  <th scope="col"><p class="etiqueta">Objeto impuesto</p></th>
                  <th scope="col"><p class="etiqueta">Importe</p></th>
                </tr>
                <tr class="d-none">
                  <td>{% for conceptos in CFDI.conceptos %}</td>
                </tr>
                <tr>
                  <td><p class="dato">[cCve_prod]</p></td>
                  <td><p class="dato">[cNum_id]</p></td>
                  <td><p class="dato">[cCantidad]</p></td>
                  <td><p class="dato">[cUnidad]</p></td>
                  <td><p class="dato">[cDescripcion]</p></td>
                  <td><p class="dato">[cValor_unitario]</p></td>
                  <td><p class="dato">[cObjeto_impuesto]</p></td>
                  <td><p class="dato">[cImporte]</p></td>
                </tr>
                <tr class="d-none">
                  <td>{% endfor %}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="row d-flex justify-content-between">
          <div class="col-2">
            <img src="https://via.placeholder.com/150" id="QR" alt="Logo" class="img-fluid" style="Border: 1px solid black; width: 147px; height: 110px;"/>
          </div>
          <div class="col-7">
            <div class="row">
              <div class="col-12">
                <table class="table table-sm table-bordered">
                  <tbody>
                    <tr>
                      <td colspan="4" class="text-center"><p class="dato">[fTotal_con_letra]</p></td>
                    </tr>
                    <tr>
                      <td colspan="4" class="text-center"><p class="etiqueta">Total con letra</p></td>
                    </tr>
                    <tr>
                      <th scope="row"><p class="etiqueta">Método de pago:</p></th>
                      <td><p class="dato">[fMetodo_pago]</p></td>
                      <th scope="row"><p class="etiqueta">Moneda:</p></th>
                      <td><p class="dato">[fMoneda]</p></td>
                    </tr>
                    <tr>
                      <th scope="row"><p class="etiqueta">Forma de pago:</p></th>
                      <td><p class="dato">[fForma_pago]</p></td>
                      <th scope="row"><p class="etiqueta">Tipo-cambio:</p></th>
                      <td><p class="dato">[fTipo_cambio]</p></td>
                    </tr>
                    <tr>
                      <th scope="row"><p class="etiqueta">Condición de pago:</p></th>
                      <td><p class="dato">[fCondicion_pago]</p></td>
                      <th scope="row"><p class="etiqueta">Confirmación:</p></th>
                      <td><p class="dato">[fConfirmacion]</p></td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <div class="col-3">
            <div class="row">
              <div class="col-12">
                <table class="table table-sm table-bordered">
                  <tbody>
                    <tr>
                      <th><p class="etiqueta">Subtotal:</p></th>
                      <td><p class="dato">[fSubtotal]</p></td>
                    </tr>
                    <tr>
                      <th><p class="etiqueta">Impuestos Equiq.:</p></th>
                      <td><p class="dato">[imImpuestos_Equiq]</p></td>
                    </tr>
                    <tr>
                      <th><p class="etiqueta">Total Imp. Trasladados:</p></th>
                      <td><p class="dato">[imTot_imp_Tras]</p></td>
                    </tr>
                    <tr>
                      <th><p class="etiqueta">Total Imp. Retenidos:</p></th>
                      <td><p class="dato">[imTot_imp_Ret]</p></td>
                    </tr>
                    <tr>
                      <th><p class="etiqueta">Descuento:</p></th>
                      <td><p class="dato">[fDescuento]</p></td>
                    </tr>
                    <tr>
                      <th><p class="etiqueta">Total:</p></th>
                      <td><p class="dato">[fTotal]</p></td>
                    </tr>
                </table>
              </div>
            </div>
          </div>
        </div>

        <div class="row">
          <div class="col-12">
            <div class="row">
              <div class="col-12 encabezado-resaltado">Cadena original del complemento de certificación del SAT</div>
            </div>
            <div class="row">
              <div class="col-12 "><p class="dato renglon">[fCertificado_SAT]</p></div>
            </div>
            <div class="row">
              <div class="col-12 encabezado-resaltado">SELLO DIGITAL DEL SAT</div>
            </div>
            <div class="row">
              <div class="col-12 "><p class="dato renglon">[fSello_SAT]</p></div>
            </div>
            <div class="row">
              <div class="col-12 encabezado-resaltado">SELLO DIGITAL DEL CONTRIBUYENTE QUE LO EXPIDE</div>
            </div>
            <div class="row">
              <div class="col-12 "><p class="dato renglon">[nSello_digital_contribuyente]</p></div>
            </div>
            <div class="row">
              <div class="col-12">
                <table class="table table-sm table-bordered">
                  <tr class="encabezado-tabla">
                    <th  colspan="6">Notas</th>
                  </tr>
                  <tr>
                    <td colspan="6"><p class="dato">[nNota]</p></td>
                  </tr>
                  <tr class="encabezado-tabla">
                    <th colspan="6">LEYENDAS FISCALES</th>
                  </tr>
                  <tr>
                    <th><p class="etiqueta">DISPOSICIÓN FISCAL:</p></th>
                    <td><p class="dato">[nDisposicion_fiscal]</p></td>
                    <th><p class="etiqueta">NORMA:</p></th>
                    <td><p class="dato">[nNorma]</p></td>
                    <th><p class="etiqueta">LEYENDA:</p></th>
                    <td><p class="dato">[nLeyenda]</p></td>
                  </tr>

                </table>
              </div>
            </div>
          </div>
        </div>
        
      </section>
    `,
  });
  //Agregar un contenedor de la factura Pago
  editor.BlockManager.add('FacturaPago',{
    label: 'Factura Pago',
    category: 'Facturas',
    attributes: { class: '' },
    content: `
      <style>
        .encabezado-resaltado{
          display: block;
          background-color: #d3d2e7;
          font-weight: bold;
          text-align: center;
          padding: 0px;
          border: 1px solid #dee2e6;
        }
        .encabezado-tabla{
          background-color: #d3d2e7;          
          text-align: center;
        }
        .etiqueta-encabezado{
          display: block;
          font-family: 'Arial', sans-serif; 
          font-size: 12px; 
          font-weight: bold;
          margin:0%;
          padding:0%;
        }
        .etiqueta{
          display: block;
          font-family: 'Arial', sans-serif; 
          font-size: 11px; 
          font-weight: bold;
          margin:0%;
          padding:0%;
        }
        .dato{
          display: block;
          word-wrap: break-word;     /* Esto permite que el texto largo se ajuste */
          overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
          white-space: normal;   /* Establece que el texto no se ajuste a la línea */
          font-family: 'Arial', sans-serif;
          font-size: 10px; 
          margin:0%;
          padding:0%;
          }
        .renglon {
            border: 1px solid #dee2e6;
        }
        .espacio-horizontal{
          height: 30px;
        }
        .espacio-vertical {
          width: 30px;
        }
        .textox {
          font-family: 'Arial', sans-serif;
          font-size: 11px;
        }
        .table th, .table td {
          padding: 0px;
          height: auto !important;
          vertical-align: top; 
        }
        
      </style>
      <section>
        <div class="row">
          <div class="col-12">
            <table class="table table-sm ">
              <tbody>
                <tr class="d-flex">
                  <td class="col-2 d-flex align-items-center">
                    <p class="etiqueta me-2">Folio:</p>
                    <p class="dato">[fFolio]</p>
                  </td>
                  <td class="col-2 d-flex align-items-center">
                    <p class="etiqueta me-2">Serie:</p>
                    <p class="dato">[fSerie]</p>
                  </td>
                  <td class="col-5 d-flex align-items-center">
                    <p class="etiqueta me-2">No. Certificado:</p>
                    <p class="dato">[fNo_certificado]</p>  
                  </td>
                  <td class="col-3 d-flex align-items-center">
                    <p class="etiqueta me-2">Versión CFDI:</p>
                    <p class="dato">[fVersion]</p>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="row"> 
          <div class="col-2">
            <img src="https://via.placeholder.com/150" id="Logo" alt="Logo" class="img-fluid" style="Border: 1px solid black; width: 147px; height: 110px;"/>
          </div>
          <div class="col-10 d-flex justify-content-between">
            <div class="col-5">
              <div class="row">
                
                  <table class="table table-sm">
                    <thead class="encabezado-tabla">
                      <tr>
                        <th colspan="2">Emisor</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <th class="col-4"><p class="etiqueta">Razón social: </p></th>
                        <td ><p class="dato">[eRazon_social]</p></td>
                      </tr>
                      <tr>
                        <th ><p class="etiqueta">RFC:</p></th>
                        <td ><p class="dato">[eRFC]</p></td>
                      </tr>
                      <tr>
                        <th ><p class="etiqueta">Domicio Fiscal:</p></th>
                        <td ><p class="dato">[eDomicilio_fiscal]</p></td>
                      </tr>
                      <tr>
                        <th ><p class="etiqueta">Fac. Atr. adquiriente:</p></th>
                        <td ><p class="dato">[eFac_Atr_adquiriente]</p></td>
                      </tr>
                      <tr>
                        <th ><p class="etiqueta">Lugar de expedición:</p></th>
                        <td ><p class="dato">[fLugar_expedicion]</p></td>
                      </tr>
                    </tbody>
                  </table>
                
              </div>
            </div>
            <div class="col-5">
              <div class="row">
                
                  <table class="table table-sm table-bordered">
                    <thead class="encabezado-tabla">
                      <tr>
                        <th colspan="2">Recibo de Pago</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <th class="col-5"><p class="etiqueta">Folio fiscal:</p></th>
                        <td><p class="dato">[fFolio_fiscal]</p></td>
                      </tr>
                      <tr>
                        <th><p class="etiqueta">Serie CSD del SAT:</p></th>
                        <td><p class="dato">[fSerie_CSD_SAT]</p></td>
                      </tr>
                      <tr>
                        <th><p class="etiqueta">Tipo de comprobante:</p></th>
                        <td><p class="dato">[fTipo_de_comprobante]</p></td>
                      </tr>
                      <tr>
                        <th><p class="etiqueta">Exportación:</p></th>
                        <td><p class="dato">[fExportacion]</p></td>
                      </tr>
                      <tr>
                        <th><p class="etiqueta">Fecha Certificación:</p></th>
                        <td><p class="dato">[fFecha_certificacion]</p></td>
                      </tr>
                      <tr>
                        <th><p class="etiqueta">Fecha emisión:</p></th>
                        <td><p class="dato">[fFecha_emision]</p></td>
                      </tr>
                      
                    </tbody>
                  </table>
                
              </div>
            </div>
          </div>                  
        </div>

        <div class="row">
          <div class="col-4">
            <table class="table table-sm table-bordered text-center">
              <thead class="encabezado-tabla">
                <tr>
                  <th colspan="3">Información Global</th>
                </tr>
              </thead>
              <tbody>
                <tr >
                  <th><p class="etiqueta">Periodicidad</p></th>
                  <th><p class="etiqueta">Meses</p></th>
                  <th><p class="etiqueta">Año</p></th>
                </tr>
                <tr>
                  <td><p class="dato">[iPeriodicidad]</p></td>
                  <td><p class="dato">[iMeses]</p></td>
                  <td><p class="dato">[iYear]</p></td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="col-8">
            <div class="row">
              
                <table class="table table-sm table-bordered">
                  <thead class="encabezado-tabla">
                    <tr>
                      <th colspan="2">CFDIs Relacionados</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td class="col-3"><p class="etiqueta">Tipo de relación</p></td>
                      <td><p class="etiqueta">UUID(s) Relacionados</p></td>
                    </tr>
                    <tr>
                      <td ><p class="dato">[cfTipo_relacion]</p></td>
                      <td><p class="dato">[cfUUIDs_relacionados]</p></td>
                    </tr>
                  </tbody>
                </table>
              
            </div>
          </div>
        </div>

        <div class="row">
          <div class="col-12 ">
            <table class="table table-sm table-bordered">
              <thead class="encabezado-tabla">
                <tr>
                  <th colspan="6">Receptor</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td class="col-1"><p class="etiqueta">RFC:</p></td>
                  <td class="col-2"><p class="dato">[rRFC]</p></td>
                  <td class="col-1"><p class="etiqueta">Razón social:</p></td>
                  <td class="col-3"><p class="dato">[rRazon_social]</p></td>
                  <td class="col-1"><p class="etiqueta">Domicilio fiscal:</p></td>
                  <td class="col-3"><p class="dato">[rDomicilio_fiscal]</p></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="row">
          <div class="col-12">
            <table class="table table-sm table-bordered">
              <thead class="encabezado-tabla">
                <tr>
                  <th colspan="8">Pago</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <th scope="col"><p class="etiqueta">Cve prod.</p></th>
                  <th scope="col"><p class="etiqueta">Num. de id</p></th>
                  <th scope="col"><p class="etiqueta">Cant.</p></th>
                  <th scope="col"><p class="etiqueta">Unidad</p></th>
                  <th scope="col"><p class="etiqueta">Descripción</p></th>
                  <th scope="col"><p class="etiqueta">Valor unitario</p></th>
                  <th scope="col"><p class="etiqueta">Objeto impuesto</p></th>
                  <th scope="col"><p class="etiqueta">Importe</p></th>
                </tr>
                <tr class="d-none">
                  <td>{% for conceptos in CFDI.conceptos %}</td>
                </tr>
                <tr>
                  <td><p class="dato">[cCve_prod]</p></td>
                  <td><p class="dato">[cNum_id]</p></td>
                  <td><p class="dato">[cCantidad]</p></td>
                  <td><p class="dato">[cUnidad]</p></td>
                  <td><p class="dato">[cDescripcion]</p></td>
                  <td><p class="dato">[cValor_unitario]</p></td>
                  <td><p class="dato">[cObjeto_impuesto]</p></td>
                  <td><p class="dato">[cImporte]</p></td>
                </tr>
                <tr class="d-none">
                  <td>{% endfor %}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="row d-flex justify-content-between">
          <div class="col-2">
              <img src="https://via.placeholder.com/150" id="QR" alt="Logo" class="img-fluid" style="Border: 1px solid black; width: 147px; height: 110px;"/>
          </div>
          <div class="col-7">
            <div class="row">
              
                <table class="table table-sm table-bordered">
                  <tbody>
                    <tr>
                      <td colspan="4" class="text-center"><p class="dato">[fTotal_con_letra]</p></td>
                    </tr>
                    <tr>
                      <td colspan="4" class="text-center"><p class="etiqueta">Total con letra</p></td>
                    </tr>
                    <tr>
                      <th class="col-3"><p class="etiqueta">Método de pago:</p></th>
                      <td><p class="dato">[fMetodo_pago]</p></td>
                      <th class="col-2"><p class="etiqueta">Moneda:</p></th>
                      <td><p class="dato">[fMoneda]</p></td>
                    </tr>
                    <tr>
                      <th><p class="etiqueta">Forma de pago:</p></th>
                      <td><p class="dato">[fForma_pago]</p></td>
                      <th><p class="etiqueta">Tipo-cambio:</p></th>
                      <td><p class="dato">[fTipo_cambio]</p></td>
                    </tr>
                    <tr>
                      <th><p class="etiqueta">Condición de pago:</p></th>
                      <td><p class="dato">[fCondicion_pago]</p></td>
                    </tr>
                  </tbody>
                </table>
              
            </div>
          </div>

          <div class="col-3">
            <div class="row">
              <div class="col-12">
                <table class="table table-sm table-bordered">
                  <tbody>
                    <tr>
                      <th><p class="etiqueta">Subtotal:</p></th>
                      <td><p class="dato">[fSubtotal]</p></td>
                    </tr>
                    <tr>
                      <th><p class="etiqueta">Impuestos Equiq.:</p></th>
                      <td><p class="dato">[imImpuestos_Equiq]</p></td>
                    </tr>
                    <tr>
                      <th><p class="etiqueta">Total Imp. Trasladados:</p></th>
                      <td><p class="dato">[imTot_imp_Tras]</p></td>
                    </tr>
                    <tr>
                      <th><p class="etiqueta">Total Imp. Retenidos:</p></th>
                      <td><p class="dato">[imTot_imp_Ret]</p></td>
                    </tr>
                    <tr>
                      <th><p class="etiqueta">Descuento:</p></th>
                      <td><p class="dato">[fDescuento]</p></td>
                    </tr>
                    <tr>
                      <th><p class="etiqueta">Total:</p></th>
                      <td><p class="dato">[fTotal]</p></td>
                    </tr>
                </table>
              </div>
            </div>
          </div>
        </div>

        <div class="row">
          <div class="col-12">
            <div class="row">
              <div class="col-12 encabezado-resaltado">Cadena original del complemento de certificación del SAT</div>
            </div>
            <div class="row">
              <div class="col-12 "><p class="dato renglon">[fCertificado_SAT]</p></div>
            </div>
            <div class="row">
              <div class="col-12 encabezado-resaltado">SELLO DIGITAL DEL SAT</div>
            </div>
            <div class="row">
              <div class="col-12 "><p class="dato renglon">[fSello_SAT]</p></div>
            </div>
            <div class="row">
              <div class="col-12 encabezado-resaltado">SELLO DIGITAL DEL CONTRIBUYENTE QUE LO EXPIDE</div>
            </div>
            <div class="row">
              <div class="col-12 "><p class="dato renglon">[nSello_digital_contribuyente]</p></div>
            </div>
          </div>
        </div>
        
      </section>
    `,
  });
  //Agregar un contenedor de la factura Pago
  editor.BlockManager.add('FacturaRetenciones',{
    label: 'Factura Retenciones',
    category: 'Facturas',
    attributes: { class: '' },
    content: `
      <style>
        .encabezado-resaltado{
          display: block;
          background-color: #d7c4ce;
          font-weight: bold;
          text-align: center;
          padding: 0px;
          border: 1px solid #dee2e6;
        }
        .encabezado-tabla{
          background-color: #d7c4ce;          
          text-align: center;
        }
        .etiqueta-encabezado{
          display: block;
          font-family: 'Arial', sans-serif; 
          font-size: 12px; 
          font-weight: bold;
          margin:0%;
          padding:0%;
        }
        .etiqueta{
          display: block;
          font-family: 'Arial', sans-serif; 
          font-size: 11px; 
          font-weight: bold;
          margin:0%;
          padding:0%;
        }
        .dato{
          display: block;
          word-wrap: break-word;     /* Esto permite que el texto largo se ajuste */
          overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
          white-space: normal;   /* Establece que el texto no se ajuste a la línea */
          font-family: 'Arial', sans-serif;
          font-size: 10px; 
          margin:0%;
          padding:0%;
          }
        .renglon {
            border: 1px solid #dee2e6;
        }
        .espacio-horizontal{
          height: 30px;
        }
        .espacio-vertical {
          width: 30px;
        }
        .textox {
          font-family: 'Arial', sans-serif;
          font-size: 11px;
        }
        .table th, .table td {
          padding: 0px;
          height: auto !important;
          vertical-align: top; 
        }
        
      </style>
      <section>
        <div class="row">
          <div class="col-12">
            <table class="table table-sm ">
              <tbody>
                <tr class="d-flex">
                  <td class="col-2 d-flex align-items-center">
                    <p class="etiqueta me-2">Folio:</p>
                    <p class="dato">[fFolio]</p>
                  </td>
                  <td class="col-2 d-flex align-items-center">
                    <p class="etiqueta me-2">Serie:</p>
                    <p class="dato">[fSerie]</p>
                  </td>
                  <td class="col-5 d-flex align-items-center">
                    <p class="etiqueta me-2">No. Certificado:</p>
                    <p class="dato">[fNo_certificado]</p>  
                  </td>
                  <td class="col-3 d-flex align-items-center">
                    <p class="etiqueta me-2">Versión CFDI:</p>
                    <p class="dato">[fVersion]</p>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="row"> 
          <div class="col-2">
            <img src="https://via.placeholder.com/150" id="Logo" alt="Logo" class="img-fluid" style="Border: 1px solid black; width: 147px; height: 110px;"/>
          </div>
          <div class="col-10 d-flex justify-content-between">
            <div class="col-5">
              <div class="row">
                
                  <table class="table table-sm">
                    <thead class="encabezado-tabla">
                      <tr>
                        <th colspan="2">Emisor</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <th class="col-4"><p class="etiqueta">Razón social: </p></th>
                        <td ><p class="dato">[eRazon_social]</p></td>
                      </tr>
                      <tr>
                        <th ><p class="etiqueta">RFC:</p></th>
                        <td ><p class="dato">[eRFC]</p></td>
                      </tr>
                      <tr>
                        <th ><p class="etiqueta">Regimen fiscal:</p></th>
                        <td ><p class="dato">[eRegimen_fiscal]</p></td>
                      </tr>
                      <tr>
                        <th ><p class="etiqueta">Lugar de expedición:</p></th>
                        <td ><p class="dato">[fLugar_expedicion]</p></td>
                      </tr>
                      <tr>
                        <th><p class="etiqueta">Fecha Certificación:</p></th>
                        <th><p class="dato">[fFecha_certificacion]</p></th>
                      </tr>
                      <tr>
                        <th><p class="etiqueta">Fecha emisión:</p></th>
                        <td><p class="dato">[fFecha_emision]</p></td>
                      </tr>
                    </tbody>
                  </table>
                
              </div>
            </div>
            <div class="col-5">
              <div class="row">
                
                  <table class="table table-sm table-bordered">
                    <thead class="encabezado-tabla">
                      <tr>
                        <th colspan="2">Receptor</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <th class="col-4"><p class="etiqueta">RFC:</p></th>
                        <td><p class="dato">[rRFC]</p></td>
                      </tr>
                      <tr>
                        <th><p class="etiqueta">Razón social:</p></th>
                        <td><p class="dato">[rRazon_social]</p></td>
                      </tr>
                      <tr>
                        <td><p class="etiqueta">CURP:</p></td>
                        <td><p class="dato">[rCURP]</p></td>
                      </tr>
                      <tr>
                        <th><p class="etiqueta">Domicilio fiscal:</p></th>
                        <td><p class="dato">[rDomicilio_fiscal]</p></td>
                      </tr>
                      <tr>
                        <th><p class="etiqueta">Nacionalidad:</p></th>
                        <td><p class="dato">[rNacionalidad]</p></td>
                      </tr>
                      <tr>
                        <th><p class="etiqueta">Num. Reg. id. trib.:</p></th>
                        <td><p class="dato">[rNum_Reg_id_Trib]</p></td>
                      </tr>
                      
                    </tbody>
                  </table>
                
              </div>
            </div>
          </div>                  
        </div>

        <div class="row">
          <div class="col-4">
            <table class="table table-sm table-bordered text-center">
              <thead class="encabezado-tabla">
                <tr>
                  <th colspan="3">Período</th>
                </tr>
              </thead>
              <tbody>
                <tr >
                  <th><p class="etiqueta">Mes inicio</p></th>
                  <th><p class="etiqueta">Mes final</p></th>
                  <th><p class="etiqueta">Año retención</p></th>
                </tr>
                <tr>
                  <td><p class="dato">[peMes_ini]</p></td>
                  <td><p class="dato">[peMes_fin]</p></td>
                  <td><p class="dato">[peEjercicio]</p></td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="col-8">
            <div class="row">
              
                <table class="table table-sm table-bordered">
                  <thead class="encabezado-tabla">
                    <tr>
                      <th colspan="2">CFDIs Relacionados</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td class="col-3"><p class="etiqueta">Tipo de relación</p></td>
                      <td><p class="etiqueta">UUID(s) Relacionados</p></td>
                    </tr>
                    <tr>
                      <td ><p class="dato">[cfTipo_relacion]</p></td>
                      <td><p class="dato">[cfUUIDs_relacionados]</p></td>
                    </tr>
                  </tbody>
                </table>
              
            </div>
          </div>
        </div>

        <div class="row">
          <div class="col-12 ">
            <table class="table table-sm table-bordered">
              <thead class="encabezado-tabla">
                <tr>
                  <th colspan="6">Retenciones</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <th class="col-3"><p class="etiqueta">Clave Retención:</p></th>
                  <th class="col"><p class="etiqueta">Descripción:</p></th>
                </tr>
                <tr>
                  <td><p class="dato">[fCveRetencion]</p></td>
                  <td><p class="dato">[fDescRetencion]</p></td>      
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="row d-flex justify-content-between">
          <div class="col-2">
              <img src="https://via.placeholder.com/150" id="QR" alt="Logo" class="img-fluid" style="Border: 1px solid black; width: 147px; height: 110px;"/>
          </div>
          <div class="col-7">
            <table class="table table-sm table-bordered">
              <thead class="encabezado-tabla">
                <tr>
                  <th colspan="8">Total de las retenciones</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <th scope="col"><p class="etiqueta">Base</p></th>
                  <th scope="col"><p class="etiqueta">Impuesto</p></th>
                  <th scope="col"><p class="etiqueta">Monto</p></th>
                  <th scope="col"><p class="etiqueta">Tipo de pago</p></th>
                </tr>
                
                <tr>
                  <td><p class="dato">[trBase]</p></td>
                  <td><p class="dato">[trImpuesto]</p></td>
                  <td><p class="dato">[trMonto]</p></td>
                  <td><p class="dato">[trTipoPago]</p></td>
                </tr>
                
              </tbody>
            </table>
          </div>

          <div class="col-3">
            <div class="row">
              <div class="col-12">
                <table class="table table-sm table-bordered">
                  <tbody>
                    <tr>
                      <th><p class="etiqueta">Total operaciones:</p></th>
                      <td><p class="dato">[trTotal_Operacion]</p></td>
                    </tr>
                    <tr>
                      <th><p class="etiqueta">Total gravado:</p></th>
                      <td><p class="dato">[trTotal_Grav]</p></td>
                    </tr>
                    <tr>
                      <th><p class="etiqueta">Total exento:</p></th>
                      <td><p class="dato">[trTotal_Exent]</p></td>
                    </tr>
                    <tr>
                      <th><p class="etiqueta">Total retenciones:</p></th>
                      <td><p class="dato">[trTotal_Renten]</p></td>
                    </tr>
                    <tr>
                      <th><p class="etiqueta">Utilidad bimestral:</p></th>
                      <td><p class="dato">[trUtilidadBimestral]</p></td>
                    </tr>
                    <tr>
                      <th><p class="etiqueta">ISR:</p></th>
                      <td><p class="dato">[trISR]</p></td>
                    </tr>
                </table>
              </div>
            </div>
          </div>
        </div>

        <div class="row">
          <div class="col-12">
            <div class="row">
              <div class="col-12 encabezado-resaltado">Cadena original del complemento de certificación del SAT</div>
            </div>
            <div class="row">
              <div class="col-12 "><p class="dato renglon">[fCertificado_SAT]</p></div>
            </div>
            <div class="row">
              <div class="col-12 encabezado-resaltado">SELLO DIGITAL DEL SAT</div>
            </div>
            <div class="row">
              <div class="col-12 "><p class="dato renglon">[fSello_SAT]</p></div>
            </div>
            <div class="row">
              <div class="col-12 encabezado-resaltado">SELLO DIGITAL DEL CONTRIBUYENTE QUE LO EXPIDE</div>
            </div>
            <div class="row">
              <div class="col-12 "><p class="dato renglon">[nSello_digital_contribuyente]</p></div>
            </div>
          </div>
        </div>
        
      </section>
    `,
  });
  //Agregar un contenedor de la factura Básica
  editor.BlockManager.add('FacturaTraslado',{
    label: 'Factura Traslado',
    category: 'Facturas',
    attributes: { class: '' },
    content: `
      <style>
        .encabezado-resaltado{
          display: block;
          background-color: #cccfeb;
          font-weight: bold;
          text-align: center;
          padding: 0px;
          border: 1px solid #dee2e6;
          
        }

        .encabezado-tabla{
          background-color: #cccfeb;          
          text-align: center;
        }
        .etiqueta-encabezado{
          display: block;
          font-family: 'Arial', sans-serif; 
          font-size: 12px; 
          font-weight: bold;
          margin:0%;
          padding:0%;
        }
        .etiqueta{
          display: block;
          font-family: 'Arial', sans-serif; 
          font-size: 11px; 
          font-weight: bold;
          margin:0%;
          padding:0%;
        }
        .dato{
          display: block;
          word-wrap: break-word;     /* Esto permite que el texto largo se ajuste */
          overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
          white-space: normal;   /* Establece que el texto no se ajuste a la línea */
          font-family: 'Arial', sans-serif;
          font-size: 10px; 
          margin:0%;
          padding:0%;
          }
        .renglon {
            border: 1px solid #dee2e6;
        }
        .espacio-horizontal{
          height: 30px;
        }
        .espacio-vertical {
          width: 30px;
        }
        .textox {
          font-family: 'Arial', sans-serif;
          font-size: 11px;
        }
        .table th, .table td {
          padding: 0px;
          height: auto !important;
          vertical-align: top; 
        }
        
      </style>
      <section>
        <div class="row">
          <div class="col-12">
            <table class="table table-sm ">
              <tbody>
                <tr class="d-flex">
                  <td class="col-2 d-flex align-items-center">
                    <p class="etiqueta me-2">Folio:</p>
                    <p class="dato">[fFolio]</p>
                  </td>
                  <td class="col-2 d-flex align-items-center">
                    <p class="etiqueta me-2">Serie:</p>
                    <p class="dato">[fSerie]</p>
                  </td>
                  <td class="col-5 d-flex align-items-center">
                    <p class="etiqueta me-2">No. Certificado:</p>
                    <p class="dato">[fNo_certificado]</p>  
                  </td>
                  <td class="col-3 d-flex align-items-center">
                    <p class="etiqueta me-2">Versión CFDI:</p>
                    <p class="dato">[fVersion]</p>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="row">
          <div class="col-2">
            <img src="https://via.placeholder.com/150" id="Logo" alt="Logo" class="img-fluid" style="Border: 1px solid black; width: 147px; height: 110px;"/>
          </div>
          <div class="col-10 d-flex justify-content-between">
            <div class="col-5">
              <div class="row">
                
                  <table class="table table-sm">
                    <thead class="encabezado-tabla">
                      <tr>
                        <th colspan="2">Emisor</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <th class="col-4"><p class="etiqueta">Razón social: </p></th>
                        <td ><p class="dato">[eRazon_social]</p></td>
                      </tr>
                      <tr>
                        <th ><p class="etiqueta">RFC:</p></th>
                        <td ><p class="dato">[eRFC]</p></td>
                      </tr>
                      <tr>
                        <th ><p class="etiqueta">Domicio Fiscal:</p></th>
                        <td ><p class="dato">[eDomicilio_fiscal]</p></td>
                      </tr>
                      <tr>
                        <th ><p class="etiqueta">Lugar de expedición:</p></th>
                        <td ><p class="dato">[fLugar_expedicion]</p></td>
                      </tr>
                    </tbody>
                  </table>
                
              </div>
            </div>
            <div class="col-5">
              <div class="row">
                
                  <table class="table table-sm table-bordered">
                    <thead class="encabezado-tabla">
                      <tr>
                        <th colspan="2">Factura traslado</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <th><p class="etiqueta">Folio fiscal:</p></th>
                        <td><p class="dato">[fFolio_fiscal]</p></td>
                      </tr>
                      <tr>
                        <th><p class="etiqueta">Serie CSD del SAT:</p></th>
                        <td><p class="dato">[fSerie_CSD_SAT]</p></td>
                      </tr>
                      <tr>
                        <th><p class="etiqueta">Tipo de comprobante:</p></th>
                        <td><p class="dato">[fTipo_de_comprobante]</p></td>
                      </tr>
                      <tr>
                        <th><p class="etiqueta">Fecha Certificación:</p></th>
                        <td><p class="dato">[fFecha_certificacion]</p></td>
                      </tr>
                      <tr>
                        <th><p class="etiqueta">Fecha emisión:</p></th>
                        <td><p class="dato">[fFecha_emision]</p></td>
                      </tr>
                    </tbody>
                  </table>
                
              </div>
            </div>
          </div>                  
        </div>

        

        <div class="row">
          <div class="col-5">
            <table class="table table-sm table-bordered">
              <thead class="encabezado-tabla">
                <tr>
                  <th colspan="2">Receptor</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <th class="col-3"><p class="etiqueta">RFC:</p></th>
                  <td><p class="dato">[rRFC]</p></td>
                </tr>
                <tr>
                  <th><p class="etiqueta">Domicilio fiscal:</p></th>
                  <td><p class="dato">[rDomicilio_fiscal]</p></td>
                </tr>
                <tr>
                  <th><p class="etiqueta">Uso de CFDI:</p></th>
                  <td><p class="dato">[rUso_CFDI]</p></td>
                </tr>
                <tr>
                  <th><p class="etiqueta">Razón social:</p></th>
                  <td><p class="dato">[rRazon_social]</p></td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="col-7">
              
                <table class="table table-sm table-bordered">
                  <thead class="encabezado-tabla">
                    <tr>
                      <th colspan="2">CFDIs Relacionados</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td class="col-3"><p class="etiqueta">Tipo de relación</p></td>
                      <td><p class="etiqueta">UUID(s) Relacionados</p></td>
                    </tr>
                    <tr>
                      <td ><p class="dato">[cfTipo_relacion]</p></td>
                      <td><p class="dato">[cfUUIDs_relacionados]</p></td>
                    </tr>
                  </tbody>
                </table>
              
                <table class="table table-sm table-bordered">
                  <tbody>
                    <tr>
                      <th class="col-3"><p class="etiqueta">Método de pago:</p></th>
                      <td><p class="dato">[fMetodo_pago]</p></td>
                      <th class="col-2"><p class="etiqueta">Moneda:</p></th>
                      <td><p class="dato">[fMoneda]</p></td>
                    </tr>
                    <tr>
                      <th><p class="etiqueta">Forma de pago:</p></th>
                      <td><p class="dato">[fForma_pago]</p></td>
                      <th><p class="etiqueta">Tipo-cambio:</p></th>
                      <td><p class="dato">[fTipo_cambio]</p></td>
                    </tr>
                  </tbody>
                </table>
              
            
              
            </div>
        </div>

        <div class="row">
          <div class="col-12">
            <table class="table table-sm table-bordered">
              <thead class="encabezado-tabla">
                <tr>
                  <th colspan="8">Conceptos</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <th scope="col"><p class="etiqueta">Cve prod.</p></th>
                  <th scope="col"><p class="etiqueta">Num. de id</p></th>
                  <th scope="col"><p class="etiqueta">Cant.</p></th>
                  <th scope="col"><p class="etiqueta">Unidad</p></th>
                  <th scope="col"><p class="etiqueta">Descripción</p></th>
                  <th scope="col"><p class="etiqueta">Valor unitario</p></th>
                  <th scope="col"><p class="etiqueta">Objeto impuesto</p></th>
                  <th scope="col"><p class="etiqueta">Importe</p></th>
                </tr>
                <tr class="d-none">
                  <td>{% for conceptos in CFDI.conceptos %}</td>
                </tr>
                <tr>
                  <td><p class="dato">[cCve_prod]</p></td>
                  <td><p class="dato">[cNum_id]</p></td>
                  <td><p class="dato">[cCantidad]</p></td>
                  <td><p class="dato">[cUnidad]</p></td>
                  <td><p class="dato">[cDescripcion]</p></td>
                  <td><p class="dato">[cValor_unitario]</p></td>
                  <td><p class="dato">[cObjeto_impuesto]</p></td>
                  <td><p class="dato">[cImporte]</p></td>
                </tr>
                <tr class="d-none">
                  <td>{% endfor %}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="row d-flex justify-content-between">
          <div class="col-2">
              <img src="https://via.placeholder.com/150" id="QR" alt="Logo" class="img-fluid" style="Border: 1px solid black; width: 147px; height: 110px;"/>
          </div>
            
          <div class="col-7">
            <table class="table table-sm table-bordered">
              <thead class="encabezado-tabla">
                <tr>
                  <th colspan="8">Total de las traslaciones</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <th scope="col"><p class="etiqueta">Base</p></th>
                  <th scope="col"><p class="etiqueta">Impuesto</p></th>
                  <th scope="col"><p class="etiqueta">Tipo de factor</p></th>
                  <th scope="col"><p class="etiqueta">Tasa de ocuota</p></th>
                  <th scope="col"><p class="etiqueta">Importe</p></th>
                </tr>
                
                <tr>
                  <td><p class="dato">[ctBase]</p></td>
                  <td><p class="dato">[ctImpuesto]</p></td>
                  <td><p class="dato">[ctTipoFactor]</p></td>
                  <td><p class="dato">[ctTasaOcuota]</p></td>
                  <td><p class="dato">[ctImporte]</p></td>
                </tr>
                
              </tbody>
            </table>
          </div>
          

          <div class="col-3">
            <div class="row">
              <div class="col-12">
                <table class="table table-sm table-bordered">
                  <tbody>
                    <tr>
                      <th><p class="etiqueta">Subtotal:</p></th>
                      <td><p class="dato">[fSubtotal]</p></td>
                    </tr>
                    <tr>
                      <th><p class="etiqueta">Impuestos Equiq.:</p></th>
                      <td><p class="dato">[imImpuestos_Equiq]</p></td>
                    </tr>
                    <tr>
                      <th><p class="etiqueta">Total Imp. Trasladados:</p></th>
                      <td><p class="dato">[imTot_imp_Tras]</p></td>
                    </tr>
                    <tr>
                      <th><p class="etiqueta">Total Imp. Retenidos:</p></th>
                      <td><p class="dato">[imTot_imp_Ret]</p></td>
                    </tr>
                    <tr>
                      <th><p class="etiqueta">Descuento:</p></th>
                      <td><p class="dato">[fDescuento]</p></td>
                    </tr>
                    <tr>
                      <th><p class="etiqueta">Total:</p></th>
                      <td><p class="dato">[fTotal]</p></td>
                    </tr>
                </table>
              </div>
            </div>
          </div>
        </div>
        <div class="row">
          <div class="col-12">
            <table class="table table-sm table-bordered">
              <thead class="encabezado-tabla">
                <tr>
                  <th colspan="4" class="text-center">Detalle carta porte</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <th><p class="etiqueta">Medio de transporte</p></th>
                  <th><p class="etiqueta">Transporte internacional</p></th>
                  <th><p class="etiqueta">Tipo de transporte</p></th>
                  <th><p class="etiqueta">Vía de transporte</p></th>
                </tr>
                <tr>
                  <td><p class="dato">[cpMedio_transporte]</p></td>
                  <td><p class="dato">[cpTransporteInter]</p></td>
                  <td><p class="dato">[cpTipo_transporte]</p></td>
                  <td><p class="dato">[cpVia_transporte]</p></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="row">
          <div class="col-12">
            <table class="table table-sm table-bordered">
              <thead class="encabezado-tabla">
                <tr>
                  <th colspan="7" class="text-center">Detalle del transporte</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <th><p class="etiqueta">Permiso SCT</p></th>
                  <th><p class="etiqueta">No. SCT</p></th>
                  <th><p class="etiqueta">Aseguradora</p></th>
                  <th><p class="etiqueta">No. poliza</p></th>
                  <th><p class="etiqueta">Configuración Vehicular</p></th>
                  <th><p class="etiqueta">Placa</p></th>
                  <th><p class="etiqueta">Año</p></th>
                </tr>
                <tr>
                  <td><p class="dato">[tPermisoSCT]</p></td>
                  <td><p class="dato">[tNumPermisoSCT]</p></td>
                  <td><p class="dato">[tAseguradora]</p></td>
                  <td><p class="dato">[tNumPoliza]</p></td>
                  <td><p class="dato">[tCont_Vehicular]</p></td>
                  <td><p class="dato">[tPlaca]</p></td>
                  <td><p class="dato">[tAnio]</p></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="row">
          <div class="col-12">
            <table class="table table-sm table-bordered">
              <thead class="encabezado-tabla">
                <tr>
                  <th colspan="7" class="text-center">Origen / Destino</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <th><p class="etiqueta"></p></th>
                  <th><p class="etiqueta">Domicilio</p></th>
                  <th><p class="etiqueta">RFC</p></th>
                  <th><p class="etiqueta">Nombre</p></th>
                  <th><p class="etiqueta">Residencia Fiscal</p></th>
                  <th><p class="etiqueta">Identidad tributaria</p></th>
                  <th><p class="etiqueta">Fecha salida/llegada</p></th>
                </tr>
                <tr>
                  <td><p class="etiqueta">Remitente</p></td>
                  <td><p class="dato">[doDomicilio]</p></td>
                  <td><p class="dato">[doRfc]</p></td>
                  <td><p class="dato">[doNombre]</p></td>
                  <td><p class="dato">[doResidencia_fiscal]</p></td>
                  <td><p class="dato">[doId_Trib]</p></td>
                  <td><p class="dato">[doFecha]</p></td>
                </tr>
                <tr>
                  <td><p class="etiqueta">Destinatario</p></td>
                  <td><p class="dato">[ddDomicilio]</p></td>
                  <td><p class="dato">[ddRfc]</p></td>
                  <td><p class="dato">[ddNombre]</p></td>
                  <td><p class="dato">[ddResidencia_fiscal]</p></td>
                  <td><p class="dato">[ddId_Trib]</p></td>
                  <td><p class="dato">[ddFecha]</p></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="row">
          <div class="col-12">
            <table class="table table-sm table-bordered">
              <thead class="encabezado-tabla">
                <tr>
                  <th colspan="6" class="text-center">Figuras de transporte</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <th><p class="etiqueta">Cargo</p></th>
                  <th><p class="etiqueta">RFC</p></th>
                  <th><p class="etiqueta">Nombre</p></th>
                  <th><p class="etiqueta">Licencia</p></th>
                  <th><p class="etiqueta">Residencia Fiscal</p></th>
                  <th><p class="etiqueta">Identidad tributaria</p></th>                  
                </tr>
                <tr>
                  <td><p class="dato">[ftCargo]</p></td>
                  <td><p class="dato">[ftRFC]</p></td>
                  <td><p class="dato">[ftNombre]</p></td>
                  <td><p class="dato">[ftLicencia]</p></td>
                  <td><p class="dato">[ftResidencia_fiscal]</p></td>
                  <td><p class="dato">[ftId_Trib]</p></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="row">
          <div class="col-12">
            <table class="table table-sm table-bordered">
              <thead class="encabezado-tabla">
                <tr>
                  <th colspan="7" class="text-center">Detalle de la mercancia</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <th><p class="etiqueta">Clave</p></th>
                  <th><p class="etiqueta">Unidad</p></th>
                  <th><p class="etiqueta">Valor</p></th>
                  <th><p class="etiqueta">Cantidad</p></th>
                  <th><p class="etiqueta">Tipo material</p></th>
                  <th><p class="etiqueta">Embalaje</p></th>
                  <th><p class="etiqueta">Peso</p></th>
                </tr>
                <tr>
                  <td><p class="dato">[dmClve]</p></td>
                  <td><p class="dato">[dmUnidad]</p></td>
                  <td><p class="dato">[dmValor]</p></td>
                  <td><p class="dato">[dmCantidad]</p></td>
                  <td><p class="dato">[dmTipo_material]</p></td>
                  <td><p class="dato">[dmEmbalaje]</p></td>
                  <td><p class="dato">[dmPeso]</p></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="row">
          <div class="col-12">
            <div class="row">
              <div class="col-12 encabezado-resaltado">Cadena original del complemento de certificación del SAT</div>
            </div>
            <div class="row">
              <div class="col-12 "><p class="dato renglon">[fCertificado_SAT]</p></div>
            </div>
            <div class="row">
              <div class="col-12 encabezado-resaltado">SELLO DIGITAL DEL SAT</div>
            </div>
            <div class="row">
              <div class="col-12 "><p class="dato renglon">[fSello_SAT]</p></div>
            </div>
            <div class="row">
              <div class="col-12 encabezado-resaltado">SELLO DIGITAL DEL CONTRIBUYENTE QUE LO EXPIDE</div>
            </div>
            <div class="row">
              <div class="col-12 "><p class="dato renglon">[nSello_digital_contribuyente]</p></div>
            </div>
          </div>
        </div>
        
      </section>
    `,
  });  
  //Agregar un contenedor de la factura Básica versión1
  editor.BlockManager.add('FacturaBasicaV1',{
    label: 'Factura básica versión1',
    category: 'Facturas',
    attributes: { class: '' },
    content: `
      <style>
        .encabezado{
          height: 30px;
        }
        .encabezado-resaltado{
          background-color: #92D46C;
          Border: 1px solid black;
          text-align: center;
        }
        .etiqueta{
          font-family: 'Arial', sans-serif; 
          font-size: 11px; 
          font-weight: bold;
          margin:0%;
          padding:0%;
        }
        .dato{
          word-wrap: break-word; /* Esto permite que el texto largo se ajuste */
          overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
          font-family: 'Arial', sans-serif;
          font-size: 10px; 
          margin:0%;
          padding:0%;
        }
        .renglon {
            border-bottom: 1px solid black;
            border-left: 1px solid black;
            box-sizing: border-box; /* Hace que el borde se quede dentro */
        }
        .renglon:last-child {
            border-right: .5px solid black;
            box-sizing: border-box; /* Asegura que el borde derecho también quede dentro */
        }
        .espacio-horizontal{
          height: 30px;
        }
        .espacio-vertical {
          width: 30px;
        }
        .textox {
          font-family: 'Arial', sans-serif;
          font-size: 11px;
        }
        
      </style>
      <section>
        <div class="row encabezado-resaltado encabezado align-items-end">
          <div class="col-4">
            <div class="row">
              <div class="col-6 d-flex">
                <p class="etiqueta me-2">Folio:</p>
                <p class="dato">[fFolio]</p>
              </div>
              <div class="col-6 d-flex">
                <p class="etiqueta me-2">Serie:</p>
                <p class="dato">[fSerie]</p>
              </div>
            </div>
          </div>
          <div class="col-8">
            <div class="row">
              <div class="col-8 d-flex">
                <p class="etiqueta me-2">No. Certificado:</p>
                <p class="dato">[fNo_certificado]</p>  
              </div>
              <div class="col-4 d-flex">
                <p class="etiqueta me-2">Versión CFDI:</p>
                <p class="dato">[fVersion]</p>
              </div>
            </div>
          </div>
        </div>
        <div class="espacio-horizontal"></div>
        <div class="row">
          <div class="col-3">
            <!-- <img src="https://via.placeholder.com/150" id="Logo" alt="Logo" class="img-fluid" style="Border: 1px solid black;"/> -->
          </div>
          <div class="col-9 d-flex justify-content-between">
            <div class="col-5">
              <div class="row">
                <div class="col-12 encabezado-resaltado">----- Datos del Emisor-----</div>
              </div>
              <div class="row">
                <div class="col-6 text-end"><p class="etiqueta">Razón social:</p></div>
                <div class="col-6 "><p class="dato">[eRazon_social]</p></div>
              </div>
              <div class="row">
                <div class="col-6 text-end"><p class="etiqueta">RFC:</p></div>
                <div class="col-6"><p class="dato">[eRFC]</p></div>
              </div>
              <div class="row">
                <div class="col-6 text-end"><p class="etiqueta">Domicio Fiscal:</p></div>
                <div class="col-6"><p class="dato">[eDomicilio_fiscal]</p></div>
              </div>
              <div class="row">
                <div class="col-6 text-end"><p class="etiqueta">Fac. Atr. adquiriente:</p></div>
                <div class="col-6"><p class="dato">[eFac_Atr_adquiriente]</p></div>
              </div>
              <div class="row">
                <div class="col-6 text-end"><p class="etiqueta">Lugar de expedición:</p></div>
                <div class="col-6"><p class="dato">[fLugar_expedicion]</p></div>
              </div>
            </div>
            <div class="col-5">
              <div class="row">
                <div class="col-12 encabezado-resaltado">-------- Factura --------</div>
              </div>
              <div class="row">
                <div class="col-6 text-end"><p class="etiqueta">Folio fiscal:</p></div>
                <div class="col-6"><p class="dato">[fFolio_fiscal]</p></div>
              </div>
              <div class="row">
                <div class="col-6 text-end"><p class="etiqueta">Serie CSD del SAT:</p></div>
                <div class="col-6"><p class="dato">[fSerie_CSD_SAT]</p></div>
              </div>
              <div class="row">
                <div class="col-6 text-end"><p class="etiqueta">Tipo de comprobante:</p></div>
                <div class="col-6"><p class="dato">[fTipo_de_comprobante]</p></div>
              </div>
              <div class="row">
                <div class="col-6 text-end"><p class="etiqueta">Fecha Certificación:</p></div>
                <div class="col-6"><p class="dato">[fFecha_certificacion]</p></div>
              </div>
              <div class="row">
                <div class="col-6 text-end"><p class="etiqueta">Fecha emisión:</p></div>
                <div class="col-6"><p class="dato">[fFecha_emision]</p></div>
              </div>
            </div>
          </div>                  
        </div>
        <div class="espacio-horizontal"></div>
        <div class="row">
          <div class="col-6">
            <div class="row">
              <div class="col-12 encabezado-resaltado">-------- Información Global --------</div>
            </div>
            <div class="row">
              <div class="col-4 renglon"><p class="etiqueta">Periodicidad</p></div>
              <div class="col-4 renglon"><p class="etiqueta">Meses</p></div>
              <div class="col-4 renglon"><p class="etiqueta">Año</p></div>
            </div>
            <div class="row">
              <div class="col-4 renglon"><p class="dato" id="periodicidad">[iPeriodicidad]</p></div>
              <div class="col-4 renglon"><p class="dato" id="meses">[iMeses]</p></div>
              <div class="col-4 renglon"><p class="dato" id="ano">[iYear]</p></div>
            </div>
          </div>
        </div>
        <div class="espacio-horizontal"></div>
        <div class="row"> 
          <div class="col-12">
            <div class="row">
              <div class="col-12 encabezado-resaltado">-------- CFDIs Relacionados --------</div>
            </div>
            <div class="row">
              <div class="col-3 renglon"><p class="etiqueta">Tipo de relación</p></div>
              <div class="col-9 renglon"><p class="etiqueta">UUID(s) Relacionados</p></div>
            </div>
            <div class="row">
              <div class="col-3 renglon"><p class="dato" id="tipoRelacion">[cfTipo_relacion]</p></div>
              <div class="col-9 renglon"><p class="dato" id="uuidsRelacionados">[cfUUIDs_relacionados]</p></div>
            </div>
          </div>
        </div>
        <div class="row espacio-horizontal"></div>
        <div class="row">
          <div class="col-12">
            <div class="row">
              <div class="col-12 encabezado-resaltado">-------- Receptor --------</div>
            </div>
            <div class="row">
              <div class="col-2 renglon"><p class="etiqueta">RFC:</p></div>
              <div class="col-2 renglon"><p class="dato" id="rfcR">[rRFC]</p></div>
              <div class="col-2 renglon"><p class="etiqueta">Razón social:</p></div>
              <div class="col-2 renglon"><p class="dato" id="razonsocialR">[rRazon_social]</p></div>
              <div class="col-2 renglon"><p class="etiqueta">Num. Reg. id. Trib.:</p></div>
              <div class="col-2 renglon"><p class="dato" id="numRegIdTribR">[rNum_Reg_id_Trib]</p></div>
            </div>
            <div class="row">
              <div class="col-2 renglon"><p class="etiqueta">Uso de CFDI:</p></div>
              <div class="col-2 renglon"><p class="dato" id="usoCFDIR">[rUso_CFDI]</p></div>
              <div class="col-2 renglon"><p class="etiqueta">Régimen fiscal:</p></div>
              <div class="col-6 renglon"><p class="dato" id="regimenFiscalR">[rRegimen_fiscal]</p></div>
            </div>
            <div class="row">
              <div class="col-2 renglon"><p class="etiqueta">Residencia fiscal:</p></div>
              <div class="col-2 renglon"><p class="dato" id="residenciaFiscalR">[rResidencia_fiscal]</p></div>
              <div class="col-2 renglon"><p class="etiqueta">Domicilio fiscal:</p></div>
              <div class="col-6 renglon"><p class="dato" id="domicilioFiscalR">[rDomicilio_fiscal]</p></div>
            </div>
          </div>
        </div>
        <div class="row espacio-horizontal"></div>
        <div class="row">
          <div class="col-12">
            <div class="row">
              <div class="col-12 encabezado-resaltado">-------- Conceptos --------</div>
            </div>
            <div class="row">
              <div class="col-1 renglon"><p class="etiqueta">Cve prod.</p></div>
              <div class="col-1 renglon"><p class="etiqueta">Num. de id</p></div>
              <div class="col-1 renglon"><p class="etiqueta">Cant.</p></div>
              <div class="col-1 renglon"><p class="etiqueta">Unidad</p></div>
              <div class="col-2 renglon"><p class="etiqueta">Descripción</p></div>
              <div class="col-2 renglon"><p class="etiqueta">Valor unitario</p></div>
              <div class="col-2 renglon"><p class="etiqueta">Objeto impuesto</p></div>
              <div class="col-2 renglon"><p class="etiqueta">Importe</p></div>
            </div>
            <div class="d-none">
              {% for conceptos in CFDI.conceptos %}
            </div>
            <div class="row">
              <div class="col-1 renglon"><p class="dato" id="cveProd">[cCve_prod]</p></div>
              <div class="col-1 renglon"><p class="dato" id="numId">[cNum_id]</p></div>
              <div class="col-1 renglon"><p class="dato" id="cant">[cCantidad]</p></div>
              <div class="col-1 renglon"><p class="dato" id="unidad">[cUnidad]</p></div>
              <div class="col-2 renglon"><p class="dato" id="descripcion">[cDescripcion]</p></div>
              <div class="col-2 renglon"><p class="dato" id="valorUnitario">[cValor_unitario]</p></div>          
              <div class="col-2 renglon"><p class="dato" id="objetoImpuesto">[cObjeto_impuesto]</p></div>
              <div class="col-2 renglon"><p class="dato" id="importe">[cImporte]</p></div>
            </div>
            <div class="d-none">
              {% endfor %}
            </div>
          </div>
        </div>
        <div class="row espacio-horizontal"></div>
        <div class="row d-flex justify-content-between">
          <div class="col-7">
            <div class="row">
              <div class="col-12 renglon d-flex flex-column align-items-center justify-content-end text-center" style="height: 30px; border-top: .5px solid black;"><p class="dato" id="totalConletra">[fTotal_con_letra]</p></div>
            </div>
            <div class="row">
              <div class="col-12 renglon text-center"><p class="etiqueta">Total con letra</p></div>
            </div>
            <div class="row">
              <div class="col-3 renglon"><p class="etiqueta">Método de pago:</p></div>
              <div class="col-3 renglon"><p class="dato" id="metodoPago">[fMetodo_pago]</p></div>
              <div class="col-3 renglon"><p class="etiqueta">Moneda:</p></div>
              <div class="col-3 renglon"><p class="dato" id="moneda">[fMoneda]</p></div>
            </div>
            <div class="row">
              <div class="col-3 renglon"><p class="etiqueta">Forma de pago:</p></div>
              <div class="col-3 renglon"><p class="dato" id="formaPago">[fForma_pago]</p></div>
              <div class="col-3 renglon"><p class="etiqueta">Tipo-cambio:</p></div>
              <div class="col-3 renglon"><p class="dato" id="tipoCambio">[fTipo_cambio]</p></div>
            </div>
            <div class="row">
              <div class="col-3 renglon"><p class="etiqueta">Condición de pago:</p></div>
              <div class="col-3 renglon"><p class="dato" id="condicionPago">[fCondicion_pago]</p></div>
              <div class="col-3 renglon"><p class="etiqueta">Confirmación:</p></div>
              <div class="col-3 renglon"><p class="dato" id="confirmacion">[fConfirmacion]</p></div>
            </div>
          </div>
          
          <div class="col-4">
            <div class="row">
              <div class="col-6 renglon text-end" style="border-top: .5px solid black;"><p class="etiqueta">Subtotal:</p></div>
              <div class="col-6 renglon" style="border-top: .5px solid black;"><p class="dato" id="subtotal">[fSubtotal]</p></div>
            </div>
            <div class="row">
              <div class="col-6 renglon text-end"><p class="etiqueta">Impuestos Equiq.:</p></div>
              <div class="col-6 renglon"><p class="dato" id="impuestoEquiq">[imImpuestos_Equiq]</p></div>
            </div>
            <div class="row">
              <div class="col-6 renglon text-end"><p class="etiqueta">Total Imp. Trasladados:</p></div>
              <div class="col-6 renglon"><p class="dato" id="impLocTrasEquiq">[imTot_imp_Tras]</p></div>
            </div>
            <div class="row">
              <div class="col-6 renglon text-end"><p class="etiqueta">Total Imp. Retenidos:</p></div>
              <div class="col-6 renglon"><p class="dato" id="impLocRetEquiq">[imTot_imp_Ret]</p></div>
            </div>
            <div class="row">
              <div class="col-6 renglon text-end"><p class="etiqueta">Descuento:</p></div>
              <div class="col-6 renglon"><p class="dato" id="descuento">[fDescuento]</p></div>
            </div>
            <div class="row">
              <div class="col-6 renglon text-end"><p class="etiqueta">Total:</p></div>
              <div class="col-6 renglon"><p class="dato" id="total">[fTotal]</p></div>
            </div>
          </div>
  
        </div>
        <div class="row espacio-horizontal"></div>
        <div class="row">
          <div class="col-12">
            <div class="row d-flex justify-content-between">
              <div class="col-3">
                <!-- <img src="https://via.placeholder.com/150" id="QR" alt="Logo" class="img-fluid" style="Border: 1px solid black;"/> -->
              </div>
  
              <div class="col-8">                      
                <div class="row">
                  <div class="col-12 encabezado-resaltado">Cadena original del complemento de certificación del SAT</div>
                </div>
                <div class="row">
                  <div class="col-12"><p class="dato" id="cadenaOrig">[fCertificado_SAT]</p></div>
                </div>
                <div class="row">
                  <div class="col-12 encabezado-resaltado">SELLO DIGITAL DEL SAT</div>
                </div>
                <div class="row">
                  <div class="col-12"><p class="dato" id="selloDigitalSAT">[fSello_SAT]</p></div>
                </div>
                <div class="row">
                  <div class="col-12 encabezado-resaltado">SELLO DIGITAL DEL CONTRIBUYENTE QUE LO EXPIDE</div>
                </div>
                <div class="row">
                  <div class="col-12"><p class="dato" id="selloDigitalContribuyente">[nSello_digital_contribuyente]</p></div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="row espacio-horizontal"></div>
        <div class="row"> 
          <div class="col-12">
  
            <div class="row">
              <div class="col-12 encabezado-resaltado">Nota</div>
            </div>
            <div class="row">
              <div class="col-12"><p class="dato" id="nota">[nNota]</p></div>
            </div>
            <div class="row">
              <div class="col-12 encabezado-resaltado">---------- LEYENDAS FISCALES--------</div>
            </div>
            <div class="row renglon">
              <div class="col-2"><p class="etiqueta">DISPOSICIÓN FISCAL:</p></div>
              <div class="col-3"><p class="dato" id="disposicionFiscal">[nDisposicion_fiscal]</p></div>
              <div class="col-1"><p class="etiqueta">NORMA:</p></div>
              <div class="col-2"><p class="dato" id="norma">[nNorma]</p></div>
              <div class="col-2"><p class="etiqueta">LEYENDA:</p></div>
              <div class="col-2"><p class="dato" id="leyenda">[nLeyenda]</p></div>
            </div>
          </div>
        </div>
      </section>
    `,
  });
    //Agregar un contenedor de la factura Básica
    editor.BlockManager.add('FacturaTabla',{
      label: 'Factura tabla',
      category: 'Facturas',
      attributes: { class: '' },
      content: `
        <style>
          .encabezado-resaltado{
            display: block;
            background-color: #c6ffb4;
            font-weight: bold;
            text-align: center;
            padding: 0px;
            border: 1px solid #dee2e6;
            
          }
  
          .encabezado-tabla{
            background-color: #c6ffb4;          
            text-align: center;
          }
          .etiqueta-encabezado{
            display: block;
            font-family: 'Arial', sans-serif; 
            font-size: 12px; 
            font-weight: bold;
            margin:0%;
            padding:0%;
          }
          .etiqueta{
            display: block;
            font-family: 'Arial', sans-serif; 
            font-size: 11px; 
            font-weight: bold;
            margin:0%;
            padding:0%;
          }
          .dato{
            display: block;
            word-wrap: break-word;     /* Esto permite que el texto largo se ajuste */
            overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
            white-space: normal;   /* Establece que el texto no se ajuste a la línea */
            font-family: 'Arial', sans-serif;
            font-size: 10px; 
            margin:0%;
            padding:0%;
            }
          .renglon {
              border: 1px solid #dee2e6;
          }
          .espacio-horizontal{
            height: 30px;
          }
          .espacio-vertical {
            width: 30px;
          }
          .textox {
            font-family: 'Arial', sans-serif;
            font-size: 11px;
          }
          .table th, .table td {
            padding: 0px;
            height: auto !important;
            vertical-align: top; 
          }
          
        </style>
        <section>
          <div>

              <table>
                <tbody>
                  <tr >
                    <td>
                      <p class="etiqueta me-2">Folio:</p>
                      <p class="dato">[fFolio]</p>
                    </td>
                    <td>
                      <p class="etiqueta me-2">Serie:</p>
                      <p class="dato">[fSerie]</p>
                    </td>
                    <td>
                      <p class="etiqueta me-2">No. Certificado:</p>
                      <p class="dato">[fNo_certificado]</p>  
                    </td>
                    <td>
                      <p class="etiqueta me-2">Versión CFDI:</p>
                      <p class="dato">[fVersion]</p>
                    </td>
                  </tr>
                </tbody>
              </table>
            
          </div>

          <div>
            <div>
              <img src="https://via.placeholder.com/150" id="Logo" alt="Logo" class="img-fluid" style="Border: 1px solid black; width: 147px; height: 110px;"/>
            </div>
            <div>
              <table>
                <thead class="encabezado-tabla">
                  <tr>
                    <th colspan="2">Emisor</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <th ><p class="etiqueta">Razón social: </p></th>
                    <td ><p class="dato">[eRazon_social]</p></td>
                  </tr>
                  <tr>
                    <th ><p class="etiqueta">RFC:</p></th>
                    <td ><p class="dato">[eRFC]</p></td>
                  </tr>
                  <tr>
                    <th ><p class="etiqueta">Domicio Fiscal:</p></th>
                    <td ><p class="dato">[eDomicilio_fiscal]</p></td>
                  </tr>
                  <tr>
                    <th ><p class="etiqueta">Fac. Atr. adquiriente:</p></th>
                    <td ><p class="dato">[eFac_Atr_adquiriente]</p></td>
                  </tr>
                  <tr>
                    <th ><p class="etiqueta">Lugar de expedición:</p></th>
                    <td ><p class="dato">[fLugar_expedicion]</p></td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div>                
              <table>
                <thead class="encabezado-tabla">
                  <tr>
                    <th colspan="2">Factura</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <th><p class="etiqueta">Folio fiscal:</p></th>
                    <td><p class="dato">[fFolio_fiscal]</p></td>
                  </tr>
                  <tr>
                    <th><p class="etiqueta">Serie CSD del SAT:</p></th>
                    <td><p class="dato">[fSerie_CSD_SAT]</p></td>
                  </tr>
                  <tr>
                    <th><p class="etiqueta">Tipo de comprobante:</p></th>
                    <td><p class="dato">[fTipo_de_comprobante]</p></td>
                  </tr>
                  <tr>
                    <th><p class="etiqueta">Fecha Certificación:</p></th>
                    <td><p class="dato">[fFecha_certificacion]</p></td>
                  </tr>
                  <tr>
                    <th><p class="etiqueta">Fecha emisión:</p></th>
                    <td><p class="dato">[fFecha_emision]</p></td>
                  </tr>
                </tbody>
              </table>
                  
            </div>
                              
          </div>
  
          <div>
            <div>
              <table>
                <thead class="encabezado-tabla">
                  <tr>
                    <th colspan="3">Información Global</th>
                  </tr>
                </thead>
                <tbody>
                  <tr >
                    <th><p class="etiqueta">Periodicidad</p></th>
                    <th><p class="etiqueta">Meses</p></th>
                    <th><p class="etiqueta">Año</p></th>
                  </tr>
                  <tr>
                    <td><p class="dato">[iPeriodicidad]</p></td>
                    <td><p class="dato">[iMeses]</p></td>
                    <td><p class="dato">[iYear]</p></td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div>              
              <table>
                <thead class="encabezado-tabla">
                  <tr>
                    <th colspan="2">CFDIs Relacionados</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td><p class="etiqueta">Tipo de relación</p></td>
                    <td><p class="etiqueta">UUID(s) Relacionados</p></td>
                  </tr>
                  <tr>
                    <td><p class="dato">[cfTipo_relacion]</p></td>
                    <td><p class="dato">[cfUUIDs_relacionados]</p></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
  
          <div>
            <table class="table table-sm table-bordered">
              <thead class="encabezado-tabla">
                <tr>
                  <th colspan="6">Receptor</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><p class="etiqueta">RFC:</p></td>
                  <td><p class="dato">[rRFC]</p></td>
                  <td><p class="etiqueta">Domicilio fiscal:</p></td>
                  <td><p class="dato">[rDomicilio_fiscal]</p></td>
                  <td><p class="etiqueta">Num. Reg. id. Trib.:</p></td>
                  <td><p class="dato">[rNum_Reg_id_Trib]</p></td>
                </tr>
                <tr>
                  <td><p class="etiqueta">Uso de CFDI:</p></td>
                  <td><p class="dato">[rUso_CFDI]</p></td>
                  <td><p class="etiqueta">Régimen fiscal:</p></td>
                  <td colspan="3"><p class="dato">[rRegimen_fiscal]</p></td>
                </tr>
                <tr>
                  
                  <td><p class="etiqueta">Razón social:</p></td>
                  <td><p class="dato">[rRazon_social]</p></td>
                  <td><p class="etiqueta">Residencia fiscal:</p></td>
                  <td colspan="3"><p class="dato">[rResidencia_fiscal]</p></td>
                  
                </tr>
              </tbody>
            </table>
          </div>
  
          <div>            
            <table>
              <thead class="encabezado-tabla">
                <tr>
                  <th colspan="8">Conceptos</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <th scope="col"><p class="etiqueta">Cve prod.</p></th>
                  <th scope="col"><p class="etiqueta">Num. de id</p></th>
                  <th scope="col"><p class="etiqueta">Cant.</p></th>
                  <th scope="col"><p class="etiqueta">Unidad</p></th>
                  <th scope="col"><p class="etiqueta">Descripción</p></th>
                  <th scope="col"><p class="etiqueta">Valor unitario</p></th>
                  <th scope="col"><p class="etiqueta">Objeto impuesto</p></th>
                  <th scope="col"><p class="etiqueta">Importe</p></th>
                </tr>
                <tr class="d-none">
                  <td>{% for conceptos in CFDI.conceptos %}</td>
                </tr>
                <tr>
                  <td><p class="dato">[cCve_prod]</p></td>
                  <td><p class="dato">[cNum_id]</p></td>
                  <td><p class="dato">[cCantidad]</p></td>
                  <td><p class="dato">[cUnidad]</p></td>
                  <td><p class="dato">[cDescripcion]</p></td>
                  <td><p class="dato">[cValor_unitario]</p></td>
                  <td><p class="dato">[cObjeto_impuesto]</p></td>
                  <td><p class="dato">[cImporte]</p></td>
                </tr>
                <tr class="d-none">
                  <td>{% endfor %}</td>
                </tr>
              </tbody>
            </table>
            
          </div>
  
          <div>
            <div>
                <img src="https://via.placeholder.com/150" id="QR" alt="Logo" class="img-fluid" style="Border: 1px solid black; width: 147px; height: 110px;"/>
            </div>
            <div>                
              <table>
                <tbody>
                  <tr>
                    <td colspan="4" class="text-center"><p class="dato">[fTotal_con_letra]</p></td>
                  </tr>
                  <tr>
                    <td colspan="4" class="text-center"><p class="etiqueta">Total con letra</p></td>
                  </tr>
                  <tr>
                    <th><p class="etiqueta">Método de pago:</p></th>
                    <td><p class="dato">[fMetodo_pago]</p></td>
                    <th><p class="etiqueta">Moneda:</p></th>
                    <td><p class="dato">[fMoneda]</p></td>
                  </tr>
                  <tr>
                    <th><p class="etiqueta">Forma de pago:</p></th>
                    <td><p class="dato">[fForma_pago]</p></td>
                    <th><p class="etiqueta">Tipo-cambio:</p></th>
                    <td><p class="dato">[fTipo_cambio]</p></td>
                  </tr>
                  <tr>
                    <th><p class="etiqueta">Condición de pago:</p></th>
                    <td colspan="3"><p class="dato">[fCondicion_pago]</p></td>
                  </tr>
                </tbody>
              </table>
            </div>
  
            <div>              
              <table>
                <tbody>
                  <tr>
                    <th><p class="etiqueta">Subtotal:</p></th>
                    <td><p class="dato">[fSubtotal]</p></td>
                  </tr>
                  <tr>
                    <th><p class="etiqueta">Impuestos Equiq.:</p></th>
                    <td><p class="dato">[imImpuestos_Equiq]</p></td>
                  </tr>
                  <tr>
                    <th><p class="etiqueta">Total Imp. Trasladados:</p></th>
                    <td><p class="dato">[imTot_imp_Tras]</p></td>
                  </tr>
                  <tr>
                    <th><p class="etiqueta">Total Imp. Retenidos:</p></th>
                    <td><p class="dato">[imTot_imp_Ret]</p></td>
                  </tr>
                  <tr>
                    <th><p class="etiqueta">Descuento:</p></th>
                    <td><p class="dato">[fDescuento]</p></td>
                  </tr>
                  <tr>
                    <th><p class="etiqueta">Total:</p></th>
                    <td><p class="dato">[fTotal]</p></td>
                  </tr>
              </table>
            </div>
          </div>
  
          
  
          <div>
            
            <table>
              <tr class="encabezado-tabla">
                <th  colspan="6">Notas</th>
              </tr>
              <tr>
                <td colspan="6"><p class="dato">[nNota]</p></td>
              </tr>
              <tr class="encabezado-tabla">
                <th colspan="6">LEYENDAS FISCALES</th>
              </tr>
              <tr>
                <th><p class="etiqueta">DISPOSICIÓN FISCAL:</p></th>
                <td><p class="dato">[nDisposicion_fiscal]</p></td>
                <th><p class="etiqueta">NORMA:</p></th>
                <td><p class="dato">[nNorma]</p></td>
                <th><p class="etiqueta">LEYENDA:</p></th>
                <td><p class="dato">[nLeyenda]</p></td>
              </tr>
            </table>
          </div>
                
  
          <div>
            <div>
              <div class="encabezado-resaltado">Cadena original del complemento de certificación del SAT</div>
            </div>
            <div>
              <div><p class="dato renglon">[fCertificado_SAT]</p></div>
            </div>
            <div>
              <div class="encabezado-resaltado">SELLO DIGITAL DEL SAT</div>
            </div>
            <div>
              <div><p class="dato renglon">[fSello_SAT]</p></div>
            </div>
            <div>
              <div class="encabezado-resaltado">SELLO DIGITAL DEL CONTRIBUYENTE QUE LO EXPIDE</div>
            </div>
            <div>
              <div><p class="dato renglon">[nSello_digital_contribuyente]</p></div>
            </div>
          </div>
          
        </section>
      `,
    });  
  //Agregar un contenedor basico
  editor.BlockManager.add('contenedor-basico',{
    label: 'Contener básico',
    category: 'Tablas',
    attributes: { class: '' },
    content: `
        <style>
          section{
            padding: 15px 30px 15px 30px;
          }
          .encabezado{
            height: 30px;
          }
          .encabezado-resaltado{
            background-color: #92D46C;
            Border: 1px solid black;
            text-align: center;
          }
          .etiqueta{
            font-family: 'Arial', sans-serif; 
            font-size: 11px; 
            font-weight: bold;
            margin:0%;
            padding:0%;
          }
          .dato{
            font-family: 'Arial', sans-serif; 
            font-size: 10px; 
            margin:0%;
            padding:0%;
          }
          .renglon{
            Border: 1px solid black;
          }
          .espacio-horizontal{
            height: 30px;
          }
          .espacio-vertical {
            width: 30px;
          }
          .col1, .col2,.col3, .col4,
          .col5,.col6, .col7, .col8,
          .col9,.col10, .col11, .col12{
            Border: 1px solid black;
          }
          .textox {
            font-family: 'Arial', sans-serif;
            font-size: 11px;
          }
          
        </style>
        <section>
        <div class="row">
          <div class=".col-1 col1"><p class="textox">columna 1</p></div>
          <div class=".col-1 col1"><p class="textox">columna 1</p></div>
          <div class=".col-1 col1"><p class="textox">columna 1</p></div>
          <div class=".col-1 col1"><p class="textox">columna 1</p></div>
          <div class=".col-2 col2"><p class="textox">columna 2</p></div>
          <div class=".col-2 col2"><p class="textox">columna 2</p></div>
          <div class=".col-2 col2"><p class="textox">columna 2</p></div>
          <div class=".col-2 col2"><p class="textox">columna 2</p></div>
        </div>
        <div class="row">
          <div class=".col-12 espacio-horizontal"></div>
        </div>
        <div class="row">
          <div class=".col-4 col4">
          <img src="https://via.placeholder.com/150" id="imagen" alt="Logo" style="Border: 1px solid black;"/>
          </div>
          <div class=".col-4 col4">
            <div class="row">
                    <div class="col-12 encabezado-resaltado">----- Datos del Emisor-----</div>
            </div>
          </div>
          <div class=".col-4 col4">
            <div class="row">
                    <div class="col-12 encabezado-resaltado">----- Datos de la factura-----</div>
            </div>
          </div>
        </div>
        
        </setion>
    `,
  });
  //Agregar una fila de 1 y 11 columnas
  editor.BlockManager.add('Fila1', {
    label: 'Fila con columnas de 1-11',
    category: 'Tablas',
    attributes: { class: '' },
    content: `
      <style>
      
      </style>
      <div class="row">
          <div class=".col-1 col1"><p class="textox">columna 1</p></div>
          <div class=".col-11 col11"><p class="textox">columna 11</p></div>
      </div>
              `,
  });
  //Agregar una fila de 2 y 11 columnas
  editor.BlockManager.add('Fila2', {
    label: 'Fila con columnas de 2-10',
    category: 'Tablas',
    attributes: { class: '' },
    content: `
      <style>
      
      </style>
      <div class="row">
          <div class=".col-2 col2"><p class="textox">columna 2</p></div>
          <div class=".col-10 col10"><p class="textox">columna 10</p></div>
      </div>
              `,
  });
  //Agregar una fila de 3 y 9 columnas
  editor.BlockManager.add('Fila3', {
    label: 'Fila con columnas de 3-9',
    category: 'Tablas',
    attributes: { class: '' },
    content: `
      <style>
      
      </style>
      <div class="row">
          <div class=".col-3 col3"><p class="textox">columna 3</p></div>
          <div class=".col-9 col9"><p class="textox">columna 9</p></div>
      </div>
              `,
  });
  //Agregar una fila de 4 y 8 columnas
  editor.BlockManager.add('Fila4', {
    label: 'Fila con columnas de 4-8',
    category: 'Tablas',
    attributes: { class: '' },
    content: `
      <style>
      
      </style>
      <div class="row">
          <div class=".col-4 col4"><p class="textox">columna 4</p></div>
          <div class=".col-8 col8"><p class="textox">columna 8</p></div>
      </div>
              `,
  });
  //Agregar una fila de 5 y 7 columnas
  editor.BlockManager.add('Fila5', {
    label: 'Fila con columnas de 5-7',
    category: 'Tablas',
    attributes: { class: '' },
    content: `
      <style>
      
      </style>
      <div class="row">
          <div class=".col-5 col5"><p class="textox">columna 5</p></div>
          <div class=".col-7 col7"><p class="textox">columna 7</p></div>
      </div>
              `,
  });
  //Agregar una fila de 6 y 6 columnas
  editor.BlockManager.add('Fila6', {
    label: 'Fila con columnas de 6-6',
    category: 'Tablas',
    attributes: { class: '' },
    content: `
      <style>
      
      </style>
      <div class="row">
          <div class=".col-6 col6"><p class="textox">columna 6</p></div>
          <div class=".col-6 col6"><p class="textox">columna 6</p></div>
      </div>
              `,
  });
  //Agregar una fila de 12 columnas
  editor.BlockManager.add('Fila7', {
    label: 'Fila con columna de 12',
    category: 'Tablas',
    attributes: { class: '' },
    content: `
      <style>
      
      </style>
      <div class="row">
          <div class=".col-12 col12"><p class="textox">columna 12</p></div>
      </div>
              `,
  });
  //columna 1
  editor.BlockManager.add('columna1', {
    label: 'Columna T1',
    category: 'Tablas',
    attributes: { class: '' },
    content: `
      <style>
      
      </style>
      <div class=".col-1 col1"><p class="textox">columna 1</p></div>
              `,
  });
  //Columna 2
  editor.BlockManager.add('columna2', {
    label: 'Columna T2',
    category: 'Tablas',
    attributes: { class: '' },
    content: `
      <style>
      
      </style>
      <div class=".col-2 col2"><p class="textox">columna 2</p></div>
              `,
  });
  //Columna 3
  editor.BlockManager.add('columna3', {
    label: 'Columna T3',
    category: 'Tablas',
    attributes: { class: '' },
    content: `
      <style>
      
      </style>
      <div class=".col-3 col3"><p class="textox">columna 3</p></div>
              `,
  });
  //Columna 4
  editor.BlockManager.add('columna4', {
    label: 'Columna T4',
    category: 'Tablas',
    attributes: { class: '' },
    content: `
      <style>
      
      </style>
      <div class=".col-4 col4"><p class="textox">columna 4</p></div>
              `,
  });
  // Columna 5
  editor.BlockManager.add('columna5', {
    label: 'Columna T5',
    category: 'Tablas',
    attributes: { class: '' },
    content: `
      <style>
      
      </style>
      <div class=".col-5 col5"><p class="textox">columna 5</p></div>
              `,
  });
  //columna 6
  editor.BlockManager.add('columna6', {
    label: 'Columna T6',
    category: 'Tablas',
    attributes: { class: '' },
    content: `
      <style>
      
      </style>
      <div class=".col-6 col6"><p class="textox">columna 6</p></div>
              `,
  });
  //columna 7
  editor.BlockManager.add('columna7', {
    label: 'Columna T7',
    category: 'Tablas',
    attributes: { class: '' },
    content: `
      <style>
      
      </style>
      <div class=".col-7 col7"><p class="textox">columna 7</p></div>
              `,
  });
  //columna 8
  editor.BlockManager.add('columna8', {
    label: 'Columna T8',
    category: 'Tablas',
    attributes: { class: '' },
    content: `
      <style>
      
      </style>
      <div class=".col-8 col8"><p class="textox">columna 8</p></div>
              `,
  });
  //columna 9
  editor.BlockManager.add('columna9', {
    label: 'Columna T9',
    category: 'Tablas',
    attributes: { class: '' },
    content: `
      <style>
      
      </style>
      <div class=".col-9 col9"><p class="textox">columna 9</p></div>
              `,
  });
  //columna 10
  editor.BlockManager.add('columna10', {
    label: 'Columna T10',
    category: 'Tablas',
    attributes: { class: '' },
    content: `
      <style>
      
      </style>
      <div class=".col-10 col10"><p class="textox">columna 10</p></div>
              `,
  });
  //columna 11
  editor.BlockManager.add('columna11', {
    label: 'Columna T11',
    category: 'Tablas',
    attributes: { class: '' },
    content: `
      <style>
      
      </style>
      <div class=".col-11 col11"><p class="textox">columna 11</p></div>
              `,
  });
  //Columna 12
  editor.BlockManager.add('columna12', {
    label: 'Columna T12',
    category: 'Tablas',
    attributes: { class: '' },
    content: `
      <style>
      
      </style>
      <div class=".col-12 col12"><p class="textox">columna 12</p></div>
              `,
  });
  //######################### APARTADO DE COMPONENTES###################################
  //DATOS DEL ENCABEZADO PRINCIPAL
  editor.BlockManager.add('Encabezado', {
    label: 'Encabezado',
    category: 'Comp. Factura Básica',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        display: block;
        background-color: #c6ffb4;
        font-weight: bold;
        text-align: center;
        padding: 0px;
        border: 1px solid #dee2e6;
        
      }
      .encabezado-tabla{
          background-color: #c6ffb4;          
          text-align: center;
      }
      .etiqueta-encabezado{
          display: block;
          font-family: 'Arial', sans-serif; 
          font-size: 12px; 
          font-weight: bold;
          margin:0%;
          padding:0%;
        }
        .etiqueta{
          display: block;
          font-family: 'Arial', sans-serif; 
          font-size: 11px; 
          font-weight: bold;
          margin:0%;
          padding:0%;
        }
        .dato{
          display: block;
          word-wrap: break-word;     /* Esto permite que el texto largo se ajuste */
          overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
          white-space: normal;   /* Establece que el texto no se ajuste a la línea */
          font-family: 'Arial', sans-serif;
          font-size: 10px; 
          margin:0%;
          padding:0%;
        }
        .textox {
          font-family: 'Arial', sans-serif;
          font-size: 11px;
        }
        .table th, .table td {
          padding: 0px;
          height: auto !important;
          vertical-align: top; 
        }
      
    </style>
    <div class="row">
      <div class="col-12">
        <table class="table table-sm ">
          <tbody>
            <tr class="d-flex">
              <td class="col-2 d-flex align-items-center">
                <p class="etiqueta me-2">Folio:</p>
                <p class="dato">[fFolio]</p>
              </td>
              <td class="col-2 d-flex align-items-center">
                <p class="etiqueta me-2">Serie:</p>
                <p class="dato">[fSerie]</p>
              </td>
              <td class="col-5 d-flex align-items-center">
                <p class="etiqueta me-2">No. Certificado:</p>
                <p class="dato">[fNo_certificado]</p>  
              </td>
              <td class="col-3 d-flex align-items-center">
                <p class="etiqueta me-2">Versión CFDI:</p>
                <p class="dato">[fVersion]</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    `,
  });
  //DATOS DEL EMISOR
  editor.BlockManager.add('Emisor', {
    label: 'Datos del Emisor',
    category: 'Comp. Factura Básica',
    attributes: { class: '' },
    content: `
      <style>
        .encabezado-resaltado{
          display: block;
          background-color: #c6ffb4;
          font-weight: bold;
          text-align: center;
          padding: 0px;
          border: 1px solid #dee2e6;
          
        }
        .encabezado-tabla{
            background-color: #c6ffb4;          
            text-align: center;
        }
        .etiqueta-encabezado{
          display: block;
          font-family: 'Arial', sans-serif; 
          font-size: 12px; 
          font-weight: bold;
          margin:0%;
          padding:0%;
        }
        .etiqueta{
          display: block;
          font-family: 'Arial', sans-serif; 
          font-size: 11px; 
          font-weight: bold;
          margin:0%;
          padding:0%;
        }
        .dato{
          display: block;
          word-wrap: break-word;     /* Esto permite que el texto largo se ajuste */
          overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
          white-space: normal;   /* Establece que el texto no se ajuste a la línea */
          font-family: 'Arial', sans-serif;
          font-size: 10px; 
          margin:0%;
          padding:0%;
        }
        .textox {
          font-family: 'Arial', sans-serif;
          font-size: 11px;
        }
        .table th, .table td {
          padding: 0px;
          height: auto !important;
          vertical-align: top; 
        }
                
      </style>
      <div class="row">
        <div class="col-2">
          <img src="https://via.placeholder.com/150" id="Logo" alt="Logo" class="img-fluid" style="Border: 1px solid black; width: 147px; height: 110px;"/>
        </div>
        <div class="col-9">
          <table class="table table-sm">
            <thead class="encabezado-tabla">
              <tr>
                <th colspan="2">Emisor</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <th class="col-4"><p class="etiqueta">Razón social: </p></th>
                <td ><p class="dato">[eRazon_social]</p></td>
              </tr>
              <tr>
                <th ><p class="etiqueta">RFC:</p></th>
                <td ><p class="dato">[eRFC]</p></td>
              </tr>
              <tr>
                <th ><p class="etiqueta">Domicio Fiscal:</p></th>
                <td ><p class="dato">[eDomicilio_fiscal]</p></td>
              </tr>
              <tr>
                <th ><p class="etiqueta">Fac. Atr. adquiriente:</p></th>
                <td ><p class="dato">[eFac_Atr_adquiriente]</p></td>
              </tr>
              <tr>
                <th ><p class="etiqueta">Lugar de expedición:</p></th>
                <td ><p class="dato">[fLugar_expedicion]</p></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>`,
  });
  //DATOS SOBRE EL FACTURA
  editor.BlockManager.add('factura', {
    label: 'Datos sobre el factura',
    category: 'Comp. Factura Básica',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        display: block;
        background-color: #c6ffb4;
        font-weight: bold;
        text-align: center;
        padding: 0px;
        border: 1px solid #dee2e6;
        
      }
      .encabezado-tabla{
          background-color: #c6ffb4;          
          text-align: center;
      }
      .etiqueta-encabezado{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 12px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .etiqueta{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        display: block;
        word-wrap: break-word;     /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        white-space: normal;   /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        vertical-align: top; 
      }
    </style>
    <div class="row">          
      <table class="table table-sm table-bordered">
        <thead class="encabezado-tabla">
          <tr>
            <th colspan="2">Factura</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <th><p class="etiqueta">Folio fiscal:</p></th>
            <td><p class="dato">[fFolio_fiscal]</p></td>
          </tr>
          <tr>
            <th><p class="etiqueta">Serie CSD del SAT:</p></th>
            <td><p class="dato">[fSerie_CSD_SAT]</p></td>
          </tr>
          <tr>
            <th><p class="etiqueta">Tipo de comprobante:</p></th>
            <td><p class="dato">[fTipo_de_comprobante]</p></td>
          </tr>
          <tr>
            <th><p class="etiqueta">Fecha Certificación:</p></th>
            <td><p class="dato">[fFecha_certificacion]</p></td>
          </tr>
          <tr>
            <th><p class="etiqueta">Fecha emisión:</p></th>
            <td><p class="dato">[fFecha_emision]</p></td>
          </tr>
        </tbody>
      </table>
  </div>`,
  });
   //DATOS SOBRE LA INFORMACION GLOBAL  
  editor.BlockManager.add('infGlobal', {
    label: 'Información Global',
    category: 'Comp. Factura Básica',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        display: block;
        background-color: #c6ffb4;
        font-weight: bold;
        text-align: center;
        padding: 0px;
        border: 1px solid #dee2e6;
        
      }
      .encabezado-tabla{
          background-color: #c6ffb4;          
          text-align: center;
      }
      .etiqueta-encabezado{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 12px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .etiqueta{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        display: block;
        word-wrap: break-word;     /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        white-space: normal;   /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        vertical-align: top; 
      }  
    </style>  
    <div class="row">
      <table class="table table-sm table-bordered text-center">
        <thead class="encabezado-tabla">
          <tr>
            <th colspan="3">Información Global</th>
          </tr>
        </thead>
        <tbody>
          <tr >
            <th><p class="etiqueta">Periodicidad</p></th>
            <th><p class="etiqueta">Meses</p></th>
            <th><p class="etiqueta">Año</p></th>
          </tr>
          <tr>
            <td><p class="dato">[iPeriodicidad]</p></td>
            <td><p class="dato">[iMeses]</p></td>
            <td><p class="dato">[iYear]</p></td>
          </tr>
        </tbody>
      </table>
    </div>`,
  });
  //DATOS SOBRE LOS CFDI RELACIONADOS 
  editor.BlockManager.add('CFDIsRelacionados', {
    label: 'CFDIs Relacionados',
    category: 'Comp. Factura Básica',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        display: block;
        background-color: #c6ffb4;
        font-weight: bold;
        text-align: center;
        padding: 0px;
        border: 1px solid #dee2e6;
        
      }
      .encabezado-tabla{
          background-color: #c6ffb4;          
          text-align: center;
      }
      .etiqueta-encabezado{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 12px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .etiqueta{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        display: block;
        word-wrap: break-word;     /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        white-space: normal;   /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        vertical-align: top; 
      }
                
    </style>
    <div class="row"> 
      <table class="table table-sm table-bordered">
        <thead class="encabezado-tabla">
          <tr>
            <th colspan="2">CFDIs Relacionados</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td class="col-3"><p class="etiqueta">Tipo de relación</p></td>
            <td><p class="etiqueta">UUID(s) Relacionados</p></td>
          </tr>
          <tr>
            <td ><p class="dato">[cfTipo_relacion]</p></td>
            <td><p class="dato">[cfUUIDs_relacionados]</p></td>
          </tr>
        </tbody>
      </table>
    </div>
    `,
  });
  //DATOS SOBRE EL RECEPTOR 
  editor.BlockManager.add('receptor', {
    label: 'Receptor',
    category: 'Comp. Factura Básica',
    attributes: { class: '' },
    content: `
    <style>
    .encabezado-resaltado{
        display: block;
        background-color: #c6ffb4;
        font-weight: bold;
        text-align: center;
        padding: 0px;
        border: 1px solid #dee2e6;
        
      }
      .encabezado-tabla{
          background-color: #c6ffb4;          
          text-align: center;
      }
      .etiqueta-encabezado{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 12px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .etiqueta{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        display: block;
        word-wrap: break-word;     /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        white-space: normal;   /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        vertical-align: top; 
      }
      
    </style>
    <div class="row">
      <div class="col-12">
        <table class="table table-sm table-bordered">
          <thead class="encabezado-tabla">
            <tr>
              <th colspan="6">Receptor</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td class="col-1"><p class="etiqueta">RFC:</p></td>
              <td><p class="dato">[rRFC]</p></td>
              <td><p class="etiqueta">Domicilio fiscal:</p></td>
              <td><p class="dato">[rDomicilio_fiscal]</p></td>
              <td><p class="etiqueta">Num. Reg. id. Trib.:</p></td>
              <td><p class="dato">[rNum_Reg_id_Trib]</p></td>
            </tr>
            <tr>
              <td><p class="etiqueta">Uso de CFDI:</p></td>
              <td><p class="dato">[rUso_CFDI]</p></td>
              <td><p class="etiqueta">Régimen fiscal:</p></td>
              <td colspan="3"><p class="dato">[rRegimen_fiscal]</p></td>
            </tr>
            <tr>
              
              <td><p class="etiqueta">Razón social:</p></td>
              <td><p class="dato">[rRazon_social]</p></td>
              <td><p class="etiqueta">Residencia fiscal:</p></td>
              <td colspan="3"><p class="dato">[rResidencia_fiscal]</p></td>
              
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    `,
  });
  //DATOS SOBRE LOS CONCEPTOS 
  editor.BlockManager.add('conceptos', {
    label: 'Conceptos',
    category: 'Comp. Factura Básica',
    attributes: { class: '' },
    content: `
  <style>
    .encabezado-resaltado{
      display: block;
      background-color: #c6ffb4;
      font-weight: bold;
      text-align: center;
      padding: 0px;
      border: 1px solid #dee2e6;
      
    }
    .encabezado-tabla{
        background-color: #c6ffb4;          
        text-align: center;
    }
    .etiqueta-encabezado{
      display: block;
      font-family: 'Arial', sans-serif; 
      font-size: 12px; 
      font-weight: bold;
      margin:0%;
      padding:0%;
    }
    .etiqueta{
      display: block;
      font-family: 'Arial', sans-serif; 
      font-size: 11px; 
      font-weight: bold;
      margin:0%;
      padding:0%;
    }
    .dato{
      display: block;
      word-wrap: break-word;     /* Esto permite que el texto largo se ajuste */
      overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
      white-space: normal;   /* Establece que el texto no se ajuste a la línea */
      font-family: 'Arial', sans-serif;
      font-size: 10px; 
      margin:0%;
      padding:0%;
    }
    .textox {
      font-family: 'Arial', sans-serif;
      font-size: 11px;
    }
    .table th, .table td {
      padding: 0px;
      height: auto !important;
      vertical-align: top; 
    }    
  </style>
  <div class="row">
    <div class="col-12">
      <table class="table table-sm table-bordered">
        <thead class="encabezado-tabla">
          <tr>
            <th colspan="8">Conceptos</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <th scope="col"><p class="etiqueta">Cve prod.</p></th>
            <th scope="col"><p class="etiqueta">Num. de id</p></th>
            <th scope="col"><p class="etiqueta">Cant.</p></th>
            <th scope="col"><p class="etiqueta">Unidad</p></th>
            <th scope="col"><p class="etiqueta">Descripción</p></th>
            <th scope="col"><p class="etiqueta">Valor unitario</p></th>
            <th scope="col"><p class="etiqueta">Objeto impuesto</p></th>
            <th scope="col"><p class="etiqueta">Importe</p></th>
          </tr>
          <tr class="d-none">
            <td>{% for conceptos in CFDI.conceptos %}</td>
          </tr>
          <tr>
            <td><p class="dato">[cCve_prod]</p></td>
            <td><p class="dato">[cNum_id]</p></td>
            <td><p class="dato">[cCantidad]</p></td>
            <td><p class="dato">[cUnidad]</p></td>
            <td><p class="dato">[cDescripcion]</p></td>
            <td><p class="dato">[cValor_unitario]</p></td>
            <td><p class="dato">[cObjeto_impuesto]</p></td>
            <td><p class="dato">[cImporte]</p></td>
          </tr>
          <tr class="d-none">
            <td>{% endfor %}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
    `,
  });//DATOS SOBRE EL METODO DE PAGO 
  editor.BlockManager.add('FormaPago', {
    label: 'Forma de pago y QR',
    category: 'Comp. Factura Básica',
    attributes: { class: '' },
    content: `
  <style>
    .encabezado-resaltado{
      display: block;
      background-color: #c6ffb4;
      font-weight: bold;
      text-align: center;
      padding: 0px;
      border: 1px solid #dee2e6;
      
    }
    .encabezado-tabla{
      background-color: #c6ffb4;          
      text-align: center;
    }
    .etiqueta-encabezado{
      display: block;
      font-family: 'Arial', sans-serif; 
      font-size: 12px; 
      font-weight: bold;
      margin:0%;
      padding:0%;
    }
    .etiqueta{
      display: block;
      font-family: 'Arial', sans-serif; 
      font-size: 11px; 
      font-weight: bold;
      margin:0%;
      padding:0%;
    }
    .dato{
      display: block;
      word-wrap: break-word;     /* Esto permite que el texto largo se ajuste */
      overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
      white-space: normal;   /* Establece que el texto no se ajuste a la línea */
      font-family: 'Arial', sans-serif;
      font-size: 10px; 
      margin:0%;
      padding:0%;
    }
    .textox {
      font-family: 'Arial', sans-serif;
      font-size: 11px;
    }
    .table th, .table td {
      padding: 0px;
      height: auto !important;
      vertical-align: top; 
    }
      
  </style>
  <div class="row">
    <div class="col-2">
        <img src="https://via.placeholder.com/150" id="QR" alt="Logo" class="img-fluid" style="Border: 1px solid black; width: 147px; height: 110px;"/>
    </div>
    <div class="col-7">
      <div class="row">
        
          <table class="table table-sm table-bordered">
            <tbody>
              <tr>
                <td colspan="4" class="text-center"><p class="dato">[fTotal_con_letra]</p></td>
              </tr>
              <tr>
                <td colspan="4" class="text-center"><p class="etiqueta">Total con letra</p></td>
              </tr>
              <tr>
                <th class="col-3"><p class="etiqueta">Método de pago:</p></th>
                <td><p class="dato">[fMetodo_pago]</p></td>
                <th class="col-2"><p class="etiqueta">Moneda:</p></th>
                <td><p class="dato">[fMoneda]</p></td>
              </tr>
              <tr>
                <th><p class="etiqueta">Forma de pago:</p></th>
                <td><p class="dato">[fForma_pago]</p></td>
                <th><p class="etiqueta">Tipo-cambio:</p></th>
                <td><p class="dato">[fTipo_cambio]</p></td>
              </tr>
              <tr>
                <th><p class="etiqueta">Condición de pago:</p></th>
                <td colspan="3"><p class="dato">[fCondicion_pago]</p></td>
              </tr>
            </tbody>
          </table>
        
      </div>
    </div>
  </div>
    `,
  });
  //DATOS SOBRE LOS IMPUESTOS 
  editor.BlockManager.add('impuestos', {
    label: 'Impuestos',
    category: 'Comp. Factura Básica',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        display: block;
        background-color: #c6ffb4;
        font-weight: bold;
        text-align: center;
        padding: 0px;
        border: 1px solid #dee2e6;
        
      }
      .encabezado-tabla{
        background-color: #c6ffb4;          
        text-align: center;
      }
      .etiqueta-encabezado{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 12px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .etiqueta{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        display: block;
        word-wrap: break-word;     /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        white-space: normal;   /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        vertical-align: top; 
      }    
    </style>
    <div class="row">
      <div class="col-12">
        <table class="table table-sm table-bordered">
          <tbody>
            <tr>
              <th><p class="etiqueta">Subtotal:</p></th>
              <td><p class="dato">[fSubtotal]</p></td>
            </tr>
            <tr>
              <th><p class="etiqueta">Impuestos Equiq.:</p></th>
              <td><p class="dato">[imImpuestos_Equiq]</p></td>
            </tr>
            <tr>
              <th><p class="etiqueta">Total Imp. TrasladadosImp. Loc. Tras. Equiq.:</p></th>
              <td><p class="dato">[imTot_imp_Tras]</p></td>
            </tr>
            <tr>
              <th><p class="etiqueta">Total Imp. Trasladados:</p></th>
              <td><p class="dato">[imTot_imp_Ret]</p></td>
            </tr>
            <tr>
              <th><p class="etiqueta">Descuento:</p></th>
              <td><p class="dato">[fDescuento]</p></td>
            </tr>
            <tr>
              <th><p class="etiqueta">Total:</p></th>
              <td><p class="dato">[fTotal]</p></td>
            </tr>
        </table>
      </div>  
    </div>
    
    `,
  });
  //DATOS SOBRE LOS SELLOS   
  editor.BlockManager.add('sellos', {
    label: 'Sellos',
    category: 'Comp. Factura Básica',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        display: block;
        background-color: #c6ffb4;
        font-weight: bold;
        text-align: center;
        padding: 0px;
        border: 1px solid #dee2e6;
        
      }
      .encabezado-tabla{
          background-color: #c6ffb4;          
          text-align: center;
      }
      .etiqueta-encabezado{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 12px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .etiqueta{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        display: block;
        word-wrap: break-word;     /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        white-space: normal;   /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        vertical-align: top; 
      }
    </style>
    <div class="row">
      <div class="col-12">
        <div class="row">
          <div class="col-12 encabezado-resaltado">Cadena original del complemento de certificación del SAT</div>
        </div>
        <div class="row">
          <div class="col-12 "><p class="dato renglon">[fCertificado_SAT]</p></div>
        </div>
        <div class="row">
          <div class="col-12 encabezado-resaltado">SELLO DIGITAL DEL SAT</div>
        </div>
        <div class="row">
          <div class="col-12 "><p class="dato renglon">[fSello_SAT]</p></div>
        </div>
        <div class="row">
          <div class="col-12 encabezado-resaltado">SELLO DIGITAL DEL CONTRIBUYENTE QUE LO EXPIDE</div>
        </div>
        <div class="row">
          <div class="col-12 "><p class="dato renglon">[nSello_digital_contribuyente]</p></div>
        </div>
      </div>
    </div>
    `,
  });
  //DATOS SOBRE LAS NOTAS Y LEYENDAS FISCALES
  editor.BlockManager.add('notas', {
    label: 'Notas y leyendas',
    category: 'Comp. Factura Básica',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        display: block;
        background-color: #c6ffb4;
        font-weight: bold;
        text-align: center;
        padding: 0px;
        border: 1px solid #dee2e6;
        
      }
      .encabezado-tabla{
          background-color: #c6ffb4;          
          text-align: center;
      }
      .etiqueta-encabezado{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 12px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .etiqueta{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        display: block;
        word-wrap: break-word;     /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        white-space: normal;   /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        vertical-align: top; 
      }
    </style>
    <div class="row"> 
      <div class="col-12">
        <table class="table table-sm table-bordered">
          <tr class="encabezado-tabla">
            <th  colspan="6">Notas</th>
          </tr>
          <tr>
            <td colspan="6"><p class="dato">[nNota]</p></td>
          </tr>
          <tr class="encabezado-tabla">
            <th colspan="6">LEYENDAS FISCALES</th>
          </tr>
          <tr>
            <th class="col-2"><p class="etiqueta">DISPOSICIÓN FISCAL:</p></th>
            <td><p class="dato">[nDisposicion_fiscal]</p></td>
            <th class="col-1"><p class="etiqueta">NORMA:</p></th>
            <td><p class="dato">[nNorma]</p></td>
            <th class="col-1"><p class="etiqueta">LEYENDA:</p></th>
            <td><p class="dato">[nLeyenda]</p></td>
          </tr>
        </table>
      </div>
    </div>
    `,
  });
  //################## Componentes Factura Nomina #####################
  //Encabezado de la factura nomina
  editor.BlockManager.add('encabezado', {
    label: 'Factura nomina, emisor y entidad SNCF',
    category: 'Comp. Factura Nomina',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        display: block;
        background-color: #b3eeda;
        font-weight: bold;
        text-align: center;
        padding: 0px;
        border: 1px solid #dee2e6;
        
      }

      .encabezado-tabla{
        background-color: #b3eeda;          
        text-align: center;
      }
      .etiqueta-encabezado{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 12px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .etiqueta{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        display: block;
        word-wrap: break-word;     /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        white-space: normal;   /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
        }
      .renglon {
          border: 1px solid #dee2e6;
      }
      .espacio-horizontal{
        height: 30px;
      }
      .espacio-vertical {
        width: 30px;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        
        vertical-align: top; 
      }
    </style>
    <div class="row">
      <div class="col-12">
        <table class="table table-sm ">
          <tbody>
            <tr class="d-flex">
              <td class="col-2 d-flex align-items-center">
                <p class="etiqueta me-2">Folio:</p>
                <p class="dato">[fFolio]</p>
              </td>
              <td class="col-2 d-flex align-items-center">
                <p class="etiqueta me-2">Serie:</p>
                <p class="dato">[fSerie]</p>
              </td>
              <td class="col-5 d-flex align-items-center">
                <p class="etiqueta me-2">No. Certificado:</p>
                <p class="dato">[fNo_certificado]</p>  
              </td>
              <td class="col-3 d-flex align-items-center">
                <p class="etiqueta me-2">Versión CFDI:</p>
                <p class="dato">[fVersion]</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div class="row">
      <div class="col-2">
        <img src="https://via.placeholder.com/150" id="Logo" alt="Logo" class="img-fluid" style="Border: 1px solid black; width: 147px; height: 110px;"/>
      </div>
      <div class="col-10 d-flex justify-content-between">
        <div class="col-5">
          <div class="row">
            <table class="table table-sm">
              <thead class="encabezado-tabla">
                <tr>
                  <th colspan="2">Emisor</th>
                </tr>
              </thead>
              <tbody>
                <tr >
                  <th><p class="etiqueta">Razón social:</p></th>
                  <td><p class="dato">[eRazon_social]</p></td>
                </tr>
                <tr>
                  <th><p class="etiqueta">RFC:</p></th>
                  <td><p class="dato">[eRFC]</p></td>
                </tr>
                <tr>
                  <th><p class="etiqueta">Curp:</p></th>
                  <td><p class="dato">[eCurp]</p></td>
                </tr>
                <tr>
                  <th><p class="etiqueta">Régimen fiscal:</p></th>
                  <td><p class="dato">[eRegimen_fiscal]</p></td>
                </tr>
                <tr>
                  <th><p class="etiqueta">Domicio Fiscal:</p></th>
                  <td><p class="dato">[eDomicilio_fiscal]</p></td>
                </tr>
                <tr>
                  <th><p class="etiqueta">Fac. Atr. adquiriente:</p></th>
                  <td><p class="dato">[eFac_Atr_adquiriente]</p></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="col-5">
          <div class="row">
            <table class="table table-sm table-bordered">
              <thead class="encabezado-tabla">
                <tr>
                  <th colspan="2">Factura</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <th><p class="etiqueta">Folio fiscal:</p></th>
                  <td><p class="dato">[fFolio_fiscal]</p></td>
                </tr>
                <tr>
                  <th><p class="etiqueta">Serie CSD del SAT:</p></th>
                  <td><p class="dato">[fSerie_CSD_SAT]</p></td>
                </tr>
                <tr>
                  <th><p class="etiqueta">Tipo de comprobante:</p></td>
                  <td><p class="dato">[fTipo_de_comprobante]</p></th>
                </tr>
                <tr>
                  <th><p class="etiqueta">Fecha Certificación:</p></th>
                  <td><p class="dato">[fFecha_certificacion]</p></td>
                </tr>
                <tr>
                  <th><p class="etiqueta">Fecha emisión:</p></th>
                  <td><p class="dato">[fFecha_emision]</p></td>
                </tr>
                <tr>
                  <th><p class="etiqueta">Lugar de expedición:</p></th>
                  <td><p class="dato">[fLugar_expedicion]</p></td>
                </tr>
              </tbody>
              </table>
          </div>
        </div>
      </div>                  
    </div>

    <div class="row">
      <div class="col-7">          
        <table class="table table-sm table-bordered">
          <thead class="encabezado-tabla">
            <tr>
              <th colspan="2">Entidad SNCF</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <th scope="col"><p class="etiqueta">Monto recurso</p></th>
              <th scope="col"><p class="etiqueta">Origen Recurso</p></th>
            </tr>
            <tr>
              <td><p class="dato">[sMonto_Recurso]</p></td>
              <td><p class="dato">[sOrigen_Recurso]</p></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    `,
  });
  //DATOS del empleado
  editor.BlockManager.add('empleado', {
    label: 'Datos del empleado',
    category: 'Comp. Factura Nomina',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        display: block;
        background-color: #b3eeda;
        font-weight: bold;
        text-align: center;
        padding: 0px;
        border: 1px solid #dee2e6;
        
      }

      .encabezado-tabla{
        background-color: #b3eeda;          
        text-align: center;
      }
      .etiqueta-encabezado{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 12px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .etiqueta{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        display: block;
        word-wrap: break-word;     /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        white-space: normal;   /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
        }
      .renglon {
          border: 1px solid #dee2e6;
      }
      .espacio-horizontal{
        height: 30px;
      }
      .espacio-vertical {
        width: 30px;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        
        vertical-align: top; 
      }
    </style>
    <div class="row">
      <div class="col-12">
        <table class="table table-sm table-bordered">
          <thead class="encabezado-tabla">
            <tr>
              <th colspan="6">Empleado</th>
            </tr>
          </thead>
          <tbody>                
              
            <tr>
              <th class="col-1"><p class="etiqueta">Empleado:</p></th>
              <td><p class="dato">[emEmpleado]</p></td>
              <th class="col-1"><p class="etiqueta">Puesto:</p></th>
              <td><p class="dato">[emPuesto]</p></td>
              <th class="col-1"><p class="etiqueta">Antigüedad:</p></th>
              <td><p class="dato">[emAntiguedad]</p></td>
            </tr>
            <tr>
              <th><p class="etiqueta">NSS:</p></th>
              <td><p class="dato">[emNSS]</p></td>
              <th><p class="etiqueta">Contrato:</p></th>
              <td><p class="dato">[emContrato]</p></td>
              <th><p class="etiqueta">Periodicidad:</p></th>
              <td><p class="dato">[emPeriodicidad]</p></td>
            </tr>
            <tr>
              <th><p class="etiqueta">CURP:</p></th>
              <td><p class="dato">[emCURP]</p></td>
              <th><p class="etiqueta">Entidad:</p></th>
              <td><p class="dato">[emEntidad]</p></td>
              <th><p class="etiqueta">Sindicalizado:</p></th>
              <td><p class="dato">[emSindicalizado]</p></td>
            </tr>
            <tr>
              <th><p class="etiqueta">RFC:</p></th>
              <td><p class="dato">[emRFC]</p></td>
              <th><p class="etiqueta">Régimen:</p></th>
              <td><p class="dato">[emRegimen]</p></td>
              <th><p class="etiqueta">Régimen pat.:</p></th>
              <td><p class="dato">[emReg_patronal]</p></td>
            </tr>
            <tr>
              <th><p class="etiqueta">Jornada:</p></th>
              <td><p class="dato">[emJornada]</p></td>
              <th><p class="etiqueta">CP:</p></th>
              <td><p class="dato">[emCodPostal]</p></td>
              <th><p class="etiqueta">Departamento:</p></th>
              <td><p class="dato">[emDepartamento]</p></td>
            </tr>
            <tr>
              <th><p class="etiqueta">Banco:</p></th>
              <td><p class="dato">[emBanco]</p></td>
              <th><p class="etiqueta">Riesgo:</p></th>
              <td><p class="dato">[emRiesgo]</p></td>
              <th><p class="etiqueta">Inicio rel. lab.:</p></th>
              <td><p class="dato">[emInicio_rel_lab]</p></td>
            </tr>
            <tr>
              <th><p class="etiqueta">ClaBe:</p></th>
              <td><p class="dato">[emClaBe]</p></td>
              <th><p class="etiqueta">No. Empleado:</p></th>
              <td><p class="dato">[emNo_Empleado]</p></td>
            </tr>
          </tbody>
        </table>    
      </div>
    </div>

    `,
  });
  //DATOS DEL ENCABEZADO PRINCIPAL
  editor.BlockManager.add('cfdi_y_sub', {
    label: 'CFDIs Relacionados y subcontratación',
    category: 'Comp. Factura Nomina',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        display: block;
        background-color: #b3eeda;
        font-weight: bold;
        text-align: center;
        padding: 0px;
        border: 1px solid #dee2e6;
        
      }

      .encabezado-tabla{
        background-color: #b3eeda;          
        text-align: center;
      }
      .etiqueta-encabezado{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 12px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .etiqueta{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        display: block;
        word-wrap: break-word;     /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        white-space: normal;   /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
        }
      .renglon {
          border: 1px solid #dee2e6;
      }
      .espacio-horizontal{
        height: 30px;
      }
      .espacio-vertical {
        width: 30px;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        
        vertical-align: top; 
      }
    </style>
    <div class="row d-flex justify-content-between">

      <div class="col-6">
        <table class="table table-sm table-bordered">
          <thead class="encabezado-tabla">
            <tr>
              <th colspan="2">CFDIs Relacionados</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <th scope="col"><p class="etiqueta">Tipo de relación</p></th>
              <th scope="col"><p class="etiqueta">UUID(s) Relacionados</p></th>
            </tr>
            <tr>
              <td><p class="dato">[cfTipo_relacion]</p></td>
              <td><p class="dato">[cfUUIDs_relacionados]</p></td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="col-5">
        <table class="table table-sm table-bordered">
          <thead class="encabezado-tabla">
            <tr>
              <th colspan="2">Subcontratación</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <th scope="col"><p class="etiqueta">RFC Laboral</p></th>
              <th scope="col"><p class="etiqueta">Tiempo(%)</p></th>
            </tr>
            <tr>
              <td><p class="dato">[suRFC]</p></td>
              <td><p class="dato">[suTiempo]</p></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    `,
  });
  //Datos de nomina
  editor.BlockManager.add('nomina', {
    label: 'Datos de nomina',
    category: 'Comp. Factura Nomina',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        display: block;
        background-color: #b3eeda;
        font-weight: bold;
        text-align: center;
        padding: 0px;
        border: 1px solid #dee2e6;
        
      }

      .encabezado-tabla{
        background-color: #b3eeda;          
        text-align: center;
      }
      .etiqueta-encabezado{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 12px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .etiqueta{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        display: block;
        word-wrap: break-word;     /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        white-space: normal;   /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
        }
      .renglon {
          border: 1px solid #dee2e6;
      }
      .espacio-horizontal{
        height: 30px;
      }
      .espacio-vertical {
        width: 30px;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        
        vertical-align: top; 
      }
    </style>
    <div class="row">
      <div class="col-12">
        <table class="table table-sm table-bordered">
          <thead class="encabezado-tabla">
            <tr>
              <th colspan="6">Nómina</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <th scope="col"><p class="etiqueta">Fecha inicial del pago</p></th>
              <th scope="col"><p class="etiqueta">Salario base</p></th>
              <th scope="col"><p class="etiqueta">Fecha final del pago</p></th>
              <th scope="col"><p class="etiqueta">Salario diario integrado</p></th>
              <th scope="col"><p class="etiqueta">Fecha de pago</p></th>
              <th scope="col"><p class="etiqueta">Días pagados</p></th>
            </tr>
            <tr>
              <td><p class="dato">[noFecha_inicial_pago]</p></td>
              <td><p class="dato">[noSalario_base]</p></td>
              <td><p class="dato">[noFecha_final_pago]</p></td>
              <td><p class="dato">[noSalario_diario_integrado]</p></td>
              <td><p class="dato">[noFecha_pago]</p></td>
              <td><p class="dato">[noDias_pagados]</p></td>
            </tr>
          </tbody>
        </table>
        
      </div>
    </div>
    `,
  });
  //Datos de percepciones
  editor.BlockManager.add('percepcion', {
    label: 'Datos de percepciones',
    category: 'Comp. Factura Nomina',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        display: block;
        background-color: #b3eeda;
        font-weight: bold;
        text-align: center;
        padding: 0px;
        border: 1px solid #dee2e6;
        
      }

      .encabezado-tabla{
        background-color: #b3eeda;          
        text-align: center;
      }
      .etiqueta-encabezado{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 12px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .etiqueta{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        display: block;
        word-wrap: break-word;     /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        white-space: normal;   /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
        }
      .renglon {
          border: 1px solid #dee2e6;
      }
      .espacio-horizontal{
        height: 30px;
      }
      .espacio-vertical {
        width: 30px;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        
        vertical-align: top; 
      }
    </style>
    <div class="row">
      <div class="col-12">
        <table class="table table-sm table-bordered">
          <thead class="encabezado-tabla">
            <tr>
              <th colspan="5">Percepciones</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <th scope="col"><p class="etiqueta">Clave</p></th>
              <th scope="col"><p class="etiqueta">Concepto</p></th>
              <th scope="col"><p class="etiqueta">Importe exento</p></th>
              <th scope="col"><p class="etiqueta">Importe gravado</p></th>
              <th scope="col"><p class="etiqueta">Tipo de percepción</p></th>
            </tr>
            <tr>
              <td><p class="dato">[pClave]</p></td>
              <td><p class="dato">[pConcepto]</p></td>
              <td><p class="dato">[pImporte_exento]</p></td>
              <td><p class="dato">[pImporte_gravado]</p></td>
              <td><p class="dato">[pTipo_percepcion]</p></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    `,
  });
  //Datos de deducciones
  editor.BlockManager.add('deduccion', {
    label: 'Datos de deducciones',
    category: 'Comp. Factura Nomina',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        display: block;
        background-color: #b3eeda;
        font-weight: bold;
        text-align: center;
        padding: 0px;
        border: 1px solid #dee2e6;
        
      }

      .encabezado-tabla{
        background-color: #b3eeda;          
        text-align: center;
      }
      .etiqueta-encabezado{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 12px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .etiqueta{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        display: block;
        word-wrap: break-word;     /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        white-space: normal;   /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
        }
      .renglon {
          border: 1px solid #dee2e6;
      }
      .espacio-horizontal{
        height: 30px;
      }
      .espacio-vertical {
        width: 30px;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        
        vertical-align: top; 
      }
    </style>
    <div class="row">
      <div class="col-12">
        <table class="table table-sm table-bordered">
          <thead class="encabezado-tabla">
            <tr>
              <th colspan="4">Deducciones</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <th scope="col"><p class="etiqueta">Clave</p></th>
              <th scope="col"><p class="etiqueta">Concepto</p></th>
              <th scope="col"><p class="etiqueta">Importe</p></th>
              <th scope="col"><p class="etiqueta">Tipo de deducción</p></th>
            </tr>
            <tr>
              <td><p class="dato">[dClabe]</p></td>
              <td><p class="dato">[dConcepto]</p></td>
              <td><p class="dato">[dImporte]</p></td>
              <td><p class="dato">[dTipo_deduccion]</p></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    `,
  });
  //Datos de horas extra, separaciones e indemnizaciones
  editor.BlockManager.add('horas_separacion', {
    label: 'Horas extra, separaciones e indemnizaciones',
    category: 'Comp. Factura Nomina',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        display: block;
        background-color: #b3eeda;
        font-weight: bold;
        text-align: center;
        padding: 0px;
        border: 1px solid #dee2e6;
        
      }

      .encabezado-tabla{
        background-color: #b3eeda;          
        text-align: center;
      }
      .etiqueta-encabezado{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 12px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .etiqueta{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        display: block;
        word-wrap: break-word;     /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        white-space: normal;   /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
        }
      .renglon {
          border: 1px solid #dee2e6;
      }
      .espacio-horizontal{
        height: 30px;
      }
      .espacio-vertical {
        width: 30px;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        
        vertical-align: top; 
      }
    </style>
    <div class="row d-flex justify-content-between">
      <div class="col-5">
        <table class="table table-sm table-bordered">
          <thead class="encabezado-tabla">
            <tr>
              <th colspan="4">Horas extra</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <th scope="col"><p class="etiqueta">Horas extra</p></th>
              <th scope="col"><p class="etiqueta">Días</p></th>
              <th scope="col"><p class="etiqueta">Tipo de horas</p></th>
              <th scope="col"><p class="etiqueta">Importe pagado</p></th>
            </tr>
            <tr>
              <td><p class="dato">[hHoras_extra]</p></td>
              <td><p class="dato">[hDias]</p></td>
              <td><p class="dato">[hTipo_horas]</p></td>
              <td><p class="dato">[hImporte_pagado]</p></td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div class="col-6">
        <table class="table table-sm table-bordered">
          <thead class="encabezado-tabla">
            <tr>
              <th colspan="5">Separaciones e indemnizaciones</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <th scope="col"><p class="etiqueta">Total</p></th>
              <th scope="col"><p class="etiqueta">Años de Serv.</p></th>
              <th scope="col"><p class="etiqueta">Sueldo</p></th>
              <th scope="col"><p class="etiqueta">Acumulable</p></th>
              <th scope="col"><p class="etiqueta">No acumulable</p></th>
            </tr>
            <tr>
              <td><p class="dato">[inTotal]</p></td>
              <td><p class="dato">[inAnios_Serv]</p></td>
              <td><p class="dato">[inSueldo]</p></td>
              <td><p class="dato">[inAcumulable]</p></td>
              <td><p class="dato">[inNo_acumulable]</p></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    `,
  });
  //Datos de acciones e incapacidades
  editor.BlockManager.add('acciones', {
    label: 'acciones e incapacidades',
    category: 'Comp. Factura Nomina',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        display: block;
        background-color: #b3eeda;
        font-weight: bold;
        text-align: center;
        padding: 0px;
        border: 1px solid #dee2e6;
      }
      .encabezado-tabla{
        background-color: #b3eeda;          
        text-align: center;
      }
      .etiqueta-encabezado{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 12px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .etiqueta{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        display: block;
        word-wrap: break-word;     /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        white-space: normal;   /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
        }
      .renglon {
          border: 1px solid #dee2e6;
      }
      .espacio-horizontal{
        height: 30px;
      }
      .espacio-vertical {
        width: 30px;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        
        vertical-align: top; 
      }
    </style>
    <div class="row">  
        <div class="col-6">
          <table class="table table-sm table-bordered">
            <thead class="encabezado-tabla">
              <tr>
                <th colspan="2">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <th scope="col"><p class="etiqueta">Precio al otorgarse</p></th>
                <th scope="col"><p class="etiqueta">Valor del mercado</p></th>
              </tr>
              <tr>
                <td><p class="dato">[aPrecio_otorgarse]</p></td>
                <td><p class="dato">[aValor_mercado]</p></td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="col-6">
          <table class="table table-sm table-bordered">
            <thead class="encabezado-tabla">
              <tr>
                <th colspan="3">Incapacidad</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <th scope="col"><p class="etiqueta">Días</p></th>
                <th scope="col"><p class="etiqueta">Importe monetario</p></th>
                <th scope="col"><p class="etiqueta">Tipo</p></th>
              </tr>
              <tr>
                <td><p class="dato">[icDias_incapacidad]</p></td>
                <td><p class="dato">[icImporte_Monetario]</p></td>
                <td><p class="dato">[icTipo_Incapacidad]</p></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    `,
  });
  //Datos de otros pagos
  editor.BlockManager.add('otros_pagos', {
    label: 'Otros pagos',
    category: 'Comp. Factura Nomina',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        display: block;
        background-color: #b3eeda;
        font-weight: bold;
        text-align: center;
        padding: 0px;
        border: 1px solid #dee2e6;
        
      }

      .encabezado-tabla{
        background-color: #b3eeda;          
        text-align: center;
      }
      .etiqueta-encabezado{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 12px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .etiqueta{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        display: block;
        word-wrap: break-word;     /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        white-space: normal;   /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
        }
      .renglon {
          border: 1px solid #dee2e6;
      }
      .espacio-horizontal{
        height: 30px;
      }
      .espacio-vertical {
        width: 30px;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        
        vertical-align: top; 
      }
    </style>
    <div class="row">
      <div class="col-12">
        <table class="table table-sm table-bordered">
          <thead class="encabezado-tabla">
            <tr>
              <th colspan="4">Otros pagos</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <th scope="col"><p class="etiqueta">Clave</p></th>
              <th scope="col"><p class="etiqueta">Concepto</p></th>
              <th scope="col"><p class="etiqueta">Importe</p></th>
              <th scope="col"><p class="etiqueta">Tipo de pago</p></th>
            </tr>
            <tr>
              <td><p class="dato">[oClave]</p></td>
              <td><p class="dato">[oConcepto]</p></td>
              <td><p class="dato">[oImporte]</p></td>
              <td><p class="dato">[oTipo_pago]</p></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    `,
  });
  //Datos de forma de pago
  editor.BlockManager.add('forma_pago', {
    label: 'forma de pago y QR',
    category: 'Comp. Factura Nomina',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        display: block;
        background-color: #b3eeda;
        font-weight: bold;
        text-align: center;
        padding: 0px;
        border: 1px solid #dee2e6;
        
      }

      .encabezado-tabla{
        background-color: #b3eeda;          
        text-align: center;
      }
      .etiqueta-encabezado{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 12px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .etiqueta{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        display: block;
        word-wrap: break-word;     /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        white-space: normal;   /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
        }
      .renglon {
          border: 1px solid #dee2e6;
      }
      .espacio-horizontal{
        height: 30px;
      }
      .espacio-vertical {
        width: 30px;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        
        vertical-align: top; 
      }
    </style>
    <div class="row">
      <div class="col-2">
        <img src="https://via.placeholder.com/150" id="QR" alt="QR" class="img-fluid" style="Border: 1px solid black; width: 110px; height: 110px;"/>
      </div>
      <div class="col-10">
        <table class="table table-sm table-bordered">
          <thead class="encabezado-tabla">
            <tr>
              <th ></th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td colspan="4"><p class="dato">[fTotal_con_letra]</p></td>
            </tr>
            <tr>
              <th colspan="4"><p class="etiqueta">Cantidad con letra</p></th>
            </tr>
            <tr>
              <th><p class="etiqueta">Método de pago:</p></th>
              <td><p class="dato">[fMetodo_pago]</p></td>
              <th><p class="etiqueta">Moneda:</p></th>
              <td><p class="dato">[fMoneda]</p></td>
            </tr>
            <tr>
              <th><p class="etiqueta">Forma de pago:</p></th>
              <td><p class="dato">[fForma_pago]</p></td>
              <th><p class="etiqueta">Condición de pago:</p></th>
              <td><p class="dato">[fCondicion_pago]</p></td>

            </tr>
          </tbody>
        </table>
      
      </div>
    </div>
    `,
  });
  //DATOS de total percepcion y total deduccion
  editor.BlockManager.add('totales', {
    label: 'totales percepcion y deduccion',
    category: 'Comp. Factura Nomina',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        display: block;
        background-color: #b3eeda;
        font-weight: bold;
        text-align: center;
        padding: 0px;
        border: 1px solid #dee2e6;
        
      }

      .encabezado-tabla{
        background-color: #b3eeda;          
        text-align: center;
      }
      .etiqueta-encabezado{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 12px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .etiqueta{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        display: block;
        word-wrap: break-word;     /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        white-space: normal;   /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
        }
      .renglon {
          border: 1px solid #dee2e6;
      }
      .espacio-horizontal{
        height: 30px;
      }
      .espacio-vertical {
        width: 30px;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        
        vertical-align: top; 
      }
    </style>
    
    <div class="col-12">
      <table class="table table-sm table-bordered">
        <thead class="encabezado-tabla">
          <tr>
            <th colspan="2">Total Percepciones</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <th><p class="etiqueta">Total exento:</p></th>
            <td><p class="dato">[tpTotal_Exento]</p></td>
          </tr>
          <tr>
            <th><p class="etiqueta">Total grabado:</p></th>
            <td><p class="dato">[tpTotal_Grabado]</p></td>
          </tr>
          <tr>
            <th><p class="etiqueta">Total Jub, pensión, retiro:</p></th>
            <td><p class="dato">[tpTotal_JPR]</p></td>
          </tr>
          <tr>
            <th><p class="etiqueta">Total Sep. indemnización:</p></th>
            <td><p class="dato">[tpTotal_Sep_Indemnizacion]</p></td>
          </tr>
          <tr>
            <th><p class="etiqueta">Total percepciones:</p></th>
            <td><p class="dato">[tpTotal_percepciones]</p></td>
          </tr>
          <tr>
            <th><p class="etiqueta">Total otros pagos:</p></th>
            <td><p class="dato">[tpTotal_otros_pagos]</p></td>
          </tr>
          <tr>
            <th><p class="etiqueta">Total deducciones:</p></th>
            <td><p class="dato">[tpTotal_deducciones]</p></td>
          </tr>
          <tr>
            <th><p class="etiqueta">Total:</p></th>
            <td><p class="dato">[tpTotal]</p></td>
          </tr>
        </tbody>
      </table>
      
      <table class="table table-sm table-bordered">
        <thead class="encabezado-tabla">
          <tr>
            <th colspan="2">Total Deducciones</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <th><p class="etiqueta">Total Imp. retenidos:</p></th>
            <td><p class="dato">[toTotal_Imp_Retenidos]</p></td>
          </tr>
          <tr>
            <th><p class="etiqueta">Total otras deducciones:</p></th>
            <td><p class="dato">[toTotal_Otras_Deducciones]</p></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
    `,
  });
  //Datos de notas
  editor.BlockManager.add('notasNomina', {
    label: 'Sellos y QR',
    category: 'Comp. Factura Nomina',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        display: block;
        background-color: #b3eeda;
        font-weight: bold;
        text-align: center;
        padding: 0px;
        border: 1px solid #dee2e6;
      }
      .encabezado-tabla{
        background-color: #b3eeda;          
        text-align: center;
      }
      .etiqueta-encabezado{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 12px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .etiqueta{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        display: block;
        word-wrap: break-word;     /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        white-space: normal;   /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
        }
      .renglon {
          border: 1px solid #dee2e6;
      }
      .espacio-horizontal{
        height: 30px;
      }
      .espacio-vertical {
        width: 30px;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        
        vertical-align: top; 
      }
    </style>
    <div class="row">
      <div class="col-12">
        <div class="row">
          <div class="col-12 renglo encabezado-resaltado">Cadena original del complemento de certificación del SAT</div>
        </div>
        <div class="row">
          <div class="col-12 renglo"><p class="dato">[fCertificado_SAT]</p></div>
        </div>
        <div class="row">
          <div class="col-12 renglo encabezado-resaltado">Sello digital del SAT</div>
        </div>
        <div class="row">
          <div class="col-12 renglo"><p class="dato">[fSello_SAT]</p></div>
        </div>
        <div class="row">
          <div class="col-12 renglo encabezado-resaltado">Sello digital del contribuyente que lo expide</div> 
        </div>
        <div class="row">
          <div class="col-12 renglo"><p class="dato">[nSello_digital_contribuyente]</p></div>
        </div>    
        <div class="row">
          <div class="col-12 renglo encabezado-resaltado">Notas</div>
        </div>
        <div class="row">
          <div class="col-12 renglo"><p class="dato">[nNota]</p></div>
        </div>
        <div class="row">
          <div class="col-3 renglon" ><p class="etiqueta">Efectos fiscales al pago:</p></div>
          <div class="col-9 renglon" ><p class="dato">[nEfectos_fiscales_al_pago]</p></div>
        </div>
      </div>
    </div>
    `,
  });

  //################## Componentes de CFDI Egreso #####################
  //Datos encabezado
  editor.BlockManager.add('Eencabezado', {
    label: 'Encabezado',
    category: 'Comp. Factura Egreso',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        background-color: #ffe4ca;
        font-weight: bold;
        text-align: center;
        padding: 4px 0;
        border: 1px solid #dee2e6;
        
      }
      .encabezado-tabla{
        background-color: #ffe4ca;          
        text-align: center;
      }
      .etiqueta{
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        word-wrap: break-word; /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        word-break: break-word; /* Alternativa para navegadores antiguos */
        white-space: normal; /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
      }
      .renglon {
          border: 1px solid #dee2e6;
      }
      .espacio-horizontal{
        height: 30px;
      }
      .espacio-vertical {
        width: 30px;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        vertical-align: top; 
      }
    </style>
    <div class="row">
      <div class="col-12">
        <table class="table table-sm ">
          <tbody class="encabezado-tabla">
            <tr class="d-flex">
              <td class="col-2 d-flex align-items-center">
                <p class="etiqueta me-2">Folio:</p>
                <p class="dato">[fFolio]</p>
              </td>
              <td class="col-2 d-flex align-items-center">
                <p class="etiqueta me-2">Serie:</p>
                <p class="dato">[fSerie]</p>
              </td>
              <td class="col-5 d-flex align-items-center">
                <p class="etiqueta me-2">No. Certificado:</p>
                <p class="dato">[fNo_certificado]</p>  
              </td>
              <td class="col-3 d-flex align-items-center">
                <p class="etiqueta me-2">Versión CFDI:</p>
                <p class="dato">[fVersion]</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    `,
  });
  //Datos emisor y factura
  editor.BlockManager.add('Eemisor_factura', {
    label: 'Datos emisor y factura egreso',
    category: 'Comp. Factura Egreso',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        background-color: #ffe4ca;
        font-weight: bold;
        text-align: center;
        padding: 4px 0;
        border: 1px solid #dee2e6;
        
      }
      .encabezado-tabla{
        background-color: #ffe4ca;          
        text-align: center;
      }
      .etiqueta{
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        word-wrap: break-word; /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        word-break: break-word; /* Alternativa para navegadores antiguos */
        white-space: normal; /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
      }
      .renglon {
          border: 1px solid #dee2e6;
      }
      .espacio-horizontal{
        height: 30px;
      }
      .espacio-vertical {
        width: 30px;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        vertical-align: top; 
      }
    </style>
    <div class="row">
      <div class="col-2">
        <img src="https://via.placeholder.com/150" id="Logo" alt="Logo" class="img-fluid" style="Border: 1px solid black; width: 147px; height: 110px;"/>
      </div>
      <div class="col-10 d-flex justify-content-between">
        <div class="col-5">
          <div class="row">
            <div class="col-12">
              <table class="table table-sm table-bordered">
                <thead class="encabezado-tabla">
                  <tr>
                    <th colspan="2">Emisor</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <th><p class="etiqueta">Razón social:</p></th>
                    <td><p class="dato">[eRazon_social]</p></td>
                  </tr>
                  <tr>
                    <th><p class="etiqueta">RFC:</p></th>
                    <td><p class="dato">[eRFC]</p></td>
                  </tr>
                  <tr>
                    <th><p class="etiqueta">Domicio Fiscal:</p></th>
                    <td><p class="dato">[eDomicilio_fiscal]</p></td>
                  </tr>
                  <tr>
                    <th><p class="etiqueta">Fac. Atr. adquiriente:</p></th>
                    <td><p class="dato">[eFac_Atr_adquiriente]</p></td>
                  </tr>
                  <tr>
                    <th><p class="etiqueta">Lugar de expedición:</p></th>
                    <td><p class="dato">[fLugar_expedicion]</p></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <div class="col-5">
          <div class="row">
            <div class="col-12">
              <table class="table table-sm table-bordered">
                <thead class="encabezado-tabla">
                  <tr>
                    <th colspan="2">Factura</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <th><p class="etiqueta">Folio fiscal:</p></th>
                    <td><p class="dato">[fFolio_fiscal]</p></td>
                  </tr>
                  <tr>
                    <th><p class="etiqueta">Serie CSD del SAT:</p></th>
                    <td><p class="dato">[fSerie_CSD_SAT]</p></td>
                  </tr>
                  <tr>
                    <th><p class="etiqueta">Tipo de comprobante:</p></th>
                    <td><p class="dato">[fTipo_de_comprobante]</p></td>
                  </tr>
                  <tr>
                    <th><p class="etiqueta">Fecha Certificación:</p></th>
                    <td><p class="dato">[fFecha_certificacion]</p></td>
                  </tr>
                  <tr>
                    <th><p class="etiqueta">Fecha emisión:</p></th>
                    <td><p class="dato">[fFecha_emision]</p></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>                  
    </div>
    `,
  });
  //Datos información global y CFDIs relacionados
  editor.BlockManager.add('EinformacionGlobal', {
    label: 'Información global y CFDIs relacionados',
    category: 'Comp. Factura Egreso',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        background-color: #ffe4ca;
        font-weight: bold;
        text-align: center;
        padding: 4px 0;
        border: 1px solid #dee2e6;
        
      }
      .encabezado-tabla{
        background-color: #ffe4ca;          
        text-align: center;
      }
      .etiqueta{
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        word-wrap: break-word; /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        word-break: break-word; /* Alternativa para navegadores antiguos */
        white-space: normal; /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
      }
      .renglon {
          border: 1px solid #dee2e6;
      }
      .espacio-horizontal{
        height: 30px;
      }
      .espacio-vertical {
        width: 30px;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        vertical-align: top; 
      }
    </style>
    <div class="row">
      <div class="col-4">
        <table class="table table-sm table-bordered text-center">
          <thead class="encabezado-tabla">
            <tr>
              <th colspan="3">Información Global</th>
            </tr>
          </thead>
          <tbody>
            <tr >
              <th><p class="etiqueta">Periodicidad</p></th>
              <th><p class="etiqueta">Meses</p></th>
              <th><p class="etiqueta">Año</p></th>
            </tr>
            <tr>
              <td><p class="dato">[iPeriodicidad]</p></td>
              <td><p class="dato">[iMeses]</p></td>
              <td><p class="dato">[iYear]</p></td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="col-8">
        <table class="table table-sm table-bordered">
          <thead class="encabezado-tabla">
            <tr>
              <th colspan="2">CFDIs Relacionados</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td class="col-3"><p class="etiqueta">Tipo de relación</p></td>
              <td><p class="etiqueta">UUID(s) Relacionados</p></td>
            </tr>
            <tr>
              <td class="col-3"><p class="dato">[cfTipo_relacion]</p></td>
              <td><p class="dato">[cfUUIDs_relacionados]</p></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    `,
  });
  //Datos del receptor
  editor.BlockManager.add('Ereceptor', {
    label: 'Receptor',
    category: 'Comp. Factura Egreso',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        background-color: #ffe4ca;
        font-weight: bold;
        text-align: center;
        padding: 4px 0;
        border: 1px solid #dee2e6;
        
      }
      .encabezado-tabla{
        background-color: #ffe4ca;          
        text-align: center;
      }
      .etiqueta{
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        word-wrap: break-word; /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        word-break: break-word; /* Alternativa para navegadores antiguos */
        white-space: normal; /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
      }
      .renglon {
          border: 1px solid #dee2e6;
      }
      .espacio-horizontal{
        height: 30px;
      }
      .espacio-vertical {
        width: 30px;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        vertical-align: top; 
      }
    </style>
    <div class="row">
      <div class="col-12">
        <table class="table table-sm table-bordered">
          <thead class="encabezado-tabla">
            <tr>
              <th colspan="6">Receptor</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><p class="etiqueta">RFC:</p></td>
              <td><p class="dato">[rRFC]</p></td>
              <td><p class="etiqueta">Razón social:</p></td>
              <td><p class="dato">[rRazon_social]</p></td>
              <td><p class="etiqueta">Num. Reg. id. Trib.:</p></td>
              <td><p class="dato">[rNum_Reg_id_Trib]</p></td>
            </tr>
            <tr>
              <td><p class="etiqueta">Uso de CFDI:</p></td>
              <td><p class="dato">[rUso_CFDI]</p></td>
              <td><p class="etiqueta">Régimen fiscal:</p></td>
              <td colspan="3"><p class="dato">[rRegimen_fiscal]</p></td>
            </tr>
            <tr>
              <td><p class="etiqueta">Residencia fiscal:</p></td>
              <td><p class="dato">[rResidencia_fiscal]</p></td>
              <td><p class="etiqueta">Domicilio fiscal:</p></td>
              <td colspan="3"><p class="dato">[rDomicilio_fiscal]</p></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    `,
  });
  //Datos de conceptos
  editor.BlockManager.add('Econceptos', {
    label: 'Conceptos',
    category: 'Comp. Factura Egreso',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        background-color: #ffe4ca;
        font-weight: bold;
        text-align: center;
        padding: 4px 0;
        border: 1px solid #dee2e6;
        
      }
      .encabezado-tabla{
        background-color: #ffe4ca;          
        text-align: center;
      }
      .etiqueta{
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        word-wrap: break-word; /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        word-break: break-word; /* Alternativa para navegadores antiguos */
        white-space: normal; /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
      }
      .renglon {
          border: 1px solid #dee2e6;
      }
      .espacio-horizontal{
        height: 30px;
      }
      .espacio-vertical {
        width: 30px;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        vertical-align: top; 
      }
    </style>
    <div class="row">
      <div class="col-12">
        <table class="table table-sm table-bordered">
          <thead class="encabezado-tabla">
            <tr>
              <th colspan="8">Conceptos</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <th scope="col"><p class="etiqueta">Cve prod.</p></th>
              <th scope="col"><p class="etiqueta">Num. de id</p></th>
              <th scope="col"><p class="etiqueta">Cant.</p></th>
              <th scope="col"><p class="etiqueta">Unidad</p></th>
              <th scope="col"><p class="etiqueta">Descripción</p></th>
              <th scope="col"><p class="etiqueta">Valor unitario</p></th>
              <th scope="col"><p class="etiqueta">Objeto impuesto</p></th>
              <th scope="col"><p class="etiqueta">Importe</p></th>
            </tr>
            <tr class="d-none">
              <td>{% for conceptos in CFDI.conceptos %}</td>
            </tr>
            <tr>
              <td><p class="dato">[cCve_prod]</p></td>
              <td><p class="dato">[cNum_id]</p></td>
              <td><p class="dato">[cCantidad]</p></td>
              <td><p class="dato">[cUnidad]</p></td>
              <td><p class="dato">[cDescripcion]</p></td>
              <td><p class="dato">[cValor_unitario]</p></td>
              <td><p class="dato">[cObjeto_impuesto]</p></td>
              <td><p class="dato">[cImporte]</p></td>
            </tr>
            <tr class="d-none">
              <td>{% endfor %}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    `,
  });
  //Datos de forma de pago y QR
  editor.BlockManager.add('Eformapago_QR', {
    label: 'Forma de pago y QR',
    category: 'Comp. Factura Egreso',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        background-color: #ffe4ca;
        font-weight: bold;
        text-align: center;
        padding: 4px 0;
        border: 1px solid #dee2e6;
        
      }
      .encabezado-tabla{
        background-color: #ffe4ca;          
        text-align: center;
      }
      .etiqueta{
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        word-wrap: break-word; /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        word-break: break-word; /* Alternativa para navegadores antiguos */
        white-space: normal; /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
      }
      .renglon {
          border: 1px solid #dee2e6;
      }
      .espacio-horizontal{
        height: 30px;
      }
      .espacio-vertical {
        width: 30px;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        vertical-align: top; 
      }
    </style>
    <div class="row">
      <div class="col-2">
        <img src="https://via.placeholder.com/150" id="QR" alt="Logo" class="img-fluid" style="Border: 1px solid black; width: 147px; height: 110px;"/>
      </div>
      <div class="col-10">
        <table class="table table-sm table-bordered">
          <tbody>
            <tr>
              <td colspan="4" class="text-center"><p class="dato">[fTotal_con_letra]</p></td>
            </tr>
            <tr>
              <td colspan="4" class="text-center"><p class="etiqueta">Total con letra</p></td>
            </tr>
            <tr>
              <th scope="row"><p class="etiqueta">Método de pago:</p></th>
              <td><p class="dato">[fMetodo_pago]</p></td>
              <th scope="row"><p class="etiqueta">Moneda:</p></th>
              <td><p class="dato">[fMoneda]</p></td>
            </tr>
            <tr>
              <th scope="row"><p class="etiqueta">Forma de pago:</p></th>
              <td><p class="dato">[fForma_pago]</p></td>
              <th scope="row"><p class="etiqueta">Tipo-cambio:</p></th>
              <td><p class="dato">[fTipo_cambio]</p></td>
            </tr>
            <tr>
              <th scope="row"><p class="etiqueta">Condición de pago:</p></th>
              <td><p class="dato">[fCondicion_pago]</p></td>
              <th scope="row"><p class="etiqueta">Confirmación:</p></th>
              <td><p class="dato">[fConfirmacion]</p></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    `,
  });
  //Datos total e impuestos
  editor.BlockManager.add('Eimpuestos', {
    label: 'Totales e inpuestos',
    category: 'Comp. Factura Egreso',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        background-color: #ffe4ca;
        font-weight: bold;
        text-align: center;
        padding: 4px 0;
        border: 1px solid #dee2e6;
        
      }
      .encabezado-tabla{
        background-color: #ffe4ca;          
        text-align: center;
      }
      .etiqueta{
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        word-wrap: break-word; /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        word-break: break-word; /* Alternativa para navegadores antiguos */
        white-space: normal; /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
      }
      .renglon {
          border: 1px solid #dee2e6;
      }
      .espacio-horizontal{
        height: 30px;
      }
      .espacio-vertical {
        width: 30px;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        vertical-align: top; 
      }
    </style>
    <div class="row">
      <div class="col-12">
        <table class="table table-sm table-bordered">
          <tbody>
            <tr>
              <th><p class="etiqueta">Subtotal:</p></th>
              <td><p class="dato">[fSubtotal]</p></td>
            </tr>
            <tr>
              <th><p class="etiqueta">Impuestos Equiq.:</p></th>
              <td><p class="dato">[imImpuestos_Equiq]</p></td>
            </tr>
            <tr>
              <th><p class="etiqueta">Total Imp. Trasladados:</p></th>
              <td><p class="dato">[imTot_imp_Tras]</p></td>
            </tr>
            <tr>
              <th><p class="etiqueta">Total Imp. Retenidos:</p></th>
              <td><p class="dato">[imTot_imp_Ret]</p></td>
            </tr>
            <tr>
              <th><p class="etiqueta">Descuento:</p></th>
              <td><p class="dato">[fDescuento]</p></td>
            </tr>
            <tr>
              <th><p class="etiqueta">Total:</p></th>
              <td><p class="dato">[fTotal]</p></td>
            </tr>
        </table>
      </div>
    </div>
    `,
  });
  //Datos de los sellos
  editor.BlockManager.add('Esellos', {
    label: 'Sellos',
    category: 'Comp. Factura Egreso',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        background-color: #ffe4ca;
        font-weight: bold;
        text-align: center;
        padding: 4px 0;
        border: 1px solid #dee2e6;
        
      }
      .encabezado-tabla{
        background-color: #ffe4ca;          
        text-align: center;
      }
      .etiqueta{
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        word-wrap: break-word; /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        word-break: break-word; /* Alternativa para navegadores antiguos */
        white-space: normal; /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
      }
      .renglon {
          border: 1px solid #dee2e6;
      }
      .espacio-horizontal{
        height: 30px;
      }
      .espacio-vertical {
        width: 30px;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        vertical-align: top; 
      }
    </style>
    <div class="row">
      <div class="col-12">
        <div class="row">
          <div class="col-12 encabezado-resaltado">Cadena original del complemento de certificación del SAT</div>
        </div>
        <div class="row">
          <div class="col-12 "><p class="dato renglon">[fCertificado_SAT]</p></div>
        </div>
        <div class="row">
          <div class="col-12 encabezado-resaltado">SELLO DIGITAL DEL SAT</div>
        </div>
        <div class="row">
          <div class="col-12 "><p class="dato renglon">[fSello_SAT]</p></div>
        </div>
        <div class="row">
          <div class="col-12 encabezado-resaltado">SELLO DIGITAL DEL CONTRIBUYENTE QUE LO EXPIDE</div>
        </div>
        <div class="row">
          <div class="col-12 "><p class="dato renglon">[nSello_digital_contribuyente]</p></div>
        </div>
      </div>
    </div>
    `,
  });
  //Datos de las notas
  editor.BlockManager.add('Enotas', {
    label: 'Notas',
    category: 'Comp. Factura Egreso',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        background-color: #ffe4ca;
        font-weight: bold;
        text-align: center;
        padding: 4px 0;
        border: 1px solid #dee2e6;
        
      }
      .encabezado-tabla{
        background-color: #ffe4ca;          
        text-align: center;
      }
      .etiqueta{
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        word-wrap: break-word; /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        word-break: break-word; /* Alternativa para navegadores antiguos */
        white-space: normal; /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
      }
      .renglon {
          border: 1px solid #dee2e6;
      }
      .espacio-horizontal{
        height: 30px;
      }
      .espacio-vertical {
        width: 30px;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        vertical-align: top; 
      }
    </style>
    <div class="row">
      <div class="col-12">
        <table class="table table-sm table-bordered">
          <tr class="encabezado-tabla">
            <th  colspan="6">Notas</th>
          </tr>
          <tr>
            <td colspan="6"><p class="dato">[nNota]</p></td>
          </tr>
          <tr class="encabezado-tabla">
            <th colspan="6">LEYENDAS FISCALES</th>
          </tr>
          <tr>
            <th><p class="etiqueta">DISPOSICIÓN FISCAL:</p></th>
            <td><p class="dato">[nDisposicion_fiscal]</p></td>
            <th><p class="etiqueta">NORMA:</p></th>
            <td><p class="dato">[nNorma]</p></td>
            <th><p class="etiqueta">LEYENDA:</p></th>
            <td><p class="dato">[nLeyenda]</p></td>
          </tr>

        </table>
      </div>
    </div>
    `,
  });
  //################## Componentes de CFDI Pago #####################
  //Datos del encabezado
  editor.BlockManager.add('Pencabezado', {
    label: 'encabezado',
    category: 'Comp. Factura Pago',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        display: block;
        background-color: #d3d2e7;
        font-weight: bold;
        text-align: center;
        padding: 0px;
        border: 1px solid #dee2e6;
      }
      .encabezado-tabla{
        background-color: #d3d2e7;          
        text-align: center;
      }
      .etiqueta-encabezado{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 12px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .etiqueta{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        display: block;
        word-wrap: break-word;     /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        white-space: normal;   /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
        }
      .renglon {
          border: 1px solid #dee2e6;
      }
      .espacio-horizontal{
        height: 30px;
      }
      .espacio-vertical {
        width: 30px;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        vertical-align: top; 
      }
    </style>
    <div class="row">
      <div class="col-12">
        <table class="table table-sm ">
          <tbody>
            <tr class="d-flex">
              <td class="col-2 d-flex align-items-center">
                <p class="etiqueta me-2">Folio:</p>
                <p class="dato">[fFolio]</p>
              </td>
              <td class="col-2 d-flex align-items-center">
                <p class="etiqueta me-2">Serie:</p>
                <p class="dato">[fSerie]</p>
              </td>
              <td class="col-5 d-flex align-items-center">
                <p class="etiqueta me-2">No. Certificado:</p>
                <p class="dato">[fNo_certificado]</p>  
              </td>
              <td class="col-3 d-flex align-items-center">
                <p class="etiqueta me-2">Versión CFDI:</p>
                <p class="dato">[fVersion]</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    `,
  });
  //Datos emisor y factura pago
  editor.BlockManager.add('Pemisor_pago', {
    label: 'Emisor y factura pago',
    category: 'Comp. Factura Pago',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        display: block;
        background-color: #d3d2e7;
        font-weight: bold;
        text-align: center;
        padding: 0px;
        border: 1px solid #dee2e6;
      }
      .encabezado-tabla{
        background-color: #d3d2e7;          
        text-align: center;
      }
      .etiqueta-encabezado{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 12px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .etiqueta{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        display: block;
        word-wrap: break-word;     /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        white-space: normal;   /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
        }
      .renglon {
          border: 1px solid #dee2e6;
      }
      .espacio-horizontal{
        height: 30px;
      }
      .espacio-vertical {
        width: 30px;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        vertical-align: top; 
      }
    </style>
    <div class="row">
      <div class="col-2">
        <img src="https://via.placeholder.com/150" id="Logo" alt="Logo" class="img-fluid" style="Border: 1px solid black; width: 147px; height: 110px;"/>
      </div>
      <div class="col-10 d-flex justify-content-between">
        <div class="col-5">
          <div class="row">
            
              <table class="table table-sm">
                <thead class="encabezado-tabla">
                  <tr>
                    <th colspan="2">Emisor</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <th class="col-4"><p class="etiqueta">Razón social: </p></th>
                    <td ><p class="dato">[eRazon_social]</p></td>
                  </tr>
                  <tr>
                    <th ><p class="etiqueta">RFC:</p></th>
                    <td ><p class="dato">[eRFC]</p></td>
                  </tr>
                  <tr>
                    <th ><p class="etiqueta">Domicio Fiscal:</p></th>
                    <td ><p class="dato">[eDomicilio_fiscal]</p></td>
                  </tr>
                  <tr>
                    <th ><p class="etiqueta">Fac. Atr. adquiriente:</p></th>
                    <td ><p class="dato">[eFac_Atr_adquiriente]</p></td>
                  </tr>
                  <tr>
                    <th ><p class="etiqueta">Lugar de expedición:</p></th>
                    <td ><p class="dato">[fLugar_expedicion]</p></td>
                  </tr>
                </tbody>
              </table>
            
          </div>
        </div>
        <div class="col-5">
          <div class="row">
            
              <table class="table table-sm table-bordered">
                <thead class="encabezado-tabla">
                  <tr>
                    <th colspan="2">Recibo de Pago</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <th class="col-5"><p class="etiqueta">Folio fiscal:</p></th>
                    <td><p class="dato">[fFolio_fiscal]</p></td>
                  </tr>
                  <tr>
                    <th><p class="etiqueta">Serie CSD del SAT:</p></th>
                    <td><p class="dato">[fSerie_CSD_SAT]</p></td>
                  </tr>
                  <tr>
                    <th><p class="etiqueta">Tipo de comprobante:</p></th>
                    <td><p class="dato">[fTipo_de_comprobante]</p></td>
                  </tr>
                  <tr>
                    <th><p class="etiqueta">Exportación:</p></th>
                    <td><p class="dato">[fExportacion]</p></td>
                  </tr>
                  <tr>
                    <th><p class="etiqueta">Fecha Certificación:</p></th>
                    <td><p class="dato">[fFecha_certificacion]</p></td>
                  </tr>
                  <tr>
                    <th><p class="etiqueta">Fecha emisión:</p></th>
                    <td><p class="dato">[fFecha_emision]</p></td>
                  </tr>
                  
                </tbody>
              </table>
            
          </div>
        </div>
      </div>                  
    </div>
    `,
  });
  //Datos información global y CFDIs relacionados
  editor.BlockManager.add('PinformacionGlobal', {
    label: 'Inf. Global y CFDIs relacionados',
    category: 'Comp. Factura Pago',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        display: block;
        background-color: #d3d2e7;
        font-weight: bold;
        text-align: center;
        padding: 0px;
        border: 1px solid #dee2e6;
      }
      .encabezado-tabla{
        background-color: #d3d2e7;          
        text-align: center;
      }
      .etiqueta-encabezado{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 12px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .etiqueta{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        display: block;
        word-wrap: break-word;     /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        white-space: normal;   /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
        }
      .renglon {
          border: 1px solid #dee2e6;
      }
      .espacio-horizontal{
        height: 30px;
      }
      .espacio-vertical {
        width: 30px;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        vertical-align: top; 
      }
    </style>
    <div class="row">
      <div class="col-4">
        <table class="table table-sm table-bordered text-center">
          <thead class="encabezado-tabla">
            <tr>
              <th colspan="3">Información Global</th>
            </tr>
          </thead>
          <tbody>
            <tr >
              <th><p class="etiqueta">Periodicidad</p></th>
              <th><p class="etiqueta">Meses</p></th>
              <th><p class="etiqueta">Año</p></th>
            </tr>
            <tr>
              <td><p class="dato">[iPeriodicidad]</p></td>
              <td><p class="dato">[iMeses]</p></td>
              <td><p class="dato">[iYear]</p></td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="col-8">
        <div class="row">
          
            <table class="table table-sm table-bordered">
              <thead class="encabezado-tabla">
                <tr>
                  <th colspan="2">CFDIs Relacionados</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td class="col-3"><p class="etiqueta">Tipo de relación</p></td>
                  <td><p class="etiqueta">UUID(s) Relacionados</p></td>
                </tr>
                <tr>
                  <td ><p class="dato">[cfTipo_relacion]</p></td>
                  <td><p class="dato">[cfUUIDs_relacionados]</p></td>
                </tr>
              </tbody>
            </table>
          
        </div>
      </div>
    </div>
    
    `,
  });
  //Datos del receptor
  editor.BlockManager.add('Preceptor', {
    label: 'Receptor',
    category: 'Comp. Factura Pago',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        display: block;
        background-color: #d3d2e7;
        font-weight: bold;
        text-align: center;
        padding: 0px;
        border: 1px solid #dee2e6;
      }
      .encabezado-tabla{
        background-color: #d3d2e7;          
        text-align: center;
      }
      .etiqueta-encabezado{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 12px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .etiqueta{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        display: block;
        word-wrap: break-word;     /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        white-space: normal;   /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
        }
      .renglon {
          border: 1px solid #dee2e6;
      }
      .espacio-horizontal{
        height: 30px;
      }
      .espacio-vertical {
        width: 30px;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        vertical-align: top; 
      }
    </style>
    <div class="row">
      <div class="col-12">
        <table class="table table-sm table-bordered">
          <thead class="encabezado-tabla">
            <tr>
              <th colspan="6">Receptor</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td class="col-1"><p class="etiqueta">RFC:</p></td>
              <td class="col-2"><p class="dato">[rRFC]</p></td>
              <td class="col-1"><p class="etiqueta">Razón social:</p></td>
              <td class="col-3"><p class="dato">[rRazon_social]</p></td>
              <td class="col-1"><p class="etiqueta">Domicilio fiscal:</p></td>
              <td class="col-3"><p class="dato">[rDomicilio_fiscal]</p></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    `,
  });
  //Datos de Pago
  editor.BlockManager.add('Pago', {
    label: 'Pago',
    category: 'Comp. Factura Pago',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        display: block;
        background-color: #d3d2e7;
        font-weight: bold;
        text-align: center;
        padding: 0px;
        border: 1px solid #dee2e6;
      }
      .encabezado-tabla{
        background-color: #d3d2e7;          
        text-align: center;
      }
      .etiqueta-encabezado{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 12px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .etiqueta{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        display: block;
        word-wrap: break-word;     /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        white-space: normal;   /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
        }
      .renglon {
          border: 1px solid #dee2e6;
      }
      .espacio-horizontal{
        height: 30px;
      }
      .espacio-vertical {
        width: 30px;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        vertical-align: top; 
      }
    </style>
    <div class="row">
      <div class="col-12">
        <table class="table table-sm table-bordered">
          <thead class="encabezado-tabla">
            <tr>
              <th colspan="8">Pago</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <th scope="col"><p class="etiqueta">Cve prod.</p></th>
              <th scope="col"><p class="etiqueta">Num. de id</p></th>
              <th scope="col"><p class="etiqueta">Cant.</p></th>
              <th scope="col"><p class="etiqueta">Unidad</p></th>
              <th scope="col"><p class="etiqueta">Descripción</p></th>
              <th scope="col"><p class="etiqueta">Valor unitario</p></th>
              <th scope="col"><p class="etiqueta">Objeto impuesto</p></th>
              <th scope="col"><p class="etiqueta">Importe</p></th>
            </tr>
            <tr class="d-none">
              <td>{% for conceptos in CFDI.conceptos %}</td>
            </tr>
            <tr>
              <td><p class="dato">[cCve_prod]</p></td>
              <td><p class="dato">[cNum_id]</p></td>
              <td><p class="dato">[cCantidad]</p></td>
              <td><p class="dato">[cUnidad]</p></td>
              <td><p class="dato">[cDescripcion]</p></td>
              <td><p class="dato">[cValor_unitario]</p></td>
              <td><p class="dato">[cObjeto_impuesto]</p></td>
              <td><p class="dato">[cImporte]</p></td>
            </tr>
            <tr class="d-none">
              <td>{% endfor %}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    `,
  });
  //Datos de forma de pago, impuestos, totales y QR
  editor.BlockManager.add('PformaPago_QR', {
    label: 'Forma de pago, totales, impuestos y QR',
    category: 'Comp. Factura Pago',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        display: block;
        background-color: #d3d2e7;
        font-weight: bold;
        text-align: center;
        padding: 0px;
        border: 1px solid #dee2e6;
      }
      .encabezado-tabla{
        background-color: #d3d2e7;          
        text-align: center;
      }
      .etiqueta-encabezado{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 12px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .etiqueta{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        display: block;
        word-wrap: break-word;     /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        white-space: normal;   /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
        }
      .renglon {
          border: 1px solid #dee2e6;
      }
      .espacio-horizontal{
        height: 30px;
      }
      .espacio-vertical {
        width: 30px;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        vertical-align: top; 
      }
    </style>
    <div class="row d-flex justify-content-between">
      <div class="col-2">
          <img src="https://via.placeholder.com/150" id="QR" alt="Logo" class="img-fluid" style="Border: 1px solid black; width: 147px; height: 110px;"/>
      </div>
      <div class="col-7">
        <div class="row">
          
            <table class="table table-sm table-bordered">
              <tbody>
                <tr>
                  <td colspan="4" class="text-center"><p class="dato">[fTotal_con_letra]</p></td>
                </tr>
                <tr>
                  <td colspan="4" class="text-center"><p class="etiqueta">Total con letra</p></td>
                </tr>
                <tr>
                  <th class="col-3"><p class="etiqueta">Método de pago:</p></th>
                  <td><p class="dato">[fMetodo_pago]</p></td>
                  <th class="col-2"><p class="etiqueta">Moneda:</p></th>
                  <td><p class="dato">[fMoneda]</p></td>
                </tr>
                <tr>
                  <th><p class="etiqueta">Forma de pago:</p></th>
                  <td><p class="dato">[fForma_pago]</p></td>
                  <th><p class="etiqueta">Tipo-cambio:</p></th>
                  <td><p class="dato">[fTipo_cambio]</p></td>
                </tr>
                <tr>
                  <th><p class="etiqueta">Condición de pago:</p></th>
                  <td><p class="dato">[fCondicion_pago]</p></td>
                </tr>
              </tbody>
            </table>
          
        </div>
      </div>

      <div class="col-3">
        <div class="row">
          <div class="col-12">
            <table class="table table-sm table-bordered">
              <tbody>
                <tr>
                  <th><p class="etiqueta">Subtotal:</p></th>
                  <td><p class="dato">[fSubtotal]</p></td>
                </tr>
                <tr>
                  <th><p class="etiqueta">Impuestos Equiq.:</p></th>
                  <td><p class="dato">[imImpuestos_Equiq]</p></td>
                </tr>
                <tr>
                  <th><p class="etiqueta">Total Imp. Trasladados:</p></th>
                  <td><p class="dato">[imTot_imp_Tras]</p></td>
                </tr>
                <tr>
                  <th><p class="etiqueta">Total Imp. Retenidos:</p></th>
                  <td><p class="dato">[imTot_imp_Ret]</p></td>
                </tr>
                <tr>
                  <th><p class="etiqueta">Descuento:</p></th>
                  <td><p class="dato">[fDescuento]</p></td>
                </tr>
                <tr>
                  <th><p class="etiqueta">Total:</p></th>
                  <td><p class="dato">[fTotal]</p></td>
                </tr>
            </table>
          </div>
        </div>
      </div>
    </div>
    `,
  });
  //Datos de sellos
  editor.BlockManager.add('Psellos', {
    label: 'Sellos',
    category: 'Comp. Factura Pago',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        display: block;
        background-color: #d3d2e7;
        font-weight: bold;
        text-align: center;
        padding: 0px;
        border: 1px solid #dee2e6;
      }
      .encabezado-tabla{
        background-color: #d3d2e7;          
        text-align: center;
      }
      .etiqueta-encabezado{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 12px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .etiqueta{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        display: block;
        word-wrap: break-word;     /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        white-space: normal;   /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
        }
      .renglon {
          border: 1px solid #dee2e6;
      }
      .espacio-horizontal{
        height: 30px;
      }
      .espacio-vertical {
        width: 30px;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        vertical-align: top; 
      }
    </style>
    <div class="row">
      <div class="col-12">
        <div class="row">
          <div class="col-12 encabezado-resaltado">Cadena original del complemento de certificación del SAT</div>
        </div>
        <div class="row">
          <div class="col-12 "><p class="dato renglon">[fCertificado_SAT]</p></div>
        </div>
        <div class="row">
          <div class="col-12 encabezado-resaltado">SELLO DIGITAL DEL SAT</div>
        </div>
        <div class="row">
          <div class="col-12 "><p class="dato renglon">[fSello_SAT]</p></div>
        </div>
        <div class="row">
          <div class="col-12 encabezado-resaltado">SELLO DIGITAL DEL CONTRIBUYENTE QUE LO EXPIDE</div>
        </div>
        <div class="row">
          <div class="col-12 "><p class="dato renglon">[nSello_digital_contribuyente]</p></div>
        </div>
      </div>
    </div>
    
    `,
  });
  //################## Componentes de CFDI Retencion #####################
  //Datos encabezado
  editor.BlockManager.add('Rencabezado', {
    label: 'Encabezado',
    category: 'Comp. Factura Retencion',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        display: block;
        background-color: #d7c4ce;
        font-weight: bold;
        text-align: center;
        padding: 0px;
        border: 1px solid #dee2e6;
      }
      .encabezado-tabla{
        background-color: #d7c4ce;          
        text-align: center;
      }
      .etiqueta-encabezado{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 12px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .etiqueta{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        display: block;
        word-wrap: break-word;     /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        white-space: normal;   /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
        }
      .renglon {
          border: 1px solid #dee2e6;
      }
      .espacio-horizontal{
        height: 30px;
      }
      .espacio-vertical {
        width: 30px;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        vertical-align: top; 
      }
    </style>
    <div class="row">
      <div class="col-12">
        <table class="table table-sm ">
          <tbody>
            <tr class="d-flex">
              <td class="col-2 d-flex align-items-center">
                <p class="etiqueta me-2">Folio:</p>
                <p class="dato">[fFolio]</p>
              </td>
              <td class="col-2 d-flex align-items-center">
                <p class="etiqueta me-2">Serie:</p>
                <p class="dato">[fSerie]</p>
              </td>
              <td class="col-5 d-flex align-items-center">
                <p class="etiqueta me-2">No. Certificado:</p>
                <p class="dato">[fNo_certificado]</p>  
              </td>
              <td class="col-3 d-flex align-items-center">
                <p class="etiqueta me-2">Versión CFDI:</p>
                <p class="dato">[fVersion]</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    `,
  });
  //Datos emisor
  editor.BlockManager.add('Remisor', {
    label: 'Emisor',
    category: 'Comp. Factura Retencion',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        display: block;
        background-color: #d7c4ce;
        font-weight: bold;
        text-align: center;
        padding: 0px;
        border: 1px solid #dee2e6;
      }
      .encabezado-tabla{
        background-color: #d7c4ce;          
        text-align: center;
      }
      .etiqueta-encabezado{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 12px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .etiqueta{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        display: block;
        word-wrap: break-word;     /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        white-space: normal;   /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
        }
      .renglon {
          border: 1px solid #dee2e6;
      }
      .espacio-horizontal{
        height: 30px;
      }
      .espacio-vertical {
        width: 30px;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        vertical-align: top; 
      }
    </style>
    <div class="row">
      <div class="col-2">
        <img src="https://via.placeholder.com/150" id="Logo" alt="Logo" class="img-fluid" style="Border: 1px solid black; width: 147px; height: 110px;"/>
      </div>
      <div class="col-10 d-flex justify-content-between">
        <div class="col-5">
          <div class="row">
            
              <table class="table table-sm">
                <thead class="encabezado-tabla">
                  <tr>
                    <th colspan="2">Emisor</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <th class="col-4"><p class="etiqueta">Razón social: </p></th>
                    <td ><p class="dato">[eRazon_social]</p></td>
                  </tr>
                  <tr>
                    <th ><p class="etiqueta">RFC:</p></th>
                    <td ><p class="dato">[eRFC]</p></td>
                  </tr>
                  <tr>
                    <th ><p class="etiqueta">Regimen fiscal:</p></th>
                    <td ><p class="dato">[eRegimen_fiscal]</p></td>
                  </tr>
                  <tr>
                    <th ><p class="etiqueta">Lugar de expedición:</p></th>
                    <td ><p class="dato">[fLugar_expedicion]</p></td>
                  </tr>
                  <tr>
                    <th><p class="etiqueta">Fecha Certificación:</p></th>
                    <th><p class="dato">[fFecha_certificacion]</p></th>
                  </tr>
                  <tr>
                    <th><p class="etiqueta">Fecha emisión:</p></th>
                    <td><p class="dato">[fFecha_emision]</p></td>
                  </tr>
                </tbody>
              </table>
            
          </div>
        </div>
    </div>
    `,
  });
  //Datos receptor
  editor.BlockManager.add('Rreceptor', {
    label: 'receptor',
    category: 'Comp. Factura Retencion',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        display: block;
        background-color: #d7c4ce;
        font-weight: bold;
        text-align: center;
        padding: 0px;
        border: 1px solid #dee2e6;
      }
      .encabezado-tabla{
        background-color: #d7c4ce;          
        text-align: center;
      }
      .etiqueta-encabezado{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 12px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .etiqueta{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        display: block;
        word-wrap: break-word;     /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        white-space: normal;   /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
        }
      .renglon {
          border: 1px solid #dee2e6;
      }
      .espacio-horizontal{
        height: 30px;
      }
      .espacio-vertical {
        width: 30px;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        vertical-align: top; 
      }
    </style>
    <div class="row">
      <div class="col-12">
        <table class="table table-sm table-bordered">
          <thead class="encabezado-tabla">
            <tr>
              <th colspan="2">Receptor</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <th class="col-4"><p class="etiqueta">RFC:</p></th>
              <td><p class="dato">[rRFC]</p></td>
            </tr>
            <tr>
              <th><p class="etiqueta">Razón social:</p></th>
              <td><p class="dato">[rRazon_social]</p></td>
            </tr>
            <tr>
              <td><p class="etiqueta">CURP:</p></td>
              <td><p class="dato">[rCURP]</p></td>
            </tr>
            <tr>
              <th><p class="etiqueta">Domicilio fiscal:</p></th>
              <td><p class="dato">[rDomicilio_fiscal]</p></td>
            </tr>
            <tr>
              <th><p class="etiqueta">Nacionalidad:</p></th>
              <td><p class="dato">[rNacionalidad]</p></td>
            </tr>
            <tr>
              <th><p class="etiqueta">Num. Reg. id. trib.:</p></th>
              <td><p class="dato">[rNum_Reg_id_Trib]</p></td>
            </tr>
            
          </tbody>
        </table>
      </div>
    </div>
    `,
  });
  //Datos periodo
  editor.BlockManager.add('Rperiodo', {
    label: 'Periodo',
    category: 'Comp. Factura Retencion',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        display: block;
        background-color: #d7c4ce;
        font-weight: bold;
        text-align: center;
        padding: 0px;
        border: 1px solid #dee2e6;
      }
      .encabezado-tabla{
        background-color: #d7c4ce;          
        text-align: center;
      }
      .etiqueta-encabezado{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 12px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .etiqueta{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        display: block;
        word-wrap: break-word;     /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        white-space: normal;   /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
        }
      .renglon {
          border: 1px solid #dee2e6;
      }
      .espacio-horizontal{
        height: 30px;
      }
      .espacio-vertical {
        width: 30px;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        vertical-align: top; 
      }
    </style>
    <div class="row">
      <div class="col-4">
        <table class="table table-sm table-bordered text-center">
          <thead class="encabezado-tabla">
            <tr>
              <th colspan="3">Período</th>
            </tr>
          </thead>
          <tbody>
            <tr >
              <th><p class="etiqueta">Mes inicio</p></th>
              <th><p class="etiqueta">Mes final</p></th>
              <th><p class="etiqueta">Año retención</p></th>
            </tr>
            <tr>
              <td><p class="dato">[peMes_ini]</p></td>
              <td><p class="dato">[peMes_fin]</p></td>
              <td><p class="dato">[peEjercicio]</p></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    `,
  });
  //Datos CFDIs Relacionados
  editor.BlockManager.add('Rcfdis', {
    label: 'CFDIs Relacionados',
    category: 'Comp. Factura Retencion',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        display: block;
        background-color: #d7c4ce;
        font-weight: bold;
        text-align: center;
        padding: 0px;
        border: 1px solid #dee2e6;
      }
      .encabezado-tabla{
        background-color: #d7c4ce;          
        text-align: center;
      }
      .etiqueta-encabezado{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 12px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .etiqueta{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        display: block;
        word-wrap: break-word;     /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        white-space: normal;   /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
        }
      .renglon {
          border: 1px solid #dee2e6;
      }
      .espacio-horizontal{
        height: 30px;
      }
      .espacio-vertical {
        width: 30px;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        vertical-align: top; 
      }
    </style>
    
    <div class="row">
      <div class="col-12">
        <table class="table table-sm table-bordered">
          <thead class="encabezado-tabla">
            <tr>
              <th colspan="2">CFDIs Relacionados</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td class="col-3"><p class="etiqueta">Tipo de relación</p></td>
              <td><p class="etiqueta">UUID(s) Relacionados</p></td>
            </tr>
            <tr>
              <td ><p class="dato">[cfTipo_relacion]</p></td>
              <td><p class="dato">[cfUUIDs_relacionados]</p></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    `,
  });
  //Datos retenciones
  editor.BlockManager.add('Rretenciones', {
    label: 'Retenciones',
    category: 'Comp. Factura Retencion',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        display: block;
        background-color: #d7c4ce;
        font-weight: bold;
        text-align: center;
        padding: 0px;
        border: 1px solid #dee2e6;
      }
      .encabezado-tabla{
        background-color: #d7c4ce;          
        text-align: center;
      }
      .etiqueta-encabezado{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 12px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .etiqueta{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        display: block;
        word-wrap: break-word;     /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        white-space: normal;   /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
        }
      .renglon {
          border: 1px solid #dee2e6;
      }
      .espacio-horizontal{
        height: 30px;
      }
      .espacio-vertical {
        width: 30px;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        vertical-align: top; 
      }
    </style>
    <div class="row">
      <div class="col-12 ">
        <table class="table table-sm table-bordered">
          <thead class="encabezado-tabla">
            <tr>
              <th colspan="6">Retenciones</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <th class="col-3"><p class="etiqueta">Clave Retención:</p></th>
              <th class="col"><p class="etiqueta">Descripción:</p></th>
            </tr>
            <tr>
              <td><p class="dato">[fCveRetencion]</p></td>
              <td><p class="dato">[fDescRetencion]</p></td>      
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    `,
  });
  //Datos Total de retenciones e impuestos
  editor.BlockManager.add('RtotalRetenciones', {
    label: 'Total de retenciones e impuestos',
    category: 'Comp. Factura Retencion',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        display: block;
        background-color: #d7c4ce;
        font-weight: bold;
        text-align: center;
        padding: 0px;
        border: 1px solid #dee2e6;
      }
      .encabezado-tabla{
        background-color: #d7c4ce;          
        text-align: center;
      }
      .etiqueta-encabezado{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 12px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .etiqueta{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        display: block;
        word-wrap: break-word;     /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        white-space: normal;   /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
        }
      .renglon {
          border: 1px solid #dee2e6;
      }
      .espacio-horizontal{
        height: 30px;
      }
      .espacio-vertical {
        width: 30px;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        vertical-align: top; 
      }
    </style>
    <div class="row d-flex justify-content-between">
      <div class="col-2">
          <img src="https://via.placeholder.com/150" id="QR" alt="Logo" class="img-fluid" style="Border: 1px solid black; width: 147px; height: 110px;"/>
      </div>
      <div class="col-7">
        <table class="table table-sm table-bordered">
          <thead class="encabezado-tabla">
            <tr>
              <th colspan="8">Total de las retenciones</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <th scope="col"><p class="etiqueta">Base</p></th>
              <th scope="col"><p class="etiqueta">Impuesto</p></th>
              <th scope="col"><p class="etiqueta">Monto</p></th>
              <th scope="col"><p class="etiqueta">Tipo de pago</p></th>
            </tr>
            
            <tr>
              <td><p class="dato">[trBase]</p></td>
              <td><p class="dato">[trImpuesto]</p></td>
              <td><p class="dato">[trMonto]</p></td>
              <td><p class="dato">[trTipoPago]</p></td>
            </tr>
            
          </tbody>
        </table>
      </div>

      <div class="col-3">
        <div class="row">
          <div class="col-12">
            <table class="table table-sm table-bordered">
              <tbody>
                <tr>
                  <th><p class="etiqueta">Total operaciones:</p></th>
                  <td><p class="dato">[trTotal_Operacion]</p></td>
                </tr>
                <tr>
                  <th><p class="etiqueta">Total gravado:</p></th>
                  <td><p class="dato">[trTotal_Grav]</p></td>
                </tr>
                <tr>
                  <th><p class="etiqueta">Total exento:</p></th>
                  <td><p class="dato">[trTotal_Exent]</p></td>
                </tr>
                <tr>
                  <th><p class="etiqueta">Total retenciones:</p></th>
                  <td><p class="dato">[trTotal_Renten]</p></td>
                </tr>
                <tr>
                  <th><p class="etiqueta">Utilidad bimestral:</p></th>
                  <td><p class="dato">[trUtilidadBimestral]</p></td>
                </tr>
                <tr>
                  <th><p class="etiqueta">ISR:</p></th>
                  <td><p class="dato">[trISR]</p></td>
                </tr>
            </table>
          </div>
        </div>
      </div>
    </div>

    `,
  });
  //Datos sellos
  editor.BlockManager.add('Rsellos', {
    label: 'Sellos',
    category: 'Comp. Factura Retencion',
    attributes: { class: '' },
    content: `
    <style>
      .encabezado-resaltado{
        display: block;
        background-color: #d7c4ce;
        font-weight: bold;
        text-align: center;
        padding: 0px;
        border: 1px solid #dee2e6;
      }
      .encabezado-tabla{
        background-color: #d7c4ce;          
        text-align: center;
      }
      .etiqueta-encabezado{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 12px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .etiqueta{
        display: block;
        font-family: 'Arial', sans-serif; 
        font-size: 11px; 
        font-weight: bold;
        margin:0%;
        padding:0%;
      }
      .dato{
        display: block;
        word-wrap: break-word;     /* Esto permite que el texto largo se ajuste */
        overflow-wrap: break-word; /* Asegura que las palabras largas no se desborden */
        white-space: normal;   /* Establece que el texto no se ajuste a la línea */
        font-family: 'Arial', sans-serif;
        font-size: 10px; 
        margin:0%;
        padding:0%;
        }
      .renglon {
          border: 1px solid #dee2e6;
      }
      .espacio-horizontal{
        height: 30px;
      }
      .espacio-vertical {
        width: 30px;
      }
      .textox {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
      }
      .table th, .table td {
        padding: 0px;
        height: auto !important;
        vertical-align: top; 
      }
    </style>
    <div class="row">
      <div class="col-12">
        <div class="row">
          <div class="col-12 encabezado-resaltado">Cadena original del complemento de certificación del SAT</div>
        </div>
        <div class="row">
          <div class="col-12 "><p class="dato renglon">[fCertificado_SAT]</p></div>
        </div>
        <div class="row">
          <div class="col-12 encabezado-resaltado">SELLO DIGITAL DEL SAT</div>
        </div>
        <div class="row">
          <div class="col-12 "><p class="dato renglon">[fSello_SAT]</p></div>
        </div>
        <div class="row">
          <div class="col-12 encabezado-resaltado">SELLO DIGITAL DEL CONTRIBUYENTE QUE LO EXPIDE</div>
        </div>
        <div class="row">
          <div class="col-12 "><p class="dato renglon">[nSello_digital_contribuyente]</p></div>
        </div>
      </div>
    </div>
    `,
  });

  //################## Componentes simples #####################
  //texto para datos de entrada
  editor.BlockManager.add('datoEntrada', {
    label: 'Texto para datos de entrada',
    category: 'Complementos',
    attributes: { class: '' },
    content: `
      <style>
              
      </style>
      <p class="dato">escribe aquí el texto</p>
              `,
  });
  //texto parra etiquetas
  editor.BlockManager.add('etiqueta', {
    label: 'Texto para etiqueta',
    category: 'Complementos',
    attributes: { class: '' },
    content: `
      <style>
              
      </style>
      <p class="etiqueta">etiqueta</p>
              `,
  });
  editor.BlockManager.add('Imagen', {
    label: 'Imagen',
    category: 'Complementos',
    attributes: { class: '' },
    select: true,
    content: { type: 'image' },
    activate: true,
  });//Separador Horizontal
  editor.BlockManager.add('separedorH', {
    label: 'Separador horizontal',
    category: 'Complementos',
    attributes: { class: '' },
    content: `
      <style>
      
      </style>
      <div class="row">
        <div class="col-12 espacio-horizontal"></div>
      </div>
    `,
  });//Separador Vertical
  editor.BlockManager.add('separedorV', {
    label: 'Separador vertical',
    category: 'Complementos',
    attributes: { class: '' },
    content: `
      <style>
      
      </style>
      <div class="row">
        <div class="col-12 espacio-vertical"></div>
      </div>
    `,
  });
  

});


// FUNCION PARA REMPLAZAR CORCHETES [] EN EL HTML POR {{VALOR}}
function RemplazarCorchetesLLaves(CFDI) {
  let html = editor.getHtml();
  let css = editor.getCss();
  // Expresión regular para encontrar valores entre corchetes []
  let updatedHtml = html.replace(/\[([^\]]+)\]/g, (match, key) => {
      let value = EncontrarValorEnCFDI(CFDI, key);
      return `{{ ${value} }}`;
  });
  editor.setComponents(updatedHtml);
  editor.setStyle(css);
}
// FUNCION PARA BUSCAR EL VALOR EN EL OBJETO CFDI
function EncontrarValorEnCFDI(CFDI, key) {
  for (let section in CFDI) {
      if (Array.isArray(CFDI[section])) {
          // Buscar en cada elemento del array
          for (let index = 0; index < CFDI[section].length; index++) {
              if (key in CFDI[section][index]) {
                  return `${section}.${key}`;
              }
          }
      } else if (typeof CFDI[section] === "object") {
          if (key in CFDI[section]) {
              return `CFDI.${section}.${key}`;
          }
      }
  }
  return key;
}
// FUNCION PARA REMPLAZAR {{ VALOR }} POR CORCHETES [VALOR]
function RemplanzarLlavesConCorchetes() {
  let html = editor.getHtml();
  let css = editor.getCss();

  // EXPRECIÓN REGULARA PARA `{{ CFDI.section[index].key }}` o `{{ conceptoS.key }}`
  let updatedHtml = html.replace(/{{\s*(CFDI\.[\w\[\].]+|conceptos\.[\w]+)\s*}}/g, (match, key) => {
      let parts = key.split('.');
      let lastPart = parts.pop(); // ULTINE LA ÚLTIMA PARTE
      if (parts[0] === 'concepto') {
          return `[${lastPart}]`;
      }
      let section = parts.join('.'); 
      if (section.match(/\[\d+\]$/)) {
          return `[${lastPart}]`;
      }

      return `[${lastPart}]`;
  });
  // Volver a cargar el HTML en el editor
  editor.setComponents(updatedHtml);
  editor.setStyle(css);
}
// Guardar plantilla o modifica la plantilla
function savePlantilla(e){
  e.preventDefault();
  //que botón se presionó
  const action = document.activeElement.value;
  let id = pageId;
  let formData = new FormData();
  let modeloId = document.getElementById("modeloSelect").value;
  let nombre = document.getElementById("modeloSelect").options[document.getElementById("modeloSelect").selectedIndex].text;

  // Validar que el usuario haya seleccionado un modelo
  if (!modeloId || modeloId === "0") {
    showAlert("warning", "Debes seleccionar un CFDI antes de hacer algo.");
    return;
  }else{
    RemplazarCorchetesLLaves(factura);
    let confirmacion;
    switch (action) {
      case 'save':
          confirmacion = confirm("¿Estás seguro de que deseas guardar los cambios en " + nombre + "?");
          if (confirmacion) {
            // Obtener el HTML y CSS del editor
            let htmlContent = editor.getHtml();
            let cssContent = editor.getCss();

            // Convertir a bytes usando Blob
            let htmlSize = new Blob([htmlContent]).size;
            let cssSize = new Blob([cssContent]).size;
            let totalSize = htmlSize + cssSize;

            // Límite de 2.5MB (2,621,440 bytes)
            let maxSize = 2.5 * 1024 * 1024;

            if (totalSize > maxSize) {
              showAlert("danger", `El tamaño de la imagen es demasiado grande`);
              break;
            }
            formData.append('modelo', modeloId);
            formData.append('html', editor.getHtml());
            formData.append('css', editor.getCss());
            console.log('----------------------TERMINA-----------------');
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const request = new Request(
            'save/',
              {
                  method: 'POST',
                  headers: {'X-CSRFToken': csrftoken},
                  mode: 'same-origin',
                  body: formData
              }
            );
            fetch(request).then((resp)=>resp.json()).then((response)=>{
              console.log(response)
              alert(nombre+' guardado correctamente')
            }).catch((error)=>{
              console.log(error)
              alert('Error'+url)
            })
          }
          break;

      case 'saveas':
          let modal = new bootstrap.Modal(document.getElementById("GuardarComo"));
          modal.show();
          break;

      case 'delete':
          confirmacion = confirm("¿Estás seguro que deseas eliminar el contenido de "+nombre+" ?");
          if (confirmacion) {
            // Obtener el HTML y CSS del editor
            let htmlContent = editor.getHtml();
            let cssContent = editor.getCss();

            // Convertir a bytes usando Blob
            let htmlSize = new Blob([htmlContent]).size;
            let cssSize = new Blob([cssContent]).size;
            let totalSize = htmlSize + cssSize;

            // Límite de 2.5MB (2,621,440 bytes)
            let maxSize = 2.5 * 1024 * 1024;

            if (totalSize > maxSize) {
              showAlert("danger", `El tamaño de la imagen es demasiado grande`);
              break;
            }
            formData.append('modelo', modeloId);
            formData.append('html', "<body></body>");
            formData.append('css', "");    
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const request = new Request(
            'save/',
              {
                  method: 'POST',
                  headers: {'X-CSRFToken': csrftoken},
                  mode: 'same-origin',
                  body: formData
              }
            );
            fetch(request).then((resp)=>resp.json()).then((response)=>{
              console.log(response)
              alert('Contenido borrado exitosamente de'+nombre)
            }).catch((error)=>{
              console.log(error)
              alert('Error'+url)
            })
            editor.setComponents("");
            editor.setStyle("");
          }
          break;

      case 'erase':
          confirmacion = confirm("¿Estás seguro que deseas eliminar " + nombre + "?");
          if (confirmacion) {
            formData.append('modelo', modeloId);  
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const request = new Request(
            'drop/',
              {
                  method: 'POST',
                  headers: {'X-CSRFToken': csrftoken},
                  mode: 'same-origin',
                  body: formData
              }
            );
            fetch(request)
            .then(resp => resp.json())
            .then(response => {
                console.log(response);
                if (response.success) {
                    alert(nombre+' eliminada correctamente');

                    // Eliminar del DOM la opción correspondiente en el select
                    const optionToRemove = document.querySelector(`#modeloSelect option[value='${modeloId}']`);
                    if (optionToRemove) optionToRemove.remove();

                    // Limpiar el editor solo si se eliminó exitosamente
                    editor.setComponents("");
                    editor.setStyle("");
                } else {
                    alert(`Error: ${response.error}`);
                }
            })
            .catch(error => {
                console.error(error);
                alert('Ocurrió un error al eliminar el CFDI.');
            });
          }
          break;

      default:
          console.warn('Acción no reconocida');
          break;
  }
    
  }
  RemplanzarLlavesConCorchetes();
}
//evalua que plantilla esta seleccionada y carga los datos (html y css) en el editor
function handleModeloSelect() {
  let select = document.getElementById("modeloSelect");
  let selectedValue = select.value;

  if (selectedValue === "0") {
    // Limpiar el editor si el usuario selecciona la opción por defecto
    editor.setComponents("");  // Elimina el contenido HTML
    editor.setStyle("");       // Elimina los estilos CSS
    pageId = null;             // Indicar que no hay plantilla cargada
    return; 
  }
  if (selectedValue === "nuevo") {
      // Mostrar el modal de Bootstrap
      let modal = new bootstrap.Modal(document.getElementById("NuevaPlantilla"));
      modal.show();
  } else if (selectedValue) {
      // Si se selecciona un modelo existente, cargar la plantilla
      fetch(`get-plantilla/${selectedValue}`)
          .then(response => response.json())
          .then(data => {
              if (data.exists) {
                  editor.setComponents(data.html);
                  editor.setStyle(data.css);
                  pageId = data.id; // Guardar el ID para futuras modificaciones
                  RemplanzarLlavesConCorchetes();
              } else {
                  editor.setComponents(""); // Dejar vacío si no hay plantilla
                  editor.setStyle("");
                  pageId = null;  // Indica que es una nueva plantilla
              }
          })
          .catch(error => console.error("Error cargando plantilla:", error));
  }
}
//funcion para confirmar el nombre de la nueva plantilla
function GuardarPlantilla() {
  let nombreModelo = document.getElementById("nuevoCFDI").value.trim();

  if (!nombreModelo) {
      alert("Por favor, ingrese un nombre válido.");
      return;
  }

  fetch("crear-modelo/", {
      method: "POST",
      headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
      },
      body: JSON.stringify({ name: nombreModelo })
  })
  .then(response => response.json())
  .then(data => {
      if (data.success) {
          let select = document.getElementById("modeloSelect");
          let newOption = document.createElement("option");
          newOption.value = data.id;
          newOption.textContent = data.name;

          let optionNuevo = select.querySelector("option[value='nuevo']");
          select.insertBefore(newOption, optionNuevo);

          // Selecciona automáticamente el nuevo modelo
          select.value = data.id;
          editor.setComponents("");
          editor.setStyle("");
          // Cerrar el modal de Bootstrap
          let modal = bootstrap.Modal.getInstance(document.getElementById("NuevaPlantilla"));
          modal.hide();

          // Mostrar alerta de éxito de Bootstrap
          let alertContainer = document.getElementById("alertContainer");
          alertContainer.innerHTML = `
              <div id="successAlert" class="alert alert-success alert-dismissible fade show" role="alert">
                  El modelo <strong>${data.name}</strong> ha sido creado exitosamente.
                  <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Cerrar"></button>
              </div>
          `;
          // Limpiar el campo después de usarlo
          document.getElementById("nuevoCFDI").value = "";
          // Eliminar la alerta después de 3 segundos
          setTimeout(() => {
            let successAlert = document.getElementById("successAlert");
            if (successAlert) {
                successAlert.remove();
            }
        }, 3000);
      } else {
          alert("Error: " + data.error);
      }
  })
  .catch(error => {
      console.error("Error:", error);
      // Limpiar el campo después de usarlo
      document.getElementById("nuevoCFDI").value = "";
      alert("Ocurrió un error al crear el modelo");
  });
}
//funcion para confirmar el nombre de la plantilla a guardar como
async function GuardarPlantillaComo(e) {
  e.preventDefault();
  
  let nombreModelo = document.getElementById("guardarCFDI").value.trim();
  if (!nombreModelo) {
      alert("Por favor, ingrese un nombre válido.");
      return;
  }
  
  
  if (!confirm("¿Estás seguro de que deseas guardar los cambios en "+nombreModelo+"?")) return;
  RemplazarCorchetesLLaves(factura);
  let formData = new FormData();
  formData.append('modelo', nombreModelo);
  formData.append('html', editor.getHtml());
  formData.append('css', editor.getCss());

  const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

  try {
      let response = await fetch('saveas/', {
          method: 'POST',
          headers: { 'X-CSRFToken': csrftoken },
          mode: 'same-origin',
          body: formData
      });
      let data = await response.json();

      if (data.success) {
          RemplanzarLlavesConCorchetes();
          let select = document.getElementById("modeloSelect");
          let newOption = document.createElement("option");
          newOption.value = data.id;
          newOption.textContent = data.name;
          
          let optionNuevo = select.querySelector("option[value='nuevo']");
          select.insertBefore(newOption, optionNuevo);

          // Selecciona automáticamente el nuevo modelo
          select.value = data.id;
          

          // Cerrar el modal solo si existe
          const modalElement = document.getElementById("GuardarComo");
          if (modalElement) {
              const modalInstance = bootstrap.Modal.getInstance(modalElement) || new bootstrap.Modal(modalElement);
              modalInstance.hide();
          }

          // Mostrar alerta de éxito
          document.getElementById("alertContainer").innerHTML = `
              <div  id="successAlert"class="alert alert-success alert-dismissible fade show" role="alert">
                  El modelo <strong>${nombreModelo}</strong> ha sido guardado exitosamente.
                  <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Cerrar"></button>
              </div>
          `;
          // Limpiar el campo después de usarlo
          document.getElementById("guardarCFDI").value = "";
          // Eliminar la alerta después de 3 segundos
          setTimeout(() => {
            let successAlert = document.getElementById("successAlert");
            if (successAlert) {
                successAlert.remove();
            }
        }, 3000);
      } else {
          alert("Error: " + data.error);
      }

  } catch (error) {
      console.error("Error:", error);
      // Limpiar el campo después de usarlo
      document.getElementById("guardarCFDI").value = "";
      alert("Ocurrió un error al guardar la plantilla en otro modelo.");
  }
}

//funcion para mostrar la alerta
function showAlert(type, message) {
  let alertContainer = document.getElementById("alertContainer");

  // Crear la alerta con clases de Bootstrap
  let alertDiv = document.createElement("div");
  alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
  alertDiv.role = "alert";
  alertDiv.innerHTML = `
      ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
  `;

  // Agregar la alerta al contenedor
  alertContainer.appendChild(alertDiv);

  // Ocultar la alerta después de 4 segundos
  setTimeout(() => {
      alertDiv.classList.remove("show");
      alertDiv.classList.add("fade");
      setTimeout(() => alertDiv.remove(), 500);
  }, 4000);
}






