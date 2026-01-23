"""
Definition of views.
"""

from datetime import datetime
import re
from sre_constants import IN
from django.shortcuts import render
from django.http import HttpRequest

from django.views.decorators.csrf import csrf_exempt
from django_soap.utils.SOAPHandlerBase import SoapResult
from spyne import Iterable, Uuid
from spyne.application import Application
from spyne.decorator import rpc
from spyne.model.complex import Array, ComplexModel, XmlAttribute
from spyne.model.primitive import Unicode, Integer, AnyXml, Ltree, String, Boolean, AnyDict
from spyne.protocol.soap import Soap11, Soap12
from spyne.protocol.xml import etree
from spyne.server.django import DjangoApplication
from spyne.service import ServiceBase

from django_soap.utils.client import SOAPClient

import lxml.etree as ET

from suds.client import Client
import logging
from decouple import config

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
        }
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title':'Contact',
            'message':'Your contact page.',
            'year':datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        }
    )

def some_view(request):
    # The variables needed are URL and HEADERS everything 
    # else is extra that you might need for your request
    client = SOAPClient(
        url='http://www.dneonline.com/calculator.asmx?wsdl',
        headers = {'content-type': 'application/soap+xml'}
    )

    # Load up your crafted XML template from your /templates folder
    # with the values it expects
    response = client.send_request('soap_request/test.xml', {'intA': 2, 'intB': 2})

    # The response is of SoapResult and you can get your items like
    value = (
        response
            .get('soap:Envelope')
            .get('soap:Body')
            .get('AddResponse')
            .get_value('AddResult')
    )
    return render(request,
                  'app/test_soap_client.html',
                  {'value': value}
                  )


class Incidencia(ComplexModel):
    _type_info = [
        ('IdIncidencia', String),
        ('RfcEmisor', String),
        ('Uuid', String),
        ('CodigoError', String),
        ('WorkProcessId', String),
        ('MensajeIncidencia', String),
        ('ExtraInfo', String),
        ('NoCertificadoPac', String),
        ('FechaRegistro', String),
    ]
    


class AcuseRecepcionCFDI(ComplexModel):
    _type_info = [
        ('xml', String),
        ('UUID', String),
        ('faultstring', String),
        ('Fecha', String),
        ('CodEstatus', String),
        ('faultcode', String),
        ('SatSeal', String),
        ('Incidencias', Array(Incidencia)),
        ('NoCertificadoSAT', String),
     
    ]
    


class SoapService(ServiceBase):
    @rpc(Unicode(nillable=False), _returns=Unicode)
    def hello(ctx, name):
        return 'Hello, {}'.format(name)

    @rpc(Integer(nillable=False), Integer(nillable=False), _returns=Integer)
    def sum(ctx, a, b):
        return int(a + b)

    @rpc(Unicode(nillable=False), Unicode(nillable=False), Unicode(nillable=False), _returns=AcuseRecepcionCFDI)
    def stamp(ctx, xml, username, password):
      
        # Consuming the stamp service
        url = config('URL_TIMBRADO')
        client = Client(url,cache=None)
        contenido = client.service.stamp(xml,username,password)        

        #arCFDI = client.factory.create('tns:stampResult')
        arCFDI = AcuseRecepcionCFDI()
        incids = []
        
        #print(str(contenido.UUID))
        
        for key, value in Client.dict(contenido).items():   
            print(key, "->", value)
            if key=='xml':
                arCFDI.xml = contenido.xml
            elif key=='UUID' :     
                arCFDI.UUID = contenido.UUID
            elif key == 'Fecha' :
                arCFDI.Fecha = contenido.Fecha
            elif key == 'CodEstatus' :
                arCFDI.CodEstatus = contenido.CodEstatus
            elif key == 'SatSeal' :
                arCFDI.SatSeal = contenido.SatSeal
            elif key == 'NoCertificadoSAT' :
                arCFDI.NoCertificadoSAT = contenido.NoCertificadoSAT
            elif (key=='Incidencias'):
                incit = contenido.Incidencias
                if not(incit is None) :
                    print(incit)
                    for value in incit:
                        incid = Incidencia()
                        print(value[1][0])
                        incid.IdIncidencia = value[1][0].IdIncidencia
                        incid.RfcEmisor = value[1][0].RfcEmisor
                        incid.Uuid = value[1][0].Uuid
                        incid.CodigoError = value[1][0].CodigoError
                        incid.WorkProcessId = value[1][0].WorkProcessId
                        incid.MensajeIncidencia = value[1][0].MensajeIncidencia
                        incid.ExtraInfo = value[1][0].ExtraInfo
                        incid.NoCertificadoPac = value[1][0].NoCertificadoPac
                        incid.FechaRegistro = value[1][0].FechaRegistro
            
                        incids.append(incid)
                
                        
                
            
        # arCFDI.xml = contenido.xml                
        # arCFDI.UUID = contenido.UUID
        # arCFDI.Fecha =  contenido.Fecha
        # arCFDI.CodEstatus =  contenido.CodEstatus
        # arCFDI.SatSeal =   contenido.SatSeal
        # arCFDI.NoCertificadoSAT =  contenido.NoCertificadoSAT
        
        # incit = contenido.Incidencias
        # if not(incit is None) :
        #     print(incit)
        #     for value in incit:
        #         incid = Incidencia()
        #         print(value[1][0])
        #         incid.IdIncidencia = value[1][0].IdIncidencia
        #         incid.RfcEmisor = value[1][0].RfcEmisor
        #         incid.Uuid = value[1][0].Uuid
        #         incid.CodigoError = value[1][0].CodigoError
        #         incid.WorkProcessId = value[1][0].WorkProcessId
        #         incid.MensajeIncidencia = value[1][0].MensajeIncidencia
        #         incid.ExtraInfo = value[1][0].ExtraInfo
        #         incid.NoCertificadoPac = value[1][0].NoCertificadoPac
        #         incid.FechaRegistro = value[1][0].FechaRegistro
            
        #         incids.append(incid)
                
                
        arCFDI.Incidencias = incids 
        

        # # # dictresp = result.value.items()
        # # # for key, value in dictresp :
        # # #     if (isinstance( value, dict)):
        # # #         incid = Incidencia()
        # # #         for key, value in value:
        # # #             incid[key.split(':')[1]] = value
        # # #         incids.append(incid)
        # # #     else:
        # # #         eval('arCFDI.' + key.split(':')[1] + ' = value')
                                
        return arCFDI
    


class UUID(ComplexModel):
    UUID = XmlAttribute(String)
    FolioSustitucion= XmlAttribute(String)
    Motivo= XmlAttribute(String)
    
class Folio(ComplexModel):
    _type_info = [
        ('UUID', String),
        ('EstatusUUID', String),
        ('EstatusCancelacion', String),
    ]
    
class CancelaCFDIResult(ComplexModel):
    _type_info = [
        ('Folios', Array(Folio)),
        ('Acuse', String),
        ('Fecha', String),
        ('RfcEmisor', String),
        ('CodEstatus', String),
    ]
    

class SoapServiceCancel(ServiceBase):
    
    @rpc(String(nillable=False), String(nillable=False), String(nillable=False), Unicode(nillable=False), Unicode(nillable=False), Boolean(nillable=False), Array(UUID), _returns=CancelaCFDIResult)
    def cancel(ctx, username, password, taxpayer_id, cer, key, store_pending, uuids=[]):
        logging.basicConfig(level=logging.INFO)
        logging.getLogger('suds.client').setLevel(logging.DEBUG)
        
        url = config('URL_CANCELACION')
        client = Client(url,cache=None)
        print(uuids)
        UUIDS_list = client.factory.create("ns0:UUIDArray")
        for uuid in uuids:
            invoices_obj = client.factory.create("ns0:UUID")
            invoices_obj._UUID=uuid.UUID
            invoices_obj._FolioSustitucion=uuid.FolioSustitucion
            invoices_obj._Motivo=uuid.Motivo
            UUIDS_list.UUID.append(invoices_obj)
        
        result = client.service.cancel(UUIDS_list, username, password, taxpayer_id, cer, key, store_pending)
        
        print(result)
        cancellCFDI = CancelaCFDIResult()
        _folios = []
        
        for k, v in Client.dict(result).items():
            if k=='Acuse' or k=='s0:Acuse':
                cancellCFDI.Acuse =  v 
            elif k=='Fecha' or k=='s0:Fecha':
                cancellCFDI.Fecha =  v  
            elif k=='RfcEmisor' or k=='s0:RfcEmisor':
                cancellCFDI.RfcEmisor =  v
            elif k=='CodEstatus' or k=='s0:CodEstatus':
                cancellCFDI.CodEstatus =  v        
            elif k=='Folios' or k=='s0:Folios':
                folios = v
                # print(v)
                if not(folios is None) :
                    for value in folios:
                        print(value)
                        print(value[1][0])
                        folio = Folio()
                        folio.UUID = value[1][0].UUID
                        folio.EstatusUUID = value[1][0].EstatusUUID
                        folio.EstatusCancelacion = value[1][0].EstatusCancelacion
                   
                        _folios.append(folio)
                
        
        cancellCFDI.Folios = _folios
                                
        return cancellCFDI


        # # The variables needed are URL and HEADERS everything 
        # # else is extra that you might need for your request
        # client = SOAPClient(
        #     url='https://demo-facturacion.finkok.com/servicios/soap/cancel.wsdl',
        #     headers = {'content-type': 'application/soap+xml'}
        # )
        # # # Load up your crafted XML template from your /templates folder
        # # # with the values it expects
        # # store_pending = 0
        # # uuids = [
        # #                         {'uuid': "0D0C5D40-F15C-5BCF-85AA-50BE8AAD81CE", 
        # #                          'folioSustitucion': "", 
        # #                          'motivo': "02" }
        # #                     ]

        # response = client.send_request('soap_request/cancel.xml', {
        #             'uuids': uuids ,
        #             'username': username, 
        #             'password': password,
        #             'taxpayer_id': taxpayer_id ,
        #             'cer': cer,
        #             'key': key,
        #             'store_pending': store_pending
        #         }          
        #         )
    
        # result = (response.get('senv:Envelope').get('senv:Body')
        #     .get('tns:cancelResponse')
        #     .get('tns:cancelResult')
        #     )

        # cancellCFDI = CancelaCFDIResult()
        # _folios = []
        
        # #arCFDI.xml =  ("", result.get_value('s0:xml'))[not(result.get_value('s0:xml')  is  None )]
        # cancellCFDI.Acuse =  result.get_value('s0:Acuse') if result.get_value('s0:Acuse')  else  ""
        # cancellCFDI.UUID =  result.get_value('s0:Fecha') if result.get_value('s0:Fecha') else "" 
        # cancellCFDI.RfcEmisor =  result.get_value('s0:RfcEmisor') if result.get_value('s0:RfcEmisor') else ""
        # cancellCFDI.CodEstatus =  result.get_value('s0:CodEstatus') if result.get_value('s0:CodEstatus') else ""        
        
        # folios = result.get('s0:Folios')
        # if not(folios is None) :
        #     for key, value in folios.value.items():
        #         folio = Folio()
        #         folio.UUID = value['s0:UUID']
        #         folio.EstatusUUID = value['s0:EstatusUUID']
        #         folio.EstatusCancelacion = value['s0:EstatusCancelacion']
                   
        #         _folios.append(folio)
                
        # #cancellCFDI.Incidencias = incids if bool(incids) else None
        # cancellCFDI.Folios = _folios
                                
        # return cancellCFDI


    
soap_app = Application(
    [SoapService],
    tns='soap.example.factupid',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11(),
)

soap_app_cancel = Application(
    [ SoapServiceCancel],
    tns='soap.example.factupid',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11(),
)

django_soap_application = DjangoApplication(soap_app)
django_soap_application_cancel = DjangoApplication(soap_app_cancel)
my_soap_application = csrf_exempt(django_soap_application)
my_soap_application_cancel = csrf_exempt(django_soap_application_cancel)
