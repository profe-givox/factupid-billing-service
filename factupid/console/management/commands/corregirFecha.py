from django.core.management.base import BaseCommand
from cfdi.models import CodigoPostal,PatenteAduanal
from datetime import date

# class Command(BaseCommand):
#     help = (
#         'Actualiza la fecha_inicio_vigencia de 07/01/2019 a 01/07/2019 y '
#         'cuenta cuántos registros tienen fechas en el año 2021.'
#     )

#     def handle(self, *args, **kwargs):
#         # Definir las fechas
#         fecha_incorrecta = date(2019, 1, 7)  # 07/01/2019
#         fecha_correcta = date(2019, 7, 1)    # 01/07/2019

#         # 1. Actualizar fechas incorrectas
#         codigos_postales = CodigoPostal.objects.filter(fecha_inicio_vigencia=fecha_incorrecta)
#         updated_count = codigos_postales.update(fecha_inicio_vigencia=fecha_correcta)

#         # Mostrar el resultado de la actualización
#         if updated_count > 0:
#             self.stdout.write(self.style.SUCCESS(
#                 f'Se actualizaron {updated_count} registros con la nueva fecha {fecha_correcta}.'
#             ))
#         else:
#             self.stdout.write(self.style.WARNING('No se encontraron registros con la fecha 07/01/2019.'))

#         # 2. Contar registros con fechas en el año 2021
#         count_2021 = CodigoPostal.objects.filter(
#             fecha_inicio_vigencia__year=2021
#         ).count()

#         # Mostrar el resultado del conteo
#         self.stdout.write(self.style.SUCCESS(
#             f'Se encontraron {count_2021} registros con fechas en el año 2021.'
#         ))




# class Command(BaseCommand):
#     help = (
#         'Intercambia el día y mes de la fecha de inicio de vigencia, y '
#         'cuenta cuántos registros tienen fechas en el año 2021.'
#     )

#     def handle(self, *args, **kwargs):
#         # 1. Identificar y corregir fechas mal formateadas
#         registros = PatenteAduanal.objects.all()
#         updated_count = 0

#         for registro in registros:
#             fecha = registro.inicio_vigencia

#             # Si la fecha es ambigua, intentamos intercambiar día y mes
#             if self._is_ambiguous(fecha):
#                 nueva_fecha = self._swap_day_month(fecha)
#                 registro.inicio_vigencia = nueva_fecha
#                 registro.save()
#                 updated_count += 1
#                 print(f"Actualizado: {fecha} -> {nueva_fecha}")

#         # Mostrar el resultado de las actualizaciones
#         if updated_count > 0:
#             self.stdout.write(self.style.SUCCESS(
#                 f'Se actualizaron {updated_count} registros con fechas corregidas.'
#             ))
#         else:
#             self.stdout.write(self.style.WARNING('No se encontraron fechas para corregir.'))

#         # 2. Contar registros con fechas en el año 2021
#         count_2021 = CodigoPostal.objects.filter(
#             fecha_inicio_vigencia__year=2021
#         ).count()

#         # Mostrar el resultado del conteo
#         self.stdout.write(self.style.SUCCESS(
#             f'Se encontraron {count_2021} registros con fechas en el año 2021.'
#         ))

#     def _is_ambiguous(self, fecha):
#         """Determina si una fecha es ambigua (día y mes intercambiables)."""
#         # Si el día es menor o igual a 12, es posible que esté mal formateada
#         return fecha.day <= 12

#     def _swap_day_month(self, fecha):
#         """Intercambia el día y el mes de una fecha."""
#         return date(fecha.year, fecha.day, fecha.month)


# class Command(BaseCommand):
#     help = (
#         'Intercambia el día y mes de la fecha de inicio de vigencia, y '
#         'cuenta cuántos registros tienen fechas en el año 2021.'
#     )

#     def handle(self, *args, **kwargs):
#         # 1. Identificar y corregir fechas mal formateadas
#         registros = CodigoPostal.objects.all()
#         updated_count = 0

#         for registro in registros:
#             fecha = registro.fecha_inicio_vigencia

#             # Verifica que la fecha no sea None
#             if fecha is not None and self._is_ambiguous(fecha):
#                 nueva_fecha = self._swap_day_month(fecha)
#                 registro.fecha_inicio_vigencia = nueva_fecha
#                 registro.save()
#                 updated_count += 1
#                 print(f"Actualizado: {fecha} -> {nueva_fecha}")

#         # Mostrar el resultado de las actualizaciones
#         if updated_count > 0:
#             self.stdout.write(self.style.SUCCESS(
#                 f'Se actualizaron {updated_count} registros con fechas corregidas.'
#             ))
#         else:
#             self.stdout.write(self.style.WARNING('No se encontraron fechas para corregir.'))

#         # 2. Contar registros con fechas en el año 2021
#         count_2021 = CodigoPostal.objects.filter(
#             fecha_inicio_vigencia__year=2021
#         ).count()

#         # Mostrar el resultado del conteo
#         self.stdout.write(self.style.SUCCESS(
#             f'Se encontraron {count_2021} registros con fechas en el año 2021.'
#         ))

#     def _is_ambiguous(self, fecha):
#         """Determina si una fecha es ambigua (día y mes intercambiables)."""
#         # Asegúrate de que fecha no sea None antes de intentar acceder a sus atributos
#         if fecha is None:
#             return False
#         # Si el día es menor o igual a 12, es posible que esté mal formateada
#         return fecha.day <= 12

#     def _swap_day_month(self, fecha):
#         """Intercambia el día y el mes de una fecha."""
#         return date(fecha.year, fecha.month, fecha.day) 



# class Command(BaseCommand):
#     help = (
#         'Intercambia el día y mes de la fecha de inicio de vigencia, y '
#         'cuenta cuántos registros tienen fechas en el año 2021.'
#     )

#     def handle(self, *args, **kwargs):
#         # 1. Identificar y corregir fechas mal formateadas
#         registros = CodigoPostal.objects.all()
#         updated_count = 0

#         for registro in registros:
#             fecha = registro.fecha_inicio_vigencia

#             # Verifica que la fecha no sea None
#             if fecha is not None and self._is_ambiguous(fecha):
#                 nueva_fecha = self._swap_day_month(fecha)
#                 registro.fecha_inicio_vigencia = nueva_fecha
#                 registro.save()
#                 updated_count += 1
#                 print(f"Actualizado: {fecha} -> {nueva_fecha}")

#         # Mostrar el resultado de las actualizaciones
#         if updated_count > 0:
#             self.stdout.write(self.style.SUCCESS(
#                 f'Se actualizaron {updated_count} registros con fechas corregidas.'
#             ))
#         else:
#             self.stdout.write(self.style.WARNING('No se encontraron fechas para corregir.'))

#         # 2. Contar registros con fechas en el año 2021
#         count_2021 = CodigoPostal.objects.filter(
#             fecha_inicio_vigencia__year=2021
#         ).count()

#         # Mostrar el resultado del conteo
#         self.stdout.write(self.style.SUCCESS(
#             f'Se encontraron {count_2021} registros con fechas en el año 2021.'
#         ))

#     def _is_ambiguous(self, fecha):
#         """Determina si una fecha es ambigua (día y mes intercambiables)."""
#         # Asegúrate de que fecha no sea None antes de intentar acceder a sus atributos
#         if fecha is None:
#             return False
#         # Si el día es menor o igual a 12, es posible que esté mal formateada
#         return fecha.day <= 12

#     def _swap_day_month(self, fecha):
#         """Intercambia el día y el mes de una fecha."""
#         return date(fecha.year, fecha.day, fecha.month)  # Intercambia mes y día




class Command(BaseCommand):
    help = 'Corrige c_CodigoPostal eliminando el .0 si es necesario.'

    def handle(self, *args, **kwargs):
        # Obtener todos los registros de CodigoPostal
        registros = CodigoPostal.objects.all()
        updated_count = 0

        for registro in registros:
            # Convertir el valor a string y eliminar .0 si lo tiene
            codigo_postal_original = str(registro.c_CodigoPostal).strip()
            codigo_postal_corregido = self._remove_decimal(codigo_postal_original)

            if codigo_postal_original != codigo_postal_corregido:
                registro.c_CodigoPostal = codigo_postal_corregido
                registro.save()
                updated_count += 1
                print(f"Actualizado c_CodigoPostal: {codigo_postal_original} -> {codigo_postal_corregido}")

        # Mostrar el resultado de las actualizaciones
        if updated_count > 0:
            self.stdout.write(self.style.SUCCESS(
                f'Se actualizaron {updated_count} registros con c_CodigoPostal corregido.'
            ))
        else:
            self.stdout.write(self.style.WARNING('No se encontraron códigos postales para corregir.'))

    def _remove_decimal(self, value):
        """Elimina el sufijo .0 si está presente en un código postal."""
        if value.endswith('.0'):
            return value[:-2]  # Elimina los últimos dos caracteres ('.0')
        return value