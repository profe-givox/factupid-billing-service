# tu_app_cfdi/views.py
from rest_framework import viewsets, status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.contrib.auth.models import User
from decimal import Decimal, InvalidOperation
import datetime
import base64
import threading # For checking thread IDs
import logging # For logging
import xml.etree.ElementTree as ET
import io # Para StringIO al parsear XML
from django.conf import settings # Para credenciales del PAC
from django.utils import timezone # Para datetimes con zona horaria

from satcfdi.models import Signer
from satcfdi.create.cfd import cfdi40
from satcfdi import catalogs as satcfdi_catalogs

from cfdi.models import (
    Pais, Estado, Localidad, Municipio, CodigoPostal, Colonia, Impuesto,
    TipoFactor, TasaOCuota, FormaPago, Moneda, TipoComprobante, Exportacion,
    MetodoPago, RegimenFiscal, ClaveProdServ, ClaveUnidad, ObjetoImp,
    Periodicidad, Meses, TipoRelacion, UsoCFDI, Aduana, PatenteAduanal,
    VersionCFDI, UsersCFDI, InformacionFiscal,
    Comprobante, CertificadoSelloDigital, ComprobanteEmitido, Complemento, TimbreFiscalDigital,
    ComprobanteNomina12, FacturaElectronica, FacturaElectronicaBorrador, FacturaCartaPorteTraslado
)
from app.views import SoapService

from ..serializers import (
    CountrySerializer, StateSerializer, LocalitySerializer, MunicipalitySerializer,
    PostalCodeSerializer, NeighborhoodSerializer, TaxCatalogSerializer, FactorTypeSerializer,
    TaxRateOrFeeSerializer, PaymentMethodSerializer, CurrencySerializer, VoucherTypeSerializer,
    ExportationSerializer, PaymentWaySerializer, TaxRegimeSerializer,
    ProductServiceKeySerializer, UnitKeySerializer, TaxObjectSerializer,
    PeriodicitySerializer, MonthSerializer, RelationTypeSerializer, CFDIUseSerializer,
    CustomsSerializer, CustomsPatentSerializer, CFDIVersionSerializer,
    DjangoUserSerializer, CFDIUserSerializer, TaxInformationSerializer,
    DigitalSealCertificateSerializer, DigitalSealCertificateCreateSerializer,
    VoucherSerializer,
    PayrollInvoice12Serializer, EInvoiceSerializer, EInvoiceDraftSerializer,
    WaybillTransferInvoiceSerializer,
    IssuedVoucherSerializer,
    CFIIIssuanceInputSerializer, CFIIIssuanceOutputSerializer
)

logger = logging.getLogger(__name__)


# --- ViewSets de Catálogos ---
class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Pais.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [AllowAny] # O IsAuthenticated si se requiere autenticación

class TaxRegimeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RegimenFiscal.objects.all()
    serializer_class = TaxRegimeSerializer
    permission_classes = [AllowAny]

class CFDIUseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UsoCFDI.objects.all()
    serializer_class = CFDIUseSerializer
    permission_classes = [AllowAny]

class StateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Estado.objects.all()
    serializer_class = StateSerializer
    permission_classes = [AllowAny]

class LocalityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Localidad.objects.all()
    serializer_class = LocalitySerializer
    permission_classes = [AllowAny]

class MunicipalityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Municipio.objects.all()
    serializer_class = MunicipalitySerializer
    permission_classes = [AllowAny]

class PostalCodeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CodigoPostal.objects.all()
    serializer_class = PostalCodeSerializer
    permission_classes = [AllowAny]

class NeighborhoodViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Colonia.objects.all()
    serializer_class = NeighborhoodSerializer
    permission_classes = [AllowAny]

class TaxCatalogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Impuesto.objects.all()
    serializer_class = TaxCatalogSerializer
    permission_classes = [AllowAny]

class FactorTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TipoFactor.objects.all()
    serializer_class = FactorTypeSerializer
    permission_classes = [AllowAny]

class TaxRateOrFeeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TasaOCuota.objects.all()
    serializer_class = TaxRateOrFeeSerializer
    permission_classes = [AllowAny]

class PaymentMethodViewSet(viewsets.ReadOnlyModelViewSet): # Corresponds to FormaPago model
    queryset = FormaPago.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = [AllowAny]

class CurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Moneda.objects.all()
    serializer_class = CurrencySerializer
    permission_classes = [AllowAny]

class VoucherTypeViewSet(viewsets.ReadOnlyModelViewSet): # Corresponds to TipoComprobante model
    queryset = TipoComprobante.objects.all()
    serializer_class = VoucherTypeSerializer
    permission_classes = [AllowAny]

class ExportationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Exportacion.objects.all()
    serializer_class = ExportationSerializer
    permission_classes = [AllowAny]

class PaymentWayViewSet(viewsets.ReadOnlyModelViewSet): # Corresponds to MetodoPago model
    queryset = MetodoPago.objects.all()
    serializer_class = PaymentWaySerializer
    permission_classes = [AllowAny]

class ProductServiceKeyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ClaveProdServ.objects.all()
    serializer_class = ProductServiceKeySerializer
    permission_classes = [AllowAny]

class UnitKeyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ClaveUnidad.objects.all()
    serializer_class = UnitKeySerializer
    permission_classes = [AllowAny]

class TaxObjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ObjetoImp.objects.all()
    serializer_class = TaxObjectSerializer
    permission_classes = [AllowAny]

class PeriodicityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Periodicidad.objects.all()
    serializer_class = PeriodicitySerializer
    permission_classes = [AllowAny]

class MonthViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Meses.objects.all()
    serializer_class = MonthSerializer
    permission_classes = [AllowAny]

class RelationTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TipoRelacion.objects.all()
    serializer_class = RelationTypeSerializer
    permission_classes = [AllowAny]

class CustomsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Aduana.objects.all()
    serializer_class = CustomsSerializer
    permission_classes = [AllowAny]

class CustomsPatentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PatenteAduanal.objects.all()
    serializer_class = CustomsPatentSerializer
    permission_classes = [AllowAny]

class CFDIVersionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = VersionCFDI.objects.all()
    serializer_class = CFDIVersionSerializer
    permission_classes = [AllowAny]


# --- ViewSets de Información de Usuario y Fiscal ---
class CFDIUserViewSet(viewsets.ModelViewSet):
    queryset = UsersCFDI.objects.all()
    serializer_class = CFDIUserSerializer
    permission_classes = [IsAdminUser] # O permisos más específicos

class TaxInformationViewSet(viewsets.ModelViewSet):
    serializer_class = TaxInformationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        try:
            # Asume que UsersCFDI tiene una relación OneToOneField con User de Django llamada 'idUserCFDI'
            user_cfdi_profile = UsersCFDI.objects.get(idUserCFDI=user)
            return InformacionFiscal.objects.filter(idUserCFDI=user_cfdi_profile)
        except UsersCFDI.DoesNotExist:
            return InformacionFiscal.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        try:
            user_cfdi_profile = UsersCFDI.objects.get(idUserCFDI=user)
            # Aquí podrías añadir lógica para verificar si ya existe una InformacionFiscal principal
            # o manejar la lógica de múltiples perfiles fiscales por usuario.
            serializer.save(idUserCFDI=user_cfdi_profile)
        except UsersCFDI.DoesNotExist:
            from rest_framework.exceptions import PermissionDenied
            # Esto depende de tu flujo de registro. Si un UsersCFDI no existe,
            # podrías crearlo aquí o, como en este caso, denegar el permiso.
            raise PermissionDenied("El perfil CFDI del usuario no existe.")


class DigitalSealCertificateViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Los usuarios solo pueden ver/gestionar sus propios certificados
        return CertificadoSelloDigital.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        # Usa un serializer diferente para la creación/actualización para manejar la subida de archivos
        if self.action in ['create', 'update', 'partial_update']:
            return DigitalSealCertificateCreateSerializer
        return DigitalSealCertificateSerializer

    def perform_create(self, serializer):
        # Lógica compleja para el procesamiento de certificados y llaves iría aquí.
        # Por ejemplo, extraer el número de certificado y la vigencia del archivo .cer
        # y validar la llave privada con su contraseña.
        # Esto se omite por brevedad pero es crucial en una implementación real.
        serializer.save(user=self.request.user)

# --- ViewSet de Borradores de Comprobantes ---
class VoucherViewSet(viewsets.ModelViewSet): # Gestiona instancias de Comprobante (borradores)
    serializer_class = VoucherSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        try:
            user_cfdi_profile = UsersCFDI.objects.get(idUserCFDI=user)
            # Filtra los comprobantes basados en la InformacionFiscal asociada al usuario
            user_tax_info_profiles = InformacionFiscal.objects.filter(idUserCFDI=user_cfdi_profile)
            return Comprobante.objects.filter(informacionFiscal__in=user_tax_info_profiles)
        except UsersCFDI.DoesNotExist:
            return Comprobante.objects.none()

    def perform_create(self, serializer):
        # Asegura que la informacionFiscal proporcionada en los datos del comprobante
        # pertenezca al usuario autenticado.
        tax_info_id = serializer.validated_data.get('informacionFiscal').id
        user = self.request.user
        try:
            user_cfdi_profile = UsersCFDI.objects.get(idUserCFDI=user)
            if not InformacionFiscal.objects.filter(pk=tax_info_id, idUserCFDI=user_cfdi_profile).exists():
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("La información fiscal especificada no pertenece al usuario.")
        except UsersCFDI.DoesNotExist:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("El perfil CFDI del usuario no existe.")
        serializer.save()


# --- ViewSet de Emisión de CFDI ---
class CFDIIssuanceViewSet(viewsets.ViewSet):
    """
    Un ViewSet para emitir nuevos CFDIs.
    Este ViewSet no corresponde directamente a un modelo para sus operaciones principales,
    sino que proporciona una acción para emitir un CFDI.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CFIIIssuanceInputSerializer # Usado por la API navegable de DRF para mostrar campos de entrada

    @action(detail=False, methods=['post'], url_path='issue-new-cfdi', serializer_class=CFIIIssuanceInputSerializer)
    def issue_new_cfdi(self, request, *args, **kwargs): # noqa: C901
        """
        Acción para emitir un nuevo CFDI.
        Recibe los datos del CFDI, los valida, simula la interacción con el PAC,
        y almacena el CFDI emitido.
        """
        logger.info(f"[DEBUG] REQUEST DATA: {request.data}")
        input_serializer = self.serializer_class(data=request.data) # Usa self.serializer_class o especifícalo directamente
        if not input_serializer.is_valid():
            return Response({
                "success": False,
                "message": "Datos de entrada inválidos.",
                "error_details": input_serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        data = input_serializer.validated_data
        current_user = request.user

        # Estas operaciones de base de datos de Django son seguras para hilos
        try: 
            cfdi_user_profile = UsersCFDI.objects.get(idUserCFDI=current_user)
            issuer_tax_info = get_object_or_404(
                InformacionFiscal,
                pk=data.get('informacionFiscal_id'),
                idUserCFDI=cfdi_user_profile
            )
            cfdi_user_profile_pk = cfdi_user_profile.pk # Guardar PKs
            issuer_tax_info_pk = issuer_tax_info.pk   # Guardar PKs
            
        except UsersCFDI.DoesNotExist:
            return Response({"success": False, "message": "Perfil CFDI del usuario no encontrado."}, status=status.HTTP_403_FORBIDDEN)
        except InformacionFiscal.DoesNotExist:
            return Response({"success": False, "message": "Información fiscal del emisor no encontrada o no pertenece al usuario."}, status=status.HTTP_404_NOT_FOUND)


        active_dsc = CertificadoSelloDigital.objects.filter(
            # user=current_user, # Asegurar que el CSD pertenezca al usuario si es necesario
            informacionFiscal=issuer_tax_info,
            estado=True, # Certificado activo
        ).order_by('-vigencia').first() # Obtiene el más reciente o el predeterminado

        if not active_dsc:
            return Response({"success": False, "message": "No se encontró un CSD activo para el emisor."}, status=status.HTTP_400_BAD_REQUEST)
        if not active_dsc.archivo_certificado or not active_dsc.clave_privada or not active_dsc.contrasena:
            return Response({"success": False, "message": "El CSD seleccionado está incompleto (falta .cer, .key o contraseña)."}, status=status.HTTP_400_BAD_REQUEST)

        # Leer los bytes del certificado y la llave una vez
        signer_cert_bytes = active_dsc.archivo_certificado.read()
        signer_key_bytes = active_dsc.clave_privada.read()
        # Es importante resetear el puntero de los archivos si se van a leer de nuevo fuera del lock,
        # aunque para Signer.load, pasar los bytes directamente es lo mejor.
        # active_dsc.archivo_certificado.seek(0)
        # active_dsc.clave_privada.seek(0)

        # Variables para almacenar resultados
        xml_base64_for_pac = None
        sello_cfdi_para_voucher = None
        certificado_cfdi_para_voucher = None
        voucher_data_to_save_on_success = None # Datos del comprobante que se guardarán solo si todo es exitoso

        try: # Bloque try principal para manejar excepciones y asegurar rollback si es necesario
            with transaction.atomic(): # Transacción de Django

                # --- INICIO DE LA SECCIÓN DE PROCESAMIENTO DE CFDI ---
                try:
                    # 1. Cargar Signer
                    signer = Signer.load(
                        certificate=signer_cert_bytes, # Usar bytes leídos
                        key=signer_key_bytes,       # Usar bytes leídos
                        password=active_dsc.contrasena
                    )
                    
                    if signer.rfc != issuer_tax_info.rfc:
                        raise ValueError(
                            f"El RFC del CSD ({signer.rfc}) no coincide con el RFC de la Información Fiscal seleccionada ({issuer_tax_info.rfc}). "
                            "Por favor, verifique la configuración del CSD y la Información Fiscal."
                        )

                    input_emisor_payload = data.get('emisor', {})
                    if input_emisor_payload.get('rfc') and input_emisor_payload.get('rfc') != signer.rfc:
                        raise ValueError(
                            f"El RFC del emisor proporcionado en los datos ({input_emisor_payload.get('rfc')}) "
                            f"no coincide con el RFC del CSD ({signer.rfc})."
                        )

                    # Preparar datos del emisor para el Voucher (modelo Django)
                    emisor_data_for_voucher = {
                        "rfc": signer.rfc,
                        "nombre": signer.legal_name,
                        "c_RegimenFiscal": issuer_tax_info.regimen_fiscal.pk,
                        "facAtrAdquirente": input_emisor_payload.get('facAtrAdquirente')
                    }

                    # Preparar datos para el VoucherSerializer (Comprobante modelo Django)
                    voucher_data_to_save_on_success = {
                        "informacionFiscal": issuer_tax_info.id,
                        "version": data.get('version'), "serie": data.get('serie'), "folio": data.get('folio'),
                        "fechaEmision": data.get('fechaEmision').date() if data.get('fechaEmision') else None, # Convertir datetime a date
                        "fechaPago": data.get('fechaPago').date() if data.get('fechaPago') else None,       # Convertir datetime a date
                        "c_FormaPago": data.get('c_FormaPago'),
                        "condicionesDePago": data.get('condicionesDePago'), 
                        "subTotal": data.get('subTotal'), 
                        "descuento": data.get('descuento'),
                        "c_Moneda": data.get('c_Moneda_id'),
                        "tipoCambio": data.get('tipoCambio'),
                        "total": data.get('total'),
                        "c_TipoDeComprobante": data.get('c_TipoDeComprobante'),
                        "c_Exportacion": data.get('c_Exportacion_id'), 
                        "c_MetodoPago": data.get('c_MetodoPago'),
                        "c_LugarExpedicion": data.get('c_LugarExpedicion'),
                        "confirmacion": data.get('confirmacion'),
                        "noCertificado": signer.certificate_number, # Del signer
                        "informacionGlobal": data.get('informacionGlobal'),
                        "cfdiRelacionados": data.get('cfdiRelacionados', []),
                        "emisor": emisor_data_for_voucher,
                        "receptor": data.get('receptor'),
                        "conceptos": data.get('conceptos'),
                        "impuestosTotales": data.get('impuestosTotales'),
                    }

                    # Validación temprana de los datos del comprobante (sin sello/certificado aún)
                    # Esto es opcional si CFIIIssuanceInputSerializer es exhaustivo, pero puede atrapar inconsistencias.
                    _temp_voucher_data = voucher_data_to_save_on_success.copy()
                    # Sello y Certificado se añadirán después si la firma es exitosa
                    _temp_voucher_data.pop('sello', None)
                    _temp_voucher_data.pop('certificado', None)
                    _temp_voucher_serializer = VoucherSerializer(data=_temp_voucher_data)
                    if not _temp_voucher_serializer.is_valid():
                        logger.error(f"Error al pre-validar datos del Comprobante (antes de firma): {_temp_voucher_serializer.errors}")
                        raise ValueError(f"Error al pre-validar datos del Comprobante: {_temp_voucher_serializer.errors}")

                    
                    # 2. Preparar objetos para satcfdi.cfdi40.Comprobante
                    emisor_cfdi = cfdi40.Emisor(
                        rfc=signer.rfc,
                        nombre=signer.legal_name,
                        regimen_fiscal=str(issuer_tax_info.regimen_fiscal.c_RegimenFiscal), # Asegurar que sea una cadena
                        fac_atr_adquirente=emisor_data_for_voucher.get('facAtrAdquirente')
                    )

                    receptor_data_input = request.data.get('receptor')
                    logger.info(f"Receptor data: {str(receptor_data_input)}")
                    receptor_cfdi = cfdi40.Receptor(
                        rfc=receptor_data_input.get('rfc'),
                        nombre=receptor_data_input.get('nombre'),
                        domicilio_fiscal_receptor=str(receptor_data_input.get('codigo_postal')),
                        regimen_fiscal_receptor=str(receptor_data_input.get('c_RegimenFiscalReceptor_id')),
                        uso_cfdi=str(request.data.get('c_UsoCFDI_id')),
                    )

                    conceptos_cfdi = []
                    for concepto_data in data.get('conceptos'):
                        impuestos_concepto_cfdi_list = []
                        if concepto_data.get('impuestos') and concepto_data.get('impuestos').get('traslados'):
                            for imp_tras_data in concepto_data.get('impuestos').get('traslados'):
                                impuestos_concepto_cfdi_list.append(
                                    cfdi40.Traslado(
                                        base=Decimal(str(imp_tras_data.get('base'))),
                                        impuesto=imp_tras_data.get('c_Impuesto_id'),
                                        tipo_factor=imp_tras_data.get('c_TipoFactor_id'),
                                        tasa_o_cuota=Decimal(str(imp_tras_data.get('tasaOCuota'))) if imp_tras_data.get('c_TipoFactor_id') != 'Exento' else None,
                                        importe=Decimal(str(imp_tras_data.get('importe'))) if imp_tras_data.get('c_TipoFactor_id') != 'Exento' else None
                                    )
                                )
                        logger.info(f"[DEBUD] Concepto: {concepto_data}")
                        conceptos_cfdi.append(
                            cfdi40.Concepto(
                                clave_prod_serv=str(concepto_data.get('c_ClaveProdServ')),
                                cantidad=Decimal(str(concepto_data.get('cantidad'))),
                                clave_unidad=str(concepto_data.get('c_ClaveUnidad')),
                                unidad=concepto_data.get('unidad'),
                                descripcion=concepto_data.get('descripcion'),
                                valor_unitario=Decimal(str(concepto_data.get('valorUnitario'))),
                                descuento=Decimal(str(concepto_data.get('descuento'))) if concepto_data.get('descuento') is not None else None,
                                objeto_imp=str(concepto_data.get('c_ObjetoImp')),
                                impuestos=cfdi40.Impuestos(traslados=impuestos_concepto_cfdi_list) if impuestos_concepto_cfdi_list else None,
                                no_identificacion=concepto_data.get('noIdentificacion')
                            )
                        )

                    # Procesamiento de la fecha de emisión
                    # data.get('fechaEmision') es un objeto datetime consciente (aware) en la zona horaria local
                    # (settings.TIME_ZONE), gracias al serializador de DRF y USE_TZ=True.
                    # El log confirma: datetime.datetime(2025, 6, 1, 15, 8, tzinfo=zoneinfo.ZoneInfo(key='America/Mexico_City'))
                    fecha_emision_aware_local = data.get('fechaEmision')

                    # Validación básica, aunque DRF debería garantizar esto.
                    if not isinstance(fecha_emision_aware_local, datetime.datetime):
                        logger.error(f"Crítico: fechaEmision obtenida de datos validados no es un objeto datetime. Valor: {fecha_emision_aware_local}, Tipo: {type(fecha_emision_aware_local)}")
                        raise ValueError("fechaEmision no es un objeto datetime válido después de la serialización.")
                    if fecha_emision_aware_local.tzinfo is None:
                        logger.error(f"Crítico: fechaEmision obtenida de datos validados es un datetime naive. Valor: {fecha_emision_aware_local}. Esto es inesperado con USE_TZ=True.")
                        # Como fallback, se intenta hacerlo consciente (aware) usando la zona horaria por defecto,
                        # pero esto podría indicar una configuración incorrecta.
                        fecha_emision_aware_local = timezone.make_aware(fecha_emision_aware_local, timezone.get_default_timezone())

                    # Eliminar microsegundos
                    fecha_emision_no_micros = fecha_emision_aware_local.replace(microsecond=0)
                    
                    # Para satcfdi.Comprobante.fecha, se necesita un datetime naive que represente
                    # la hora local de emisión. Se logra tomando el datetime local consciente (aware)
                    # y eliminando la información de tzinfo.
                    fecha_naive_para_cfdi = fecha_emision_no_micros.replace(tzinfo=None)
                    
                    logger.info(f"[DEBUG] Fecha para CFDI (naive, local time, no micros): {fecha_naive_para_cfdi}, strftime by satcfdi should be: {fecha_naive_para_cfdi.strftime('%Y-%m-%dT%H:%M:%S')}")
                    logger.info(f"[DEBUG] DATA: {data}")
                    logger.info(f"[DEBUG] Conceptos: {conceptos_cfdi}")

                    cfdi_obj = cfdi40.Comprobante(
                        emisor=emisor_cfdi,
                        receptor=receptor_cfdi,
                        conceptos=conceptos_cfdi,
                        lugar_expedicion=str(data.get('c_LugarExpedicion')),
                        fecha=fecha_naive_para_cfdi,
                        metodo_pago=str(data.get('c_MetodoPago')) if data.get('c_MetodoPago') else None,
                        forma_pago=data.get('c_FormaPago'),
                        moneda=str(data.get('c_Moneda_id')), 
                        tipo_de_comprobante=str(data.get('c_TipoDeComprobante')),
                        exportacion=str(data.get('c_Exportacion_id')),
                        serie=data.get('serie'),
                        folio=data.get('folio'),
                        tipo_cambio=Decimal(str(data.get('tipoCambio'))) if data.get('tipoCambio') is not None else None,
                        condiciones_de_pago=data.get('condicionesDePago'),
                        confirmacion=data.get('confirmacion'),
                    )
                    cfdi_obj.sign(signer)

                    sello_cfdi_para_voucher = cfdi_obj['Sello']
                    nocertificado_cfdi_para_voucher = cfdi_obj['NoCertificado']
                    certificado_cfdi_para_voucher = cfdi_obj['Certificado']

                    xml_to_stamp_str = cfdi_obj.xml_bytes(pretty_print=False).decode("utf-8")
                    xml_base64_for_pac = base64.b64encode(xml_to_stamp_str.encode("utf-8")).decode("utf-8")

                except ValueError as ve_section: # Errores de validación específicos
                    logger.error(f"ValueError durante la preparación del CFDI: {ve_section}", exc_info=True)
                    raise 
                except Exception as e_section: # Otros errores durante el procesamiento de datos CFDI
                    logger.error(f"Error durante la preparación del CFDI: {e_section}", exc_info=True)
                    raise 
                # --- FIN DE LA SECCIÓN DE PROCESAMIENTO DE CFDI ---

                # --- LLAMADA AL PAC ---
                pac_user = getattr(settings, "PAC_USER", "tu_usuario_pac")
                pac_password = getattr(settings, "PAC_PASSWORD", "tu_contraseña_pac")
                pac_response = None
                try:
                    pac_response = SoapService.stamp('', xml_base64_for_pac, pac_user, pac_password)
                except Exception as pac_error:
                    logger.error(f"Error de comunicación con el PAC: {pac_error}", exc_info=True)
                    # Lanzar una excepción para asegurar el rollback de la transacción
                    raise ConnectionError(f"Error de comunicación con el PAC: {str(pac_error)}")

                if not pac_response or not hasattr(pac_response, 'xml') or not pac_response.xml:
                    msg = "Respuesta inválida del PAC."
                    if pac_response and hasattr(pac_response, 'Incidencias') and pac_response.Incidencias:
                        incidencias_msgs = [str(inc.MensajeIncidencia) for inc in pac_response.Incidencias if hasattr(inc, 'MensajeIncidencia')]
                        if incidencias_msgs:
                            msg += " Incidencias: " + ", ".join(incidencias_msgs)
                    logger.warning(f"Respuesta inválida del PAC: {msg}. User: {current_user.username}, Folio: {data.get('folio')}")
                    # Lanzar una excepción para asegurar el rollback de la transacción
                    raise ValueError(f"Respuesta inválida del PAC: {msg}")

                stamped_xml_str = pac_response.xml.strip().replace("\x00", "") 
                logger.info(f"[THREAD_DIAG] Processing stamped XML. Thread ID: {threading.get_ident()}")
                if not stamped_xml_str:
                    logger.warning(f"PAC devolvió XML vacío. User: {current_user.username}, Folio: {data.get('folio')}")
                    # Lanzar una excepción para asegurar el rollback de la transacción
                    raise ValueError("El PAC devolvió un XML timbrado vacío.")

                try:
                    root = ET.fromstring(stamped_xml_str)
                    tfd_ns_map = {'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'}
                    timbre_element = root.find('.//tfd:TimbreFiscalDigital', namespaces=tfd_ns_map)

                    if timbre_element is None: 
                        for _, node_ns_tuple in ET.iterparse(io.StringIO(stamped_xml_str), events=['start-ns']):
                            prefix, uri = node_ns_tuple
                            if 'TimbreFiscalDigital' in uri: 
                                tfd_ns_map = {prefix if prefix else 'tfd': uri}
                                timbre_element = root.find(f'.//{{{uri}}}TimbreFiscalDigital') 
                                if timbre_element is not None:
                                    break
                    if timbre_element is None:
                        raise ValueError("Nodo TimbreFiscalDigital no encontrado en XML timbrado.")

                    uuid_val = timbre_element.get("UUID")
                    fecha_timbrado_str = timbre_element.get("FechaTimbrado")
                    fecha_timbrado_dt = datetime.datetime.fromisoformat(fecha_timbrado_str)
                    if fecha_timbrado_dt.tzinfo is None: 
                        fecha_timbrado_dt = fecha_timbrado_dt.replace(tzinfo=datetime.timezone.utc) 
                    
                    sello_cfd_tfd = timbre_element.get("SelloCFD")
                    no_certificado_sat_tfd = timbre_element.get("NoCertificadoSAT")
                    sello_sat_tfd = timbre_element.get("SelloSAT")
                    rfc_prov_certif_tfd = timbre_element.get("RfcProvCertif")
                except Exception as e: 
                    logger.error(f"Error al procesar XML timbrado del PAC: {str(e)}", exc_info=True)
                    # Lanzar una excepción para asegurar el rollback de la transacción
                    raise ValueError(f"Error al procesar XML timbrado: {str(e)}")
                logger.info(f"[THREAD_DIAG] Parsed TFD. UUID: {uuid_val}. Thread ID: {threading.get_ident()}")

                # --- SI TODO FUE EXITOSO HASTA AQUÍ, GUARDAR EN DB ---
                # Actualizar voucher_data_to_save_on_success con sello y certificado del cfdi_obj firmado
                voucher_data_to_save_on_success['sello'] = sello_cfdi_para_voucher
                voucher_data_to_save_on_success['certificado'] = certificado_cfdi_para_voucher
                # noCertificado ya está presente desde signer.certificate_number

                final_voucher_serializer = VoucherSerializer(data=voucher_data_to_save_on_success)
                if not final_voucher_serializer.is_valid():
                    # Esto sería un error interno grave si las validaciones previas fueron correctas
                    logger.error(f"Error CRÍTICO al serializar Comprobante final para DB: {final_voucher_serializer.errors}")
                    raise ValueError(f"Error interno al validar datos finales del Comprobante: {final_voucher_serializer.errors}")
                
                voucher_instance = final_voucher_serializer.save()

                # Crear Complemento y TimbreFiscalDigital asociados al voucher_instance recién guardado
                complement_obj, created = Complemento.objects.get_or_create(idComrobante=voucher_instance)
                TimbreFiscalDigital.objects.create(
                    idComplemento=complement_obj,
                    uuid=uuid_val,
                    fechaTimbrado=fecha_timbrado_dt,
                    rfcProvCertif=rfc_prov_certif_tfd,
                    selloCFD=sello_cfd_tfd,
                    noCerticadoSAT=no_certificado_sat_tfd, 
                    selloSAT=sello_sat_tfd,
                    version="4.0", 
                )

                # Crear el ComprobanteEmitido
                issued_voucher = ComprobanteEmitido.objects.create(
                    idUserCFDI=cfdi_user_profile,
                    comprobante_relacionado=voucher_instance,
                    fecha=fecha_timbrado_dt, 
                    folio=f"{voucher_instance.serie or ''}{voucher_instance.folio or ''}",
                    uuid=uuid_val,
                    rfc=issuer_tax_info.rfc, 
                    nombre=issuer_tax_info.razon_social, 
                    fecha_pago=voucher_instance.fechaEmision, 
                    total=voucher_instance.total,
                    xml_timbrado=stamped_xml_str, 
                    tipo=voucher_instance.c_TipoDeComprobante.descripcion if voucher_instance.c_TipoDeComprobante else None,
                    cod_estatus=pac_response.CodEstatus if hasattr(pac_response, 'CodEstatus') else "Timbrado",
                    metodo_pago=voucher_instance.c_MetodoPago.descripcion if voucher_instance.c_MetodoPago else None,
                    forma_pago=voucher_instance.c_FormaPago.descripcion if voucher_instance.c_FormaPago else None,
                    version_cfdi=voucher_instance.version
                )

                logger.info(f"[THREAD_DIAG] After creating ComprobanteEmitido. ID: {issued_voucher.id}. Thread ID: {threading.get_ident()}")
                simulated_pdf_url = f"/media/cfdi_pdfs/{uuid_val}.pdf" 

                output_data = {
                    "success": True,
                    "message": "CFDI emitido y timbrado exitosamente.",
                    "uuid": uuid_val,
                    "xml_timbrado_url": f"/api/v1/cfdi/issued-vouchers/{issued_voucher.id}/download-xml/", 
                    "pdf_url": simulated_pdf_url,
                    "comprobante_emitido_id": issued_voucher.id,
                    "pac_status_code": pac_response.CodEstatus if hasattr(pac_response, 'CodEstatus') else None,
                    "pac_incidences": [str(inc.MensajeIncidencia) for inc in pac_response.Incidencias if hasattr(inc, 'MensajeIncidencia')] if hasattr(pac_response, 'Incidencias') and pac_response.Incidencias else [],
                }
                return Response(output_data, status=status.HTTP_201_CREATED)

        # Los siguientes excepts capturarán excepciones lanzadas desde dentro del bloque transaction.atomic(),
        # o errores que ocurrieron antes de entrar al bloque de transacción.
        # Si la excepción ocurrió dentro de transaction.atomic(), Django se encarga del rollback.
        except ValueError as ve: # Captura ValueErrors de preparación, PAC, parseo TFD, o validación final
            logger.warning(f"ValueError en issue_new_cfdi (causando rollback si ocurrió en transacción): {ve}", exc_info=True) 
            return Response({"success": False, "message": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except ConnectionError as ce: # Captura error de conexión con PAC
            logger.error(f"ConnectionError en issue_new_cfdi (causando rollback si ocurrió en transacción): {ce}", exc_info=True)
            # Usar HTTP_503_SERVICE_UNAVAILABLE podría ser más apropiado para errores de PAC
            return Response({"success": False, "message": str(ce)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except UsersCFDI.DoesNotExist: 
            # Este error ocurre antes de la transacción
            return Response({"success": False, "message": "Perfil CFDI del usuario no encontrado."}, status=status.HTTP_403_FORBIDDEN)
        except InformacionFiscal.DoesNotExist:
            # Este error ocurre antes de la transacción
            return Response({"success": False, "message": "Información fiscal del emisor no encontrada o no pertenece al usuario."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e: 
            logger.error(f"Error general al emitir CFDI (causando rollback si ocurrió en transacción): {str(e)}", exc_info=True)
            return Response({
                "success": False,
                "message": "Ocurrió un error interno al intentar emitir el CFDI.",
                "error_details": str(e) 
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class IssuedVoucherViewSet(viewsets.ReadOnlyModelViewSet): # Gestiona instancias de ComprobanteEmitido
    serializer_class = IssuedVoucherSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        try:
            user_cfdi_profile = UsersCFDI.objects.get(idUserCFDI=user)
            return ComprobanteEmitido.objects.filter(idUserCFDI=user_cfdi_profile).order_by('-fecha')
        except UsersCFDI.DoesNotExist:
            return ComprobanteEmitido.objects.none()

    @action(detail=True, methods=['get'], url_path='download-xml')
    def download_xml(self, request, pk=None):
        """
        Acción para descargar el XML de un CFDI emitido.
        """
        issued_voucher = self.get_object() 
        if not issued_voucher.xml_timbrado:
            return Response({"error": "XML no disponible"}, status=status.HTTP_404_NOT_FOUND)
        
        from django.http import HttpResponse
        response = HttpResponse(issued_voucher.xml_timbrado, content_type='application/xml')
        response['Content-Disposition'] = f'attachment; filename="{issued_voucher.uuid}.xml"'
        return response

    # Podrías añadir una acción similar 'download_pdf' si generas y almacenas PDFs.

# --- ViewSets para Nómina, Factura Electrónica, Carta Porte (gestión de borradores/plantillas) ---
class PayrollInvoice12ViewSet(viewsets.ModelViewSet):
    serializer_class = PayrollInvoice12Serializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        # Filtra por el usuario que creó el registro de la factura de nómina
        return ComprobanteNomina12.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    # Podrías añadir una acción personalizada @action aquí para 'issue_payroll_cfdi'

class EInvoiceViewSet(viewsets.ModelViewSet): # Para FacturaElectronica (plantillas/datos maestros)
    serializer_class = EInvoiceSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return FacturaElectronica.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    # Podrías añadir una acción personalizada @action aquí para 'issue_e_invoice_cfdi'

class EInvoiceDraftViewSet(viewsets.ModelViewSet): # Para FacturaElectronicaBorrador
    serializer_class = EInvoiceDraftSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return FacturaElectronicaBorrador.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class WaybillTransferInvoiceViewSet(viewsets.ModelViewSet): # Para FacturaCartaPorteTraslado
    serializer_class = WaybillTransferInvoiceSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return FacturaCartaPorteTraslado.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    # Podrías añadir una acción personalizada @action aquí para 'issue_waybill_cfdi'

class IssuedVoucherViewSet(viewsets.ReadOnlyModelViewSet): # Gestiona instancias de ComprobanteEmitido
    serializer_class = IssuedVoucherSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        try:
            user_cfdi_profile = UsersCFDI.objects.get(idUserCFDI=user)
            return ComprobanteEmitido.objects.filter(idUserCFDI=user_cfdi_profile).order_by('-fecha')
        except UsersCFDI.DoesNotExist:
            return ComprobanteEmitido.objects.none()

    @action(detail=True, methods=['get'], url_path='download-xml')
    def download_xml(self, request, pk=None):
        """
        Acción para descargar el XML de un CFDI emitido.
        """
        issued_voucher = self.get_object() # Obtiene la instancia de ComprobanteEmitido
        if not issued_voucher.xml_timbrado:
            return Response({"error": "XML no disponible"}, status=status.HTTP_404_NOT_FOUND)
        
        from django.http import HttpResponse
        response = HttpResponse(issued_voucher.xml_timbrado, content_type='application/xml')
        response['Content-Disposition'] = f'attachment; filename="{issued_voucher.uuid}.xml"'
        return response

    # Podrías añadir una acción similar 'download_pdf' si generas y almacenas PDFs.

# --- ViewSets para Nómina, Factura Electrónica, Carta Porte (gestión de borradores/plantillas) ---
class PayrollInvoice12ViewSet(viewsets.ModelViewSet):
    serializer_class = PayrollInvoice12Serializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        # Filtra por el usuario que creó el registro de la factura de nómina
        return ComprobanteNomina12.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    # Podrías añadir una acción personalizada @action aquí para 'issue_payroll_cfdi'

class EInvoiceViewSet(viewsets.ModelViewSet): # Para FacturaElectronica (plantillas/datos maestros)
    serializer_class = EInvoiceSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return FacturaElectronica.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    # Podrías añadir una acción personalizada @action aquí para 'issue_e_invoice_cfdi'

class EInvoiceDraftViewSet(viewsets.ModelViewSet): # Para FacturaElectronicaBorrador
    serializer_class = EInvoiceDraftSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return FacturaElectronicaBorrador.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class WaybillTransferInvoiceViewSet(viewsets.ModelViewSet): # Para FacturaCartaPorteTraslado
    serializer_class = WaybillTransferInvoiceSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return FacturaCartaPorteTraslado.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    # Podrías añadir una acción personalizada @action aquí para 'issue_waybill_cfdi'
