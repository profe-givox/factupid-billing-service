import re

from django.contrib.admin import AdminSite, ModelAdmin
from django.utils.html import format_html
from django.urls import path, reverse, reverse_lazy
from .models import *
from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from datetime import date
from django.http import HttpRequest, HttpResponse, HttpResponseNotFound, JsonResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from django.http import HttpResponse
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
import xml.dom.minidom as minidom
from django.http import HttpResponse
from lxml import etree
from cfdi.models import ComprobanteNomina12, Nomina
from satcfdi.create.cfd.cfdi40 import Comprobante
from django.http import HttpResponse
from satcfdi.create.cfd.cfdi40 import Comprobante as CFDIComprobante
from django.utils.timezone import make_aware
from lxml import etree

from cfdi.models import ComprobanteNomina12, Nomina

from decimal import Decimal
from satcfdi.models import Signer
from satcfdi.create.cfd import cfdi40
import os
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages as django_messages  # Asegurar importación correcta
import nested_admin  # Importar la biblioteca nested_admin para NestedModelAdmin

import sqlite3

conn = sqlite3.connect('db.sqlite3', check_same_thread=False)
from cfdi.views import obtener_datos_comprobante_nomina12, obtener_datos_factura
from satcfdi import render
from weasyprint import HTML
import base64
from app.views import SoapService
from cfdi.pdf_utils import render_comprobante_pdf_bytes

import xml.etree.ElementTree as ET
from datetime import datetime
import json
from django.db.models import Subquery, OuterRef
from satcfdi.cfdi import CFDI

from django.db import transaction
import traceback
from cfdi.forms import *
from django.utils.safestring import mark_safe
from lxml import etree
import base64
from datetime import datetime
import xml.etree.ElementTree as ET
from django.shortcuts import redirect
from django.core.exceptions import ValidationError
from cfdi.models import UsersCFDI, ComprobanteEmitido
from . import views
from django.db.models import Max
from django.contrib.auth.models import Group as AuthGroup, Permission
# Importar las bibliotecas necesarias para manejar certificados y claves
from cryptography.x509.oid import ExtensionOID
from cryptography.x509.oid import NameOID
from cryptography import x509
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_der_private_key
from cryptography.hazmat.backends import default_backend
from OpenSSL import crypto
from datetime import datetime as dt, timezone
import os
from console.models import User_Service, Service_Plan
import json  # Asegúrate de importar esto al inicio del archivo

from django.utils import timezone as dj_timezone
from django.db.models import Sum
from django.core.mail import EmailMessage
from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse
import io

from django.contrib.auth.hashers import identify_hasher
from django.contrib.auth.models import Group
from cfdi.context_processor import *
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import Group, Permission
from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.utils.html import escape
# Agrega permisos del modelo User si el usuario los tiene
from django.contrib.contenttypes.models import ContentType
from django.forms.models import model_to_dict
#puedes importar el dj_timezone
from datetime import timezone as py_timezone
from invoice.views import RegisterService


User = get_user_model()

from django.views.decorators.http import require_GET




NOMINA_AUTOCOMPLETE_FIELDS = [
    'curp',
    'rfc_patron_origen',
    'entidad_sncf',
    'origen_recurso',
    'monto_recurso_propio',
    'rfc_trabajador',
    'curp_trabajador',
    'numero_empleado',
    'numero_seguro_social',
    'registro_patronal',
    'nombre',
    'apellido_paterno',
    'apellido_materno',
    'genero',
    'entidad_presto_servicio',
    'calle',
    'numero_exterior',
    'numero_interior',
    'colonia',
    'ciudad',
    'municipio',
    'estado',
    'pais',
    'c_CodigoPostal',
    'referencia',
    'clave_pais',
    'c_ResidenciaFiscal',
    'telefono',
    'correo_electronico',
    'fecha_inicio_relacion_laboral',
    'tipo_regimen',
    'departamento',
    'sindicalizado',
    'puesto',
    'riesgo_puesto',
    'tipo_contrato',
    'tipo_jornada',
    'salario_base',
    'salario_diario',
    'banco',
    'periodicidad',
    'cuenta_bancaria',
    'numero_dias_pagados',
    'fecha_pago',
    'fecha_inicial_pago',
    'fecha_final_pago',
    'tipo_nomina',
]


def _serialize_value(value):
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    return value


def _serialize_from_mapping(obj, field_map):
    serialized = {}
    for field_name, attr_name in field_map.items():
        value = getattr(obj, attr_name)
        serialized[field_name] = _serialize_value(value)
    return serialized


def _iter_related_source(source):
    if not source:
        return []
    if hasattr(source, 'all'):
        return source.all()
    return source


def _serialize_related_records(field_map, *sources):
    serialized = []
    seen_pks = set()
    for source in sources:
        for related_obj in _iter_related_source(source):
            if related_obj is None:
                continue
            pk = getattr(related_obj, 'pk', None)
            if pk is not None:
                if pk in seen_pks:
                    continue
                seen_pks.add(pk)
            serialized.append(_serialize_from_mapping(related_obj, field_map))
    return serialized


def _serialize_nomina(nomina):
    data = model_to_dict(nomina, fields=NOMINA_AUTOCOMPLETE_FIELDS)
    serialized = {}
    for key, value in data.items():
        serialized[key] = _serialize_value(value)
    return serialized


@require_GET
def nomina_autocomplete(request):
    term = request.GET.get('term', '').strip()
    field = request.GET.get('field')

    if not request.user.is_authenticated:
        return JsonResponse({'results': []})

    if not term or field not in {'rfc_trabajador', 'curp_trabajador'}:
        return JsonResponse({'results': []})

    filter_kwargs = {f"{field}__icontains": term}
    queryset = (
        Nomina.objects
        .filter(**filter_kwargs)
        .exclude(**{f"{field}__isnull": True})
        .exclude(**{field: ''})
        .order_by(field)[:10]
    )

    results = []
    for nomina in queryset:
        value = getattr(nomina, field, '')
        if not value:
            continue

        fields_data = _serialize_nomina(nomina)
        full_name = " ".join(filter(None, [nomina.nombre, nomina.apellido_paterno, nomina.apellido_materno])).strip()

        alternate_identifier = nomina.curp_trabajador if field == 'rfc_trabajador' else nomina.rfc_trabajador
        label_parts = [value]
        if alternate_identifier:
            label_parts.append(alternate_identifier)
        if full_name:
            label_parts.append(full_name)

        percepciones_data = _serialize_related_records(
            {
                'comprobanteNomina12': 'comprobanteNomina12_id',
                'nomina': 'nomina_id',
                'tipo_percepcion': 'tipo_percepcion_id',
                'clave': 'clave',
                'importe_exento': 'importe_exento',
                'importe_gravado': 'importe_gravado',
            },
            nomina.percepciones,
            nomina.comprobanteNomina12.nominaPercepciones if nomina.comprobanteNomina12_id else None,
        )

        deducciones_data = _serialize_related_records(
            {
                'comprobanteNomina12': 'comprobanteNomina12_id',
                'nomina': 'nomina_id',
                'tipo_deduccion': 'tipo_deduccion_id',
                'clave': 'clave',
                'importe': 'importe',
            },
            nomina.deducciones,
            nomina.comprobanteNomina12.nominaDeducciones if nomina.comprobanteNomina12_id else None,
        )

        otros_pagos_data = _serialize_related_records(
            {
                'comprobanteNomina12': 'comprobanteNomina12_id',
                'nomina': 'nomina_id',
                'tipo_otro_pago': 'tipo_otro_pago_id',
                'subsidioCausado': 'subsidioCausado',
                'saldoAfavor': 'saldoAfavor',
                'anio': 'anio',
                'remanente': 'remanente',
                'clave': 'clave',
                'importe': 'importe',
            },
            nomina.otros_pagos,
            nomina.comprobanteNomina12.nominaOtrosPagos if nomina.comprobanteNomina12_id else None,
        )

        subcontrataciones_data = _serialize_related_records(
            {
                'comprobanteNomina12': 'comprobanteNomina12_id',
                'rfclaboral': 'rfclaboral',
                'porcentaje': 'porcentaje',
            },
            nomina.comprobanteNomina12.subcontrataciones if nomina.comprobanteNomina12_id else None,
        )

        results.append({
            'id': nomina.pk,
            'value': value,
            'label': " - ".join(label_parts),
            'fields': fields_data,
            'percepciones': percepciones_data,
            'deducciones': deducciones_data,
            'otros_pagos': otros_pagos_data,
            'subcontrataciones': subcontrataciones_data,
        })

    return JsonResponse({'results': results})


class EmailOrUsernameAuthenticationForm(AuthenticationForm):
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        # Si parece un correo, buscar por email
        if '@' in username:
            try:
                user_obj = User.objects.get(email__iexact=username)
                username = user_obj.username
            except User.DoesNotExist:
                pass  # Dejar que el backend lo maneje

        self.cleaned_data['username'] = username
        return super().clean()

class CustomGroupAdminForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.none(),  # se define en __init__
        widget=admin.widgets.FilteredSelectMultiple("Permisos CFDI", is_stacked=False),
        required=False,
        label="Permisos CFDI",
    )

    class Meta:
        model = Group
        fields = ["name", "permissions"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        permisos_cfdi = Permission.objects.filter(content_type__app_label="cfdi")

        if user:
            # Permisos individuales asignados directamente al usuario
            directos = user.user_permissions.all()

            # Permisos heredados por los grupos del usuario
            grupales = Permission.objects.filter(group__user=user)

            # Unión segura con distinct (y sin usar el operador `|`)
            todos_los_permisos = Permission.objects.filter(
                pk__in=(directos | grupales).values_list('pk', flat=True).distinct()
            )

            # Filtra solo los permisos de la app cfdi que el usuario tiene
            permisos_cfdi = todos_los_permisos.filter(content_type__app_label="cfdi")

            # Obtener todos los permisos del modelo 'User'
            try:
                content_type_user = ContentType.objects.get(app_label="auth", model="user")
                permisos_user = todos_los_permisos.filter(content_type=content_type_user)
            except ContentType.DoesNotExist:
                permisos_user = Permission.objects.none()

            # Combinar permisos cfdi + permisos del modelo User si el usuario logueado los tiene
            permisos_finales = (permisos_cfdi | permisos_user).distinct()

            self.fields["permissions"].queryset = permisos_finales.order_by("content_type__model", "codename")
        else:
            self.fields["permissions"].queryset = Permission.objects.none()






class MiAdminSite(AdminSite):
    site_header = "Administracion de negocios"
    site_title = "Panel de Administración"
    index_title = "Bienvenido al Sistema de Información Fiscal"
    login_template = "LadoClientes/pages/login.html"
    index_template = "LadoClientes/pages/index.html"
    login_form = EmailOrUsernameAuthenticationForm
    

    def has_permission(self, request):
        """
        Permite acceso si el usuario pertenece al grupo 'cfdi'
        o si su usuario raíz lo tiene.
        """
        if not request.user.is_authenticated:
            return False

        # 1. Si el usuario directamente tiene el grupo, permitir acceso
        if request.user.groups.filter(name__iexact='cfdi').exists():
            return True

        # 2. Si no, intentar encontrar su usuario raíz y verificar
        try:
            usuario_cfdi = UsersCFDI.objects.get(idUserCFDI=request.user)
            usuario_raiz = usuario_cfdi.get_raiz()
            if usuario_raiz and usuario_raiz.idUserCFDI.groups.filter(name__iexact='cfdi').exists():
                return True
        except UsersCFDI.DoesNotExist:
            pass  # Si no tiene perfil CFDI, no se permite

        return False
    
    

    def index(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}

        chart_data = []
        try:
            user_cfdi_profile = UsersCFDI.objects.get(idUserCFDI=request.user)
            user_cfdi_profile = user_cfdi_profile.get_raiz()
            issued = ComprobanteEmitido.objects.filter(
                idUserCFDI=user_cfdi_profile
            ).order_by('-fecha')[:10]

            for c in issued:
                if c.fecha and c.total is not None:
                    chart_data.append({
                        'name': c.nombre or "Sin nombre",
                        'fecha': c.fecha.strftime('%Y-%m-%d'),
                        'total': float(c.total) if c.total else 0,
                    })

            now = dj_timezone.now()
            monthly_qs = ComprobanteEmitido.objects.filter(
                idUserCFDI=user_cfdi_profile,
                fecha__year=now.year,
                fecha__month=now.month,
            )

            movimientos = {}
            montos = {}
            tipo_map = [
                ('I', 'ingresos'),
                ('E', 'egresos'),
                ('T', 'traslado'),
                ('N', 'nomina'),
                ('P', 'pagos'),
                ('G', 'gastos'),
            ]
            for code, key in tipo_map:
                qs = monthly_qs.filter(
                    comprobante_relacionado__c_TipoDeComprobante__c_TipoDeComprobante=code
                )
                movimientos[key] = qs.count()
                montos[key] = qs.aggregate(total=Sum('total'))['total'] or Decimal('0')
            movimientos['total'] = sum(movimientos.values())
            montos['total'] = sum(montos.values(), Decimal('0'))
            extra_context['montos'] = montos

            extra_context['movimientos'] = movimientos
            extra_context['issued'] = issued
        except UsersCFDI.DoesNotExist:
            chart_data = []

        extra_context['chart_data_json'] = json.dumps(chart_data)
        return super().index(request, extra_context=extra_context)



    def LadoClientes_comprobanteemitido_changedelete(self, request: HttpRequest, pk):
        """ Elimina un objeto comprobante emitido y redirige a la lista de ComprobanteEmitido en el admin. """
        try:
            obj = ComprobanteEmitido.objects.get(pk=pk)
            obj.delete()

            # Agrega un mensaje de éxito al usuario administrado
            if hasattr(request, 'session'):  # Asegura que el request es válido para mensajes
                django_messages.success(request, f"El comprobante emitido {obj.folio} ha sido eliminado exitosamente.")

            # Redirigir a la vista de lista de ComprobanteEmitido en el admin
            return redirect(reverse_lazy('mi_admin:cfdi_comprobanteemitido_changelist'))

        except ComprobanteEmitido.DoesNotExist:
            if hasattr(request, 'session'):
                django_messages.error(request, "El comprobante emitido no existe.")
            return HttpResponseNotFound("El comprobante emitido no existe.")

    
    def get_urls(self):
        """
        Agrega una URL personalizada además de las predeterminadas del admin.
        """
        urls = super().get_urls()
        custom_urls = [
            path(
                'comprobante-emitido/eliminar/<int:pk>/',
                self.admin_view(self.LadoClientes_comprobanteemitido_changedelete),  # Protegido para admin
                name='LadoClientes_comprobanteemitido_delete'
            ),
            path(
                'nomina/autocomplete/',
                self.admin_view(nomina_autocomplete),
                name='nomina_autocomplete'
            ),
              path('manifiesto/', views.manifiesto, name='manifiesto'),
            path('manifiesto/contrato/', views.manifiesto_contrato, name='manifiesto_contrato'),
            path('manifiesto/contrato/wizard/', views.manifiesto_contrato_wizard, name='manifiesto_contrato_wizard'),
            path('manifiesto/contrato/wizard/estado/', views.manifiesto_contrato_wizard_estado, name='manifiesto_contrato_wizard_estado'),
            path(
                'manifiesto/contrato/wizard/descargar/<str:tipo>/<str:rfc>/',
                views.manifiesto_contrato_wizard_descargar,
                name='manifiesto_wizard_descargar'
            ),
            path('manifiesto/contrato/qr/', views.manifiesto_contrato_qr, name='manifiesto_contrato_qr'),
            path('manifiesto/firmar/', views.firmar_manifiesto, name='firmar_manifiesto'),
            path('manifiesto/contrato/firmar/', views.manifiesto_contrato_firmar, name='manifiesto_firmar'),
            path('manifiesto/contrato/descargar/xml/', views.manifiesto_contrato_descargar_xml, name='manifiesto_descargar_xml'),
            path('manifiesto/contrato/descargar/pdf/', views.manifiesto_contrato_descargar_pdf, name='manifiesto_descargar_pdf'),
            path('manifiesto/contrato/descargar/privacidad/', views.manifiesto_contrato_descargar_privacidad, name='manifiesto_descargar_privacidad'),
            path('manifiesto/contrato/descargar/servicio/', views.manifiesto_contrato_descargar_servicio, name='manifiesto_descargar_servicio'),
            path('register/', views.register, name='registrarse'),
            path('editor/', views.editor, name='editor'),
            path('editor/get-modelos/', views.ModeloDePlantilla, name='get_modelos'),
            path('editor/get-usuario/', views.ModeloDeUsuario, name='get_usuario'),
            path('editor/get-plantilla/<int:id>/', views.getPlantilla, name='getPlantilla'),
            path('editor/crear-modelo/', views.crearModelo, name='crearModelo'),
            path('editor/saveas/', views.GuardarComo, name='GuardarComo'),
            path('editor/save/', views.savePlantilla, name='savePlantilla'),
            path('editor/drop/', views.dropPlantilla, name='dropPlantilla'),
            path('plantillas/Getpdf/<int:id>/<int:tipo>', views.getPDF, name='getPDF'),
            path('plantillas/imprimirPDF/<int:id>/<int:tipo>', views.imprimirPDF, name='imprimirPDF'),
            path('editor/subir_imagen/', views.subir_imagen, name='subir_imagen'),
            path('editor/elegir_plantilla/', views.ElegirPlantilla, name='set_plantilla'),
            path('editor-pdf/', views.personalizar_pdf, name='personalizar_pdf'),
            path('editor-pdf/listar/', views.listar_pdf_personalizados, name='listar_pdf_personalizado'),
            path('editor-pdf/<int:pk>/', views.obtener_pdf_personalizado, name='obtener_pdf_personalizado'),
            path('editor-pdf/guardar/', views.guardar_pdf_personalizado, name='guardar_pdf_personalizado'),
            path('editor-pdf/exportar/', views.exportar_pdf_personalizado, name='exportar_pdf_personalizado'),
        ]
        return custom_urls + urls

# Instancia del admin personalizado
mi_admin_site = MiAdminSite(name='mi_admin')



class GroupCRUD(admin.ModelAdmin):
    delete_confirmation_template = 'LadoClientes/forms/delete_confirmation.html'  # Ruta a tu plantilla personalizada
    delete_selected_confirmation_template = 'LadoClientes/forms/delete_selected_confirmation.html'
    index_template = 'LadoClientes/pages/index.html'
    change_list_template = 'LadoClientes/forms/change_list.html'
    change_form_template = 'LadoClientes/pages/manage_groups.html'


    form = CustomGroupAdminForm
    
    def get_queryset(self, request):
        """
        Solo mostrar GruposCFDI que fueron creados por el usuario actual,
        según lo registrado en GroupMeta.
        """
        qs = super().get_queryset(request)

        # Filtra solo los grupos AUTH vinculados con GroupMeta del usuario
        grupos_ids = GroupMeta.objects.filter(created_by=request.user).values_list('group__name', flat=True)

        # Como el modelo GruposCFDI usa el mismo nombre que Group (auth), filtramos por nombre
        return qs.filter(name__in=grupos_ids)


    # def get_form(self, request, obj=None, **kwargs):
    #     """Asegurar que los permisos se pasen al contexto correctamente."""
    #     form = super().get_form(request, obj, **kwargs)
    #     form.base_fields['permissions'].queryset = Permission.objects.all()
    #     return form
    
    def get_form(self, request, obj=None, **kwargs):
        kwargs['form'] = self.form
        form_class = super().get_form(request, obj, **kwargs)

        class FormWithUser(form_class):
            def __init__(self2, *args, **inner_kwargs):
                inner_kwargs['user'] = request.user  # 👈 Pasa el usuario al form
                super().__init__(*args, **inner_kwargs)

        return FormWithUser


    def get_context_data(self, request, obj=None):
        """Pasar los permisos disponibles y elegidos al contexto de la plantilla."""
        context = super().get_changeform_initial_data(request)
        context['available_permissions'] = Permission.objects.all()
        if obj:
            context['chosen_permissions'] = obj.permissions.all()
        else:
            context['chosen_permissions'] = []
        return context

    def save_model(self, request, obj, form, change):
        """
        1) Guarda el GruposCFDI (obj).
        2) Asegura un Group (auth) espejo por nombre.
        3) Sincroniza permisos.
        4) Crea GroupMeta con .create(...) la primera vez; en ediciones solo actualiza updated_by.
        """
        with transaction.atomic():
            # 1) Guarda el proxy/CFDI
            super().save_model(request, obj, form, change)

            # 2) Asegura el Group "real" de Django emparejado por nombre
            auth_group, created_auth = AuthGroup.objects.get_or_create(name=obj.name)

            # 3) Sincroniza permisos del CFDI al Group real
            #    (si vienes de un form, úsalo; si no, usa el M2M del obj)
            if form and 'permissions' in form.cleaned_data:
                auth_group.permissions.set(form.cleaned_data['permissions'])
            else:
                auth_group.permissions.set(obj.permissions.all())

            # 4) Crea/actualiza GroupMeta con estilo ".create(...)"
            #    Si NO existe, CREAR como tu ejemplo 'objects.create(...)'
            if not GroupMeta.objects.filter(group=auth_group).exists():
                GroupMeta.objects.create(
                    group=auth_group,
                    created_by=request.user,
                    updated_by=request.user,
                )
            else:
                meta = GroupMeta.objects.get(group=auth_group)
                meta.updated_by = request.user
                meta.save(update_fields=['updated_by', 'updated_at'])

    


mi_admin_site.register(GruposCFDI, GroupCRUD)





    





class GroupAdmin(admin.ModelAdmin):
    index_template = 'LadoClientes/pages/index.html'
    change_list_template = 'LadoClientes/forms/change_listUsuariosGrupos.html'
    change_form_template = 'LadoClientes/forms/change_form.html'
    delete_confirmation_template = 'LadoClientes/forms/delete_confirmation.html'  # Ruta a tu plantilla personalizada
    delete_selected_confirmation_template = 'LadoClientes/forms/delete_selected_confirmation.html'


    list_display = ('get_creator', 'get_created_at', 'updated_by')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(created_by=request.user)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        meta, _ = GroupMeta.objects.get_or_create(group=obj)
        if not change and not meta.created_by:
            meta.created_by = request.user
        meta.updated_by = request.user
        meta.save()

    def get_creator(self, obj):
        return getattr(obj.meta, 'created_by', None)
    get_creator.short_description = "Creado por"

    def get_created_at(self, obj):
        return getattr(obj.meta, 'created_at', None)
    get_created_at.short_description = "Creado el"

mi_admin_site.register(GroupMeta, GroupAdmin)

class InformacionFiscalForm(forms.ModelForm):
    class Meta:
        model = InformacionFiscal
        fields = '__all__'
        # NO LO EXCLUYAS
        # exclude = ('token',)

        widgets = {
            'idUserCFDI': forms.HiddenInput(),
            'activo': forms.HiddenInput(),
            
           
        }

        
class InformacionFiscalAdmin(ModelAdmin):
    # Agregamos 'imagen_preview' al list_display
    form = InformacionFiscalForm
    change_form_template = 'negocios/negocios.html'  # Ruta a tu plantilla personalizada
    change_list_template = 'negocios/informacion_fiscal_list.html'  # Ruta a tu plantilla personalizada
    delete_confirmation_template = 'LadoClientes/forms/delete_confirmation.html'  # Ruta a tu plantilla personalizada
    delete_selected_confirmation_template = 'LadoClientes/forms/delete_selected_confirmation.html'  # Ruta a tu plantilla personalizada
    index_template = 'LadoClientes/pages/index.html'
    # list_display = ('imagen_preview', 'nombre', 'rfc', 'curp', 'razon_social', 'activo', 'es_principal')
    # list_filter = ('activo', 'regimen_fiscal', 'regimen_receptor', 'es_principal')
    actions = ['marcar_como_principal']
    search_fields = ('nombre', 'rfc', 'curp', 'razon_social')
    fieldsets = (
        ('Información General', {
            'fields': ('idUserCFDI', 'nombre', 'activo', 'imagen')
        }),
        ('Datos Fiscales', {
            'fields': ('rfc', 'curp', 'razon_social', 'regimen_fiscal', 'regimen_receptor')
        }),
        ('Domicilio', {
            'fields': ('calle', 'numero_exterior', 'numero_interior', 'colonia', 'ciudad', 'municipio', 'estado', 'pais', 'codigo_postal', 'referencia')
        }),
        ('Datos de Contacto', {
            'fields': ('telefono', 'correo_electronico')
        }),
        ('Validación CFDI', {
            'fields': ('confirmar_datos_cfdi', 'ignorar_validacion_sociedad')
        }),
    )

    actions = ['marcar_como_principal', 'desmarcar_como_principal']


    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        try:
            user_cfdi = UsersCFDI.objects.get(idUserCFDI=request.user)
            usuario_raiz = user_cfdi.get_raiz()
        except UsersCFDI.DoesNotExist:
            return qs.none()

        # # Obtener el usuario actual y todos sus hijos directos (nivel 1)
        # usuarios_hijos = UsersCFDI.objects.filter(userParent=user_cfdi)
        # print(f"Usuarios hijos: {usuarios_hijos}")

        # Opcional: incluir al usuario principal también
        return qs.filter(idUserCFDI__in=[usuario_raiz])

    def response_change(self, request, obj):
        """
        Maneja acciones personalizadas al guardar el modelo.
        """
        print(f"Request POST data: {request.POST}")  # Debug: Verifica los datos del POST
        if "_facturar_timbrar" in request.POST:
            return self.facturar_y_timbrar(request, obj)
        if "_generar_pdf" in request.POST:
            return self.generar_pdf(request, obj)
        
        if "_save" in request.POST:
            return super().response_change(request, obj)

        if "_save_draft" in request.POST:  # Detectar si se presionó el botón "Guardar borrador". _save_draft es el boton vinculado con la plantilla change_form.html de django admin
            return super().response_change(request, obj)
        
        return super().response_change(request, obj)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        print(f"Request POST data in change_view: {request.POST}")  # Debug: Verifica los datos del POST
        if request.method == "POST":

            # 🔹 Si se presionó el botón 'Facturar y Timbrar', redirigir manualmente a `response_change()`
            if "_facturar_timbrar" in request.POST:
                return self.response_change(request, self.get_object(request, object_id))
            
            if "_generar_pdf" in request.POST:
                return self.response_change(request, self.get_object(request, object_id))
            
            if "_save_draft" in request.POST:
                return self.response_change(request, self.get_object(request, object_id))

        return super().change_view(request, object_id, form_url, extra_context)
    
    def save_model(self, request, obj, form, change):
        """
        Asegura que al crear un objeto, se asocie automáticamente al usuario logueado.
        """
        es_nuevo = not change
        
        if not change:  # Si es un objeto nuevo
            user_cfdi = UsersCFDI.objects.get(idUserCFDI=request.user)
            usuario_raiz = user_cfdi.get_raiz()
            obj.idUserCFDI = usuario_raiz
        super().save_model(request, obj, form, change)
        
         # Solo aquí: registro en PAC
        if es_nuevo:
            # Asignar como negocio activo automáticamente
            try:
                usuario_cfdi = UsersCFDI.objects.get(idUserCFDI=request.user)
                usuario_raiz = usuario_cfdi.get_raiz()

                usuario_cfdi.negocio_activo = obj   # el nuevo negocio recién creado
                usuario_cfdi.save()

                print(f"Negocio activo asignado automáticamente: {obj}")

            except UsersCFDI.DoesNotExist:
                print("⚠ No se encontró UsersCFDI para el usuario al crear información fiscal.")

            # Registrar en PAC
            self.registrar_en_pac(obj, request)
        
    def registrar_en_pac(self, obj, request):
        
        try:
            user_cfdi = UsersCFDI.objects.get(idUserCFDI=request.user)
            usuario_raiz = user_cfdi.get_raiz()
            user_services = usuario_raiz.idUserServicePlan_id
            service_plan  = user_services.idServicePlan
            # Descargar .cer y .key como base64
            ctx = ''
            key_base64 = ''
            cer_base64 = ''
            passh = ''


            # Llamada SOAP
            response = RegisterService.add(
                ctx,
                service_plan.supplierStamp.user,
                service_plan.supplierStamp.decrypt_password(),
                obj.rfc,
                'O',
                cer_base64,
                key_base64,
                passh
            )
            
            print(f"Respuesta PAC: {response}")

            if response.success:
                messages.success(request, f"Usuario registrado en PAC: {response.message}")
            else:
                messages.error(request, f"Error PAC: {response.message}")

        except Exception as exc:
            messages.error(request, f"Error al registrar en PAC: {exc}")


mi_admin_site.register(InformacionFiscal, InformacionFiscalAdmin)




class NominaInlineForm(forms.ModelForm):
    class Meta:
        model = Nomina
        fields = '__all__'

    class Media:
        js = ('js/nomina_autocomplete.js',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        autocomplete_url = reverse_lazy('mi_admin:nomina_autocomplete')
        for field_name in ('rfc_trabajador', 'curp_trabajador'):
            if field_name in self.fields:
                css_class = self.fields[field_name].widget.attrs.get('class', '')
                css_class = f"{css_class} nomina-autocomplete".strip()
                self.fields[field_name].widget.attrs.update({
                    'data-autocomplete-url': str(autocomplete_url),
                    'data-autocomplete-field': field_name,
                    'autocomplete': 'off',
                    'class': css_class,
                })


class nominaInline(nested_admin.NestedStackedInline):   
    model = Nomina
    form = NominaInlineForm
    extra = 1
    max_num = 1  # Solo se permite un formulario
    autocomplete_fields = ['c_CodigoPostal', 'c_ResidenciaFiscal', 'banco','entidad_presto_servicio']

class EstadoAdmin(admin.ModelAdmin):
    search_fields = ['c_Estado', 'nombre', 'c_Pais__c_Pais', 'c_Pais__descripcion']
    list_display = ['c_Estado', 'nombre', 'c_Pais']
    ordering = ['c_Estado']







class TipoComprobanteForm(forms.ModelForm):
    class Meta:
        model = TipoComprobante
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        inicio = cleaned_data.get('fecha_inicio_vigencia')
        fin = cleaned_data.get('fecha_fin_vigencia')
        if inicio and fin and fin < inicio:
            self.add_error("fecha_fin_vigencia", "La fecha de fin de vigencia no puede ser anterior a la fecha de inicio.")
        if cleaned_data.get('c_TipoDeComprobante') not in ['I', 'E', 'T', 'N', 'P']:
            self.add_error("c_TipoDeComprobante", "El tipo de comprobante debe ser uno de los valores permitidos: I, E, T, N, P.")
        return cleaned_data




class TipoComprobanteInline(nested_admin.NestedTabularInline):
    model = TipoComprobante
     # form = TipoComprobanteForm
    extra = 1
    max_num = 1
    fields = (
        'c_TipoDeComprobante',
        'descripcion',
        'valor_maximo',
        'valor_maximoNS',
        'valor_maximoNDS',
        'fecha_inicio_vigencia',
        'fecha_fin_vigencia'
    )





# class InformacionPagoInline(nested_admin.NestedTabularInline):
#     model = InformacionPago  # Relación con el modelo definido arriba
#     extra = 1
#    max_num = 1  # Solo se permite un formulario  # numero de filas extra a mostrar
#     fields = ('Metodopago', 'Formapago', 'Fechapago', 'Moneda', 'Tipocambio','Condicionespago')

class InformacionPagoForm(forms.ModelForm):
    class Meta:
        model = InformacionPago
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        metodo_pago = cleaned_data.get('Metodopago')
        moneda = cleaned_data.get('Moneda')
        tipo_cambio = cleaned_data.get('Tipocambio')
        if metodo_pago not in ['PUE', 'PPD']:
            self.add_error("Metodopago", "El Método de Pago debe ser 'PUE' o 'PPD'.")
        if moneda != 'MXN' and (not tipo_cambio or tipo_cambio <= 0):
            self.add_error("Tipocambio", "Si la moneda no es 'MXN', el tipo de cambio debe ser mayor a 0.")
        if moneda == 'MXN' and tipo_cambio and tipo_cambio != 1:
            self.add_error("Tipocambio", "El tipo de cambio debe ser 1 para moneda MXN.")
        return cleaned_data




# class InformacionPagoInline(nested_admin.NestedTabularInline):
#     model = InformacionPago
#       # form = InformacionPagoForm
#     extra = 1
#     max_num = 1
#     fields = (
#         'FacturaElectronica',
#         'FacturaNomina12',
#         'FacturaElectronicaBorrador',
#         'Metodopago',
#         'Formapago',
#         'Fechapago',
#         'Moneda',
#         'Tipocambio',
#         'Condicionespago'
#     )




# class ReceptorInline(nested_admin.NestedStackedInline):
#     model = Receptor  # Relación con el modelo definido arriba
#     extra = 1
#   max_num = 1  # Solo se permite un formulario
#     fieldsets = (
#         ('Receptor', {
#             'fields': (
#                 'Rfc', 'Razon_social', 'Nombre', 'Apellido_paterno', 'Apellio_materno',  # Información básica
#                 'Telefono', 'Correo_electronico',  # Contacto
#                 'Calle', 'Numero_exterior', 'Numero_interior', 'Colonia', 'Ciudad', 'Municipio',  # Domicilio
#                 'Estado', 'Pais', 'Codigo_postal', 'Referencia', 'Clave_pais', 'Residencia_fiscal',
#                 'Usocfdi', 'Ignorar_validacion_sociedad', 'Mostrardireccionpdf', 'Regimen_fiscal', 'Registrotributario'  # Información complementaria
#             )
#         }),
#     )



class ReceptorForm(forms.ModelForm):
    class Meta:
        model = Receptor
        fields = '__all__'
        widgets = {
            'rfc': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'RFC'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Razón Social'}),
            'numRegldTrib': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Registro Tributario'}),
            'c_UsoCFDI': forms.Select(attrs={'class': 'form-select'}),
            'c_ResidenciaFiscal': forms.Select(attrs={'class': 'form-select'}),  # aunque sea autocomplete, esto fuerza estilo
            'c_RegimenFiscalReceptor': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        c_ResidenciaFiscal = cleaned_data.get('c_ResidenciaFiscal')
        numRegldTrib = cleaned_data.get('numRegldTrib')
        
        if c_ResidenciaFiscal and c_ResidenciaFiscal.c_Pais != 'MEX' and not numRegldTrib:
            self.add_error('numRegldTrib', "Requerido para receptores extranjeros")
        elif numRegldTrib and (not c_ResidenciaFiscal or c_ResidenciaFiscal.c_Pais == 'MEX'):
            self.add_error('numRegldTrib', "Solo para receptores extranjeros")
        
        print(f"Cleaned data: {cleaned_data}")  # Debug: Verifica los datos limpios
        print(f"errors: {self.errors}")  # Debug: Verifica los valores específicos
        return cleaned_data


class ReceptorInline(nested_admin.NestedTabularInline):
    model = Receptor
    form = ReceptorForm  # ✅ usa el formulario personalizado
    extra = 1
    max_num = 1
    fk_name = 'comprobante'
    autocomplete_fields = ['c_DomicilioFiscalReceptor']  # esto sigue funcionando con widget custom
    verbose_name = "Receptor"
    verbose_name_plural = "Receptores"
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        # Debug: Verifica el management form
        print(formset.management_form)
        return formset



class PaisAdmin(admin.ModelAdmin):
    search_fields = ['c_Pais', 'descripcion']
    list_display = ['c_Pais', 'descripcion']
    ordering = ['c_Pais']


class BancoAdmin(admin.ModelAdmin):
    search_fields = ['c_Banco', 'descripcion', 'razon_social']
    list_display = ['c_Banco', 'descripcion', 'razon_social']
    ordering = ['c_Banco']




class CodigoPostalAdmin(admin.ModelAdmin):

 
    change_form_template = 'LadoClientes/forms/change_form.html'  # Ruta a tu plantilla personalizada
    change_list_template = 'LadoClientes/forms/change_list.html'  # Ruta a tu plantilla personalizada
    delete_confirmation_template = 'LadoClientes/forms/delete_confirmation.html'  # Ruta a tu plantilla personalizada
    delete_selected_confirmation_template = 'LadoClientes/forms/delete_selected_confirmation.html'  # Ruta a tu plantilla personalizada
    index_template = 'LadoClientes/pages/index.html'
    search_fields = ['c_CodigoPostal', 'c_Municipio__descripcion', 'c_Localidad__descripcion']



    def has_view_permission(self, request, obj=None):
        return request.user.is_authenticated
    

mi_admin_site.register(CodigoPostal, CodigoPostalAdmin) 

mi_admin_site.register(Pais, PaisAdmin)
mi_admin_site.register(Banco, BancoAdmin)
mi_admin_site.register(Estado, EstadoAdmin)


class ClaveUnidadAdmin(admin.ModelAdmin):
    change_form_template = 'LadoClientes/forms/change_form.html'  # Ruta a tu plantilla personalizada
    change_list_template = 'LadoClientes/forms/change_list.html'  # Ruta a tu plantilla personalizada
    delete_confirmation_template = 'LadoClientes/forms/delete_confirmation.html'  # Ruta a tu plantilla personalizada
    delete_selected_confirmation_template = 'LadoClientes/forms/delete_selected_confirmation.html'  # Ruta a tu plantilla personalizada
    index_template = 'LadoClientes/pages/index.html'
    search_fields = ['c_ClaveUnidad', 'nombre', 'descripcion', 'nota']  # Permitir búsquedas
    list_display = ['c_ClaveUnidad', 'nombre', 'descripcion', 'nota']
    list_filter = ['fecha_inicio_vigencia', 'fecha_fin_vigencia']

mi_admin_site.register(ClaveUnidad, ClaveUnidadAdmin) 


class ClaveProdServAdmin(admin.ModelAdmin):
    change_form_template = 'LadoClientes/forms/change_form_base.html'  # Ruta a tu plantilla personalizada
    change_list_template = 'LadoClientes/forms/change_list.html'  # Ruta a tu plantilla personalizada
    delete_confirmation_template = 'LadoClientes/forms/delete_confirmation.html'  # Ruta a tu plantilla personalizada
    delete_selected_confirmation_template = 'LadoClientes/forms/delete_selected_confirmation.html'  # Ruta a tu plantilla personalizada
    index_template = 'LadoClientes/pages/index.html'
    search_fields = ['c_ClaveProdServ', 'descripcion', 'palabras_similares']  # Permitir búsquedas
    list_display = ['c_ClaveProdServ', 'descripcion', 'fecha_inicio_vigencia', 'fecha_fin_vigencia']
    list_filter = ['fecha_inicio_vigencia', 'fecha_fin_vigencia', 'estimulo_franja_fronteriza']

    def has_view_permission(self, request, obj=None):
        return request.user.is_authenticated


# Registrar el modelo
mi_admin_site.register(ClaveProdServ, ClaveProdServAdmin)





from django.core.exceptions import ValidationError


class ConceptoForm(forms.ModelForm):
    class Meta:
        model = Conceptos
        fields = '__all__'
        widgets = {
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control border border-secondary',
                'rows': 4
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        cantidad = cleaned_data.get('cantidad')
        valor_unitario = cleaned_data.get('valor_unitario')
        importe = cleaned_data.get('importe')
        total = cleaned_data.get('total')
        if cantidad and valor_unitario and importe:
            if round(importe, 2) != round(cantidad * valor_unitario, 2):
                self.add_error("importe", "El importe debe ser igual a la cantidad multiplicada por el valor unitario.")
        if total and importe and total < importe:
            self.add_error("total", "El total no puede ser menor que el importe.")
        return cleaned_data

class ConceptoimpuestosInline(nested_admin.NestedTabularInline):
    model = Conceptosimpuesto
    extra = 1
    can_delete = True
    fieldsets = (
        ('Impuesto', {
            'fields': ('impuesto','valor','incluido','valorImpuesto','base')
        }),
    )

class ConceptoImpuestosInline(nested_admin.NestedTabularInline):
    model = Impuestos
    extra = 1

class ACuentaTercerosInline(nested_admin.NestedTabularInline):
    model = ACuentaTerceros
    extra = 1

class InformacionAduaneraInline(nested_admin.NestedTabularInline):
    model = InformacionAduanera
    extra = 1

class CuentaPredialInline(nested_admin.NestedTabularInline):
    model = CuentaPredial
    extra = 1

class ComplementoConceptoInline(nested_admin.NestedTabularInline):
    model = ComplementoConcepto
    extra = 1

class ParteInline(nested_admin.NestedTabularInline):
    model = Parte
    extra = 1

class ImpuestosInline(nested_admin.NestedTabularInline):
    model = Impuestos
    extra = 1
    max_num = 1  # Solo se permite un formulario
    
    
class ConceptoInline(nested_admin.NestedStackedInline):
    model = Conceptos
    form = ConceptoForm
    extra = 1
    max_num = 1
    can_delete = True
    inlines = [ImpuestosInline,]
    fieldsets = (
        ('Clave y Descripción del Producto', {
            'fields': (
                'c_ClaveProdServ', 'descripcion', 'noIdentificacion',
            )
        }),
        ('Medida y Cantidad', {
            'fields': (
                'cantidad', 'unidad', 'c_ClaveUnidad', 'valorUnitario', 'importe', 'descuento',
            )
        }),
        ('Información Fiscal', {
            'fields': (
                'c_ObjetoImp',
                'complemento_tipo'
            )
        }),
        ('Descuento', {
            'fields': (
                'descuento_porcentaje',
                'descuento_incluido'
            )
        }),
    )

    autocomplete_fields = ['c_ClaveProdServ', 'c_ClaveUnidad']



    
    
class AddendaInline(nested_admin.NestedTabularInline):
    model = Addenda
    extra = 1
    max_num = 1
    can_delete = True


class InformacionGlobalForm(forms.ModelForm):
    class Meta:
        model = InformacionGlobal
        fields = ['Escomprobantelegal', 'Periodicidad', 'Meses', 'Anio']


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Aplica form-control para estilo
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control mb-3'  # hace que cada campo tenga margen inferior
            })
            
    def clean(self):
        cleaned_data = super().clean()
        periodicidad = cleaned_data.get('Periodicidad')

        if periodicidad:  # Verifica que no sea None
            if periodicidad.c_Periodicidad not in ['01', '02', '03', '04', '05']:
                self.add_error("Periodicidad", "La periodicidad debe ser un valor válido del catálogo del SAT.")
    
        return cleaned_data




class InformacionGlobalInline(nested_admin.NestedTabularInline):
    model = InformacionGlobal
    # form = InformacionGlobalForm
    extra = 1 #cambiar a 0 para que no se muestre el formulario extra cuando se crea de forma manual
    max_num = 1
    can_delete = False
    show_change_link = False
    fields = ['Escomprobantelegal', 'Periodicidad', 'Meses', 'Anio']

class EmisorForm(forms.ModelForm):
    class Meta:
        model = Emisor
        fields = '__all__' # Los campos visibles

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['c_RegimenFiscal'].label = "Régimen Fiscal del Negocio emisor"
        self.fields['c_RegimenFiscal'].widget.attrs.update({'class': 'form-select'})

        self.fields['facAtrAdquirente'].label = "Facatradquirente"
        self.fields['facAtrAdquirente'].widget.attrs.update({
            'placeholder': 'Facatradquirente',
            'class': 'form-control'
        })


class EmisorInline(nested_admin.NestedStackedInline):
    model = Emisor
    extra = 1  # para que Django genere uno al iniciar
    max_num = 1
    can_delete = False
    fk_name = 'comprobante'  # si aplica
    form = EmisorForm  # si estás usando un formulario personalizado

    
            
UUID_REGEX = re.compile(r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[1-5][0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$')
class CfdiRelacionadosForm(forms.ModelForm):
    class Meta:
        model = CfdiRelacionados
        fields = ['c_TipoRelacion', 'uuid']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['c_TipoRelacion'].label = "Tipo de relación CFDI"
        self.fields['uuid'].widget.attrs.update({
            'placeholder': 'UUID del CFDI relacionado',
            'class': 'form-control'
        })
        
    def clean_uuid(self):
        uuid = self.cleaned_data.get('uuid', '').strip()
        
        # Validar formato
        if not UUID_REGEX.match(uuid):
            raise ValidationError("El UUID no tiene un formato válido (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx).")

        # Validar longitud exacta (36 caracteres)
        if len(uuid) != 36:
            raise ValidationError("El UUID debe tener 36 caracteres incluyendo los guiones.")

        # Opcional: Validar unicidad
        # if CfdiRelacionados.objects.filter(uuid=uuid).exclude(pk=self.instance.pk).exists():
        #     raise ValidationError("Este UUID ya ha sido registrado en otro CFDI relacionado.")

        return uuid

        

class CfdiRelacionadosInline(nested_admin.NestedTabularInline):
    model = CfdiRelacionados
    form = CfdiRelacionadosForm
    extra = 1
    max_num = 1
    can_delete = True
    verbose_name = "Comprobante relacionado"
    verbose_name_plural = "CFDI Relacionados"



# class ComprobantesRelacionadosForm(forms.ModelForm):
#     uuid = forms.CharField(required=False)  # <-- lo haces explícitamente opcional

#     class Meta:
#         model = ComprobantesRelacionados
#         fields = '__all__'

#     def clean(self):
#         cleaned_data = super().clean()
#         uuid = cleaned_data.get('uuid')
#         if uuid and not re.match(r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$', uuid):
#             self.add_error("uuid", "El UUID debe tener un formato válido.")
#         return cleaned_data



    
# class ComprobantesRelacionadosInline(nested_admin.NestedTabularInline):
#     model = ComprobantesRelacionados
#     #  form = ComprobantesRelacionadosForm
#     extra = 0
#     fields = (
#         'FacturaElectronica',
#         'FacturaNomina12',
#         'FacturaCartaPorteTraslado',
#         'FacturaElectronicaBorrador',
#         'Tiporelacion',
#         'origenCFDI',
#         'receptorRFC',
#         'uuid'
#     )
    
class LeyendasFiscalesInline(nested_admin.NestedTabularInline):
    model = LeyendasFiscales
    extra = 1
    max_num = 1
  



from django.core.exceptions import ValidationError
from django.utils.html import format_html
from django.shortcuts import redirect







class CartaPorteInline(nested_admin.NestedTabularInline):
    model =  CartaPorte
    extra = 1
    max_num = 1  # Solo se permite un formulario
    fieldsets = (
        (
            "Información de la Carta Porte",
            {
                "fields": (
                    "version_cp",
                    "transporte_internacional",
                    "entrada_salida_mercancia",
                    "via_transporte",
                    "pais_origen_destino",
                    "total_distancia_recorrida",
                    "registro_istmo",
                    "polo_origen",
                    "polo_destino",
                )
            },
        ),
    )

class UbicacionInline(nested_admin.NestedTabularInline):
    model = Ubicacion
    extra = 1
    max_num = 1  # Solo se permite un formulario
   
    fieldsets = ( 
        (
            "Ubicación",
            {
                "fields": (
                    "tipo_ubicacion",
                    "id_ubicacion",
                    "distancia_recorrida_km",
                )
            },
        ),
        (
            "Estación",
            {
                "fields": (
                    "tipo_estacion",
                    "numero_estacion",
                    "nombre_estacion",
                    "fecha_salida_llegada",
                    "hora_salida_llegada",
                    "navegacion_trafico",
                )
            },
        ),
        (
            "Remitente/Destinatario",
            {
                "fields": (
                    "rfc_remitente_destinatario",
                    "numero_registro_tributario",
                    "nombre_remitente",
                    "residencia_fiscal",
                    "descripcion_resid_fiscal",
                )
            },
        ),
    )


class UbicaciondomicilioInline(nested_admin.NestedTabularInline):
    model = Ubicaciondomicilio
    extra = 1
    max_num = 1  # Solo se permite un formulario

 

    fieldsets = (
        (
            "Información del Domicilio",
            {
                "fields": (
                    "ubicacion",
                    "pais",
                    "codigo_postal",
                    "calle",
                    "numero_exterior",
                    "numero_interior",
                    "colonia",
                    "localidad",
                    "municipio",
                    "estado",
                    "referencia",
                )
            },
        ),
    )
     
class MercanciaInline(nested_admin.NestedStackedInline):
    model = Mercancia
    extra = 1
    max_num = 1  # Solo se permite un formulario

    

    fieldsets = (
        (
            "Datos Generales",
            {
                "fields": ("numero_total_mercancias", "logistica_inversa")
            },
        ),
        (
            "Peso y Unidad",
            {
                "fields": ("clave_unidad_peso", "unidad_peso", "peso_bruto_total", "peso_neto_total", "cargo_por_tasacion")
            },
        ),
        (
            "Detalles de Bienes Transportados",
            {
                "fields": ("cantidad", "descripcion_producto", "clave_bienes_transp", "clave_producto_STCC")
            },
        ),
        (
            "Características de Bienes",
            {
                "fields": ("clave_unidad", "unidad", "peso_kg", "dimensiones", "unidad_dimension")
            },
        ),
        (
            "Material Peligroso",
            {
                "fields": ("material_peligroso", "clave_material_peligroso", "descripcion_material_peligroso", "embalaje", "descripcion_embalaje")
            },
        ),
        (
            "Valor y Clasificación",
            {
                "fields": ("valor_mercancia", "moneda", "fraccion_arancelaria", "descripcion_fraccion_arancelaria", "uuid_cfdi_com_ext")
            },
        ),
        (
            "Sector COFEPRIS",
            {
                "fields": ("sector_cofepris", "nombre_ingrediente_activo", "nombre_quimico", "denominacion_generica", "denominacion_distintiva")
            },
        ),
        (
            "Medicamentos y Sustancias",
            {
                "fields": ("fabricante", "fecha_caducidad", "lote_medicamento", "registro_sanitario", "numero_cas")
            },
        ),
        (
            "Datos Adicionales",
            {
                "fields": ("datos_fabricante", "datos_formulador", "datos_maquilador", "uso_autorizado", "estado_materia")
            },
        ),
        (
            "Permisos de Importación",
            {
                "fields": ("folio_permiso_importacion", "folio_vucem", "razon_social_importadora")
            },
        ),
    )



class CantidadTransportadaInline(nested_admin.NestedTabularInline):
    model = CantidadTransportada
    extra = 1
    max_num = 1  # Solo se permite un formulario

  

    fieldsets = (
        (
            "Información General",
            {
                "fields": ("cantidad", "id_origen", "id_destino", "clave_transporte")
            },
        ),
        (
            "Detalles de Mercancía (Solo para transporte marítimo)",
            {
                "fields": ("unidad_peso", "descripcion_unidad_peso", "numero_piezas", "peso_bruto", "peso_neto", "peso_tara")
            },
        ),
    )


class DetalleMercanciaMaritimaInline(nested_admin.NestedTabularInline):
    model = DetalleMercanciaMaritima
    extra = 1
    max_num = 1  # Solo se permite un formulario

   
    fieldsets = (
        (
            "Detalles de Mercancía Marítima",
            {
                "fields": ("unidad_peso", "descripcion_unidad_peso", "numero_piezas", "peso_bruto", "peso_neto", "peso_tara")
            },
        ),
    )


class PedimentoInline(nested_admin.NestedTabularInline):
    model = Pedimento
    extra = 1


    fieldsets = (
        (
            "Información del Pedimento",
            {
                "fields": ("tipo_documento", "folio_documento", "rfc_importador", "numero_pedimento")
            },
        ),
    )


class GuiaIdentificacionInline(nested_admin.NestedTabularInline):
    model = GuiaIdentificacion
    extra = 1


    fieldsets = (
        (
            "Detalles de la Guía de Identificación",
            {
                "fields": ("numero_guia", "descripcion_contenido", "peso_kg")
            },
        ),
    )




class AutotransporteInline(nested_admin.NestedTabularInline):
    model = Autotransporte
    extra = 1
    max_num = 1


    fieldsets = (
        ("Información General", {"fields": ("tipo_permiso_sct", "numero_permiso_sct")}),
        ("Identificación Vehicular", {"fields": ("configuracion_vehicular", "placa", "modelo_anio", "peso_bruto_vehicular")}),
        ("Remolques", {"fields": ("subtipo_remolque", "placa_remolque")}),
        ("Seguros", {"fields": ("prima_seguro", "aseguradora_resp_civil", "poliza_resp_civil", "aseguradora_ambiental", "poliza_ambiental", "aseguradora_carga", "poliza_carga")}),
    )


class TransporteMaritimoInline(nested_admin.NestedTabularInline):
    model = TransporteMaritimo
    extra = 1
    max_num = 1

  

    fieldsets = (
        ("Información General", {"fields": ("tipo_permiso_sct", "numero_permiso_sct")}),
        ("Aseguradora", {"fields": ("nombre_aseguradora", "numero_poliza_seguro")}),
        ("Embarcación", {"fields": ("tipo_embarcacion", "matricula", "numero_id_omi", "modelo_embarcacion_anio", "nombre_embarcacion", "nacionalidad_embarcacion", "descripcion_nacionalidad")}),
        ("Capacidad", {"fields": ("numero_cert_itc", "permiso_navegacion", "unidades_arqueo", "tipo_carga", "eslora_pies", "manga_pies", "calado_pies", "puntal_pies")}),
        ("Línea Naviera", {"fields": ("linea_naviera", "nombre_agente_naviero", "numero_reg_aut_naviera", "numero_viaje", "numero_conocimiento_embarque")}),
    )


class TransporteAereoInline(nested_admin.NestedTabularInline):
    model = TransporteAereo
    extra = 1
    max_num = 1

  

    fieldsets = (
        ("Información General", {"fields": ("tipo_permiso_sct", "numero_permiso_sct")}),
        ("Codigo de transportista", {"fields": ("codigo_transportista", "lugar_contrato")}),
        ("Aseguradora", {"fields": ("nombre_aseguradora", "numero_poliza_seguro")}),
        ("Datos de Aeronave", {"fields": ("numero_matricula_aeronave", "numero_guia")}),
        ("Datos del Embarcador", {"fields": ("rfc_embarcador", "nombre_embarcador", "residencia_fiscal_embarcador", "descripcion_residencia_fiscal", "numero_id_reg_trib_embarcador")}),
    )


class TransporteFerroviarioInline(nested_admin.NestedTabularInline):
    model = TransporteFerroviario
    extra = 1
    max_num = 1

  

    fieldsets = (
        ("Información General", {"fields": ("tipo_servicio", "tipo_trafico")}),
        ("Aseguradora", {"fields": ("nombre_aseguradora", "numero_poliza_seguro", "tipos_derechos_paso")}),
        ("Carro Ferroviario", {"fields": ("tipo_carro", "matricula_carro", "guia_carro", "toneladas_netas_carro")}),
        ("Contenedor", {"fields": ("tipo_contenedor", "peso_contenedor_vacio_kg", "peso_neto_mercancia_kg")}),
    )


class FiguraTransporteInline(nested_admin.NestedTabularInline):
    model = FiguraTransporte
    extra = 1
    max_num = 1


    fieldsets = (
        ("Información de la Figura de Transporte", {"fields": ("tipo_figura", "numero_licencia", "rfc", "numero_registro_trib", "nombre", "residencia_fiscal", "descripcion_residencia_fiscal")}),
    )


class DomicilioInline(nested_admin.NestedTabularInline):
    model = Domicilio
    extra = 1
    max_num = 1


    fieldsets = (
        ("Información del Domicilio", {"fields": ("pais", "codigo_postal", "calle", "numero_exterior", "numero_interior", "colonia", "localidad", "municipio", "estado", "referencia")}),
    )


class ParteTransporteInline(nested_admin.NestedTabularInline):
    model = partetransporte
    extra = 1
    max_num = 1

    fieldsets = (
        ("Información de la Parte de Transporte", {"fields": ("codigo", "descripcion",)}),
    )


class RegimenAduaneroInline(nested_admin.NestedTabularInline):
    model = regimenaduaneroccptresuno
    extra = 1
    max_num = 1


    fieldsets = ( 
        ("Regimen Aduanero", {"fields": ("codigo", "descripcion")}),
    )



    


class CartaporteTraslado30(admin.ModelAdmin):
    change_form_template = 'LadoClientes/carta porte traslado 30/change_formcartaportetraslado3.0.html'
    change_list_template = 'LadoClientes/forms/change_list.html'
    delete_confirmation_template = 'LadoClientes/forms/delete_confirmation.html'
    delete_selected_confirmation_template = 'LadoClientes/forms/delete_selected_confirmation.html'
    index_template = 'LadoClientes/pages/index.html'
    
    # list_display = ('nombre', 'rfc', 'activo', 'fecha_creacion', 'get_tipos_comprobantes_detallados', 'informacion_fiscal', 'regimen_fiscal')
    # list_filter = ('activo', 'regimen_fiscal', 'fecha_creacion')
    search_fields = ('nombre', 'rfc', 'informacion_fiscal__rfc', 'informacion_fiscal__razon_social')
    # ordering = ['nombre', 'fecha_creacion']
    readonly_fields = ('fecha_creacion',)

    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'rfc', 'descripcion', 'codigo_postal', 'activo', 'fecha_creacion', 'informacion_fiscal', 'regimen_fiscal')
        }),
    )





    # inlines = [
    #     TipoComprobanteInline, InformacionGlobalInline, 
    #     EmisorInline,ComprobantesRelacionadosInline, 
    #     ReceptorInline, CartaPorteInline, UbicacionInline, UbicaciondomicilioInline,
    #     MercanciaInline, CantidadTransportadaInline, DetalleMercanciaMaritimaInline,
    #     PedimentoInline, GuiaIdentificacionInline, AutotransporteInline, TransporteMaritimoInline, TransporteAereoInline,
    #     TransporteFerroviarioInline, FiguraTransporteInline, DomicilioInline, ParteTransporteInline, RegimenAduaneroInline,
    #     ConceptoInline,
    #     #nominaInline, PercepcionInline, DeduccionInline, OtroPagoInline, subcontratacionInline
    # ]


    def get_tipos_comprobantes_detallados(self, obj):
        # Implementa la lógica aquí
        return "Detalles no disponibles"
    get_tipos_comprobantes_detallados.short_description = "Tipos de Comprobantes Detallados"

    #LeyendasFiscalesInline, ConceptoInline,

# mi_admin_site.register(FacturaCartaPorteTraslado, CartaporteTraslado30)




class FacturaElectronicaForm(forms.ModelForm):
    class Meta:
        model = FacturaElectronica
        fields = '__all__'  # Incluye todos los campos del modelo

    def clean(self):
        cleaned_data = super().clean()

        # Validación de RFC
        rfc_regex = r'^[A-Z&Ñ]{3,4}\d{6}[A-Z0-9]{3}$'
        rfc = cleaned_data.get("rfc")
        if rfc and not re.match(rfc_regex, rfc):
            self.add_error("rfc", "El RFC del emisor no es válido.")

        # Validación de Código Postal
        codigo_postal = cleaned_data.get("codigo_postal")
        if not codigo_postal or not re.match(r'^\d{5}$', str(codigo_postal)):
            self.add_error("codigo_postal", "El código postal debe tener 5 dígitos.")

        # Validación de Régimen Fiscal
        regimen_fiscal = cleaned_data.get("regimen_fiscal")
        if not regimen_fiscal:
            self.add_error("regimen_fiscal", "El régimen fiscal es obligatorio.")

        return cleaned_data
    
class EmisorAdmin(nested_admin.NestedModelAdmin):
    change_form_template = 'LadoClientes/forms/change_form.html'
    change_list_template = 'LadoClientes/forms/change_list.html'
    delete_confirmation_template = 'LadoClientes/forms/delete_confirmation.html'
    delete_selected_confirmation_template = 'LadoClientes/forms/delete_selected_confirmation.html'
    index_template = 'LadoClientes/pages/index.html'
    # list_display = ('Rfc', 'Nombre', 'C_RegimenFiscal', 'FacAtrAdquirente',)
    # list_filter = ('C_RegimenFiscal', )
    search_fields = ('rfc', 'nombre', 'facAtrAdquirente', 'user__username')
    # ordering = ['Rfc']
   
    fieldsets = (
        (None, {
            'fields': ('rfc', 'nombre', 'c_RegimenFiscal', 'facAtrAdquirente')
        }),
    )

mi_admin_site.register(Emisor,EmisorAdmin)



class CfdirelacionadosAdmin(nested_admin.NestedModelAdmin):
    form = CfdiRelacionadosForm
    change_form_template = 'LadoClientes/forms/change_form.html'
    change_list_template = 'LadoClientes/forms/change_list.html'
    delete_confirmation_template = 'LadoClientes/forms/delete_confirmation.html'
    delete_selected_confirmation_template = 'LadoClientes/forms/delete_selected_confirmation.html'
    index_template = 'LadoClientes/pages/index.html'

    list_display = ('c_TipoRelacion', 'mostrar_uuid')
    list_filter = ('c_TipoRelacion',)
    search_fields = ('c_TipoRelacion__c_TipoRelacion', 'c_TipoRelacion__descripcion', 'uuid')

    fieldsets = (
        (None, {
            'fields': ('c_TipoRelacion', 'uuid')
        }),
    )

    def mostrar_uuid(self, obj):
        return obj.uuid
    mostrar_uuid.short_description = "UUID relacionado"


mi_admin_site.register(CfdiRelacionados,CfdirelacionadosAdmin)






class InformacionglobalAdmin(nested_admin.NestedModelAdmin):
    change_form_template = 'LadoClientes/forms/change_form.html'
    change_list_template = 'LadoClientes/forms/change_list.html'
    delete_confirmation_template = 'LadoClientes/forms/delete_confirmation.html'
    delete_selected_confirmation_template = 'LadoClientes/forms/delete_selected_confirmation.html'
    index_template = 'LadoClientes/pages/index.html'

    # list_display = ( 'Escomprobantelegal','Periodicidad','Meses','Anio', )
    # list_filter = ('Escomprobantelegal','Periodicidad','Meses','Anio', )
    search_fields = ('Escomprobantelegal','Periodicidad','Meses','Anio', )  # o ajusta según tu modelo

    fieldsets = (
        (None, {
            'fields': ('Escomprobantelegal','Periodicidad','Meses','Anio', )
        }),
    )




mi_admin_site.register(InformacionGlobal,InformacionglobalAdmin)



class ImpuestosTotalesAdmin(nested_admin.NestedModelAdmin):
    change_form_template = 'LadoClientes/forms/change_form.html'
    change_list_template = 'LadoClientes/forms/change_list.html'
    delete_confirmation_template = 'LadoClientes/forms/delete_confirmation.html'
    delete_selected_confirmation_template = 'LadoClientes/forms/delete_selected_confirmation.html'
    index_template = 'LadoClientes/pages/index.html'

    # list_display = ('TotalImpuestosRetenidos','TotalImpuestosTraslados','Traslados_idTraslados','Retenciones_idRetenciones',)
    # list_filter = ('TotalImpuestosRetenidos','TotalImpuestosTraslados','Traslados_idTraslados','Retenciones_idRetenciones',)
    search_fields = ('TotalImpuestosRetenidos','TotalImpuestosTraslados','Traslados_idTraslados','Retenciones_idRetenciones',)  # o ajusta según tu modelo

    fieldsets = (
        (None, {
            'fields': ('TotalImpuestosRetenidos','TotalImpuestosTraslados','Traslados_idTraslados','Retenciones_idRetenciones',)
        }),
    )




mi_admin_site.register(ImpuestosTotales,ImpuestosTotalesAdmin)


class ComplementoAdmin(nested_admin.NestedModelAdmin):
    change_form_template = 'LadoClientes/forms/change_form.html'
    change_list_template = 'LadoClientes/forms/change_list.html'
    delete_confirmation_template = 'LadoClientes/forms/delete_confirmation.html'
    delete_selected_confirmation_template = 'LadoClientes/forms/delete_selected_confirmation.html'
    index_template = 'LadoClientes/pages/index.html'

    # list_display = ('TimbreFiscalDigital',)
    # list_filter = ('TimbreFiscalDigital',)
    search_fields = ('idTipoComplemento',)  # o ajusta según tu modelo

    fieldsets = (
        (None, {
            'fields': ('idTipoComplemento','idComrobante')
        }),
    )




mi_admin_site.register(Complemento,ComplementoAdmin)


class addendaAdmin(nested_admin.NestedModelAdmin):
    change_form_template = 'LadoClientes/forms/change_form.html'
    change_list_template = 'LadoClientes/forms/change_list.html'
    delete_confirmation_template = 'LadoClientes/forms/delete_confirmation.html'
    delete_selected_confirmation_template = 'LadoClientes/forms/delete_selected_confirmation.html'
    index_template = 'LadoClientes/pages/index.html'

    # list_display = ('Addenda',)
    # list_filter = ('Addenda',)
    search_fields = ('Addenda',)  # o ajusta según tu modelo

    fieldsets = (
        (None, {
            'fields': ('Addenda',)
        }),
    )




mi_admin_site.register(Addenda,addendaAdmin)





class ReceptorAdmin(admin.ModelAdmin):
    change_form_template = 'LadoClientes/forms/change_form.html'
    change_list_template = 'LadoClientes/forms/change_list.html'
    delete_confirmation_template = 'LadoClientes/forms/delete_confirmation.html'
    delete_selected_confirmation_template = 'LadoClientes/forms/delete_selected_confirmation.html'
    index_template = 'LadoClientes/pages/index.html'
    list_display = (
        'rfc',
        'nombre',
        'c_DomicilioFiscalReceptor',
        'c_ResidenciaFiscal',
        'c_RegimenFiscalReceptor',
        'c_UsoCFDI'
    )
    list_filter = (
        'c_ResidenciaFiscal',
        'c_RegimenFiscalReceptor',
        'c_UsoCFDI'
    )
    search_fields = (
        'rfc',
        'nombre',
        'numRegldTrib'
    )
 

    fieldsets = (
        (None, {
            'fields': (
                'rfc',
                'nombre',
                'c_ResidenciaFiscal',
                'numRegldTrib',
                'c_RegimenFiscalReceptor',
                'c_UsoCFDI',
            )
        }),
    )
    autocomplete_fields = ['c_DomicilioFiscalReceptor']

mi_admin_site.register(Receptor,ReceptorAdmin)

class ComprobanteForm(forms.ModelForm):
    class Meta:
        model = Comprobante
        fields = '__all__'
        widgets = {
            
            'condicionesDePago': forms.Textarea(attrs={
                'class': 'form-control border border-secondary',
                'rows': 2,
                'placeholder': 'Condiciones de pago...'
            }),
            'c_MetodoPago': forms.Select(attrs={'class': 'form-select'}),
            'c_FormaPago': forms.Select(attrs={'class': 'form-select'}),
            'c_Moneda': forms.Select(attrs={'class': 'form-select'}),
        }

    
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # 👉 Precargar la fecha actual
        if not self.instance.pk:  # solo en creación, no en edición
            self.fields['fechaEmision'].initial = now()
            self.fields['fechaPago'].initial = now()

        if request:
            try:
                usuario_cfdi = UsersCFDI.objects.get(idUserCFDI=request.user)
                usuario_raiz = usuario_cfdi.get_raiz()
                # Negocio activo desde sesión
                negocio_actual = obtener_negocio_activo_para(request)
                #negocio_actual = InformacionFiscal.objects.filter(idUserCFDI=usuario_raiz, activo=True, es_principal=True).first()
                if negocio_actual:
                    self.fields['informacionFiscal'].queryset = InformacionFiscal.objects.filter(pk=negocio_actual.pk)
                    self.fields['informacionFiscal'].initial = negocio_actual
            except UsersCFDI.DoesNotExist:
                self.fields['informacionFiscal'].queryset = InformacionFiscal.objects.none()


class ComprobanteAdmin(nested_admin.NestedModelAdmin):
    form = ComprobanteForm
    tipo_comprobante_default = 'I'
    url_default = 'mi_admin:cfdi_comprobante_changelist'
    tipo_default='Factura electrónica'
    raw_id_fields = ['c_MetodoPago', 'c_FormaPago', 'c_Moneda']
    change_form_template = 'LadoClientes/forms/change_formFacturas_Personalizado.html'
    change_list_template = 'LadoClientes/forms/change_list.html'
    delete_confirmation_template = 'LadoClientes/forms/delete_confirmation.html'
    delete_selected_confirmation_template = 'LadoClientes/forms/delete_selected_confirmation.html'
    index_template = 'LadoClientes/pages/index.html'

    list_display = ('id','version', 'informacionFiscal', 'serie', 'folio', 'c_FormaPago', 'noCertificado')
    list_filter = ('tipo_documento', 'c_TipoDeComprobante')
    search_fields = ('serie', 'folio', 'informacionFiscal', 'c_TipoDeComprobante', 'c_LugarExpedicion', 'c_MetodoPago', 'c_FormaPago', 'c_Moneda', 'confirmacion')

    
    list_per_page = 10

    # readonly_fields = ('Fecha',)

    
    fieldsets = (
        ('Datos Generales', {
            'fields': ('version', 'informacionFiscal', 'serie', 'folio', 'fechaEmision')
        }),
        ('Información de pago', {
            'fields': (
                'c_MetodoPago',
                'c_FormaPago',
                'condicionesDePago',
                'c_Moneda',
                'tipoCambio',
                'fechaPago'
            )
        }),
    )


    # inlines = [ConceptoInline]
    autocomplete_fields = ['c_LugarExpedicion']  # Autocompletar el campo de código postal
   

    inlines = [
    InformacionGlobalInline,
    EmisorInline,
    CfdiRelacionadosInline,
    ReceptorInline,
    ConceptoInline,
    AddendaInline
    ]


 
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs.filter(c_TipoDeComprobante__c_TipoDeComprobante=self.tipo_comprobante_default)
        
        usuario_cfdi = UsersCFDI.objects.get(idUserCFDI=request.user)
        usuario_raiz = usuario_cfdi.get_raiz()
        negocio_activo = obtener_negocio_activo_para(request)
        #informacionFiscal__es_principal=True con esta linea nos aseguramos que solo se muestren los comprobantes del usuario logueado y su información fiscal principal
        
        return qs.filter(informacionFiscal=negocio_activo, c_TipoDeComprobante__c_TipoDeComprobante=self.tipo_comprobante_default)
    
    def has_change_permission(self, request, obj=None):
        if obj and getattr(obj, "tipo_documento", "").lower() == "timbrado":
            if request.method not in ("GET", "HEAD", "OPTIONS"):
                return False
        return super().has_change_permission(request, obj)


    def get_form(self, request, obj=None, **kwargs):
        Form = super().get_form(request, obj, **kwargs)
        class CustomForm(Form):
            def __init__(self2, *args, **kwargs2):
                kwargs2['request'] = request
                super().__init__(*args, **kwargs2)
        return CustomForm
    
    def response_add(self, request, obj, post_url_continue=None):
        if "_facturar_timbrar" in request.POST:
            print("Botón 'Facturar y Timbrar' presionado desde ADD.")
            return self.facturar_y_timbrar(request, obj)
        
        if "_generar_pdf" in request.POST:
            print("Botón 'Generar PDF' presionado desde ADD.")
            return self.generar_pdf(request, obj)
        
        if "_generar_xml" in request.POST:
            print("Botón 'Generar XML' presionado desde ADD.")
            return self.generar_xml(request, obj)
        
        return super().response_add(request, obj, post_url_continue)


    def response_change(self, request, obj):
        """
        Maneja acciones personalizadas al guardar el modelo.
        """
        
        # Si está timbrado, no permitir guardado de ninguna forma
        if getattr(obj, "tipo_documento", "").lower() == "timbrado":
            if any(key in request.POST for key in ["_save", "_continue", "_addanother",
                                                "_facturar_timbrar", "_generar_pdf", "_generar_xml"]):
                self.message_user(request, "Este comprobante ya está timbrado y no puede modificarse.", level=messages.ERROR)
                return HttpResponseRedirect(request.path)
        
        if "_facturar_timbrar" in request.POST:
            form = self.get_form(request, obj)(request.POST, request.FILES, instance=obj)
            formsets, inline_instances = self._create_formsets(request, obj, change=True)

            if form.is_valid() and all(fs.is_valid() for fs in formsets):
                # 1. Guardar el comprobante (sin guardarlo aún)
                obj = form.save(commit=False)

                # 2. Guardar modelo (ejecuta save_model)
                self.save_model(request, obj, form, change=True)

                # 3. Guardar todos los formsets (inlines)
                for formset in formsets:
                    self.save_formset(request, form, formset, change=True)

                # 4. Guardar relaciones adicionales (many-to-many, etc.)
                self.save_related(request, form, formsets, change=True)

                # 5. Guardar finalmente el objeto en la base de datos
                obj.save()

                # 6. Llamar al timbrado
                return self.facturar_y_timbrar(request, obj)

            else:
                # Si hubo errores, mostrar el mismo formulario con los errores
                return self.changeform_view(request, str(obj.pk), form_url="", extra_context={
                    'form': form,
                    'errors': form.errors,
                })

        if "_copy_form" in request.POST:
            form = self.get_form(request, obj)(request.POST, request.FILES, instance=obj)
            formsets, inline_instances = self._create_formsets(request, obj, change=True)

            if form.is_valid() and all(fs.is_valid() for fs in formsets):
                updated_obj = form.save(commit=False)

                self.save_model(request, updated_obj, form, change=True)

                for formset in formsets:
                    self.save_formset(request, form, formset, change=True)

                self.save_related(request, form, formsets, change=True)

                updated_obj.save()

                if hasattr(form, "save_m2m"):
                    form.save_m2m()

                try:
                    updated_obj.refresh_from_db()
                    new_obj = self._duplicate_comprobante(updated_obj)
                    lat = request.POST.get("latitud")
                    lon = request.POST.get("longitud")
                    ubicacion = f"{lat}, {lon}" if lat and lon else None
                    ip = request.META.get("REMOTE_ADDR")

                    BitacoraCFDI.objects.create(
                        comprobante=new_obj,
                        creado_por=request.user,
                        fecha_creacion=now(),
                        ip_creacion=ip,
                        ubicacion_creacion=ubicacion
                    )
                except Exception as exc:
                    self.message_user(
                        request,
                        f"No se pudo copiar el comprobante: {exc}",
                        level=messages.ERROR,
                    )
                    return HttpResponseRedirect(request.path)

                self.message_user(
                    request,
                    "Se creó una copia del comprobante correctamente.",
                    level=messages.SUCCESS,
                    extra_tags="copy-success",
                )
                return HttpResponseRedirect(
                    reverse('mi_admin:cfdi_comprobante_change', args=[new_obj.pk])
                )

            return self.changeform_view(
                request,
                str(obj.pk),
                form_url="",
                extra_context={'form': form, 'errors': form.errors},
            )
        # if "_copy_form" in request.POST:
        #     form = self.get_form(request, obj)(request.POST, request.FILES, instance=obj)
        #     formsets, inline_instances = self._create_formsets(request, obj, change=True)

        #     if form.is_valid() and all(fs.is_valid() for fs in formsets):
        #         updated_obj = form.save(commit=False)

        #         self.save_model(request, updated_obj, form, change=True)

        #         for formset in formsets:
        #             self.save_formset(request, form, formset, change=True)

        #         self.save_related(request, form, formsets, change=True)

        #         updated_obj.save()

        #         if hasattr(form, "save_m2m"):
        #             form.save_m2m()

        #         try:
        #             updated_obj.refresh_from_db()
        #             new_obj = self._duplicate_comprobante(updated_obj)
        #         except Exception as exc:
        #             self.message_user(
        #                 request,
        #                 f"No se pudo copiar el comprobante: {exc}",
        #                 level=messages.ERROR,
        #             )
        #             return HttpResponseRedirect(request.path)

        #         self.message_user(
        #             request,
        #             "Se creó una copia del comprobante correctamente.",
        #             level=messages.SUCCESS,
        #             extra_tags="copy-success",
        #         )
        #         return HttpResponseRedirect(
        #             reverse('mi_admin:cfdi_comprobante_change', args=[new_obj.pk])
        #         )

        #     return self.changeform_view(
        #         request,
        #         str(obj.pk),
        #         form_url="",
        #         extra_context={'form': form, 'errors': form.errors},
        #     )
        
        if "_generar_pdf" in request.POST:
            form = self.get_form(request, obj)(request.POST, request.FILES, instance=obj)
            formsets, inline_instances = self._create_formsets(request, obj, change=True)

            if form.is_valid() and all(fs.is_valid() for fs in formsets):
                # 1. Guardar el comprobante (sin guardarlo aún)
                obj = form.save(commit=False)

                # 2. Guardar modelo (ejecuta save_model)
                self.save_model(request, obj, form, change=True)

                # 3. Guardar todos los formsets (inlines)
                for formset in formsets:
                    self.save_formset(request, form, formset, change=True)

                # 4. Guardar relaciones adicionales (many-to-many, etc.)
                self.save_related(request, form, formsets, change=True)

                # 5. Guardar finalmente el objeto en la base de datos
                obj.save()

                # 6. Llamar al pdf
                return self.generar_pdf(request, obj)

            else:
                # Si hubo errores, mostrar el mismo formulario con los errores
                return self.changeform_view(request, str(obj.pk), form_url="", extra_context={
                    'form': form,
                    'errors': form.errors,
                })
            
        
        if "_generar_xml" in request.POST:
            form = self.get_form(request, obj)(request.POST, request.FILES, instance=obj)
            formsets, inline_instances = self._create_formsets(request, obj, change=True)

            if form.is_valid() and all(fs.is_valid() for fs in formsets):
                # 1. Guardar el comprobante (sin guardarlo aún)
                obj = form.save(commit=False)

                # 2. Guardar modelo (ejecuta save_model)
                self.save_model(request, obj, form, change=True)

                # 3. Guardar todos los formsets (inlines)
                for formset in formsets:
                    self.save_formset(request, form, formset, change=True)

                # 4. Guardar relaciones adicionales (many-to-many, etc.)
                self.save_related(request, form, formsets, change=True)

                # 5. Guardar finalmente el objeto en la base de datos
                obj.save()

                # 6. Llamar al xml
                return self.generar_xml(request, obj)

            else:
                # Si hubo errores, mostrar el mismo formulario con los errores
                return self.changeform_view(request, str(obj.pk), form_url="", extra_context={
                    'form': form,
                    'errors': form.errors,
                })
        if "_save" in request.POST:
            return super().response_change(request, obj)
        
        if "_generar_pdf_timbrado" in request.POST:
            return self.generar_pdf_timbrado(request, obj)
        
        if "_generar_xml_timbrado" in request.POST:
            return self.generar_xml_timbrado(request, obj)

        if "_save_draft" in request.POST:  # Detectar si se presionó el botón "Guardar borrador". _save_draft es el boton vinculado con la plantilla change_form.html de django admin
            return super().response_change(request, obj)
        
        return super().response_change(request, obj)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if request.method == "POST":

            # 🔹 Si se presionó el botón 'Facturar y Timbrar', redirigir manualmente a `response_change()`
            if "_copy_form" in request.POST:
                return self.response_change(request, self.get_object(request, object_id))
            if "_facturar_timbrar" in request.POST:
                return self.response_change(request, self.get_object(request, object_id))
            
            if "_generar_pdf" in request.POST:
                return self.response_change(request, self.get_object(request, object_id))
            
            if "_generar_xml" in request.POST:
                 return self.response_change(request, self.get_object(request, object_id))
             
            if "_generar_pdf_timbrado" in request.POST:
                 return self.response_change(request, self.get_object(request, object_id))
             
            if "_generar_xml_timbrado" in request.POST:
                 return self.response_change(request, self.get_object(request, object_id))
            
            if "_save_draft" in request.POST:
                return self.response_change(request, self.get_object(request, object_id))
            
        extra_context = extra_context or {}
        extra_context["changelist_url"] = request.GET.get("changelist", request.META.get("HTTP_REFERER"))

        return super().change_view(request, object_id, form_url, extra_context=extra_context)


    def _clone_model_instance(self, instance, overrides=None):
        overrides = overrides or {}
        data = {}

        for field in instance._meta.concrete_fields:
            if field.auto_created or isinstance(field, models.AutoField):
                continue
            data[field.name] = getattr(instance, field.name)

        data.update(overrides)
        return instance.__class__.objects.create(**data)

    def _duplicate_comprobante(self, source_obj):
        source = source_obj.__class__.objects.get(pk=source_obj.pk)

        overrides = {
            'sello': None,
            'certificado': None,
            'noCertificado': None,
            'tipo_documento': 'borrador',
        }

        with transaction.atomic():
            new_obj = self._clone_model_instance(source, overrides)
            self._clone_comprobante_relations(source, new_obj)

        return new_obj

    def _clone_comprobante_relations(self, source, target):
        for info_global in InformacionGlobal.objects.filter(Comprobante=source):
            self._clone_model_instance(info_global, {'Comprobante': target})

        for emisor in Emisor.objects.filter(comprobante=source):
            self._clone_model_instance(emisor, {'comprobante': target})

        for receptor in Receptor.objects.filter(comprobante=source):
            self._clone_model_instance(receptor, {'comprobante': target})

        for relacionado in CfdiRelacionados.objects.filter(comprobante=source):
            self._clone_model_instance(relacionado, {'comprobante': target})

        for total in ImpuestosTotales.objects.filter(comprobante=source):
            self._clone_model_instance(total, {'comprobante': target})

        for concepto in Conceptos.objects.filter(comprobante=source):
            new_concepto = self._clone_model_instance(concepto, {'comprobante': target})

            for impuesto in concepto.impuestos.all():
                self._clone_model_instance(impuesto, {'idConcepto': new_concepto})

            for tercero in concepto.aCuentaTerceros.all():
                self._clone_model_instance(tercero, {'idConcepto': new_concepto})

            aduanera_map = {}
            for info_aduanera in concepto.informacionAduanera.all():
                new_info_aduanera = self._clone_model_instance(info_aduanera, {'idConcepto': new_concepto})
                aduanera_map[info_aduanera.pk] = new_info_aduanera

            for pedimento in concepto.pedimentos.all():
                self._clone_model_instance(pedimento, {'concepto': new_concepto})

            for cuenta in concepto.cuentaPredial.all():
                self._clone_model_instance(cuenta, {'idConcepto': new_concepto})

            for complemento in concepto.complementoConcepto.all():
                self._clone_model_instance(complemento, {'idConcepto': new_concepto})

            for parte in concepto.parte.all():
                overrides = {'idConcepto': new_concepto}
                if parte.informacionAduanera_id:
                    overrides['informacionAduanera'] = aduanera_map.get(parte.informacionAduanera_id)
                self._clone_model_instance(parte, overrides)

        for addenda in Addenda.objects.filter(comprobante=source):
            new_addenda = self._clone_model_instance(addenda, {'comprobante': target})

            try:
                siemens = addenda.siemens_gamesa
            except AddendaSiemensGamesa.DoesNotExist:
                siemens = None
            if siemens:
                self._clone_model_instance(siemens, {'addenda': new_addenda})

            try:
                ado = addenda.grupo_ado
            except AddendaGrupoADO.DoesNotExist:
                ado = None
            if ado:
                self._clone_model_instance(ado, {'addenda': new_addenda})

            try:
                waldos = addenda.waldos
            except AddendaWaldos.DoesNotExist:
                waldos = None
            if waldos:
                self._clone_model_instance(waldos, {'addenda': new_addenda})

            for terra in addenda.terra_multitransportes.all():
                self._clone_model_instance(terra, {'addenda': new_addenda})
    
    def save_model(self, request, obj, form, change):
        """
        Guarda el comprobante, asignando automáticamente al usuario logueado y su información fiscal principal.
        """
        
        super(nested_admin.NestedModelAdmin, self).save_model(request, obj, form, change)

        lat = request.POST.get("latitud")
        lon = request.POST.get("longitud")
        ubicacion = f"{lat}, {lon}" if lat and lon else None
        ip = request.META.get("REMOTE_ADDR")

        bitacora, _ = BitacoraCFDI.objects.get_or_create(comprobante=obj)
            
        if not change:
            # Asignar el usuario (si el modelo Comprobante lo tiene)
            if hasattr(obj, 'user'):
                obj.user = request.user
                

            # Obtener la información fiscal principal del usuario CFDI relacionado
            try:
                # usuario_cfdi = UsersCFDI.objects.get(idUserCFDI=request.user)
                # usuario_raiz = usuario_cfdi.get_raiz()
                # informacion_principal = InformacionFiscal.objects.filter(
                #     idUserCFDI=usuario_raiz,
                #     es_principal=True
                # ).first()
                
                informacion_principal = obtener_negocio_activo_para(request)
                print('tipo_comprobante_default:', self.tipo_comprobante_default)

                if informacion_principal:
                    obj.informacionFiscal = informacion_principal
                    obj.c_LugarExpedicion = CodigoPostal.objects.get(c_CodigoPostal=informacion_principal.codigo_postal)
                    # ✅ Solo fijar tipo si aún no tiene uno definido
                    if not obj.c_TipoDeComprobante_id:
                        obj.c_TipoDeComprobante = TipoComprobante.objects.get(c_TipoDeComprobante=self.tipo_comprobante_default)
                    obj.c_Exportacion = Exportacion.objects.get(c_Exportacion='01')
                print("Información fiscal asignada:", obj.informacionFiscal, "Lugar de expedición:", obj.c_LugarExpedicion, "Tipo de comprobante:", obj.c_TipoDeComprobante)
            except UsersCFDI.DoesNotExist:
                pass  # O registrar un mensaje de error si lo necesitas
            
            bitacora.creado_por = request.user
            bitacora.fecha_creacion = now()
            bitacora.ip_creacion = ip
            bitacora.ubicacion_creacion = ubicacion
            
        else:
            bitacora.editado_por = request.user
            bitacora.fecha_edicion = now()
            bitacora.ip_edicion = ip
            bitacora.ubicacion_edicion = ubicacion

        bitacora.save()

        super(nested_admin.NestedModelAdmin, self).save_model(request, obj, form, change)
        
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        # ------------------------ GUARDADO DE COMPLEMENTOS DE CONCEPTOS ------------------------
        # Asegura que todos los Conceptos estén guardados
        for concepto in form.instance.conceptos.all():
            if concepto.pk is None:
                concepto.save()
        # ------------------------ GUARDADO DE COMPLEMENTOS DE CONCEPTOS ------------------------
        for i, concepto in enumerate(form.instance.conceptos.all()):
            tipo = concepto.complemento_tipo

            # Elimina todos los complementos que NO correspondan al tipo actual
            if tipo != "cuenta_terceros":
                ACuentaTerceros.objects.filter(idConcepto=concepto).delete()
            if tipo != "cuenta_predial":
                CuentaPredial.objects.filter(idConcepto=concepto).delete()
            if tipo != "informacion_aduanera":
                InformacionAduanera.objects.filter(idConcepto=concepto).delete()
            if tipo != "parte":
                Parte.objects.filter(idConcepto=concepto).delete()

            # GUARDAR EL COMPLEMENTO ACTUAL
            if tipo == "cuenta_terceros":
                rfc = request.POST.get("rfcACuentaTerceros")
                nombre = request.POST.get("nombreACuentaTerceros")
                regimen = request.POST.get("c_RegimenFiscalACuentaTerceros")
                domicilio = request.POST.get("domicilioFiscalACuentaTerceros")

                if rfc or nombre or regimen or domicilio:
                    ACuentaTerceros.objects.update_or_create(
                        idConcepto=concepto,
                        defaults={
                            "rfcACuentaTerceros": rfc,
                            "nombreACuentaTerceros": nombre,
                            "c_RegimenFiscalACuentaTerceros_id": regimen or None,
                            "domicilioFiscalACuentaTerceros": domicilio,
                        }
                    )

            elif tipo == "cuenta_predial":
                formset = CuentaPredialFormSet(request.POST, prefix=f"predial-{i}")
                if formset.is_valid():
                    for f in formset:
                        if f.cleaned_data.get("DELETE") and f.instance.pk:
                            f.instance.delete()
                        else:
                            instancia = f.save(commit=False)
                            instancia.idConcepto = concepto
                            instancia.save()
                else:
                    print(f"Errores en Cuenta Predial del concepto {concepto.pk}:", formset.errors)

            elif tipo == "informacion_aduanera":
                formset = PedimentoCFDIFormSet(request.POST, prefix=f"aduana-{i}")
                print("Procesando Información Aduanera para el concepto:", concepto.pk)
                print("Datos recibidos:", request.POST)

                if formset.is_valid():
                    print("Formset de Información Aduanera es válido.")
                    for form in formset:
                        if form.cleaned_data.get("DELETE") and form.instance.pk:
                            form.instance.delete()
                        else:
                            instance = form.save(commit=False)
                            instance.concepto = concepto

                            # Determinar si se debe generar un nuevo número
                            generar_nuevo = False
                            
                            if instance.pk:
                                print("Editando un registro existente de Información Aduanera.", instance.pk)
                                original = PedimentoCFDI.objects.get(pk=instance.pk)
                                if (
                                    original.aduana != instance.aduana or
                                    original.patente != instance.patente or
                                    original.ejercicio != instance.ejercicio
                                ):
                                    generar_nuevo = True
                                else:
                                    # No se generará nuevo, conservar el número actual
                                    instance.numero = original.numero
                            else:
                                generar_nuevo = True  # Es un nuevo registro

                            if generar_nuevo:
                                # FECHA
                                ejercicio = instance.ejercicio
                                yy = str(ejercicio)[-2:]
                                y = str(datetime.now().year)[-1:]

                                # DATOS DE CATÁLOGOS
                                clave_aduana = str(instance.aduana.c_Aduana).zfill(2)
                                clave_patente = str(instance.patente.c_PatenteAduanal).zfill(4)
                                prefijo = f"{yy}  {clave_aduana}  {clave_patente}  {y}"

                                # Obtener InformacionFiscal desde el concepto → comprobante
                                informacion_fiscal = instance.concepto.comprobante.informacionFiscal

                                # Buscar el número mayor registrado con esa combinación
                                ultimo = PedimentoCFDI.objects.filter(
                                    concepto__comprobante__informacionFiscal=informacion_fiscal,
                                    aduana=instance.aduana,
                                    patente=instance.patente,
                                    ejercicio=ejercicio,
                                    numero__startswith=prefijo
                                ).aggregate(maximo=Max('numero'))['maximo']

                                if ultimo:
                                    ultima_secuencia = int(ultimo.strip()[-6:])
                                else:
                                    ultima_secuencia = 0

                                nueva_secuencia = str(ultima_secuencia + 1).zfill(6)
                                instance.numero = f"{prefijo}{nueva_secuencia}"

                            # Verificación para evitar duplicados
                            ya_existe = PedimentoCFDI.objects.filter(
                                concepto=concepto,
                                aduana=instance.aduana,
                                patente=instance.patente,
                                ejercicio=instance.ejercicio,
                            ).exclude(pk=instance.pk).exists()

                            if not ya_existe:
                                instance.save()
                else:
                    print(f"Errores en Información Aduanera del concepto {concepto.pk}:", formset.errors)


            elif tipo == "parte":
                formset = ParteFormSet(request.POST, prefix=f"parte-{i}")
                if formset.is_valid():
                    for f in formset:
                        if f.cleaned_data.get("DELETE") and f.instance.pk:
                            f.instance.delete()
                        else:
                            instancia = f.save(commit=False)
                            instancia.idConcepto = concepto
                            instancia.cantidad = 1  # Asignar cantidad por defecto
                            instancia.save()
                else:
                    print(f"Errores en Parte del concepto {concepto.pk}:", formset.errors)

            else:
                # Si no hay tipo definido, elimina todo por si acaso
                ACuentaTerceros.objects.filter(idConcepto=concepto).delete()
                CuentaPredial.objects.filter(idConcepto=concepto).delete()
                PedimentoCFDI.objects.filter(concepto=concepto).delete()
                Parte.objects.filter(idConcepto=concepto).delete()

        # ------------------------ COMPLEMENTOS DE ADDENDA (igual que ya tenías) ------------------------

        if isinstance(form.instance, Comprobante):
            addenda_inst = form.instance.addenda_set.first()
            ...
        else:
            print("⚠️ No es un comprobante. Es:", type(form.instance))
            return
        
        if not addenda_inst:
            print("No se encontró instancia de Addenda relacionada.")
            return

        tipo = addenda_inst.addenda if addenda_inst else None
        print("ID Addenda actual:", addenda_inst.id, "| Tipo:", tipo)

        # Limpia modelos no coincidentes
        if tipo != "siemens_gamesa":
            AddendaSiemensGamesa.objects.filter(addenda=addenda_inst).delete()
        if tipo != "grupo_ado":
            AddendaGrupoADO.objects.filter(addenda=addenda_inst).delete()
        if tipo != "waldos":
            AddendaWaldos.objects.filter(addenda=addenda_inst).delete()
        if tipo != "terra_multitransportes":
            AddendaTerraMultitransportes.objects.filter(addenda=addenda_inst).delete()

        # Guardado del formulario actual
        if tipo == "siemens_gamesa":
            AddendaSiemensGamesa.objects.update_or_create(
                addenda=addenda_inst,
                defaults={
                    "tipodocumento": request.POST.get("tipodocumento"),
                    "numero_orden": request.POST.get("numero_orden"),
                    "nota_entrega": request.POST.get("nota_entrega"),
                }
            )

        elif tipo == "grupo_ado":
            AddendaGrupoADO.objects.update_or_create(
                addenda=addenda_inst,
                defaults={
                    "tipo_addenda": request.POST.get("tipo_addenda"),
                    "pedido": request.POST.get("pedido"),
                }
            )

        elif tipo == "waldos":
            AddendaWaldos.objects.update_or_create(
                addenda=addenda_inst,
                defaults={
                    "numero_orden": request.POST.get("numero_orden"),
                }
            )

        elif tipo == "terra_multitransportes":
            formset = AddendaTerraMultitransportesFormSet(request.POST, prefix="terra")
            if formset.is_valid():
                for form in formset:
                    if form.cleaned_data.get("DELETE") and form.instance.pk:
                        form.instance.delete()
                    else:
                        instance = form.save(commit=False)
                        instance.addenda = addenda_inst

                        ya_existe = AddendaTerraMultitransportes.objects.filter(
                            addenda=addenda_inst,
                            contenedor=instance.contenedor,
                            reservacion=instance.reservacion,
                            referencia=instance.referencia,
                            descripcion=instance.descripcion,
                            valor=instance.valor,
                            iva=instance.iva,
                            retencion=instance.retencion,
                            total=instance.total,
                        ).exclude(pk=instance.pk).exists()

                        if not ya_existe:
                            instance.save()
            else:
                print("Errores en Formset Terra:", formset.errors)

        # Elimina Addenda si quedó sin tipo
        if tipo is None or (
            not AddendaSiemensGamesa.objects.filter(addenda=addenda_inst).exists() and
            not AddendaGrupoADO.objects.filter(addenda=addenda_inst).exists() and
            not AddendaWaldos.objects.filter(addenda=addenda_inst).exists() and
            not AddendaTerraMultitransportes.objects.filter(addenda=addenda_inst).exists()
        ):
            addenda_inst.delete()
            print("Addenda principal eliminada al no tener tipo relacionado.")

        # Puedes agregar los otros casos igual
                
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}

        if object_id:
            comprobante = Comprobante.objects.select_related('informacionFiscal').filter(pk=object_id).first()
        else:
            # usuario_cfdi = UsersCFDI.objects.get(idUserCFDI=request.user)
            # usuario_raiz = usuario_cfdi.get_raiz()
            # comprobante = InformacionFiscal.objects.filter(
            #     idUserCFDI__idUserCFDI=usuario_raiz,
            #     activo=True,
            #     es_principal=True
            # ).select_related('regimen_fiscal').first()
            comprobante = obtener_negocio_activo_para(request)
        extra_context['comprobante_obj'] = comprobante if object_id else None
        extra_context['info_fiscal_obj'] = comprobante.informacionFiscal if object_id and comprobante else comprobante
        
        if extra_context['info_fiscal_obj']:
            certificado_default = CertificadoSelloDigital.objects.filter(
                informacionFiscal=extra_context['info_fiscal_obj'],
                defecto=True,
                estado=True
            ).first()
            extra_context['certificado_default'] = certificado_default
        else:
            extra_context['certificado_default'] = None
    
        tasas = TasaOCuota.objects.select_related('impuesto', 'factor')
        tasas_por_impuesto = {}

        for tasa in tasas:
            cod = tasa.impuesto.c_Impuesto
            if cod not in tasas_por_impuesto:
                tasas_por_impuesto[cod] = []
            tasas_por_impuesto[cod].append({
                'id': tasa.pk,
                'representacionporcentual': str(tasa.representacionporcentual),
                'factor': tasa.factor.c_TipoFactor,
                'traslado': tasa.traslado,
                'retencion': tasa.retencion,
                'valor_maximo': tasa.valor_maximo,
                'rango': tasa.rango_o_fijo,
            })

        extra_context['tasas_por_impuesto'] = mark_safe(json.dumps(tasas_por_impuesto, default=str))
        extra_context['impuestos'] = Impuesto.objects.all()

        # Valores por defecto para el inline de Emisor
        emisor_defaults = {}
        if object_id:
            emisor = Emisor.objects.filter(comprobante_id=object_id).first()
            if emisor:
                emisor_defaults = {
                    'rfc': emisor.rfc or '',
                    'nombre': emisor.nombre or '',
                    'c_RegimenFiscal': emisor.c_RegimenFiscal.c_RegimenFiscal if emisor.c_RegimenFiscal else '',
                    'facAtrAdquirente': emisor.facAtrAdquirente or '',
                }
        else:
            info = extra_context.get('info_fiscal_obj')
            if info:
                emisor_defaults = {
                    'rfc': info.rfc or '',
                    'nombre': info.razon_social or '',
                    'c_RegimenFiscal': info.regimen_fiscal.c_RegimenFiscal if info.regimen_fiscal else '',
                    'facAtrAdquirente': '',
                }

        extra_context['emisor_defaults'] = mark_safe(json.dumps(emisor_defaults))

        return super().changeform_view(request, object_id, form_url, extra_context=extra_context)
    
    # #URL PARA HACER LA FUNCION
    # def get_urls(self):
    #             urls = super().get_urls()
    #             custom_urls = [
    #                 path(
    #                 '<pk>/generate-xml/',
    #                 self.admin_site.admin_view(self.generate_xml),
    #                 name='myapp_mymodel_generate_xml',
    #             ),
    #             #     path(
    #             #     '<pk>/generate-pdf/',
    #             #     self.admin_site.admin_view(self.generate_pdff),
    #             #     name='myapp_mymodel_generate_pdff',
    #             # ),
                        
    #             #     path('get-informacion-fiscal/', self.admin_site.admin_view(self.get_informacion_fiscal), name='get_informacion_fiscal'),
    #             ]
    #             return custom_urls + urls

    def generar_xml(self, request, pk):
        try:
            print("timbrando", pk.id)
            comprobante = obtener_datos_factura(pk.id)
            print("comprobante", comprobante)
            xml_content = comprobante.xml_bytes(pretty_print=True, validate=True).decode("utf-8")

            # Devolver el XML como respuesta HTTP
            response = HttpResponse(xml_content, content_type="application/xml")
            response["Content-Disposition"] = f'attachment; filename="factura_{pk}.xml"'
            return response
        
        except Exception as e:
            print("Error en timbrado:", traceback.format_exc())
            self.message_user(request, f"Ocurrió un error inesperado: {e}", level="error")
            return redirect("..")
    
    def generar_pdf(self, request, pk):
        try:
            print("timbrando", pk.id)
            comprobante = obtener_datos_factura(pk.id)

            # Generar el PDF utilizando la plantilla personalizada de comprobantes
            pdf_content = render_comprobante_pdf_bytes(comprobante)

            # Crear una respuesta HTTP con el PDF
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="factura_{pk}.pdf"'

            return response
        
        except Exception as e:
            print("Error en timbrado:", traceback.format_exc())
            self.message_user(request, f"Ocurrió un error inesperado: {e}", level="error")
            return redirect("..")
        
    def generar_xml_timbrado(self, request, pk):
        print("timbrando", pk)
        comprobante = ComprobanteEmitido.objects.filter(comprobante_relacionado=pk, uuid__isnull=False  # Solo si tiene UUID (timbrado)
        ).exclude(uuid="").order_by('-fecha').first()
        print(comprobante)
        xml_content = comprobante.xml_timbrado

        # Devolver el XML como respuesta HTTP
        response = HttpResponse(xml_content, content_type="application/xml")
        response["Content-Disposition"] = f'attachment; filename="factura_{pk}.xml"'
        return response

    def generar_pdf_timbrado(self, request, pk):
        print("timbrando", pk)
        
        cfdi_xml = ComprobanteEmitido.objects.filter(comprobante_relacionado=pk, uuid__isnull=False  # Solo si tiene UUID (timbrado)
        ).exclude(uuid="").order_by('-fecha').first()
        
        print("cfdi_xml", cfdi_xml) 
        print("XML:", cfdi_xml.xml_timbrado[:1000])  # Imprimir solo los primeros 1000 caracteres

        # Parsear el XML
        cfdi = CFDI.from_string(cfdi_xml.xml_timbrado.encode('utf-8'))

        print("cfdi: ", cfdi)

        # Obtener el timbre fiscal digital
        timbre = cfdi  # es un objeto tipo TimbreFiscalDigital

        

        # Generar el PDF utilizando la función `pdf_bytes`
        pdf_content = render_comprobante_pdf_bytes(cfdi)

        # Crear una respuesta HTTP con el PDF
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="factura_{pk}.pdf"'

        return response

    def facturar_y_timbrar(self, request, obj):
        """
        Timbra un comprobante, actualiza los datos fiscales,
        crea su complemento con TimbreFiscalDigital y lo guarda en ComprobanteEmitido.
        """
        usuario_cfdi = UsersCFDI.objects.get(idUserCFDI=request.user)
        usuario_raiz = usuario_cfdi.get_raiz()
        # == Obtén el usuario logueado y su Service_Plan correspondiente al servicio ==
        user_services = usuario_raiz.idUserServicePlan_id
        # Obtén los Service_Plan relacionados con el usuario logueado
        service_plans = Service_Plan.objects.filter(service=user_services.idService, plan=user_services.idPlan).first()
                
        # == Validar que este guardado si no lo guarda
        if not Comprobante.objects.filter(id=obj.id).exists():
            obj.save()  # Guarda si aún no se ha guardado


        # === Validar que el comprobante no esté ya timbrado ===
        comprobante_bd = Comprobante.objects.get(id=obj.id)
        if comprobante_bd.tipo_documento == 'timbrado':
            self.message_user(request, "Este comprobante ya fue timbrado y no se puede volver a timbrar.", level="warning")
            return redirect("..")
        try:
            with transaction.atomic():
                
                # === 0. Validar que el usuario aún tiene timbres disponibles ===
                conteo = usuario_raiz.get_conteo_timbres_actual()
                
                
                # Solo validar si el plan tiene límite (es decir, mayor a 0)
                if conteo.limite_timbres and conteo.contador_actual >= conteo.limite_timbres:
                    self.message_user(
                        request,
                        f"Has alcanzado el límite de {conteo.limite_timbres} timbres permitidos en tu plan. "
                        "No puedes timbrar más comprobantes en este periodo.",
                        level="error"
                    )
                    return redirect("..")
                
                # === 1. Generar XML y codificar a Base64 ===
                comprobante = obtener_datos_factura(obj.id)
                xml_str = comprobante.xml_bytes(pretty_print=True, validate=True).decode("utf-8")
                xml_base64 = base64.b64encode(xml_str.encode("utf-8")).decode("utf-8")

                # === 2. Enviar a timbrar vía PAC ===
                user = usuario_raiz.idUserCFDI.username
                token = usuario_raiz.decrypt_token()
                
                estado = SoapService.stamp('', xml_base64, user, token)

                # Verificar si hay errores de timbrado (Incidencias)
                if hasattr(estado, 'Incidencias') and estado.Incidencias:
                    mensajes = []
                    for incidencia in estado.Incidencias:
                        mensaje = f"Error {incidencia.CodigoError}: {incidencia.MensajeIncidencia}"
                        fecha_error = incidencia.FechaRegistro
                        mensajes.append(mensaje)
                    mensaje_completo = "\n".join(mensajes)
                    
                    try:
                        xml_str = xml_str.strip().replace("\x00", "")
                        root = ET.fromstring(xml_str)
                    except Exception as e:
                        self.message_user(request, f"Error al procesar el XML timbrado: {e}", level="error")
                        return redirect("..")

                    # === Detectar namespace de cfdi ===
                    ns_cfdi = root.tag.split("}")[0].strip("{")

                    # === Buscar Receptor ===
                    receptor = root.find(f".//{{{ns_cfdi}}}Receptor")
                    rfc_receptor = receptor.attrib.get("Rfc", "") if receptor is not None else "Desconocido"
                    nombre_receptor = receptor.attrib.get("Nombre", "No encontrado") if receptor is not None else "Desconocido"
                    folio = root.attrib.get("Folio", "")

                    # === Obtener Total del CFDI ===
                    total = root.attrib.get("Total", "0.00")
                    
                    
                    # === REGISTRAR INCIDENCIA COMO COMPROBANTE EMITIDO ===
                    # user_cfdi = UsersCFDI.objects.get(idUserCFDI=request.user)
                    
                    ComprobanteEmitido.objects.create(
                        idUserCFDI=usuario_raiz,
                        comprobante_relacionado=comprobante_bd,
                        fecha=fecha_error,
                        folio=folio or "-",
                        rfc=rfc_receptor,
                        nombre=nombre_receptor,
                        total=total,
                        tipo=self.tipo_default,
                        cod_estatus='Error al timbrar',
                        metodo_pago=root.attrib.get("MetodoPago", "No especificado"),
                        forma_pago=root.attrib.get("FormaPago", "No especificado"),
                        version_cfdi=root.attrib.get("Version", "Desconocida"),
                        detallesError=mensaje
                    )
                    
                    self.message_user(request, f"No se pudo timbrar el comprobante:\n{mensaje_completo}", level="error")
                    return redirect("..")

                # if not estado.xml:
                #     self.message_user(request, "Error: El PAC no devolvió XML timbrado.", level="error")
                #     print("Estado de timbrado:", estado) 
                #     return redirect("..")

                # === 3. Parsear el XML timbrado ===
                try:
                    xml = estado.xml.strip().replace("\x00", "")
                    root = ET.fromstring(xml)
                except Exception as e:
                    self.message_user(request, f"Error al procesar el XML timbrado: {e}", level="error")
                    return redirect("..")

                # === 4. Detectar namespaces y obtener nodos clave ===
                namespaces = {node.tag.split("}")[0].strip("{"): node.tag.split("}")[0].strip("{") for node in root.iter()}
                ns = {
                    'cfdi': list(namespaces.keys())[0],
                    'tfd': list(namespaces.keys())[1]
                }
                timbre = root.find(f".//{{{ns['tfd']}}}TimbreFiscalDigital")
                receptor = root.find(f".//{{{ns['cfdi']}}}Receptor")

                if timbre is None or receptor is None:
                    self.message_user(request, "Error: El XML timbrado no contiene los nodos obligatorios.", level="error")
                    return redirect("..")

                # === 5. Extraer datos fiscales y del receptor ===
                uuid = timbre.attrib.get("UUID")
                rfc_receptor = receptor.attrib.get("Rfc", "")
                nombre_receptor = receptor.attrib.get("Nombre", "No encontrado")
                folio = root.attrib.get("Folio", "")
                total = root.attrib.get("Total", "0.00")

                # === 6. Actualizar el comprobante original ===
                comprobante_bd.sello = root.attrib.get("Sello", "")
                comprobante_bd.certificado = root.attrib.get("Certificado", "")
                comprobante_bd.noCertificado = root.attrib.get("NoCertificado", "")
                comprobante_bd.tipo_documento = "timbrado"
                comprobante_bd.save(update_fields=["sello", "certificado", "noCertificado", "tipo_documento"])

                # === 7. Crear o recuperar el tipo de complemento y la versión ===
                tipo_complemento, _ = TiposComplemento.objects.get_or_create(
                    nombre="Timbre Fiscal Digital",
                    defaults={"descripcion": "Complemento generado por el PAC", "version": "1.1"}
                )

                # === 8. Crear el complemento y timbre fiscal ===
                complemento = Complemento.objects.create(
                    idComrobante=comprobante_bd,
                    idTipoComplemento=tipo_complemento
                )
                TimbreFiscalDigital.objects.create(
                    idComplemento=complemento,
                    uuid=uuid,
                    fechaTimbrado=estado.Fecha,
                    rfcProvCertif=timbre.attrib.get("RfcProvCertif"),
                    selloCFD=timbre.attrib.get("SelloCFD"),
                    selloSAT=timbre.attrib.get("SelloSAT"),
                    noCerticadoSAT=timbre.attrib.get("NoCertificadoSAT"),
                )

                # === 9. Obtener usuario y registrar en ComprobanteEmitido ===
                # user_cfdi = UsersCFDI.objects.get(idUserCFDI=request.user)
                
                if ComprobanteEmitido.objects.filter(uuid=uuid).exists():
                    self.message_user(request, "Este comprobante ya fue registrado anteriormente.", level="warning")
                    return redirect("..")

                ComprobanteEmitido.objects.create(
                    idUserCFDI=usuario_raiz,
                    comprobante_relacionado=comprobante_bd,
                    fecha=estado.Fecha,
                    folio=folio,
                    uuid=uuid,
                    rfc=rfc_receptor,
                    nombre=nombre_receptor,
                    fecha_pago=comprobante_bd.fechaPago,
                    total=total,
                    xml_timbrado=estado.xml,
                    tipo=self.tipo_default,
                    cod_estatus=estado.CodEstatus,
                    metodo_pago=root.attrib.get("MetodoPago", "No especificado"),
                    forma_pago=root.attrib.get("FormaPago", "No especificado"),
                    version_cfdi=root.attrib.get("Version", "Desconocida"),
                )
                
                lat = request.POST.get("latitud")
                lon = request.POST.get("longitud")
                ubicacion = f"{lat}, {lon}" if lat and lon else None
                ip = request.META.get("REMOTE_ADDR")

                bitacora, _ = BitacoraCFDI.objects.get_or_create(comprobante=comprobante_bd)
                bitacora.timbrado_por = request.user
                bitacora.fecha_timbrado = now()
                bitacora.ip_timbrado = ip
                bitacora.ubicacion_timbrado = ubicacion
                bitacora.save()
                
                # === Actualizar contador de timbres del usuario raíz ===
                try:
                    usuario_raiz.registrar_timbre()
                except ValueError as e:
                    # Esto no debería ocurrir porque ya se validó antes, pero por seguridad lo manejamos
                    self.message_user(request, str(e), level="warning")

                self.message_user(request, "Comprobante timbrado correctamente.", level="success")
                return redirect(self.url_default)


        except Exception as e:
            print("Error en timbrado:", traceback.format_exc())
            self.message_user(request, f"Ocurrió un error inesperado: {e}", level="error")
            return redirect("..")

    
mi_admin_site.register(Comprobante,ComprobanteAdmin)

class ComprobanteEgresoAdmin(ComprobanteAdmin):
    tipo_comprobante_default = 'E'
    url_default = 'mi_admin:cfdi_comprobanteegreso_changelist'
    tipo_default='Factura de egreso'
    
    

mi_admin_site.register(ComprobanteEgreso, ComprobanteEgresoAdmin)

class ComprobanteTrasladoAdmin(ComprobanteAdmin):
    tipo_comprobante_default = 'T'
    url_default = 'mi_admin:cfdi_comprobantetraslado_changelist'
    tipo_default='Traslado'

mi_admin_site.register(ComprobanteTraslado, ComprobanteTrasladoAdmin)

class HorasExtraInline(nested_admin.NestedStackedInline):
    model = HorasExtra
    extra = 1
    max_num = None  # Solo se permite un formulario
    #max_num = 1

    
    fields = ['horas_extra','tipo_horas','dias','importe_pagado']

class incapacidadInline(nested_admin.NestedStackedInline):
    model = Incapacidad
    extra = 1
    max_num = None   # Solo se permite un formulario
  
    fields = ['dias_incapacidad','importe_Monetario','tipo_incapacidad']

class PercepcionForm(forms.ModelForm):
    class Meta:
        model = Percepcion
        fields = '__all__'

    

class PercepcionInline(nested_admin.NestedStackedInline):
    model = Percepcion
    form = PercepcionForm
    extra = 2
     # Allow multiple perception records
    max_num = None
    inlines = [HorasExtraInline]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "nomina" and hasattr(request, "_obj_") and request._obj_:
            kwargs["queryset"] = Nomina.objects.filter(comprobanteNomina12=request._obj_)
            nomina_default = Nomina.objects.filter(comprobanteNomina12=request._obj_).first()
            if nomina_default:
                kwargs["initial"] = nomina_default.id
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    

class DeduccionInline(nested_admin.NestedStackedInline):
    model = Deduccion
    extra = 1
    max_num = None
    can_delete = True
    inlines = [incapacidadInline]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "nomina" and hasattr(request, "_obj_") and request._obj_:
            kwargs["queryset"] = Nomina.objects.filter(comprobanteNomina12=request._obj_)
            nomina_default = Nomina.objects.filter(comprobanteNomina12=request._obj_).first()
            if nomina_default:
                kwargs["initial"] = nomina_default.id
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class OtroPagoInline(nested_admin.NestedStackedInline):
    model = OtroPago
    extra = 1  # Solo se permite un formulario
    max_num = 1  # Sin límite en la cantidad de formularios
    can_delete = True
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "nomina" and hasattr(request, "_obj_") and request._obj_:
            kwargs["queryset"] = Nomina.objects.filter(comprobanteNomina12=request._obj_)
            nomina_default = Nomina.objects.filter(comprobanteNomina12=request._obj_).first()
            if nomina_default:
                kwargs["initial"] = nomina_default.id
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class subcontratacionInline(nested_admin.NestedTabularInline):
    model = subcontratacion
    extra = 1
    max_num = 1  # Solo se permite un formulario


class Nomina12Form(forms.ModelForm):
    class Meta:
        model = ComprobanteNomina12
        fields = '__all__'
        
        widgets = {
            
            'condicionesDePago': forms.Textarea(attrs={
                'class': 'form-control border border-secondary',
                'rows': 2,
                'placeholder': 'Condiciones de pago...'
            }),
            'c_MetodoPago': forms.Select(attrs={'class': 'form-select'}),
            'c_FormaPago': forms.Select(attrs={'class': 'form-select'}),
            'c_Moneda': forms.Select(attrs={'class': 'form-select'}),
        }


    
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # 👉 Precargar la fecha actual
        if not self.instance.pk:  # solo en creación, no en edición
            self.fields['fechaEmision'].initial = now()

        print("Request en form:", request)
        if request:
            print("Usuario en form:", request.user)
            try:
                usuario_cfdi = UsersCFDI.objects.get(idUserCFDI=request.user)
                usuario_raiz = usuario_cfdi.get_raiz()
                # Negocio activo desde sesión
                negocio_actual = obtener_negocio_activo_para(request)
                #negocio_actual = InformacionFiscal.objects.filter(idUserCFDI=usuario_raiz, activo=True, es_principal=True).first()
                if negocio_actual:
                    self.fields['informacionFiscal'].queryset = InformacionFiscal.objects.filter(pk=negocio_actual.pk)
                    self.fields['informacionFiscal'].initial = negocio_actual
            except UsersCFDI.DoesNotExist:
                self.fields['informacionFiscal'].queryset = InformacionFiscal.objects.none()


class NominaAdmin(ModelAdmin):
    change_form_template = 'LadoClientes/forms nomina/change_formnomina-empleados.html'
    change_list_template = 'LadoClientes/forms nomina/change_list.html'
    delete_confirmation_template = 'LadoClientes/forms/delete_confirmation.html'
    delete_selected_confirmation_template = 'LadoClientes/forms/delete_selected_confirmation.html'
    index_template = 'LadoClientes/pages/index.html'

    autocomplete_fields = ['c_CodigoPostal']

mi_admin_site.register(Nomina, NominaAdmin)


                
class Nomina12Admin(nested_admin.NestedModelAdmin):
    form = Nomina12Form
    tipo_comprobante_default = 'N'
    change_form_template = 'LadoClientes/forms nomina/change_formnomina_sn.html'
    change_list_template = 'LadoClientes/forms nomina/change_list.html'
    delete_confirmation_template = 'LadoClientes/forms/delete_confirmation.html'
    delete_selected_confirmation_template = 'LadoClientes/forms/delete_selected_confirmation.html'
    index_template = 'LadoClientes/pages/index.html'

    list_display = ('id','version', 'informacionFiscal', 'serie', 'folio', 'c_FormaPago', 'noCertificado')
    list_filter = ('tipo_documento', 'c_TipoDeComprobante')
    search_fields = ('serie', 'folio', 'informacionFiscal', 'c_TipoDeComprobante', 'c_LugarExpedicion', 'c_MetodoPago', 'c_FormaPago', 'c_Moneda', 'confirmacion')

    ordering = ['id']
    list_per_page = 10

    # readonly_fields = ('Fecha',)

    
    fieldsets = (
        ('Datos Generales', {
            'fields': ('version', 'informacionFiscal', 'serie', 'folio', 'fechaEmision')
        }),
        ('Información de pago', {
            'fields': (
                'c_MetodoPago',
                'c_FormaPago',
                'condicionesDePago',
                'c_Moneda',
                'tipoCambio',
                'fechaPago'
            )
        }),
    )


    inlines = [
            EmisorInline,CfdiRelacionadosInline,nominaInline,PercepcionInline,
            DeduccionInline,OtroPagoInline,subcontratacionInline
        ]






    # inlines = [ConceptoInline]
    autocomplete_fields = ['c_LugarExpedicion']  # Autocompletar el campo de código postal

        
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs.filter(c_TipoDeComprobante__c_TipoDeComprobante=self.tipo_comprobante_default)
        usuario_cfdi = UsersCFDI.objects.get(idUserCFDI=request.user)
        usuario_raiz = usuario_cfdi.get_raiz()
        negocio_activo = obtener_negocio_activo_para(request)
        #informacionFiscal__es_principal=True con esta linea nos aseguramos que solo se muestren los comprobantes del usuario logueado y su información fiscal principal
        
        return qs.filter(informacionFiscal=negocio_activo,c_TipoDeComprobante__c_TipoDeComprobante=self.tipo_comprobante_default)
    
    def get_formsets_with_inlines(self, request, obj=None):
        request._obj_ = obj
        return super().get_formsets_with_inlines(request, obj)
    
    def has_change_permission(self, request, obj=None):
        if obj and getattr(obj, "tipo_documento", "").lower() == "timbrado":
            if request.method not in ("GET", "HEAD", "OPTIONS"):
                return False
        return super().has_change_permission(request, obj)
    
    def get_form(self, request, obj=None, **kwargs):
        Form = super().get_form(request, obj, **kwargs)
        class CustomForm(Form):
            def __init__(self2, *args, **kwargs2):
                kwargs2['request'] = request
                super().__init__(*args, **kwargs2)
        return CustomForm
    
    def response_add(self, request, obj, post_url_continue=None):
        if "_facturar_timbrar_nomina" in request.POST:
            print("Botón 'Facturar y Timbrar' presionado desde ADD.")
            return self.facturar_y_timbrar_nomina(request, obj)
        
        if "_generar_pdf_nomina" in request.POST:
            print("Botón 'PDF' presionado desde ADD.")
            return self.generate_pdf_nomina(request, obj)
        
        if "_generar_xml_nomina" in request.POST:
            print("Botón 'XML' presionado desde ADD.")
            return self.generate_xml_nomina(request, obj)
        
        return super().response_add(request, obj, post_url_continue)
    
    def response_change(self, request, obj):
        """
        Maneja acciones personalizadas al guardar el modelo.
        """
        
        # Si está timbrado, no permitir guardado de ninguna forma
        if getattr(obj, "tipo_documento", "").lower() == "timbrado":
            if any(key in request.POST for key in ["_save", "_continue", "_addanother",
                                                "_facturar_timbrar_nomina", "_generar_pdf_nomina", "_generar_xml_nomina"]):
                self.message_user(request, "Este comprobante ya está timbrado y no puede modificarse.", level=messages.ERROR)
                return HttpResponseRedirect(request.path) 
            
            
        if "_facturar_timbrar_nomina" in request.POST:
            form = self.get_form(request, obj)(request.POST, request.FILES, instance=obj)
            formsets, inline_instances = self._create_formsets(request, obj, change=True)

            if form.is_valid() and all(fs.is_valid() for fs in formsets):
                # 1. Guardar el comprobante (sin guardarlo aún)
                obj = form.save(commit=False)

                # 2. Guardar modelo (ejecuta save_model)
                self.save_model(request, obj, form, change=True)

                # 3. Guardar todos los formsets (inlines)
                for formset in formsets:
                    self.save_formset(request, form, formset, change=True)

                # 4. Guardar relaciones adicionales (many-to-many, etc.)
                self.save_related(request, form, formsets, change=True)

                # 5. Guardar finalmente el objeto en la base de datos
                obj.save()

                # 6. Llamar al timbrado
                return self.facturar_y_timbrar_nomina(request, obj)
            
            else:
                # Si hubo errores, mostrar el mismo formulario con los errores
                return self.changeform_view(request, str(obj.pk), form_url="", extra_context={
                    'form': form,
                    'errors': form.errors,
                })
        
        if "_generar_pdf_nomina" in request.POST:
            form = self.get_form(request, obj)(request.POST, request.FILES, instance=obj)
            formsets, inline_instances = self._create_formsets(request, obj, change=True)

            if form.is_valid() and all(fs.is_valid() for fs in formsets):
                # 1. Guardar el comprobante (sin guardarlo aún)
                obj = form.save(commit=False)

                # 2. Guardar modelo (ejecuta save_model)
                self.save_model(request, obj, form, change=True)

                # 3. Guardar todos los formsets (inlines)
                for formset in formsets:
                    self.save_formset(request, form, formset, change=True)

                # 4. Guardar relaciones adicionales (many-to-many, etc.)
                self.save_related(request, form, formsets, change=True)

                # 5. Guardar finalmente el objeto en la base de datos
                obj.save()

                # 6. Llamar al pdf
                return self.generate_pdf_nomina(request, obj)
            
            else:
                # Si hubo errores, mostrar el mismo formulario con los errores
                return self.changeform_view(request, str(obj.pk), form_url="", extra_context={
                    'form': form,
                    'errors': form.errors,
                })
                
        if "_generar_xml_nomina" in request.POST:
            form = self.get_form(request, obj)(request.POST, request.FILES, instance=obj)
            formsets, inline_instances = self._create_formsets(request, obj, change=True)

            if form.is_valid() and all(fs.is_valid() for fs in formsets):
                # 1. Guardar el comprobante (sin guardarlo aún)
                obj = form.save(commit=False)

                # 2. Guardar modelo (ejecuta save_model)
                self.save_model(request, obj, form, change=True)

                # 3. Guardar todos los formsets (inlines)
                for formset in formsets:
                    self.save_formset(request, form, formset, change=True)

                # 4. Guardar relaciones adicionales (many-to-many, etc.)
                self.save_related(request, form, formsets, change=True)

                # 5. Guardar finalmente el objeto en la base de datos
                obj.save()

                # 6. Llamar al xml
                return self.generate_xml_nomina(request, obj)
            
            else:
                # Si hubo errores, mostrar el mismo formulario con los errores
                return self.changeform_view(request, str(obj.pk), form_url="", extra_context={
                    'form': form,
                    'errors': form.errors,
                })
        
        if "_save" in request.POST:
            return super().response_change(request, obj)
        
        if "_generar_pdf_nomina_timbrado" in request.POST:
            return self.generar_pdf_nomina_timbrado(request, obj)
        
        if "_generar_xml_nomina_timbrado" in request.POST:
            return self.generar_xml_nomina_timbrado(request, obj)

        if "_save_draft" in request.POST:  # Detectar si se presionó el botón "Guardar borrador". _save_draft es el boton vinculado con la plantilla change_form.html de django admin
            return super().response_change(request, obj)
        
        return super().response_change(request, obj)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if request.method == "POST":

            # 🔹 Si se presionó el botón 'Facturar y Timbrar', redirigir manualmente a `response_change()`
            if "_facturar_timbrar_nomina" in request.POST:
                return self.response_change(request, self.get_object(request, object_id))
            
            if "_generar_pdf_nomina" in request.POST:
                return self.response_change(request, self.get_object(request, object_id))
            
            if "_generar_xml_nomina" in request.POST:
                return self.response_change(request, self.get_object(request, object_id))
            
            if "_generar_pdf_nomina_timbrado" in request.POST:
                 return self.response_change(request, self.get_object(request, object_id))
             
            if "_generar_xml_nomina_timbrado" in request.POST:
                 return self.response_change(request, self.get_object(request, object_id))
             
            if "_save_draft" in request.POST:
                return self.response_change(request, self.get_object(request, object_id))

        extra_context = extra_context or {}
        extra_context["changelist_url"] = request.GET.get("changelist", request.META.get("HTTP_REFERER"))

        return super().change_view(request, object_id, form_url, extra_context=extra_context)
    
    def save_model(self, request, obj, form, change):
        """
        Guarda el comprobante, asignando automáticamente al usuario logueado y su información fiscal principal.
        """
        
        super(nested_admin.NestedModelAdmin, self).save_model(request, obj, form, change)
        
        lat = request.POST.get("latitud")
        lon = request.POST.get("longitud")
        ubicacion = f"{lat}, {lon}" if lat and lon else None
        ip = request.META.get("REMOTE_ADDR")

        bitacora, _ = BitacoraCFDI.objects.get_or_create(comprobante=obj)
        
        if not change:
            # Asignar el usuario (si el modelo Comprobante lo tiene)
            if hasattr(obj, 'user'):
                obj.user = request.user

            # Obtener la información fiscal principal del usuario CFDI relacionado
            try:
                # usuario_cfdi = UsersCFDI.objects.get(idUserCFDI=request.user)
                # usuario_raiz = usuario_cfdi.get_raiz()
                # informacion_principal = InformacionFiscal.objects.filter(
                #     idUserCFDI=usuario_raiz,
                #     es_principal=True
                # ).first()
                informacion_principal = obtener_negocio_activo_para(request)

                if informacion_principal:
                    obj.informacionFiscal = informacion_principal
                    obj.c_LugarExpedicion = CodigoPostal.objects.get(c_CodigoPostal=informacion_principal.codigo_postal)
                    obj.c_TipoDeComprobante = TipoComprobante.objects.get(c_TipoDeComprobante='N')
                    obj.c_Exportacion = Exportacion.objects.get(c_Exportacion='01')
            except UsersCFDI.DoesNotExist:
                pass  # O registrar un mensaje de error si lo necesitas

            bitacora.creado_por = request.user
            bitacora.fecha_creacion = now()
            bitacora.ip_creacion = ip
            bitacora.ubicacion_creacion = ubicacion
            
        else:
            bitacora.editado_por = request.user
            bitacora.fecha_edicion = now()
            bitacora.ip_edicion = ip
            bitacora.ubicacion_edicion = ubicacion
            
        super().save_model(request, obj, form, change)
        
    def save_related(self, request, form, formsets, change):
        print("Entrando a save_related del admin...")  # <--- DEBUG PRINT

        super().save_related(request, form, formsets, change)

        comprobante = form.instance
        instancia_nomina = None

        # 1. Guardar primero el formset de Nomina
        for formset in formsets:
            if isinstance(formset, forms.BaseInlineFormSet) and formset.model == Nomina:
                print("Procesando formset de Nomina...")  # <--- DEBUG
                for form_nomina in formset.forms:
                    if not form_nomina.cleaned_data.get('DELETE', False):
                        instancia_nomina = form_nomina.save(commit=False)
                        instancia_nomina.comprobanteNomina12 = comprobante
                        instancia_nomina.save()
                        form_nomina.save_m2m()
                        print(f"Nomina guardada: id={instancia_nomina.id}")  # <--- DEBUG

        # Asegurar que se haya guardado una Nomina
        if not instancia_nomina:
            print("No se guardó ninguna nómina, abortando save_related.")  # <--- DEBUG
            return

        # 2. Guardar Percepciones y, si aplica, sus incapacidades
        for formset in formsets:
            if isinstance(formset, forms.BaseInlineFormSet) and formset.model == Percepcion:
                print("Procesando formset de Percepcion...")  # <--- DEBUG
                for idx, form_percepcion in enumerate(formset.forms):
                    if not form_percepcion.cleaned_data or form_percepcion.cleaned_data.get('DELETE', False):
                        continue
                    instancia_percepcion = form_percepcion.save(commit=False)
                    instancia_percepcion.nomina = instancia_nomina
                    instancia_percepcion.save()
                    form_percepcion.save_m2m()
                    print(f"Percepcion guardada: id={instancia_percepcion.id}, tipo={getattr(instancia_percepcion.tipo_percepcion, 'c_TipoPercepcion', None)}")  # <--- DEBUG

                    # Incapacidad (tipo_percepcion == "014")
                    tipo_percepcion = getattr(instancia_percepcion.tipo_percepcion, 'c_TipoPercepcion', None)
                    if tipo_percepcion == "014":
                        print("Procesando formset de Incapacidad para percepción tipo 014...")  # <--- DEBUG
                        IncapacidadFormSet = inlineformset_factory(
                            Percepcion, Incapacidad,
                            form=IncapacidadForm,
                            fields=['dias_incapacidad', 'importe_Monetario', 'tipo_incapacidad'],
                            extra=0, can_delete=True
                        )
                        incapacidad_formset = IncapacidadFormSet(
                            request.POST, request.FILES,
                            instance=instancia_percepcion,
                            prefix='incapacidades_set'
                        )
                        if incapacidad_formset.is_valid():
                            incapacidad_formset.save()
                            print("Incapacidad guardada correctamente para percepción id:", instancia_percepcion.id)  # <--- DEBUG
                        else:
                            print("Errores en IncapacidadFormSet:", incapacidad_formset.errors)
                            print("Non-form errors:", incapacidad_formset.non_form_errors())


                         # Separación/Indemnización (tipo_percepcion == "023")
                    elif tipo_percepcion == "023":
                        print("Procesando formset de Separación/Indemnización para percepción tipo 023...")  # <--- DEBUG
                        from .forms import SeparacionIndemnizacionForm, SeparacionIndemnizacionFormSet
                        SeparacionIndemnizacionFormSet = inlineformset_factory(
                            Percepcion, SeparacionIndemnizacion,
                            form=SeparacionIndemnizacionForm,
                            fields=[
                                'total_pagado', 'num_anos_servicio', 'ultimo_sueldo_mens_ord',
                                'ingreso_acumulable', 'ingreso_no_acumulable'
                            ],
                            extra=0, can_delete=True
                        )
                        separacionindemnizacion_formset = SeparacionIndemnizacionFormSet(
                            request.POST, request.FILES,
                            instance=instancia_percepcion,
                            prefix='separacionindemnizacion_set'
                        )
                        if separacionindemnizacion_formset.is_valid():
                            separacionindemnizacion_formset.save()
                            print("Separación/Indemnización guardada correctamente para percepción id:", instancia_percepcion.id)  # <--- DEBUG
                        else:
                            print("Errores en SeparacionIndemnizacionFormSet:", separacionindemnizacion_formset.errors)
                            print("Non-form errors:", separacionindemnizacion_formset.non_form_errors())

                    elif tipo_percepcion == "039":
                        print("Procesando formset de Jubilación/Pensión/Retiro para percepción tipo 039...")  # <--- DEBUG
                        from .forms import JubilacionPensionRetiroForm, JubilacionPensionRetiroFormSet
                        JubilacionPensionRetiroFormSet = inlineformset_factory(
                            Percepcion, JubilacionPensionRetiro,
                            form=JubilacionPensionRetiroForm,
                            fields=[
                                'total_una_exhibicion',
                                'ingreso_acumulable',
                                'ingreso_no_acumulable',
                            ],
                            extra=0, can_delete=True
                        )
                        jubilacionpensionretiro_formset = JubilacionPensionRetiroFormSet(
                            request.POST, request.FILES,
                            instance=instancia_percepcion,
                            prefix='jubilacionpensionretiro_set'
                        )
                        if jubilacionpensionretiro_formset.is_valid():
                            jubilacionpensionretiro_formset.save()
                            print("Jubilación/Pensión/Retiro guardada correctamente para percepción id:", instancia_percepcion.id)  # <--- DEBUG
                        else:
                            print("Errores en JubilacionPensionRetiroFormSet:", jubilacionpensionretiro_formset.errors)
                            print("Non-form errors:", jubilacionpensionretiro_formset.non_form_errors())

        

        # Limpieza: borra incapacidad si el tipo_percepcion ya no aplica
        print("Limpiando incapacidades no válidas...")  # <--- DEBUG
        for percepcion in Percepcion.objects.filter(nomina=instancia_nomina):
            tipo_percepcion = getattr(percepcion.tipo_percepcion, 'c_TipoPercepcion', None)
            if tipo_percepcion != "014":
                Incapacidad.objects.filter(percepcion=percepcion).delete()
                print(f"Incapacidades eliminadas para percepción id: {percepcion.id}")  # <--- DEBUG
        

       

       
       



    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}

        if object_id:
            comprobante = Comprobante.objects.select_related('informacionFiscal').filter(pk=object_id).first()
        else:
            usuario_cfdi = UsersCFDI.objects.get(idUserCFDI=request.user)
            usuario_raiz = usuario_cfdi.get_raiz()
            # comprobante = InformacionFiscal.objects.filter(
            #     idUserCFDI__idUserCFDI=usuario_raiz,
            #     activo=True,
            #     es_principal=True
            # ).select_related('regimen_fiscal').first()
            comprobante = obtener_negocio_activo_para(request)
        extra_context['comprobante_obj'] = comprobante if object_id else None
        extra_context['info_fiscal_obj'] = comprobante.informacionFiscal if object_id and comprobante else comprobante
        
        if extra_context['info_fiscal_obj']:
            certificado_default = CertificadoSelloDigital.objects.filter(
                informacionFiscal=extra_context['info_fiscal_obj'],
                defecto=True,
                estado=True
            ).first()
            extra_context['certificado_default'] = certificado_default
        else:
            extra_context['certificado_default'] = None
        
        tasas = TasaOCuota.objects.select_related('impuesto', 'factor')
        tasas_por_impuesto = {}

        for tasa in tasas:
            cod = tasa.impuesto.c_Impuesto
            if cod not in tasas_por_impuesto:
                tasas_por_impuesto[cod] = []
            tasas_por_impuesto[cod].append({
                'id': tasa.pk,
                'representacionporcentual': str(tasa.representacionporcentual),
                'factor': tasa.factor.c_TipoFactor,
                'traslado': tasa.traslado,
                'retencion': tasa.retencion,
            })

        extra_context['tasas_por_impuesto'] = mark_safe(json.dumps(tasas_por_impuesto))
        extra_context['impuestos'] = Impuesto.objects.all()


        # Valores por defecto para el inline de Emisor
        emisor_defaults = {}
        if object_id:
            emisor = Emisor.objects.filter(comprobante_id=object_id).first()
            if emisor:
                emisor_defaults = {
                    'rfc': emisor.rfc or '',
                    'nombre': emisor.nombre or '',
                    'c_RegimenFiscal': emisor.c_RegimenFiscal.c_RegimenFiscal if emisor.c_RegimenFiscal else '',
                    'facAtrAdquirente': emisor.facAtrAdquirente or '',
                }
        else:
            info = extra_context.get('info_fiscal_obj')
            if info:
                emisor_defaults = {
                    'rfc': info.rfc or '',
                    'nombre': info.razon_social or '',
                    'c_RegimenFiscal': info.regimen_fiscal.c_RegimenFiscal if info.regimen_fiscal else '',
                    'facAtrAdquirente': '',
                }

        extra_context['emisor_defaults'] = mark_safe(json.dumps(emisor_defaults))

        return super().changeform_view(request, object_id, form_url, extra_context=extra_context)
    


    # def get_urls(self):
    #             urls = super().get_urls()
    #             custom_urls = [
    #                 path(
    #                 'xml/nomina/<int:pk>/',
    #                 self.admin_site.admin_view(self.generate_xml_nomina),
    #                 name='myapp_mymodel_generate_xml_nomina',
    #             ),
                
    #                 path(
    #                 '<pk>/generate-pdf/',
    #                 self.admin_site.admin_view(self.generate_pdff),
    #                 name='myapp_mymodel_generate_pdf_nomina',
    #             ),
                        
    #             #     path('get-informacion-fiscal/', self.admin_site.admin_view(self.get_informacion_fiscal), name='get_informacion_fiscal'),
    #             ]
    #             return custom_urls + urls

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'nomina-data/<int:pk>/',
                self.admin_site.admin_view(self.nomina_data),
                name='cfdi_comprobantenomina12_nomina_data',
            ),
            # path('get-informacion-fiscal/', self.admin_site.admin_view(self.get_informacion_fiscal), name='get_informacion_fiscal'),
        ]
        return custom_urls + urls

    def nomina_data(self, request, pk):
        nomina = get_object_or_404(Nomina, pk=pk)
        data = model_to_dict(nomina)
        return JsonResponse(data)


    # def generate_xml_nomina(self, request, pk):
    #     nomina_cfdi = obtener_datos_nomina(pk)
    #     if not nomina_cfdi:
    #         return HttpResponse("No se pudo generar el XML. Datos incompletos.", status=400)

    #     # Serializar el XML
    #     xml_element = nomina_cfdi.to_xml()
    #     xml_str = etree.tostring(xml_element, pretty_print=True, xml_declaration=True, encoding="UTF-8")

    #     # Respuesta HTTP
    #     response = HttpResponse(xml_str, content_type='application/xml')
    #     response['Content-Disposition'] = f'attachment; filename=nomina_{pk}.xml'
    #     return response

    def generate_xml_nomina(self, request, pk):
        try:
            comprobante = obtener_datos_comprobante_nomina12(pk.id)  # Desempaqueta la tupla
            xml_content = comprobante.xml_bytes(pretty_print=True, validate=True).decode("utf-8")

            # Devolver el XML como respuesta HTTP
            response = HttpResponse(xml_content, content_type="application/xml")
            response["Content-Disposition"] = f'attachment; filename="factura_{pk}.xml"'
            return response
        
        except Exception as e:
            print("Error en timbrado:", traceback.format_exc())
            self.message_user(request, f"Ocurrió un error inesperado: {e}", level="error")
            return redirect("..")

    
    def generate_pdf_nomina(self, request, pk):
        try:
            comprobante = obtener_datos_comprobante_nomina12(pk.id)

            # Generar el PDF utilizando la función `pdf_bytes`
            pdf_content = render_comprobante_pdf_bytes(comprobante)

            # Crear una respuesta HTTP con el PDF
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="nomina_{pk}.pdf"'

            return response
        
        except Exception as e:
            print("Error en timbrado:", traceback.format_exc())
            self.message_user(request, f"Ocurrió un error inesperado: {e}", level="error")
            return redirect("..")
    
    def generar_xml_nomina_timbrado(self, request, pk):
        print("timbrando", pk)
        comprobante = ComprobanteEmitido.objects.filter(comprobante_relacionado=pk, uuid__isnull=False  # Solo si tiene UUID (timbrado)
        ).exclude(uuid="").order_by('-fecha').first()
        print(comprobante)
        xml_content = comprobante.xml_timbrado

        # Devolver el XML como respuesta HTTP
        response = HttpResponse(xml_content, content_type="application/xml")
        response["Content-Disposition"] = f'attachment; filename="factura_{pk}.xml"'
        return response

    def generar_pdf_nomina_timbrado(self, request, pk):
        print("timbrando", pk)
        
        cfdi_xml = ComprobanteEmitido.objects.filter(comprobante_relacionado=pk, uuid__isnull=False  # Solo si tiene UUID (timbrado)
        ).exclude(uuid="").order_by('-fecha').first()
        
        print("cfdi_xml", cfdi_xml) 
        print("XML:", cfdi_xml.xml_timbrado[:1000])  # Imprimir solo los primeros 1000 caracteres

        # Parsear el XML
        cfdi = CFDI.from_string(cfdi_xml.xml_timbrado.encode('utf-8'))

        print("cfdi: ", cfdi)

        # Obtener el timbre fiscal digital
        timbre = cfdi  # es un objeto tipo TimbreFiscalDigital

        

        # Generar el PDF utilizando la función `pdf_bytes`
        pdf_content = render_comprobante_pdf_bytes(cfdi)

        # Crear una respuesta HTTP con el PDF
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="factura_{pk}.pdf"'

        return response



    def facturar_y_timbrar_nomina(self, request, obj):
        try:
            usuario_cfdi = UsersCFDI.objects.get(idUserCFDI=request.user)
            usuario_raiz = usuario_cfdi.get_raiz()
            # == Obtén el usuario logueado y su Service_Plan correspondiente al servicio ==
            user_services = usuario_raiz.idUserServicePlan_id
            # Obtén los Service_Plan relacionados con el usuario logueado
            service_plans = Service_Plan.objects.filter(service=user_services.idService, plan=user_services.idPlan).first()
        
            # 1. Validar si ya fue guardado
            if not ComprobanteNomina12.objects.filter(id=obj.id).exists():
                obj.save()

            # 2. Validar si ya fue timbrado
            comprobante_bd = ComprobanteNomina12.objects.get(id=obj.id)
            if comprobante_bd.tipo_documento == 'timbrado':
                self.message_user(request, "Este comprobante ya fue timbrado y no se puede volver a timbrar.", level="warning")
                return redirect("..")

            with transaction.atomic():
                # === 0. Validar que el usuario aún tiene timbres disponibles ===
                conteo = usuario_raiz.get_conteo_timbres_actual()
                
                
                # Solo validar si el plan tiene límite (es decir, mayor a 0)
                if conteo.limite_timbres and conteo.contador_actual >= conteo.limite_timbres:
                    self.message_user(
                        request,
                        f"Has alcanzado el límite de {conteo.limite_timbres} timbres permitidos en tu plan. "
                        "No puedes timbrar más comprobantes en este periodo.",
                        level="error"
                    )
                    return redirect("..")
                
                print("Timbrando comprobante con ID:", obj.id)
                usuario_cfdi = UsersCFDI.objects.get(idUserCFDI=request.user)
                usuario_raiz = usuario_cfdi.get_raiz()
                
                # == Obtén el usuario logueado y su Service_Plan correspondiente al servicio ==
                user_services = usuario_raiz.idUserServicePlan_id
                # Obtén los Service_Plan relacionados con el usuario logueado
                service_plans = Service_Plan.objects.filter(service=user_services.idService, plan=user_services.idPlan).first()

                # 3. Obtener datos CFDI
                comprobante = obtener_datos_comprobante_nomina12(obj.id)
                if comprobante is None:
                    self.message_user(request, "Error: No se pudo obtener el comprobante de nómina.", level="error")
                    return redirect("..")

                xml_content = comprobante.xml_bytes(pretty_print=True, validate=True).decode("utf-8")
                xml_base64 = base64.b64encode(xml_content.encode("utf-8")).decode("utf-8")
                print("XML en Base64 generado correctamente.")

                # 4. Timbrar
                user = usuario_raiz.idUserCFDI.username
                token = usuario_raiz.decrypt_token()
                
                estado = SoapService.stamp('', xml_base64, user, token)
                if hasattr(estado, 'Incidencias') and estado.Incidencias:
                    mensajes = []
                    for incidencia in estado.Incidencias:
                        mensaje = f"⚠️ Error {incidencia.CodigoError}: {incidencia.MensajeIncidencia}"
                        fecha_error = incidencia.FechaRegistro
                        mensajes.append(mensaje)
                    mensaje_completo = "\n".join(mensajes)
                    
                    try:
                        xml_content = xml_content.strip().replace("\x00", "")
                        root = ET.fromstring(xml_content)
                    except Exception as e:
                        self.message_user(request, f"Error al procesar el XML timbrado: {e}", level="error")
                        return redirect("..")

                    # === Detectar namespace de cfdi ===
                    ns_cfdi = root.tag.split("}")[0].strip("{")

                    # === Buscar Receptor ===
                    receptor = root.find(f".//{{{ns_cfdi}}}Receptor")
                    rfc_receptor = receptor.attrib.get("Rfc", "") if receptor is not None else "Desconocido"
                    nombre_receptor = receptor.attrib.get("Nombre", "No encontrado") if receptor is not None else "Desconocido"
                    folio = root.attrib.get("Folio", "")

                    # === Obtener Total del CFDI ===
                    total = root.attrib.get("Total", "0.00")
                    
                    
                    # === REGISTRAR INCIDENCIA COMO COMPROBANTE EMITIDO ===
                    # user_cfdi = UsersCFDI.objects.get(idUserCFDI=request.user)
                    
                    ComprobanteEmitido.objects.create(
                        idUserCFDI=usuario_raiz,
                        comprobante_relacionado=comprobante_bd,
                        fecha=fecha_error,
                        folio=folio or "-",
                        rfc=rfc_receptor,
                        nombre=nombre_receptor,
                        total=total,
                        tipo='Nómina',
                        cod_estatus='Error al timbrar',
                        metodo_pago=root.attrib.get("MetodoPago", "No especificado"),
                        forma_pago=root.attrib.get("FormaPago", "No especificado"),
                        version_cfdi=root.attrib.get("Version", "Desconocida"),
                        detallesError=mensaje
                    )
                    
                    self.message_user(request, f"No se pudo timbrar el comprobante:\n{mensaje_completo}", level="error")
                    return redirect("..")

                # 5. Parsear XML
                try:
                    xml = estado.xml.strip().replace("\x00", "")
                    root = ET.fromstring(xml)
                except Exception as e:
                    self.message_user(request, f"Error al procesar el XML timbrado: {e}", level="error")
                    return redirect("..")

                # 6. Detectar namespaces
                namespaces = {}
                for elem in root.iter():
                    if '}' in elem.tag:
                        ns = elem.tag.split('}')[0].strip('{')
                        if 'cfd/4' in ns:
                            namespaces['cfdi'] = ns
                        elif 'nomina' in ns:
                            namespaces['nomina'] = ns
                        elif 'TimbreFiscalDigital' in ns:
                            namespaces['tfd'] = ns
                namespaces.setdefault('cfdi', 'http://www.sat.gob.mx/cfd/4')

                # 7. Extraer nodos clave
                receptor = root.find(".//cfdi:Receptor", namespaces)
                timbre = root.find(f".//{{{namespaces.get('tfd', '')}}}TimbreFiscalDigital")

                if receptor is None or timbre is None:
                    self.message_user(request, "Error: El XML no contiene los nodos <Receptor> o <TimbreFiscalDigital>.", level="error")
                    return redirect("..")

                # 8. Extraer datos
                uuid = timbre.attrib.get("UUID")
                rfc_receptor = receptor.attrib.get("Rfc", "")
                nombre_receptor = receptor.attrib.get("Nombre", "No encontrado")
                folio = root.attrib.get("Folio", "")
                total = root.attrib.get("Total", "0.00")
                metodo_pago = root.attrib.get("MetodoPago", "No especificado")
                forma_pago = root.attrib.get("FormaPago", "No especificado")
                version_cfdi = root.attrib.get("Version", "Desconocida")
                no_certificado = root.attrib.get("NoCertificado", "")

                # Convertir fecha a objeto timezone-aware
                fecha_original = getattr(estado, 'Fecha', None)
                fecha_convertida = None
                if fecha_original:
                    try:
                        fecha_dt = datetime.strptime(fecha_original, "%Y-%m-%dT%H:%M:%S")
                        fecha_convertida = make_aware(fecha_dt)
                    except ValueError:
                        print("Error al convertir la fecha:", fecha_original)

                # 9. Marcar el comprobante como timbrado
                comprobante_bd.tipo_documento = 'timbrado'
                comprobante_bd.noCertificado = no_certificado
                comprobante_bd.save(update_fields=["tipo_documento", "noCertificado"])

                # 10. Verificar duplicado por UUID
                if ComprobanteEmitido.objects.filter(uuid=uuid).exists():
                    self.message_user(request, "Este comprobante ya fue registrado anteriormente.", level="warning")
                    return redirect("..")

                # 11. Obtener usuario CFDI
                # user_cfdi = UsersCFDI.objects.get(idUserCFDI=request.user)
                nomina = Nomina.objects.filter(comprobanteNomina12=comprobante_bd).first()
                fecha_pago_final = nomina.fecha_pago if nomina and nomina.fecha_pago else fecha_convertida or timezone.now()

                # 12. Guardar en ComprobanteEmitido
                ComprobanteEmitido.objects.create(
                    idUserCFDI=usuario_raiz,
                    comprobante_relacionado=comprobante_bd,
                    fecha=fecha_convertida,
                    folio=folio,
                    uuid=uuid,
                    rfc=rfc_receptor,
                    nombre=nombre_receptor,
                    fecha_pago=fecha_pago_final,
                    total=total,
                    xml_timbrado=estado.xml,
                    tipo='Nómina',
                    cod_estatus=estado.CodEstatus,
                    metodo_pago=metodo_pago,
                    forma_pago=forma_pago,
                    version_cfdi=version_cfdi,
                )
                
                lat = request.POST.get("latitud")
                lon = request.POST.get("longitud")
                ubicacion = f"{lat}, {lon}" if lat and lon else None
                ip = request.META.get("REMOTE_ADDR")

                bitacora, _ = BitacoraCFDI.objects.get_or_create(comprobante=comprobante_bd)
                bitacora.timbrado_por = request.user
                bitacora.fecha_timbrado = now()
                bitacora.ip_timbrado = ip
                bitacora.ubicacion_timbrado = ubicacion
                bitacora.save()

                self.message_user(request, "El comprobante de nómina fue timbrado y registrado exitosamente.")
                return redirect("..")

        except Exception as e:
            print("Error inesperado:", traceback.format_exc())
            self.message_user(request, f"Error inesperado: {e}", level="error")
            return redirect("..")







        # Puedes agregar los otros casos igual
                
   


    


mi_admin_site.register(ComprobanteNomina12, Nomina12Admin)







class ComprobanteCartaPorteTrasladoForm(forms.ModelForm):
    class Meta:
        model = ComprobanteCartaPorteTraslado
        fields = '__all__'
        widgets = {
            'fecha': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control border border-secondary'
            }, format='%Y-%m-%d'),  # <--- Asegúrate de incluir el formato
            'condicionesDePago': forms.Textarea(attrs={
                'class': 'form-control border border-secondary',
                'rows': 2,
                'placeholder': 'Condiciones de pago...'
            }),
            'c_MetodoPago': forms.Select(attrs={'class': 'form-select'}),
            'c_FormaPago': forms.Select(attrs={'class': 'form-select'}),
            'c_Moneda': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)




class Comprobantecartaportetraslado30Admin(admin.ModelAdmin):
    form = ComprobanteCartaPorteTrasladoForm
    raw_id_fields = ['c_MetodoPago', 'c_FormaPago', 'c_Moneda']
    change_form_template = 'LadoClientes/carta porte traslado 30/change_formcartaportetraslado3.0.html'
    change_list_template = 'LadoClientes/forms/change_list.html'
    delete_confirmation_template = 'LadoClientes/forms/delete_confirmation.html'
    delete_selected_confirmation_template = 'LadoClientes/forms/delete_selected_confirmation.html'
    index_template = 'LadoClientes/pages/index.html'

    list_display = ('id','version', 'informacionFiscal', 'serie', 'folio', 'sello', 'c_FormaPago', 'noCertificado')
    list_filter = ('c_Moneda', 'c_FormaPago', 'c_TipoDeComprobante')
    search_fields = ('serie', 'folio', 'informacionFiscal', 'c_TipoDeComprobante', 'c_LugarExpedicion', 'c_MetodoPago', 'c_FormaPago', 'c_Moneda', 'confirmacion')

    inlines = [CartaPorteInline,UbicacionInline,DomicilioInline,MercanciaInline,
               CantidadTransportadaInline, DetalleMercanciaMaritimaInline,PedimentoInline,
               AutotransporteInline,TransporteMaritimoInline,TransporteAereoInline,
               RegimenAduaneroInline,
               TransporteFerroviarioInline, FiguraTransporteInline, ParteTransporteInline,
               GuiaIdentificacionInline,InformacionGlobalInline,EmisorInline,CfdiRelacionadosInline,
               ReceptorInline,ConceptoInline,]


 # inlines = [
    #     TipoComprobanteInline, 
    #     
    #    
    #     
    #      
    #   
    #     ConceptoInline,
    #     #nominaInline, PercepcionInline, DeduccionInline, OtroPagoInline, subcontratacionInline
    # ]


    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(informacionFiscal__idUserCFDI__idUserCFDI=request.user)
    
    def get_changeform_initial_data(self, request):
        return super().get_changeform_initial_data(request)
    
    def response_change(self, request, obj):
        """
        Maneja acciones personalizadas al guardar el modelo.
        """
        if "_facturar_timbrar" in request.POST:
            return self.facturar_y_timbrar(request, obj)
        if "_generar_pdf" in request.POST:
            return self.generar_pdf(request, obj)
        
        if "_save" in request.POST:
            return super().response_change(request, obj)

        if "_save_draft" in request.POST:  # Detectar si se presionó el botón "Guardar borrador". _save_draft es el boton vinculado con la plantilla change_form.html de django admin
            return super().response_change(request, obj)
        
        return super().response_change(request, obj)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if request.method == "POST":

            # 🔹 Si se presionó el botón 'Facturar y Timbrar', redirigir manualmente a `response_change()`
            if "_facturar_timbrar" in request.POST:
                return self.response_change(request, self.get_object(request, object_id))
            
            if "_generar_pdf" in request.POST:
                return self.response_change(request, self.get_object(request, object_id))
            
            if "_save_draft" in request.POST:
                return self.response_change(request, self.get_object(request, object_id))

        return super().change_view(request, object_id, form_url, extra_context)
    
    def save_model(self, request, obj, form, change):
        """
        Guarda el comprobante, asignando automáticamente al usuario logueado y su información fiscal principal.
        """
        if not change:
            # Asignar el usuario (si el modelo Comprobante lo tiene)
            if hasattr(obj, 'user'):
                obj.user = request.user

            # Obtener la información fiscal principal del usuario CFDI relacionado
            try:
                user_cfdi = UsersCFDI.objects.get(idUserCFDI=request.user)
                informacion_principal = InformacionFiscal.objects.filter(
                    idUserCFDI=user_cfdi,
                    es_principal=True
                ).first()

                if informacion_principal:
                    obj.informacionFiscal = informacion_principal
            except UsersCFDI.DoesNotExist:
                pass  # O registrar un mensaje de error si lo necesitas

        super().save_model(request, obj, form, change)
        
    # def save_formset(self, request, form, formset, change):
    #     """
    #     Permite asignar campos automáticos a inlines como Emisor.
    #     """
    #     print("Guardando formset")
    #     instances = formset.save(commit=False)
    #     for instance in instances:
    #         if isinstance(instance, Emisor):
    #             try:
    #                 info_fiscal = form.instance.informacionFiscal
    #                 instance.rfc = info_fiscal.rfc
    #                 instance.nombre = info_fiscal.nombre
    #             except Exception as e:
    #                 print(f"⚠️ Error al asignar RFC/NOMBRE del emisor: {e}")

    #         instance.save()
    #     formset.save_m2m()
                
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}

        if object_id:
            comprobante = Comprobante.objects.select_related('informacionFiscal').filter(pk=object_id).first()
        else:
            comprobante = InformacionFiscal.objects.filter(
                idUserCFDI__idUserCFDI=request.user,
                activo=True,
                es_principal=True
            ).select_related('regimen_fiscal').first()
        extra_context['comprobante_obj'] = comprobante if object_id else None
        extra_context['info_fiscal_obj'] = comprobante.informacionFiscal if object_id and comprobante else comprobante

        return super().changeform_view(request, object_id, form_url, extra_context=extra_context)
    
    #URL PARA HACER LA FUNCION
    def get_urls(self):
                urls = super().get_urls()
                custom_urls = [
                    path(
                    '<pk>/generate-xml/',
                    self.admin_site.admin_view(self.generate_xml),
                    name='myapp_mymodel_generate_xml',
                ),
                    path(
                    '<pk>/generate-pdf/',
                    self.admin_site.admin_view(self.generate_pdff),
                    name='myapp_mymodel_generate_pdff',
                ),
                        
                #     path('get-informacion-fiscal/', self.admin_site.admin_view(self.get_informacion_fiscal), name='get_informacion_fiscal'),
                ]
                return custom_urls + urls

    def generate_xml(self, request, pk):
        print("timbrando", pk)
        comprobante = obtener_datos_factura(pk)
        print("comprobante", comprobante)
        xml_content = comprobante.xml_bytes(pretty_print=True, validate=True).decode("utf-8")

        # Devolver el XML como respuesta HTTP
        response = HttpResponse(xml_content, content_type="application/xml")
        response["Content-Disposition"] = f'attachment; filename="factura_{pk}.xml"'
        return response
    
    def generate_pdff(self, request, pk):
        comprobante = obtener_datos_factura(pk)

         # Generar el PDF utilizando la función `pdf_bytes`
        pdf_content = render_comprobante_pdf_bytes(comprobante)

        # Crear una respuesta HTTP con el PDF
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="factura_{pk}.pdf"'

        return response

    
    def facturar_y_timbrar(self, request, obj):
        """
        Genera un objeto en el modelo ComprobanteEmitido tomando los datos indicados.
        """
        try:
            print(" Timbrando comprobante con ID:", obj.id)
            
            # Obtener datos del CFDI
            comprobante = obtener_datos_factura(obj.id)
            xml_content = comprobante.process()
            xml_content = comprobante.xml_bytes(pretty_print=True, validate=True).decode("utf-8")

            # Convertir XML a Base64
            xml_base64 = base64.b64encode(xml_content.encode("utf-8")).decode("utf-8")
            print("XML en Base64 generado correctamente.")

            # Timbrar XML
            estado = SoapService.stamp('', xml_base64, 'antojitossol13@gmail.com', '1nT36R4c!0N')

            # Verificar si hay incidencias
            if not estado.Incidencias:
                print(' No hay incidencias, timbrado exitoso:', estado.CodEstatus)
            else:
                print('⚠ Advertencia: Incidencias detectadas:', estado.Incidencias[0].MensajeIncidencia)

            # Asegurar que el XML recibido sea válido
            xml = estado.xml
            if not xml:
                print(" Error: No se recibió XML timbrado.")
                return

            try:
                print("XML recibido antes de parsear:", xml[:500])  # Muestra solo los primeros 500 caracteres

                if not xml or xml.strip() == "":
                    print(" Error: XML vacío o nulo.")
                    return
                
                xml = xml.strip().replace("\x00", "")  # Elimina caracteres nulos

                try:
                    root = ET.fromstring(xml)  # Intenta parsear el XML
                except ET.ParseError as e:
                    print(" Error al procesar el XML:", str(e))
                    return

                # Detectar namespaces en el XML
                namespaces = {node.tag.split("}")[0].strip("{"): node.tag.split("}")[0].strip("{") for node in root.iter()}
                print(" Namespaces detectados:", namespaces)

                # Obtener dinámicamente los namespaces
                ns = {
                    'cfdi': list(namespaces.keys())[0],  # CFDI
                    'tfd': list(namespaces.keys())[1]   # Timbre Fiscal Digital
                }

                # Buscar datos
                folio = root.attrib.get("Folio", "")
                total = root.attrib.get("Total", "")
                print(f"Folio: {folio}, Total: {total}")

                # Buscar Receptor y UUID con los namespaces correctos
                # Asegura el namespace correcto manualmente si es necesario
                namespaces.setdefault('cfdi', "http://www.sat.gob.mx/cfd/4")
                receptor = root.find(".//cfdi:Receptor", namespaces)
                if receptor is not None:
                    rfc_receptor = receptor.attrib.get("Rfc", "")
                    nombre_receptor = receptor.attrib.get("Nombre", "No encontrado")
                    print(f"RFC Receptor: {rfc_receptor}")
                    print(f"Nombre del Receptor: {nombre_receptor}")
                else:
                    print("⚠ No se encontró el nodo <cfdi:Receptor>")

                timbre = root.find(f".//{{{ns['tfd']}}}TimbreFiscalDigital")
                if timbre is not None:
                    uuid = timbre.attrib.get("UUID", "")
                    print(f" UUID: {uuid}")
                else:
                    print(" No se encontró el nodo <tfd:TimbreFiscalDigital>")

            except Exception as e:
                print(" Error inesperado:", str(e))
            
            # Extraer el nombre del receptor
            if receptor is not None:
                nombre_receptor = receptor.attrib.get("Nombre", "No encontrado")
                print(f" Nombre del Receptor: {nombre_receptor}")
            else:
                nombre_receptor = "No encontrado"
                print(" No se encontró el nodo <cfdi:Receptor>")

            
            # Validación de datos antes de guardar
            print("Datos que se intentarán guardar en la BD:")
            print(f"Usuario: {request.user}")
            print(f"Fecha: {estado.Fecha}")
            print(f"Folio: {folio}")
            print(f"UUID: {uuid}")
            print(f"RFC Receptor: {rfc_receptor}")
            print(f"Nombre: {nombre_receptor}")
            print(f"Fecha de Pago: {estado.Fecha}")
            print(f"Total: {total}")
            
            # Convertir fecha al formato correcto
            fecha_original = estado.Fecha  # Ejemplo: '2025-03-11T17:25:02'
            try:
                fecha_convertida = datetime.strptime(estado.Fecha, "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d")
            except ValueError:
                fecha_convertida = None  # Manejar el error si el formato no es correcto
                
            print(f"Fecha convertida: {fecha_convertida}")
            
            UserCFDI = UsersCFDI.objects.get(idUserCFDI=request.user)

            # Crear el objeto ComprobanteEmitido
            try:
                comprobante_emitido = ComprobanteEmitido.objects.create(
                    idUserCFDI=UserCFDI,
                    fecha=estado.Fecha,
                    folio=folio,
                    uuid=uuid,
                    rfc=rfc_receptor,
                    nombre=nombre_receptor,
                    fecha_pago=fecha_convertida,
                    total=total,
                    xml_timbrado=estado.xml,
                    tipo='Factura electrónica',
                    cod_estatus=estado.CodEstatus,  # 🔹 Ahora en su propio campo
                    metodo_pago=root.attrib.get("MetodoPago", "No especificado"),
                    forma_pago=root.attrib.get("FormaPago", "No especificado"),
                    version_cfdi=root.attrib.get("Version", "Desconocida"),
                )
                
                print('Comprobante emitido creado:', comprobante_emitido)
            except Exception as e:
                print(' Error al crear ComprobanteEmitido:', str(e))

            self.message_user(request, "El comprobante fue generado exitosamente.")
        except ValidationError as e:
            self.message_user(request, f"Error al generar el comprobante: {e.messages[0]}", level="error")
        except Exception as e:
            self.message_user(request, f"Error inesperado: {str(e)}", level="error")

        return redirect("..")





mi_admin_site.register(ComprobanteCartaPorteTraslado, Comprobantecartaportetraslado30Admin)






class FacturaElectronicaAdmin(nested_admin.NestedModelAdmin):
    form=FacturaElectronicaForm
    change_form_template = 'LadoClientes/forms/change_formFacturas.html'  # Ruta a tu plantilla personalizada
    change_list_template = 'LadoClientes/forms/change_list.html'  # Ruta a tu plantilla personalizada
    delete_confirmation_template = 'LadoClientes/forms/delete_confirmation.html'  # Ruta a tu plantilla personalizada
    delete_selected_confirmation_template = 'LadoClientes/forms/delete_selected_confirmation.html'  # Ruta a tu plantilla personalizada
    index_template = 'LadoClientes/pages/index.html'
    # list_display = ('nombre', 'rfc', 'activo', 'fecha_creacion', 'get_tipos_comprobantes_detallados', 'informacion_fiscal', 'regimen_fiscal')
    # list_filter = ('activo', 'regimen_fiscal', 'fecha_creacion')
    search_fields = ('nombre', 'rfc', 'informacion_fiscal__rfc', 'informacion_fiscal__razon_social')
    # ordering = ['nombre', 'fecha_creacion']
    readonly_fields = ('fecha_creacion',)

    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'rfc', 'descripcion', 'codigo_postal', 'activo', 'fecha_creacion', 'informacion_fiscal', 'regimen_fiscal')
        }),
    )

    # inlines = [
    # TipoComprobanteInline, InformacionGlobalInline, InformacionPagoInline,
    # ComprobantesRelacionadosInline,EmisorInline,  
    # LeyendasFiscalesInline,ConceptoInline, ReceptorInline
    # ]

    class Media:
     css = {
            'all': ('assets/css/forms.css',)  # Asegura que se cargue el CSS personalizado
     }


    #agrega un get_queryset para filtrar por usuario que este logueado

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
            if db_field.name == "informacion_fiscal":
                # Filtrar usando el campo correcto `user` en lugar de `usuario`
                kwargs["queryset"] = InformacionFiscal.objects.filter(user=request.user)
            return super().formfield_for_foreignkey(db_field, request, **kwargs)



    def get_informacion_fiscal(self, request):
        info_fiscal_id = request.GET.get('info_fiscal_id')
        if info_fiscal_id:
            try:
                info_fiscal = InformacionFiscal.objects.get(pk=info_fiscal_id)
                data = {
                    "nombre": info_fiscal.nombre,
                    "rfc": info_fiscal.rfc,
                    "descripcion": f"{info_fiscal.calle} {info_fiscal.numero_exterior}, {info_fiscal.colonia}, {info_fiscal.ciudad}",
                    "codigo_postal": info_fiscal.codigo_postal,
                    "activo": info_fiscal.activo,
                    "regimen_fiscal": info_fiscal.regimen_fiscal.first().id if info_fiscal.regimen_fiscal.exists() else "",
                }
                return JsonResponse(data)
            except InformacionFiscal.DoesNotExist:
                return JsonResponse({"error": "Información fiscal no encontrada"}, status=404)
        return JsonResponse({"error": "ID no proporcionado"}, status=400)






    # Métodos personalizados
    def get_tipos_comprobantes_detallados(self, obj):
        """
        Devuelve detalles completos de los tipos de comprobantes asociados al negocio.
        """
        if obj.tipos_comprobantes.exists():
            detalles = [
                f"<strong>{tipo.descripcion}</strong> (Clave: {tipo.c_TipoDeComprobante}, "
                f"Valor Máximo: {tipo.valor_maximo}, "
                f"Vigencia: {tipo.fecha_inicio_vigencia} - {tipo.fecha_fin_vigencia or 'Indefinido'})"
                for tipo in obj.tipos_comprobantes.all()
            ]
            return format_html("<br>".join(detalles))
        return "No hay tipos de comprobantes asociados"
    get_tipos_comprobantes_detallados.short_description = "Tipos de Comprobantes Detallados"

    def save_model(self, request, obj, form, change):
        """
        Guarda el modelo asegurándose de que la información esté relacionada correctamente.
        """
   

        # Asignar el usuario logueado si es una nueva factura
        if not change:
            obj.user = request.user  # Asigna el usuario que está creando la factura

            informacion_principal = InformacionFiscal.objects.filter(es_principal=True).first()
            if informacion_principal:
                obj.nombre = informacion_principal.nombre
                obj.informacion_fiscal = informacion_principal

        super().save_model(request, obj, form, change)

    def facturar_y_timbrar(self, request, obj):
        """
        Genera un objeto en el modelo ComprobanteEmitido tomando los datos indicados.
        """
        try:
            print(" Timbrando comprobante con ID:", obj.id)
            
            # Obtener datos del CFDI
            comprobante = obtener_datos_factura(obj.id)
            xml_content = comprobante.process()
            xml_content = comprobante.xml_bytes(pretty_print=True, validate=True).decode("utf-8")

            # Convertir XML a Base64
            xml_base64 = base64.b64encode(xml_content.encode("utf-8")).decode("utf-8")
            print("XML en Base64 generado correctamente.")

            # Timbrar XML
            estado = SoapService.stamp('', xml_base64, 'antojitossol13@gmail.com', '1nT36R4c!0N')

            # Verificar si hay incidencias
            if not estado.Incidencias:
                print(' No hay incidencias, timbrado exitoso:', estado.CodEstatus)
            else:
                print('⚠ Advertencia: Incidencias detectadas:', estado.Incidencias[0].MensajeIncidencia)

            # Asegurar que el XML recibido sea válido
            xml = estado.xml
            if not xml:
                print(" Error: No se recibió XML timbrado.")
                return

            try:
                print("XML recibido antes de parsear:", xml[:500])  # Muestra solo los primeros 500 caracteres

                if not xml or xml.strip() == "":
                    print(" Error: XML vacío o nulo.")
                    return
                
                xml = xml.strip().replace("\x00", "")  # Elimina caracteres nulos

                try:
                    root = ET.fromstring(xml)  # Intenta parsear el XML
                except ET.ParseError as e:
                    print(" Error al procesar el XML:", str(e))
                    return

                # Detectar namespaces en el XML
                namespaces = {node.tag.split("}")[0].strip("{"): node.tag.split("}")[0].strip("{") for node in root.iter()}
                print(" Namespaces detectados:", namespaces)

                # Obtener dinámicamente los namespaces
                ns = {
                    'cfdi': list(namespaces.keys())[0],  # CFDI
                    'tfd': list(namespaces.keys())[1]   # Timbre Fiscal Digital
                }

                # Buscar datos
                folio = root.attrib.get("Folio", "")
                total = root.attrib.get("Total", "")
                print(f"Folio: {folio}, Total: {total}")

                # Buscar Receptor y UUID con los namespaces correctos
                receptor = root.find(f".//{{{ns['cfdi']}}}Receptor")
                if receptor is not None:
                    rfc_receptor = receptor.attrib.get("Rfc", "")
                    print(f"RFC Receptor: {rfc_receptor}")
                else:
                    print(" No se encontró el nodo <cfdi:Receptor>")

                timbre = root.find(f".//{{{ns['tfd']}}}TimbreFiscalDigital")
                if timbre is not None:
                    uuid = timbre.attrib.get("UUID", "")
                    print(f" UUID: {uuid}")
                else:
                    print(" No se encontró el nodo <tfd:TimbreFiscalDigital>")

            except Exception as e:
                print(" Error inesperado:", str(e))
            
            # Extraer el nombre del receptor
            if receptor is not None:
                nombre_receptor = receptor.attrib.get("Nombre", "No encontrado")
                print(f" Nombre del Receptor: {nombre_receptor}")
            else:
                nombre_receptor = "No encontrado"
                print(" No se encontró el nodo <cfdi:Receptor>")

            
            # Validación de datos antes de guardar
            print("Datos que se intentarán guardar en la BD:")
            print(f"Usuario: {request.user}")
            print(f"Fecha: {estado.Fecha}")
            print(f"Folio: {folio}")
            print(f"UUID: {uuid}")
            print(f"RFC Receptor: {rfc_receptor}")
            print(f"Nombre: {nombre_receptor}")
            print(f"Fecha de Pago: {estado.Fecha}")
            print(f"Total: {total}")
            
            # Convertir fecha al formato correcto
            fecha_original = estado.Fecha  # Ejemplo: '2025-03-11T17:25:02'
            try:
                fecha_convertida = datetime.strptime(estado.Fecha, "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d")
            except ValueError:
                fecha_convertida = None  # Manejar el error si el formato no es correcto
                
            print(f"Fecha convertida: {fecha_convertida}")

            # Crear el objeto ComprobanteEmitido
            try:
                comprobante_emitido = ComprobanteEmitido.objects.create(
                    user=request.user,
                    fecha=estado.Fecha,
                    folio=folio,
                    uuid=uuid,
                    rfc=rfc_receptor,
                    nombre=nombre_receptor,
                    fecha_pago=fecha_convertida,
                    total=total,
                    xml_timbrado=estado.xml,
                    tipo='Factura electrónica',
                    cod_estatus=estado.CodEstatus,  # 🔹 Ahora en su propio campo
                    metodo_pago=root.attrib.get("MetodoPago", "No especificado"),
                    forma_pago=root.attrib.get("FormaPago", "No especificado"),
                    version_cfdi=root.attrib.get("Version", "Desconocida"),
                )
                
                print('Comprobante emitido creado:', comprobante_emitido)
            except Exception as e:
                print(' Error al crear ComprobanteEmitido:', str(e))

            self.message_user(request, "El comprobante fue generado exitosamente.")
        except ValidationError as e:
            self.message_user(request, f"Error al generar el comprobante: {e.messages[0]}", level="error")
        except Exception as e:
            self.message_user(request, f"Error inesperado: {str(e)}", level="error")

        return redirect("..")





    def generar_pdf(self, request, obj):
        """
        Genera un PDF con formato mejorado para FacturaElectronica.
        """
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Factura_{obj.id}.pdf"'

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
        p.drawString(150, 755, f"Recibo de Honorarios: {obj.nombre}")
        p.drawString(150, 740, f"RFC: {obj.rfc}")
        p.drawString(150, 725, f"Fecha de Creación: {obj.fecha_creacion.strftime('%Y-%m-%d')}")

    # Información General
        p.setFillColor(section_color)
        p.rect(40, 700, 520, 20, fill=1, stroke=0)
        p.setFillColor(colors.black)
        p.setFont("Helvetica-Bold", 10)
        p.drawString(50, 707, "Información General")
        p.setFont("Helvetica", 9)
        p.setFillColor(text_color)
        p.drawString(50, 690, f"Descripción: {obj.descripcion}")
        p.drawString(50, 675, f"Código Postal: {obj.codigo_postal}")
        p.drawString(50, 660, f"Régimen Fiscal: {obj.regimen_fiscal}")

    # Sección de Conceptos
        p.setFillColor(section_color)
        p.rect(40, 630, 520, 20, fill=1, stroke=0)
        p.setFillColor(colors.black)
        p.setFont("Helvetica-Bold", 10)
        p.drawString(50, 637, "Detalles de Conceptos")
        p.setFont("Helvetica", 9)
        y_position = 620
        for concepto in obj.Conceptos.all():
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

        for receptor in obj.receptores.all():
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
        p.drawString(410, y_position - 3, f"TOTAL: ${sum(concepto.importe for concepto in obj.Conceptos.all()):.2f}")

    # Finalizar PDF
        p.showPage()
        p.save()

        return response


    def response_change(self, request, obj):
        """
        Maneja acciones personalizadas al guardar el modelo.
        """
        if "_facturar_timbrar" in request.POST:
            return self.facturar_y_timbrar(request, obj)
        if "_generar_pdf" in request.POST:
            return self.generar_pdf(request, obj)
        
        if "_save" in request.POST:
            return super().response_change(request, obj)

        if "_save_draft" in request.POST:  # Detectar si se presionó el botón "Guardar borrador". _save_draft es el boton vinculado con la plantilla change_form.html de django admin




            # Verificar si ya existe un borrador para este objeto
            borrador, created = FacturaElectronicaBorrador.objects.get_or_create(
                informacion_fiscal=obj.informacion_fiscal,
                defaults={
                    'nombre': obj.nombre,
                    'rfc': obj.rfc,
                    'descripcion': obj.descripcion,
                    'codigo_postal': obj.codigo_postal,
                    'activo': False,  # El borrador no está activo por defecto
                    'regimen_fiscal': obj.regimen_fiscal,
                    'fecha_creacion': None,  # Fecha en blanco para el borrador
                }
            )

            if not created:  # Si ya existía un borrador, actualízalo
                borrador.nombre = obj.nombre
                borrador.rfc = obj.rfc
                borrador.descripcion = obj.descripcion
                borrador.codigo_postal = obj.codigo_postal
                borrador.regimen_fiscal = obj.regimen_fiscal
                borrador.save()

            # Copiar relación de tipos_comprobantes al borrador ubicando el related_name correcto para esa relacion en el moodelo FacturaElectronicaBorrador siendo este tipos_comprobantes_Borrador
            borrador.tipos_comprobantes_Borrador.all().delete()  # Limpiar relaciones previas
            # Recorremos todos los tipos de comprobantes asociados al objeto original ubicandolo por su related_name "tipos_comprobantes" y los creamos en el borrador
            for tipo in obj.tipos_comprobantes.all():
                TipoComprobante.objects.create(
                    FacturaElectronicaBorrador=borrador,
                    descripcion=tipo.descripcion,
                    c_TipoDeComprobante=tipo.c_TipoDeComprobante,
                    valor_maximo=tipo.valor_maximo,
                    fecha_inicio_vigencia=tipo.fecha_inicio_vigencia,
                    fecha_fin_vigencia=tipo.fecha_fin_vigencia,
                )

               # Copiar relación de tipos_comprobantes al borrador ubicando el related_name correcto para esa relacion en el moodelo FacturaElectronicaBorrador siendo este ConceptosBorrador
            borrador.ConceptosBorrador.all().delete()  # Limpiar conceptos previos

            # Recorremos todos los tipos de comprobantes asociados al objeto original ubicandolo por su related_name "conceptos" y los creamos en el borrador
            for concepto in obj.Conceptos.all():
                borrador.ConceptosBorrador.create(
                    descripcion=concepto.descripcion,
                    cantidad=concepto.cantidad,
                    valor_unitario=concepto.valor_unitario,
                    importe=concepto.importe,
                    objetoimpuesto = concepto.objetoimpuesto,
                    identificador = concepto.identificador,
                    unidad = concepto.unidad,
                    impuesto = concepto.impuesto,
                    claveprodserv = concepto.claveprodserv,
                    clave_producto = concepto.clave_producto,
                    identificacion_sat = concepto.identificacion_sat,
                    clave_unidad = concepto.clave_unidad,
                    nombre_unidad_sat = concepto.nombre_unidad_sat,
                    notas = concepto.notas,
                    total = concepto.total,



                )

            borrador.informacion_global_Borrador.all().delete()  # Limpiar conceptos previos
            for informacionglobal in obj.Informacion_global.all():  # Usar el related_name correcto
                borrador.informacion_global_Borrador.create(
                Escomprobantelegal = informacionglobal.Escomprobantelegal,
                Periodicidad = informacionglobal.Periodicidad,
                Meses = informacionglobal.Meses,
                Anio = informacionglobal.Anio,
                )

            borrador.InformacionPagoBorrador.all().delete()  # Limpiar conceptos previos
            for informacion_pago in obj.InformacionPago.all():  # Usar el related_name correcto
                borrador.InformacionPagoBorrador.create(
                Metodopago = informacion_pago.Metodopago,
                Formapago =  informacion_pago.Formapago,
                Fechapago =  informacion_pago.Fechapago,
                Moneda =  informacion_pago.Moneda,
                Tipocambio =  informacion_pago.Tipocambio,
                Condicionespago =  informacion_pago.Condicionespago,
                )

            borrador.Emisor_Borrador.all().delete()
            for emisor in obj.Emisor.all():
                borrador.Emisor_Borrador.create(
                regimen_fiscal = emisor.regimen_fiscal,
                Factura_adquiriente = emisor.Factura_adquiriente,
                pdf = emisor.pdf,

                )


            #'FacturaElectronica' object has no attribute 'ComprobanteRelacionados'
            borrador.Comprobante_relacionados_Borrador.all().delete()  # Limpiar conceptos previos
            for comprobanterelacionados in obj.Comprobante_relacionados.all():
                borrador.Comprobante_relacionados_Borrador.create(
                Tiporelacion = comprobanterelacionados.Tiporelacion,
                uuid = comprobanterelacionados.uuid,
                )

            borrador.receptores_borrador.all().delete()
            for receptors in obj.receptores.all():
                borrador.receptores_borrador.create(

                   Usocfdi = receptors.Usocfdi,
                   Ignorar_validacion_sociedad = receptors.Ignorar_validacion_sociedad,
                   Mostrardireccionpdf = receptors.Mostrardireccionpdf,
                   Rfc = receptors.Rfc,
                   Razon_social = receptors.Razon_social,
                   Registrotributario = receptors.Registrotributario,
                   Nombre = receptors.Nombre,
                   Apellido_paterno = receptors.Apellido_paterno,
                   Apellido_materno = receptors.Apellido_materno,
                   Telefono = receptors.Telefono,
                   Correo_electronico = receptors.Correo_electronico,
                   Calle = receptors.Calle,
                   Numero_exterior = receptors.Numero_exterior,
                   Numero_interior = receptors.Numero_interior,
                   Colonia = receptors.Colonia,
                   Ciudad = receptors.Ciudad,
                   Municipio = receptors.Municipio,
                   Estado = receptors.Estado,
                   Pais = receptors.Pais,
                   Codigo_postal = receptors.Codigo_postal,
                   Referencia = receptors.Referencia,
                   Clave_pais = receptors.Clave_pais,
                   Residencia_fiscal = receptors.Residencia_fiscal,
                )

            borrador.LeyendasFiscalesBorrador.all().delete()
            for leyendas_fiscales in obj.LeyendasFiscales.all():
                borrador.LeyendasFiscalesBorrador.create(
                    TextoLeyenda = leyendas_fiscales.TextoLeyenda,
                    Disposicionfiscal = leyendas_fiscales.Disposicionfiscal,
                    Norma = leyendas_fiscales.Norma,
                    )

            if not created:  # Si ya existía un borrador, actualízalo
                borrador.nombre = obj.nombre
                borrador.rfc = obj.rfc
                borrador.descripcion = obj.descripcion
                borrador.codigo_postal = obj.codigo_postal
                borrador.regimen_fiscal = obj.regimen_fiscal
                borrador.save()
                self.message_user(request, "El borrador se actualizó correctamente.")

            else:
                self.message_user(request, "El borrador de la factura se guardó correctamente.")
            return redirect("..")  # Regresa al listado de objetos

        return super().response_change(request, obj)

    def change_view(self, request, object_id, form_url='', extra_context=None):

        if request.method == "POST":

            # 🔹 Si se presionó el botón 'Facturar y Timbrar', redirigir manualmente a `response_change()`
            if "_facturar_timbrar" in request.POST:
                return self.response_change(request, self.get_object(request, object_id))
            
            if "_generar_pdf" in request.POST:
                return self.response_change(request, self.get_object(request, object_id))
            
            if "_save_draft" in request.POST:
                return self.response_change(request, self.get_object(request, object_id))

        return super().change_view(request, object_id, form_url, extra_context)


    #URL PARA HACER LA FUNCION
    def get_urls(self):
                urls = super().get_urls()
                custom_urls = [
                    path(
                    '<pk>/generate-xml/',
                    self.admin_site.admin_view(self.generate_xml),
                    name='myapp_mymodel_generate_xml',
                ),
                    path(
                    '<pk>/generate-pdf/',
                    self.admin_site.admin_view(self.generate_custom_pdf),
                    name='myapp_mymodel_generate_pdf',
                ),
                        
                    path('get-informacion-fiscal/', self.admin_site.admin_view(self.get_informacion_fiscal), name='get_informacion_fiscal'),
                ]
                return custom_urls + urls

    def generate_xml(self, request, pk):
        print("timbrando", pk)
        comprobante = obtener_datos_factura(pk)
        xml_content = comprobante.xml_bytes(pretty_print=True, validate=True).decode("utf-8")

        # Devolver el XML como respuesta HTTP
        response = HttpResponse(xml_content, content_type="application/xml")
        response["Content-Disposition"] = f'attachment; filename="factura_{pk}.xml"'
        return response
    
    def generate_pdf(self, request, pk):
        comprobante = obtener_datos_factura(pk)

        # Generar el PDF utilizando la función `pdf_bytes`
        pdf_content = render_comprobante_pdf_bytes(comprobante)

        # Crear una respuesta HTTP con el PDF
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="factura_{pk}.pdf"'

        return response
    
    def generate_custom_pdf(self, request, pk):
        # Obtener la factura
        factura = self.get_object(request, pk)
        if not factura:
            self.message_user(request, "Factura no encontrada.", level="error")
            return redirect("..")

        # Obtener el receptor asociado
        receptor_model = factura.receptores.first()  # Usar el primer receptor asociado
        if not receptor_model:
            self.message_user(request, "No se encontró un receptor asociado a la factura.", level="error")
            return redirect("..")

        # Obtener el receptor asociado
        formaPago_model = factura.InformacionPago.first()  # Usar el primer receptor asociado
        if not receptor_model:
            self.message_user(request, "No se encontró un receptor asociado a la factura.", level="error")
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
            password=certificado.get_plain_password(),
        )

        # Crear objeto Emisor
        emisor = cfdi40.Emisor(
            rfc=signer.rfc,
            nombre=signer.legal_name,
            regimen_fiscal=informacion_fiscal.regimen_receptor.c_RegimenFiscal,
        )


        # Crear los conceptos
        conceptos = []
        for concepto_model in factura.Conceptos.all():
            print('clave unidad',concepto_model.clave_unidad)
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

        print('forma de pago',formaPago_model.Metodopago.c_MetodoPago)
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
        # comprobante.sign(signer)
        # comprobante=comprobante.process() # Timbrar el comprobante

        # # Generar el PDF utilizando la función `pdf_bytes`
        # pdf_content = pdf_write(comprobante)

        # # Crear una respuesta HTTP con el PDF
        # response = HttpResponse(pdf_content, content_type='application/pdf')
        # response['Content-Disposition'] = f'attachment; filename="factura_{pk}.pdf"'

        # return response
        
        comprobante = comprobante.process()  # Timbrar el comprobante

        # Generar el HTML base desde el CFDI
        html_content = render.html_str(comprobante)
        bootstrap_css = """
        @import url('https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css');
        """

        # Modificar el HTML antes de convertirlo en PDF (agregar estilos, logotipos, etc.)
        custom_html = f"""
        <html>
        <head>
            <style>
            {bootstrap_css}
                body {{
                    font-family: Arial, sans-serif;
                    font-size: 12px;
                }}
                .header {{
                    text-align: center;
                    font-size: 18px;
                    font-weight: bold;
                }}
                .invoice-details {{
                    margin-top: 20px;
                    border: 1px solid #000;
                    padding: 10px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 10px;
                }}
                th, td {{
                    border: 1px solid black;
                    padding: 5px;
                    text-align: left;
                }}
            </style>
        </head>
        <body>
            <div class="header">Factura CFDI</div>
            <div class="invoice-details">
                <p><strong>RFC Emisor:</strong> {emisor['Rfc']}</p>
                <p><strong>Nombre Emisor:</strong> {emisor['Nombre']}</p>
                <p><strong>RFC Receptor:</strong> {receptor['Rfc']}</p>
                <p><strong>Nombre Receptor:</strong> {receptor['Nombre']}</p>
            </div>
            <div class="card" style="width: 18rem;">
            <img src="..." class="card-img-top" alt="...">
            <div class="card-body">
                <h5 class="card-title">No hay plantillas</h5>
                <p class="card-text">No hay plantillas para editar</p>
                <a href="" class="btn btn-primary stretched-link">Crear</a>
            </div>
            </div>
        </body>
        </html>
        """

        # Convertir el HTML modificado en un PDF con WeasyPrint
        pdf_content = HTML(string=custom_html).write_pdf()

        # Crear una respuesta HTTP con el PDF
        response = HttpResponse(pdf_content, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="factura_{pk}.pdf"'

        return response    
    
    def clean(self):
        """
        Validaciones adicionales al guardar la instancia.
        """
        super().clean()
        for inline in self.inlines:
            if inline.__class__ == ConceptoInline:
                for form in inline.forms:
                    cantidad = form.cleaned_data.get('cantidad')
                    valor_unitario = form.cleaned_data.get('valor_unitario')
                    importe = form.cleaned_data.get('importe')
                    total = form.cleaned_data.get('total')

                    if cantidad and valor_unitario and importe:
                        if importe != cantidad * valor_unitario:
                            raise ValidationError("El importe debe ser igual a la cantidad multiplicada por el valor unitario.")
                    if total and importe and total < importe:
                        raise ValidationError("El total no puede ser menor que el importe.")












mi_admin_site.register(FacturaElectronica, FacturaElectronicaAdmin)









#############################borrador


class FacturaElectronicaBorradorAdmin(ModelAdmin):
   # form = FacturaElectronicaForm
    change_form_template = 'LadoClientes/forms/change_formFacturas.html'
    change_list_template = 'LadoClientes/forms/change_list.html'
    delete_confirmation_template = 'LadoClientes/forms/delete_confirmation.html'
    delete_selected_confirmation_template = 'LadoClientes/forms/delete_selected_confirmation.html'
    index_template = 'LadoClientes/pages/index.html'
    # list_display = ('nombre', 'rfc', 'activo', 'fecha_creacion', 'get_tipos_comprobantes_detallados', 'informacion_fiscal', 'regimen_fiscal')
    # list_filter = ('activo', 'regimen_fiscal', 'fecha_creacion')
    search_fields = ('nombre', 'rfc', 'informacion_fiscal__rfc', 'informacion_fiscal__razon_social')
    # ordering = ['nombre', 'fecha_creacion']
    readonly_fields = ('fecha_creacion',)

    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'rfc', 'descripcion', 'codigo_postal', 'activo', 'fecha_creacion', 'informacion_fiscal', 'regimen_fiscal')
        }),
    )
    
    # inlines = [
    #     TipoComprobanteInline, InformacionGlobalInline, InformacionPagoInline,
    #     ComprobantesRelacionadosInline, EmisorInline, LeyendasFiscalesInline, 
    #     ConceptoInline, ReceptorInline,
    # ]

    class Media:
        css = {
            'all': ('assets/css/forms.css',)
        }

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(user=request.user)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "informacion_fiscal":
            kwargs["queryset"] = InformacionFiscal.objects.filter(user=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_informacion_fiscal(self, request):
        info_fiscal_id = request.GET.get('info_fiscal_id')
        if info_fiscal_id:
            try:
                info_fiscal = InformacionFiscal.objects.get(pk=info_fiscal_id, user=request.user)
                data = {
                    "nombre": info_fiscal.nombre,
                    "rfc": info_fiscal.rfc,
                    "descripcion": f"{info_fiscal.calle} {info_fiscal.numero_exterior}, {info_fiscal.colonia}, {info_fiscal.ciudad}",
                    "codigo_postal": info_fiscal.codigo_postal,
                    "activo": info_fiscal.activo,
                    "regimen_fiscal": info_fiscal.regimen_fiscal.first().id if info_fiscal.regimen_fiscal.exists() else "",
                }
                return JsonResponse(data)
            except InformacionFiscal.DoesNotExist:
                return JsonResponse({"error": "Información fiscal no encontrada"}, status=404)
        return JsonResponse({"error": "ID no proporcionado"}, status=400)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('get-informacion-fiscal/', self.admin_site.admin_view(self.get_informacion_fiscal), name='get_informacion_fiscal'),
        ]
        return custom_urls + urls

    def get_tipos_comprobantes_detallados(self, obj):
        if hasattr(obj, 'tipos_comprobantes') and obj.tipos_comprobantes.exists():
            detalles = [
                f"<strong>{tipo.descripcion}</strong> (Clave: {tipo.c_TipoDeComprobante}, Valor Máximo: {tipo.valor_maximo}, Vigencia: {tipo.fecha_inicio_vigencia} - {tipo.fecha_fin_vigencia or 'Indefinido'})"
                for tipo in obj.tipos_comprobantes.all()
            ]
            return format_html("<br>".join(detalles))
        return "No hay tipos de comprobantes asociados"
    get_tipos_comprobantes_detallados.short_description = "Tipos de Comprobantes Detallados"

    def save_model(self, request, obj, form, change):
        if "_continue" in request.POST:
            obj.activo = False
            obj.fecha_creacion = None

        if not obj.rfc or len(obj.rfc) not in [12, 13]:
            raise ValidationError("El RFC debe tener 12 caracteres para personas morales y 13 para personas físicas.")
        if not obj.codigo_postal:
            raise ValidationError("El código postal es obligatorio.")
        if not obj.regimen_fiscal:
            raise ValidationError("El régimen fiscal es obligatorio.")

        if not change:
            informacion_principal = InformacionFiscal.objects.filter(es_principal=True).first()
            if informacion_principal:
                obj.nombre = informacion_principal.nombre
                obj.informacion_fiscal = informacion_principal

        super().save_model(request, obj, form, change)

    def clean(self):
        super().clean()
        for inline in self.inlines:
            if inline.__class__ == ConceptoInline:
                for form in inline.forms:
                    cantidad = form.cleaned_data.get('cantidad')
                    valor_unitario = form.cleaned_data.get('valor_unitario')
                    importe = form.cleaned_data.get('importe')
                    total = form.cleaned_data.get('total')

                    if cantidad and valor_unitario and importe:
                        if importe != cantidad * valor_unitario:
                            raise ValidationError("El importe debe ser igual a la cantidad multiplicada por el valor unitario.")
                    if total and importe and total < importe:
                        raise ValidationError("El total no puede ser menor que el importe.")

mi_admin_site.register(FacturaElectronicaBorrador, FacturaElectronicaBorradorAdmin)



class CertificadoSelloDigitalAdmin(ModelAdmin):
    change_form_template = 'LadoClientes/forms/change_form_base.html'  # Ruta a tu plantilla personalizada
    change_list_template = 'negocios/certificados_list.html'  # Ruta a tu plantilla personalizada
    delete_confirmation_template = 'LadoClientes/forms/delete_confirmation.html'  # Ruta a tu plantilla personalizada
    delete_selected_confirmation_template = 'LadoClientes/forms/delete_selected_confirmation.html'  # Ruta a tu plantilla personalizada
    index_template = 'LadoClientes/pages/index.html'
    # list_display = ('nombre_certificado', 'archivo_certificado_preview', 'clave_privada_preview', 'user')
    # search_fields = ('nombre_certificado', 'user__username')
    readonly_fields = ('user',)
    fieldsets = (
        ('Información del Certificado', {
            'fields': ('nombre_certificado', 'archivo_certificado', 'clave_privada', 'contrasena')
        }),
    )

    def archivo_certificado_preview(self, obj):
        if obj.archivo_certificado:
            return format_html('<a href="{}" download>{}</a>', obj.archivo_certificado.url, "Descargar .cer")
        return "No disponible"
    archivo_certificado_preview.short_description = "Certificado (*.cer)"

    def clave_privada_preview(self, obj):
        if obj.clave_privada:
            return format_html('<a href="{}" download>{}</a>', obj.clave_privada.url, "Descargar .key")
        return "No disponible"
    clave_privada_preview.short_description = "Clave privada (*.key)"

    def save_model(self, request, obj, form, change):
        errors = {}
        es_nuevo = not change
        
        if not change:  # Solo asignar el usuario al crear un nuevo objeto
            user_cfdi = UsersCFDI.objects.get(idUserCFDI=request.user)
            usuario_raiz = user_cfdi.get_raiz()
            # informacion_fiscal = InformacionFiscal.objects.filter(idUserCFDI=usuario_raiz, activo=True)
            # negocio = informacion_fiscal.filter(es_principal=True).first()
            negocio = obtener_negocio_activo_para(request)
        
            obj.user = usuario_raiz.idUserCFDI
            obj.informacionFiscal = negocio  # Asigna la información fiscal principal del usuario
        
        try:
            obj.archivo_certificado.open('rb')
            obj.clave_privada.open('rb')
            cer_data = obj.archivo_certificado.read()
            key_data = obj.clave_privada.read()
            plain_password = obj.get_plain_password() if obj else None
            passphrase = plain_password.encode() if plain_password else None

            try:
                cert = x509.load_pem_x509_certificate(cer_data, default_backend())
                certt = crypto.load_certificate(crypto.FILETYPE_PEM, cer_data)
            except ValueError:
                cert = x509.load_der_x509_certificate(cer_data, default_backend())
                certt = crypto.load_certificate(crypto.FILETYPE_ASN1, cer_data)

            try:
                private_key = load_pem_private_key(key_data, password=passphrase, backend=default_backend())
            except ValueError:
                private_key = load_der_private_key(key_data, password=passphrase, backend=default_backend())

            # Número de certificado en ASCII
            hex_string = format(cert.serial_number, 'x')
            if len(hex_string) % 2:
                hex_string = '0' + hex_string
            numero_certificado = bytes.fromhex(hex_string).decode('ascii')

            # Vigencia
            not_after = dt.strptime(certt.get_notAfter().decode('ascii'),"%Y%m%d%H%M%SZ").replace(tzinfo=py_timezone.utc)

            # Descripción (Common Name)
            descripcion = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value

            # Sucursal (Organizational Unit)
            sucursal = cert.subject.get_attributes_for_oid(NameOID.ORGANIZATIONAL_UNIT_NAME)[0].value

            # Tipo (FIEL o CSD)
            tipo = "CSD"

            # Asignar
            obj.numero_certificado = numero_certificado
            obj.vigencia = not_after
            obj.descripcion = descripcion
            obj.sucursal = sucursal
            obj.defecto=True
            obj.tipo = tipo
            obj.notas = "El CSD se utiliza únicamente para timbrar comprobantes fiscales digitales (CFDI)."

        except Exception as e:
            self.message_user(request, f"Error al procesar el certificado: {str(e)}", level='error')
            
        with transaction.atomic():
            if obj.defecto:
                modelo = obj.__class__
                modelo.objects.filter(
                    informacionFiscal=obj.informacionFiscal,
                    defecto=True
                ).exclude(pk=obj.pk).update(defecto=False)

        super().save_model(request, obj, form, change)   
        
        if es_nuevo or ('archivo_certificado' in form.changed_data or 'clave_privada' in form.changed_data):
            self.activar_en_pac(obj, request)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        
        if request.user.is_superuser:
            return qs
        
        user_cfdi = UsersCFDI.objects.get(idUserCFDI=request.user)
        usuario_raiz = user_cfdi.get_raiz()
        informacion_fiscal = InformacionFiscal.objects.filter(idUserCFDI=usuario_raiz, activo=True)
        negocio = informacion_fiscal.filter(es_principal=True).first()
        negocio_activo = obtener_negocio_activo_para(request)
        
        return qs.filter(user=usuario_raiz.idUserCFDI, informacionFiscal=negocio_activo)  # Filtra por el usuario logueado
    
    def activar_en_pac(self, obj, request):

        try:
            user_cfdi = UsersCFDI.objects.get(idUserCFDI=request.user)
            usuario_raiz = user_cfdi.get_raiz()
            user_services = usuario_raiz.idUserServicePlan_id
            service_plan  = user_services.idServicePlan
            
            # Descargar .cer y .key como base64
            # Obtener datos CSD
            # cer_data = obj.archivo_certificado.read()
            # key_data = obj.clave_privada.read()
            # passphrase = obj.decrypt_password()

            # cer_b64 = base64.b64encode(cer_data).decode()
            # key_b64 = base64.b64encode(key_data).decode()
            
            rfc = obj.informacionFiscal.rfc
            
            ctx = ''
            key_base64 = ''
            cer_base64 = ''
            passh = ''

            #Llamada SOAP
            response = RegisterService.edit(
                ctx,
                service_plan.supplierStamp.user,
                service_plan.supplierStamp.decrypt_password(),
                rfc,
                'A',
                key_base64,
                cer_base64,
                passh
            )
            
            print("Registrando en PAC...")
            print("RFC:", rfc)
            
            print(f"Respuesta PAC: {response}")

            if response.success:
                messages.success(request, f"Usuario registrado en PAC: {response.message}")
            else:
                messages.error(request, f"Error PAC: {response.message}")

        except Exception as exc:
            messages.error(request, f"Error al registrar en PAC: {exc}")


# Registra el modelo con tu instancia personalizada de admin site
mi_admin_site.register(CertificadoSelloDigital, CertificadoSelloDigitalAdmin)

############################################################################comprobantes emitidos



class ComprobanteEmitidoAdmin(admin.ModelAdmin):
    change_form_template = 'LadoClientes/forms/change_form_base.html'  # Ruta a tu plantilla personalizada
    change_list_template = 'LadoClientes/forms/change_list_estado.html'  # Ruta a tu plantilla personalizada
    delete_confirmation_template = 'LadoClientes/forms/delete_confirmation_CFDI_emitidos.html'  # Ruta a tu plantilla personalizada
    delete_selected_confirmation_template = 'LadoClientes/forms/delete_selected_confirmation.html'  # Ruta a tu plantilla personalizada
    index_template = 'LadoClientes/pages/index.html'
    # list_display = ('folio', 'nombre', 'rfc', 'fecha', 'fecha_pago', 'total')  # Campos visibles en el listado
    # list_filter = ('fecha', 'fecha_pago')  # Filtros por fecha
    search_fields = ('folio', 'nombre', 'rfc', 'uuid')  # Búsqueda por folio, nombre, RFC y UUID
    # ordering = ['-fecha']  # Orden descendente por fecha
    readonly_fields = ('uuid', 'fecha')  # Campos que no pueden ser editados
    fieldsets = (
        ('Información del Comprobante', {
            'fields': ('folio', 'uuid', 'fecha', 'rfc', 'nombre', 'fecha_pago', 'total')  # Campos organizados en secciones
        }),
    )



    @admin.display(description="Acciones")
    def acciones(self, obj):
        """Genera los botones de acciones en la lista del admin."""
       
        eliminar_url = reverse('mi_admin:LadoClientes_comprobanteemitido_delete', args=[obj.pk])

        return format_html(
            
            '<a href="{}" class="button" style="color: red;" onclick="return confirm(\'¿Estás seguro de que deseas eliminar este comprobante?\');">Eliminar</a>',
           eliminar_url
        )



    def get_queryset(self, request):
        qs = super().get_queryset(request)

        forma_pago_subquery = FormaPago.objects.filter(
            c_FormaPago=OuterRef('forma_pago')
        ).values('descripcion')[:1]

        metodo_pago_subquery = MetodoPago.objects.filter(
            c_MetodoPago=OuterRef('metodo_pago')
        ).values('descripcion')[:1]

        qs = qs.annotate(
            forma_pago_desc=Subquery(forma_pago_subquery),
            metodo_pago_desc=Subquery(metodo_pago_subquery),
        )
        
        if request.user.is_superuser:
            return qs
        
        usuario_cfdi = UsersCFDI.objects.get(idUserCFDI=request.user)
        usuario_raiz = usuario_cfdi.get_raiz()
        # Negocio activo desde sesión
        negocio_activo = obtener_negocio_activo_para(request)

        

        return qs.filter(
            idUserCFDI__idUserCFDI=usuario_raiz,  # Asegura que pertenezca al usuario
            comprobante_relacionado__informacionFiscal=negocio_activo,  # Solo información fiscal principal
            comprobante_relacionado__informacionFiscal__activo=True,  # Solo activas
        ).distinct().select_related(
            'comprobante_relacionado__informacionFiscal'
        )


    

    def save_model(self, request, obj, form, change):
        """
        Valida y guarda el modelo con lógica personalizada.
        """
        # Validación del total para que no sea negativo
        if obj.total < 0:
            raise ValidationError("El total del comprobante no puede ser negativo.")

        # Asignar el usuario logueado si es una nueva factura
        if not change:
            obj.user = request.user  # Asigna el usuario que está creando la factura


        super().save_model(request, obj, form, change)
        

    def response_change(self, request, obj):
        """
        Maneja acciones personalizadas al guardar el modelo.
        """
        if "_save_draft" in request.POST:  # Detectar si se presionó un botón especial
            self.message_user(request, "El borrador del comprobante fue guardado correctamente.")
            return redirect("..")  # Regresa al listado de objetos

        return super().response_change(request, obj)
    
    #URL PARA HACER LA FUNCION
    def get_urls(self):
                urls = super().get_urls()
                custom_urls = [
                    path(
                    '<int:pk>/generate-xml/',
                    self.admin_site.admin_view(self.generate_xml),
                    name='comprobante_generate_xml',
                ),
                    path(
                    '<int:pk>/generate-pdf/',
                    self.admin_site.admin_view(self.generate_pdf),
                    name='comprobante_generate_pdf',
                ),
                    path(
                    '<int:pk>/send-invoice-email/',
                    self.admin_site.admin_view(self.send_invoice_email),
                    name='comprobante_send_invoice_email',
                ),

                path(
                    '<int:pk>/send-invoice-email-multiple/',
                    self.admin_site.admin_view(self.send_invoice_email_multiple),
                    name='comprobante_send_invoice_multi_email',
                ),
                    path(
                    '<int:pk>/generate-xml-cancelado/',
                    self.admin_site.admin_view(self.generate_xml_cancelado),
                    name='comprobante_generate_xml_cancelado',
                ),
                ]
                return custom_urls + urls

    def generate_xml(self, request, pk):
        print("timbrando", pk)
        comprobante = ComprobanteEmitido.objects.get(pk=pk)
        print(comprobante)
        xml_content = comprobante.xml_timbrado

        # Devolver el XML como respuesta HTTP
        response = HttpResponse(xml_content, content_type="application/xml")
        response["Content-Disposition"] = f'attachment; filename="factura_{pk}.xml"'
        return response
    
    def generate_xml_cancelado(self, request, pk):
        comprobante = CancelacionCFDI.objects.get(comprobante=pk)
        print(comprobante)
        xml_content = comprobante.respuesta_sat
        
        # Devolver el XML como respuesta HTTP
        response = HttpResponse(xml_content, content_type="application/xml")
        response["Content-Disposition"] = f'attachment; filename="factura_{pk}.xml"'
        return response
    
    def generate_pdf(self, request, pk):
        print("timbrando", pk)
        comprobante = ComprobanteEmitido.objects.get(pk=pk)
        cfdi_xml = ComprobanteEmitido.objects.get(pk=pk)
        print("cfdi_xml", cfdi_xml) 
        print("XML:", cfdi_xml.xml_timbrado[:1000])  # Imprimir solo los primeros 1000 caracteres

        # Parsear el XML
        cfdi = CFDI.from_string(cfdi_xml.xml_timbrado.encode('utf-8'))

        print("cfdi: ", cfdi)

        # Obtener el timbre fiscal digital
        timbre = cfdi  # es un objeto tipo TimbreFiscalDigital

        

        # Generar el PDF utilizando la función `pdf_bytes`
        pdf_content = render_comprobante_pdf_bytes(cfdi)

        # Crear una respuesta HTTP con el PDF
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="factura_{pk}.pdf"'

        return response
    

    def send_invoice_email(self, request, pk):
        comprobante = get_object_or_404(ComprobanteEmitido, pk=pk)
        cfdi_model = comprobante.comprobante_relacionado

        if not cfdi_model or not cfdi_model.informacionFiscal:
            self.message_user(request, "No se encontró la información fiscal asociada.", level=messages.ERROR)
            return HttpResponseRedirect("..")

        sucursal = cfdi_model.informacionFiscal
        cliente_email = sucursal.correo_electronico
        cliente_nombre = sucursal.nombre or "Cliente"

        if not cliente_email:
            self.message_user(request, "No hay correo electrónico en la sucursal seleccionada.", level=messages.ERROR)
            return HttpResponseRedirect("..")

        # Contenido del XML y PDF
        xml_data = comprobante.xml_timbrado.encode("utf-8")
        cfdi = CFDI.from_string(xml_data)
        pdf_data = render_comprobante_pdf_bytes(cfdi)

        subject = f"Factura {comprobante.folio or comprobante.pk}"
        body = f"""
        Estimado(a) {cliente_nombre},

        Le enviamos su factura correspondiente al folio {comprobante.folio or comprobante.pk}.
        En este correo encontrará adjuntos los archivos en formato PDF y XML.

        Gracias por su preferencia.

        -- 
        Este es un mensaje automático. No responder a este correo.
        """

        # Crear email con DEFAULT_FROM_EMAIL
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[cliente_email],
        )

        # Adjuntar archivos
        email.attach(f"factura_{comprobante.pk}.xml", xml_data, "application/xml")
        email.attach(f"factura_{comprobante.pk}.pdf", pdf_data, "application/pdf")

        try:
            email.send()
            self.message_user(request, f"Factura enviada correctamente a {cliente_email}.", level=messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"Error al enviar el correo: {e}", level=messages.ERROR)

        return redirect("mi_admin:cfdi_comprobanteemitido_changelist")

    def send_invoice_email_multiple(self, request, pk):
        comprobante = get_object_or_404(ComprobanteEmitido, pk=pk)
        emails_raw = request.POST.get("emails", "")
        email_list = [e.strip() for e in emails_raw.split(",") if e.strip()]
        if not email_list:
            return JsonResponse({"success": False, "message": "No se proporcionaron correos electrónicos."}, status=400)

        xml_data = comprobante.xml_timbrado.encode("utf-8")
        cfdi = CFDI.from_string(xml_data)
        pdf_data = render_comprobante_pdf_bytes(cfdi)

        subject = f"Factura {comprobante.folio or comprobante.pk}"
        body = """Estimado(a),

            Le enviamos su factura correspondiente.

            Gracias por su preferencia.

            --
            Este es un mensaje automático. No responder a este correo.
            """

        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=email_list,
        )
        email.attach(f"factura_{comprobante.pk}.xml", xml_data, "application/xml")
        email.attach(f"factura_{comprobante.pk}.pdf", pdf_data, "application/pdf")

        try:
            email.send()
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)


    
# Registro del modelo en el sitio de administración
mi_admin_site.register(ComprobanteEmitido, ComprobanteEmitidoAdmin)



class UserSingleGroupForm(forms.ModelForm):
    group = forms.ModelChoiceField(
        label="Grupo",
        queryset=Group.objects.none(),
        required=False,
        widget=forms.Select
    )

    class Meta:
        model = User
        exclude = ("groups",)  # ocultamos el ManyToMany original

    def __init__(self, *args, **kwargs):
        # Sacamos el usuario actual del request que pasaremos manualmente
        user = kwargs.pop('request_user', None)
        super().__init__(*args, **kwargs)

        if user:
            grupos_ids = GroupMeta.objects.filter(created_by=user).values_list('group_id', flat=True)
            self.fields['group'].queryset = Group.objects.filter(id__in=grupos_ids)
        else:
            self.fields['group'].queryset = Group.objects.none()

        # valor inicial si se está editando un usuario ya existente
        if self.instance and self.instance.pk:
            self.fields["group"].initial = self.instance.groups.first()

def is_hashed(value:str) -> bool:
    try:
        identify_hasher(value)
        return True
    except Exception:
        return False
    
class UserAdmin(admin.ModelAdmin):
    change_form_template = 'LadoClientes/forms/change_form_usuarios.html'
    change_list_template = 'LadoClientes/forms/change_list_usuarios.html'
    delete_confirmation_template = 'LadoClientes/forms/delete_confirmation.html'
    delete_selected_confirmation_template = 'LadoClientes/forms/delete_selected_confirmation.html'
    index_template = 'LadoClientes/pages/index.html'

    form = UserSingleGroupForm
    readonly_fields = ('date_joined',)

    fieldsets = (
        (None, {
            'fields': ('password', 'username', 'is_active', 'group', 'date_joined')
        }),
    )
    # list_display = ('nombre_certificado', 'archivo_certificado_preview', 'clave_privada_preview', 'user')
    # search_fields = ('nombre_certificado', 'user__username')
    # readonly_fields = ('user',)
    # fieldsets = (
    #     ('Información del Certificado', {
    #         'fields': ('nombre_certificado', 'archivo_certificado', 'clave_privada', 'contrasena')
    #     }),
    # )


    # def get_queryset(self, request):
    #     qs = super().get_queryset(request)

    #     if request.user.is_superuser:
    #         return qs.exclude(id__in=self._get_nodos_raiz_ids())

    #     try:
    #         usuario_cfdi = UsersCFDI.objects.get(idUserCFDI=request.user)
    #         usuario_raiz = usuario_cfdi.get_raiz()

    #         def obtener_descendientes(nodo):
    #             hijos = UsersCFDI.objects.filter(userParent=nodo)
    #             resultado = list(hijos)
    #             for h in hijos:
    #                 resultado += obtener_descendientes(h)
    #             return resultado

    #         # 🔁 árbol completo desde la raíz
    #         arbol = [usuario_raiz] + obtener_descendientes(usuario_raiz)

    #         # ✅ excluir manualmente al nodo raíz
    #         usuarios_ids = [
    #             u.idUserCFDI.id for u in arbol if u.idUserCFDI != usuario_raiz.idUserCFDI
    #         ]

    #         return qs.filter(id__in=usuarios_ids)

    #     except UsersCFDI.DoesNotExist:
    #         return qs.none()

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs.exclude(id__in=self._get_nodos_raiz_ids())

        try:
            usuario_cfdi = UsersCFDI.objects.get(idUserCFDI=request.user)

            # Usuario raíz: ver todo el árbol excepto él mismo
            if usuario_cfdi.userParent is None:
                usuario_raiz = usuario_cfdi

                def obtener_descendientes(nodo):
                    hijos = UsersCFDI.objects.filter(userParent=nodo)
                    resultado = list(hijos)
                    for h in hijos:
                        resultado += obtener_descendientes(h)
                    return resultado

                arbol = [usuario_raiz] + obtener_descendientes(usuario_raiz)

                usuarios_ids = [
                    u.idUserCFDI.id for u in arbol if u.idUserCFDI != usuario_raiz.idUserCFDI
                ]

                return qs.filter(id__in=usuarios_ids)

            # Usuario hijo: solo ve a los usuarios que él creó directamente
            else:
                hijos_directos = UsersCFDI.objects.filter(userParent=usuario_cfdi)
                hijos_ids = [u.idUserCFDI.id for u in hijos_directos]
                return qs.filter(id__in=hijos_ids)

        except UsersCFDI.DoesNotExist:
            return qs.none()


    def _get_nodos_raiz_ids(self):
        return list(
            UsersCFDI.objects.filter(userParent__isnull=True).values_list('idUserCFDI__id', flat=True)
        )

    @transaction.atomic
    def save_model(self, request, obj, form, change):
        # 1) Hash de password si vino en claro (crear o editar)
        raw = form.cleaned_data.get("password")
        if raw and not is_hashed(raw):
            obj.set_password(raw)

        # 2) (opcional) dar acceso al admin
        obj.is_staff = True

        # 3) Guarda el User UNA sola vez
        super().save_model(request, obj, form, change)

        # 4) Un solo grupo desde el combo `group` (crear o editar)
        if 'group' in form.cleaned_data:
            selected = form.cleaned_data['group']  # puede ser None
            obj.groups.set([selected] if selected else [])
            

        # 5) UsersCFDI: SOLO al crear (no tocar en edición)
        if not change:
            cfdiUser = UsersCFDI.objects.filter(idUserCFDI=request.user).first()
            UsersCFDI.objects.get_or_create(
                idUserCFDI=obj,
                defaults={
                    'userParent': cfdiUser,  # será None si el creador no tiene perfil CFDI (raíz)
                    # Usa el nombre de campo REAL: si tu FK es idUserServicePlan (no *_id), cámbialo abajo:
                    'idUserServicePlan_id': cfdiUser.idUserServicePlan_id,
                }
            )

    def get_form(self, request, obj=None, **kwargs):
        Form = super().get_form(request, obj, **kwargs)

        class RequestUserBoundForm(Form):
            def __init__(self2, *args, **kwargs):
                kwargs['request_user'] = request.user
                super().__init__(*args, **kwargs)

        return RequestUserBoundForm
    
        


# Registra el modelo con tu instancia personalizada de admin site
mi_admin_site.register(User, UserAdmin)


class BitacoraCFDIAdmin(nested_admin.NestedModelAdmin):
    change_form_template = 'LadoClientes/forms/change_form_bitacora.html'
    change_list_template = 'LadoClientes/forms/change_list.html'
    delete_confirmation_template = 'LadoClientes/forms/delete_confirmation.html'
    delete_selected_confirmation_template = 'LadoClientes/forms/delete_selected_confirmation.html'
    index_template = 'LadoClientes/pages/index.html'

    list_display = ('comprobante', 'creado_por')
    # list_filter = ('creado_por', 'editado_por', 'timbrado_por', 'cancelado_por')
    search_fields = ('creado_por', 'editado_por', 'timbrado_por', 'cancelado_por')
    list_per_page = 10

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        # Obtener perfil del usuario CFDI y negocio activo
        cfdiUser = UsersCFDI.objects.get(idUserCFDI=request.user)
        usuario_raiz = cfdiUser.get_raiz()
        negocio_activo = obtener_negocio_activo_para(request)

        if cfdiUser == usuario_raiz:
            # Usuario raíz ve registros creados por él o sus descendientes en el negocio activo
            descendientes = usuario_raiz.get_descendientes()
            usuarios_ids = [u.idUserCFDI.id for u in descendientes]

            return qs.filter(
                creado_por__in=usuarios_ids,
                comprobante__informacionFiscal=negocio_activo,
                comprobante__informacionFiscal__activo=True
            ).distinct().select_related('comprobante__informacionFiscal')
        else:
            # Usuario no raíz: solo lo que él creó, dentro del negocio activo
            return qs.filter(
                creado_por=request.user,
                comprobante__informacionFiscal=negocio_activo,
                comprobante__informacionFiscal__activo=True
            ).distinct().select_related('comprobante__informacionFiscal')


    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        # Obtener instancia del objeto actual (BitacoraCFDI)
        bitacora = self.get_object(request, object_id)
        
        extra_context = extra_context or {}
        
        if bitacora and bitacora.comprobante:
            # Construye la URL absoluta del PDF para el iframe
            # pdf_url = request.build_absolute_uri(
            #     reverse('cfdi:ver_pdf_comprobante', args=[bitacora.comprobante.id])
            # )
            #extra_context['pdf_url'] = pdf_url
            extra_context['pdf_url'] = reverse('cfdi:ver_pdf_comprobante', args=[bitacora.comprobante.id])


        return super().changeform_view(request, object_id, form_url, extra_context=extra_context)


mi_admin_site.register(BitacoraCFDI,BitacoraCFDIAdmin)