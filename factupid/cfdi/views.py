import datetime
from email.headerregistry import Group
from io import BytesIO
import re
from django.conf import settings
from django.shortcuts import render
from reportlab.lib.pagesizes import LETTER
from adapter.console.django_user_repository import CustomAuthAdapter
from console.models import Plan, Service, Service_Plan, User_Service
from cfdi.vistas.user import register as cfdi_register
from invoice.views import UtilitiesSOAP
from .forms import *
from django.utils.encoding import force_str as force_text
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth import login, logout
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden, Http404
from .models import InformacionFiscal,UsersCFDI
from .forms import InformacionFiscalForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import FacturaElectronica, FacturaElectronicaBorrador
from django.shortcuts import render
from reportlab.pdfgen import canvas
import binascii

import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)
# importaciones para generar xml
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from satcfdi.pacs.sat import Signer
from reportlab.pdfgen import canvas
from decimal import Decimal
from cfdi.Ladoclientes import FacturaElectronica  
from satcfdi.models import Signer
from satcfdi.create.cfd import cfdi40,nomina12
from satcfdi.create.cfd.catalogos import RegimenFiscal, UsoCFDI, MetodoPago, Impuesto, TipoFactor
from satcfdi.models import Signer
from satcfdi.create.cfd import cfdi40
from django.template import Template, Context
from django.core.serializers import serialize
from .models import PDFPersonalizado, Plantilla
from django.core.files.base import ContentFile
from django.utils.text import slugify

from weasyprint import HTML, CSS
from django.template.loader import render_to_string
from app.views import SoapService
import json, os, base64, time
from pathlib import Path
import xml.etree.ElementTree as ET
from django.core.files.storage import default_storage
import shutil
from bs4 import BeautifulSoup
import tinycss2
from satcfdi.cfdi import CFDI
from django.db.models import Q
import qrcode

from django.forms import modelformset_factory, inlineformset_factory
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect
from django.contrib import messages
from app.views import SoapServiceCancel

from cryptography import x509
from cryptography.hazmat.backends import default_backend
import base64

from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_der_private_key
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.hazmat.primitives import serialization

from django.utils.timezone import make_aware
from typing import Dict, Optional
from dateutil.parser import parse as parse_date  

from django.views.decorators.clickjacking import xframe_options_exempt
from cfdi.pdf_utils import render_comprobante_pdf_bytes

from django.http import HttpResponse, HttpResponseNotFound
from invoice.views import RegisterService
from decouple import config

# view generar XML
def Datos_factura(factura):
    comprobante_model = factura
    if not comprobante_model:
        print('No se encontró el comprobante')
        return None

    # Receptor
    receptor_model = Receptor.objects.filter(comprobante=comprobante_model).first()
    if not receptor_model:
        print('No se encontró el receptor')
        return None

    receptor = cfdi40.Receptor(
        rfc=receptor_model.rfc,
        nombre=receptor_model.nombre,
        uso_cfdi=receptor_model.c_UsoCFDI.c_UsoCFDI,
        domicilio_fiscal_receptor=str(receptor_model.c_DomicilioFiscalReceptor.c_CodigoPostal),
        regimen_fiscal_receptor=str(receptor_model.c_RegimenFiscalReceptor.c_RegimenFiscal)
    )

    # Información del emisor
    emisor_model = Emisor.objects.filter(comprobante=comprobante_model).first()
    if not emisor_model:
        print('No se encontró el emisor')
        return None

    # Obtener certificado desde la información fiscal
    info_fiscal = comprobante_model.informacionFiscal
    certificado = info_fiscal.idUserCFDI.idUserCFDI.certificados.first()

    signer = Signer.load(
        certificate=certificado.archivo_certificado.read(),
        key=certificado.clave_privada.read(),
        password=certificado.get_plain_password(),
    )

    emisor = cfdi40.Emisor(
        rfc=signer.rfc,
        nombre=emisor_model.nombre,
        regimen_fiscal=str(emisor_model.c_RegimenFiscal.c_RegimenFiscal),
        
    )

    # Crear conceptos
    conceptos = []
    for concepto_model in comprobante_model.conceptos.all():
        concepto_cfdi = cfdi40.Concepto(
            clave_prod_serv=concepto_model.c_ClaveProdServ.c_ClaveProdServ,
            cantidad=Decimal(concepto_model.cantidad),
            clave_unidad=concepto_model.c_ClaveUnidad.c_ClaveUnidad,
            descripcion=concepto_model.descripcion,
            valor_unitario=Decimal(concepto_model.valorUnitario),
            unidad=concepto_model.unidad or "",
            objeto_imp=concepto_model.c_ObjetoImp.c_ObjetoImp,
            impuestos=cfdi40.Impuestos()
        )
        conceptos.append(concepto_cfdi)
        

    # Crear el comprobante CFDI
    cfdi = cfdi40.Comprobante(
        emisor=emisor,
        lugar_expedicion=str(58000),
        receptor=receptor,
        metodo_pago=comprobante_model.c_MetodoPago.c_MetodoPago if comprobante_model.c_MetodoPago else None,
        forma_pago=comprobante_model.c_FormaPago.c_FormaPago if comprobante_model.c_FormaPago else None,
        serie=comprobante_model.serie or 'A',
        folio=comprobante_model.folio or '1',
        moneda=comprobante_model.c_Moneda.c_Moneda if comprobante_model.c_Moneda else 'MXN',
        tipo_de_comprobante='I',
        exportacion=comprobante_model.c_Exportacion.c_Exportacion if comprobante_model.c_Exportacion else '01',
        conceptos=conceptos,
    )

    # Firmar y procesar
    cfdi.sign(signer)
    cfdi = cfdi.process()
    
    return cfdi

def limpiar_css_usado(html, css):

    soup = BeautifulSoup(html, 'html.parser')

    # Extraer selectores usados
    clases_usadas = set()
    ids_usados = set()
    etiquetas_usadas = set()

    for tag in soup.find_all(True):
        etiquetas_usadas.add(tag.name)
        if tag.get('id'):
            ids_usados.add(f"#{tag.get('id')}")
        if tag.get('class'):
            clases_usadas.update([f".{cls}" for cls in tag.get('class')])

    reglas_usadas = []
    reglas_normalizadas = set()

    reglas = tinycss2.parse_stylesheet(css, skip_whitespace=True)

    for regla in reglas:
        if regla.type == 'qualified-rule':
            selector = tinycss2.serialize(regla.prelude).strip()
            selectores = [sel.strip() for sel in selector.split(',')]

            for sel in selectores:
                if (
                    sel in clases_usadas or
                    sel in ids_usados or
                    sel in etiquetas_usadas or
                    sel == '*' or
                    sel.startswith('body')
                ):
                    regla_serializada = tinycss2.serialize([regla]).strip()

                    # Normalizar para comparación
                    regla_normalizada = regla_serializada.replace(" ", "").replace("\n", "")
                    if regla_normalizada not in reglas_normalizadas:
                        reglas_usadas.append(regla_serializada)
                        reglas_normalizadas.add(regla_normalizada)
                    break

    # Estilos forzados para compactar tablas
    estilos_tabla = """
            p {margin-top: 0 !important;margin-bottom: 0 !important;}
            .dato{word-wrap: break-word;
        overflow-wrap: break-word;
        word-break: break-word;
        white-space: normal;}
        .renglon {border: 1px solid #dee2e6;}
    """

    reglas_usadas.append(estilos_tabla.strip())
    css_limpio = '\n'.join(reglas_usadas)
    #print("CSS limpio:", css_limpio)
    return css_limpio

############################# EDITOR GRAPES #################################################
## Función para cargar el editor de plantillas
@login_required(login_url="/mi-admin/login/")

def editor(request):
    #return render(request, 'cfdi/editor.html')
    return render(request, 'LadoClientes/forms/change_form_editor.html')


def _cargar_comprobante_base():
    """Lee el HTML base del comprobante para usarlo como punto de partida en el editor."""

    plantilla_path = Path(settings.BASE_DIR) / "cfdi" / "templates" / "pdf" / "Comprobante.html"
    try:
        return plantilla_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def _cargar_css_base():
    """Lee el CSS por defecto del comprobante (estilos de satcfdi)."""

    css_path = Path(settings.BASE_DIR) / "static" / "librerias" / "satcfdi" / "_style.css"
    try:
        return css_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


@login_required(login_url="/mi-admin/login/")
def personalizar_pdf(request):
    """Pantalla para crear diseños de PDF con arrastrar y soltar usando GrapesJS."""

    plantillas = PDFPersonalizado.objects.filter(created_by=request.user).values(
        "id", "name", "is_default"
    ).order_by("-updated_at")

    contexto = {
        "base_html": _cargar_comprobante_base(),
        "base_css": _cargar_css_base(),
        "plantillas": plantillas,
    }

    return render(request, 'LadoClientes/pages/personalizar_pdf.html', contexto)


def _escribir_plantilla_default(html: str, css: str):
    """Sobrescribe la plantilla principal cuando el usuario marca su diseño como default."""

    plantilla_dir = os.path.join(settings.BASE_DIR, "cfdi", "templates", "pdf")
    os.makedirs(plantilla_dir, exist_ok=True)
    destino = os.path.join(plantilla_dir, "Comprobante.html")

    with open(destino, "w", encoding="utf-8") as salida:
        salida.write(f"<style>\n{css}\n</style>\n{html}")


@login_required(login_url="/mi-admin/login/")
@csrf_exempt
def exportar_pdf_personalizado(request):
    """Genera un PDF desde el editor y guarda la plantilla asociándola al usuario."""

    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Método no permitido."}, status=405)

    html = request.POST.get("html", "")
    css = request.POST.get("css", "")
    nombre = request.POST.get("nombre", "Plantilla PDF")
    plantilla_id = request.POST.get("plantilla_id")
    es_default = request.POST.get("is_default") in ["true", "True", "1", True]

    if not html.strip():
        return JsonResponse({"success": False, "error": "No se recibió contenido para generar el PDF."}, status=400)

    contenido = f"<style>{css}</style>{html}"
    pdf_bytes = HTML(string=contenido, base_url=request.build_absolute_uri('/')).write_pdf()

    defaults = {
        "html": html,
        "css": css,
        "is_default": es_default,
    }

    if plantilla_id:
        instancia = get_object_or_404(PDFPersonalizado, pk=plantilla_id, created_by=request.user)
        for campo, valor in defaults.items():
            setattr(instancia, campo, valor)
        instancia.name = nombre
        instancia.save()
    else:
        instancia, _ = PDFPersonalizado.objects.update_or_create(
            created_by=request.user,
            name=nombre,
            defaults=defaults,
        )

    nombre_archivo = f"{slugify(nombre) or 'plantilla'}-{instancia.id}.pdf"
    instancia.pdf_file.save(nombre_archivo, ContentFile(pdf_bytes))

    if es_default:
        PDFPersonalizado.objects.filter(created_by=request.user).exclude(pk=instancia.pk).update(is_default=False)
        _escribir_plantilla_default(html, css)

    respuesta = HttpResponse(pdf_bytes, content_type="application/pdf")
    respuesta["Content-Disposition"] = f"attachment; filename=\"{nombre_archivo}\""
    return respuesta


@login_required(login_url="/mi-admin/login/")
@csrf_exempt
def guardar_pdf_personalizado(request):
    """Guarda la plantilla del editor sin descargar el PDF."""

    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Método no permitido."}, status=405)

    html = request.POST.get("html", "").strip()
    css = request.POST.get("css", "")
    nombre = request.POST.get("nombre", "Plantilla PDF")
    plantilla_id = request.POST.get("plantilla_id")
    es_default = request.POST.get("is_default") in ["true", "True", "1", True]

    if not html:
        return JsonResponse({"success": False, "error": "No hay contenido para guardar."}, status=400)

    defaults = {
        "html": html,
        "css": css,
        "is_default": es_default,
    }

    if plantilla_id:
        instancia = get_object_or_404(PDFPersonalizado, pk=plantilla_id, created_by=request.user)
        for campo, valor in defaults.items():
            setattr(instancia, campo, valor)
        instancia.name = nombre
        instancia.save()
    else:
        instancia, _ = PDFPersonalizado.objects.update_or_create(
            created_by=request.user,
            name=nombre,
            defaults=defaults,
        )

    if es_default:
        PDFPersonalizado.objects.filter(created_by=request.user).exclude(pk=instancia.pk).update(is_default=False)
        _escribir_plantilla_default(html, css)

    return JsonResponse({"success": True, "id": instancia.pk, "name": instancia.name, "is_default": instancia.is_default})


@login_required(login_url="/mi-admin/login/")
def listar_pdf_personalizados(request):
    """Devuelve las plantillas creadas por el usuario autenticado."""

    plantillas = PDFPersonalizado.objects.filter(created_by=request.user).values(
        "id", "name", "is_default", "updated_at"
    ).order_by("-updated_at")
    return JsonResponse(list(plantillas), safe=False)


@login_required(login_url="/mi-admin/login/")
def obtener_pdf_personalizado(request, pk):
    """Recupera el contenido HTML/CSS de una plantilla del usuario."""

    plantilla = get_object_or_404(PDFPersonalizado, pk=pk, created_by=request.user)
    data = {
        "id": plantilla.pk,
        "name": plantilla.name,
        "html": plantilla.html,
        "css": plantilla.css,
        "is_default": plantilla.is_default,
    }
    return JsonResponse(data)

## FUNCION PARA OBTENER LOS MODELOS DE PLANTILLAS
@login_required(login_url="/mi-admin/login/")
def ModeloDePlantilla(request):
    modelo = Plantilla.objects.values('id', 'name', 'status')
    return JsonResponse(list(modelo), safe=False)
## FUNCION PARA OBTENER LOS usuarios de CFDI
@login_required(login_url="/mi-admin/login/")
def ModeloDeUsuario(request):
    modelo = UsersCFDI.objects.values(
    'idUserCFDI',                # ID del User
    'idUserCFDI__username',      # Username del User
    'idUserCFDI__email',         # Email del User
    'userParent',                # ID del padre (otro UsersCFDI)
    'idUserServicePlan_id'       # ID del servicio
    )
    return JsonResponse(list(modelo), safe=False)

# FUNCION PARA CREAR UN NUEVO MODELO DE PLANTILLA
@login_required(login_url="/mi-admin/login/")
@csrf_exempt
def crearModelo(request):
    if request.method == "POST":
        nombre = request.POST['nombre']
        id_usuario = request.POST['id_usuario']
        if not nombre:
            return JsonResponse({"success": False, "error": "Nombre no válido."})
        # Verificar si ya existe un modelo con ese nombre
        if Plantilla.objects.filter(name=nombre).exists():
            return JsonResponse({"success": False, "error": "El modelo ya existe."})
        # Obtener el usuario CFDI
        usuario = UsersCFDI.objects.get(idUserCFDI=id_usuario)
        # Verifica cuántas plantillas tiene ya este usuario
        cantidad_plantillas = Plantilla.objects.filter(idUserCFDI=usuario).count()
        status = "draft"
        if cantidad_plantillas == 0:
            status = "published"
        
        plantilla = Plantilla.objects.create(
            idUserCFDI=usuario,
            name=nombre,           # Asigna el mismo nombre
            html="<body></body>",       # HTML por defecto
            css="",                       # CSS vacío por defecto
            status=status
        )

        return JsonResponse({"success": True, "id": plantilla.id, "name": plantilla.name})

## FUNCIONES PARA OBTENER LOS DATOS DE LAS PLANTILLAS
@login_required(login_url="/mi-admin/login/")
@csrf_exempt
def getPlantilla(request, id):
    try:
        plantilla = Plantilla.objects.get(id=id)
        return JsonResponse({
            "exists": True,
            "id": plantilla.id,
            "html": plantilla.html,
            "css": plantilla.css,
            "img": plantilla.imagen.url if plantilla.imagen else None,
        })
    except Plantilla.DoesNotExist:
        return JsonResponse({"exists": False})

## FUNCION PARA SALVAR O MODIFICAR LAS PLANTILLAS
@login_required(login_url="/mi-admin/login/")
@csrf_exempt
def savePlantilla(request):
    if request.method == 'POST':
        id = request.POST['id']
        html = request.POST['html']
        if html=="<body></body>":
            css = ""
        else:
            css = request.POST['css']
        try:
            plantilla = Plantilla.objects.get(id=id)
        except Plantilla.DoesNotExist:
            return JsonResponse({"error": "Plantilla no encontrada"})
        # Verificar si ya existe una plantilla para ese modelo
        plantilla.html = html
        plantilla.css = css
        plantilla.save()

        return JsonResponse({"result": {"id": plantilla.id, "name": plantilla.name, "imagen_url": plantilla.imagen.url if plantilla.imagen else None}})    

# FUNCION PARA Guardar como
@csrf_exempt
@login_required(login_url="/mi-admin/login/")
def GuardarComo(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Método no permitido."})
    
    id = request.POST['id_modelo']
    nombre = request.POST['modelo']
    html = request.POST['html']
    cssx = request.POST['css']
    css = limpiar_css_usado(html, cssx)  # Limpieza aquí

    if not nombre:
        return JsonResponse({"success": False, "error": "Nombre no válido."})

    try:
        plantillaO= Plantilla.objects.get(id=id)
        # Crear el nuevo modelo
        usuario = plantillaO.idUserCFDI
        # Crear una nueva plantilla asociada
        plantilla = Plantilla.objects.create(
            idUserCFDI=usuario,
            name=nombre,           # Asigna el mismo nombre
            html=html,       # HTML por defecto
            css=css,
            imagen=plantillaO.imagen,
        )
        
        return JsonResponse({
            "success": True,
            "id": plantilla.id,
            "name": plantilla.name,
            "html": plantilla.html,
            "css": plantilla.css,
            "imagen": plantilla.imagen.url if plantilla.imagen else None,
        })

    except Exception as e:
        return JsonResponse({"success": False, "error": f"Error inesperado: {str(e)}"})
## FUNCION PARA ELIMINAR LA PLANTILLA
@login_required(login_url="/mi-admin/login/")
@csrf_exempt
def dropPlantilla(request):
    if request.method == 'POST':
        id = request.POST['modelo']
        try:
            plantilla = Plantilla.objects.get(id=id)

            if plantilla.imagen and plantilla.imagen.name:
                ruta_imagen = os.path.join(settings.MEDIA_ROOT, plantilla.imagen.name)
                if os.path.isfile(ruta_imagen):
                    os.remove(ruta_imagen)
            
            plantilla.delete()
            return JsonResponse({"success": True, "mensaje": "Plantilla eliminada correctamente."})
    
        except Plantilla.DoesNotExist:
            return JsonResponse({"success": False, "error": "La plantilla no existe."})
        
        except Exception as e:
            return JsonResponse({"success": False, "error": f"Error inesperado: {str(e)}"})
## FUNCION PARA SUBIR IMAGEN
@login_required(login_url="/mi-admin/login/")
@csrf_exempt
def subir_imagen(request):
    if request.method == 'POST' and request.FILES.get('imagen'):
        imagen = request.FILES['imagen']
        modelo_id = request.POST['modelo']
        plantilla = Plantilla.objects.get(id=modelo_id)  # Busca la plantilla
        if plantilla.imagen and plantilla.imagen.name:
                ruta_imagen_anterior = os.path.join(settings.MEDIA_ROOT, plantilla.imagen.name)
                if os.path.isfile(ruta_imagen_anterior):
                    os.remove(ruta_imagen_anterior)

        plantilla.imagen = imagen
        plantilla.save()

        return JsonResponse({'url': plantilla.imagen.url})
    return JsonResponse({'error': 'No se subió imagen'}, status=400)

## Funcion para obetener la plantilla
def obtener_plantilla_base():
    # Obtener todas las plantillas
    plantilla_publicada = Plantilla.objects.filter(status="published").first()
    if plantilla_publicada:
        return plantilla_publicada.id

    # Si no hay ninguna plantilla publicada, retornar -1
    return -1

#obtener datos de la factura
def datos_factura(id):
    factura = Comprobante.objects.get(id=id)
    comprobante = Datos_factura(factura)
    datos = {
            "factura": {
                "fVersion": comprobante['Version'],#
                "fSerie": comprobante['Serie'],#
                "fFolio": comprobante['Folio'],#
                "fFecha_emision": comprobante['Fecha'],#
                "fFecha_certificacion": "XXXXXXX",
                "fSello_SAT": "XXXXXX",
                "fForma_pago": comprobante['FormaPago'],##
                "fNo_certificado": comprobante['NoCertificado'],#
                "fCertificado_SAT": comprobante['Certificado'],
                "fCondicion_pago": "XXXXXXX",
                "fSubtotal": comprobante['SubTotal'],#
                "fDescuento": "XXXXXXX",
                "fMoneda": comprobante['Moneda'],##
                "fTipo_cambio": "XXXXXXX",
                "fTotal": comprobante['Total'],#
                "fTipo_de_comprobante": comprobante['TipoDeComprobante'],#
                "fExportacion": comprobante['Exportacion'],##
                "fMetodo_pago": comprobante['MetodoPago'],##
                "fLugar_expedicion": comprobante['LugarExpedicion'],#
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
                "eRFC": comprobante['Emisor']['Rfc'],#
                "eRazon_social": comprobante['Emisor']['Nombre'],#
                "eRegimen_fiscal": comprobante['Emisor']['RegimenFiscal'],##
                "eFac_Atr_adquiriente": "XXXX",
                
                "eDomicilio_fiscal": "XXXXX",
                "eCurp": "XXXXXXX"
            },
            "receptor": {
                "rRFC": comprobante['Receptor']['Rfc'],#
                "rRazon_social": comprobante['Receptor']['Nombre'],#
                "rDomicilio_fiscal": comprobante['Receptor']['DomicilioFiscalReceptor'],##
                "rResidencia_fiscal": "XXXXXXX",
                "rNum_Reg_id_Trib": "XXXXXXX",
                "rRegimen_fiscal": comprobante['Receptor']['RegimenFiscalReceptor'],##
                "rUso_CFDI": comprobante['Receptor']['UsoCFDI'],##
                "rNacionalidad": "XXXXXXX",
                "rCURP": "XXXXXXX",
            },
            "conceptos":[
                {
                    "cCve_prod": c['ClaveProdServ'],##
                    "cNum_id": "XXXXXXX",
                    "cCantidad": c['Cantidad'],#
                    "cCve_Unidad": c['ClaveUnidad'],##
                    "cUnidad": c['Unidad'],#
                    "cDescripcion": c['Descripcion'],#
                    "cValor_unitario": c['ValorUnitario'],#
                    "cImporte": c['Importe'],#
                    "cDescuento": "XXXXXXX",
                    "cObjeto_impuesto": c['ObjetoImp'],#
                    # traslados*/
                    "ctBase": "XXXXXXX",
                    "ctImpuesto": "XXXXXXX",
                    "ctTipoFactor": "XXXXXXX",
                    "ctTasaOcuota": "XXXXXXX",
                    "ctImporte": "XXXXXXX",
                    # retencion*/
                    "crBase": "XXXXXXX",
                    "crImpuesto": "XXXXXXX",
                    "crTipoFactor": "XXXXXXX",
                    "crTasaOcuota": "XXXXXXX",
                    "crImporte": "XXXXXXX",
                    # ACuentaTerceros */
                    "caRFC": "XXXXXXX",
                    "caRazonSocial": "XXXXXXX",
                    "caRegimenFiscal": "XXXXXXX",
                    "caDomicilioFiscal": "XXXXXXX",
                    #Informacion Aduanera */
                    "ciNumeroPedimento": "XXXXXXX",
                    #Cuenta predial*/
                    "ccNumero": "XXXXXXX",
                    #Parte*/
                    "cpCve_prod": "XXXXXXX",
                    "cpNum_id": "XXXXXXX",
                    "cpCantidad": "XXXXXXX",
                    "cpUnidad": "XXXXXXX",
                    "cpDescripcion": "XXXXXXX",
                    "cpValor_unitario": "XXXXXXX",
                    "cpImporte": "XXXXXXX",
                    # informacipon aduanera (parte)*/
                    "cpNum_pedi": "XXXXXXX",
                    
                }
                for c in comprobante['Conceptos']
            ],
            "impuesto": {
                "imTot_imp_Ret": "XXXXXXX",
                "imTot_imp_Tras": "XXXXXXX",
                # retencion*/
                "imrImpuesto": "XXXXXXX",
                "imrImporte": "XXXXXXX",
                # traslados*/
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
                # ImpRetenidos*/
                "trBase":"xxxxx",
                "trImpuesto":"xxxxx",
                "trMonto":"xxxxx",
                "trTipoPago":"xxxxx"
            },
            "notas":{
                "nSello_digital_contribuyente":comprobante['Sello'] ,#???
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
            }
        }
    
    return datos
#OBTENER DATOS DE LA FACTURA TIMBRADA
import xml.etree.ElementTree as ET

import xml.etree.ElementTree as ET

def datos_factura_timbrada(id):
    comprobante_cfdi = ComprobanteEmitido.objects.get(pk=id)
    xml_string = comprobante_cfdi.xml_timbrado

    NS = {
        'cfdi': 'http://www.sat.gob.mx/cfd/4',
        'nomina12': 'http://www.sat.gob.mx/nomina12',
        'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'
    }

    root = ET.fromstring(xml_string.encode('utf-8'))
    tipo_comprobante = comprobante_cfdi.tipo

    if tipo_comprobante == "Factura electrónica":
        datos = {}
        datos['factura'] = {
            "fVersion": root.attrib.get("Version", ""),
            "fSerie": root.attrib.get("Serie", ""),
            "fFolio": root.attrib.get("Folio", ""),
            "fFecha_emision": root.attrib.get("Fecha", ""),
            "fForma_pago": root.attrib.get("FormaPago", "N/A"),
            "fNo_certificado": root.attrib.get("NoCertificado", ""),
            "fCertificado_SAT": root.attrib.get("Certificado", ""),
            "fCondicion_pago": root.attrib.get("CondicionesDePago", ""),
            "fSubtotal": root.attrib.get("SubTotal", ""),
            "fDescuento": root.attrib.get("Descuento", ""),
            "fMoneda": root.attrib.get("Moneda", ""),
            "fTipo_cambio": root.attrib.get("TipoCambio", ""),
            "fTotal": root.attrib.get("Total", ""),
            "fTipo_de_comprobante": root.attrib.get("TipoDeComprobante", ""),
            "fExportacion": root.attrib.get("Exportacion", ""),
            "fMetodo_pago": root.attrib.get("MetodoPago", "N/A"),
            "fLugar_expedicion": root.attrib.get("LugarExpedicion", ""),
            "fConfirmacion": root.attrib.get("Confirmacion", ""),
            "fTotal_con_letra": "",
        }

        tfd = root.find('.//cfdi:Complemento/tfd:TimbreFiscalDigital', NS)
        if tfd is not None:
            datos["factura"].update({
                "fFolio_fiscal": tfd.attrib.get('UUID', ''),
                "fFecha_certificacion": tfd.attrib.get('FechaTimbrado', ''),
                "fSello_SAT": tfd.attrib.get('SelloSAT', ''),
                "fSerie_CSD_SAT": tfd.attrib.get('NoCertificadoSAT', ''),
            })

        emisor = root.find('cfdi:Emisor', NS)
        datos["emisor"] = {
            "eRFC": emisor.attrib.get("Rfc", "") if emisor is not None else "",
            "eRazon_social": emisor.attrib.get("Nombre", "") if emisor is not None else "",
            "eRegimen_fiscal": emisor.attrib.get("RegimenFiscal", "") if emisor is not None else "",
        }
        receptor = root.find('cfdi:Receptor', NS)
        datos["receptor"] = {
            "rRFC": receptor.attrib.get("Rfc", "") if receptor is not None else "",
            "rRazon_social": receptor.attrib.get("Nombre", "") if receptor is not None else "",
            "rDomicilio_fiscal": receptor.attrib.get("DomicilioFiscalReceptor", "") if receptor is not None else "",
            "rRegimen_fiscal": receptor.attrib.get("RegimenFiscalReceptor", "") if receptor is not None else "",
            "rUso_CFDI": receptor.attrib.get("UsoCFDI", "") if receptor is not None else "",
        }

        datos["conceptos"] = []
        conceptos = root.find('cfdi:Conceptos', NS)
        if conceptos is not None:
            for c in conceptos.findall('cfdi:Concepto', NS):
                datos["conceptos"].append({
                    "cCve_prod": c.attrib.get('ClaveProdServ', ''),
                    "cCantidad": c.attrib.get('Cantidad', ''),
                    "cCve_Unidad": c.attrib.get('ClaveUnidad', ''),
                    "cUnidad": c.attrib.get('Unidad', ''),
                    "cDescripcion": c.attrib.get('Descripcion', ''),
                    "cValor_unitario": c.attrib.get('ValorUnitario', ''),
                    "cImporte": c.attrib.get('Importe', ''),
                    "cObjeto_impuesto": c.attrib.get('ObjetoImp', ''),
                })
        return datos

    elif tipo_comprobante == "Nómina":
        complemento = root.find('cfdi:Complemento', NS)
        nomina = complemento.find('nomina12:Nomina', NS) if complemento is not None else None
        if nomina is None:
            raise Exception("No se encontró el complemento de Nómina en el XML.")

        tfd = root.find('.//cfdi:Complemento/tfd:TimbreFiscalDigital', NS)
        emisor = root.find('cfdi:Emisor', NS)
        receptor = root.find('cfdi:Receptor', NS)
        nomina_receptor = nomina.find('nomina12:Receptor', NS)
        nomina_emisor = nomina.find('nomina12:Emisor', NS)

        datos = {}
        datos['factura'] = {
            "fVersion": root.attrib.get("Version", ""),
            "fSerie": root.attrib.get("Serie", ""),
            "fFolio": root.attrib.get("Folio", ""),
            "fFecha_emision": root.attrib.get("Fecha", ""),
            "fForma_pago": root.attrib.get("FormaPago", "N/A"),
            "fNo_certificado": root.attrib.get("NoCertificado", ""),
            "fCertificado_SAT": root.attrib.get("Certificado", ""),
            "fCondicion_pago": root.attrib.get("CondicionesDePago", ""),
            "fSubtotal": root.attrib.get("SubTotal", ""),
            "fDescuento": root.attrib.get("Descuento", ""),
            "fMoneda": root.attrib.get("Moneda", ""),
            "fTipo_cambio": root.attrib.get("TipoCambio", ""),
            "fTotal": root.attrib.get("Total", ""),
            "fTipo_de_comprobante": root.attrib.get("TipoDeComprobante", ""),
            "fExportacion": root.attrib.get("Exportacion", ""),
            "fMetodo_pago": root.attrib.get("MetodoPago", "N/A"),
            "fLugar_expedicion": root.attrib.get("LugarExpedicion", ""),
            "fConfirmacion": root.attrib.get("Confirmacion", ""),
            "fTotal_con_letra": "",
        }

        if tfd is not None:
            datos["factura"].update({
                "fFolio_fiscal": tfd.attrib.get('UUID', ''),
                "fFecha_certificacion": tfd.attrib.get('FechaTimbrado', ''),
                "fSello_SAT": tfd.attrib.get('SelloSAT', ''),
                "fSerie_CSD_SAT": tfd.attrib.get('NoCertificadoSAT', ''),
            })

        datos["emisor"] = {
            "eRFC": emisor.attrib.get("Rfc", "") if emisor is not None else "",
            "eRazon_social": emisor.attrib.get("Nombre", "") if emisor is not None else "",
            "eRegimen_fiscal": emisor.attrib.get("RegimenFiscal", "") if emisor is not None else "",
            #curp
            "eCurp": nomina_emisor.attrib.get("Curp", "") if nomina_emisor is not None else "",
            #Domicilio fiscal temporal porque se usa el de expedicion
            "eDomicilio_fiscal": root.attrib.get("LugarExpedicion", "") if root is not None else "",
            "eFac_Atr_adquiriente": emisor.attrib.get("FacAtrAdquirente", "") if emisor is not None else ""
        }
        datos["receptor"] = {
            "rRFC": receptor.attrib.get("Rfc", "") if receptor is not None else "",
            "rRazon_social": receptor.attrib.get("Nombre", "") if receptor is not None else "",
            "rDomicilio_fiscal": receptor.attrib.get("DomicilioFiscalReceptor", "") if receptor is not None else "",
            "rRegimen_fiscal": receptor.attrib.get("RegimenFiscalReceptor", "") if receptor is not None else "",
            "rUso_CFDI": receptor.attrib.get("UsoCFDI", "") if receptor is not None else "",
        }
        datos["nomina"] = {
            "noFecha_inicial_pago": nomina.attrib.get('FechaInicialPago', ''),
            "noFecha_final_pago": nomina.attrib.get('FechaFinalPago', ''),
            "noFecha_pago": nomina.attrib.get('FechaPago', ''),
            "noDias_pagados": nomina.attrib.get('NumDiasPagados', ''),
            "noSalario_base": nomina_receptor.attrib.get('SalarioBaseCotApor', ''),
            "noSalario_diario_integrado": nomina_receptor.attrib.get('SalarioDiarioIntegrado', ''),
            
        }

        nomina_tag = root.find('.//nomina12:Nomina', NS)
        percepciones_tag = root.find('.//nomina12:Percepciones', NS)
        deducciones_tag = root.find('.//nomina12:Deducciones', NS)

        datos["total_percepciones"] = {
            "tpTotal_percepciones": nomina_tag.attrib.get("TotalPercepciones", "") if nomina_tag is not None else "",
            "tpTotal_otros_pagos": nomina_tag.attrib.get("TotalOtrosPagos", "") if nomina_tag is not None else "",
            "tpTotal_deducciones": nomina_tag.attrib.get("TotalDeducciones", "") if nomina_tag is not None else "",
            "tpTotal_Exento": percepciones_tag.attrib.get("TotalExento", "") if percepciones_tag is not None else "",
            "tpTotal_Grabado": percepciones_tag.attrib.get("TotalGravado", "") if percepciones_tag is not None else "",
            "tpTotal_JPR": percepciones_tag.attrib.get("TotalJubilacionPensionRetiro", "") if percepciones_tag is not None else "",
            "tpTotal_Sep_Indemnizacion": percepciones_tag.attrib.get("TotalSeparacionIndemnizacion", "") if percepciones_tag is not None else "",
            "tpTotal": percepciones_tag.attrib.get("TotalSueldos", "") if percepciones_tag is not None else "",
        }

        datos["total_deducciones"] = {
        "toTotal_Otras_Deducciones": deducciones_tag.attrib.get("TotalOtrasDeducciones", "") if deducciones_tag is not None else "",
        "toTotal_Imp_Retenidos": deducciones_tag.attrib.get("TotalImpuestosRetenidos", "") if deducciones_tag is not None else "",
        }

        datos["empleado"] = {
            "emNSS": nomina_receptor.attrib.get("NumSeguridadSocial", "") if nomina_receptor is not None else "",
            "emContrato": nomina_receptor.attrib.get("TipoContrato", "") if nomina_receptor is not None else "",
            "emPeriodicidad": nomina_receptor.attrib.get("PeriodicidadPago", "") if nomina_receptor is not None else "",
            "emEntidad": nomina_receptor.attrib.get("ClaveEntFed", "") if nomina_receptor is not None else "",
            "emSindicalizado": nomina_receptor.attrib.get("Sindicalizado", "") if nomina_receptor is not None else "",
            "emRFC": receptor.attrib.get("Rfc", "") if receptor is not None else "",  # Del CFDI principal
            "emRegimen": nomina_receptor.attrib.get("TipoRegimen", "") if nomina_receptor is not None else "",
            "emReg_patronal": nomina_emisor.attrib.get("RegistroPatronal", "") if nomina_emisor is not None else "",
            "emJornada": nomina_receptor.attrib.get("TipoJornada", "") if nomina_receptor is not None else "",
            "emCodPostal": receptor.attrib.get("DomicilioFiscalReceptor", "") if receptor is not None else "",
            "emDepartamento": nomina_receptor.attrib.get("Departamento", "") if nomina_receptor is not None else "",
            "emBanco": nomina_receptor.attrib.get("Banco", "") if nomina_receptor is not None else "",
            "emRiesgo": nomina_receptor.attrib.get("RiesgoPuesto", "") if nomina_receptor is not None else "",
            "emInicio_rel_lab": nomina_receptor.attrib.get("FechaInicioRelLaboral", "") if nomina_receptor is not None else "",
            "emClaBe": nomina_receptor.attrib.get("CuentaBancaria", "") if nomina_receptor is not None else "",
            "emNo_Empleado": nomina_receptor.attrib.get("NumEmpleado", "") if nomina_receptor is not None else "",
            "emEmpleado": nomina_receptor.attrib.get("NumEmpleado", "") if nomina_receptor is not None else "",
            "emCURP": nomina_receptor.attrib.get("Curp", "") if nomina_receptor is not None else "",
            "emAntiguedad": nomina_receptor.attrib.get("Antigüedad", "") if nomina_receptor is not None else "",
            "emTipoJornada": nomina_receptor.attrib.get("TipoJornada", "") if nomina_receptor is not None else "",
            "emBanco": nomina_receptor.attrib.get("Banco", "") if nomina_receptor is not None else "",
            #puesto
            "emPuesto": nomina_receptor.attrib.get("Puesto", "") if nomina_receptor is not None else "",
            "emSindicalizado": nomina_receptor.attrib.get("Sindicalizado", "") if nomina_receptor is not None else "",
            "emDepartamento": nomina_receptor.attrib.get("Departamento", "") if nomina_receptor is not None else "",
        }

        percepciones = nomina.find('nomina12:Percepciones', NS)
        datos["percepciones"] = []
        if percepciones is not None:
            for p in percepciones.findall('nomina12:Percepcion', NS):
                datos["percepciones"].append({
                    "pClave": p.attrib.get("Clave", ""),
                    "pConcepto": p.attrib.get("Concepto", ""),
                    "pImporte_exento": p.attrib.get("ImporteExento", ""),
                    "pImporte_gravado": p.attrib.get("ImporteGravado", ""),
                    "pTipo_percepcion": p.attrib.get("TipoPercepcion", ""),
                })

        deducciones = nomina.find('nomina12:Deducciones', NS)
        datos["deducciones"] = []
        if deducciones is not None:
            # Extraer los totales generales de deducciones
            datos["totales_deducciones"] = {
                "toTotal_Otras_Deducciones": deducciones.attrib.get("TotalOtrasDeducciones", ""),
                "TotalImpuestosRetenidos": deducciones.attrib.get("TotalImpuestosRetenidos", "")
            }
            for d in deducciones.findall('nomina12:Deduccion', NS):
                datos["deducciones"].append({
                    "dClabe": d.attrib.get("Clave", ""),
                    "dConcepto": d.attrib.get("Concepto", ""),
                    "dImporte": d.attrib.get("Importe", ""),
                    "dTipo_deduccion": d.attrib.get("TipoDeduccion", ""),
                })

        otros_pagos = nomina.find('nomina12:OtrosPagos', NS)
        datos["otros_pagos"] = []
        if otros_pagos is not None:
            for o in otros_pagos.findall('nomina12:OtroPago', NS):
                datos["otros_pagos"].append({
                    "oClave": o.attrib.get("Clave", ""),
                    "oConcepto": o.attrib.get("Concepto", ""),
                    "oImporte": o.attrib.get("Importe", ""),
                    "oTipo_pago": o.attrib.get("TipoOtroPago", ""),
                })

        incapacidades = nomina.find('nomina12:Incapacidades', NS)
        datos["incapacidades"] = []
        if incapacidades is not None:
            for i in incapacidades.findall('nomina12:Incapacidad', NS):
                datos["incapacidades"].append({
                    "icDias_incapacidad": i.attrib.get("DiasIncapacidad", ""),
                    "icImporte_Monetario": i.attrib.get("ImporteMonetario", ""),
                    "icTipo_Incapacidad": i.attrib.get("TipoIncapacidad", ""),
                })


        subcontratacion = nomina_receptor.findall('nomina12:SubContratacion', NS)
        datos["subcontratacion"] = []
        if subcontratacion is not None:
            for s in subcontratacion:
                datos["subcontratacion"].append({
                    "suRFC": s.attrib.get("RfcLabora", ""),
                    "suPorcentajeTiempo": s.attrib.get("PorcentajeTiempo", ""),
                })

        return datos

    else:
        raise Exception(f"Tipo de comprobante no soportado: {tipo_comprobante}")

    
def GenerarQR(foliofiscal,emisor,receptor):
    url = (
        "https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx"
        f"?id={foliofiscal}&re={emisor}&rr={receptor}&tt=1368.00&fe=UGaKZg=="
    )
    qr = qrcode.make(url)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return image_base64

@login_required(login_url="/mi-admin/login/")
def getPDF(request, id, tipo):
    # 1. Obtener el comprobante para saber el tipo
    comprobante = get_object_or_404(ComprobanteEmitido, pk=id)
    
    # Mapear tipo de comprobante, según cómo lo guardas en la base (ajusta si tus nombres difieren)
    # Por ejemplo, si comprobante.tipo == "Nómina" => "N", etc.
    TIPO_MAP = {
        "Factura electrónica": "I",  # Ingreso
        "Ingreso": "I",
        "Egreso": "E",
        "Nómina": "N",
        "Pago": "P",
    }
    # Detectar el tipo_comprobante (por campo .tipo o el que uses)
    tipo_nombre = comprobante.tipo  # Asegúrate que este campo tenga valores como "Nómina", "Ingreso", etc.
    tipo_comprobante = TIPO_MAP.get(tipo_nombre, "I")  # Default a "I" si no se encuentra

    # 2. Buscar la plantilla del usuario y tipo comprobante (ajusta idUserCFDI según tu lógica)
    print("Buscando plantilla para usuario:", comprobante.idUserCFDI)
    print("Tipo comprobante buscado:", tipo_comprobante)
    print("Plantillas encontradas:", Plantilla.objects.filter(tipo_comprobante=tipo_comprobante).values_list("id", "name", "idUserCFDI", "status","tipo_comprobante"))
    plantillas = Plantilla.objects.filter(
    idUserCFDI=comprobante.idUserCFDI,
    tipo_comprobante=tipo_comprobante,
    status="draft",  # Solo plantillas publicadas
    ).order_by('-created_at')

    if plantillas.count() == 0:
        return JsonResponse({"error": f"No hay plantillas para este tipo de comprobante: {tipo_comprobante}"}, status=404)
    elif plantillas.count() > 1:
        print(f"ADVERTENCIA: Hay {plantillas.count()} plantillas encontradas. Se usará la más reciente.")

    plantilla = plantillas.first()

    if not plantilla:
        return JsonResponse({"error": f"No hay plantillas disponibles para este tipo de comprobante: {tipo_comprobante}"}, status=404)

    html = plantilla.html
    css_personalizado = plantilla.css or ""
    imagen_base64 = ""
    img_QR = ""

    # 3. Obtener datos del comprobante
    datos = datos_factura_timbrada(id)  # SIEMPRE usa datos_factura_timbrada

    if tipo_comprobante != 'I':  # Si solo quieres QR para otros tipos
        foliofiscal = datos['factura']['fFolio_fiscal']
        rfc_emisor = datos['emisor']['eRFC']
        rfc_receptor = datos['receptor']['rRFC']
        img_QR = GenerarQR(foliofiscal, rfc_emisor, rfc_receptor)
        html = reemplazar_src_por_base64(html, img_QR, "img-fluid")

    # 4. Leer estilos base
    bootstrap_path = os.path.join(settings.BASE_DIR, "cfdi/static/librerias/styles_grapesjs.css")
    with open(bootstrap_path, 'r', encoding='utf-8') as f:
        bootstrap_css = f.read()

    # 5. Imagen plantilla a base64
    if plantilla.imagen and plantilla.imagen.name:
        ruta_imagen = os.path.join(settings.MEDIA_ROOT, plantilla.imagen.name)
        if os.path.exists(ruta_imagen):
            imagen_base64 = imagen_a_base64(ruta_imagen)
            html = reemplazar_src_por_base64(html, imagen_base64, "imagen-subida")

    # 6. Renderizar plantilla
    template = Template(html)
    context = Context({
        "CFDI": datos,
        "CSS": f"{bootstrap_css}\n{css_personalizado}",
        "IMAGEN_BASE64": imagen_base64
    })
    html_renderizado = template.render(context)

    # 7. Retornar vista para previsualización
    return render(request, "cfdi/editorPDF.html", {
        "html_renderizado": html_renderizado,
        "css_renderizado": f"{bootstrap_css}\n{css_personalizado}",
        "cfdi": datos,
        "id": id,
        "tipo": tipo
    })


# #Imprimir el pdf de la factura
# def imprimirPDF(request, id, tipo):
#     inicio = time.time()
#     id_plantilla = obtener_plantilla_base()
#     if id_plantilla == -1:
#         return JsonResponse({"error": "No hay plantillas disponibles"}, status=404)
    
#     plantilla = Plantilla.objects.get(id=id_plantilla)
#     html = plantilla.html
#     css = plantilla.css
#     img_QR = ""

#     if tipo == 1:
#         datos = datos_factura(id)
#     else:
#         datos = datos_factura_timbrada(id)
#         foliofiscal = datos['factura']['fFolio_fiscal']
#         Rfc_emisor = datos['emisor']['eRFC']
#         Rfc_receptor = datos['receptor']['rRFC']
#         img_QR = GenerarQR(foliofiscal, Rfc_emisor, Rfc_receptor)
#         html = reemplazar_src_por_base64(html, img_QR, "img-fluid")

#     # Carga del archivo styles_grapesjs.css
#     bootstrap_path = os.path.join(settings.BASE_DIR, "cfdi/static/librerias/styles_grapesjs.css")
#     with open(bootstrap_path, 'r', encoding='utf-8') as f:
#         bootstrap_css = f.read()

#     # Convierte la imagen de la plantilla a base64 si existe
#     imagen_base64 = ""
#     if plantilla.imagen and plantilla.imagen.name:
#         ruta_imagen = os.path.join(settings.MEDIA_ROOT, plantilla.imagen.name)
#         if os.path.exists(ruta_imagen):
#             imagen_base64 = imagen_a_base64(ruta_imagen)

#     html = reemplazar_src_por_base64(html, imagen_base64, "imagen-subida")

#     # Renderiza HTML con contexto
#     template = Template(html)
#     context = Context({
#         "CFDI": datos,
#         "CSS": f"{bootstrap_css}\n{css}",
#         "IMAGEN_BASE64": imagen_base64,
#         "imagen": img_QR
#     })
#     html_renderizado = template.render(context)

#     # Estilos extra para PDF
#     css_extra = """
#     @page {
#         size: A4;
#         margin: 5mm;
#         border: none;
#     }
#     body {
#         margin: 0;
#         padding: 0;
#     }
#     """

#     # Genera el PDF aplicando todos los estilos correctamente
#     pdf = HTML(string=html_renderizado).write_pdf(stylesheets=[
#         CSS(string=css_extra),
#         CSS(string=bootstrap_css),  # ✅ Estilos de styles_grapesjs.css aplicados aquí
#         CSS(string=css)             # ✅ Estilos propios de la plantilla
#     ])

#     fin = time.time()
#     duracion = fin - inicio
#     print(f"Tiempo para generar el PDF: {duracion:.2f} segundos")

#     response = HttpResponse(pdf, content_type="application/pdf")
#     response["Content-Disposition"] = f'attachment; filename="factura_{id}.pdf"'
#     return response


def imprimirPDF(request, id, tipo):
    import time
    inicio = time.time()

    # 1. Obtener el comprobante para saber el tipo
    comprobante = get_object_or_404(ComprobanteEmitido, pk=id)
    
    # Mapear tipo de comprobante, según cómo lo guardas en la base (ajusta si tus nombres difieren)
    TIPO_MAP = {
        "Ingreso": "I",
        "Egreso": "E",
        "Nómina": "N",
        "Pago": "P",
    }
    tipo_nombre = comprobante.tipo  # Ajusta si tu campo se llama diferente
    tipo_comprobante = TIPO_MAP.get(tipo_nombre, "I")  # Default a "I"
    
    # 2. Buscar la plantilla del usuario y tipo comprobante
    plantillas = Plantilla.objects.filter(
        idUserCFDI=comprobante.idUserCFDI,
        tipo_comprobante=tipo_comprobante,
        status="draft",  # O "publicada", según tu lógica
    ).order_by('-created_at')

    if plantillas.count() == 0:
        return JsonResponse({"error": f"No hay plantillas para este tipo de comprobante: {tipo_comprobante}"}, status=404)
    elif plantillas.count() > 1:
        print(f"ADVERTENCIA: Hay {plantillas.count()} plantillas encontradas. Se usará la más reciente.")

    plantilla = plantillas.first()

    html = plantilla.html
    css = plantilla.css or ""
    img_QR = ""

    # 3. Obtener datos del comprobante
    if tipo_comprobante == "I" and int(tipo) == 1:
        datos = datos_factura(id)
    else:
        datos = datos_factura_timbrada(id)
        foliofiscal = datos['factura']['fFolio_fiscal']
        rfc_emisor = datos['emisor']['eRFC']
        rfc_receptor = datos['receptor']['rRFC']
        img_QR = GenerarQR(foliofiscal, rfc_emisor, rfc_receptor)
        html = reemplazar_src_por_base64(html, img_QR, "img-fluid")

    # 4. Carga del archivo styles_grapesjs.css
    bootstrap_path = os.path.join(settings.BASE_DIR, "cfdi/static/librerias/styles_grapesjs.css")
    with open(bootstrap_path, 'r', encoding='utf-8') as f:
        bootstrap_css = f.read()

    # 5. Convierte la imagen de la plantilla a base64 si existe
    imagen_base64 = ""
    if plantilla.imagen and plantilla.imagen.name:
        ruta_imagen = os.path.join(settings.MEDIA_ROOT, plantilla.imagen.name)
        if os.path.exists(ruta_imagen):
            imagen_base64 = imagen_a_base64(ruta_imagen)
            html = reemplazar_src_por_base64(html, imagen_base64, "imagen-subida")

    # 6. Renderiza HTML con contexto
    template = Template(html)
    context = Context({
        "CFDI": datos,
        "CSS": f"{bootstrap_css}\n{css}",
        "IMAGEN_BASE64": imagen_base64,
        "imagen": img_QR
    })
    html_renderizado = template.render(context)

    # 7. Estilos extra para PDF
    css_extra = """
    @page {
        size: A4;
        margin: 5mm;
        border: none;
    }
    body {
        margin: 0;
        padding: 0;
    }
    """

    # 8. Genera el PDF aplicando todos los estilos correctamente
    pdf = HTML(string=html_renderizado).write_pdf(stylesheets=[
        CSS(string=css_extra),
        CSS(string=bootstrap_css),
        CSS(string=css)
    ])

    fin = time.time()
    duracion = fin - inicio
    print(f"Tiempo para generar el PDF: {duracion:.2f} segundos")

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="factura_{id}.pdf"'
    return response
#Elegir la plantilla para imprimir
def ElegirPlantilla(request):
    if request.method == 'POST':
        plantilla_id = request.POST['id']

        plantillas = Plantilla.objects.all()
        if not plantillas.exists():
            return JsonResponse({"success": False, "error": "No hay plantillas disponibles."})

        plantilla_imprimir = plantillas.filter(status='published').first()
        if plantilla_imprimir and plantilla_imprimir.id == plantilla_id:
            return JsonResponse({"success": True, "mensaje": "La plantilla ya está seleccionada para impresión."})
        
        if plantilla_imprimir:
            plantilla_imprimir.status = 'draft'
            plantilla_imprimir.save()

        nueva_plantilla = Plantilla.objects.get(id=plantilla_id)
        nueva_plantilla.status = 'published'
        nueva_plantilla.save()
        return JsonResponse({"success": True, "mensaje": "La "+nueva_plantilla.name+" ahora ese la plantilla por defecto para imprimir CFDI"})
    
    return JsonResponse({"success": False, "error": "Método no permitido."})

# FUNCION PARA CONVERTIR IMAGENES A BASE64
def imagen_a_base64(path_absoluto):
    with open(path_absoluto, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')
# FUNCION PARA REMPLAZAR SRC DE IMAGENES EN HTML
def reemplazar_src_por_base64(html, imagen_base64, clase, mime_type="image/png"):
    """
    Reemplaza el atributo src de las imágenes con la clase especificada por una imagen en base64.

    Args:
        html (str): El HTML original.
        imagen_base64 (str): La cadena base64 de la imagen.
        clase (str): Nombre de la clase de las imágenes a reemplazar.
        mime_type (str): El tipo MIME de la imagen (por defecto image/png).

    Returns:
        str: HTML modificado con las imágenes reemplazadas.
    """
    base64_src = f'data:{mime_type};base64,{imagen_base64}'

    def reemplazo(match):
        tag = match.group(0)
        pattern = rf'class=["\'][^"\']*\b{re.escape(clase)}\b[^"\']*["\']'
        if re.search(pattern, tag):
            return re.sub(
                r'src=["\'][^"\']*["\']',
                f'src="{base64_src}"',
                tag
            )
        return tag

    html_modificado = re.sub(
        r'<img[^>]*>',
        reemplazo,
        html,
        flags=re.IGNORECASE
    )
    return html_modificado
    

##############################################################################


# Create your views here.
def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'cfdi/contact.html',
        {
            'title':'Contact',
            'message':'Your contact page.',
            'year': datetime.datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'cfdi/about.html',
        {
            'title':'About',
            'message':'Your application description page.',
            'year': datetime.datetime.now().year,
        }
    )

def home(request):
    """Renderiza la página de inicio."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'cfdi/index.html',
        {
            'title': 'Página de inicio',
            'year': datetime.datetime.now().year,
        }
    )

def errorLinkreutilizado(request):
    """Renderiza la página de error en la activacion."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'cfdi/link_reutilizado.html',
        {
            'title': 'Página de envio de activacion',
            'year': datetime.datetime.now().year,
        }
    )

# partes para el registro *************************************************************************************************************************************


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        
        # Verificar si los campos de contraseña están vacíos
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        email = request.POST.get('email')
        
        # Expresión regular para verificar que la contraseña tenga al menos 8 caracteres y al menos un número o símbolo
        password_regex = re.compile(r'^(?=.*[0-9!@#$%^&*])(?=.{8,})')

        if not password1 or not password2:
            form.add_error('password1', 'Los campos de contraseña no pueden estar vacíos.')
        elif not email:
            form.add_error('email', 'El campo de correo electrónico no puede estar vacío.')
        elif not password_regex.match(password1):
            form.add_error('password1', 'La contraseña debe tener al menos 8 caracteres y contener al menos un número o símbolo.')
        elif form.is_valid():
            if User.objects.filter(email=email).exists():  # Verificar si el correo electrónico ya existe
                form.add_error('email', 'Este correo electrónico ya está registrado.')  # Agregar error al formulario
            else:
                user = form.save(commit=False)
                user.is_active = False  # Desactivar al usuario hasta que haga clic en el enlace de activación
                user.is_staff = False
                
                # Generar un username único basado en el email
                user.username = generate_unique_username(email)

                # Guardar el usuario
                user.save()
                
                # Agregar el usuario al grupo 'cfdi'
                #group = Group.objects.get(name='cfdi')
                group = Group.objects.filter(name__in=['cfdi', 'CFDI'])
                user.groups.add(*group)

                # Enviar correo electrónico de activación
                send_activation_email(request, user)

                return redirect(reverse_lazy('cfdi:activacionenviada'))  # Redirigir a una página de éxito después de registrar al usuario
    else:
        form = CustomUserCreationForm()
    return render(request, 'cfdi/register.html', {'form': form})



def generate_unique_username(email):
    base_username = email.split('@')[0]
    username = base_username
    counter = 1
    while User.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1
    return username

def activate_account(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if not user.is_active:  # Verificar si el usuario ya está activo
            # Activar la cuenta del usuario
            user.is_active = True
            user.is_staff = True  # Asegurarse de que is_staff este al activar la cuenta
            user.save()

            free_plan = Plan.objects.get(nombre='FREE')
            cfdi_service = Service.objects.get(nombre='CFDI') 

            idServiceP = Service_Plan.objects.get(
                service=cfdi_service,
                plan=free_plan,
                isActive=True
            )
  
            # Crear el registro en User_Service con aceptarTerminos=True
            user_service = User_Service.objects.create(
            idUser=user,
            idPlan=free_plan,
            idService=cfdi_service,
            date_cutoff=datetime.date.today() + datetime.timedelta(days=30),
            idServicePlan=idServiceP,
            aceptarTerminos=True
            )
            
            cfdi_user = UsersCFDI.objects.create(
            idUserCFDI=user,
            idUserServicePlan_id=user_service
            )
            
            # Generar token inicial SOLO una vez
            cfdi_user.generar_token_inicial()

            

            # Verificar si el usuario es parte del staff
            if 'is_staff' in request.POST and request.POST['is_staff'] == 'on':
                user.is_staff = True
                user.save()

                # Asignar permisos de CRUD para todos los modelos de la app `cfdi`
                cfdi_models = apps.get_app_config('cfdi').get_models()
                for model in cfdi_models:
                    content_type = ContentType.objects.get_for_model(model)
                    permissions = [
                        f'add_{model._meta.model_name}',
                        f'change_{model._meta.model_name}',
                        f'delete_{model._meta.model_name}',
                        f'view_{model._meta.model_name}',
                    ]
                    for perm in permissions:
                        try:
                            permission = Permission.objects.get(codename=perm, content_type=content_type)
                            user.user_permissions.add(permission)
                        except Permission.DoesNotExist:
                            continue  # En caso de que no exista algún permiso, lo ignora

            return redirect(reverse_lazy('cfdi:activacionbien'))
        else:
            # Usuario ya activado, redirigir a página de activación inválida
            return redirect(reverse_lazy('cfdi:activacionmal'))
    else:
        # Token inválido o usuario no encontrado, redirigir a página de activación inválida
        return redirect(reverse_lazy('cfdi:errorLinkreutilizado'))


    
def send_activation_email(request,user):
    
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    
    # Usar el nombre de la aplicación 'cfdi' en el reverse
    activation_link = reverse('cfdi:activate_account', kwargs={'uidb64': uidb64, 'token': token})
    
    # Concatenar el enlace base de tu dominio
    current_host = request.get_host()
    activation_link = f"http://{current_host}{activation_link}"
    
    email_subject = 'Activa tu cuenta'
    email_body = f'Hola {user.email}, Por favor, utiliza el siguiente enlace para activar tu cuenta: {activation_link}'
    send_mail(email_subject, email_body, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)

def activacionBien(request):
    """Renderiza la página de activacion."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'cfdi/activation_success.html',
        {
            'title': 'Página de confirmacion',
            'year': datetime.datetime.now().year,
        }
    )


def activacionMal(request):
    """Renderiza la página de error en la activacion."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'cfdi/activation_failure.html',
        {
            'title': 'Página de error en la activacion',
            'year': datetime.datetime.now().year,
        }
    )

def activacionMalCorreo(request):
    """Renderiza la página de error en el correo."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'cfdi/activation_failure_correo.html',
        {
            'title': 'Página de error en el correo',
            'year': datetime.datetime.now().year,
        }
    )


def activacionMalContrasena(request):
    """Renderiza la página de error en la contrasena."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'cfdi/activation_failure_password.html',
        {
            'title': 'Página de error en la contrasena',
            'year': datetime.datetime.now().year,
        }
    )

def activacionMalUsuarionoregistrado(request):
    """Renderiza la página de error usuario no registrado."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'cfdi/activation_failure_usuarioRegistrado.html',
        {
            'title': 'Página de error usuario no registrado',
            'year': datetime.datetime.now().year,
        }
    )

def activacionenviada(request):
    """Renderiza la página de envío de activación."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'cfdi/activation_sent.html',
        {
            'title': 'Página de envío de activación',
            'year': datetime.datetime.now().year,
        }
    )

#************************************************************************************************************************************

#para inicar sesion*****************************************************************************************************

#METODO UTILIZANDO LAS FORMAS ABSTRASCTAS
# DDD Y REPOSITORY VINCULADO CON EL DE sesioniniciada(request)
def iniciarsesionpartial(request):
    """Renderiza la página de inicio de sesión."""
    assert isinstance(request, HttpRequest)
    if request.method == 'POST':
        identifier = request.POST['identifier']  # Puede ser username o email
        password = request.POST['password']

        auth_adapter = CustomAuthAdapter()
        user = auth_adapter.authenticate(identifier, password)  # Autenticar al usuario

        if user:
            # Verificar si el usuario está activo
            if user.is_active:
                # Crear sesión de usuario en Django.
                login(request, user)
                
                # Verificar si el usuario pertenece al grupo "cfdi"
                if user.groups.filter(name='cfdi').exists():
                    return redirect(reverse_lazy('cfdi:iniciarsesionpartial'))  # Redirige a la página de inicio
                else:
                    return redirect(reverse_lazy('cfdi:activacionmalusuarionoregistrado'))  # Redirige si no pertenece al grupo "cfdi"
            else:
                return redirect(reverse_lazy('cfdi:activacionmal'))  # Redirige si no está activo
        else:
            # Verificar si el correo es incorrecto
            if not auth_adapter.email_exists(identifier):
                return redirect(reverse_lazy('cfdi:activacionmalcorreo'))  # Redirige si el correo es incorrecto
            else:
                # Usuario no encontrado o contraseña incorrecta
                return redirect(reverse_lazy('cfdi:activacionmalcontrasena'))  # Redirige si la contraseña es incorrecta

    # Si no es un método POST o si la autenticación falla, renderiza la plantilla de inicio de sesión.
    return render(
        request,
        'cfdi/index.html',  # Cambia a 'iniciarsesionpartial.html' si es necesario
        {
            'title': 'Iniciar Sesión',
            'year': datetime.datetime.now(),
        }
    )


def sesioniniciada(request):
    if request.method == 'POST':
        identifier = request.POST['identifier']  # Puede ser username o email
        password = request.POST['password']
        auth_adapter = CustomAuthAdapter()
        user = auth_adapter.authenticate(identifier, password)
        
        if user:
            # Verificar si el usuario está activo
            if user.is_active:
                # Iniciar sesión y verificar el grupo
                login(request, user)
                
                # Verificar si el usuario pertenece al grupo "cfdi"
                if user.groups.filter(name='cfdi').exists():
                    return redirect(reverse_lazy('cfdi:iniciarsesionpartial'))  # Redirige a la página de inicio
        
            else:
                return redirect(reverse_lazy('cfdi:activacionmal'))  # Redirige si no está activo
        else:
            # Verificar si el identificador (email o username) es incorrecto
            if not auth_adapter.email_exists(identifier):
                return redirect(reverse_lazy('cfdi:activacionmalcorreo'))  # Redirige si el correo es incorrecto
            else:
                # Usuario no encontrado o contraseña incorrecta
                return redirect(reverse_lazy('cfdi:activacionmalcontrasena'))  # Redirige si la contraseña es incorrecta

    return render(
        request,
        'cfdi/index.html',  # Cambia a 'iniciarsesionpartial.html' si es necesario
        {
            'title': 'Iniciar Sesión',
            'year': timezone.now().year,
        }
    )

def cerrarsesion(request):
    """Cierra la sesión del usuario y redirige a la página de inicio."""
    assert isinstance(request, HttpRequest)
    logout(request)  # Cierra la sesión del usuario
    return redirect(reverse_lazy('cfdi:inicio'))


#################################################################################
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from cfdi.forms import SendEmailResetPasswordForm, ResetPasswordForm2
import hashlib
import random
from django.contrib.auth import update_session_auth_hash
#el httpresponse
from django.http import HttpRequest, HttpResponse


def generate_unique_token_for_user(user):
    # Genera un token único para el usuario
    return hashlib.sha256(f'{user.pk}{user.email}{random.random()}{timezone.now()}'.encode()).hexdigest()


def send_resetPassword_email(request,user):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    resetPassword_link = reverse('cfdi:resetPassword_account', kwargs={'uidb64': uidb64, 'token': token})
    current_host = request.get_host()
    resetPassword_link = f"http://{current_host}{resetPassword_link}"
    email_subject = 'Restablece tu cuenta'
    email_body = f'Hola {user.username}, Por favor, utiliza el siguiente enlace para restablece la clave tu cuenta: {resetPassword_link}'
    send_mail(email_subject, email_body, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)




def restablecer_password(request):
    form = SendEmailResetPasswordForm()  # Movido fuera del bloque 'else'
    if request.method == 'POST':
        form = SendEmailResetPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = None

            if user is not None:
                # Generar token
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                
                # Enviar correo con el enlace para restablecer contraseña
                resetPassword_link = reverse('cfdi:resetPassword_account', kwargs={'uidb64': uidb64, 'token': token})
                current_host = request.get_host()
                resetPassword_link = f"http://{current_host}{resetPassword_link}"
                email_subject = 'Restablece tu contraseña'
                email_body = f'Hola {user.email}, Por favor, utiliza el siguiente enlace para restablecer tu contraseña: {resetPassword_link}'
                send_mail(email_subject, email_body, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
                return redirect(reverse_lazy('cfdi:reseteo_enviada'))

                
            else:
                form.add_error('email', 'Este correo electrónico no está registrado.')
    return render(request, 'cfdi/reseteo_password.html', {'form': form})



def resetPassword_account(request, uidb64, token):
    if request.method == 'POST':
        form = ResetPasswordForm2(request.POST)

        # Verificar si los campos son válidos primero
        password = form.cleaned_data.get('password') if form.is_valid() else ''
        password2 = form.cleaned_data.get('password2') if form.is_valid() else ''

        # Expresión regular para verificar que la contraseña tenga al menos 8 caracteres y contenga al menos un número o símbolo
        password_regex = re.compile(r'^(?=.*[0-9!@#$%^&*])(?=.{8,})')

        # Verificar si las contraseñas están vacías
        if not password or not password2:
            form.add_error('password', 'Los campos de contraseña no pueden estar vacíos.')
        # Verificar si las contraseñas coinciden
        elif password != password2:
            form.add_error('password2', 'Las contraseñas no coinciden.')
        # Verificar si la contraseña cumple con el formato
        elif not password_regex.match(password):
            form.add_error('password', 'La contraseña debe tener al menos 8 caracteres y contener al menos un número o símbolo.')
        else:
            try:
                uid = force_text(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                user = None

            if user is not None and default_token_generator.check_token(user, token):
                # Resetear la contraseña del usuario
                user.set_password(password)
                user.save()
                update_session_auth_hash(request, user)
                return redirect(reverse_lazy('cfdi:reseteobien'))

            return redirect(reverse_lazy('cfdi:reseteomal'))

    else:
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            form = ResetPasswordForm2()
            return render(request, 'cfdi/form_reset_password.html', {'form': form})
        else:
            return redirect(reverse_lazy('cfdi:reseteomal'))

    return render(request, 'cfdi/form_reset_password.html', {'form': form})




def resteoMal(request):
    """Renderiza la página de error en la activacion."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'cfdi/reseteomal.html',
        {
            'title': 'Página de error en restear contraseña',
            'year': datetime.datetime.now().year,
        }
    )


def reseteoBien(request):
    """Renderiza la página de error en la activacion."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'cfdi/reseteobien.html',
        {
            'title': 'Página de restear contraseña',
            'year': datetime.datetime.now().year,
        }
    )

def reseteoEnviado(request):
    """Renderiza la página de error en la activacion."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'cfdi/reseteoEnviado.html',
        {
            'title': 'Página de envio de correo para resetar contraseña',
            'year': datetime.datetime.now().year,
        }
    )
    
    



#tabla

# def informacion_fiscal_list(request):
#     informacion_fiscal = InformacionFiscal.objects.all()
#     return render(request, 'negocios/informacion_fiscal_list.html', {'informacion_fiscal': informacion_fiscal})

# def agregar_informacion_fiscal(request):
#     if request.method == 'POST':
#         form = InformacionFiscalForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             return redirect('cfdi:informacion_fiscal_list')
#     else:
#         form = InformacionFiscalForm()
#     return render(request, 'negocios/negocios.html', {'form': form})


# # Vista para editar la información fiscal
# def editar_informacion_fiscal(request, pk):
#     info_fiscal = get_object_or_404(InformacionFiscal, pk=pk)
#     if request.method == 'POST':
#         form = InformacionFiscalForm(request.POST, instance=info_fiscal)
#         if form.is_valid():
#             form.save()
#             return redirect(reverse_lazy('cfdi:informacion_fiscal_list'))
#     else:
#         form = InformacionFiscalForm(instance=info_fiscal)
#     return render(request, 'negocios/plantillas_acciones/editar_informacion_fiscal.html', {'form': form})

# # Vista para borrar la información fiscal
# def borrar_informacion_fiscal(request, pk):
#     info_fiscal = get_object_or_404(InformacionFiscal, pk=pk)
#     if request.method == 'POST':
#         info_fiscal.delete()
#         return redirect(reverse_lazy('cfdi:informacion_fiscal_list'))
#     else:
#         form = InformacionFiscalForm(instance=info_fiscal)
#     return render(request, 'negocios/plantillas_acciones/borrar_informacion_fiscal.html', {'form': form})

# # Vista para activar un registro de información fiscal
# def activar_informacion_fiscal(request, pk):
#     info_fiscal = get_object_or_404(InformacionFiscal, pk=pk)
#     # Cambiar el estado de confirmacion de datos a True
#     info_fiscal.confirmar_datos_cfdi = True
#     info_fiscal.save()
#     return redirect(reverse_lazy('cfdi:informacion_fiscal_list'))

# # Vista para subir una imagen a la información fiscal
# def subir_imagen_informacion_fiscal(request, pk):
#     info_fiscal = get_object_or_404(InformacionFiscal, pk=pk)
#     if request.method == 'POST' and request.FILES['imagen']:
#         info_fiscal.imagen = request.FILES['imagen']
#         info_fiscal.save()
#         return redirect(reverse_lazy('cfdi:informacion_fiscal_list'))
#     return render(request, 'negocios/plantillas_acciones/subir_imagen_informacion_fiscal.html', {'info_fiscal': info_fiscal})




# Vista para activar un registro de información fiscal del usuario logueado
@login_required
@require_POST
def activar_informacion_fiscal(request, pk):
    user_cfdi = UsersCFDI.objects.get(idUserCFDI=request.user)
    info_fiscal = get_object_or_404(InformacionFiscal, pk=pk, idUserCFDI=user_cfdi)

    info_fiscal.activo = not info_fiscal.activo
    if info_fiscal.activo:
        info_fiscal.confirmar_datos_cfdi = True
    info_fiscal.save()
    
    # Redirige a la página anterior (la misma desde donde se hizo la petición)
    return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))




# Vista para subir una imagen a la información fiscal del usuario logueado
@login_required
def subir_imagen_informacion_fiscal(request, pk):
    info_fiscal = get_object_or_404(InformacionFiscal, pk=pk, user=request.user)
    if request.method == 'POST' and request.FILES.get('imagen'):
        info_fiscal.imagen = request.FILES['imagen']
        info_fiscal.save()
        return redirect(reverse_lazy('cfdi:informacion_fiscal_list'))
    return render(request, 'negocios/plantillas_acciones/subir_imagen_informacion_fiscal.html', {'info_fiscal': info_fiscal})


# view generar XML
# def obtener_datos_factura(id):
#         # Obtener la factura
#         factura = FacturaElectronica.objects.get(id=id)
#         if not factura:
#             print('No se encontró la factura')

#         # Obtener el receptor asociado
#         receptor_model = factura.receptores.first()  # Usar el primer receptor asociado
        
#         # Obtener el receptor asociado
#         formaPago_model = factura.InformacionPago.first()  # Usar el primer receptor asociado

#         # Obtener el régimen fiscal del receptor
#         regimen_fiscal_receptor = receptor_model.Regimen_fiscal.first()

#         # Crear objeto Receptor
#         receptor = cfdi40.Receptor(
#             rfc=receptor_model.Rfc,
#             nombre=receptor_model.Razon_social,
#             uso_cfdi=receptor_model.Usocfdi.c_UsoCFDI,
#             domicilio_fiscal_receptor=receptor_model.Codigo_postal,
#             regimen_fiscal_receptor=regimen_fiscal_receptor.c_RegimenFiscal,
#         )

#         # Obtener datos del emisor
#         informacion_fiscal = factura.informacion_fiscal

#         certificado = informacion_fiscal.user.certificados.first()

#         # Leer los datos del certificado
#         signer = Signer.load(
#             certificate=certificado.archivo_certificado.read(),
#             key=certificado.clave_privada.read(),
#             password=certificado.contrasena,
#         )

#         regimen_fiscal_obj = informacion_fiscal.regimen_fiscal.first()
#         # Crear objeto Emisor
#         emisor = cfdi40.Emisor(
#             rfc=signer.rfc,
#             nombre=signer.legal_name,
#             regimen_fiscal=regimen_fiscal_obj.c_RegimenFiscal,
#         )

        
#         # Crear los conceptos 
#         conceptos = []
#         for concepto_model in factura.Conceptos.all():
#             print('clave unidad',concepto_model.clave_unidad)
#             conceptos.append(
#                 cfdi40.Concepto(
#                     clave_prod_serv=concepto_model.claveprodserv.c_ClaveProdServ,
#                     cantidad=Decimal(concepto_model.cantidad),
#                     clave_unidad=concepto_model.clave_unidad.c_ClaveUnidad,
#                     descripcion=concepto_model.descripcion,
#                     valor_unitario=Decimal(concepto_model.valor_unitario),
#                     impuestos=cfdi40.Impuestos(),
#                 )
#             )

#         print('forma de pago',formaPago_model.Metodopago.c_MetodoPago)
#         # Crear el comprobante
#         comprobante = cfdi40.Comprobante(
#             emisor=emisor,
#             lugar_expedicion=informacion_fiscal.codigo_postal,
#             receptor=receptor,
#             metodo_pago=formaPago_model.Metodopago.c_MetodoPago,  # Ejemplo de método de pago
#             forma_pago=formaPago_model.Formapago.c_FormaPago,  # Ejemplo de forma de pago
#             serie="A",
#             folio="12345",
#             conceptos=conceptos,
#         )

#         # Firmar el comprobante
#         comprobante.sign(signer)
#         # xml_content = comprobante.xml_bytes(pretty_print=True, validate=True).decode("utf-8")

#         # # Devolver el XML como respuesta HTTP
#         # response = HttpResponse(xml_content, content_type="application/xml")
#         # response["Content-Disposition"] = f'attachment; filename="factura_{pk}.xml"'
#         # return response
#         comprobante = comprobante.process()
#         return comprobante

# factura con impuestos
# def obtener_datos_factura(id):
#     # Obtener el comprobante (antes FacturaElectronica)
#     comprobante_model = Comprobante.objects.get(id=id)
#     print('comprobante_model', comprobante_model)
#     if not comprobante_model:
#         print('No se encontró el comprobante')
#         return None

#     # Receptor
#     receptor_model = Receptor.objects.filter(comprobante=comprobante_model).first()
#     if not receptor_model:
#         print('No se encontró el receptor')
#         return None

#     receptor = cfdi40.Receptor(
#         rfc=receptor_model.rfc,
#         nombre=receptor_model.nombre,
#         uso_cfdi=receptor_model.c_UsoCFDI.c_UsoCFDI,
#         domicilio_fiscal_receptor=str(receptor_model.c_DomicilioFiscalReceptor.c_CodigoPostal),
#         regimen_fiscal_receptor=str(receptor_model.c_RegimenFiscalReceptor.c_RegimenFiscal)
#     )

#     # Información del emisor
#     emisor_model = Emisor.objects.filter(comprobante=comprobante_model).first()
#     if not emisor_model:
#         print('No se encontró el emisor')
#         return None

#     # Obtener certificado desde la información fiscal
#     info_fiscal = comprobante_model.informacionFiscal
#     certificado = CertificadoSelloDigital.objects.filter(informacionFiscal=info_fiscal, estado=True).order_by('-defecto', '-vigencia').first()
#     print('informacion_fiscal', info_fiscal)
#     print('certificado', certificado)

#     signer = Signer.load(
#         certificate=certificado.archivo_certificado.read(),
#         key=certificado.clave_privada.read(),
#         password=certificado.contrasena,
#     )

#     emisor = cfdi40.Emisor(
#         rfc=signer.rfc,
#         nombre=emisor_model.nombre,
#         regimen_fiscal=str(emisor_model.c_RegimenFiscal.c_RegimenFiscal)
#     )

#     # Crear conceptos con sus impuestos
#     conceptos = []
#     for concepto_model in comprobante_model.conceptos.all():
#         # Procesar impuestos del concepto
#         traslados_concepto = []
#         retenciones_concepto = []
        
#         for impuesto_model in concepto_model.impuestos.all():
#             if impuesto_model.tipo == 'Traslado':
#                 traslado = cfdi40.Traslado(
#                     base=Decimal(impuesto_model.base) if impuesto_model.base else Decimal(concepto_model.valorUnitario) * Decimal(concepto_model.cantidad),
#                     impuesto=impuesto_model.c_Impuesto.c_Impuesto,
#                     tipo_factor=impuesto_model.c_TipoFactor.c_TipoFactor,
#                     tasa_o_cuota=Decimal(impuesto_model.c_TasaOCuota.valor_maximo) if impuesto_model.c_TasaOCuota else None,
#                     importe=Decimal(impuesto_model.importe) if impuesto_model.importe else None
#                 )
#                 traslados_concepto.append(traslado)
                
#             elif impuesto_model.tipo == 'Retención':
#                 retencion = cfdi40.Retencion(
#                     base=Decimal(impuesto_model.base) if impuesto_model.base else Decimal(concepto_model.valorUnitario) * Decimal(concepto_model.cantidad),
#                     impuesto=impuesto_model.c_Impuesto.c_Impuesto,
#                     tipo_factor=impuesto_model.c_TipoFactor.c_TipoFactor,
#                     tasa_o_cuota=Decimal(impuesto_model.c_TasaOCuota.valor_maximo) if impuesto_model.c_TasaOCuota else None,
#                     importe=Decimal(impuesto_model.importe) if impuesto_model.importe else None
#                 )
#                 retenciones_concepto.append(retencion)
        
#         # Crear objeto de impuestos para el concepto
#         impuestos_concepto = None
#         if traslados_concepto or retenciones_concepto:
#             impuestos_concepto = cfdi40.Impuestos(
#                 traslados=traslados_concepto if traslados_concepto else None,
#                 retenciones=retenciones_concepto if retenciones_concepto else None
#             )
        
#         # Crear el concepto CFDI
#         concepto_cfdi = cfdi40.Concepto(
#             clave_prod_serv=concepto_model.c_ClaveProdServ.c_ClaveProdServ,
#             cantidad=Decimal(concepto_model.cantidad),
#             clave_unidad=concepto_model.c_ClaveUnidad.c_ClaveUnidad,
#             descripcion=concepto_model.descripcion,
#             valor_unitario=Decimal(concepto_model.valorUnitario),
#             unidad=concepto_model.unidad or "",
#             objeto_imp=concepto_model.c_ObjetoImp.c_ObjetoImp,
#             impuestos=impuestos_concepto
#         )
#         conceptos.append(concepto_cfdi)

#     # Crear el comprobante CFDI
#     cfdi = cfdi40.Comprobante(
#         emisor=emisor,
#         lugar_expedicion=str(58000),
#         receptor=receptor,
#         metodo_pago=comprobante_model.c_MetodoPago.c_MetodoPago if comprobante_model.c_MetodoPago else None,
#         forma_pago=comprobante_model.c_FormaPago.c_FormaPago if comprobante_model.c_FormaPago else None,
#         serie=comprobante_model.serie or 'A',
#         folio=comprobante_model.folio or '1',
#         moneda=comprobante_model.c_Moneda.c_Moneda if comprobante_model.c_Moneda else 'MXN',
#         tipo_de_comprobante=comprobante_model.c_TipoDeComprobante.c_TipoDeComprobante,
#         exportacion=comprobante_model.c_Exportacion.c_Exportacion if comprobante_model.c_Exportacion else '01',
#         conceptos=conceptos,
#     )

#     # Firmar y procesar
#     cfdi.sign(signer)
#     cfdi = cfdi.process()
    
#     return cfdi

def obtener_datos_factura(id):
    comprobante_model = Comprobante.objects.get(id=id)
    if not comprobante_model:
        print('No se encontró el comprobante')
        return None
    

    receptor_model = Receptor.objects.filter(comprobante=comprobante_model).first()
    if not receptor_model:
        print('No se encontró el receptor')
        return None

    receptor = cfdi40.Receptor(
        rfc=receptor_model.rfc,
        nombre=receptor_model.nombre,
        uso_cfdi=receptor_model.c_UsoCFDI.c_UsoCFDI,
        domicilio_fiscal_receptor=str(receptor_model.c_DomicilioFiscalReceptor.c_CodigoPostal),
        regimen_fiscal_receptor=str(receptor_model.c_RegimenFiscalReceptor.c_RegimenFiscal),
        residencia_fiscal = (
        receptor_model.c_ResidenciaFiscal.c_Pais if receptor_model.c_ResidenciaFiscal and receptor_model.c_ResidenciaFiscal.c_Pais != "MEX" else None),
        num_reg_id_trib = receptor_model.numRegldTrib or None
    )

    emisor_model = Emisor.objects.filter(comprobante=comprobante_model).first()
    if not emisor_model:
        print('No se encontró el emisor')
        return None

    info_fiscal = comprobante_model.informacionFiscal
    certificado = CertificadoSelloDigital.objects.filter(informacionFiscal=info_fiscal, estado=True, defecto=True).order_by('-defecto', '-vigencia').first()
    print('informacion_fiscal', info_fiscal)
    print('certificado', certificado)
    signer = Signer.load(
        certificate=certificado.archivo_certificado.read(),
        key=certificado.clave_privada.read(),
        password=certificado.get_plain_password(),
    )

    emisor = cfdi40.Emisor(
        rfc=signer.rfc,
        nombre=emisor_model.nombre,
        regimen_fiscal=str(emisor_model.c_RegimenFiscal.c_RegimenFiscal)
    )
    
    # ----- Informacion Global -----#
    informacionGlobal = None 
    infoGlobal_model = InformacionGlobal.objects.filter(Comprobante=comprobante_model).first()
    if infoGlobal_model:
        informacionGlobal = cfdi40.InformacionGlobal(
            periodicidad = infoGlobal_model.Periodicidad.c_Periodicidad,
            meses = infoGlobal_model.Meses.c_Meses,
            ano = infoGlobal_model.Anio
        )
    
    
    # --- CFDI RELACIONADOS ---
    cfdis_relacionados_model = comprobante_model.cfdirelacionados_set.all()
    cfdi_relacionados = None
    if cfdis_relacionados_model.exists():
        # Agrupamos por tipo de relación (aunque normalmente es uno solo)
        from collections import defaultdict
        relaciones_dict = defaultdict(list)
        for rel in cfdis_relacionados_model:
            relaciones_dict[rel.c_TipoRelacion.c_TipoRelacion].append(rel.uuid)

        cfdi_relacionados = [
            cfdi40.CfdiRelacionados(
                tipo_relacion=tipo,
                cfdi_relacionado=uuids
            ) for tipo, uuids in relaciones_dict.items()
        ]
        
        print("CFDI Relacionados:", cfdi_relacionados)


    conceptos = []
    for concepto_model in comprobante_model.conceptos.all():
        traslados_concepto = []
        retenciones_concepto = []

        for impuesto_model in concepto_model.impuestos.all():
            base = Decimal(impuesto_model.base) if impuesto_model.base else Decimal(concepto_model.valorUnitario) * Decimal(concepto_model.cantidad)
            impuesto_data = {
                'base': base,
                'impuesto': impuesto_model.c_Impuesto.c_Impuesto,
                'tipo_factor': impuesto_model.c_TipoFactor.c_TipoFactor or None,
                'tasa_o_cuota': (impuesto_model.porcentaje if impuesto_model.c_TipoFactor.c_TipoFactor != 'Exento' else None),
                'importe': Decimal(impuesto_model.importe) if impuesto_model.importe else None
            }
            print(impuesto_model.id,'impuesto', impuesto_data)
            if impuesto_model.tipo == 'Traslado':
                traslados_concepto.append(cfdi40.Traslado(**impuesto_data))
            elif impuesto_model.tipo == 'Retención':
                retenciones_concepto.append(cfdi40.Retencion(**impuesto_data))

        impuestos_concepto = cfdi40.Impuestos(
            traslados=traslados_concepto or None,
            retenciones=retenciones_concepto or None
        ) if traslados_concepto or retenciones_concepto else None

        # A Cuenta de Terceros
        terceros_model = concepto_model.aCuentaTerceros.first()
        a_cuenta_terceros = None
        if terceros_model:
            print("Terceros:", terceros_model)
            a_cuenta_terceros = cfdi40.ACuentaTerceros(
                rfc_a_cuenta_terceros=terceros_model.rfcACuentaTerceros,
                nombre_a_cuenta_terceros=terceros_model.nombreACuentaTerceros,
                regimen_fiscal_a_cuenta_terceros=str(terceros_model.c_RegimenFiscalACuentaTerceros.c_RegimenFiscal),
                domicilio_fiscal_a_cuenta_terceros=terceros_model.domicilioFiscalACuentaTerceros,
            )

        # Cuenta Predial
        cuenta_predial = [cp.numero for cp in concepto_model.cuentaPredial.all() if cp.numero]


        # Información Aduanera (pedimentos)
        informacion_aduanera = [p.numero for p in concepto_model.pedimentos.all() if p.numero]

        # Partes
        partes = []
        for parte_model in concepto_model.parte.all():
            parte_info_aduanera = (
                [parte_model.informacionAduanera.numero]
                if parte_model.informacionAduanera and parte_model.informacionAduanera.numero else None
            )
            partes.append(cfdi40.Parte(
                clave_prod_serv=parte_model.claveProdServ.c_ClaveProdServ,
                cantidad=parte_model.cantidad,
                descripcion=parte_model.descripcion,
                no_identificacion=parte_model.noIdentificacion,
                unidad=parte_model.unidad,
                valor_unitario=parte_model.valorUnitario,
                importe=parte_model.importe,
                informacion_aduanera=parte_info_aduanera
            ))

        concepto_cfdi = cfdi40.Concepto(
            clave_prod_serv=concepto_model.c_ClaveProdServ.c_ClaveProdServ,
            cantidad=Decimal(concepto_model.cantidad),
            clave_unidad=concepto_model.c_ClaveUnidad.c_ClaveUnidad,
            descripcion=concepto_model.descripcion,
            valor_unitario=Decimal(concepto_model.valorUnitario),
            no_identificacion = concepto_model.noIdentificacion or None,
            unidad=concepto_model.unidad or None,
            descuento=concepto_model.descuento or None,
            objeto_imp=concepto_model.c_ObjetoImp.c_ObjetoImp,
            impuestos=impuestos_concepto,
            a_cuenta_terceros=a_cuenta_terceros,
            cuenta_predial=cuenta_predial,
            informacion_aduanera=informacion_aduanera or None,
            parte=partes or None
        )
        conceptos.append(concepto_cfdi)

    cfdi = cfdi40.Comprobante(
        emisor=emisor,
        lugar_expedicion=comprobante_model.c_LugarExpedicion.c_CodigoPostal,  # Puedes hacer esto dinámico si lo necesitas
        receptor=receptor,
        metodo_pago=comprobante_model.c_MetodoPago.c_MetodoPago if comprobante_model.c_MetodoPago else None,
        informacion_global = informacionGlobal or None,
        forma_pago=comprobante_model.c_FormaPago.c_FormaPago if comprobante_model.c_FormaPago else None,
        condiciones_de_pago= comprobante_model.condicionesDePago or None,
        tipo_cambio=comprobante_model.tipoCambio or None,
        serie=comprobante_model.serie or None,
        folio=comprobante_model.folio or None,
        moneda=comprobante_model.c_Moneda.c_Moneda or 'MXN',
        tipo_de_comprobante=comprobante_model.c_TipoDeComprobante.c_TipoDeComprobante,
        exportacion=comprobante_model.c_Exportacion.c_Exportacion if comprobante_model.c_Exportacion else '01',
        conceptos=conceptos,
        cfdi_relacionados=cfdi_relacionados
    )
    
    # Parchea ObjetoImp para forzar el valor original
    for i, concepto_model in enumerate(comprobante_model.conceptos.all()):
        if cfdi["Conceptos"][i].get("ObjetoImp") not in ("01", "02", "03", "04", "05", "06", "07", "08"):
            cfdi["Conceptos"][i]["ObjetoImp"] = concepto_model.c_ObjetoImp.c_ObjetoImp
        else:
            # Siempre sobrescribe, si quieres forzarlo completamente:
            cfdi["Conceptos"][i]["ObjetoImp"] = concepto_model.c_ObjetoImp.c_ObjetoImp


    cfdi.sign(signer)
    cfdi = cfdi.process()

    return cfdi



#funcion obtener datos nomina
# def obtener_datos_comprobante_nomina12(id):
#     from datetime import date
#     from decimal import Decimal
#     from satcfdi.models import Signer
#     from satcfdi.create.cfd import cfdi40, nomina12
#     from dateutil.relativedelta import relativedelta
#     from django.db import models
#     from cfdi.models import (
#         ComprobanteNomina12, CertificadoSelloDigital, Nomina, Emisor,
#         Percepcion, Deduccion, OtroPago, Incapacidad, subcontratacion
#     )

#     # ============= PATCHES =============
#     class ComprobanteSinFormaPago(cfdi40.Comprobante):
#         def __init__(self, *args, **kwargs):
#             if kwargs.get("tipo_de_comprobante") == "N":
#                 kwargs.pop("forma_pago", None)
#             super().__init__(*args, **kwargs)
#     cfdi40.Comprobante = ComprobanteSinFormaPago


#     from decimal import Decimal
#     from satcfdi.create.cfd import cfdi40

# # Parche para evitar error de suma None + Decimal
#     _original_nomina_method = cfdi40.Comprobante.nomina

#     def patched_nomina(
#         cls,
#         emisor,
#         lugar_expedicion,
#         receptor,
#         complemento_nomina,
#         cfdi_relacionados=None,
#         confirmacion=None,
#         serie=None,
#         folio=None,
#         addenda=None,
#         fecha=None
#     ):
#         def safe(val):
#             return val if val is not None else Decimal(0)
#         # Si existe y no es Decimal, conviértelo, si no, Decimal(0)
#         total_percepciones = complemento_nomina.get('TotalPercepciones', None)
#         total_otros_pagos = complemento_nomina.get('TotalOtrosPagos', None)
#         total_percepciones = Decimal(total_percepciones) if total_percepciones not in (None, '') else Decimal(0)
#         total_otros_pagos = Decimal(total_otros_pagos) if total_otros_pagos not in (None, '') else Decimal(0)
#         valor_unitario = total_percepciones + total_otros_pagos

#         concepto_data = {
#             "clave_prod_serv": "84111505",
#             "cantidad": 1,
#             "clave_unidad": "ACT",
#             "descripcion": "Pago de nómina",
#             "valor_unitario": valor_unitario,
#             "objeto_imp": "03",
#         }

#         # Solo agrega descuento si es mayor a 0
#         try:
#             descuento_valor = Decimal(complemento_nomina.get("TotalDeducciones", "0") or "0")
#         except:
#             descuento_valor = Decimal("0")

#         if descuento_valor > Decimal("0"):
#             concepto_data["descuento"] = descuento_valor

#         concepto = cfdi40.Concepto(**concepto_data)

#         if cls.version == "3.3":
#             receptor["UsoCFDI"] = "P01"
#         else:
#             receptor["UsoCFDI"] = "CN01"

#         return cls(
#             emisor=emisor,
#             lugar_expedicion=lugar_expedicion,
#             receptor=receptor,
#             conceptos=concepto,
#             complemento=complemento_nomina,
#             serie=serie,
#             folio=folio,
#             moneda='MXN',
#             tipo_de_comprobante='N',
#             metodo_pago="PUE",
#             forma_pago="99",
#             cfdi_relacionados=cfdi_relacionados,
#             confirmacion=confirmacion,
#             exportacion="01",
#             addenda=addenda,
#             fecha=fecha,
#         )

#     cfdi40.Comprobante.nomina = classmethod(patched_nomina)



#     class EmisorNominaPatch(nomina12.Emisor):
#         def __init__(self, *args, **kwargs):
#             rfc = kwargs.get("rfc", "")  # Asegúrate de pasar el RFC en la instancia
#             curp = kwargs.get("curp", "")
#             registro_patronal = kwargs.get("registro_patronal", "")

#             # Quitar CURP si está vacío o si es moral (longitud RFC = 12)
#             if not curp or len(rfc) == 12:
#                 kwargs.pop("curp", None)

#             # Quitar REGISTRO PATRONAL si es persona moral (RFC 12)
#             if len(rfc) == 12:
#                 kwargs.pop("registro_patronal", None)

#             super().__init__(*args, **kwargs)

#     nomina12.Emisor = EmisorNominaPatch

#     def make_receptor_nomina(**kwargs):
#         registro_patronal_emisor = kwargs.pop("registro_patronal_emisor", None)
#         if not (registro_patronal_emisor and str(registro_patronal_emisor).strip()):
#             kwargs.pop("num_seguridad_social", None)
#             kwargs.pop("fecha_inicio_rel_laboral", None)
#             kwargs.pop("antiguedad", None)
#             kwargs.pop("riesgo_puesto", None)
#             kwargs.pop("salario_diario_integrado", None)
#         return nomina12.Receptor(**kwargs)


   


#     class EntidadSNCFNominaPatch(nomina12.EntidadSNCF):
#         def __init__(self, *args, **kwargs):
#             origen_recurso = kwargs.get("origen_recurso", "")
#             # Si origen_recurso NO es IM, elimina monto_recurso_propio
#             if origen_recurso != "IM":
#                 kwargs.pop("monto_recurso_propio", None)
#             super().__init__(*args, **kwargs)

#     nomina12.EntidadSNCF = EntidadSNCFNominaPatch   

    

#     class NominaPatch(nomina12.Nomina):
#         def __init__(self, *args, **kwargs):
#             super().__init__(*args, **kwargs)
#             ded = self.get("Deducciones")
#             if isinstance(ded, dict):
#                 deduccion_list = ded.get("Deduccion", [])
#                 has_isr = any(
#                     isinstance(d, dict) and d.get("TipoDeduccion") == "002"
#                     for d in deduccion_list
#                 )
#                 if not has_isr:
#                     ded.pop("TotalImpuestosRetenidos", None)
#                     if "TotalOtrasDeducciones" in ded:
#                         self["TotalDeducciones"] = ded["TotalOtrasDeducciones"]
#                     else:
#                         self["TotalDeducciones"] = None

#     nomina12.Nomina = NominaPatch


#     class NominaSafePatch(nomina12.Nomina):
#         def __init__(self, *args, **kwargs):
#             super().__init__(*args, **kwargs)

#             ded = self.get("Deducciones")
#             if isinstance(ded, dict):
#                 deduccion_list = ded.get("Deduccion", [])
#                 # Si todas las deducciones tienen Importe=0.00, elimina el nodo completo
#                 all_zero = all(
#                     isinstance(d, dict) and Decimal(d.get("Importe", "0")) == Decimal("0.00")
#                     for d in deduccion_list
#                 )
#                 if all_zero:
#                     self.pop("Deducciones", None)
#                     self.pop("TotalDeducciones", None)

#     nomina12.Nomina = NominaSafePatch




#     # ====================================

#     def safe_decimal(value, default='0'):
#         return Decimal(value) if value is not None else Decimal(default)

#     def calcular_antiguedad(fecha_inicio, fecha_fin):
#         diferencia = relativedelta(fecha_fin, fecha_inicio)
#         partes = []
#         if diferencia.years:
#             partes.append(f"{diferencia.years}Y")
#         if diferencia.months:
#             partes.append(f"{diferencia.months}M")
#         if diferencia.days:
#             partes.append(f"{diferencia.days}D")
#         return "P" + "".join(partes) if partes else "P1D"

#     comprobante_nomina = ComprobanteNomina12.objects.get(id=id)
#     info_fiscal = comprobante_nomina.informacionFiscal
#     certificado = CertificadoSelloDigital.objects.filter(
#         informacionFiscal=info_fiscal, estado=True
#     ).order_by('-defecto', '-vigencia').first()
#     nomina = Nomina.objects.get(comprobanteNomina12=comprobante_nomina)
#     emisor_model = Emisor.objects.filter(comprobante=comprobante_nomina).first()

#     percepciones_qs = Percepcion.objects.filter(comprobanteNomina12=comprobante_nomina)
#     deducciones_qs = Deduccion.objects.filter(comprobanteNomina12=comprobante_nomina)
#     otros_pagos_qs = OtroPago.objects.filter(comprobanteNomina12=comprobante_nomina)
#     subcontrataciones_qs = subcontratacion.objects.filter(comprobanteNomina12=comprobante_nomina)

#     antiguedad_str = calcular_antiguedad(
#         nomina.fecha_inicio_relacion_laboral,
#         nomina.fecha_final_pago
#     )

#     # === EntidadSNCF

#     entidadsncf = None
#     if nomina.origen_recurso:
#         origen_recurso_val = str(nomina.origen_recurso.c_OrigenRecurso)
#         monto_recurso_propio_val = str(nomina.monto_recurso_propio) if nomina.monto_recurso_propio is not None else "0.00"
#         entidadsncf = nomina12.EntidadSNCF(
#             origen_recurso=origen_recurso_val,
#             monto_recurso_propio=monto_recurso_propio_val
#         )


    


#     # --- INCAPACIDADES ---
#     incapacidades_qs = Incapacidad.objects.filter(
#         models.Q(percepcion__comprobanteNomina12=comprobante_nomina) |
#         models.Q(Deduccion__comprobanteNomina12=comprobante_nomina)
#     ).distinct()

#     incapacidades_list = [
#         nomina12.Incapacidad(
#             tipo_incapacidad=i.tipo_incapacidad.c_TipoIncapacidad if i.tipo_incapacidad else "01",
#             dias_incapacidad=i.dias_incapacidad or 0,
#             importe_monetario=safe_decimal(getattr(i, 'importe_Monetario', 0), '0')
#         ) for i in incapacidades_qs if getattr(i, 'percepcion', None) or getattr(i, 'Deduccion', None)
#     ]
#     # Si no hay incapacidades, se pasa None
#     incapacidades_list = incapacidades_list if incapacidades_list else None

#     # --- SUBCONTRATACION ---
#     subcontratacion_list = [
#         nomina12.SubContratacion(
#             rfc_labora=sub.rfclaboral,
#             porcentaje_tiempo=sub.porcentaje
#         )
#         for sub in subcontrataciones_qs
#     ]
#     subcontratacion_list = subcontratacion_list if subcontratacion_list else None

   
#     # --- PERCEPCIONES ---
#     def safe_int(value, default=0):
#         """Devuelve un entero seguro, o el valor por defecto si es None."""
#         return int(value) if value is not None else default
    


#     percepciones_list = []
#     for p in percepciones_qs:
#         tipo_percepcion = p.tipo_percepcion.c_TipoPercepcion if p.tipo_percepcion else "001"
#         horas_extra_list = [
#             nomina12.HorasExtra(
#                 tipo_horas=he.tipo_horas.c_TipoHoras if he.tipo_horas else "01",
#                 dias=he.dias or 0,
#                 horas_extra=he.horas_extra or 0,
#                 importe_pagado=safe_decimal(he.importe_pagado, '0')
#             ) for he in p.horas_extra.all()
#         ]

#         percepcion_kwargs = {
#             "tipo_percepcion": tipo_percepcion,
#             "clave": p.clave,
#             "concepto": p.tipo_percepcion.descripcion if p.tipo_percepcion else "DESCONOCIDO",
#             "importe_gravado": safe_decimal(p.importe_gravado, '0'),
#             "importe_exento": safe_decimal(p.importe_exento, '0'),
#             "horas_extra": horas_extra_list if horas_extra_list else None,
#         }

#         # Si TipoPercepcion es "045", agregamos el nodo AccionesOTitulos
#         if tipo_percepcion == "045":
#             percepcion_kwargs["acciones_o_titulos"] = nomina12.AccionesOTitulos(
#                 valor_mercado=safe_decimal(p.importe_exento, '0'),
#                 precio_al_otorgarse=safe_decimal(p.importe_exento, '0'),
#             )


#         if tipo_percepcion == "023":
#             separacion_obj = getattr(p, 'separacion_indemnizacion', None)
#             if separacion_obj:
#                 sep = separacion_obj.first()
#                 if sep:
#                     print("DEBUG SEP:", sep.num_anos_servicio, repr(sep.num_anos_servicio), type(sep.num_anos_servicio))
#                     separacion_indemnizacion_data = {
#                         "total_pagado": safe_decimal(sep.total_pagado, '0'),
#                         "num_anos_servicio": safe_int(sep.num_anos_servicio, 0),
#                         "ultimo_sueldo_mens_ord": safe_decimal(sep.ultimo_sueldo_mens_ord, '0'),
#                         "ingreso_acumulable": safe_decimal(sep.ingreso_acumulable, '0'),
#                         "ingreso_no_acumulable": safe_decimal(sep.ingreso_no_acumulable, '0')
#                     }


#         percepciones_list.append(nomina12.Percepcion(**percepcion_kwargs))

#     if percepciones_list:
#         if separacion_indemnizacion_data:
#             percepciones_obj = nomina12.Percepciones(
#                 percepcion=percepciones_list,
#                 separacion_indemnizacion=nomina12.SeparacionIndemnizacion(**separacion_indemnizacion_data)
#             )
#         else:
#             percepciones_obj = nomina12.Percepciones(percepcion=percepciones_list)
#     else:
#         percepciones_obj = None


#     # --- PARCHE PARA ELIMINAR TotalSueldos Y AGREGAR TotalSeparacionIndemnizacion ---
#     # Parche seguro para Percepciones tipo 023
#     if percepciones_obj is not None:
#         percepciones_dict = dict(percepciones_obj)
#         percepciones_list_dict = percepciones_dict.get('Percepcion', [])
#         if not isinstance(percepciones_list_dict, list):
#             percepciones_list_dict = [percepciones_list_dict]
#         hay_023 = any(p.get('TipoPercepcion') == '023' for p in percepciones_list_dict)
#         # Si hay 023, elimina TotalSueldos del dict (por si luego serializas el dict a XML)
#         if hay_023:
#             percepciones_dict.pop('TotalSueldos', None)
#         # Reconstruye objeto Percepciones solo con argumentos válidos
#         percepciones_kwargs = {
#             'percepcion': percepciones_list,
#         }
#         if separacion_indemnizacion_data:
#             percepciones_kwargs['separacion_indemnizacion'] = nomina12.SeparacionIndemnizacion(**separacion_indemnizacion_data)
#         percepciones_obj = nomina12.Percepciones(**percepciones_kwargs)




#     # --- DEDUCCIONES ---
    
#     deducciones_list = []

#     if deducciones_qs.exists():
#         for d in deducciones_qs:
#             deducciones_list.append(nomina12.Deduccion(
#                 tipo_deduccion=d.tipo_deduccion.c_TipoDeduccion if d.tipo_deduccion else "002",
#                 clave=d.clave,
#                 concepto=d.tipo_deduccion.descripcion if d.tipo_deduccion else "DESCONOCIDO",
#                 importe=safe_decimal(d.importe, '0')
#             ))
#     else:
#         # Se agrega una deducción dummy en cero para evitar errores
#         deducciones_list.append(nomina12.Deduccion(
#             tipo_deduccion="001",
#             clave="000",
#             concepto="Deducción automática en cero",
#             importe=Decimal("0.00")
#         ))

#     deducciones_obj = nomina12.Deducciones(deduccion=deducciones_list)


    

#     # --- OTROS PAGOS ---
#     otro_pago_list = []
#     for op in otros_pagos_qs:
#         tipo_otro_pago_val = op.tipo_otro_pago.c_TipoOtroPago if op.tipo_otro_pago else "002"
#         subsidio_causado = safe_decimal(getattr(op, 'subsidioCausado', 0), '0')

#         if tipo_otro_pago_val == "002":
#             otro_pago = nomina12.OtroPago(
#                 tipo_otro_pago=tipo_otro_pago_val,
#                 clave=op.clave or "999",
#                 concepto=op.tipo_otro_pago.descripcion if op.tipo_otro_pago else "",
#                 importe=safe_decimal(op.importe, '0'),
#                 subsidio_al_empleo= safe_decimal(subsidio_causado),
#             )
#         else:
#             otro_pago = nomina12.OtroPago(
#                 tipo_otro_pago=tipo_otro_pago_val,
#                 clave=op.clave or "999",
#                 concepto=op.tipo_otro_pago.descripcion if op.tipo_otro_pago else "",
#                 importe=safe_decimal(op.importe, '0'),
#                 # NO se incluye subsidio_al_empleo
#             )

#         otro_pago_list.append(otro_pago)

#     otro_pago_list = otro_pago_list if otro_pago_list else None

#     signer = Signer.load(
#         certificate=certificado.archivo_certificado.read(),
#         key=certificado.clave_privada.read(),
#         password=certificado.contrasena,
#     )

#     cuenta_bancaria = nomina.cuenta_bancaria or ""
#     if len(cuenta_bancaria) == 18 and cuenta_bancaria.isdigit():
#         banco_val = None
#     else:
#         banco_val = nomina.banco.c_Banco if nomina.banco else None

#     # ------------------- Generar Comprobante -------------------
#     invoice = cfdi40.Comprobante.nomina(
#         emisor=cfdi40.Emisor(
#             rfc=signer.rfc,
#             nombre=emisor_model.nombre,
#             regimen_fiscal=str(emisor_model.c_RegimenFiscal.c_RegimenFiscal),
            

#         ),
#         receptor=cfdi40.Receptor(
#             rfc=nomina.rfc_trabajador,
#             nombre=" ".join(filter(None, [nomina.nombre, nomina.apellido_paterno, nomina.apellido_materno])),
#             uso_cfdi="CN01",
#             domicilio_fiscal_receptor=str(nomina.c_CodigoPostal.c_CodigoPostal) if nomina.c_CodigoPostal else "00000",
#             regimen_fiscal_receptor="605"
#         ),
#         lugar_expedicion=  comprobante_nomina.c_LugarExpedicion.c_CodigoPostal if comprobante_nomina.c_LugarExpedicion else "00000",
#         complemento_nomina=nomina12.Nomina(
#             emisor=nomina12.Emisor(
#                 registro_patronal=nomina.registro_patronal or None,
#                 curp=nomina.curp or "",
#                 entidad_sncf=entidadsncf

#             ),


#             receptor=make_receptor_nomina(
#                 curp=nomina.curp_trabajador or "",
#                 clave_ent_fed=nomina.entidad_presto_servicio.c_Estado if nomina.entidad_presto_servicio else "",
#                 num_empleado=nomina.numero_empleado or "",
#                 periodicidad_pago=nomina.periodicidad.c_PeriodicidadPago if nomina.periodicidad else "",
#                 tipo_contrato=nomina.tipo_contrato.c_TipoContrato if nomina.tipo_contrato else "01",
#                 tipo_regimen=nomina.tipo_regimen.c_TipoRegimen if nomina.tipo_regimen else "02",
#                 fecha_inicio_rel_laboral=nomina.fecha_inicio_relacion_laboral,
#                 antiguedad=antiguedad_str or "P1D",
#                 riesgo_puesto=str(nomina.riesgo_puesto.c_RiesgoPuesto) if nomina.riesgo_puesto else None,
#                 salario_diario_integrado=nomina.salario_diario or "0",
#                 num_seguridad_social=nomina.numero_seguro_social or "",
#                 tipo_jornada=nomina.tipo_jornada.c_TipoJornada if nomina.tipo_jornada else None,
#                 cuenta_bancaria=nomina.cuenta_bancaria or "",
#                 banco=banco_val,
#                 puesto=nomina.puesto if nomina.puesto else None,
#                 sindicalizado=nomina.sindicalizado.opcion if hasattr(nomina.sindicalizado, "opcion") else None,
#                 departamento=nomina.departamento if nomina.departamento else None,
#                 salario_base_cot_apor=nomina.salario_base or "0",
#                 sub_contratacion=subcontratacion_list,   # <-- Se pasa None si no hay
#                 registro_patronal_emisor=nomina.registro_patronal or None,
#             ),
#             incapacidades=incapacidades_list,           # <-- Se pasa None si no hay
#             percepciones=percepciones_obj,              # <-- Siempre requerido
#             deducciones=deducciones_obj,                # <-- Se pasa None si no hay
#             otros_pagos=otro_pago_list,                 # <-- Se pasa None si no hay
#             tipo_nomina=nomina.tipo_nomina.c_TipoNomina if nomina.tipo_nomina else "01",
#             fecha_pago=nomina.fecha_pago or date(2020, 1, 31),
#             fecha_final_pago=nomina.fecha_final_pago or date(2020, 1, 31),
#             fecha_inicial_pago=nomina.fecha_inicial_pago or date(2020, 1, 16),
#             num_dias_pagados=safe_decimal(nomina.numero_dias_pagados, '16.000')
#         ),
#         serie=comprobante_nomina.serie or 'A',
#         folio=comprobante_nomina.folio or '1',
#     )

    


#     #cambia el obj impuesto a 01 en vez de 03
#     if hasattr(invoice, "get") and invoice.get("Conceptos"):
#         conceptos = invoice["Conceptos"]
#         if isinstance(conceptos, list):
#             for concepto in conceptos:
#                 concepto['ObjetoImp'] = '01'
#         elif isinstance(conceptos, dict):
#             conceptos['ObjetoImp'] = '01'

#     invoice.sign(signer)
#     invoice_cfdi = invoice.process()

#     percepciones = (
#         invoice_cfdi
#         .get("Complemento", {})
#         .get("Nomina", {})
#         .get("Percepciones")
#     )
#     if isinstance(percepciones, dict) and "TotalSueldos" in percepciones:
#         percepciones["TotalSeparacionIndemnizacion"] = percepciones.pop(
#             "TotalSueldos"
#         )

#     return invoice_cfdi


def obtener_datos_comprobante_nomina12(id):
    from datetime import date
    from decimal import Decimal
    from satcfdi.models import Signer
    from satcfdi.create.cfd import cfdi40, nomina12
    from dateutil.relativedelta import relativedelta
    from django.db import models
    from cfdi.models import (
        ComprobanteNomina12, CertificadoSelloDigital, Nomina, Emisor,
        Percepcion, Deduccion, OtroPago, Incapacidad, subcontratacion
    )

    # ============= PATCHES =============
    class ComprobanteSinFormaPago(cfdi40.Comprobante):
        def __init__(self, *args, **kwargs):
            if kwargs.get("tipo_de_comprobante") == "N":
                kwargs.pop("forma_pago", None)
            super().__init__(*args, **kwargs)
    cfdi40.Comprobante = ComprobanteSinFormaPago

    # Parche para evitar error de suma None + Decimal
    _original_nomina_method = cfdi40.Comprobante.nomina
    def patched_nomina(
        cls,
        emisor,
        lugar_expedicion,
        receptor,
        complemento_nomina,
        cfdi_relacionados=None,
        confirmacion=None,
        serie=None,
        folio=None,
        addenda=None,
        fecha=None
    ):
        def safe(val):
            return val if val is not None else Decimal(0)
        total_percepciones = complemento_nomina.get('TotalPercepciones', None)
        total_otros_pagos = complemento_nomina.get('TotalOtrosPagos', None)
        total_percepciones = Decimal(total_percepciones) if total_percepciones not in (None, '') else Decimal(0)
        total_otros_pagos = Decimal(total_otros_pagos) if total_otros_pagos not in (None, '') else Decimal(0)
        valor_unitario = total_percepciones + total_otros_pagos

        concepto_data = {
            "clave_prod_serv": "84111505",
            "cantidad": 1,
            "clave_unidad": "ACT",
            "descripcion": "Pago de nómina",
            "valor_unitario": valor_unitario,
            "objeto_imp": "03",
        }
        try:
            descuento_valor = Decimal(complemento_nomina.get("TotalDeducciones", "0") or "0")
        except:
            descuento_valor = Decimal("0")
        if descuento_valor > Decimal("0"):
            concepto_data["descuento"] = descuento_valor
        concepto = cfdi40.Concepto(**concepto_data)
        if cls.version == "3.3":
            receptor["UsoCFDI"] = "P01"
        else:
            receptor["UsoCFDI"] = "CN01"
        return cls(
            emisor=emisor,
            lugar_expedicion=lugar_expedicion,
            receptor=receptor,
            conceptos=concepto,
            complemento=complemento_nomina,
            serie=serie,
            folio=folio,
            moneda='MXN',
            tipo_de_comprobante='N',
            metodo_pago="PUE",
            forma_pago="99",
            cfdi_relacionados=cfdi_relacionados,
            confirmacion=confirmacion,
            exportacion="01",
            addenda=addenda,
            fecha=fecha,
        )
    cfdi40.Comprobante.nomina = classmethod(patched_nomina)

    # ============ PATCHES extra ==============
    
    
    class EmisorNominaPatch(nomina12.Emisor):
        def __init__(self, *args, **kwargs):
            rfc = kwargs.get("rfc", "")
            curp = kwargs.get("curp", "")
            registro_patronal = kwargs.get("registro_patronal", "")
            if not curp or len(rfc) == 12:
                kwargs.pop("curp", None)
            if len(rfc) == 12:
                kwargs.pop("registro_patronal", None)
            super().__init__(*args, **kwargs)
    nomina12.Emisor = EmisorNominaPatch

    def make_receptor_nomina(**kwargs):
        registro_patronal_emisor = kwargs.pop("registro_patronal_emisor", None)
        if not (registro_patronal_emisor and str(registro_patronal_emisor).strip()):
            kwargs.pop("num_seguridad_social", None)
            kwargs.pop("fecha_inicio_rel_laboral", None)
            kwargs.pop("antiguedad", None)
            kwargs.pop("riesgo_puesto", None)
            kwargs.pop("salario_diario_integrado", None)
        return nomina12.Receptor(**kwargs)

    class EntidadSNCFNominaPatch(nomina12.EntidadSNCF):
        def __init__(self, *args, **kwargs):
            origen_recurso = kwargs.get("origen_recurso", "")
            if origen_recurso != "IM":
                kwargs.pop("monto_recurso_propio", None)
            super().__init__(*args, **kwargs)
    nomina12.EntidadSNCF = EntidadSNCFNominaPatch

    class NominaPatch(nomina12.Nomina):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            ded = self.get("Deducciones")
            if isinstance(ded, dict):
                deduccion_list = ded.get("Deduccion", [])
                has_isr = any(
                    isinstance(d, dict) and d.get("TipoDeduccion") == "002"
                    for d in deduccion_list
                )
                if not has_isr:
                    ded.pop("TotalImpuestosRetenidos", None)
                    if "TotalOtrasDeducciones" in ded:
                        self["TotalDeducciones"] = ded["TotalOtrasDeducciones"]
                    else:
                        self["TotalDeducciones"] = None
    nomina12.Nomina = NominaPatch

    class NominaSafePatch(nomina12.Nomina):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            ded = self.get("Deducciones")
            if isinstance(ded, dict):
                deduccion_list = ded.get("Deduccion", [])
                all_zero = all(
                    isinstance(d, dict) and Decimal(d.get("Importe", "0")) == Decimal("0.00")
                    for d in deduccion_list
                )
                if all_zero:
                    self.pop("Deducciones", None)
                    self.pop("TotalDeducciones", None)
    nomina12.Nomina = NominaSafePatch

    # ====================================

    def safe_decimal(value, default='0'):
        return Decimal(value) if value is not None else Decimal(default)

    def calcular_antiguedad(fecha_inicio, fecha_fin):
        diferencia = relativedelta(fecha_fin, fecha_inicio)
        partes = []
        if diferencia.years:
            partes.append(f"{diferencia.years}Y")
        if diferencia.months:
            partes.append(f"{diferencia.months}M")
        if diferencia.days:
            partes.append(f"{diferencia.days}D")
        return "P" + "".join(partes) if partes else "P1D"

    comprobante_nomina = ComprobanteNomina12.objects.get(id=id)
    info_fiscal = comprobante_nomina.informacionFiscal
    certificado = CertificadoSelloDigital.objects.filter(
        informacionFiscal=info_fiscal, estado=True
    ).order_by('-defecto', '-vigencia').first()
    nomina = Nomina.objects.get(comprobanteNomina12=comprobante_nomina)
    emisor_model = Emisor.objects.filter(comprobante=comprobante_nomina).first()
    percepciones_qs = Percepcion.objects.filter(comprobanteNomina12=comprobante_nomina)
    deducciones_qs = Deduccion.objects.filter(comprobanteNomina12=comprobante_nomina)
    otros_pagos_qs = OtroPago.objects.filter(comprobanteNomina12=comprobante_nomina)
    subcontrataciones_qs = subcontratacion.objects.filter(comprobanteNomina12=comprobante_nomina)

    antiguedad_str = calcular_antiguedad(
        nomina.fecha_inicio_relacion_laboral,
        nomina.fecha_final_pago
    )

    # === EntidadSNCF
    entidadsncf = None
    if nomina.origen_recurso:
        origen_recurso_val = str(nomina.origen_recurso.c_OrigenRecurso)
        monto_recurso_propio_val = str(nomina.monto_recurso_propio) if nomina.monto_recurso_propio is not None else "0.00"
        entidadsncf = nomina12.EntidadSNCF(
            origen_recurso=origen_recurso_val,
            monto_recurso_propio=monto_recurso_propio_val
        )

    # --- INCAPACIDADES ---
    incapacidades_qs = Incapacidad.objects.filter(
        models.Q(percepcion__comprobanteNomina12=comprobante_nomina) |
        models.Q(Deduccion__comprobanteNomina12=comprobante_nomina)
    ).distinct()
    incapacidades_list = [
        nomina12.Incapacidad(
            tipo_incapacidad=i.tipo_incapacidad.c_TipoIncapacidad if i.tipo_incapacidad else "01",
            dias_incapacidad=i.dias_incapacidad or 0,
            importe_monetario=safe_decimal(getattr(i, 'importe_Monetario', 0), '0')
        ) for i in incapacidades_qs if getattr(i, 'percepcion', None) or getattr(i, 'Deduccion', None)
    ]
    incapacidades_list = incapacidades_list if incapacidades_list else None

    # --- SUBCONTRATACION ---
    subcontratacion_list = [
        nomina12.SubContratacion(
            rfc_labora=sub.rfclaboral,
            porcentaje_tiempo=sub.porcentaje
        )
        for sub in subcontrataciones_qs
    ]
    subcontratacion_list = subcontratacion_list if subcontratacion_list else None

    # --- PERCEPCIONES ---
    def safe_int(value, default=0):
        return int(value) if value is not None else default
    

    # --- PERCEPCIONES ---
    percepciones_list = []
    separacion_indemnizacion_data = None
    jubilacion_pension_retiro_data = None

    for p in percepciones_qs:
        tipo_percepcion = p.tipo_percepcion.c_TipoPercepcion if p.tipo_percepcion else "001"
        horas_extra_list = [
            nomina12.HorasExtra(
                tipo_horas=he.tipo_horas.c_TipoHoras if he.tipo_horas else "01",
                dias=he.dias or 0,
                horas_extra=he.horas_extra or 0,
                importe_pagado=safe_decimal(he.importe_pagado, '0')
            ) for he in p.horas_extra.all()
        ]
        percepcion_kwargs = {
            "tipo_percepcion": tipo_percepcion,
            "clave": p.clave,
            "concepto": p.tipo_percepcion.descripcion if p.tipo_percepcion else "DESCONOCIDO",
            "importe_gravado": safe_decimal(p.importe_gravado, '0'),
            "importe_exento": safe_decimal(p.importe_exento, '0'),
            "horas_extra": horas_extra_list if horas_extra_list else None,
        }
        # Acciones o títulos
        if tipo_percepcion == "045":
            percepcion_kwargs["acciones_o_titulos"] = nomina12.AccionesOTitulos(
                valor_mercado=safe_decimal(p.importe_exento, '0'),
                precio_al_otorgarse=safe_decimal(p.importe_exento, '0'),
            )
        # Separación/indemnización
        if tipo_percepcion == "023":
            separacion_obj = getattr(p, 'separacion_indemnizacion', None)
            if separacion_obj:
                sep = separacion_obj.first()
                if sep:
                    separacion_indemnizacion_data = {
                        "total_pagado": safe_decimal(sep.total_pagado, '0'),
                        "num_anos_servicio": safe_int(sep.num_anos_servicio, 0),
                        "ultimo_sueldo_mens_ord": safe_decimal(sep.ultimo_sueldo_mens_ord, '0'),
                        "ingreso_acumulable": safe_decimal(sep.ingreso_acumulable, '0'),
                        "ingreso_no_acumulable": safe_decimal(sep.ingreso_no_acumulable, '0')
                    }
        # Jubilación/pensión/retiro
        if tipo_percepcion == "039":
            jubilacion_obj = getattr(p, 'jubilacion_pension_retiro', None)
            if jubilacion_obj:
                jubilacion = jubilacion_obj.first()
                if jubilacion:
                    jubilacion_pension_retiro_data = {
                        "total_una_exhibicion": safe_decimal(jubilacion.total_una_exhibicion, '0'),
                        "ingreso_acumulable": safe_decimal(jubilacion.ingreso_acumulable, '0'),
                        "ingreso_no_acumulable": safe_decimal(jubilacion.ingreso_no_acumulable, '0'),
                    }
        percepciones_list.append(nomina12.Percepcion(**percepcion_kwargs))

  
    percepciones_kwargs = {
        'percepcion': percepciones_list,
    }
    if separacion_indemnizacion_data:
        percepciones_kwargs['separacion_indemnizacion'] = nomina12.SeparacionIndemnizacion(**separacion_indemnizacion_data)
    if jubilacion_pension_retiro_data:
        percepciones_kwargs['jubilacion_pension_retiro'] = nomina12.JubilacionPensionRetiro(**jubilacion_pension_retiro_data)

    if percepciones_list:
        percepciones_obj = nomina12.Percepciones(**percepciones_kwargs)

        # Calcula los totales:
        percepciones_dict = dict(percepciones_obj)
        percepcion_items = percepciones_dict.get("Percepcion", [])
        if isinstance(percepcion_items, dict):
            percepcion_items = [percepcion_items]
        total_sueldos = Decimal("0.00")
        total_jubilacion = Decimal("0.00")
        total_gravado = Decimal("0.00")
        hay_jubilacion = False

        for p in percepcion_items:
            tipo = p.get("TipoPercepcion")
            gravado = Decimal(str(p.get("ImporteGravado", "0") or "0"))
            exento = Decimal(str(p.get("ImporteExento", "0") or "0"))
            total_gravado += gravado
            if tipo in ("039", "044"):
                total_jubilacion += gravado + exento
                hay_jubilacion = True
            else:
                total_sueldos += gravado + exento

        # Ajusta TotalSueldos si hay 039 o 044
        if hay_jubilacion:
            total_sueldos = total_gravado - total_jubilacion

        percepciones_obj["TotalSueldos"] = f"{total_sueldos:.2f}"
        if total_jubilacion > 0:
            percepciones_obj["TotalJubilacionPensionRetiro"] = f"{total_jubilacion:.2f}"
    else:
        percepciones_obj = None




    # --- DEDUCCIONES ---
    deducciones_list = []
    if deducciones_qs.exists():
        for d in deducciones_qs:
            deducciones_list.append(nomina12.Deduccion(
                tipo_deduccion=d.tipo_deduccion.c_TipoDeduccion if d.tipo_deduccion else "002",
                clave=d.clave,
                concepto=d.tipo_deduccion.descripcion if d.tipo_deduccion else "DESCONOCIDO",
                importe=safe_decimal(d.importe, '0')
            ))
    else:
        deducciones_list.append(nomina12.Deduccion(
            tipo_deduccion="001",
            clave="000",
            concepto="Deducción automática en cero",
            importe=Decimal("0.00")
        ))
    deducciones_obj = nomina12.Deducciones(deduccion=deducciones_list)

    # --- OTROS PAGOS ---
    otro_pago_list = []
    for op in otros_pagos_qs:
        tipo_otro_pago_val = op.tipo_otro_pago.c_TipoOtroPago if op.tipo_otro_pago else "002"
        subsidio_causado = safe_decimal(getattr(op, 'subsidioCausado', 0), '0')
        if tipo_otro_pago_val == "002":
            otro_pago = nomina12.OtroPago(
                tipo_otro_pago=tipo_otro_pago_val,
                clave=op.clave or "999",
                concepto=op.tipo_otro_pago.descripcion if op.tipo_otro_pago else "",
                importe=safe_decimal(op.importe, '0'),
                subsidio_al_empleo= safe_decimal(subsidio_causado),
            )
        else:
            otro_pago = nomina12.OtroPago(
                tipo_otro_pago=tipo_otro_pago_val,
                clave=op.clave or "999",
                concepto=op.tipo_otro_pago.descripcion if op.tipo_otro_pago else "",
                importe=safe_decimal(op.importe, '0'),
            )
        otro_pago_list.append(otro_pago)
    otro_pago_list = otro_pago_list if otro_pago_list else None

    signer = Signer.load(
        certificate=certificado.archivo_certificado.read(),
        key=certificado.clave_privada.read(),
        password=certificado.get_plain_password(),
    )
    cuenta_bancaria = nomina.cuenta_bancaria or ""
    if len(cuenta_bancaria) == 18 and cuenta_bancaria.isdigit():
        banco_val = None
    else:
        banco_val = nomina.banco.c_Banco if nomina.banco else None

    # ------------- PATCH: solo agrega nodo emisor de nómina si hay SNCF (entidadsncf) -------------------
    # emisor_nomina_obj = None
    # if entidadsncf is not None:
    #     emisor_nomina_obj = nomina12.Emisor(
    #         registro_patronal=nomina.registro_patronal or None,
    #         curp=nomina.curp or "",
    #         entidad_sncf=entidadsncf
    #     )

    # ------------- Emisor en nómina: incluir RegistroPatronal aunque no haya EntidadSNCF -------------------
    # Antes solo se agregaba el nodo Emisor si existía EntidadSNCF, lo cual
    # impedía que apareciera el RegistroPatronal. Construimos el Emisor con
    # los campos disponibles y agregamos entidad_sncf solo cuando exista.
    emisor_kwargs = {}
    if getattr(nomina, "registro_patronal", None):
        emisor_kwargs["registro_patronal"] = nomina.registro_patronal
    if getattr(nomina, "curp", None):
        emisor_kwargs["curp"] = nomina.curp
    if entidadsncf is not None:
        emisor_kwargs["entidad_sncf"] = entidadsncf
    emisor_nomina_obj = nomina12.Emisor(**emisor_kwargs) if emisor_kwargs else None

    # ------------------- Generar Comprobante -------------------
    invoice = cfdi40.Comprobante.nomina(
        emisor=cfdi40.Emisor(
            rfc=signer.rfc,
            nombre=emisor_model.nombre,
            regimen_fiscal=str(emisor_model.c_RegimenFiscal.c_RegimenFiscal),
        ),
        receptor=cfdi40.Receptor(
            rfc=nomina.rfc_trabajador,
            nombre=" ".join(filter(None, [nomina.nombre, nomina.apellido_paterno, nomina.apellido_materno])),
            uso_cfdi="CN01",
            domicilio_fiscal_receptor=str(nomina.c_CodigoPostal.c_CodigoPostal) if nomina.c_CodigoPostal else "00000",
            regimen_fiscal_receptor="605"
        ),
        lugar_expedicion=  comprobante_nomina.c_LugarExpedicion.c_CodigoPostal if comprobante_nomina.c_LugarExpedicion else "00000",
        complemento_nomina=nomina12.Nomina(
            emisor=emisor_nomina_obj,  # <-- Solo si hay SNCF, si no, se omite (no aparece nodo)
            receptor=make_receptor_nomina(
                curp=nomina.curp_trabajador or "",
                clave_ent_fed=nomina.entidad_presto_servicio.c_Estado if nomina.entidad_presto_servicio else "",
                num_empleado=nomina.numero_empleado or "",
                periodicidad_pago=nomina.periodicidad.c_PeriodicidadPago if nomina.periodicidad else "",
                tipo_contrato=nomina.tipo_contrato.c_TipoContrato if nomina.tipo_contrato else "01",
                tipo_regimen=nomina.tipo_regimen.c_TipoRegimen if nomina.tipo_regimen else "02",
                fecha_inicio_rel_laboral=nomina.fecha_inicio_relacion_laboral,
                antiguedad=antiguedad_str or "P1D",
                riesgo_puesto=str(nomina.riesgo_puesto.c_RiesgoPuesto) if nomina.riesgo_puesto else None,
                salario_diario_integrado=nomina.salario_diario or "0",
                num_seguridad_social=nomina.numero_seguro_social or "",
                tipo_jornada=nomina.tipo_jornada.c_TipoJornada if nomina.tipo_jornada else None,
                cuenta_bancaria=nomina.cuenta_bancaria or "",
                banco=banco_val,
                puesto=nomina.puesto if nomina.puesto else None,
                sindicalizado=nomina.sindicalizado.opcion if hasattr(nomina.sindicalizado, "opcion") else None,
                departamento=nomina.departamento if nomina.departamento else None,
                salario_base_cot_apor=nomina.salario_base or "0",
                sub_contratacion=subcontratacion_list,
                registro_patronal_emisor=nomina.registro_patronal or None,
            ),
            incapacidades=incapacidades_list,
            percepciones=percepciones_obj,
            deducciones=deducciones_obj,
            otros_pagos=otro_pago_list,
            tipo_nomina=nomina.tipo_nomina.c_TipoNomina if nomina.tipo_nomina else "01",
            fecha_pago=nomina.fecha_pago or date(2020, 1, 31),
            fecha_final_pago=nomina.fecha_final_pago or date(2020, 1, 31),
            fecha_inicial_pago=nomina.fecha_inicial_pago or date(2020, 1, 16),
            num_dias_pagados=safe_decimal(nomina.numero_dias_pagados, '16.000')
        ),
        serie=comprobante_nomina.serie or 'A',
        folio=comprobante_nomina.folio or '1',
    )

    # Cambia el obj impuesto a 01 en vez de 03
    if hasattr(invoice, "get") and invoice.get("Conceptos"):
        conceptos = invoice["Conceptos"]
        if isinstance(conceptos, list):
            for concepto in conceptos:
                concepto['ObjetoImp'] = '01'
        elif isinstance(conceptos, dict):
            conceptos['ObjetoImp'] = '01'

    invoice_cfdi = invoice.process()

    # --- Parche para TotalSeparacionIndemnizacion (si quieres dejarlo también)
    percepciones = (
        invoice_cfdi
        .get("Complemento", {})
        .get("Nomina", {})
        .get("Percepciones")
    )
    hay_023 = False
    if isinstance(percepciones, dict):
        percepcion_items = percepciones.get('Percepcion', [])
        if isinstance(percepcion_items, dict):
            percepcion_items = [percepcion_items]
        hay_023 = any(p.get('TipoPercepcion') == '023' for p in percepcion_items)
    if hay_023 and "TotalSueldos" in percepciones:
        percepciones["TotalSeparacionIndemnizacion"] = percepciones.pop("TotalSueldos")

    #este es el que falla, si hace las cuentas bien pero truena al timbrar
    percepciones = (
    invoice_cfdi
    .get("Complemento", {})
    .get("Nomina", {})
    .get("Percepciones")
    )
    if isinstance(percepciones, dict):
        percepcion_items = percepciones.get('Percepcion', [])
        if isinstance(percepcion_items, dict):
            percepcion_items = [percepcion_items]
        hay_039_044 = any(p.get('TipoPercepcion') in ('039', '044') for p in percepcion_items)
        if hay_039_044:
            total_gravado = sum(Decimal(str(p.get("ImporteGravado", "0") or "0")) for p in percepcion_items)
            total_jubilacion = sum(
                Decimal(str(p.get("ImporteGravado", "0") or "0")) + Decimal(str(p.get("ImporteExento", "0") or "0"))
                for p in percepcion_items if p.get("TipoPercepcion") in ("039", "044")
            )
            percepciones["TotalSueldos"] = f"{(total_gravado - total_jubilacion):.2f}"
            percepciones["TotalJubilacionPensionRetiro"] = f"{total_jubilacion:.2f}"

    

    invoice_cfdi.sign(signer)
    
    return invoice_cfdi



# #funcion para obtener datos del comprobante de nómina 1.2
# def obtener_datos_comprobante_nomina12(id):
#     from datetime import date
#     from decimal import Decimal
#     from satcfdi.models import Signer
#     from satcfdi.create.cfd import cfdi40, nomina12
#     from dateutil.relativedelta import relativedelta
#     from django.db import models
#     from cfdi.models import (
#         ComprobanteNomina12, CertificadoSelloDigital, Nomina, Emisor,
#         Percepcion, Deduccion, OtroPago, Incapacidad, subcontratacion
#     )
#     # Start of patches version 1.0.0 
#     # ============= PATCHES =============
#     class ComprobanteSinFormaPago(cfdi40.Comprobante):
#         def __init__(self, *args, **kwargs):
#             if kwargs.get("tipo_de_comprobante") == "N":
#                 kwargs.pop("forma_pago", None)
#             super().__init__(*args, **kwargs)
#     cfdi40.Comprobante = ComprobanteSinFormaPago

#     class EmisorNominaPatch(nomina12.Emisor):
#         def __init__(self, *args, **kwargs):
#             rfc = kwargs.get("rfc", "")  # Asegúrate de pasar el RFC en la instancia
#             curp = kwargs.get("curp", "")
#             registro_patronal = kwargs.get("registro_patronal", "")
#             # Quitar CURP si está vacío o si es moral (longitud RFC = 12)
#             if not curp or len(rfc) == 12:
#                 kwargs.pop("curp", None)
#             # Quitar REGISTRO PATRONAL si es persona moral (RFC 12)
#             if len(rfc) == 12:
#                 kwargs.pop("registro_patronal", None)
#             super().__init__(*args, **kwargs)
#     nomina12.Emisor = EmisorNominaPatch

#     def make_receptor_nomina(**kwargs):
#         registro_patronal_emisor = kwargs.pop("registro_patronal_emisor", None)
#         if not (registro_patronal_emisor and str(registro_patronal_emisor).strip()):
#             kwargs.pop("num_seguridad_social", None)
#             kwargs.pop("fecha_inicio_rel_laboral", None)
#             kwargs.pop("antiguedad", None)
#             kwargs.pop("riesgo_puesto", None)
#             kwargs.pop("salario_diario_integrado", None)
#         return nomina12.Receptor(**kwargs)

#     class EntidadSNCFNominaPatch(nomina12.EntidadSNCF):
#         def __init__(self, *args, **kwargs):
#             origen_recurso = kwargs.get("origen_recurso", "")
#             # Si origen_recurso NO es IM, elimina monto_recurso_propio
#             if origen_recurso != "IM":
#                 kwargs.pop("monto_recurso_propio", None)
#             super().__init__(*args, **kwargs)
#     nomina12.EntidadSNCF = EntidadSNCFNominaPatch
#     # ====================================

#     # parche suma decimales

#     def safe_decimal(value, default='0'):
#         try:
#             if value is None or value == '':
#                 return Decimal(default)
#             return Decimal(value)
#         except Exception:
#             return Decimal(default)

#     def calcular_antiguedad(fecha_inicio, fecha_fin):
#         diferencia = relativedelta(fecha_fin, fecha_inicio)
#         partes = []
#         if diferencia.years:
#             partes.append(f"{diferencia.years}Y")
#         if diferencia.months:
#             partes.append(f"{diferencia.months}M")
#         if diferencia.days:
#             partes.append(f"{diferencia.days}D")
#         return "P" + "".join(partes) if partes else "P1D"

#     comprobante_nomina = ComprobanteNomina12.objects.get(id=id)
#     info_fiscal = comprobante_nomina.informacionFiscal
#     certificado = CertificadoSelloDigital.objects.filter(
#         informacionFiscal=info_fiscal, estado=True
#     ).order_by('-defecto', '-vigencia').first()
#     nomina = Nomina.objects.get(comprobanteNomina12=comprobante_nomina)
#     emisor_model = Emisor.objects.filter(comprobante=comprobante_nomina).first()

#     percepciones_qs = Percepcion.objects.filter(comprobanteNomina12=comprobante_nomina)
#     deducciones_qs = Deduccion.objects.filter(comprobanteNomina12=comprobante_nomina)
#     otros_pagos_qs = OtroPago.objects.filter(comprobanteNomina12=comprobante_nomina)
#     subcontrataciones_qs = subcontratacion.objects.filter(comprobanteNomina12=comprobante_nomina)

#     antiguedad_str = calcular_antiguedad(
#         nomina.fecha_inicio_relacion_laboral,
#         nomina.fecha_final_pago
#     )

#     # === EntidadSNCF
#     entidadsncf = None
#     if nomina.origen_recurso:
#         origen_recurso_val = str(nomina.origen_recurso.c_OrigenRecurso)
#         monto_recurso_propio_val = str(nomina.monto_recurso_propio) if nomina.monto_recurso_propio is not None else "0.00"
#         entidadsncf = nomina12.EntidadSNCF(
#             origen_recurso=origen_recurso_val,
#             monto_recurso_propio=monto_recurso_propio_val
#         )

#     # --- INCAPACIDADES ---
#     incapacidades_qs = Incapacidad.objects.filter(
#         models.Q(percepcion__comprobanteNomina12=comprobante_nomina) |
#         models.Q(Deduccion__comprobanteNomina12=comprobante_nomina)
#     ).distinct()
#     incapacidades_list = [
#         nomina12.Incapacidad(
#             tipo_incapacidad=i.tipo_incapacidad.c_TipoIncapacidad if i.tipo_incapacidad else "01",
#             dias_incapacidad=i.dias_incapacidad or 0,
#             importe_monetario=safe_decimal(getattr(i, 'importe_Monetario', 0), '0')
#         ) for i in incapacidades_qs if getattr(i, 'percepcion', None) or getattr(i, 'Deduccion', None)
#     ]
#     incapacidades_list = incapacidades_list if incapacidades_list else None

#     # --- SUBCONTRATACION ---
#     subcontratacion_list = [
#         nomina12.SubContratacion(
#             rfc_labora=sub.rfclaboral,
#             porcentaje_tiempo=sub.porcentaje
#         )
#         for sub in subcontrataciones_qs
#     ]
#     subcontratacion_list = subcontratacion_list if subcontratacion_list else None

#     # --- PERCEPCIONES ---
#     percepciones_list = []
#     for p in percepciones_qs:
#         tipo_percepcion = p.tipo_percepcion.c_TipoPercepcion if p.tipo_percepcion else "001"
#         horas_extra_list = [
#             nomina12.HorasExtra(
#                 tipo_horas=he.tipo_horas.c_TipoHoras if he.tipo_horas else "01",
#                 dias=he.dias or 0,
#                 horas_extra=he.horas_extra or 0,
#                 importe_pagado=safe_decimal(he.importe_pagado, '0')
#             ) for he in p.horas_extra.all()
#         ]
#         percepcion_kwargs = {
#             "tipo_percepcion": tipo_percepcion,
#             "clave": p.clave,
#             "concepto": p.tipo_percepcion.descripcion if p.tipo_percepcion else "DESCONOCIDO",
#             "importe_gravado": safe_decimal(p.importe_gravado, '0'),
#             "importe_exento": safe_decimal(p.importe_exento, '0'),
#             "horas_extra": horas_extra_list if horas_extra_list else None,
#         }
#         if tipo_percepcion == "045":
#             percepcion_kwargs["acciones_o_titulos"] = nomina12.AccionesOTitulos(
#                 valor_mercado=safe_decimal(p.importe_exento, '0'),
#                 precio_al_otorgarse=safe_decimal(p.importe_exento, '0'),
#             )
#         percepciones_list.append(nomina12.Percepcion(**percepcion_kwargs))
#     percepciones_obj = nomina12.Percepciones(percepcion=percepciones_list) if percepciones_list else None

#     # --- DEDUCCIONES ---
#     deducciones_list = [
#         nomina12.Deduccion(
#             tipo_deduccion=d.tipo_deduccion.c_TipoDeduccion if d.tipo_deduccion else "002",
#             clave=d.clave,
#             concepto=d.tipo_deduccion.descripcion if d.tipo_deduccion else "DESCONOCIDO",
#             importe=safe_decimal(d.importe, '0')
#         ) for d in deducciones_qs
#     ]
#     deducciones_obj = nomina12.Deducciones(deduccion=deducciones_list) if deducciones_list else None

#     # --- OTROS PAGOS ---
#     otro_pago_list = []
#     for op in otros_pagos_qs:
#         tipo_otro_pago_val = op.tipo_otro_pago.c_TipoOtroPago if op.tipo_otro_pago else "002"
#         subsidio_causado = safe_decimal(getattr(op, 'subsidioCausado', 0), '0')
#         if tipo_otro_pago_val == "002":
#             otro_pago = nomina12.OtroPago(
#                 tipo_otro_pago=tipo_otro_pago_val,
#                 clave=op.clave or "999",
#                 concepto=op.tipo_otro_pago.descripcion if op.tipo_otro_pago else "",
#                 importe=safe_decimal(op.importe, '0'),
#                 subsidio_al_empleo=safe_decimal(subsidio_causado),
#             )
#         else:
#             otro_pago = nomina12.OtroPago(
#                 tipo_otro_pago=tipo_otro_pago_val,
#                 clave=op.clave or "999",
#                 concepto=op.tipo_otro_pago.descripcion if op.tipo_otro_pago else "",
#                 importe=safe_decimal(op.importe, '0'),
#             )
#         otro_pago_list.append(otro_pago)
#     otro_pago_list = otro_pago_list if otro_pago_list else None

#     signer = Signer.load(
#         certificate=certificado.archivo_certificado.read(),
#         key=certificado.clave_privada.read(),
#         password=certificado.contrasena,
#     )

#     cuenta_bancaria = nomina.cuenta_bancaria or ""
#     if len(cuenta_bancaria) == 18 and cuenta_bancaria.isdigit():
#         banco_val = None
#     else:
#         banco_val = nomina.banco.c_Banco if nomina.banco else None

#     # ========== Crea el complemento de nómina ==========
#     complemento_nomina_obj = nomina12.Nomina(
#         emisor=nomina12.Emisor(
#             registro_patronal=nomina.registro_patronal or None,
#             curp=nomina.curp or "",
#             entidad_sncf=entidadsncf
#         ),
#         receptor=make_receptor_nomina(
#             curp=nomina.curp_trabajador or "",
#             clave_ent_fed=nomina.entidad_presto_servicio.c_Estado if nomina.entidad_presto_servicio else "",
#             num_empleado=nomina.numero_empleado or "",
#             periodicidad_pago=nomina.periodicidad.c_PeriodicidadPago if nomina.periodicidad else "",
#             tipo_contrato=nomina.tipo_contrato.c_TipoContrato if nomina.tipo_contrato else "01",
#             tipo_regimen=nomina.tipo_regimen.c_TipoRegimen if nomina.tipo_regimen else "02",
#             fecha_inicio_rel_laboral=nomina.fecha_inicio_relacion_laboral,
#             antiguedad=antiguedad_str or "P1D",
#             riesgo_puesto=str(nomina.riesgo_puesto.c_RiesgoPuesto) if nomina.riesgo_puesto else None,
#             salario_diario_integrado=nomina.salario_diario or "0",
#             num_seguridad_social=nomina.numero_seguro_social or "",
#             tipo_jornada=nomina.tipo_jornada.c_TipoJornada if nomina.tipo_jornada else None,
#             cuenta_bancaria=nomina.cuenta_bancaria or "",
#             banco=banco_val,
#             puesto=nomina.puesto if nomina.puesto else None,
#             sindicalizado=nomina.sindicalizado.opcion if hasattr(nomina.sindicalizado, "opcion") else None,
#             departamento=nomina.departamento if nomina.departamento else None,
#             salario_base_cot_apor=nomina.salario_base or "0",
#             sub_contratacion=subcontratacion_list,
#             registro_patronal_emisor=nomina.registro_patronal or None,
#         ),
#         incapacidades=incapacidades_list,
#         percepciones=percepciones_obj,
#         deducciones=deducciones_obj,
#         otros_pagos=otro_pago_list,
#         tipo_nomina=nomina.tipo_nomina.c_TipoNomina if nomina.tipo_nomina else "01",
#         fecha_pago=nomina.fecha_pago or date(2020, 1, 31),
#         fecha_final_pago=nomina.fecha_final_pago or date(2020, 1, 31),
#         fecha_inicial_pago=nomina.fecha_inicial_pago or date(2020, 1, 16),
#         num_dias_pagados=safe_decimal(nomina.numero_dias_pagados, '16.000')
#     )

#     # ==== Obtén los totales de manera segura ====
#     total_percepciones = safe_decimal(getattr(complemento_nomina_obj, 'TotalPercepciones', 0), '0')
#     total_otros_pagos  = safe_decimal(getattr(complemento_nomina_obj, 'TotalOtrosPagos', 0), '0')
#     total_deducciones  = safe_decimal(getattr(complemento_nomina_obj, 'TotalDeducciones', 0), '0')
#     valor_unitario = total_percepciones + total_otros_pagos
#     descuento = total_deducciones if total_deducciones > 0 else None

#     # ------------------- Generar Comprobante -------------------
#     invoice = cfdi40.Comprobante.nomina(
#         emisor=cfdi40.Emisor(
#             rfc=signer.rfc,
#             nombre=emisor_model.nombre,
#             regimen_fiscal=str(emisor_model.c_RegimenFiscal.c_RegimenFiscal),
#         ),
#         receptor=cfdi40.Receptor(
#             rfc=nomina.rfc_trabajador,
#             nombre=" ".join(filter(None, [nomina.nombre, nomina.apellido_paterno, nomina.apellido_materno])),
#             uso_cfdi="CN01",
#             domicilio_fiscal_receptor=str(nomina.c_CodigoPostal.c_CodigoPostal) if nomina.c_CodigoPostal else "00000",
#             regimen_fiscal_receptor="605"
#         ),
#         lugar_expedicion=comprobante_nomina.c_LugarExpedicion.c_CodigoPostal if comprobante_nomina.c_LugarExpedicion else "00000",
#         complemento_nomina=complemento_nomina_obj,
#         serie=comprobante_nomina.serie or 'A',
#         folio=comprobante_nomina.folio or '1',
#     )

#     # Fuerza ObjetoImp = '01' a todos los conceptos antes de firmar
#     if hasattr(invoice, "get") and invoice.get("Conceptos"):
#         conceptos = invoice["Conceptos"]
#         if isinstance(conceptos, list):
#             for concepto in conceptos:
#                 concepto['ObjetoImp'] = '01'
#                 # Parchea valor_unitario y descuento al concepto (opcional)
#                 concepto['ValorUnitario'] = str(valor_unitario)
#                 if descuento is not None:
#                     concepto['Descuento'] = str(descuento)
#         elif isinstance(conceptos, dict):
#             conceptos['ObjetoImp'] = '01'
#             conceptos['ValorUnitario'] = str(valor_unitario)
#             if descuento is not None:
#                 conceptos['Descuento'] = str(descuento)

#     invoice.sign(signer)
#     return invoice.process()







    #  # Crear el comprobante Nomina1.2 con todos los datos previos (emisor, percepciones_cfdi,deducciones_cfdi, otros_pagos_cfdi,nomina)
    # comprobante_nomina = nomina12.ComprobanteNomina12(
    #     emisor=emisor,
    #     receptor=nomina12.Receptor(
    #         rfc=nomina_model.receptor.rfc,
    #         nombre=nomina_model.receptor.nombre,
    #         curp=nomina_model.receptor.curp,
    #         regimen_fiscal_receptor=str(nomina_model.receptor.c_RegimenFiscalReceptor.c_RegimenFiscal),
    #         domicilio_fiscal_receptor=str(nomina_model.receptor.c_DomicilioFiscalReceptor.c_CodigoPostal)
    #     ),
    #     tipo_nomina=nomina.tipo_nomina,
    #     fecha_expedicion=comprobantenomina_model.fecha_expedicion,
    #     sello_emisor=comprobantenomina_model.sello_emisor or "",
    #     sello_sat=comprobantenomina_model.sello_sat or "",
    #     certificado=certificado.archivo_certificado.name if certificado else None,
    #     no_certificado=certificado.numero_certificado if certificado else None,
    #     nomina=nomina
    # )


   
    # percepcion_model = Percepcion.objects.filter(comprobante=comprobantenomina_model).first()
    # if not percepcion_model:
    #     print('No se encontró la percepción')
    #     return None
    
    
    
    # deduccion_model = Deduccion.objects.filter(comprobante=comprobantenomina_model).first()
    # if not deduccion_model:
    #     print('No se encontró la deducción')
    #     return None
    
    # otropago_model = OtroPago.objects.filter(comprobante=comprobantenomina_model).first()
    # if not otropago_model:
    #     print('No se encontró el otro pago')
    #     return None
    
    # subcontratacion_model = subcontratacion.objects.filter(comprobante=comprobantenomina_model).first()
    # if not subcontratacion_model:
    #     print('No se encontró la subcontratación')
    #     return None


# def obtener_datos_factura(id):
#     # Obtener el comprobante (antes FacturaElectronica)
#     comprobante_model = Comprobante.objects.get(id=id)
#     if not comprobante_model:
#         print('No se encontró el comprobante')
#         return None

#     # Receptor
#     receptor_model = Receptor.objects.filter(comprobante=comprobante_model).first()
#     if not receptor_model:
#         print('No se encontró el receptor')
#         return None

#     receptor = cfdi40.Receptor(
#         rfc=receptor_model.rfc,
#         nombre=receptor_model.nombre,
#         uso_cfdi=receptor_model.c_UsoCFDI.c_UsoCFDI,
#         domicilio_fiscal_receptor=str(receptor_model.c_DomicilioFiscalReceptor.c_CodigoPostal),
#         regimen_fiscal_receptor=str(receptor_model.c_RegimenFiscalReceptor.c_RegimenFiscal)
#     )

#     # Información del emisor
#     emisor_model = Emisor.objects.filter(comprobante=comprobante_model).first()
#     if not emisor_model:
#         print('No se encontró el emisor')
#         return None

#     # Obtener certificado desde la información fiscal
#     info_fiscal = comprobante_model.informacionFiscal
#     certificado = info_fiscal.idUserCFDI.idUserCFDI.certificados.first()

#     signer = Signer.load(
#         certificate=certificado.archivo_certificado.read(),
#         key=certificado.clave_privada.read(),
#         password=certificado.contrasena,
#     )

#     emisor = cfdi40.Emisor(
#         rfc=signer.rfc,
#         nombre=emisor_model.nombre,
#         regimen_fiscal=str(emisor_model.c_RegimenFiscal.c_RegimenFiscal)
#     )
#     print(f"Emisor: {signer.legal_name}")

#     print(f"Emisor: {emisor}")
#     # Crear conceptos
#     conceptos = []
#     for concepto_model in comprobante_model.conceptos.all():
#         concepto_cfdi = cfdi40.Concepto(
#             clave_prod_serv=concepto_model.c_ClaveProdServ.c_ClaveProdServ,
#             cantidad=Decimal(concepto_model.cantidad),
#             clave_unidad=concepto_model.c_ClaveUnidad.c_ClaveUnidad,
#             descripcion=concepto_model.descripcion,
#             valor_unitario=Decimal(concepto_model.valorUnitario),
#             unidad=concepto_model.unidad or "",
#             objeto_imp=concepto_model.c_ObjetoImp.c_ObjetoImp,
#             impuestos=cfdi40.Impuestos()
#         )
#         conceptos.append(concepto_cfdi)
        
#         print(f"Concepto: {comprobante_model.c_TipoDeComprobante}")

#     # Crear el comprobante CFDI
#     cfdi = cfdi40.Comprobante(
#         emisor=emisor,
#         lugar_expedicion=str(58000),
#         receptor=receptor,
#         metodo_pago=comprobante_model.c_MetodoPago.c_MetodoPago if comprobante_model.c_MetodoPago else None,
#         forma_pago=comprobante_model.c_FormaPago.c_FormaPago if comprobante_model.c_FormaPago else None,
#         serie=comprobante_model.serie or 'A',
#         folio=comprobante_model.folio or '1',
#         moneda=comprobante_model.c_Moneda.c_Moneda if comprobante_model.c_Moneda else 'MXN',
#         tipo_de_comprobante=comprobante_model.c_TipoDeComprobante.c_TipoDeComprobante,
#         exportacion=comprobante_model.c_Exportacion.c_Exportacion if comprobante_model.c_Exportacion else '01',
#         conceptos=conceptos,
#     )
    
#     print(f"Comprobante: {cfdi}")

#     # Firmar y procesar
#     cfdi.sign(signer)
#     cfdi = cfdi.process()
    
#     return cfdi
######################funciones admin personalizados

#funciones para filtrar por fecha
from django.contrib.auth import logout as auth_logout
def custom_logout(request):
    auth_logout(request)  # Llama al logout de Django
    return redirect(reverse_lazy('mi_admin:index'))  # Redirige al panel de administración




from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from cfdi.models import ClaveProdServ

@staff_member_required
def get_claveprodserv(request):
    clave_id = request.GET.get('id', None)
    if clave_id:
        clave = ClaveProdServ.objects.filter(pk=clave_id).first()
        if clave:
            return JsonResponse({'c_ClaveProdServ': clave.c_ClaveProdServ})
    return JsonResponse({}, status=404)


def get_claveunidad(request):
    clave_id = request.GET.get('id')
    try:
        clave = ClaveUnidad.objects.get(c_ClaveUnidad=clave_id)
        return JsonResponse({'nombre': clave.nombre})
    except ClaveUnidad.DoesNotExist:
        return JsonResponse({'error': 'ClaveUnidad no encontrada'}, status=404)


# @staff_member_required
# def verificar_comprobante(request):
#     uuid = request.GET.get('uuid', None)
#     rfc = request.GET.get('rfc', None)

#     if uuid and rfc:
#         comprobante = ComprobanteEmitido.objects.filter(uuid=uuid, rfc=rfc).first()
        
#         if comprobante:
#             # URL de archivos PDF y XML (si existen, genera las URLs correspondientes)
#             pdf_url = f"/media/pdfs/{comprobante.uuid}.pdf" if comprobante.xml_timbrado else None
#             xml_url = f"/media/xml/{comprobante.uuid}.xml" if comprobante.xml_timbrado else None

#             return JsonResponse({
#                 'existe': True,
#                 'uuid': comprobante.uuid,
#                 'fecha': comprobante.fecha.strftime('%Y-%m-%d %H:%M:%S'),
#                 'folio': comprobante.folio,
#                 'emisor_rfc': comprobante.rfc,
#                 'emisor_nombre': comprobante.nombre,
#                 'receptor_rfc': comprobante.rfc,  # Si hay otro campo para receptor, cámbialo aquí
#                 'receptor_nombre': comprobante.nombre,  # Si hay otro campo para receptor, cámbialo aquí
#                 'pdf_url': pdf_url,
#                 'xml_url': xml_url
#             })

#     return JsonResponse({'existe': False})



@staff_member_required
def verificar_comprobante(request):
    uuid = request.GET.get('uuid', None)
    rfc = request.GET.get('rfc', None)
    user = request.user

    if uuid and rfc:
        comprobante = ComprobanteEmitido.objects.filter(uuid=uuid, rfc=rfc, idUserCFDI=user).first()

        if comprobante:
            pdf_url = f"/media/pdfs/{comprobante.uuid}.pdf" if comprobante.xml_timbrado else None
            xml_url = f"/media/xml/{comprobante.uuid}.xml" if comprobante.xml_timbrado else None

            return JsonResponse({
                'existe': True,
                'uuid': comprobante.uuid,
                'fecha': comprobante.fecha.strftime('%Y-%m-%d %H:%M:%S'),
                'folio': comprobante.folio,
                'emisor_rfc': comprobante.rfc,
                'emisor_nombre': comprobante.nombre,
                'receptor_rfc': comprobante.rfc,  # Si usas otro campo para receptor, cámbialo aquí
                'receptor_nombre': comprobante.nombre,
                'pdf_url': pdf_url,
                'xml_url': xml_url
            })

    return JsonResponse({'existe': False})

def get_datos_codigo_postal(request):
    cp_id = request.GET.get('id')
    try:
        cp = CodigoPostal.objects.select_related('c_Estado', 'c_Municipio', 'c_Localidad').get(id=cp_id)
        return JsonResponse({
            'estado': str(cp.c_Estado) if cp.c_Estado else '',
            'municipio': str(cp.c_Municipio) if cp.c_Municipio else '',
            'localidad': str(cp.c_Localidad) if cp.c_Localidad else ''
        })
    except CodigoPostal.DoesNotExist:
        return JsonResponse({'error': 'Código Postal no encontrado'}, status=404)
    
    
def get_addenda_form(request):
    tipo = request.GET.get('tipo')
    id_addenda = request.GET.get('id_addenda')

    instancia = None
    addenda = None  # Asegura que siempre esté definida

    if id_addenda:
        try:
            addenda = Addenda.objects.get(id=id_addenda)
            if tipo == "siemens_gamesa":
                instancia = getattr(addenda, "siemens_gamesa", None)
            elif tipo == "grupo_ado":
                instancia = getattr(addenda, "grupo_ado", None)
            elif tipo == "waldos":
                instancia = getattr(addenda, "waldos", None)
            elif tipo == "terra_multitransportes":
                instancia = getattr(addenda, "terra_multitransportes", None)
        except Addenda.DoesNotExist:
            addenda = None

    if tipo == "siemens_gamesa":
        form = AddendaSiemensForm(instance=instancia) 
        html = render_to_string("LadoClientes/partials/addenda_siemens_form.html", {"form": form})

    elif tipo == "grupo_ado":
        form = AddendaGrupoADOForm(instance=instancia) 
        html = render_to_string("LadoClientes/partials/addenda_grupo_ado_form.html", {"form": form})

    elif tipo == "waldos":
        form = AddendaWaldosForm(instance=instancia)
        html = render_to_string("LadoClientes/partials/addenda_waldos_form.html", {"form": form})

    elif tipo == "terra_multitransportes":
        if addenda:
            queryset = AddendaTerraMultitransportes.objects.filter(addenda=addenda)
        else:
            queryset = AddendaTerraMultitransportes.objects.none()

        formset = AddendaTerraMultitransportesFormSet(queryset=queryset, prefix="terra")
        html = render_to_string("LadoClientes/partials/addenda_multitransportes_form.html", {
            "formset": formset,
        })

    else:
        html = "<p>Seleccione un tipo válido de addenda</p>"

    return JsonResponse({"html": html})







def get_percepcion_extra_form(request):
    print(">>> Entrando a get_incapacidad_percepcion_form")

    percepcion_id = request.GET.get('percepcion_id')
    print(f"📩 percepcion_id recibido: {percepcion_id}")

    percepcion = None
    if percepcion_id:
        try:
            percepcion = Percepcion.objects.get(id=percepcion_id)
            print(f"✅ Percepción encontrada: {percepcion}")
        except Percepcion.DoesNotExist:
            print("❌ Percepción no encontrada.")
    else:
        print("⚠️ No se recibió un ID de percepción válido.")

    if percepcion:
        relacionadas = percepcion.incapacidad.all()  # ← aquí corregido
        print(f"📦 Incapacidades relacionadas encontradas: {relacionadas.count()}")
        for inc in relacionadas:
            print(f" - Tipo: {inc.tipo_incapacidad}, Días: {inc.dias_incapacidad}, Importe: {inc.importe_Monetario}")
    else:
        print("🚫 No se puede consultar incapacidades, no hay percepción.")

    try:
        formset = IncapacidadFormSet(instance=percepcion, prefix="incapacidades_set")  # Usa el prefix que coincide con tu HTML
        print(f"🧾 Formset generado con {len(formset.forms)} formulario(s)")
    except Exception as e:
        print(f"❌ Error al generar formset: {e}")
        formset = None

    html = render_to_string("LadoClientes/partials/incapacidad_form.html", {
        "formset": formset,
        "percepcion": percepcion,
    })

    return JsonResponse({"html": html})




def get_separacion_indemnizacion_form(request):
    print(">>> Entrando a get_separacion_indemnizacion_form")

    percepcion_id = request.GET.get('percepcion_id')
    print(f"📩 percepcion_id recibido: {percepcion_id}")

    percepcion = None
    if percepcion_id:
        try:
            percepcion = Percepcion.objects.get(id=percepcion_id)
            print(f"✅ Percepción encontrada: {percepcion}")
        except Percepcion.DoesNotExist:
            print("❌ Percepción no encontrada.")
    else:
        print("⚠️ No se recibió un ID de percepción válido.")

    if percepcion:
        relacionadas = percepcion.separacion_indemnizacion.all()
        print(f"📦 Separaciones/Indemnizaciones relacionadas encontradas: {relacionadas.count()}")
        for sep in relacionadas:
            print(f" - Total pagado: {sep.total_pagado}, Años: {sep.num_anos_servicio}, Último sueldo: {sep.ultimo_sueldo_mens_ord}")
    else:
        print("🚫 No se puede consultar separaciones/indemnizaciones, no hay percepción.")

    try:
        formset = SeparacionIndemnizacionFormSet(instance=percepcion, prefix="separacionindemnizacion_set")
        print(f"🧾 Formset generado con {len(formset.forms)} formulario(s)")
    except Exception as e:
        print(f"❌ Error al generar formset: {e}")
        formset = None

    html = render_to_string("LadoClientes/partials/SeparacionIndemnizacion_form.html", {
        "separacionindemnizacion_formset": formset,
        "percepcion": percepcion,
    }, request=request)

    return JsonResponse({"html": html})




def get_jubilacion_pension_retiro_form(request):
    print(">>> Entrando a get_jubilacion_pension_retiro_form")

    percepcion_id = request.GET.get('percepcion_id')
    print(f"📩 percepcion_id recibido: {percepcion_id}")

    percepcion = None
    if percepcion_id:
        try:
            percepcion = Percepcion.objects.get(id=percepcion_id)
            print(f"✅ Percepción encontrada: {percepcion}")
        except Percepcion.DoesNotExist:
            print("❌ Percepción no encontrada.")
    else:
        print("⚠️ No se recibió un ID de percepción válido.")

    if percepcion:
        relacionadas = percepcion.jubilacion_pension_retiro.all()
        print(f"📦 Jubilaciones/Pensiones/Retiro relacionadas encontradas: {relacionadas.count()}")
        for jpr in relacionadas:
            print(f" - Total una exhibición: {jpr.total_una_exhibicion}, Acumulable: {jpr.ingreso_acumulable}, No acumulable: {jpr.ingreso_no_acumulable}")
    else:
        print("🚫 No se puede consultar jubilaciones/pensiones/retiro, no hay percepción.")

    try:
        formset = JubilacionPensionRetiroFormSet(instance=percepcion, prefix="jubilacionpensionretiro_set")
        print(f"🧾 Formset generado con {len(formset.forms)} formulario(s)")
    except Exception as e:
        print(f"❌ Error al generar formset: {e}")
        formset = None

    html = render_to_string("LadoClientes/partials/jubilacion_form.html", {
        "jubilacionpensionretiro_formset": formset,
        "percepcion": percepcion,
    }, request=request)

    return JsonResponse({"html": html})


#delete

# @require_POST
# @login_required
# def ajax_delete_otro_pago(request):
#     if not request.user.is_staff:
#         return HttpResponseForbidden("Solo administradores")
#     # Permitir uno o varios IDs
#     ids_json = request.POST.get("ids")
#     if ids_json:
#         import json
#         try:
#             ids = json.loads(ids_json)
#             objs = OtroPago.objects.filter(pk__in=ids)
#             deleted_count = objs.count()
#             objs.delete()
#             return JsonResponse({"success": True, "deleted": deleted_count})
#         except Exception as e:
#             return JsonResponse({"success": False, "error": str(e)})
#     else:
#         pk = request.POST.get("id")
#         try:
#             obj = OtroPago.objects.get(pk=pk)
#             obj.delete()
#             return JsonResponse({"success": True})
#         except OtroPago.DoesNotExist:
#             return JsonResponse({"success": False, "error": "No encontrado"})




# @require_POST
# @login_required
# def ajax_delete_subcontratacion(request):
#     if not request.user.is_staff:
#         return HttpResponseForbidden("Solo administradores")
#     ids_json = request.POST.get("ids")
#     if ids_json:
#         import json
#         try:
#             ids = json.loads(ids_json)
#             objs = subcontratacion.objects.filter(pk__in=ids)
#             deleted_count = objs.count()
#             objs.delete()
#             return JsonResponse({"success": True, "deleted": deleted_count})
#         except Exception as e:
#             return JsonResponse({"success": False, "error": str(e)})
#     else:
#         pk = request.POST.get("id")
#         try:
#             obj = subcontratacion.objects.get(pk=pk)
#             obj.delete()
#             return JsonResponse({"success": True})
#         except subcontratacion.DoesNotExist:
#             return JsonResponse({"success": False, "error": "No encontrado"})



# @require_POST
# @login_required
# def ajax_delete_deduccion(request):
#     if not request.user.is_staff:
#         return HttpResponseForbidden("Solo administradores")
#     ids_json = request.POST.get("ids")
#     if ids_json:
#         import json
#         try:
#             ids = json.loads(ids_json)
#             objs = Deduccion.objects.filter(pk__in=ids)
#             deleted_count = objs.count()
#             objs.delete()
#             return JsonResponse({"success": True, "deleted": deleted_count})
#         except Exception as e:
#             return JsonResponse({"success": False, "error": str(e)})
#     else:
#         pk = request.POST.get("id")
#         try:
#             obj = Deduccion.objects.get(pk=pk)
#             obj.delete()
#             return JsonResponse({"success": True})
#         except Deduccion.DoesNotExist:
#             return JsonResponse({"success": False, "error": "No encontrado"})
        

# @require_POST
# @login_required
# def ajax_delete_percepcion(request):
#     if not request.user.is_staff:
#         return HttpResponseForbidden("Solo administradores")
#     ids_json = request.POST.get("ids")
#     if ids_json:
#         import json
#         try:
#             ids = json.loads(ids_json)
#             objs = Percepcion.objects.filter(pk__in=ids)
#             deleted_count = objs.count()
#             objs.delete()
#             return JsonResponse({"success": True, "deleted": deleted_count})
#         except Exception as e:
#             return JsonResponse({"success": False, "error": str(e)})
#     else:
#         pk = request.POST.get("id")
#         try:
#             obj = Percepcion.objects.get(pk=pk)
#             obj.delete()
#             return JsonResponse({"success": True})
#         except Percepcion.DoesNotExist:
#             return JsonResponse({"success": False, "error": "No encontrado"})






def get_complemento_form(request):
    tipo = request.GET.get("tipo")
    index = request.GET.get("index")
    concepto_id = request.GET.get("concepto_id")

    concepto = None
    instancia = None
    context = {"index": index}
    print('tipo', tipo, 'index', index, 'concepto_id', concepto_id)

    # 🔎 Busca el concepto solo si existe
    try:
        concepto_id = int(concepto_id)
        concepto = Conceptos.objects.get(id=concepto_id)
        context["concepto"] = concepto
    except (TypeError, ValueError, Conceptos.DoesNotExist):
        concepto = None
        context["concepto"] = None


    if tipo == "cuenta_terceros":
        if concepto:
            instancia = ACuentaTerceros.objects.filter(idConcepto=concepto).first()
            print("Instancia A Cuenta de Terceros:", instancia)

        form = ACuentaTercerosForm(instance=instancia)
        context["form"] = form
        html = render_to_string("LadoClientes/partials/concepto_acuentaterceros_form.html", context)

    elif tipo == "cuenta_predial":
        queryset = CuentaPredial.objects.filter(idConcepto=concepto) if concepto else CuentaPredial.objects.none()
        formset = CuentaPredialFormSet(queryset=queryset, prefix=f"predial-{index}")

        #  Prellenar idConcepto en formularios
        if concepto:
            for form in formset.forms:
                form.initial['idConcepto'] = concepto.pk

        context["formset"] = formset
        html = render_to_string("LadoClientes/partials/concepto_cuentapredial_form.html", context)

    elif tipo == "informacion_aduanera":
        queryset = PedimentoCFDI.objects.filter(concepto=concepto) if concepto else PedimentoCFDI.objects.none()
        formset = PedimentoCFDIFormSet(queryset=queryset, prefix=f"aduana-{index}")

        #  Prellenar idConcepto
        if concepto:
            for form in formset.forms:
                form.initial['idConcepto'] = concepto.pk

        context["formset"] = formset
        html = render_to_string("LadoClientes/partials/concepto_informacionaduanera_form.html", context)

    elif tipo == "parte":
        queryset = Parte.objects.filter(idConcepto=concepto) if concepto else Parte.objects.none()
        formset = ParteFormSet(queryset=queryset, prefix=f"parte-{index}")

        #  Prellenar idConcepto
        if concepto:
            for form in formset.forms:
                form.initial['idConcepto'] = concepto.pk

        context["formset"] = formset
        html = render_to_string("LadoClientes/partials/concepto_parte_form.html", context)

    else:
        html = "<p>Tipo de complemento inválido</p>"

    return JsonResponse({"html": html})





class ClaveProdServAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Filtrar todos los objetos de ClaveProdServ
        qs = ClaveProdServ.objects.all()
        
        if self.q:
            # Buscar por código o descripción
            qs = qs.filter(
                models.Q(c_ClaveProdServ__icontains=self.q) |
                models.Q(descripcion__icontains=self.q)
            )
        
        return qs
    
    def get_result_label(self, item):
        return f"{item.c_ClaveProdServ} | {item.descripcion}"


class InformacionAduaneraAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Filtrar todos los objetos de InformacionAduanera
        qs = InformacionAduanera.objects.all()
        
        if self.q:
            # Buscar por aduana, patente o ejercicio
            qs = qs.filter(
                models.Q(aduana__descripcion__icontains=self.q) |
                models.Q(patente__c_PatenteAduanal__icontains=self.q) |
                models.Q(ejercicio__icontains=self.q)
            )
        
        return qs
    
    def get_result_label(self, item):
        return f"Aduana {item.aduana} - Patente {item.patente} - Ejercicio {item.ejercicio}"
    

# @login_required
# def activar_negocio(request, negocio_id):
    
#     usuario_cfdi = UsersCFDI.objects.get(idUserCFDI=request.user)
#     usuario_raiz = usuario_cfdi.get_raiz()
#     negocio = get_object_or_404(
#         InformacionFiscal,
#         id=negocio_id,
#         idUserCFDI__idUserCFDI=usuario_raiz,
#         activo=True
#     )

#     # Desactivar todos
#     InformacionFiscal.objects.filter(idUserCFDI__idUserCFDI=usuario_raiz).update(es_principal=False)

#     # Activar el nuevo
#     negocio.es_principal = True
#     negocio.save()

#     return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def activar_negocio(request, negocio_id):
    usuario_cfdi = UsersCFDI.objects.get(idUserCFDI=request.user)
    usuario_raiz = usuario_cfdi.get_raiz()

    negocio = get_object_or_404(
        InformacionFiscal,
        id=negocio_id,
        idUserCFDI=usuario_raiz,
        activo=True
    )

    # Guardar en base de datos
    usuario_cfdi.negocio_activo = negocio
    usuario_cfdi.save()
    
    print(f"Negocio activo cambiado a: {negocio} para usuario {usuario_cfdi}")

    return redirect(request.META.get('HTTP_REFERER', '/'))



class UUIDCancelacion:
    def __init__(self, uuid, motivo, folio_sustitucion):
        self.UUID = uuid
        self.Motivo = motivo
        self.FolioSustitucion = folio_sustitucion

def procesar_cancelacion_cfdi(emitido, motivo, uuid_original, ubicacion, ip, usercfdi, uuid_sustitucion=None, user_cfdi=None, service_plans=None):
    print('>>> Iniciando proceso de cancelación')
    infoFiscal = emitido.comprobante_relacionado.informacionFiscal
    csd = CertificadoSelloDigital.objects.get(informacionFiscal=infoFiscal, estado=True, defecto=True)

    # === Preparar certificado y llave ===
    with open(csd.archivo_certificado.path, 'rb') as f:
        cert = x509.load_der_x509_certificate(f.read(), default_backend())
    cert_base64 = base64.b64encode(cert.public_bytes(encoding=serialization.Encoding.PEM)).decode()

    plain_password = csd.get_plain_password()
    password_bytes = plain_password.encode() if plain_password else None
    with open(csd.clave_privada.path, 'rb') as f:
        private_key = serialization.load_der_private_key(f.read(), password=password_bytes, backend=default_backend())
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    key_base64 = base64.b64encode(private_bytes).decode()

    # === Cancelar ===
    uuid_obj = UUIDCancelacion(uuid_original, motivo, uuid_sustitucion)
    resultado = SoapServiceCancel.cancel(
        '', service_plans.supplierStamp.user, service_plans.supplierStamp.decrypt_password(),
        infoFiscal.rfc, cert_base64, key_base64, 0, [uuid_obj]
    )
    

    if "No Encontrado" in str(resultado.CodEstatus):
        print("El CFDI no fue encontrado, deteniendo ejecución.")
        return
    datos = extraer_datos_cancelacion(resultado)

    cancelacion, created = CancelacionCFDI.objects.get_or_create(
        comprobante=emitido,
        defaults={
            "uuid_original": datos["uuid_original"],
            "motivo": motivo,
            "uuid_sustitucion": uuid_sustitucion,
            "usuario": user_cfdi,
            "respuesta_sat": datos["respuesta_sat"],
            "exitoso": datos["exitoso"],
            "fecha_inicio_cancelacion": datos["fecha_inicio_cancelacion"],
            "fecha_ultimo_intento": datos["fecha_ultimo_intento"],
            "estado_cancelacion": datos["estado_cancelacion"],
        }
    )
    
    # SOLO actualizar la bitácora si se creó por primera vez
    if created:
        bitacora, _ = BitacoraCFDI.objects.get_or_create(comprobante=emitido.comprobante_relacionado)
        
        print('>>> Guardando en bitacora', usercfdi)
        print('>>> ubicacion', ubicacion)
        bitacora.ubicacion_cancelacion = ubicacion
        bitacora.ip_cancelacion = ip
        bitacora.cancelado_por = usercfdi
        bitacora.fecha_cancelacion = timezone.now() 
        bitacora.save()


    if not created:
        cancelacion.fecha_ultimo_intento = datos["fecha_ultimo_intento"]
        if datos.get("estado_cancelacion") is not None:
            cancelacion.estado_cancelacion = datos["estado_cancelacion"]
        cancelacion.exitoso = datos["exitoso"]
        cancelacion.save()


    estado = (datos.get("estado_cancelacion") or "").lower()
    if "cancelado" in estado or "plazo vencido" in estado:
        cancelacion.cancelado = True
        emitido.cancelado = True
        emitido.cod_estatus = "Correcta cancelación"
        cancelacion.save()
        emitido.save()
    elif created and datos.get("exitoso"):
        emitido.cancelado = True
        emitido.cod_estatus = "Pendiente de cancelación"
        emitido.save()

    return cancelacion, datos

def cancelar_comprobante(request):
     if request.method == 'POST':
        comprobante_id = request.POST.get('id')
        motivo = request.POST.get('motivo')
        uuid = request.POST.get('uuid')
        uuid_sustitucion = request.POST.get('uuid_sustitucion') or None
        
        lat = request.POST.get("lat")
        lon = request.POST.get("lon")
        ubicacion = f"{lat}, {lon}" if lat and lon else None
        ip = request.META.get("REMOTE_ADDR")

        emitido = ComprobanteEmitido.objects.get(id=comprobante_id)
        user_cfdi = UsersCFDI.objects.get(idUserCFDI=emitido.idUserCFDI)
        usercfdi = request.user
        
        user_services = user_cfdi.idUserServicePlan_id
        service_plans = Service_Plan.objects.filter(service=user_services.idService, plan=user_services.idPlan).first()

        cancelacion = procesar_cancelacion_cfdi(emitido, motivo, uuid, ubicacion, ip, usercfdi, uuid_sustitucion, user_cfdi, service_plans)

        messages.success(request, f"CFDI con folio {emitido.folio} cancelado exitosamente.")
        return redirect('mi_admin:cfdi_comprobanteemitido_changelist')
 
 
def extraer_datos_cancelacion(result) -> Dict[str, any]:
    """
    Extrae campos relevantes desde un objeto CancelaCFDIResult
    y devuelve un diccionario compatible con el modelo CancelacionCFDI.
    """

    # 1. Convertir la fecha del proceso (string ISO o datetime) a datetime aware
    fecha_inicio = make_aware(parse_date(str(result.Fecha)))

    # 2. Tomar el primer folio del resultado
    folio = result.Folios[0] if result.Folios else None

    uuid = folio.UUID if folio else ""
    estatus_uuid = folio.EstatusUUID if folio else ""
    estado_cancelacion = folio.EstatusCancelacion if folio else ""

    # 3. Interpretar si fue exitoso (estatus 201 = cancelado exitosamente)
    exitoso = estatus_uuid == "201"

    # 4. Guardar el acuse en texto plano si viene en la respuesta
    acuse_str = str(result.Acuse) if result.Acuse else None

    return {
        "uuid_original": uuid,
        "fecha_inicio_cancelacion": fecha_inicio,
        "fecha_ultimo_intento": fecha_inicio,  # ahora
        "estado_cancelacion": estado_cancelacion,
        "respuesta_sat": acuse_str,
        "exitoso": exitoso
    }
    
def obtener_cancelacion(request, id):
    comprobante = ComprobanteEmitido.objects.get(id=id)
    cancelacion = CancelacionCFDI.objects.filter(comprobante=comprobante).first()

    data = {
        "uuid": comprobante.uuid,
        "folio": comprobante.folio,
        "nombre": comprobante.nombre,
        "total": f"${comprobante.total:.2f}",
        "fecha": timezone.localtime(comprobante.fecha).strftime("%d-%m-%Y %H:%M"),
    }

    if cancelacion:
        data.update({
            "fecha_inicio": timezone.localtime(cancelacion.fecha_inicio_cancelacion).strftime("%Y-%m-%d %H:%M:%S") if cancelacion.fecha_inicio_cancelacion else '',
            "fecha_ultimo": timezone.localtime(cancelacion.fecha_ultimo_intento).strftime("%Y-%m-%d %H:%M:%S") if cancelacion.fecha_ultimo_intento else '',
            "estado_cancelacion": cancelacion.estado_cancelacion,
            "motivo": cancelacion.get_motivo_display(),
            "sustitucion": cancelacion.uuid_sustitucion,
            "estado_sat": "Cancelado" if cancelacion.cancelado else "En proceso",
            "estado_sat_color": "bg-danger" if cancelacion.exitoso else "bg-warning",
        })

    return JsonResponse(data)


def obtener_datos_cancelacion_modal(request, id):
    comprobante = ComprobanteEmitido.objects.get(id=id)

    data = {
        "uuid": comprobante.uuid,
        "folio": comprobante.folio,
        "nombre": comprobante.nombre,
        "total": f"${comprobante.total:.2f}",
        "fecha": timezone.localtime(comprobante.fecha).strftime("%d-%m-%Y %H:%M"),
    }

    return JsonResponse(data)


def actualizar_estatus_cancelaciones(request):
    usuario_cfdi = UsersCFDI.objects.get(idUserCFDI=request.user)
    usuario_raiz = usuario_cfdi.get_raiz()
    pendientes = CancelacionCFDI.objects.filter(usuario=usuario_raiz,cancelado=False)
    
    print(f"Actualizando {pendientes.count()} cancelaciones pendientes para el usuario {usuario_raiz.idUserCFDI.username}")

    for cancelacion in pendientes:
        emitido = cancelacion.comprobante
        user_cfdi = cancelacion.usuario
        user_services = user_cfdi.idUserServicePlan_id

        service_plans = Service_Plan.objects.filter(service=user_services.idService, plan=user_services.idPlan).first()

        procesar_cancelacion_cfdi(
            emitido,
            motivo=cancelacion.motivo,
            uuid_original=cancelacion.uuid_original,
            uuid_sustitucion=cancelacion.uuid_sustitucion,
            ubicacion = None, 
            ip = None, 
            usercfdi = None,
            user_cfdi=user_cfdi,
            service_plans=service_plans
        )
        

    return JsonResponse({"mensaje": "Cancelaciones actualizadas correctamente"})



@xframe_options_exempt
def ver_pdf_comprobante(request, pk):
    try:

        # Buscar el comprobante timbrado más reciente asociado a ese `pk`
        comprobante = ComprobanteEmitido.objects.filter(
            comprobante_relacionado=pk,
            uuid__isnull=False  # Solo si tiene UUID (timbrado)
        ).exclude(uuid="").order_by('-fecha').first()

        if not comprobante:
            return HttpResponseNotFound("No se encontró un comprobante timbrado para este CFDI.")

        # Parsear el XML
        cfdi = CFDI.from_string(comprobante.xml_timbrado.encode('utf-8'))

        # Generar el PDF
        pdf_content = render_comprobante_pdf_bytes(cfdi)

        return HttpResponse(pdf_content, content_type="application/pdf", headers={
            "Content-Disposition": "inline; filename=comprobante.pdf",
            "X-Frame-Options": "SAMEORIGIN",
        })

    except Exception as e:
        return HttpResponse(f"Error al generar el PDF: {str(e)}", status=500)
    

logger = logging.getLogger(__name__)


def _decode_contract_document(document):
    """Decode a manifest document that may arrive as base64 text or raw XML/PDF."""
    if not document:
        return None

    if isinstance(document, bytes):
        return document

    try:
        return base64.b64decode(document, validate=True)
    except (binascii.Error, ValueError):
        if isinstance(document, str):
            return document.encode('utf-8')
    return None


def _format_spanish_date(fecha):
    """Return a date formatted as '01 de Enero de 2024' in Spanish."""

    if fecha is None:
        fecha = timezone.localdate()

    meses = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ]

    mes = meses[fecha.month - 1]
    return f"{fecha.day:02d} de {mes} de {fecha.year}"


def _extract_signature_value(document):
    """Extract the SignatureValue from a contract XML document."""

    contenido = _decode_contract_document(document)
    if not contenido:
        return None

    try:
        root = ET.fromstring(contenido)
    except ET.ParseError:
        return None

    for element in root.iter():
        if isinstance(element.tag, str) and element.tag.endswith('SignatureValue'):
            value = (element.text or '').strip()
            if value:
                return value

    return None


from io import BytesIO
from typing import Optional
from django.utils import timezone
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT

def _build_contract_manifest_pdf(info_fiscal: Optional[InformacionFiscal]) -> bytes:
    """Genera el PDF del manifiesto de contrato con mejor formato visual."""

    # Datos base
    razon_social = (info_fiscal.razon_social or info_fiscal.nombre) if info_fiscal else "Razón Social"
    razon_social = razon_social.strip() or "Razón Social"
    rfc = info_fiscal.rfc.strip() if info_fiscal and info_fiscal.rfc else "RFC"
    fecha = _format_spanish_date(timezone.localdate())
    firma = _extract_signature_value(info_fiscal.manifiesto_contrato_xml) if info_fiscal else None
    firma = firma or "Firma disponible en el documento XML firmado."

    # Buffer PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER, leftMargin=50, rightMargin=50, topMargin=40)

    # Estilos
    styles = getSampleStyleSheet()
    titulo = ParagraphStyle('Titulo', parent=styles['Heading1'], alignment=TA_CENTER, spaceAfter=20)
    cuerpo = ParagraphStyle('Cuerpo', parent=styles['Normal'], alignment=TA_JUSTIFY, leading=15, spaceAfter=12)
    centrado = ParagraphStyle('Centrado', parent=styles['Normal'], alignment=TA_CENTER, spaceAfter=12)
    firma_style = ParagraphStyle('Firma', parent=styles['Normal'], alignment=TA_LEFT, spaceAfter=6, leading=14)

    elementos = []

    # Título
    elementos.append(Paragraph("MANIFIESTO", titulo))
    elementos.append(Spacer(1, 6))
    elementos.append(HRFlowable(width="100%", thickness=1, lineCap='round'))
    elementos.append(Spacer(1, 20))

    # Encabezado ciudad y fecha
    elementos.append(Paragraph(f"Ciudad de México, a {fecha}.", centrado))
    elementos.append(Spacer(1, 14))

    # Cuerpo del manifiesto
    contenido = f"""
    Por medio del presente <b>{razon_social}</b>, con Registro Federal de Contribuyentes <b>(RFC: {rfc})</b>,
    manifiesto mi conformidad y autorización para que la empresa <b>Centro de Validación Digital CVDSA, S.A. de C.V.</b>,
    Proveedor Autorizado de Certificación de CFDI con número de autorización <b>69901</b>, proceda a
    entregar al <b>Servicio de Administración Tributaria (SAT)</b> copia de los comprobantes fiscales que haya
    certificado, de acuerdo con lo establecido en la regla <b>2.7.2.7 de la Resolución Miscelánea Fiscal vigente</b>.
    """

    elementos.append(Paragraph(contenido, cuerpo))

    contenido2 = """
    Asimismo, acepto que Centro de Validación Digital CVDSA, S.A. de C.V. sea quien me proporcione, a mi nombre o
    al de mi representada, el <b>Servicio de Certificación para todos los Comprobantes Fiscales Digitales por Internet (CFDI)</b>
    que emita ya sea como persona física o moral.
    """

    elementos.append(Paragraph(contenido2, cuerpo))

    # Nota de servicio
    elementos.append(Spacer(1, 10))
    elementos.append(Paragraph(
        "<i>*Servicio de Certificación: validación y timbrado de CFDI.</i>",
        styles['Italic']
    ))
    elementos.append(Spacer(1, 30))

    # Firma
    elementos.append(Paragraph("<b>ATENTAMENTE</b>", centrado))
    elementos.append(Spacer(1, 40))
    elementos.append(Paragraph(f"<b>{razon_social.upper()}</b>", centrado))
    elementos.append(Spacer(1, 30))

    elementos.append(HRFlowable(width="50%", thickness=1, lineCap='round', hAlign='CENTER'))
    elementos.append(Spacer(1, 8))
    elementos.append(Paragraph("Firma del Contribuyente", centrado))
    elementos.append(Spacer(1, 15))

    elementos.append(Paragraph("<b>Firma Digital del cliente:</b>", firma_style))
    elementos.append(Paragraph(firma, firma_style))

    # Construcción final
    doc.build(elementos)
    buffer.seek(0)
    return buffer.read()


from io import BytesIO
from typing import Optional
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, ListFlowable, ListItem
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT

def _build_privacy_notice_pdf(info_fiscal: Optional[InformacionFiscal]) -> bytes:
    """Genera PDF profesional del Aviso de Privacidad."""

    from datetime import datetime
    import locale

    # ===== Locale español =====
    try:
        locale.setlocale(locale.LC_TIME, "es_MX.UTF-8")
    except:
        try:
            locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
        except:
            pass

    fecha_actual = datetime.now().strftime("%d de %B de %Y")

    razon_social = (info_fiscal.razon_social or info_fiscal.nombre) if info_fiscal else "Razón Social"
    razon_social = razon_social.strip() or "Razón Social"

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER, leftMargin=50, rightMargin=50, topMargin=40)

    # ===== Estilos =====
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle('h1', parent=styles['Heading1'], alignment=TA_CENTER, spaceAfter=18)
    text = ParagraphStyle('text', parent=styles['Normal'], alignment=TA_JUSTIFY, leading=15, spaceAfter=12)
    bold_center = ParagraphStyle('bold_center', parent=styles['Normal'], alignment=TA_CENTER, leading=14, spaceAfter=20)
    signature = ParagraphStyle('signature', parent=styles['Normal'], alignment=TA_LEFT, leading=14, spaceAfter=5)

    elems = []

    # ===== HEADER =====
    elems.append(Paragraph("AVISO DE PRIVACIDAD", h1))
    elems.append(HRFlowable(width="100%", thickness=1))
    elems.append(Spacer(1, 15))

    # ===== BODY CONTENT =====
    body = """
    Centro de Validación Digital CVDSA, S.A. de C.V., comercialmente conocida como <b>techfidg solutions</b>,
    Proveedor Autorizado Certificado por el <b>Servicio de Administración Tributaria (SAT)</b>, con domicilio en
    Montecito No. 38, Piso 25, Oficina 22, Interior A, Col. Nápoles, Alcaldía Benito Juárez,
    Ciudad de México, C.P. 03810; en cumplimiento con la Ley Federal de Protección de Datos
    Personales en Posesión de los Particulares, hace de su conocimiento que es responsable
    del tratamiento, uso y protección de los datos personales proporcionados.
    """
    elems.append(Paragraph(body, text))

    body2 = """
    Los datos recabados serán utilizados para fines de identificación, verificación, alta de usuarios,
    provisión de servicios contratados, relaciones comerciales y, en algunos casos, fines de mercadotecnia.
    """
    elems.append(Paragraph(body2, text))

    elems.append(Spacer(1, 8))
    elems.append(Paragraph("<b>Datos recabados:</b>", text))

    # ===== LISTS =====
    personal_data = [
        "Nombre completo",
        "Correos electrónicos",
        "Teléfono fijo o celular",
        "Cargo o puesto"
    ]

    fiscal_data = [
        "RFC",
        "Domicilio fiscal",
        "Teléfono de contacto",
        "Correo electrónico empresarial"
    ]

    elems.append(ListFlowable(
        [ListItem(Paragraph(item, text), bulletColor="#8f0d16") for item in personal_data],
        bulletType="bullet", spaceBefore=6
    ))

    elems.append(Spacer(1, 5))
    elems.append(Paragraph("<b>Datos fiscales o de razón social:</b>", text))

    elems.append(ListFlowable(
        [ListItem(Paragraph(item, text), bulletColor="#8f0d16") for item in fiscal_data],
        bulletType="bullet", spaceBefore=6
    ))

    # ===== MORE BODY =====
    body3 = """
    techfidg solutions podrá transferir esta información a terceros nacionales o internacionales, cuando sea
    necesario para el cumplimiento de obligaciones legales, relaciones comerciales o requerimientos
    por autoridad competente.
    """
    elems.append(Spacer(1, 12))
    elems.append(Paragraph(body3, text))

    body4 = """
    El usuario tiene derecho a ejercer los derechos <b>ARCO</b> (Acceso, Rectificación, Cancelación u Oposición),
    así como revocar su consentimiento en cualquier momento.
    """
    elems.append(Paragraph(body4, text))

    body5 = """
    Para ejercer estos derechos puede contactar al área de Atención al Cliente:
    <b> +52 1 55 4219 2712 2023-2025</b> o enviar su solicitud a:
    <b>techfidgsolutions1@gmail.com</b>
    """
    elems.append(Paragraph(body5, text))

    elems.append(Spacer(1, 18))
    elems.append(Paragraph("<b>Medidas de seguridad</b>", text))

    body6 = """
    Los datos son resguardados bajo protocolos de cifrado TLS 1.2, servidores seguros bajo HTTPS
    y certificados digitales exclusivos para Proveedores Autorizados del SAT, garantizando la
    confidencialidad, integridad y no repudio de la información.
    """
    elems.append(Paragraph(body6, text))

    elems.append(Spacer(1, 18))
    elems.append(Paragraph(
        "El titular de los datos manifiesta haber leído y aceptado este Aviso de Privacidad.",
        bold_center
    ))

    # ===== SIGNATURE =====
    elems.append(Spacer(1, 30))
    elems.append(Paragraph(razon_social.upper(), bold_center))
    elems.append(HRFlowable(width="50%", thickness=1, hAlign="CENTER"))
    elems.append(Spacer(1, 6))
    elems.append(Paragraph("Firma del titular", bold_center))

    elems.append(Spacer(1, 20))
    elems.append(Paragraph(
        f"<b>Fecha de última actualización:</b> {fecha_actual}",
        signature
    ))

    # ===== BUILD PDF =====
    doc.build(elems)
    buffer.seek(0)
    return buffer.read()





def _get_user_cfdi(
    user: User,
    include_supplier: bool = False,
) -> Optional[UsersCFDI]:
    """Fetch the UsersCFDI instance for the given Django user with the desired relations."""

    queryset = UsersCFDI.objects.filter(idUserCFDI=user)

    related_fields = ['negocio_activo']
    if include_supplier:
        related_fields.append('idUserServicePlan_id__idServicePlan__supplierStamp')

    if related_fields:
        queryset = queryset.select_related(*related_fields)

    return queryset.first()


def _get_informacion_fiscal_activa(user_cfdi: Optional[UsersCFDI]) -> Optional[InformacionFiscal]:
    """Return the active InformacionFiscal record associated with the provided UsersCFDI."""

    if user_cfdi is None:
        return None

    if user_cfdi.negocio_activo:
        return user_cfdi.negocio_activo

    return InformacionFiscal.objects.filter(
        idUserCFDI=user_cfdi,
        activo=True,
    ).first()


def _get_informacion_fiscal_por_rfc(
    user_cfdi: Optional[UsersCFDI],
    rfc: str,
) -> Optional[InformacionFiscal]:
    """Return the fiscal information for the RFC within the user hierarchy."""

    if user_cfdi is None or not rfc:
        return None

    return InformacionFiscal.objects.filter(
        idUserCFDI=user_cfdi,
        rfc__iexact=rfc,
        activo=True,
    ).order_by('-id').first()



@login_required(login_url="/mi-admin/login/")
def manifiesto(request):
    """Renderiza la vista con el manifiesto de aceptación."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'LadoClientes/pages/manifiesto.html',
        {
            'title': 'Manifiesto',
            'year': datetime.datetime.now().year,
        }
    )

def _build_qr_image(url):
    """Return a base64 PNG QR code for the provided URL."""

    if not url:
        return None

    try:
        qr = qrcode.QRCode(box_size=6, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        image = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        image.save(buffer, format="PNG")
    except Exception:
        logger.exception('No fue posible generar el código QR para la URL del manifiesto.')
        return None

    return base64.b64encode(buffer.getvalue()).decode('ascii')


def _get_manifest_qr_payload(request):
    """Resolve the QR signing URL and return its base64 image representation."""

    qr_target = getattr(settings, 'CFDI_MANIFIESTO_QR_URL', '').strip()

    if not qr_target:
        try:
            qr_target = request.build_absolute_uri(
                reverse('mi_admin:manifiesto_contrato_qr')
            )
        except Exception:
            qr_target = request.build_absolute_uri()

    qr_image = _build_qr_image(qr_target)

    if not qr_image:
        return None, None

    return qr_target, qr_image


def manifiesto_contrato_qr(request):
    """Muestra la página simplificada que se abre desde el código QR del manifiesto."""
    assert isinstance(request, HttpRequest)

    user_cfdi = _get_user_cfdi(request.user)

    if user_cfdi is None:
        messages.error(request, 'No se encontró la configuración de usuario para mostrar el manifiesto móvil.')
        return redirect('mi_admin:manifiesto_contrato')

    info_fiscal = _get_informacion_fiscal_activa(user_cfdi)

    if info_fiscal is None:
        messages.error(request, 'No existe información fiscal activa para mostrar en la vista móvil del manifiesto.')
        return redirect('mi_admin:manifiesto_contrato')

    nombre_razon = (info_fiscal.razon_social or info_fiscal.nombre or '').strip()
    if not nombre_razon:
        nombre_razon = 'Nombre o Razón Social'

    direccion_linea = ' '.join(filter(None, [
        info_fiscal.calle,
        f"#{info_fiscal.numero_exterior}" if info_fiscal.numero_exterior else '',
        f"Int. {info_fiscal.numero_interior}" if info_fiscal.numero_interior else '',
    ])).strip()

    direccion = ', '.join(filter(None, [
        direccion_linea,
        info_fiscal.colonia,
        info_fiscal.municipio,
        info_fiscal.estado,
        f"CP {info_fiscal.codigo_postal}" if info_fiscal.codigo_postal else '',
        info_fiscal.pais,
    ])) or 'Dirección no disponible'

    return render(
        request,
        'LadoClientes/pages/manifiesto_contrato_qr.html',
        {
            'title': 'Manifiesto - Firma móvil',
            'year': datetime.datetime.now().year,
            'qr_contract': {
                'nombre': nombre_razon,
                'rfc': (info_fiscal.rfc or '').upper(),
                'correo': info_fiscal.correo_electronico or '',
                'direccion': direccion,
            }
        }
    )




def _get_user_cfdi(
    user: User,
    include_supplier: bool = False,
) -> Optional[UsersCFDI]:
    """Fetch the UsersCFDI instance for the given Django user with the desired relations."""

    queryset = UsersCFDI.objects.filter(idUserCFDI=user)

    related_fields = ['negocio_activo']
    if include_supplier:
        related_fields.append('idUserServicePlan_id__idServicePlan__supplierStamp')

    if related_fields:
        queryset = queryset.select_related(*related_fields)

    return queryset.first()


def _get_informacion_fiscal_activa(user_cfdi: Optional[UsersCFDI]) -> Optional[InformacionFiscal]:
    """Return the active InformacionFiscal record associated with the provided UsersCFDI."""

    if user_cfdi is None:
        return None

    if user_cfdi.negocio_activo:
        return user_cfdi.negocio_activo

    return InformacionFiscal.objects.filter(
        idUserCFDI=user_cfdi,
        activo=True,
    ).first()


def _get_informacion_fiscal_por_rfc(
    user_cfdi: Optional[UsersCFDI],
    rfc: str,
) -> Optional[InformacionFiscal]:
    """Return the fiscal information for the RFC within the user hierarchy."""

    if user_cfdi is None or not rfc:
        return None

    return InformacionFiscal.objects.filter(
        idUserCFDI=user_cfdi,
        rfc__iexact=rfc,
        activo=True,
    ).order_by('-id').first()



@login_required(login_url="/mi-admin/login/")
def manifiesto_contrato(request):
    """Renderiza la ventana final del proceso de firma de contrato."""
    assert isinstance(request, HttpRequest)
    descargas = request.session.get('manifiesto_contrato_descargas', {})
    contrato_firmado = bool(descargas.get('xml') or descargas.get('pdf'))
    qr_url, qr_image = _get_manifest_qr_payload(request)
    return render(
        request,
        'LadoClientes/pages/manifiesto_contrato.html',
        {
            'title': 'Manifiesto - Paso 3 de 3',
            'year': datetime.datetime.now().year,
            'contract_signed': contrato_firmado,
            'contract_downloads': descargas,
            'contract_qr_image': qr_image,
            'contract_qr_url': qr_url,
        }
    )


@login_required(login_url="/mi-admin/login/")
def manifiesto_contrato_wizard(request):
    """Renderiza la página con el formulario intermedio del manifiesto."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'LadoClientes/pages/manifiesto_contrato_wizard.html',
        {
            'title': 'Manifiesto - Paso 2 de 3',
            'year': datetime.datetime.now().year,
        }
    )


@login_required(login_url="/mi-admin/login/")
@require_POST
def manifiesto_contrato_wizard_estado(request):
    """Valida si el RFC ya cuenta con un contrato firmado y expone las descargas disponibles."""
    assert isinstance(request, HttpRequest)

    try:
        payload = json.loads(request.body.decode('utf-8')) if request.body else {}
    except json.JSONDecodeError:
        return JsonResponse({'already_signed': False, 'error': 'Formato de datos inválido.'}, status=400)

    rfc = (payload.get('rfc') or '').strip().upper()
    if not rfc:
        request.session.pop('manifiesto_wizard_descargas', None)
        return JsonResponse({'already_signed': False, 'error': 'Ingresa un RFC válido.'}, status=400)

    user_cfdi = _get_user_cfdi(request.user, include_supplier=True)

    if user_cfdi is None:
        return JsonResponse({'already_signed': False, 'error': 'No se encontró la configuración de usuario.'}, status=400)

    service_plan = getattr(user_cfdi.idUserServicePlan_id, 'idServicePlan', None)
    supplier = getattr(service_plan, 'supplierStamp', None)

    if supplier is None:
        return JsonResponse({'already_signed': False, 'error': 'No hay un proveedor de firma configurado.'}, status=400)

    informacion_firmada = _get_informacion_fiscal_por_rfc(user_cfdi, rfc)
    
    print('>>> informacion_firmada', informacion_firmada)

    if informacion_firmada is None or not (
        informacion_firmada.confirmar_datos_cfdi or informacion_firmada.manifiesto_firmado
    ):
        request.session.pop('manifiesto_wizard_descargas', None)
        print(">>> NO PASA: no hay manifiesto firmado o no se confirmaron datos")
        resultado_pdf = cfdi_register.SignContractSOAP.get_documents(
                '',
                supplier.idSocio,
                rfc,
                'PDF'
            )
            
        
        
        if getattr(resultado_pdf, 'success', False) and getattr(resultado_pdf, 'contract', None):
            print('>>> resultado pdf ya se encontraba firmado en el webservice')
            documento_pdf = resultado_pdf.contract
            informacion_firmada.manifiesto_contrato_pdf = documento_pdf
            informacion_firmada.manifiesto_firmado = True
            InformacionFiscal.objects.filter(pk=informacion_firmada.pk).update(
                manifiesto_contrato_pdf=documento_pdf,
                manifiesto_firmado=True,
            )
        else:
            print(">>> NO PASA: no hay informacion firmada en el webservice")
            return JsonResponse({'already_signed': False})

    documento_pdf = (informacion_firmada.manifiesto_contrato_pdf or 'vacio')
    print('>>> documento_pdf existente en la base de datos')
    

    if not documento_pdf:
        print('>>> Obteniendo documentos firmados del manifiesto para el RFC', rfc)
        try:
            resultado_pdf = cfdi_register.SignContractSOAP.get_documents(
                '',
                supplier.idSocio,
                rfc,
                'PDF'
            )
            
            print('>>> resultado_pdf', resultado_pdf)
        except Exception:
            logger.exception('Error al obtener documentos firmados del manifiesto para el RFC %s', rfc)
            request.session.pop('manifiesto_wizard_descargas', None)
            return JsonResponse({
                'already_signed': True,
                'error': 'Este RFC ya firmó el contrato, pero no fue posible recuperar los documentos en este momento.'
            })

        if getattr(resultado_pdf, 'success', False) and getattr(resultado_pdf, 'contract', None):
            documento_pdf = resultado_pdf.contract
            informacion_firmada.manifiesto_contrato_pdf = documento_pdf
            informacion_firmada.manifiesto_firmado = True
            InformacionFiscal.objects.filter(pk=informacion_firmada.pk).update(
                manifiesto_contrato_pdf=documento_pdf,
                manifiesto_firmado=True,
            )
        else:
            mensaje = getattr(resultado_pdf, 'message', '') or 'Los documentos firmados no están disponibles.'
            request.session.pop('manifiesto_wizard_descargas', None)
            return JsonResponse({
                'already_signed': True,
                'error': mensaje
            })

    request.session['manifiesto_wizard_descargas'] = {
        'rfc': rfc,
        'pdf': documento_pdf
    }
    request.session.modified = True

    downloads = {
        'contract': reverse('mi_admin:manifiesto_wizard_descargar', kwargs={'tipo': 'contrato', 'rfc': rfc}),
        'privacy': reverse('mi_admin:manifiesto_wizard_descargar', kwargs={'tipo': 'privacidad', 'rfc': rfc})
    }

    return JsonResponse({
        'already_signed': True,
        'downloads': downloads,
        'rfc': rfc,
        'nombre': informacion_firmada.nombre,
        'razon_social': informacion_firmada.razon_social,
    })


@login_required(login_url="/mi-admin/login/")
def manifiesto_contrato_wizard_descargar(request, tipo, rfc):
    """Descarga los documentos firmados disponibles desde el paso 2 del manifiesto."""
    assert isinstance(request, HttpRequest)

    tipo = (tipo or '').lower()
    if tipo not in {'contrato', 'privacidad'}:
        raise Http404

    rfc = (rfc or '').strip().upper()
    descargas = request.session.get('manifiesto_wizard_descargas', {})
    documento = None

    user_cfdi = _get_user_cfdi(request.user)
    info_fiscal = _get_informacion_fiscal_por_rfc(user_cfdi, rfc) if user_cfdi else None

    if descargas.get('rfc', '').upper() == rfc:
        documento = descargas.get('pdf')

    if not documento and info_fiscal and info_fiscal.manifiesto_contrato_pdf:
        documento = info_fiscal.manifiesto_contrato_pdf

    if not documento and tipo != 'contrato':
        messages.error(request, 'No se encontraron documentos firmados para el RFC indicado.')
        return redirect('mi_admin:manifiesto_contrato_wizard')

    if tipo == 'contrato':
        contenido = _build_contract_manifest_pdf(info_fiscal)  # 👈 Contrato firmado
    else:
        contenido = _build_privacy_notice_pdf(info_fiscal)  # 👈 Aviso de privacidad


    if contenido is None:
        messages.error(request, 'El documento firmado no está disponible. Inténtalo nuevamente más tarde.')
        return redirect('mi_admin:manifiesto_contrato_wizard')

    nombre_archivo = 'Contrato_de_Servicio' if tipo == 'contrato' else 'Aviso_de_Privacidad'
    response = HttpResponse(contenido, content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="{nombre_archivo}_{rfc}.pdf"'
    )
    return response


@login_required(login_url="/mi-admin/login/")
@require_POST
def manifiesto_contrato_firmar(request):
    """Ejecuta el proceso de firma del manifiesto en el paso final."""
    assert isinstance(request, HttpRequest)

    user_cfdi = _get_user_cfdi(request.user, include_supplier=True)

    if user_cfdi is None:
        messages.error(request, 'No se encontró la configuración de usuario para firmar el manifiesto.')
        return redirect('mi_admin:manifiesto_contrato')

    info_fiscal = _get_informacion_fiscal_activa(user_cfdi)

    if info_fiscal is None:
        messages.error(request, 'No existe información fiscal activa para continuar con la firma.')
        return redirect('mi_admin:manifiesto_contrato')

    service_plan = getattr(user_cfdi.idUserServicePlan_id, 'idServicePlan', None)
    supplier = getattr(service_plan, 'supplierStamp', None)

    if supplier is None:
        messages.error(request, 'No hay un proveedor de firma configurado para este usuario.')
        return redirect('mi_admin:manifiesto_contrato')

    taxpayer_id = info_fiscal.rfc
    snid = supplier.idSocio

    request.session.pop('manifiesto_contrato_descargas', None)

    try:
        resultado_xml = cfdi_register.SignContractSOAP.get_documents(
            '',
            snid,
            taxpayer_id,
            'XML'
        )
    except Exception:
        logger.exception('Error al ejecutar la firma del manifiesto para el RFC %s', taxpayer_id)
        messages.error(request, 'Ocurrió un error al firmar el manifiesto. Inténtalo nuevamente más tarde.')
        return redirect('mi_admin:manifiesto_contrato')

    exito = getattr(resultado_xml, 'success', False)
    mensaje = getattr(resultado_xml, 'message', '') or 'El manifiesto se firmó correctamente.'
    descargas = {}

    if exito:
        contrato_xml = getattr(resultado_xml, 'contract', None)
        if contrato_xml:
            descargas['xml'] = contrato_xml
        try:
            resultado_pdf = cfdi_register.SignContractSOAP.get_documents(
                '',
                snid,
                taxpayer_id,
                'PDF'
            )
        except Exception:
            logger.exception('Error al obtener el PDF firmado del manifiesto para el RFC %s', taxpayer_id)
            messages.warning(request, 'El manifiesto se firmó, pero no fue posible obtener el PDF firmado en este momento.')
        else:
            if getattr(resultado_pdf, 'success', False):
                contrato_pdf = getattr(resultado_pdf, 'contract', None)
                if contrato_pdf:
                    descargas['pdf'] = contrato_pdf
            else:
                advertencia_pdf = getattr(resultado_pdf, 'message', '') or 'No fue posible obtener el PDF firmado.'
                messages.warning(request, f'El manifiesto se firmó, pero {advertencia_pdf}')

        campos_actualizados = set()
        if contrato_xml:
            info_fiscal.manifiesto_contrato_xml = contrato_xml
            campos_actualizados.add('manifiesto_contrato_xml')

        if descargas.get('pdf'):
            info_fiscal.manifiesto_contrato_pdf = descargas['pdf']
            campos_actualizados.add('manifiesto_contrato_pdf')

        if not info_fiscal.confirmar_datos_cfdi:
            info_fiscal.confirmar_datos_cfdi = True
            campos_actualizados.add('confirmar_datos_cfdi')

        if not info_fiscal.manifiesto_firmado:
            info_fiscal.manifiesto_firmado = True
            campos_actualizados.add('manifiesto_firmado')

        if campos_actualizados:
            info_fiscal.save(update_fields=sorted(campos_actualizados))
        if descargas:
            descargas['rfc'] = taxpayer_id
            request.session['manifiesto_contrato_descargas'] = descargas
            request.session.modified = True
        messages.success(request, mensaje)
    else:
        messages.warning(request, mensaje or 'No fue posible completar la firma del manifiesto.')

    return redirect('mi_admin:manifiesto_contrato')


@login_required(login_url="/mi-admin/login/")
def manifiesto_contrato_descargar_xml(request):
    descargas = request.session.get('manifiesto_contrato_descargas', {})
    documento = descargas.get('xml')
    rfc = descargas.get('rfc')

    if not documento or not rfc:
        user_cfdi = _get_user_cfdi(request.user)
        info_fiscal = _get_informacion_fiscal_activa(user_cfdi)
        if info_fiscal and info_fiscal.manifiesto_contrato_xml:
            documento = info_fiscal.manifiesto_contrato_xml
            rfc = info_fiscal.rfc

    if not documento:
        messages.error(request, 'No se encontró un XML firmado para descargar. Firma nuevamente el manifiesto.')
        return redirect('mi_admin:manifiesto_contrato')

    contenido = _decode_contract_document(documento)
    if contenido is None:
        messages.error(request, 'El archivo XML firmado no está disponible. Inténtalo nuevamente más tarde.')
        return redirect('mi_admin:manifiesto_contrato')

    rfc = (rfc or 'manifiesto').upper()
    response = HttpResponse(contenido, content_type='application/xml')
    response['Content-Disposition'] = f'attachment; filename="Manifiesto_{rfc}.xml"'
    return response


@login_required(login_url="/mi-admin/login/")
def manifiesto_contrato_descargar_pdf(request):
    descargas = request.session.get('manifiesto_contrato_descargas', {})
    documento = descargas.get('pdf')
    rfc = descargas.get('rfc')

    if not documento or not rfc:
        user_cfdi = _get_user_cfdi(request.user)
        info_fiscal = _get_informacion_fiscal_activa(user_cfdi)
        if info_fiscal and info_fiscal.manifiesto_contrato_pdf:
            documento = info_fiscal.manifiesto_contrato_pdf
            rfc = info_fiscal.rfc

    if not documento:
        messages.error(request, 'No se encontró un PDF firmado para descargar. Firma nuevamente el manifiesto.')
        return redirect('mi_admin:manifiesto_contrato')

    contenido = _decode_contract_document(documento)
    if contenido is None:
        messages.error(request, 'El archivo PDF firmado no está disponible. Inténtalo nuevamente más tarde.')
        return redirect('mi_admin:manifiesto_contrato')

    rfc = (rfc or 'manifiesto').upper()
    response = HttpResponse(contenido, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Manifiesto_{rfc}.pdf"'
    return response


login_required(login_url="/mi-admin/login/")
def manifiesto_contrato_descargar_privacidad(request):
    descargas = request.session.get('manifiesto_contrato_descargas', {})
    documento = descargas.get('privacy_notice')
    rfc = descargas.get('rfc')

    user_cfdi = _get_user_cfdi(request.user)
    info_fiscal = _get_informacion_fiscal_activa(user_cfdi) if user_cfdi else None

    if documento:
        contenido = _decode_contract_document(documento)
    else:
        contenido = _build_privacy_notice_pdf(info_fiscal)

    if contenido is None:
        messages.error(request, 'No fue posible generar el Aviso de Privacidad. Inténtalo nuevamente más tarde.')
        return redirect('mi_admin:manifiesto_contrato')

    if not rfc and info_fiscal:
        rfc = info_fiscal.rfc

    rfc = (rfc or 'manifiesto').upper()
    response = HttpResponse(contenido, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Aviso_de_Privacidad_{rfc}.pdf"'
    return response


@login_required(login_url="/mi-admin/login/")
def manifiesto_contrato_descargar_servicio(request):
    descargas = request.session.get('manifiesto_contrato_descargas', {})
    documento = descargas.get('contract_template')
    rfc = descargas.get('rfc')

    user_cfdi = _get_user_cfdi(request.user)
    info_fiscal = _get_informacion_fiscal_activa(user_cfdi) if user_cfdi else None

    if documento:
        contenido = _decode_contract_document(documento)
    else:
        contenido = _build_contract_manifest_pdf(info_fiscal)

    if contenido is None:
        messages.error(request, 'No fue posible generar el Contrato de Servicios. Inténtalo nuevamente más tarde.')
        return redirect('mi_admin:manifiesto_contrato')

    if not rfc and info_fiscal:
        rfc = info_fiscal.rfc

    rfc = (rfc or 'manifiesto').upper()
    response = HttpResponse(contenido, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Contrato_de_Servicios_{rfc}.pdf"'
    return response

from suds.client import Client
DEFAULT_MANIFIESTO_WSDL = config('URL_SIGNCONTRACT')

def _firmar_manifiesto_en_servicio(*, nombre: str, rfc: str, email: str, direccion: str, firma: str, snid=None):
    wsdl_url = getattr(settings, "MANIFIESTO_FIRMAR_WSDL", DEFAULT_MANIFIESTO_WSDL)
    client = Client(wsdl_url, cache=None)

    variaciones_kwargs = []
    kwargs_base = {
        "nombre": nombre,
        "taxpayer_id": rfc,
        "email": email,
        "direccion": direccion,
        "firma": firma,
    }
    if snid:
        kwargs_base["snid"] = snid
    variaciones_kwargs.append(kwargs_base)

    kwargs_alternativos = {
        "name": nombre,
        "rfc": rfc,
        "correo": email,
        "address": direccion,
        "signature": firma,
    }
    if snid:
        kwargs_alternativos["snid"] = snid
    variaciones_kwargs.append(kwargs_alternativos)

    last_exception = None
    for posibles_kwargs in variaciones_kwargs:
        try:
            argumentos_filtrados = {k: v for k, v in posibles_kwargs.items() if v not in (None, '')}
            return client.service.firmar(**argumentos_filtrados)
        except Exception as exc:  # pragma: no cover - dependiente del servicio externo
            last_exception = exc

    variaciones_args = []
    if snid:
        variaciones_args.append((snid, rfc, nombre, email, direccion, firma))
    variaciones_args.append((nombre, rfc, email, direccion, firma))

    for posibles_args in variaciones_args:
        try:
            return client.service.firmar(*posibles_args)
        except Exception as exc:  # pragma: no cover - dependiente del servicio externo
            last_exception = exc

    if last_exception:
        raise last_exception


def manifiesto(request):
    snid = request.GET.get('snid', '')

    # Generar QR con la URL hacia firmar_manifiesto incluyendo SNID
    firmar_url = reverse('mi_admin:firmar_manifiesto')
    if snid:
        firmar_url = f"{firmar_url}?snid={snid}"

    # ✅ Construcción del QR (Base64)
    qr = qrcode.make(firmar_url)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()
    qr_image = f"data:image/png;base64,{qr_base64}"

    contexto = {
        'title': 'Manifiesto',
        'qr_image': qr_image,
        'firmar_url': firmar_url,
        'snid': snid,
    }

    return render(request, 'LadoClientes/pages/manifiesto.html', contexto)

def firmar_manifiesto(request):
    snid = request.GET.get('snid') or request.POST.get('snid') or ''
    initial = {'snid': snid} if snid else {}

    if request.method == 'POST':
        form = ManifiestoFirmaForm(request.POST, initial=initial)
        if form.is_valid():
            datos = form.cleaned_data
            try:
                respuesta = _firmar_manifiesto_en_servicio(
                    nombre=datos['nombre'],
                    rfc=datos['rfc'],
                    email=datos['email'],
                    direccion=datos['direccion'],
                    firma=datos['firma'],
                    snid=datos.get('snid') or None,
                )
            except Exception as exc:  # pragma: no cover - dependiente del servicio externo
                form.add_error(None, f'No fue posible firmar el manifiesto: {exc}')
            else:
                valor_success = getattr(respuesta, 'success', None)
                if isinstance(valor_success, str):
                    valor_success = valor_success.lower() in ('true', '1', 'ok', 'success')
                elif valor_success is None:
                    valor_success = True

                mensaje_respuesta = (
                    getattr(respuesta, 'message', '')
                    or getattr(respuesta, 'mensaje', '')
                    or getattr(respuesta, 'error', '')
                )

                if valor_success:
                    messages.success(request, mensaje_respuesta or 'El manifiesto se firmó correctamente.')
                    return redirect('mi_admin:manifiesto')

                form.add_error(None, mensaje_respuesta or 'No se pudo firmar el manifiesto. Inténtalo de nuevo.')
    else:
        form = ManifiestoFirmaForm(initial=initial)

    contexto = {
        'form': form,
        'title': 'Firmar manifiesto',
        'firma_data_url': request.POST.get('firma', '') if request.method == 'POST' else '',
    }
    return render(request, 'LadoClientes/pages/firmar_manifiesto.html', contexto)

