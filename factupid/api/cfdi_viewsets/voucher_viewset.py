from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from cfdi.models import Comprobante, InformacionFiscal, Emisor, Receptor, Conceptos, ImpuestosTotales  # Importa tus modelos
from ..serializers import VoucherSerializer, IssuerCFDISerializer, ReceiverCFDISerializer, ConceptSerializer, TaxSerializer  # Necesitarás crear un serializador
from django.shortcuts import get_object_or_404

class ComprobanteViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Comprobantes to be viewed or edited.
    """
    serializer_class = VoucherSerializer
    permission_classes = [permissions.IsAuthenticated]  # Asegura que solo usuarios autenticados puedan acceder

    def get_queryset(self):
        """
        Filtra los comprobantes para mostrar solo los del usuario actual.
        """
        try:
            informacion_fiscal = InformacionFiscal.objects.get(idUserCFDI__idUserCFDI=self.request.user)
            return Comprobante.objects.filter(informacionFiscal=informacion_fiscal)
        except InformacionFiscal.DoesNotExist:
            return Comprobante.objects.none()  # O devuelve un error indicando que el usuario no tiene información fiscal

    def perform_create(self, serializer):
        """
        Asigna automáticamente la información fiscal del usuario al crear un nuevo comprobante.
        """
        try:
            informacion_fiscal = InformacionFiscal.objects.get(idUserCFDI__idUserCFDI=self.request.user, es_principal=True)
            serializer.save(informacionFiscal=informacion_fiscal)
        except InformacionFiscal.DoesNotExist:
            # Maneja el caso en que el usuario no tiene información fiscal o no tiene una marcada como principal
            return Response({"error": "El usuario no tiene información fiscal principal configurada."}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """
        Obtiene un comprobante específico.
        """
        queryset = self.get_queryset()
        comprobante = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(comprobante)
        return Response(serializer.data)

    def update(self, request, pk=None):
        """
        Actualiza un comprobante existente.
        """
        queryset = self.get_queryset()
        comprobante = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(comprobante, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        Elimina un comprobante.
        """
        queryset = self.get_queryset()
        comprobante = get_object_or_404(queryset, pk=pk)
        comprobante.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # Acciones personalizadas (ejemplos)
    @action(detail=True, methods=['get'])
    def detalles(self, request, pk=None):
        """
        Obtiene los detalles de un comprobante, incluyendo Emisor, Receptor, Conceptos, etc.
        """
        comprobante = self.get_object()
        emisor = Emisor.objects.filter(comprobante=comprobante).first()
        receptor = Receptor.objects.filter(comprobante=comprobante).first()
        conceptos = Conceptos.objects.filter(comprobante=comprobante)
        impuestos_totales = ImpuestosTotales.objects.filter(comprobante=comprobante).first()

        # Serializa los datos adicionales como sea necesario (crea serializadores para Emisor, Receptor, etc.)
        #  ... (asumiendo que tienes los serializadores creados)
        emisor_data = IssuerCFDISerializer(emisor).data if emisor else None
        receptor_data = ReceiverCFDISerializer(receptor).data if receptor else None
        conceptos_data = ConceptSerializer(conceptos, many=True).data if conceptos else []
        impuestos_data = TaxSerializer(impuestos_totales).data if impuestos_totales else None

        return Response({
            'comprobante': self.get_serializer(comprobante).data,
            'emisor': emisor_data,
            'receptor': receptor_data,
            'conceptos': conceptos_data,
            'impuestos_totales': impuestos_data,
            # ... incluye otros datos del comprobante
        })

    @action(detail=False, methods=['post'])
    def crear_con_detalles(self, request):
        """
        Crea un comprobante con todos los detalles (Emisor, Receptor, Conceptos, etc.) en una sola solicitud.
        """
        comprobante_data = request.data.get('comprobante')
        emisor_data = request.data.get('emisor')
        receptor_data = request.data.get('receptor')
        conceptos_data = request.data.get('conceptos', [])
        impuestos_totales_data = request.data.get('impuestos_totales')
        # ... otros datos

        #  Validar y crear el comprobante base (similar a `perform_create`, pero más completo)
        # ... lógica de validación y creación aquí ...
        try:
            informacion_fiscal = InformacionFiscal.objects.get(idUserCFDI__idUserCFDI=self.request.user, es_principal=True)
            comprobante_serializer = self.get_serializer(data=comprobante_data)
            if comprobante_serializer.is_valid():
                comprobante = comprobante_serializer.save(informacionFiscal=informacion_fiscal)
            else:
                return Response(comprobante_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except InformacionFiscal.DoesNotExist:
            return Response({"error": "El usuario no tiene información fiscal principal configurada."}, status=status.HTTP_400_BAD_REQUEST)

        # Crear Emisor, Receptor, etc., asociándolos al comprobante
        # ... (utiliza tus serializadores y lógica de creación)
        if emisor_data:
            emisor_serializer = IssuerCFDISerializer(data=emisor_data)
            if emisor_serializer.is_valid():
                emisor_serializer.save(comprobante=comprobante)
            else:
                comprobante.delete()  # Si hay error, elimina el comprobante para evitar inconsistencias
                return Response(emisor_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if receptor_data:
            receptor_serializer = ReceiverCFDISerializer(data=receptor_data)
            if receptor_serializer.is_valid():
                receptor_serializer.save(comprobante=comprobante)
            else:
                comprobante.delete()
                return Response(receptor_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # ... Crea Conceptos, ImpuestosTotales, y otros datos de manera similar ...
        for concepto_data in conceptos_data:
            concepto_serializer = ConceptSerializer(data=concepto_data)
            if concepto_serializer.is_valid():
                concepto_serializer.save(comprobante=comprobante)
            else:
                comprobante.delete()
                return Response(concepto_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # .... y así para todos los otros elementos

        if impuestos_totales_data:
            impuestos_serializer = TaxSerializer(data=impuestos_totales_data)
            if impuestos_serializer.is_valid():
                impuestos_serializer.save(comprobante=comprobante)
            else:
                comprobante.delete()
                return Response(impuestos_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(VoucherSerializer(comprobante).data, status=status.HTTP_201_CREATED)
