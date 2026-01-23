import base64
import binascii
from django import forms
from django.utils import timezone
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .models import *
from django.forms import modelformset_factory, inlineformset_factory
from dal import autocomplete
from django.contrib.admin.widgets import AdminDateWidget


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Requerido. Proporciona una dirección de correo electrónico válida.')

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')


class LoginForm(forms.Form):
    identifier = forms.EmailField(label='Correo electrónico')
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)

class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'Username'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Password'}))

class SendEmailResetPasswordForm(forms.Form):
    email = forms.EmailField(max_length=254, label='Correo electrónico')

class ResetPasswordForm2(forms.Form):
    password = forms.CharField(max_length=254,widget=forms.PasswordInput, label='Nueva contraseña')
    password2 = forms.CharField(max_length=254,widget=forms.PasswordInput, label='Confirmar contraseña')
    
    
    
class InformacionFiscalForm(forms.ModelForm):


    class Meta:
        model = InformacionFiscal
        fields = '__all__'
        exclude = ['user']  # Excluye cualquier campo llamado 'user'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'confirmar_datos_cfdi': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ignorar_validacion_sociedad': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'rfc': forms.TextInput(attrs={'class': 'form-control'}),
            'curp': forms.TextInput(attrs={'class': 'form-control'}),
            'razon_social': forms.TextInput(attrs={'class': 'form-control'}),
            'regimen_fiscal': forms.SelectMultiple(attrs={'class': 'form-control'}), 
            'regimen_receptor': forms.Select(attrs={'class': 'form-control'}),
            'calle': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_exterior': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_interior': forms.TextInput(attrs={'class': 'form-control'}),
            'colonia': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control'}),
            'municipio': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.TextInput(attrs={'class': 'form-control'}),
            'pais': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo_postal': forms.TextInput(attrs={'class': 'form-control'}),
            'referencia': forms.TextInput(attrs={'class': 'form-control'}),
            'clave_pais': forms.TextInput(attrs={'class': 'form-control'}),
            'residencia_fiscal': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'correo_electronico': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['curp'].required = False
        



class AddendaSiemensForm(forms.ModelForm):
    class Meta:
        model = AddendaSiemensGamesa
        fields = '__all__'
        exclude = ['addenda']

class AddendaGrupoADOForm(forms.ModelForm):
    class Meta:
        model = AddendaGrupoADO
        fields = '__all__'

class AddendaWaldosForm(forms.ModelForm):
    class Meta:
        model = AddendaWaldos
        fields = '__all__'


class AddendaTerraMultitransportesForm(forms.ModelForm):
     class Meta:
        model = AddendaTerraMultitransportes
        fields = '__all__'
        widgets = {
            'addenda': forms.HiddenInput()
        }
        
AddendaTerraMultitransportesFormSet = modelformset_factory(
    AddendaTerraMultitransportes,
    form=AddendaTerraMultitransportesForm,
    extra=1,
    max_num=1,
    can_delete=True
    
)


class ACuentaTercerosForm(forms.ModelForm):
    class Meta:
        model = ACuentaTerceros
        fields = "__all__"
        max_num=1
        extra=1


class InformacionAduaneraForm(forms.ModelForm):
    class Meta:
        model = InformacionAduanera
        fields = '__all__'
        widgets = {
            'fecha_inicio_vigencia': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control border border-secondary'
            }, format='%Y-%m-%d'),
            'fecha_fin_vigencia': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control border border-secondary'
            }, format='%Y-%m-%d'),
            'idConcepto': forms.HiddenInput(),
        }

        
InformacionAduaneraFormSet = modelformset_factory(
    InformacionAduanera, 
    form=InformacionAduaneraForm,
    extra=1, 
    can_delete=True,
    max_num=1,
)

class PedimentoCFDIForm(forms.ModelForm):
    class Meta:
        model = PedimentoCFDI
        fields = '__all__'
        widgets = {
            'fecha_inicio_vigencia': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control border border-secondary'
            }, format='%Y-%m-%d'),
            'fecha_fin_vigencia': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control border border-secondary'
            }, format='%Y-%m-%d'),
            'concepto': forms.HiddenInput(),
        }

        
PedimentoCFDIFormSet = modelformset_factory(
    PedimentoCFDI, 
    form=PedimentoCFDIForm,
    extra=1, 
    can_delete=True,
    max_num=1,
)

CuentaPredialFormSet = modelformset_factory(
    CuentaPredial, 
    fields="__all__", 
    extra=1, 
    can_delete=True,
    max_num=1,
)

ComplementoConceptoFormSet = modelformset_factory(
    ComplementoConcepto, 
    fields="__all__", 
    extra=1, 
    can_delete=True,
    max_num=1,
)

class ParteForm(forms.ModelForm):
    class Meta:
        model = Parte
        fields = '__all__'
        widgets = {
            'claveProdServ': autocomplete.ModelSelect2(
                url='cfdi:claveprodserv-autocomplete',
                attrs={'data-theme': 'admin-autocomplete',
                    'class': 'admin-autocomplete border border-secondary'}
            ),
            'informacionAduanera': autocomplete.ModelSelect2(
                url='cfdi:informacionaduanera-autocomplete',
                attrs={'class': 'form-control'}
            ),
        }

ParteFormSet = modelformset_factory(
    Parte, 
    form = ParteForm,
    fields="__all__", 
    extra=1, 
    can_delete=True,
    max_num=1,
)



class IncapacidadForm(forms.ModelForm):
    class Meta:
        model = Incapacidad
        # Elimina 'percepcion' de los fields
        fields = ['tipo_incapacidad', 'dias_incapacidad', 'importe_Monetario']

# El formset lo puedes importar donde lo uses:
IncapacidadFormSet = inlineformset_factory(
    Percepcion, Incapacidad,
    form=IncapacidadForm,
    fields=['tipo_incapacidad', 'dias_incapacidad', 'importe_Monetario'],
    extra=1,
    can_delete=True
)


class SeparacionIndemnizacionForm(forms.ModelForm):
    class Meta:
        model = SeparacionIndemnizacion
        fields = [
            'total_pagado',
            'num_anos_servicio',
            'ultimo_sueldo_mens_ord',
            'ingreso_acumulable',
            'ingreso_no_acumulable',
        ]

SeparacionIndemnizacionFormSet = inlineformset_factory(
    Percepcion, SeparacionIndemnizacion,
    form=SeparacionIndemnizacionForm,
    fields=[
        'total_pagado',
        'num_anos_servicio',
        'ultimo_sueldo_mens_ord',
        'ingreso_acumulable',
        'ingreso_no_acumulable',
    ],
    extra=1,
    can_delete=True
)



class JubilacionPensionRetiroForm(forms.ModelForm):
    class Meta:
        model = JubilacionPensionRetiro
        fields = [
            'total_una_exhibicion',
            'ingreso_acumulable',
            'ingreso_no_acumulable',
        ]

JubilacionPensionRetiroFormSet = inlineformset_factory(
    Percepcion, JubilacionPensionRetiro,
    form=JubilacionPensionRetiroForm,
    fields=[
        'total_una_exhibicion',
        'ingreso_acumulable',
        'ingreso_no_acumulable',
    ],
    extra=1,
    can_delete=True
)



class ManifiestoFirmaForm(forms.Form):
    nombre = forms.CharField(
        label='Nombre o Razón Social',
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre o Razón Social'}),
    )
    rfc = forms.CharField(
        label='RFC',
        max_length=13,
        widget=forms.TextInput(attrs={'class': 'form-control text-uppercase', 'placeholder': 'RFC'}),
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@dominio.com'}),
    )
    direccion = forms.CharField(
        label='Dirección',
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección'}),
    )
    snid = forms.CharField(widget=forms.HiddenInput(), required=False)
    firma = forms.CharField(widget=forms.HiddenInput(), required=False)

    def clean_nombre(self):
        return self.cleaned_data['nombre'].strip()

    def clean_rfc(self):
        rfc = self.cleaned_data['rfc'].strip().upper()
        if len(rfc) not in (12, 13):
            raise forms.ValidationError('El RFC debe tener 12 o 13 caracteres.')
        return rfc

    def clean_direccion(self):
        return self.cleaned_data['direccion'].strip()

    def clean_firma(self):
        firma = (self.cleaned_data.get('firma') or '').strip()
        if not firma:
            raise forms.ValidationError('Debes ingresar la firma antes de firmar el manifiesto.')

        if ',' in firma:
            _, firma = firma.split(',', 1)

        try:
            base64.b64decode(firma, validate=True)
        except (binascii.Error, ValueError):
            raise forms.ValidationError('La firma enviada tiene un formato inválido.')

        return firma