from decimal import Decimal
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ValidationError
from cfdi.models import FacturaElectronica, InformacionFiscal, ComprobanteEmitido
from ..serializers import ElectronicInvoiceSerializer, FiscalInformationSerializer
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
import base64
from app.views import SoapService
from satcfdi.create.cfd import cfdi40
from satcfdi.models import Signer
from satcfdi.create.cfd import cfdi40
from decouple import config


class ElectronicInvoiceViewSet(viewsets.ModelViewSet):
    queryset = FacturaElectronica.objects.all()
    serializer_class = ElectronicInvoiceSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_superuser:
            return qs
        return qs.filter(user=self.request.user)

    @action(detail=True, methods=['get'])
    def informacion_fiscal(self, request, pk=None):
        info_fiscal_id = request.GET.get('info_fiscal_id')
        if info_fiscal_id:
            info_fiscal = get_object_or_404(InformacionFiscal, pk=info_fiscal_id)
            serializer = FiscalInformationSerializer(info_fiscal)
            return Response(serializer.data)
        return Response({"error": "ID no proporcionado"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def facturar_y_timbrar(self, request, pk=None):
        s=self
        factura = self.get_object()
        try:
            # timbra xml
            comprobante = obtener_datos_factura(self, request, factura.id)
            xml_content = comprobante.process()
            xml_content = comprobante.xml_bytes(pretty_print=True, validate=True).decode("utf-8")

            # Convertir el XML a Base64
            xml_base64 = base64.b64encode(xml_content.encode("utf-8")).decode("utf-8")

            estado = SoapService.stamp('', xml_base64, config('PAC_USER'), config('PAC_PASSWORD'))

            if not estado.Incidencias:
                estatus = estado.CodEstatus
            else:
                estatus = estado.Incidencias[0].MensajeIncidencia

            # Extraer datos necesarios
            tipo_comprobante = factura.tipos_comprobantes.first()
            comprobante_relacionado = factura.Comprobante_relacionados.first()
            receptor = factura.receptores.first()
            informacion_pago = factura.InformacionPago.first()
            concepto = factura.Conceptos.first()

            if not (tipo_comprobante and comprobante_relacionado and receptor and informacion_pago and concepto):
                raise ValidationError("Faltan datos necesarios para generar el comprobante.")

            # Obtener el estado basado en MetodoPago y FormaPago
            estado = []

            # MetodoPago
            metodo_pago = informacion_pago.Metodopago
            if metodo_pago:
                metodo_pago_clave = getattr(metodo_pago, 'c_MetodoPago', str(metodo_pago))
                if metodo_pago_clave == "PPD":
                    estado.append("PPD ")
                elif metodo_pago_clave == "PUE":
                    estado.append("PUE")
                else:
                    estado.append("Desconocido")

            # FormaPago
            forma_pago = informacion_pago.Formapago
            if forma_pago:
                forma_pago_clave = getattr(forma_pago, 'c_FormaPago', str(forma_pago))
                forma_pago_mapping = {
                    "1": "Efectivo", "2": "Cheque nominativo", "3": "Transferencia electrónica de fondos",
                    "4": "Tarjeta de crédito", "5": "Monedero electrónico", "6": "Dinero electrónico",
                    "8": "Vales de despensa", "12": "Dación de pago", "13": "Pago por subrogación",
                    "14": "Pago por consignación", "15": "Condonación", "17": "Compensación",
                    "23": "Novación", "24": "Confusión", "25": "Remisión de deuda",
                    "26": "Prescripción o caducidad", "27": "A satisfacción del acreedor",
                    "28": "Tarjeta de débito", "29": "Tarjeta de servicios", "30": "Aplicación de anticipos",
                    "31": "Intermediario de pagos", "99": "Por definir"
                }
                estado.append(forma_pago_mapping.get(forma_pago_clave, estatus))

            if tipo_comprobante and tipo_comprobante.version_cfdi:
                estado.append(f"CFDI 4.0")
            else:
                estado.append("Versión CFDI desconocida")

            # Concatenar el estado
            estado = " - ".join(estado)
            estado += " - Factura Electrónica"

            # Crear el objeto ComprobanteEmitido
            ComprobanteEmitido.objects.create(
                user=request.user,
                fecha=now(),
                folio=tipo_comprobante.c_TipoDeComprobante,
                uuid=comprobante_relacionado.uuid,
                rfc=receptor.Rfc,
                nombre=factura.nombre,
                fecha_pago=informacion_pago.Fechapago,
                total=concepto.total,
                estado=estado
            )
            return Response({"message": "El comprobante fue generado exitosamente."})
        except ValidationError as e:
            return Response({"error": str(e)+"; "+str(s)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)+"; "+str(s)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def get_pdf(self, request, pk=None):
        factura = self.get_object()
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Factura_{factura.id}.pdf"'

        # Configurar el lienzo
        p = canvas.Canvas(response, pagesize=letter)

        # Colores y estilos
        main_color = HexColor("#003366")  # Azul oscuro
        section_color = HexColor("#CCCCCC")  # Gris claro para las secciones
        text_color = HexColor("#333333")  # Gris oscuro

        # Encabezado con logotipo
        image_path = "https://drive.google.com/uc?export=download&id=1cFL55JapvRDGrVzwhZYoXM1SnvvFV3Hd"
        try:
            p.drawImage(image_path, 40, 720, width=80, height=80)  # Logotipo
        except:
            p.setFillColor(main_color)
            p.drawString(50, 760, "LOGO")

        # Encabezado Principal
        p.setFont("Helvetica-Bold", 14)
        p.setFillColor(main_color)
        p.drawString(150, 770, "FACTURA ELECTRÓNICA")
        p.setFont("Helvetica", 10)
        p.setFillColor(text_color)
        p.drawString(150, 755, f"Recibo de Honorarios: {factura.nombre}")
        p.drawString(150, 740, f"RFC: {factura.rfc}")
        p.drawString(150, 725, f"Fecha de Creación: {factura.fecha_creacion.strftime('%Y-%m-%d')}")

        # Información General
        p.setFillColor(section_color)
        p.rect(40, 700, 520, 20, fill=1, stroke=0)
        p.setFillColor(colors.black)
        p.setFont("Helvetica-Bold", 10)
        p.drawString(50, 707, "Información General")
        p.setFont("Helvetica", 9)
        p.setFillColor(text_color)
        p.drawString(50, 690, f"Descripción: {factura.descripcion}")
        p.drawString(50, 675, f"Código Postal: {factura.codigo_postal}")
        p.drawString(50, 660, f"Régimen Fiscal: {factura.regimen_fiscal}")

        # Sección de Conceptos
        p.setFillColor(section_color)
        p.rect(40, 630, 520, 20, fill=1, stroke=0)
        p.setFillColor(colors.black)
        p.setFont("Helvetica-Bold", 10)
        p.drawString(50, 637, "Detalles de Conceptos")
        p.setFont("Helvetica", 9)
        y_position = 620
        for concepto in factura.Conceptos.all():
            p.setFillColor(text_color)
            p.drawString(50, y_position, f"Descripcion: {concepto.descripcion}")
            y_position -= 15
            p.drawString(50, y_position, f"Cantidad: {concepto.cantidad}        Subtotal: ${concepto.valor_unitario}        Total:${concepto.importe}")
            y_position -= 15

        # Sección de Receptores
        p.setFillColor(section_color)
        p.rect(40, y_position - 10, 520, 20, fill=1, stroke=0)
        p.setFillColor(colors.black)
        p.setFont("Helvetica-Bold", 10)
        p.drawString(50, y_position - 3, "Receptores")
        y_position -= 25
        p.setFont("Helvetica", 9)

        for receptor in factura.receptores.all():
            p.setFillColor(text_color)
            p.drawString(50, y_position, f"RFC: {receptor.Rfc}, Razón Social: {receptor.Razon_social}")
            y_position -= 15
            #agrega el Usocfi
            p.drawString(50, y_position, f"Uso de cfdi: {receptor.Usocfdi}")
            y_position -= 15

            p.drawString(50, y_position, f"Régimen Fiscal: {receptor.Regimen_fiscal}, Registro Tributario: {receptor.Registrotributario}")
            y_position -= 15
            p.drawString(50, y_position, f"Nombre Completo: {receptor.Nombre} {receptor.Apellido_paterno} {receptor.Apellido_materno}")
            y_position -= 15
            p.drawString(50, y_position, f"Teléfono: {receptor.Telefono}, Correo: {receptor.Correo_electronico}")
            y_position -= 15
            p.drawString(50, y_position, f"Domicilio: {receptor.Calle} {receptor.Numero_exterior}, {receptor.Numero_interior}, {receptor.Colonia}")
            y_position -= 15
            p.drawString(50, y_position, f"Ciudad: {receptor.Ciudad}, Municipio: {receptor.Municipio}, Estado: {receptor.Estado}")
            y_position -= 15
            p.drawString(50, y_position, f"País: {receptor.Pais}, Código Postal: {receptor.Codigo_postal}")
            y_position -= 15
            p.drawString(50, y_position, f"Referencia: {receptor.Referencia}, Clave País: {receptor.Clave_pais}")
            y_position -= 15
            p.drawString(50, y_position, f"Residencia Fiscal: {receptor.Residencia_fiscal}")
            y_position -= 25  # Espacio adicional entre receptores

        # Total
        p.setFillColor(section_color)
        p.rect(400, y_position - 10, 160, 20, fill=1, stroke=0)
        p.setFillColor(colors.black)
        p.setFont("Helvetica-Bold", 10)
        p.drawString(410, y_position - 3, f"TOTAL: ${sum(concepto.importe for concepto in factura.Conceptos.all()):.2f}")

        # Finalizar PDF
        p.showPage()
        p.save()

        return response

    @action(detail=True, methods=['post'])
    def save_draft(self, request, pk=None):
        factura = self.get_object()
        try:
            # Verificar si ya existe un borrador para este objeto
            borrador, created = FacturaElectronicaBorrador.objects.get_or_create(
                informacion_fiscal=factura.informacion_fiscal,
                defaults={
                    'nombre': factura.nombre,
                    'rfc': factura.rfc,
                    'descripcion': factura.descripcion,
                    'codigo_postal': factura.codigo_postal,
                    'activo': False,  # El borrador no está activo por defecto
                    'regimen_fiscal': factura.regimen_fiscal,
                    'fecha_creacion': None,  # Fecha en blanco para el borrador
                }
            )

            if not created:  # Si ya existía un borrador, actualízalo
                borrador.nombre = factura.nombre
                borrador.rfc = factura.rfc
                borrador.descripcion = factura.descripcion
                borrador.codigo_postal = factura.codigo_postal
                borrador.regimen_fiscal = factura.regimen_fiscal
                borrador.save()

            # Copiar relación de tipos_comprobantes al borrador
            # borrador.tipos_comprobantes_Borrador.all().delete()  # Limpiar relaciones previas
            # for tipo in factura.tipos_comprobantes.all():
            #     TipoComprobante.objects.create(
            #         FacturaElectronicaBorrador=borrador,
            #         descripcion=tipo.descripcion,
            #         c_TipoDeComprobante=tipo.c_TipoDeComprobante,
            #         valor_maximo=tipo.valor_maximo,
            #         fecha_inicio_vigencia=tipo.fecha_inicio_vigencia,
            #         fecha_fin_vigencia=tipo.fecha_fin_vigencia,
            #     )

            # Copiar relación de conceptos al borrador
            borrador.ConceptosBorrador.all().delete()  # Limpiar conceptos previos
            for concepto in factura.Conceptos.all():
                borrador.ConceptosBorrador.create(
                    descripcion=concepto.descripcion,
                    cantidad=concepto.cantidad,
                    valor_unitario=concepto.valor_unitario,
                    importe=concepto.importe,
                    objetoimpuesto=concepto.objetoimpuesto,
                    identificador=concepto.identificador,
                    unidad=concepto.unidad,
                    impuesto=concepto.impuesto,
                    claveprodserv=concepto.claveprodserv,
                    clave_producto=concepto.clave_producto,
                    identificacion_sat=concepto.identificacion_sat,
                    clave_unidad=concepto.clave_unidad,
                    nombre_unidad_sat=concepto.nombre_unidad_sat,
                    notas=concepto.notas,
                    total=concepto.total,
                )

            # Copiar relación de información global al borrador
            borrador.informacion_global_Borrador.all().delete()  # Limpiar conceptos previos
            for informacionglobal in factura.Informacion_global.all():  # Usar el related_name correcto
                borrador.informacion_global_Borrador.create(
                    Escomprobantelegal=informacionglobal.Escomprobantelegal,
                    Periodicidad=informacionglobal.Periodicidad,
                    Meses=informacionglobal.Meses,
                    Anio=informacionglobal.Anio,
                )

            # Copiar relación de información de pago al borrador
            borrador.InformacionPagoBorrador.all().delete()  # Limpiar conceptos previos
            for informacion_pago in factura.InformacionPago.all():  # Usar el related_name correcto
                borrador.InformacionPagoBorrador.create(
                    Metodopago=informacion_pago.Metodopago,
                    Formapago=informacion_pago.Formapago,
                    Fechapago=informacion_pago.Fechapago,
                    Moneda=informacion_pago.Moneda,
                    Tipocambio=informacion_pago.Tipocambio,
                    Condicionespago=informacion_pago.Condicionespago,
                )

            # Copiar relación de emisor al borrador
            borrador.Emisor_Borrador.all().delete()
            for emisor in factura.Emisor.all():
                borrador.Emisor_Borrador.create(
                    regimen_fiscal=emisor.regimen_fiscal,
                    Factura_adquiriente=emisor.Factura_adquiriente,
                    pdf=emisor.pdf,
                )

            # Copiar relación de comprobantes relacionados al borrador
            borrador.Comprobante_relacionados_Borrador.all().delete()  # Limpiar conceptos previos
            for comprobanterelacionados in factura.Comprobante_relacionados.all():
                borrador.Comprobante_relacionados_Borrador.create(
                    Tiporelacion=comprobanterelacionados.Tiporelacion,
                    uuid=comprobanterelacionados.uuid,
                )

            # Copiar relación de receptores al borrador
            borrador.receptores_borrador.all().delete()
            for receptors in factura.receptores.all():
                borrador.receptores_borrador.create(
                    Usocfdi=receptors.Usocfdi,
                    Ignorar_validacion_sociedad=receptors.Ignorar_validacion_sociedad,
                    Mostrardireccionpdf=receptors.Mostrardireccionpdf,
                    Rfc=receptors.Rfc,
                    Razon_social=receptors.Razon_social,
                    Registrotributario=receptors.Registrotributario,
                    Nombre=receptors.Nombre,
                    Apellido_paterno=receptors.Apellido_paterno,
                    Apellido_materno=receptors.Apellido_materno,
                    Telefono=receptors.Telefono,
                    Correo_electronico=receptors.Correo_electronico,
                    Calle=receptors.Calle,
                    Numero_exterior=receptors.Numero_exterior,
                    Numero_interior=receptors.Numero_interior,
                    Colonia=receptors.Colonia,
                    Ciudad=receptors.Ciudad,
                    Municipio=receptors.Municipio,
                    Estado=receptors.Estado,
                    Pais=receptors.Pais,
                    Codigo_postal=receptors.Codigo_postal,
                    Referencia=receptors.Referencia,
                    Clave_pais=receptors.Clave_pais,
                    Residencia_fiscal=receptors.Residencia_fiscal,
                )

            # Copiar relación de leyendas fiscales al borrador
            borrador.LeyendasFiscalesBorrador.all().delete()
            for leyendas_fiscales in factura.LeyendasFiscales.all():
                borrador.LeyendasFiscalesBorrador.create(
                    TextoLeyenda=leyendas_fiscales.TextoLeyenda,
                    Disposicionfiscal=leyendas_fiscales.Disposicionfiscal,
                    Norma=leyendas_fiscales.Norma,
                )

            return Response({"message": "El borrador de la factura se guardó correctamente."})
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def save_model(self, request, pk=None):
        factura = self.get_object()
        try:
            if not factura.rfc or len(factura.rfc) not in [12, 13]:
                raise ValidationError("El RFC del emisor debe tener 12 caracteres para personas morales y 13 para personas físicas.")
            if not factura.codigo_postal:
                raise ValidationError("El código postal es obligatorio.")
            if not factura.regimen_fiscal:
                raise ValidationError("El régimen fiscal es obligatorio para el emisor.")

            if not factura.pk:
                factura.user = request.user

                informacion_principal = InformacionFiscal.objects.filter(es_principal=True).first()
                if informacion_principal:
                    factura.informacion_fiscal = informacion_principal

            factura.save()
            return Response({"message": "El modelo se guardó correctamente."})
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def get_tipos_comprobantes_detallados(self, request, pk=None):
        factura = self.get_object()
        if factura.tipos_comprobantes.exists():
            detalles = [
                f"<strong>{tipo.descripcion}</strong> (Clave: {tipo.c_TipoDeComprobante}, "
                f"Valor Máximo: {tipo.valor_maximo}, "
                f"Vigencia: {tipo.fecha_inicio_vigencia} - {tipo.fecha_fin_vigencia or 'Indefinido'})"
                for tipo in factura.tipos_comprobantes.all()
            ]
            return Response({"detalles": "<br>".join(detalles)})
        return Response({"detalles": "No hay tipos de comprobantes asociados"})
    

def obtener_datos_factura(self, request, pk):
    # Obtener la factura
    factura = self.get_object()
    if not factura:
        self.message_user(request, "Factura no encontrada.", level="error")
        return redirect("..")

    # Obtener el receptor asociado
    receptor_model = factura.receptores.first()  # Usar el primer receptor asociado
    if not receptor_model:
        self.message_user(request, "No se encontró un receptor asociado a la factura.", level="error")
        return redirect("..")
    
    # Obtener la información de pago asociada
    formaPago_model = factura.InformacionPago.first()  # Usar la primera información de pago asociada
    if not formaPago_model:
        self.message_user(request, "No se encontró información de pago asociada a la factura.", level="error")
        return redirect("..")

    # Obtener el régimen fiscal del receptor
    regimen_fiscal_receptor = receptor_model.Regimen_fiscal.first()
    if not regimen_fiscal_receptor:
        self.message_user(request, "El receptor no tiene un régimen fiscal asociado.", level="error")
        return redirect("..")

    # Crear objeto Receptor
    receptor = cfdi40.Receptor(
        rfc=receptor_model.Rfc,
        nombre=receptor_model.Razon_social,
        uso_cfdi=receptor_model.Usocfdi.c_UsoCFDI,
        domicilio_fiscal_receptor=receptor_model.Codigo_postal,
        regimen_fiscal_receptor=regimen_fiscal_receptor.c_RegimenFiscal,
    )

    # Obtener datos del emisor
    informacion_fiscal = factura.informacion_fiscal
    if not informacion_fiscal:
        self.message_user(request, "No se encontró información fiscal asociada a la factura.", level="error")
        return redirect("..")

    certificado = informacion_fiscal.user.certificados.first()
    if not certificado:
        self.message_user(request, "No se encontró un certificado asociado al usuario.", level="error")
        return redirect("..")

    # Leer los datos del certificado
    signer = Signer.load(
        certificate=certificado.archivo_certificado.read(),
        key=certificado.clave_privada.read(),
        password=certificado.contrasena,
    )

    regimen_fiscal_obj = informacion_fiscal.regimen_fiscal.first()
    # Crear objeto Emisor
    emisor = cfdi40.Emisor(
        rfc=signer.rfc,
        nombre=signer.legal_name,
        regimen_fiscal=regimen_fiscal_obj.c_RegimenFiscal,
    )

    # Crear los conceptos 
    conceptos = []
    for concepto_model in factura.Conceptos.all():
        conceptos.append(
            cfdi40.Concepto(
                clave_prod_serv=concepto_model.claveprodserv.c_ClaveProdServ,
                cantidad=Decimal(concepto_model.cantidad),
                clave_unidad=concepto_model.clave_unidad.c_ClaveUnidad,
                descripcion=concepto_model.descripcion,
                valor_unitario=Decimal(concepto_model.valor_unitario),
                impuestos=cfdi40.Impuestos(),
            )
        )

    # Crear el comprobante
    comprobante = cfdi40.Comprobante(
        emisor=emisor,
        lugar_expedicion=informacion_fiscal.codigo_postal,
        receptor=receptor,
        metodo_pago=formaPago_model.Metodopago.c_MetodoPago,  # Ejemplo de método de pago
        forma_pago=formaPago_model.Formapago.c_FormaPago,  # Ejemplo de forma de pago
        serie="A",
        folio="12345",
        conceptos=conceptos,
    )

    # Firmar el comprobante
    comprobante.sign(signer)
    comprobante = comprobante.process()
    return comprobante