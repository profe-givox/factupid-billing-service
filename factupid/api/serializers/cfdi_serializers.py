from rest_framework import serializers
from django.contrib.auth.models import User # User model from Django
from cfdi.models import (
    Pais, Estado, Localidad, Municipio, CodigoPostal, Colonia, Impuesto,
    TipoFactor, TasaOCuota, FormaPago, Moneda, TipoComprobante, Exportacion,
    MetodoPago, RegimenFiscal, ClaveProdServ, ClaveUnidad, ObjetoImp,
    Periodicidad, Meses, TipoRelacion, UsoCFDI, Aduana, PatenteAduanal,
    VersionCFDI, UsersCFDI, InformacionFiscal, InformacionGlobal,
    CfdiRelacionados, Emisor, Receptor, Impuestos, ACuentaTerceros,
    InformacionAduanera, CuentaPredial, ComplementoConcepto, Parte,
    ImpuestosTotales, TimbreFiscalDigital, TiposComplemento, Complemento, Addenda,
    Comprobante, Conceptos,
    # Payroll Models
    Banco, TipoJornada, TipoContrato, RiesgoPuesto, Sindicalizado, Genero,
    OrigenRecurso, TipoNomina, ComprobanteNomina12, subcontratacion, Nomina,
    TipoPercepcion, Percepcion, TipoDeduccion, Deduccion, TipoOtroPago, OtroPago,
    # E-invoicing Models
    FacturaElectronica, InformacionPago, Conceptosimpuesto, origenCFDI,
    ComprobantesRelacionados, LeyendasFiscales, FacturaElectronicaBorrador,
    CertificadoSelloDigital, ComprobanteEmitido,
    # Template Models
    Plantilla,
    # Waybill (Carta Porte) Models
    FacturaCartaPorteTraslado, Ubicacion, Ubicaciondomicilio, CartaPorte, Mercancia,
    CantidadTransportada, DetalleMercanciaMaritima, Pedimento, GuiaIdentificacion,
    TipopermisoSCT, configuracionvehicular, subtiporemolque, Autotransporte,
    TipopermisoSCTmaritimo, Tipoembarcacion, tipodecarga, numeroregautnaviera,
    TransporteMaritimo, tipocontenedor, Contenedor, TipopermisoSCTaereo,
    codigotransportista, TransporteAereo, tiposervicio, tipotrafico,
    tipoderechopaso, tipocarro, tipocontenedorcarro, TransporteFerroviario,
    tipofigura, FiguraTransporte, partetransporte, Domicilio, regimenaduaneroccptresuno
    # Ensure console.models.User_Service is available or adjust UsersCFDI if necessary
)
from decimal import Decimal

# Serializers para los perfiles fiscales de negocio
class DigitalStampCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificadoSelloDigital
        fields = '__all__'
        

class FiscalInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = InformacionFiscal
        fields = '__all__'
        

class TaxRegimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegimenFiscal
        fields = '__all__'
        
class CFDIVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VersionCFDI
        fields = '__all__'
        
class EmitedReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComprobanteEmitido
        fields = '__all__'
#--- Serializer para facturacion electronica ------------------------------------

class ElectronicInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacturaElectronica
        fields = '__all__'
        
class ElectronicInvoiceDraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacturaElectronicaBorrador
        fields = '__all__'
        
class TypeReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoComprobante
        fields = '__all__'
        
class IssuerCFDISerializer(serializers.ModelSerializer):
    class Meta:
        model = Emisor
        fields = '__all__'

class ReceiverCFDISerializer(serializers.ModelSerializer):
    class Meta:
        model = Receptor
        fields = '__all__'

class UseCFDISerializer(serializers.ModelSerializer):
    class Meta:
        model = UsoCFDI
        fields = '__all__'

class RelatedVouchersSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComprobantesRelacionados
        fields = '__all__'

class TypeRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoRelacion
        fields = '__all__'
        
class OriginCFDISerializer(serializers.ModelSerializer):
    class Meta:
        model = origenCFDI
        fields = '__all__'

class FiscalLegendSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeyendasFiscales
        fields = '__all__'

class ConceptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conceptos
        fields = '__all__'

class UnitKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaveUnidad
        fields = '__all__'

class ProServKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaveProdServ
        fields = '__all__'

class TaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Impuesto
        fields = '__all__'

class ObjectImpSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjetoImp
        fields = '__all__'

class GlobalInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = InformacionGlobal
        fields = '__all__'

class MonthsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meses
        fields = '__all__'

class PeriodicitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Periodicidad
        fields = '__all__'

class PaymentInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = InformacionPago
        fields = '__all__'
        
class PaymentFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormaPago
        fields = '__all__'
        
class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetodoPago
        fields = '__all__'

class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model: Moneda
        fields = '__all__'

class TotalTaxesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImpuestosTotales
        fields = '__all__'

class VoucherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comprobante
        fields = '__all__'  # O especifica los campos que quieres exponer
        read_only_fields = ['informacionFiscal'] # Evita que se modifique


# Nuevos serializers 

# --- Catalog Serializers ---
class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Pais
        fields = '__all__'

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estado
        fields = '__all__'

class LocalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Localidad
        fields = '__all__'

class MunicipalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Municipio
        fields = '__all__'

class PostalCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodigoPostal
        fields = '__all__'

class NeighborhoodSerializer(serializers.ModelSerializer): # Colonia
    class Meta:
        model = Colonia
        fields = '__all__'

class TaxCatalogSerializer(serializers.ModelSerializer): # Impuesto (Catálogo)
    class Meta:
        model = Impuesto
        fields = '__all__'

class FactorTypeSerializer(serializers.ModelSerializer): # TipoFactor
    class Meta:
        model = TipoFactor
        fields = '__all__'

class TaxRateOrFeeSerializer(serializers.ModelSerializer): # TasaOCuota
    impuesto = serializers.SlugRelatedField(slug_field='c_Impuesto', queryset=Impuesto.objects.all())
    factor = serializers.SlugRelatedField(slug_field='c_TipoFactor', queryset=TipoFactor.objects.all())
    class Meta:
        model = TasaOCuota
        fields = '__all__'

class PaymentMethodSerializer(serializers.ModelSerializer): # FormaPago
    class Meta:
        model = FormaPago
        fields = '__all__'

class CurrencySerializer(serializers.ModelSerializer): # Moneda
    class Meta:
        model = Moneda
        fields = '__all__'

class VoucherTypeSerializer(serializers.ModelSerializer): # TipoComprobante
    class Meta:
        model = TipoComprobante
        fields = '__all__'

class ExportationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exportacion
        fields = '__all__'

class PaymentWaySerializer(serializers.ModelSerializer): # MetodoPago (PUE, PPD)
    class Meta:
        model = MetodoPago
        fields = '__all__'

class TaxRegimeSerializer(serializers.ModelSerializer): # RegimenFiscal
    class Meta:
        model = RegimenFiscal
        fields = '__all__'

class ProductServiceKeySerializer(serializers.ModelSerializer): # ClaveProdServ
    class Meta:
        model = ClaveProdServ
        fields = '__all__'

class UnitKeySerializer(serializers.ModelSerializer): # ClaveUnidad
    class Meta:
        model = ClaveUnidad
        fields = '__all__'

class TaxObjectSerializer(serializers.ModelSerializer): # ObjetoImp
    class Meta:
        model = ObjetoImp
        fields = '__all__'

class PeriodicitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Periodicidad
        fields = '__all__'

class MonthSerializer(serializers.ModelSerializer): # Meses
    class Meta:
        model = Meses
        fields = '__all__'

class RelationTypeSerializer(serializers.ModelSerializer): # TipoRelacion
    class Meta:
        model = TipoRelacion
        fields = '__all__'

class CFDIUseSerializer(serializers.ModelSerializer): # UsoCFDI
    regimen_fiscal_receptor = TaxRegimeSerializer(many=True, read_only=True)
    class Meta:
        model = UsoCFDI
        fields = '__all__'

class CustomsSerializer(serializers.ModelSerializer): # Aduana
    class Meta:
        model = Aduana
        fields = '__all__'

class CustomsPatentSerializer(serializers.ModelSerializer): # PatenteAduanal
    class Meta:
        model = PatenteAduanal
        fields = '__all__'

class CFDIVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VersionCFDI
        fields = '__all__'

# --- User and Tax Information Serializers ---
class DjangoUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

class CFDIUserSerializer(serializers.ModelSerializer): # UsersCFDI
    idUserCFDI = DjangoUserSerializer(read_only=True)
    # idUserServicePlan_id = serializers.PrimaryKeyRelatedField(queryset=User_Service.objects.all()) # Assumes User_Service is defined
    class Meta:
        model = UsersCFDI
        fields = '__all__'

class TaxInformationSerializer(serializers.ModelSerializer): # InformacionFiscal
    regimen_fiscal = serializers.SlugRelatedField(slug_field='c_RegimenFiscal', queryset=RegimenFiscal.objects.all())
    regimen_receptor = serializers.SlugRelatedField(slug_field='c_RegimenFiscal', queryset=RegimenFiscal.objects.all(), allow_null=True, required=False)

    class Meta:
        model = InformacionFiscal
        fields = '__all__'
        read_only_fields = ('idUserCFDI',)

class DigitalSealCertificateSerializer(serializers.ModelSerializer): # CertificadoSelloDigital
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)
    informacionFiscal = serializers.PrimaryKeyRelatedField(queryset=InformacionFiscal.objects.all(), allow_null=True, required=False)
    class Meta:
        model = CertificadoSelloDigital
        fields = ('id', 'user', 'informacionFiscal', 'nombre_certificado',
                    'numero_certificado', 'vigencia', 'descripcion', 'sucursal',
                    'tipo', 'defecto', 'estado', 'notas')

class DigitalSealCertificateCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificadoSelloDigital
        fields = ('user', 'informacionFiscal', 'nombre_certificado', 'archivo_certificado',
                    'clave_privada', 'contrasena', 'vigencia', 'descripcion',
                    'sucursal', 'tipo', 'defecto', 'estado', 'notas')
        extra_kwargs = {
            'contrasena': {'write_only': True, 'style': {'input_type': 'password'}},
            'clave_privada': {'write_only': True},
            'archivo_certificado': {'write_only': True}
        }


# --- Voucher (Comprobante/CFDI) Structure Serializers ---
class GlobalInformationSerializer(serializers.ModelSerializer): # InformacionGlobal
    Periodicidad = serializers.SlugRelatedField(slug_field='c_Periodicidad', queryset=Periodicidad.objects.all(), allow_null=True, required=False)
    Meses = serializers.SlugRelatedField(slug_field='c_Meses', queryset=Meses.objects.all(), allow_null=True, required=False)
    Anio = serializers.CharField(max_length=4, allow_null=True, required=False)
    class Meta:
        model = InformacionGlobal
        exclude = ('Comprobante',)

class RelatedCFDISerializer(serializers.ModelSerializer): # CfdiRelacionados
    c_TipoRelacion = serializers.SlugRelatedField(slug_field='c_TipoRelacion', queryset=TipoRelacion.objects.all(), allow_null=True, required=False)
    class Meta:
        model = CfdiRelacionados
        exclude = ('comprobante',)

class IssuerSerializer(serializers.ModelSerializer): # Emisor
    #c_RegimenFiscal = serializers.SlugRelatedField(slug_field='c_RegimenFiscal', queryset=RegimenFiscal.objects.all())
    c_RegimenFiscal = serializers.PrimaryKeyRelatedField(
        queryset=RegimenFiscal.objects.all()
    )
    class Meta:
        model = Emisor
        exclude = ('comprobante',)

class ReceiverSerializer(serializers.ModelSerializer): # Receptor
    c_DomicilioFiscalReceptor = serializers.SlugRelatedField(slug_field='c_CodigoPostal', queryset=CodigoPostal.objects.all(), allow_null=True, required=False)
    c_ResidenciaFiscal = serializers.SlugRelatedField(slug_field='c_Pais', queryset=Pais.objects.all(), allow_null=True, required=False)
    c_RegimenFiscalReceptor = serializers.SlugRelatedField(slug_field='c_RegimenFiscal', queryset=RegimenFiscal.objects.all(), allow_null=True, required=False)
    c_UsoCFDI = serializers.SlugRelatedField(slug_field='c_UsoCFDI', queryset=UsoCFDI.objects.all(), allow_null=True, required=False)
    class Meta:
        model = Receptor
        exclude = ('comprobante',)

class ConceptTaxSerializer(serializers.ModelSerializer): # Impuestos (de Concepto)
    c_Impuesto = serializers.SlugRelatedField(slug_field='c_Impuesto', queryset=Impuesto.objects.all(), allow_null=True, required=False)
    c_TipoFactor = serializers.SlugRelatedField(slug_field='c_TipoFactor', queryset=TipoFactor.objects.all(), allow_null=True, required=False)
    c_TasaOCuota = serializers.PrimaryKeyRelatedField(queryset=TasaOCuota.objects.all(), allow_null=True, required=False)
    class Meta:
        model = Impuestos
        exclude = ('idComprobante',)

class ThirdPartyAccountSerializer(serializers.ModelSerializer): # ACuentaTerceros
    c_RegimenFiscalACuentaTerceros = serializers.SlugRelatedField(slug_field='c_RegimenFiscal', queryset=RegimenFiscal.objects.all(), allow_null=True, required=False)
    class Meta:
        model = ACuentaTerceros
        exclude = ('idConcepto',)

class ConceptCustomsInformationSerializer(serializers.ModelSerializer): # InformacionAduanera (de Concepto)
    aduana = serializers.SlugRelatedField(slug_field='c_Aduana', queryset=Aduana.objects.all())
    patente = serializers.SlugRelatedField(slug_field='c_PatenteAduanal', queryset=PatenteAduanal.objects.all())
    class Meta:
        model = InformacionAduanera
        exclude = ('idConcepto',)

class PropertyTaxAccountSerializer(serializers.ModelSerializer): # CuentaPredial
    class Meta:
        model = CuentaPredial
        exclude = ('idConcepto',)

class ConceptComplementSerializer(serializers.ModelSerializer): # ComplementoConcepto
    class Meta:
        model = ComplementoConcepto
        exclude = ('idConcepto',)

class PartSerializer(serializers.ModelSerializer): # Parte
    claveProdServ = serializers.SlugRelatedField(slug_field='c_ClaveProdServ', queryset=ClaveProdServ.objects.all(), allow_null=True, required=False)
    informacionAduanera = ConceptCustomsInformationSerializer(many=False, required=False)
    class Meta:
        model = Parte
        exclude = ('idConcepto',)

class ConceptSerializer(serializers.ModelSerializer): # Conceptos
    c_ClaveProdServ = serializers.SlugRelatedField(slug_field='c_ClaveProdServ', queryset=ClaveProdServ.objects.all())
    c_ClaveUnidad = serializers.SlugRelatedField(slug_field='c_ClaveUnidad', queryset=ClaveUnidad.objects.all())
    c_ObjetoImp = serializers.SlugRelatedField(slug_field='c_ObjetoImp', queryset=ObjetoImp.objects.all())

    impuestos = ConceptTaxSerializer(many=True, required=False)
    aCuentaTerceros = ThirdPartyAccountSerializer(required=False)
    informacionAduanera = ConceptCustomsInformationSerializer(many=True, required=False)
    cuentaPredial = PropertyTaxAccountSerializer(required=False)
    complementoConcepto = ConceptComplementSerializer(required=False)
    parte = PartSerializer(many=True, required=False)

    class Meta:
        model = Conceptos
        exclude = ('comprobante',)

class TotalTaxesSerializer(serializers.ModelSerializer): # ImpuestosTotales
    c_Impuesto = serializers.SlugRelatedField(slug_field='c_Impuesto', queryset=Impuesto.objects.all(), allow_null=True, required=False)
    c_TipoFactor = serializers.SlugRelatedField(slug_field='c_TipoFactor', queryset=TipoFactor.objects.all(), allow_null=True, required=False)
    c_TasaOCuota = serializers.PrimaryKeyRelatedField(queryset=TasaOCuota.objects.all(), allow_null=True, required=False)
    class Meta:
        model = ImpuestosTotales
        exclude = ('comprobante',)

class DigitalTaxStampSerializer(serializers.ModelSerializer): # TimbreFiscalDigital
    version = serializers.PrimaryKeyRelatedField(queryset=VersionCFDI.objects.all(), allow_null=True, required=False)
    class Meta:
        model = TimbreFiscalDigital
        exclude = ('idComplemento',)

class ComplementTypesSerializer(serializers.ModelSerializer): # TiposComplemento
    class Meta:
        model = TiposComplemento
        fields = '__all__'

class ComplementSerializer(serializers.ModelSerializer): # Complemento (nodo padre)
    idTipoComplemento = serializers.PrimaryKeyRelatedField(queryset=TiposComplemento.objects.all(), allow_null=True, required=False)
    class Meta:
        model = Complemento
        exclude = ('idComrobante',)


class AddendumSerializer(serializers.ModelSerializer): # Addenda
    class Meta:
        model = Addenda
        exclude = ('comprobante',)

class VoucherSerializer(serializers.ModelSerializer): # Comprobante
    informacionFiscal = serializers.PrimaryKeyRelatedField(queryset=InformacionFiscal.objects.all(), allow_null=True, required=False)
    c_FormaPago = serializers.SlugRelatedField(slug_field='c_FormaPago', queryset=FormaPago.objects.all(), allow_null=True, required=False)
    c_Moneda = serializers.SlugRelatedField(slug_field='c_Moneda', queryset=Moneda.objects.all(), allow_null=True, required=False)
    c_TipoDeComprobante = serializers.SlugRelatedField(slug_field='c_TipoDeComprobante', queryset=TipoComprobante.objects.all(), allow_null=True, required=False)
    c_Exportacion = serializers.SlugRelatedField(slug_field='c_Exportacion', queryset=Exportacion.objects.all(), allow_null=True, required=False)
    c_MetodoPago = serializers.SlugRelatedField(slug_field='c_MetodoPago', queryset=MetodoPago.objects.all(), allow_null=True, required=False)
    c_LugarExpedicion = serializers.SlugRelatedField(slug_field='c_CodigoPostal', queryset=CodigoPostal.objects.all(), allow_null=True, required=False)

    informacionGlobal = GlobalInformationSerializer(required=False, allow_null=True)
    cfdiRelacionados = RelatedCFDISerializer(many=True, required=False)
    emisor = IssuerSerializer(required=False)
    receptor = ReceiverSerializer(required=False)
    conceptos = ConceptSerializer(many=True)
    impuestosTotales = TotalTaxesSerializer(required=False, allow_null=True)
    complemento = ComplementSerializer(many=True, required=False)
    addenda = AddendumSerializer(required=False)

    class Meta:
        model = Comprobante
        fields = '__all__'

    def create(self, validated_data):
        global_info_data = validated_data.pop('informacionGlobal', None)
        related_cfdi_data = validated_data.pop('cfdiRelacionados', [])
        issuer_data = validated_data.pop('emisor', None)
        receiver_data = validated_data.pop('receptor', None)
        concepts_data = validated_data.pop('conceptos', [])
        total_taxes_data = validated_data.pop('impuestosTotales', None)
        complements_data = validated_data.pop('complemento', [])
        addendum_data = validated_data.pop('addenda', None)

        voucher = Comprobante.objects.create(**validated_data)

        if global_info_data:
            InformacionGlobal.objects.create(Comprobante=voucher, **global_info_data)

        for related_data in related_cfdi_data:
            CfdiRelacionados.objects.create(comprobante=voucher, **related_data)

        if issuer_data:
            Emisor.objects.create(comprobante=voucher, **issuer_data)

        if receiver_data:
            Receptor.objects.create(comprobante=voucher, **receiver_data)

        for concept_item_data in concepts_data:
            concept_taxes_data = concept_item_data.pop('impuestos', [])
            third_party_data = concept_item_data.pop('aCuentaTerceros', None)
            customs_info_list_data = concept_item_data.pop('informacionAduanera', [])
            property_tax_data = concept_item_data.pop('cuentaPredial', None)
            concept_complement_data = concept_item_data.pop('complementoConcepto', None)
            parts_data = concept_item_data.pop('parte', [])

            concept_obj = Conceptos.objects.create(comprobante=voucher, **concept_item_data)

            for tax_data in concept_taxes_data:
                Impuestos.objects.create(idComprobante=concept_obj, **tax_data)

            if third_party_data:
                ACuentaTerceros.objects.create(idConcepto=concept_obj, **third_party_data)

            for customs_data in customs_info_list_data:
                InformacionAduanera.objects.create(idConcepto=concept_obj, **customs_data)

            if property_tax_data:
                CuentaPredial.objects.create(idConcepto=concept_obj, **property_tax_data)

            if concept_complement_data:
                ComplementoConcepto.objects.create(idConcepto=concept_obj, **concept_complement_data)

            for part_item_data in parts_data:
                part_customs_info_data = part_item_data.pop('informacionAduanera', None)
                part_obj = Parte.objects.create(idConcepto=concept_obj, **part_item_data)
                if part_customs_info_data:
                    InformacionAduanera.objects.create(idConcepto=concept_obj, **part_customs_info_data) # Or link to part_obj if model allows

        if total_taxes_data:
            ImpuestosTotales.objects.create(comprobante=voucher, **total_taxes_data)

        for comp_data in complements_data:
            Complemento.objects.create(idComrobante=voucher, **comp_data)

        if addendum_data:
            Addenda.objects.create(comprobante=voucher, **addendum_data)

        return voucher

    def update(self, instance, validated_data):
        instance.serie = validated_data.get('serie', instance.serie)
        instance.save()

        concepts_data = validated_data.get('conceptos')
        if concepts_data is not None:
            instance.conceptos.all().delete()
            for concept_item_data in concepts_data:
                concept_taxes_data = concept_item_data.pop('impuestos', [])
                concept_obj = Conceptos.objects.create(comprobante=instance, **concept_item_data)
                for tax_data in concept_taxes_data:
                    Impuestos.objects.create(idComprobante=concept_obj, **tax_data)
        return super().update(instance, validated_data)

# --- Issued Voucher Serializer ---
class IssuedVoucherSerializer(serializers.ModelSerializer): # ComprobanteEmitido
    idUserCFDI = CFDIUserSerializer(read_only=True)
    comprobante_relacionado = VoucherSerializer(read_only=True)
    class Meta:
        model = ComprobanteEmitido
        fields = '__all__'

# --- Payroll Serializers ---
class PayrollTypeSerializer(serializers.ModelSerializer): # TipoNomina
    class Meta:
        model = TipoNomina
        fields = '__all__'

class PerceptionSerializer(serializers.ModelSerializer):
    tipo_percepcion = serializers.PrimaryKeyRelatedField(queryset=TipoPercepcion.objects.all(), allow_null=True, required=False)
    class Meta:
        model = Percepcion
        exclude = ('nomina', 'factura_nomina')

class DeductionSerializer(serializers.ModelSerializer):
    tipo_deduccion = serializers.PrimaryKeyRelatedField(queryset=TipoDeduccion.objects.all(), allow_null=True, required=False)
    class Meta:
        model = Deduccion
        exclude = ('nomina', 'factura_nomina')

class OtherPaymentSerializer(serializers.ModelSerializer):
    tipo_otro_pago = serializers.PrimaryKeyRelatedField(queryset=TipoOtroPago.objects.all(), allow_null=True, required=False)
    class Meta:
        model = OtroPago
        exclude = ('nomina', 'factura_nomina')

class PayrollSerializer(serializers.ModelSerializer): # Nomina
    tipo_nomina = serializers.PrimaryKeyRelatedField(queryset=TipoNomina.objects.all(), allow_null=True, required=False)
    origen_recurso = serializers.PrimaryKeyRelatedField(queryset=OrigenRecurso.objects.all(), allow_null=True, required=False)
    entidad_presto_servicio = serializers.SlugRelatedField(slug_field='c_Estado', queryset=Estado.objects.all(), allow_null=True, required=False)
    genero = serializers.PrimaryKeyRelatedField(queryset=Genero.objects.all(), allow_null=True, required=False)
    sindicalizado = serializers.PrimaryKeyRelatedField(queryset=Sindicalizado.objects.all(), allow_null=True, required=False)
    riesgo_puesto = serializers.PrimaryKeyRelatedField(queryset=RiesgoPuesto.objects.all(), allow_null=True, required=False)
    tipo_contrato = serializers.PrimaryKeyRelatedField(queryset=TipoContrato.objects.all(), allow_null=True, required=False)
    tipo_jornada = serializers.PrimaryKeyRelatedField(queryset=TipoJornada.objects.all(), allow_null=True, required=False)
    banco = serializers.PrimaryKeyRelatedField(queryset=Banco.objects.all(), allow_null=True, required=False)
    periodicidad = serializers.SlugRelatedField(slug_field='c_Periodicidad', queryset=Periodicidad.objects.all(), allow_null=True, required=False)

    percepciones = PerceptionSerializer(many=True, required=False)
    deducciones = DeductionSerializer(many=True, required=False)
    otros_pagos = OtherPaymentSerializer(many=True, required=False)

    class Meta:
        model = Nomina
        exclude = ('factura_nomina',)

class SubcontractingSerializer(serializers.ModelSerializer): # subcontratacion
    class Meta:
        model = subcontratacion
        exclude = ('ComprobanteNomina12',)


class PayrollInvoice12Serializer(serializers.ModelSerializer): # ComprobanteNomina12
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)
    informacion_fiscal = serializers.PrimaryKeyRelatedField(queryset=InformacionFiscal.objects.all())
    regimen_fiscal = serializers.SlugRelatedField(slug_field='c_RegimenFiscal', queryset=RegimenFiscal.objects.all(), allow_null=True, required=False)
    
    subcontrataciones = SubcontractingSerializer(many=True, required=False)
    nomina = PayrollSerializer(many=True, required=False)

    class Meta:
        model = ComprobanteNomina12
        fields = '__all__'

    def create(self, validated_data):
        subcontracting_list_data = validated_data.pop('subcontrataciones', [])
        payroll_list_data = validated_data.pop('nomina', [])
        
        payroll_invoice = ComprobanteNomina12.objects.create(**validated_data)

        for sub_data in subcontracting_list_data:
            subcontratacion.objects.create(ComprobanteNomina12=payroll_invoice, **sub_data)

        for payroll_item_data in payroll_list_data:
            perceptions_data = payroll_item_data.pop('percepciones', [])
            deductions_data = payroll_item_data.pop('deducciones', [])
            other_payments_data = payroll_item_data.pop('otros_pagos', [])
            
            payroll_obj = Nomina.objects.create(factura_nomina=payroll_invoice, **payroll_item_data)

            for p_data in perceptions_data: Percepcion.objects.create(nomina=payroll_obj, factura_nomina=payroll_invoice, **p_data)
            for d_data in deductions_data: Deduccion.objects.create(nomina=payroll_obj, factura_nomina=payroll_invoice, **d_data)
            for o_data in other_payments_data: OtroPago.objects.create(nomina=payroll_obj, factura_nomina=payroll_invoice, **o_data)
        return payroll_invoice

# --- E-Invoice Serializers (General, Draft) ---
class PaymentInformationSerializer(serializers.ModelSerializer): # InformacionPago
    Metodopago = serializers.SlugRelatedField(slug_field='c_MetodoPago', queryset=MetodoPago.objects.all(), allow_null=True, required=False)
    Formapago = serializers.SlugRelatedField(slug_field='c_FormaPago', queryset=FormaPago.objects.all(), allow_null=True, required=False)
    Moneda = serializers.SlugRelatedField(slug_field='c_Moneda', queryset=Moneda.objects.all(), allow_null=True, required=False)
    class Meta:
        model = InformacionPago
        exclude = ('Comprobante', 'FacturaElectronica', 'ComprobanteNomina12', 'FacturaElectronicaBorrador')


class ConceptInvoiceTaxSerializer(serializers.ModelSerializer): # Conceptosimpuesto
    Impuesto = serializers.PrimaryKeyRelatedField(queryset=TasaOCuota.objects.all())
    class Meta:
        model = Conceptosimpuesto
        exclude = ('FacturaElectronica', 'Conceptos')

class CFDIOriginSerializer(serializers.ModelSerializer): # origenCFDI
    class Meta:
        model = origenCFDI
        fields = '__all__'

class RelatedVouchersInvoiceSerializer(serializers.ModelSerializer): # ComprobantesRelacionados (para Factura)
    Tiporelacion = serializers.SlugRelatedField(slug_field='c_TipoRelacion', queryset=TipoRelacion.objects.all(), allow_null=True, required=False)
    origenCFDI = serializers.PrimaryKeyRelatedField(queryset=origenCFDI.objects.all(), allow_null=True, required=False)
    class Meta:
        model = ComprobantesRelacionados
        exclude = ('Comprobante', 'FacturaElectronica', 'ComprobanteNomina12', 'FacturaCartaPorteTraslado', 'FacturaElectronicaBorrador')

class FiscalLegendsSerializer(serializers.ModelSerializer): # LeyendasFiscales
    class Meta:
        model = LeyendasFiscales
        exclude = ('Comprobante', 'FacturaElectronica', 'ComprobanteNomina12', 'FacturaElectronicaBorrador')


class EInvoiceSerializer(serializers.ModelSerializer): # FacturaElectronica
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)
    informacion_fiscal = serializers.PrimaryKeyRelatedField(queryset=InformacionFiscal.objects.all())
    regimen_fiscal = serializers.SlugRelatedField(slug_field='c_RegimenFiscal', queryset=RegimenFiscal.objects.all(), allow_null=True, required=False)

    InformacionPago = PaymentInformationSerializer(many=True, required=False, source='InformacionPago')
    Comprobante_relacionados = RelatedVouchersInvoiceSerializer(many=True, required=False, source='Comprobante_relacionados')
    LeyendasFiscales = FiscalLegendsSerializer(many=True, required=False, source='LeyendasFiscales')

    class Meta:
        model = FacturaElectronica
        fields = '__all__'

    def create(self, validated_data):
        payment_info_list_data = validated_data.pop('InformacionPago', [])
        related_vouchers_list_data = validated_data.pop('Comprobante_relacionados', [])
        legends_list_data = validated_data.pop('LeyendasFiscales', [])

        e_invoice = FacturaElectronica.objects.create(**validated_data)

        for pi_data in payment_info_list_data:
            InformacionPago.objects.create(FacturaElectronica=e_invoice, **pi_data)
        for rv_data in related_vouchers_list_data:
            ComprobantesRelacionados.objects.create(FacturaElectronica=e_invoice, **rv_data)
        for l_data in legends_list_data:
            LeyendasFiscales.objects.create(FacturaElectronica=e_invoice, **l_data)
        return e_invoice

class EInvoiceDraftSerializer(serializers.ModelSerializer): # FacturaElectronicaBorrador
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)
    informacion_fiscal = serializers.PrimaryKeyRelatedField(queryset=InformacionFiscal.objects.all())
    regimen_fiscal = serializers.SlugRelatedField(slug_field='c_RegimenFiscal', queryset=RegimenFiscal.objects.all(), allow_null=True, required=False)

    InformacionPagoBorrador = PaymentInformationSerializer(many=True, required=False, source='InformacionPagoBorrador')
    Comprobante_relacionados_Borrador = RelatedVouchersInvoiceSerializer(many=True, required=False, source='Comprobante_relacionados_Borrador')
    LeyendasFiscalesBorrador = FiscalLegendsSerializer(many=True, required=False, source='LeyendasFiscalesBorrador')

    class Meta:
        model = FacturaElectronicaBorrador
        fields = '__all__'

    def create(self, validated_data):
        payment_info_list_data = validated_data.pop('InformacionPagoBorrador', [])
        related_vouchers_list_data = validated_data.pop('Comprobante_relacionados_Borrador', [])
        legends_list_data = validated_data.pop('LeyendasFiscalesBorrador', [])

        draft_invoice = FacturaElectronicaBorrador.objects.create(**validated_data)

        for pi_data in payment_info_list_data:
            InformacionPago.objects.create(FacturaElectronicaBorrador=draft_invoice, **pi_data)
        for rv_data in related_vouchers_list_data:
            ComprobantesRelacionados.objects.create(FacturaElectronicaBorrador=draft_invoice, **rv_data)
        for l_data in legends_list_data:
            LeyendasFiscales.objects.create(FacturaElectronicaBorrador=draft_invoice, **l_data)
        return draft_invoice

# --- Waybill (Carta Porte) Serializers ---
class WaybillLocationAddressSerializer(serializers.ModelSerializer): # Ubicaciondomicilio (Carta Porte)
    class Meta:
        model = Ubicaciondomicilio
        exclude = ('ubicacion', 'FacturaCartaPorteTraslado')

class WaybillLocationSerializer(serializers.ModelSerializer): # Ubicacion (Carta Porte)
    domicilio = WaybillLocationAddressSerializer(required=False)
    class Meta:
        model = Ubicacion
        exclude = ('FacturaCartaPorteTraslado',)

class WaybillMerchandiseSerializer(serializers.ModelSerializer): # Mercancia (Carta Porte)
    class Meta:
        model = Mercancia
        exclude = ('FacturaCartaPorteTraslado',)

class WaybillAutotransportSerializer(serializers.ModelSerializer): # Autotransporte (Carta Porte)
    tipo_permiso_sct = serializers.PrimaryKeyRelatedField(queryset=TipopermisoSCT.objects.all(), allow_null=True, required=False)
    configuracion_vehicular = serializers.PrimaryKeyRelatedField(queryset=configuracionvehicular.objects.all(), allow_null=True, required=False)
    subtipo_remolque = serializers.PrimaryKeyRelatedField(queryset=subtiporemolque.objects.all(), allow_null=True, required=False)
    class Meta:
        model = Autotransporte
        exclude = ('FacturaCartaPorteTraslado',)

class WaybillFigureAddressSerializer(serializers.ModelSerializer): # Domicilio (de FiguraTransporte)
    class Meta:
        model = Domicilio
        exclude = ('figura_transporte', 'FacturaCartaPorteTraslado')

class WaybillTransportFigureSerializer(serializers.ModelSerializer): # FiguraTransporte (Carta Porte)
    tipo_figura = serializers.PrimaryKeyRelatedField(queryset=tipofigura.objects.all(), allow_null=True, required=False)
    domicilio = WaybillFigureAddressSerializer(required=False)
    class Meta:
        model = FiguraTransporte
        exclude = ('FacturaCartaPorteTraslado',)


class FullWaybillSerializer(serializers.ModelSerializer): # CartaPorte
    class Meta:
        model = CartaPorte
        exclude = ('FacturaCartaPorteTraslado',)


class WaybillTransferInvoiceSerializer(serializers.ModelSerializer): # FacturaCartaPorteTraslado
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)
    informacion_fiscal = serializers.PrimaryKeyRelatedField(queryset=InformacionFiscal.objects.all())
    regimen_fiscal = serializers.SlugRelatedField(slug_field='c_RegimenFiscal', queryset=RegimenFiscal.objects.all(), allow_null=True, required=False)
    
    ubicaciones = WaybillLocationSerializer(many=True, required=False)
    mercancias = WaybillMerchandiseSerializer(many=True, required=False)
    cartas_porte = FullWaybillSerializer(many=True, required=False)
    autotransportes = WaybillAutotransportSerializer(many=True, required=False)
    figuras_transporte = WaybillTransportFigureSerializer(many=True, required=False)

    class Meta:
        model = FacturaCartaPorteTraslado
        fields = '__all__'

    def create(self, validated_data):
        locations_data = validated_data.pop('ubicaciones', [])
        merchandise_list_data = validated_data.pop('mercancias', [])
        waybills_data = validated_data.pop('cartas_porte', [])
        autotransports_data = validated_data.pop('autotransportes', [])
        transport_figures_data = validated_data.pop('figuras_transporte', [])

        waybill_invoice = FacturaCartaPorteTraslado.objects.create(**validated_data)

        for loc_data in locations_data:
            address_data = loc_data.pop('domicilio', None)
            loc_obj = Ubicacion.objects.create(FacturaCartaPorteTraslado=waybill_invoice, **loc_data)
            if address_data:
                Ubicaciondomicilio.objects.create(ubicacion=loc_obj, FacturaCartaPorteTraslado=waybill_invoice, **address_data)
        
        for merch_data in merchandise_list_data:
            Mercancia.objects.create(FacturaCartaPorteTraslado=waybill_invoice, **merch_data)

        for wb_data in waybills_data:
            CartaPorte.objects.create(FacturaCartaPorteTraslado=waybill_invoice, **wb_data)

        for at_data in autotransports_data:
            Autotransporte.objects.create(FacturaCartaPorteTraslado=waybill_invoice, **at_data)

        for fig_data in transport_figures_data:
            address_data = fig_data.pop('domicilio', None)
            fig_obj = FiguraTransporte.objects.create(FacturaCartaPorteTraslado=waybill_invoice, **fig_data)
            if address_data:
                Domicilio.objects.create(figura_transporte=fig_obj, FacturaCartaPorteTraslado=waybill_invoice, **address_data)
        
        return waybill_invoice


# --- CFDI Issuance Serializers ---
class ConceptCFDIIsuaanceImputSerializer(serializers.Serializer): # ConceptoEmisionCFDI
    c_ClaveProdServ = serializers.CharField(max_length=11)
    cantidad = serializers.DecimalField(max_digits=18, decimal_places=6, help_text="Cantidad del bien o servicio.")
    c_ClaveUnidad = serializers.CharField(max_length=3)
    unidad = serializers.CharField(max_length=20, required=False, allow_blank=True, allow_null=True, help_text="Unidad de medida. Opcional si la clave unidad lo incluye.")
    descripcion = serializers.CharField(max_length=1000, help_text="Descripción detallada del bien o servicio.")
    valorUnitario = serializers.DecimalField(max_digits=18, decimal_places=6, help_text="Valor unitario del bien o servicio.")
    descuento = serializers.DecimalField(max_digits=18, decimal_places=2,required=False, allow_null=True, help_text="Monto del descuento aplicable.")
    c_ObjetoImp = serializers.CharField(max_length=2)
    
    impuestos = ConceptTaxSerializer(many=True, required=False)
    aCuentaTerceros = ThirdPartyAccountSerializer(required=False)
    informacionAduanera = ConceptCustomsInformationSerializer(many=True, required=False)
    cuentaPredial = PropertyTaxAccountSerializer(required=False)
    complementoConcepto = ConceptComplementSerializer(required=False)
    parte = PartSerializer(many=True, required=False)

    class Meta:
        model = Conceptos
        exclude = ('comprobante',)
    
class CFIIIssuanceInputSerializer(serializers.Serializer): # EmisionCFDIInputSerializer
    informacionFiscal_id = serializers.IntegerField(help_text="ID de la InformacionFiscal del emisor.")

    version = serializers.CharField(default='4.0', max_length=10) 
    serie = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)
    folio = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)
    fechaEmision = serializers.DateTimeField() 
    fechaPago = serializers.DateTimeField() 
    c_FormaPago = serializers.CharField(max_length=2, required=False, allow_null=True)
    condicionesDePago = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True) 
    subTotal = serializers.DecimalField(max_digits=18, decimal_places=6)
    subTotal = serializers.DecimalField(max_digits=18, decimal_places=2) 
    descuento = serializers.DecimalField(max_digits=18, decimal_places=2, required=False, allow_null=True) 
    c_Moneda = serializers.CharField(max_length=3, source="c_Moneda_id")
    tipoCambio = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True) 
    total = serializers.DecimalField(max_digits=18, decimal_places=2) 
    c_TipoDeComprobante = serializers.CharField(max_length=1)
    c_Exportacion = serializers.CharField(max_length=3, source="c_Exportacion_id")
    c_MetodoPago = serializers.CharField(max_length=3, required=False, allow_null=True)
    c_LugarExpedicion = serializers.CharField(max_length=5,required=False, allow_null=True)
    confirmacion = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True) 

    informacionGlobal = GlobalInformationSerializer(required=False, allow_null=True) 
    cfdiRelacionados = RelatedCFDISerializer(many=True, required=False) 
    emisor = IssuerSerializer() 
    receptor = ReceiverSerializer() 
    conceptos = ConceptCFDIIsuaanceImputSerializer(many=True)
    impuestosTotales = TotalTaxesSerializer(required=False, allow_null=True) 


    def validate_c_Moneda_id(self, value):
        initial_data = self.get_initial()
        exchange_rate = initial_data.get('tipoCambio') 

        if value == "MXN":
            if exchange_rate is not None and Decimal(str(exchange_rate)) != Decimal("1.000000"):
                raise serializers.ValidationError(
                    {"tipoCambio": "Tipo de cambio debe ser 1.000000 para MXN o no especificarse."}
                )
        elif not exchange_rate:
            raise serializers.ValidationError(
                {"tipoCambio": "Tipo de cambio es requerido para monedas distintas a MXN."}
            )
        return value

    def validate(self, data):
        subtotal_val = data.get('subTotal', Decimal('0.00')) 
        discount_val = data.get('descuento', Decimal('0.00')) 
        # expected_total_before_tax = subtotal_val - discount_val
        # Further validation logic here
        return data

class CFIIIssuanceOutputSerializer(serializers.Serializer): # EmisionCFDIOutputSerializer
    success = serializers.BooleanField()
    message = serializers.CharField()
    uuid = serializers.CharField(required=False, allow_null=True)
    xml_timbrado_url = serializers.CharField(required=False, allow_null=True)
    pdf_url = serializers.CharField(required=False, allow_null=True)
    comprobante_emitido_id = serializers.IntegerField(required=False, allow_null=True) 
    error_details = serializers.JSONField(required=False, allow_null=True)
