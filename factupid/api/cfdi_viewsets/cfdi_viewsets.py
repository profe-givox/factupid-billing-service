from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from cfdi.models import *
from ..serializers import *

# --- Viewsets para los perfiles fiscales -------------------------------------
class TaxRegimeViewSet(viewsets.ModelViewSet):
    queryset = RegimenFiscal.objects.all()
    serializer_class = TaxRegimeSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

class CFDIVersionViewSet(viewsets.ModelViewSet):
    queryset = VersionCFDI.objects.all()
    serializer_class = CFDIVersionSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    

class FiscalInformationViewSet(viewsets.ModelViewSet):
    queryset = InformacionFiscal.objects.all()
    serializer_class = FiscalInformationSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    
    
    def get_queryset(self):
        return InformacionFiscal.objects.filter(user=self.request.user)
    
class DigitalStampCertificateViewSet(viewsets.ModelViewSet):
    queryset = CertificadoSelloDigital.objects.all()
    serializer_class = DigitalStampCertificateSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    
    def get_queryset(self):
        return CertificadoSelloDigital.objects.filter(user=self.request.user)
    
class EmitedReceiptViewSet(viewsets.ModelViewSet):
    queryset = ComprobanteEmitido.objects.all()
    serializer_class = EmitedReceiptSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    
    def get_queryset(self):
        return ComprobanteEmitido.objects.filter(user=self.request.user)

# --- Viewsets para facturacion electronica ------------------------------------

class ElectronicInvoiceDraftViewSet(viewsets.ModelViewSet):
    queryset = FacturaElectronicaBorrador.objects.all()
    serializer_class = ElectronicInvoiceDraftSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    
    def get_queryset(self):
        return FacturaElectronicaBorrador.objects.filter(user=self.request.user)
    
class TypeReceiptViewSet(viewsets.ModelViewSet):
    queryset = TipoComprobante.objects.all()
    serializer_class = TypeReceiptSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

class IssuerCFDIViewSet(viewsets.ModelViewSet):
    queryset = Emisor.objects.all()
    serializer_class = IssuerCFDISerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

class ReceiverCFDIViewSet(viewsets.ModelViewSet):
    queryset = Receptor.objects.all()
    serializer_class = ReceiverCFDISerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

class UseCFDIViewSet(viewsets.ModelViewSet):
    queryset = UsoCFDI.objects.all()
    serializer_class = UseCFDISerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

class RelatedVouchersViewSet(viewsets.ModelViewSet):
    queryset = ComprobantesRelacionados.objects.all()
    serializer_class = RelatedVouchersSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

class TypeRelationViewSet(viewsets.ModelViewSet):
    queryset = TipoRelacion.objects.all()
    serializer_class = TypeRelationSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    
class OriginCFDIViewSet(viewsets.ModelViewSet):
    queryset = origenCFDI.objects.all()
    serializer_class = OriginCFDISerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

class FiscalLegendViewSet(viewsets.ModelViewSet):
    queryset = LeyendasFiscales.objects.all()
    serializer_class = FiscalLegendSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

class ConceptViewSet(viewsets.ModelViewSet):
    queryset = Conceptos.objects.all()
    serializer_class = ConceptSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

class UnitKeyViewSet(viewsets.ModelViewSet):
    queryset = ClaveUnidad.objects.all()
    serializer_class = UnitKeySerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

class ProServKeyViewSet(viewsets.ModelViewSet):
    queryset = ClaveProdServ.objects.all()
    serializer_class = ProServKeySerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

class TaxViewSet(viewsets.ModelViewSet):
    queryset = Impuesto.objects.all()
    serializer_class = TaxSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

class ObjectImpViewSet(viewsets.ModelViewSet):
    queryset = ObjetoImp.objects.all()
    serializer_class = ObjectImpSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

class GlobalInformationViewSet(viewsets.ModelViewSet):
    queryset = InformacionGlobal.objects.all()
    serializer_class = GlobalInformationSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

class MonthsViewSet(viewsets.ModelViewSet):
    queryset = Meses.objects.all()
    serializer_class = MonthsSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

class PeriodicityViewSet(viewsets.ModelViewSet):
    queryset = Periodicidad.objects.all()
    serializer_class = PeriodicitySerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

class PaymentInformationViewSet(viewsets.ModelViewSet):
    queryset = InformacionPago.objects.all()
    serializer_class = PaymentInformationSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

class PaymentFormViewSet(viewsets.ModelViewSet):
    queryset = FormaPago.objects.all()
    serializer_class = PaymentFormSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

class PaymentMethodViewSet(viewsets.ModelViewSet):
    queryset = MetodoPago.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

class CurrencyViewSet(viewsets.ModelViewSet):
    queryset = Moneda.objects.all()
    serializer_class = CurrencySerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]