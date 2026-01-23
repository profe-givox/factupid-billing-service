import pandas as pd
from django.core.management.base import BaseCommand
from datetime import date

class Command(BaseCommand):
    help = 'Cargar datos desde un archivo Excel a la base de datos'

    def handle(self, *args, **kwargs):
        from cfdi.models import FormaPago, VersionCFDI  # Importaciones locales

        # Leer el archivo Excel
        df = pd.read_excel(r'C:\Users\admin\Documents\FAC\factupid\catCFDI.xls', sheet_name='c_FormaPago')
        df.columns = df.columns.str.strip()  # Limpiar los nombres de las columnas

        # Obtener o crear VersionCFDI
        version_cfdi_id = 1  # Cambia este ID según sea necesario
        try:
            version_cfdi = VersionCFDI.objects.get(id=version_cfdi_id)
        except VersionCFDI.DoesNotExist:
            self.stdout.write(self.style.WARNING(f"No se encontró VersionCFDI con ID {version_cfdi_id}. Creando uno nuevo."))
            version_cfdi = VersionCFDI(
                version_cfdi="4.0",
                version_catalogo=1.0,
                revision_catalogo=0,
                fecha_publicacion_catalogo=date(2024, 9, 26),
                fecha_inicio_vigencia=date(2022, 1, 1)
            )
            version_cfdi.save()

        # Procesar los datos y guardarlos en la base de datos
        for index, row in df.iterrows():
            forma_pago = FormaPago(
                version_cfdi=version_cfdi,
                c_FormaPago=row['c_FormaPago'],
                descripcion=row['Descripción'],
                bancarizado=row['Bancarizado'] == 'Sí',  # Ajusta según tus datos
                numero_operacion=row['Número de operación'],
                rfc_emisor_cuenta_ordenante=row['RFC del Emisor de la cuenta ordenante'],
                cuenta_ordenante=row['Cuenta Ordenante'],
                patron_cuenta_ordenante=row['Patrón para cuenta ordenante'],
                rfc_emisor_cuenta_beneficiario=row['RFC del Emisor Cuenta de Beneficiario'],
                cuenta_beneficiario=row['Cuenta de Benenficiario'],
                patron_cuenta_beneficiaria=row['Patrón para cuenta Beneficiaria'],
                tipo_cadena_pago=row['Tipo Cadena Pago'],
                nombre_banco_emisor_extranjero=row['Nombre del Banco emisor de la cuenta ordenante en caso de extranjero'],
                fecha_inicio_vigencia=row['Fecha inicio de vigencia'],
                fecha_fin_vigencia=row['Fecha fin de vigencia']
            )
            forma_pago.save()  # Guardar en la base de datos

        self.stdout.write(self.style.SUCCESS('Datos cargados exitosamente desde Excel a la base de datos.'))
