from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

from django.forms import *
from django import forms
from console.models import Customer, User_Service,Plan
from invoice.models import Cliente, TimbreUserPerfil,  PerfilFiscalUser, Tokens


from django.contrib.auth.models import User

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
    
class ClienteForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            'nombre', 'correoElectronico', 'rfc', 'telefono', 'tipoDeCliente',
            'certificado', 'llave', 'contrasena', 'calle', 'noExterior', 'noInterior',
            'colonia', 'localidad', 'municipio', 'estado', 'codigoPostal'
        ]
        widgets = {
            'contrasena': forms.PasswordInput(),  # Para que el campo de contraseña se muestre como un campo de contraseña
        }



    
class ClientForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # for form in self.visible_fields():
        #     form.field.widget.attrs['class'] = 'col-md-5'
        #     form.field.widget.attrs['autocomplete'] = 'off'
        self.fields['nombre'].widget.attrs['autofocus'] = True

    class Meta:
        model = Cliente
        fields = '__all__'
        widgets = {
            'nombre': TextInput(
                attrs={
                    'placeholder': 'Ingrese un nombre',
                }
            ),
            'apellidoP': TextInput(
                attrs={
                    'placeholder': 'Ingrese un nombre',  
                }
            ),
            'tipoReceptor': forms.HiddenInput(),  # Ocultar este campo en el formulario
        }

class ClientMoralForm(ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Obtener el usuario del contexto
        super().__init__(*args, **kwargs)
        
        print(f"User: {user}")
        user_service = User_Service.objects.filter(idUser=user).first()
        print(f"User Service: {user_service}")

        self.fields['nombre'].widget.attrs['autofocus'] = True
        
        if self.instance and self.instance.rfc:
            self.fields['rfc'].widget.attrs['readonly'] = True
       
        # Filter file fields for .cer and .key extensions
        self.fields['Cer'].widget = forms.FileInput(attrs={'accept': '.cer'})
        self.fields['Key'].widget = forms.FileInput(attrs={'accept': '.key'})
        
        if user_service and user_service.idPlan.tipo == 'bajo consumo':
            print('es enterprise puede poner ondamant')
        else:
            print('el plan free y pro solo puede ser prepago')
            self.fields.pop('tipoCliente', None)  # Eliminar el campo del formulario
        
        # if user_service and user_service.idPlan.nombre in ['FREE', 'PRO']:
        #     print('el plan free y pro solo puede ser prepago')
        #     self.fields.pop('tipoCliente', None)  # Eliminar el campo del formulario
        # elif user_service and user_service.idPlan.nombre == 'Enterprise':
        #     print('es enterprise puede poner ondamant')
            # Aquí podrías agregar lógica para manejar el plan Enterprise


        # for form in self.visible_fields():
        #     form.field.widget.attrs['class'] = 'col-md-5'
        #     form.field.widget.attrs['autocomplete'] = 'off'
        

    class Meta:
        model = Cliente
        fields = '__all__'
        widgets = {
            'nombre': TextInput(
                attrs={
                    'placeholder': 'Ingrese un nombre',
                }
            ),
            'passphrase': PasswordInput(
                attrs={'placeholder': 'Ingrese passphrase', 'autocomplete': 'new-password'}
            ),
            'tipoReceptor': forms.HiddenInput(),  # Ocultar este campo en el formulario
            'apellidoP': forms.HiddenInput(),  # Ocultar este campo en el formulario
            'apellidoM': forms.HiddenInput(),  # Ocultar este campo en el formulario
            'pais': forms.HiddenInput(),  # Ocultar este campo en el formulario
            'curp': forms.HiddenInput(),  # Ocultar este campo en el formulario
            'cer_base64': forms.HiddenInput(),  # Ocultar este campo en el formulario
            'key_base64': forms.HiddenInput(),  # Ocultar este campo en el formulario
        }

class ClientFisicoForm(ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Obtener el usuario del contexto
        super().__init__(*args, **kwargs)
        
        print(f"User: {user}")
        user_service = User_Service.objects.filter(idUser=user).first()
        print(f"User Service: {user_service}")

        self.fields['nombre'].widget.attrs['autofocus'] = True
        
        if self.instance and self.instance.rfc:
            self.fields['rfc'].widget.attrs['readonly'] = True

        # Filter file fields for .cer and .key extensions
        self.fields['Cer'].widget = forms.FileInput(attrs={'accept': '.cer'})
        self.fields['Key'].widget = forms.FileInput(attrs={'accept': '.key'})
        
        if user_service and user_service.idPlan.tipo == 'bajo consumo':
            print('es enterprise puede poner ondamant')
        else:
            print('el plan free y pro solo puede ser prepago')
            self.fields.pop('tipoCliente', None)  # Eliminar el campo del formulario
            
        # if user_service and user_service.idPlan.nombre in ['FREE', 'PRO']:
        #     print('el plan free y pro solo puede ser prepago')
        #     self.fields.pop('tipoCliente', None)  # Eliminar el campo del formulario
        # elif user_service and user_service.idPlan.nombre == 'Enterprise':
        #     print('es enterprise puede poner ondamant')
            # Aquí podrías agregar lógica para manejar el plan Enterprise
        # for form in self.visible_fields():
        #     form.field.widget.attrs['class'] = 'col-md-5'
        #     form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = Cliente
        fields = '__all__'
        widgets = {
            'nombre': TextInput(
                attrs={
                    'placeholder': 'Ingrese un nombre',
                }
            ),
            'apellidoP': TextInput(
                attrs={
                    'placeholder': 'Ingrese un nombre',  
                }
            ),
            'passphrase': PasswordInput(
                attrs={'placeholder': 'Ingrese passphrase', 'autocomplete': 'new-password'}
            ),
            'tipoReceptor': forms.HiddenInput(),  # Ocultar este campo en el formulario
            'pais': forms.HiddenInput(),  # Ocultar este campo en el formulario
            'cer_base64': forms.HiddenInput(),  # Ocultar este campo en el formulario
            'key_base64': forms.HiddenInput(),  # Ocultar este campo en el formulario
        }

class ClientExtranjeroForm(ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Obtener el usuario del contexto
        super().__init__(*args, **kwargs)
        
        print(f"User: {user}")
        user_service = User_Service.objects.filter(idUser=user).first()
        print(f"User Service: {user_service}")

        self.fields['nombre'].widget.attrs['autofocus'] = True
        
        if self.instance and self.instance.rfc:
            self.fields['rfc'].widget.attrs['readonly'] = True

        # Filter file fields for .cer and .key extensions
        self.fields['Cer'].widget = forms.FileInput(attrs={'accept': '.cer'})
        self.fields['Key'].widget = forms.FileInput(attrs={'accept': '.key'})
        
        if user_service and user_service.idPlan.tipo == 'bajo consumo':
            print('es enterprise puede poner ondamant')
        else:
            print('el plan free y pro solo puede ser prepago')
            self.fields.pop('tipoCliente', None)  # Eliminar el campo del formulario
            
        # if user_service and user_service.idPlan.nombre in ['FREE', 'PRO']:
        #     print('el plan free y pro solo puede ser prepago')
        #     self.fields.pop('tipoCliente', None)  # Eliminar el campo del formulario
        # elif user_service and user_service.idPlan.nombre == 'Enterprise':
        #     print('es enterprise puede poner ondamant')
            # Aquí podrías agregar lógica para manejar el plan Enterprise
        # for form in self.visible_fields():
        #     form.field.widget.attrs['class'] = 'col-md-5'
        #     form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = Cliente
        fields = '__all__'
        widgets = {
            'nombre': TextInput(
                attrs={
                    'placeholder': 'Ingrese un nombre',
                }
            ),
            'apellidoP': TextInput(
                attrs={
                    'placeholder': 'Ingrese un nombre',  
                }
            ),
            'passphrase': PasswordInput(
                attrs={'placeholder': 'Ingrese passphrase', 'autocomplete': 'new-password'}
            ),
            'tipoReceptor': forms.HiddenInput(),  # Ocultar este campo en el formulario
            'curp': forms.HiddenInput(),  # Ocultar este campo en el formulario
            'cer_base64': forms.HiddenInput(),  # Ocultar este campo en el formulario
            'key_base64': forms.HiddenInput(),  # Ocultar este campo en el formulario
        }
        
        
        
        
############################# SE AGREGO UNA REVISION DE EXISTENCIA DE USUARIO EN LA LINEA 273 Y TAMBIEN SE OCULTARON LOS CAMPOS DE FIRMAS Y CER CON KEY CON EXCLUDE



class PerfilMoralForm(ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Obtener el usuario del contexto
        super().__init__(*args, **kwargs)

        self.fields['nombre'].widget.attrs['autofocus'] = True
        
        # Filter file fields for .cer and .key extensions
        self.fields['Cer'].widget = forms.FileInput(attrs={'accept': '.cer'})
        self.fields['Key'].widget = forms.FileInput(attrs={'accept': '.key'})
         
        if self.instance and self.instance.rfc:
            self.fields['rfc'].widget.attrs['readonly'] = True

        # # Obtener el plan del usuario
        # user_service = User_Service.objects.filter(idUser=user).first()
        # if user_service and user_service.idPlan.nombre in ['FREE', 'PRO']:
        #     self.fields.pop('tipoCliente', None)  # Eliminar el campo del formulario


    class Meta:
        model = PerfilFiscalUser
        fields = '__all__'
        exclude = ['cer_base64', 'key_base64', 'fecha', 'estado_firma', 'contratoXML', 'contratoPDF', 'token', 'estatus', 'validado', 'tipoCliente']
        widgets = {
            'nombre': TextInput(attrs={'placeholder': 'Ingrese un nombre'}),
            'tipoReceptor': forms.HiddenInput(),
            'apellidoP': forms.HiddenInput(),
            'apellidoM': forms.HiddenInput(),
            'pais': forms.HiddenInput(),
            'curp': forms.HiddenInput(),
            'regimen_Fiscal': forms.HiddenInput(),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)

        if commit:
            try:
                # Obtener el plan del usuario
                user_service = User_Service.objects.filter(idUser=self.instance.user).first()
                plan_name = user_service.idPlan.nombre if user_service else None
                plan_tipo = user_service.idPlan.tipo if user_service else None

                facturas = user_service.idPlan.limite_operaciones_plan # Ilimitado

                # Guardar la instancia
                instance.save()

                # Verificar si ya existe un TimbreUserPerfil para este usuario y servicio
                if not TimbreUserPerfil.objects.filter(userInvoice=instance.user, idUser_ServicePlan=user_service).exists():
                    # Crear el objeto TimbreUserPerfil automáticamente si no existe
                    TimbreUserPerfil.objects.create(
                        userInvoice=instance.user,  # Ajuste para usar userInvoice
                        idUser_ServicePlan=user_service,  # Asignar el User_Service
                        stamp=facturas,
                        # isOnDemmand=(plan_name == 'Enterprise' or plan_name == 'PRO' or plan_name == 'FREE')  # Marcar como True para todos estos planes
                        isOnDemmand=(plan_tipo == 'Bajo consumo' or plan_tipo == 'bajo consumo')
                    )

            except Exception as e:
                raise ValidationError(str(e))

        return instance

class PerfilFisicoForm(PerfilMoralForm):
    # Hereda de PerfilMoralForm y tiene la misma lógica de inicialización y guardado
    class Meta:
        model = PerfilFiscalUser
        exclude = ['cer_base64', 'key_base64', 'fecha', 'estado_firma', 'contratoXML', 'contratoPDF', 'token', 'estatus', 'validado']
        fields = '__all__'
        widgets = {
            'nombre': TextInput(attrs={'placeholder': 'Ingrese un nombre'}),
            'apellidoP': TextInput(attrs={'placeholder': 'Ingrese un apellido'}),
            'tipoReceptor': forms.HiddenInput(),
            'pais': forms.HiddenInput(),
            'regimen_Fiscal': forms.HiddenInput(),
        }





##################################### REGIMENES FISCALES ########################################


class RegimenFiscalForm(forms.ModelForm):
    
    class Meta:
        model =  PerfilFiscalUser
        fields = ['regimen_Fiscal']
        widgets = {
            'regimen_Fiscal': forms.Select(
                attrs={
                    'placeholder': 'Seleccione un régimen fiscal',
                }
            ),
        }

class TokensForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # for form in self.visible_fields():
        #     form.field.widget.attrs['class'] = 'col-md-5'
        #     form.field.widget.attrs['autocomplete'] = 'off'
        self.fields['nombre'].widget.attrs['autofocus'] = True

    class Meta:
        model = Tokens
        fields = ['nombre', 'userName', 'taxpayer_id', 'estatus']  # Excluir 'idUser'
        widgets = {
            'nombre': TextInput(
                attrs={
                    'placeholder': 'Ingrese un nombre',
                }
            ),
            'userName': TextInput(
                attrs={
                    'placeholder': 'Ingrese un nombre de usuario',  
                }
            ),
            'taxpayer_id': TextInput(
                attrs={
                    'placeholder': 'Ingrese un RFC',  
                }
            )
        }

class TokensResetForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # for form in self.visible_fields():
        #     form.field.widget.attrs['class'] = 'col-md-5'
        #     form.field.widget.attrs['autocomplete'] = 'off'
        self.fields['nombre'].widget.attrs['autofocus'] = True

    class Meta:
        model = Tokens
        fields = ['nombre', 'userName', 'taxpayer_id']  # Excluir los campos que no estan presentes
        widgets = {
            'nombre': TextInput(
                attrs={
                    'placeholder': 'Ingrese un nombre',
                }
            ),
            'userName': TextInput(
                attrs={
                    'placeholder': 'Ingrese un nombre de usuario',  
                }
            ),
            'taxpayer_id': TextInput(
                attrs={
                    'placeholder': 'Ingrese un RFC',  
                }
            )
        }

class TokensUPdateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # for form in self.visible_fields():
        #     form.field.widget.attrs['class'] = 'col-md-5'
        #     form.field.widget.attrs['autocomplete'] = 'off'
        self.fields['nombre'].widget.attrs['autofocus'] = True

    class Meta:
        model = Tokens
        fields = ['nombre', 'userName', 'taxpayer_id', 'estatus']  # Excluir 'idUser'
        widgets = {
            'nombre': TextInput(
                attrs={
                    'placeholder': 'Ingrese un nombre',
                }
            ),
            'userName': TextInput(
                attrs={
                    'placeholder': 'Ingrese un nombre de usuario',  
                }
            ),
            'taxpayer_id': TextInput(
                attrs={
                    'placeholder': 'Ingrese un RFC',  
                }
            ),
            'estatus': forms.HiddenInput()  # Establece estatus como HiddenInput
        }
    
    def clean(self):
        cleaned_data = super().clean()

        # Cambiar el valor de estatus si el objeto ya existe
        if self.instance and self.instance.pk:
            current_status = self.instance.estatus
            new_status = 'false' if current_status == 'true' else 'true'
            cleaned_data['estatus'] = new_status

        return cleaned_data
    