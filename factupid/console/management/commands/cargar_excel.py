import pandas as pd
from django.core.management.base import BaseCommand
from cfdi.models import *
from datetime import time



from django.core.exceptions import ObjectDoesNotExist



# class Command(BaseCommand):
#     help = 'Cargar datos de Códigos Postales desde un archivo Excel a la base de datos'

#     def handle(self, *args, **kwargs):
#         file_path = r'C:\Users\admin\Documents\FAC\factupid\catCFDI.xls'

#         try:
#             # Leer el archivo Excel
#             df_codigos_postales = pd.read_excel(
#                 file_path, sheet_name='c_CodigoPostal_Parte_2', header=5
                
#             )
#             df_codigos_postales.columns = df_codigos_postales.columns.str.strip()

#             # Función para corregir fechas invertidas
#             def corregir_fecha(fecha):
#                 if pd.isnull(fecha):
#                     return None
#                 try:
#                     # Intentar interpretar la fecha correctamente
#                     parsed_date = pd.to_datetime(fecha, dayfirst=True, errors='coerce')
#                     if parsed_date is not None:
#                         return parsed_date.date()
#                 except Exception:
#                     pass
#                 return None

#             # Aplicar la corrección de fechas
#             df_codigos_postales['Fecha inicio de vigencia'] = df_codigos_postales['Fecha inicio de vigencia'].apply(corregir_fecha)
#             df_codigos_postales['Fecha fin de vigencia'] = df_codigos_postales['Fecha fin de vigencia'].apply(corregir_fecha)

#             # Función para convertir horas
#             def parse_time(value):
#                 try:
#                     return pd.to_datetime(value, format='%H:%M').time()
#                 except (ValueError, TypeError):
#                     return None

#             # Aplicar la conversión de horas
#             df_codigos_postales['Hora_Inicio_Horario_Verano'] = df_codigos_postales['Hora_Inicio_Horario_Verano'].apply(parse_time)
#             df_codigos_postales['Hora_Inicio_Horario_Invierno'] = df_codigos_postales['Hora_Inicio_Horario_Invierno'].apply(parse_time)

#             # Procesar y guardar los datos en la base de datos
#             for index, row in df_codigos_postales.iterrows():
#                 estado_codigo = row['c_Estado']
#                 estado = Estado.objects.filter(c_Estado=estado_codigo).first()
#                 if not estado:
#                     self.stderr.write(self.style.WARNING(
#                         f"Estado '{estado_codigo}' no encontrado, omitiendo el código postal."
#                     ))
#                     continue

#                 try:
#                     municipio_codigo = int(row['c_Municipio'])
#                 except (ValueError, TypeError):
#                     self.stderr.write(self.style.WARNING(f"Municipio '{row['c_Municipio']}' no válido, omitiendo el código postal."))
#                     continue

#                 municipio = Municipio.objects.filter(c_Estado=estado).filter(c_Municipio=municipio_codigo).first()
#                 if not municipio:
#                     self.stderr.write(self.style.WARNING(f"Municipio '{municipio_codigo}' no encontrado en el estado '{estado_codigo}', omitiendo el código postal."))
#                     continue

#                 try:
#                     localidad_codigo = int(row['c_Localidad'])
#                 except (ValueError, TypeError):
#                     self.stderr.write(self.style.WARNING(f"Localidad '{row['c_Localidad']}' no válida, omitiendo el código postal."))
#                     continue

#                 localidad = Localidad.objects.filter(c_Estado=estado).filter(c_Localidad=localidad_codigo).first()
#                 if not localidad:
#                     self.stderr.write(self.style.WARNING(f"Localidad '{localidad_codigo}' no encontrada en el estado '{estado_codigo}', omitiendo el código postal."))
#                     continue

#                 estimulo = row['Estímulo Franja Fronteriza'] == 1 if pd.notna(row['Estímulo Franja Fronteriza']) else False

#                 codigo_postal = CodigoPostal(
#                     c_CodigoPostal=row.get('c_CodigoPostal', ''),
#                     c_Estado=estado,
#                     c_Municipio=municipio,
#                     c_Localidad=localidad,
#                     estimulo_franja_fronteriza=estimulo,
#                     fecha_inicio_vigencia=row['Fecha inicio de vigencia'],
#                     fecha_fin_vigencia=row['Fecha fin de vigencia'],
#                     descripcion_huso_horario=row.get('Descripción del Huso Horario', ''),
#                     mes_inicio_horario_verano=row.get('Mes_Inicio_Horario_Verano', ''),
#                     dia_inicio_horario_verano=row.get('Día_Inicio_Horario_Verano', ''),
#                     hora_inicio_verano=row['Hora_Inicio_Horario_Verano'],
#                     diferencia_horaria_verano=row['Diferencia_Horaria_Verano'] if pd.notna(row['Diferencia_Horaria_Verano']) else 0,
#                     mes_inicio_horario_invierno=row.get('Mes_Inicio_Horario_Invierno', ''),
#                     dia_inicio_horario_invierno=row.get('Día_Inicio_Horario_Invierno', ''),
#                     hora_inicio_invierno=row['Hora_Inicio_Horario_Invierno'],
#                     diferencia_horaria_invierno=row['Diferencia_Horaria_Invierno'] if pd.notna(row['Diferencia_Horaria_Invierno']) else 0,
#                 )

#                 codigo_postal.save()

#             self.stdout.write(self.style.SUCCESS(
#                 'Códigos postales cargados exitosamente desde Excel a la base de datos.'
#             ))

#         except Exception as e:
#             self.stderr.write(self.style.ERROR(f"Ocurrió un error: {e}"))




# class Command(BaseCommand):
#     help = 'Cargar datos de FormaPago desde un archivo Excel a la base de datos'

#     def handle(self, *args, **kwargs):
#         file_path = r'C:\Users\admin\Documents\FAC\factupid\catCFDI.xls'
#         try:
            # Leer el archivo Excel para c_FormaPago
#             df_forma_pago = pd.read_excel(file_path, sheet_name='c_FormaPago', header=5)  # Cambia el nombre de la hoja
#             df_forma_pago.columns = df_forma_pago.columns.str.strip()  # Limpiar los nombres de las columnas

#             C_Moneda = pd.read_excel(file_path, sheet_name='c_Moneda', header=4)  # Cambia el nombre de la hoja
#             C_Moneda.columns = C_Moneda.columns.str.strip()  # Limpiar los nombres de las columnas

#             C_Exportacion = pd.read_excel(file_path, sheet_name='c_Exportacion', header=4)  # Cambia el nombre de la hoja
#             C_Exportacion.columns = C_Exportacion.columns.str.strip()  # Limpiar los nombres de las columnas


            # Imprimir los nombres de las columnas de FormaPago
            # print("Nombres de las columnas de FormaPago:", df_forma_pago.columns.tolist())
            # print("Primeras filas del DataFrame de FormaPago:", df_forma_pago.head())  # Muestra las primeras filas


            # print("Nombres de las columnas de Moneda:", C_Moneda.columns.tolist())
            # print("Primeras filas del DataFrame de Moneda:", C_Moneda.head())


            # print("Nombres de las columnas de Exportacion:", C_Exportacion.columns.tolist())
            # print("Primeras filas del DataFrame de Exportacion:", C_Exportacion.head())

            # Procesar los datos de FormaPago y guardarlos en la base de datos
            # for index, row in df_forma_pago.iterrows():
            #     # Manejo de fechas
            #     fecha_inicio_vigencia = row['Fecha inicio de vigencia'] if pd.notna(row['Fecha inicio de vigencia']) else None
            #     fecha_fin_vigencia = row['Fecha fin de vigencia'] if pd.notna(row['Fecha fin de vigencia']) else None

            #     # Convertir las fechas a datetime solo si no son None
            #     if fecha_inicio_vigencia is not None:
            #         fecha_inicio_vigencia = pd.to_datetime(fecha_inicio_vigencia, errors='coerce')
            #     if fecha_fin_vigencia is not None:
            #         fecha_fin_vigencia = pd.to_datetime(fecha_fin_vigencia, errors='coerce')

            #     forma_pago = FormaPago(
            #         c_FormaPago=row['c_FormaPago'],
            #         descripcion=row['Descripción'],
            #         bancarizado=row['Bancarizado'] == 'Sí',  # Ajusta según tus datos
            #         numero_operacion=row['Número de operación'],
            #         rfc_emisor_cuenta_ordenante=row['RFC del Emisor de la cuenta ordenante'],
            #         cuenta_ordenante=row['Cuenta Ordenante'],
            #         patron_cuenta_ordenante=row['Patrón para cuenta ordenante'],
            #         rfc_emisor_cuenta_beneficiario=row['RFC del Emisor Cuenta de Beneficiario'],
            #         cuenta_beneficiario=row['Cuenta de Benenficiario'],
            #         patron_cuenta_beneficiaria=row['Patrón para cuenta Beneficiaria'],
            #         tipo_cadena_pago=row['Tipo Cadena Pago'],
            #         nombre_banco_emisor_extranjero=row['Nombre del Banco emisor de la cuenta ordenante en caso de extranjero'],
            #         fecha_inicio_vigencia=fecha_inicio_vigencia,
            #         fecha_fin_vigencia=fecha_fin_vigencia
            #     )
            #     forma_pago.save()  # Guardar en la base de datos

            # Procesar los datos de C_Moneda y guardarlos en la base de datos
            # for index, row in C_Moneda.iterrows():
            #     # Validar y convertir fechas a None si son NaT
            #     fecha_inicio_vigencia = pd.to_datetime(row['Fecha inicio de vigencia'], errors='coerce')
            #     fecha_inicio_vigencia = fecha_inicio_vigencia if pd.notna(fecha_inicio_vigencia) else None

            #     fecha_fin_vigencia = pd.to_datetime(row['Fecha fin de vigencia'], errors='coerce')
            #     fecha_fin_vigencia = fecha_fin_vigencia if pd.notna(fecha_fin_vigencia) else None

            #     # Reemplazar NaN con un valor por defecto en campos numéricos
            #     decimales = row['Decimales'] if pd.notna(row['Decimales']) else 0
            #     porcentaje_variacion = row['Porcentaje variación'] if pd.notna(row['Porcentaje variación']) else 0.0

            #     moneda = Moneda(
            #         c_Moneda=row['c_Moneda'],
            #         descripcion=row['Descripción'],
            #         decimales=decimales,
            #         porcentaje_variacion=porcentaje_variacion,
            #         fecha_inicio_vigencia=fecha_inicio_vigencia,
            #         fecha_fin_vigencia=fecha_fin_vigencia
            #     )
            #     moneda.save()

            # for index, row in C_Exportacion.iterrows():

            #     # Validar y convertir fechas a None si son NaT
            #     fecha_inicio_vigencia = pd.to_datetime(row['Fecha inicio de vigencia'], errors='coerce')
            #     fecha_inicio_vigencia = fecha_inicio_vigencia if pd.notna(fecha_inicio_vigencia) else None

            #     fecha_fin_vigencia = pd.to_datetime(row['Fecha fin de vigencia'], errors='coerce')
            #     fecha_fin_vigencia = fecha_fin_vigencia if pd.notna(fecha_fin_vigencia) else None

            #     exportacion = Exportacion(
            #         c_Exportacion=row['c_Exportacion'],
            #         descripcion=row['Descripción'],
            #         fecha_inicio_vigencia=fecha_inicio_vigencia,
            #         fecha_fin_vigencia=fecha_fin_vigencia
            #     )
            #     exportacion.save()



            # df_metodo_pago = pd.read_excel(file_path, sheet_name='c_MetodoPago', header=5)
            # df_metodo_pago.columns = df_metodo_pago.columns.str.strip()

            # # Mostrar información para depuración
            # print("Nombres de las columnas de MetodoPago:", df_metodo_pago.columns.tolist())
            # print("Primeras filas del DataFrame de MetodoPago:", df_metodo_pago.head())

            # # Procesar y guardar los datos de c_MetodoPago en la base de datos
            # for index, row in df_metodo_pago.iterrows():
            #     # Validar y convertir fechas a None si son NaT
            #     fecha_inicio_vigencia = pd.to_datetime(row['Fecha inicio de vigencia'], errors='coerce')
            #     fecha_inicio_vigencia = fecha_inicio_vigencia if pd.notna(fecha_inicio_vigencia) else None

            #     fecha_fin_vigencia = pd.to_datetime(row['Fecha fin de vigencia'], errors='coerce')
            #     fecha_fin_vigencia = fecha_fin_vigencia if pd.notna(fecha_fin_vigencia) else None

            #     metodo_pago = MetodoPago(
            #         c_MetodoPago=row['c_MetodoPago'],
            #         descripcion=row['Descripción'],
            #         fecha_inicio_vigencia=fecha_inicio_vigencia,
            #         fecha_fin_vigencia=fecha_fin_vigencia
            #     )
            #     metodo_pago.save()


            # df_parte_1 = pd.read_excel(file_path, sheet_name='c_CodigoPostal_Parte_1', header=5)
            # # df_parte_2 = pd.read_excel(file_path, sheet_name='c_CodigoPostal_Parte_2', header=5)

            # # Limpiar los nombres de las columnas
            # df_parte_1.columns = df_parte_1.columns.str.strip()
            # # df_parte_2.columns = df_parte_2.columns.str.strip()

            # # Concatenar las dos partes en un solo DataFrame
            # df_codigo_postal = pd.concat([df_parte_1], ignore_index=True)

            # # Verificar la estructura del DataFrame combinado
            # print("Nombres de las columnas:", df_codigo_postal.columns.tolist())
            # print("Primeras filas del DataFrame combinado:", df_codigo_postal.head())

            # # Iterar sobre las filas del DataFrame combinado y guardar cada registro en la base de datos
            # for index, row in df_codigo_postal.iterrows():
            #     # Convertir fechas
            #     fecha_inicio_vigencia = pd.to_datetime(row['Fecha inicio de vigencia'], errors='coerce')
            #     fecha_inicio_vigencia = fecha_inicio_vigencia if pd.notna(fecha_inicio_vigencia) else None

            #     fecha_fin_vigencia = pd.to_datetime(row['Fecha fin de vigencia'], errors='coerce')
            #     fecha_fin_vigencia = fecha_fin_vigencia if pd.notna(fecha_fin_vigencia) else None

            #     # Convertir estímulo franja fronteriza a booleano
            #     estimulo_franja_fronteriza = bool(row['Estímulo Franja Fronteriza'])

            #     # Crear instancia del modelo CodigoPostal
            #     codigo_postal = CodigoPostal(
            #         c_CodigoPostal=row['c_CodigoPostal'],
            #         c_Estado=row['c_Estado'],
            #         c_Municipio=row['c_Municipio'],
            #         c_Localidad=row.get('c_Localidad', None),
            #         estimulo_franja_fronteriza=estimulo_franja_fronteriza,
            #         fecha_inicio_vigencia=fecha_inicio_vigencia,
            #         fecha_fin_vigencia=fecha_fin_vigencia,
            #         descripcion_huso_horario=row.get('Descripción del Huso Horario', None),
            #         mes_inicio_horario_verano=row.get('Mes_Inicio_Horario_Verano', None),
            #         dia_inicio_horario_verano=row.get('Día_Inicio_Horario_Verano', None),
            #         diferencia_horaria_verano=row.get('Diferencia_Horaria_Verano', None),
            #         mes_inicio_horario_invierno=row.get('Mes_Inicio_Horario_Invierno', None),
            #         dia_inicio_horario_invierno=row.get('Día_Inicio_Horario_Invierno', None),
            #         diferencia_horaria_invierno=row.get('Diferencia_Horaria_Invierno', None)
            #     )

            #     # Guardar la instancia en la base de datos
            #     codigo_postal.save()

            


            # df_estado = pd.read_excel(file_path, sheet_name='c_Estado', header=4)
            # df_municipio = pd.read_excel(file_path, sheet_name='C_Municipio', header=4)
            # df_localidad = pd.read_excel(file_path, sheet_name='C_Localidad', header=4)

            # Limpiar los nombres de las columnas
            # df_estado.columns = df_estado.columns.str.strip()
            # df_municipio.columns = df_municipio.columns.str.strip()
            # df_localidad.columns = df_localidad.columns.str.strip()

            # # Procesar e insertar los datos de Estado
            # for index, row in df_estado.iterrows():
            #     fecha_inicio_vigencia = pd.to_datetime(row['Fecha inicio de vigencia'], errors='coerce')
            #     fecha_fin_vigencia = pd.to_datetime(row['Fecha fin de vigencia'], errors='coerce')

            #     estado = Estado(
            #         c_Estado=row['c_Estado'],
            #         c_Pais=row['c_Pais'],
            #         nombre=row['Nombre del estado'],
            #         fecha_inicio_vigencia=fecha_inicio_vigencia,
            #         fecha_fin_vigencia=fecha_fin_vigencia if pd.notna(fecha_fin_vigencia) else None
            #     )
            #     estado.save()

            # self.stdout.write(self.style.SUCCESS('Estados cargados exitosamente.'))

            # Procesar e insertar los datos de Municipio

            # print("Nombres de las columnas de df_municipio:", df_municipio.columns.tolist())
            # print("Nombres de las columnas de df_localidad:", df_localidad.columns.tolist())
            # for index, row in df_municipio.iterrows():
            #     fecha_inicio_vigencia = pd.to_datetime(row['Fecha de inicio de vigencia'], errors='coerce')
            #     fecha_fin_vigencia = pd.to_datetime(row['Fecha de fin de vigencia'], errors='coerce')

            #     # Obtener la instancia del Estado
            #     estado = Estado.objects.get(c_Estado=row['c_Estado'])

            #     municipio = Municipio(
            #         c_Municipio=row['c_Municipio'],
            #         c_Estado=estado,
            #         descripcion=row['Descripción'],
            #         fecha_inicio_vigencia=fecha_inicio_vigencia,
            #         fecha_fin_vigencia=fecha_fin_vigencia if pd.notna(fecha_fin_vigencia) else None
            #     )
            #     municipio.save()

            # self.stdout.write(self.style.SUCCESS('Municipios cargados exitosamente.'))

            # Procesar e insertar los datos de Localidad
            # for index, row in df_localidad.iterrows():
            #     fecha_inicio_vigencia = pd.to_datetime(row['Fecha de inicio de vigencia'], errors='coerce')
            #     fecha_fin_vigencia = pd.to_datetime(row['Fecha de fin de vigencia'], errors='coerce')

            #     # Obtener la instancia del Estado
            #     estado = Estado.objects.get(c_Estado=row['c_Estado'])

            #     localidad = Localidad(
            #         c_Localidad=row['c_Localidad'],
            #         c_Estado=estado,
            #         descripcion=row['Descripción'],
            #         fecha_inicio_vigencia=fecha_inicio_vigencia,
            #         fecha_fin_vigencia=fecha_fin_vigencia if pd.notna(fecha_fin_vigencia) else None
            #     )
            #     localidad.save()

            # self.stdout.write(self.style.SUCCESS('Localidades cargadas exitosamente.'))

            


            




        #     self.stdout.write(self.style.SUCCESS('Datos cargados exitosamente desde Excel a la base de datos.'))

        # except Exception as e:
        #     print(f"Ocurrió un error: {e}")



# class Command(BaseCommand):
#     help = 'Cargar datos de Meses desde un archivo Excel a la base de datos'

#     def handle(self, *args, **kwargs):
#         file_path = r'C:\Users\admin\Documents\FAC\factupid\catCFDI.xls'

#         try:
#             # Leer la hoja 'c_Meses'
#             df_meses = pd.read_excel(file_path, sheet_name='c_Meses', header=4)

#             # Verificar cuántas filas se cargaron
#             print(f"Filas cargadas: {len(df_meses)}")

#             # Limpiar los nombres de las columnas
#             df_meses.columns = df_meses.columns.str.strip()

#             # Imprimir los nombres de las columnas para asegurar que sean correctos
#             print("Columnas:", df_meses.columns)

#             # Procesar e insertar los datos de Meses
#             for index, row in df_meses.iterrows():
#                 print(f"Procesando fila {index}: {row.to_dict()}")  # Verificar cada fila

#                 fecha_inicio_vigencia = pd.to_datetime(row['Fecha inicio de vigencia'], errors='coerce')
#                 fecha_fin_vigencia = pd.to_datetime(row['Fecha fin de vigencia'], errors='coerce')

#                 # Crear instancia del modelo Meses
#                 meses = Meses(
#                     c_Meses=row['c_Meses'],
#                     descripcion=row['Descripción'],
#                     fecha_inicio_vigencia=fecha_inicio_vigencia,
#                     fecha_fin_vigencia=fecha_fin_vigencia if pd.notna(fecha_fin_vigencia) else None
#                 )

#                 try:
#                     meses.save()
#                     print(f"Fila {index} guardada correctamente.")
#                 except Exception as e:
#                     print(f"Error al guardar la fila {index}: {e}")

#             # Mostrar mensaje de éxito
#             self.stdout.write(self.style.SUCCESS('Meses cargados exitosamente.'))

#         except Exception as e:
#             print(f"Ocurrió un error: {e}")





# class Command(BaseCommand):
#     help = 'Cargar datos de TipoRelacion desde un archivo Excel a la base de datos'

#     def handle(self, *args, **kwargs):
#         file_path = r'C:\Users\admin\Documents\FAC\factupid\catCFDI.xls'

#         try:
#             # Leer la hoja 'c_TipoRelacion'
#             df_tipo_relacion = pd.read_excel(file_path, sheet_name='c_TipoRelacion', header=4)

#             # Verificar cuántas filas se cargaron
#             print(f"Filas cargadas: {len(df_tipo_relacion)}")

#             # Limpiar los nombres de las columnas
#             df_tipo_relacion.columns = df_tipo_relacion.columns.str.strip()

#             # Imprimir los nombres de las columnas para asegurar que sean correctos
#             print("Columnas:", df_tipo_relacion.columns)

#             # Procesar e insertar los datos de TipoRelacion
#             for index, row in df_tipo_relacion.iterrows():
#                 print(f"Procesando fila {index}: {row.to_dict()}")  # Verificar cada fila

#                 fecha_inicio_vigencia = pd.to_datetime(row['Fecha inicio de vigencia'], errors='coerce')
#                 fecha_fin_vigencia = pd.to_datetime(row['Fecha fin de vigencia'], errors='coerce')

#                 # Crear instancia del modelo TipoRelacion
#                 tipo_relacion = TipoRelacion(
#                     c_TipoRelacion=row['c_TipoRelacion'],
#                     descripcion=row['Descripción'],
#                     fecha_inicio_vigencia=fecha_inicio_vigencia,
#                     fecha_fin_vigencia=fecha_fin_vigencia if pd.notna(fecha_fin_vigencia) else None
#                 )

#                 try:
#                     tipo_relacion.save()
#                     print(f"Fila {index} guardada correctamente.")
#                 except Exception as e:
#                     print(f"Error al guardar la fila {index}: {e}")

#             # Mostrar mensaje de éxito
#             self.stdout.write(self.style.SUCCESS('Tipos de Relación cargados exitosamente.'))

#         except Exception as e:
#             print(f"Ocurrió un error: {e}")


# class Command(BaseCommand):
#     help = 'Cargar datos de RegimenFiscal desde un archivo Excel a la base de datos'

#     def handle(self, *args, **kwargs):
#         file_path = r'C:\Users\admin\Documents\FAC\factupid\catCFDI.xls'

#         try:
#             # Leer la hoja 'c_RegimenFiscal'
#             df_regimen_fiscal = pd.read_excel(file_path, sheet_name='c_RegimenFiscal', header=5)

#             # Verificar cuántas filas se cargaron
#             print(f"Filas cargadas: {len(df_regimen_fiscal)}")

#             # Limpiar los nombres de las columnas
#             df_regimen_fiscal.columns = df_regimen_fiscal.columns.str.strip()

#             # Imprimir los nombres de las columnas para asegurar que sean correctos
#             print("Columnas:", df_regimen_fiscal.columns)

#             # Procesar e insertar los datos de RegimenFiscal
#             for index, row in df_regimen_fiscal.iterrows():
#                 print(f"Procesando fila {index}: {row.to_dict()}")  # Verificar cada fila

#                 fecha_inicio_vigencia = pd.to_datetime(row['Fecha de inicio de vigencia'], errors='coerce')
#                 fecha_fin_vigencia = pd.to_datetime(row['Fecha de fin de vigencia'], errors='coerce')

#                 # Crear instancia del modelo RegimenFiscal
#                 regimen = RegimenFiscal(
#                     c_RegimenFiscal=row['c_RegimenFiscal'],
#                     descripcion=row['Descripción'],
#                     fisica=row['Física'].strip().lower() == 'sí',
#                     moral=row['Moral'].strip().lower() == 'sí',
#                     fecha_inicio_vigencia=fecha_inicio_vigencia,
#                     fecha_fin_vigencia=fecha_fin_vigencia if pd.notna(fecha_fin_vigencia) else None
#                 )

#                 try:
#                     regimen.save()
#                     print(f"Fila {index} guardada correctamente.")
#                 except Exception as e:
#                     print(f"Error al guardar la fila {index}: {e}")

#             # Mostrar mensaje de éxito
#             self.stdout.write(self.style.SUCCESS('Régimenes fiscales cargados exitosamente.'))

#         except Exception as e:
#             print(f"Ocurrió un error: {e}")



# class Command(BaseCommand):
#     help = 'Cargar datos de Pais desde un archivo Excel a la base de datos'

#     def handle(self, *args, **kwargs):
#         file_path = r'C:\Users\admin\Documents\FAC\factupid\catCFDI.xls'

#         try:
#             # Leer la hoja 'c_Pais'
#             df_pais = pd.read_excel(file_path, sheet_name='c_Pais', header=4)

#             # Verificar cuántas filas se cargaron
#             print(f"Filas cargadas: {len(df_pais)}")

#             # Limpiar los nombres de las columnas
#             df_pais.columns = df_pais.columns.str.strip()

#             # Imprimir los nombres de las columnas para asegurar que sean correctos
#             print("Columnas:", df_pais.columns)

#             # Procesar e insertar los datos de Pais
#             for index, row in df_pais.iterrows():
#                 print(f"Procesando fila {index}: {row.to_dict()}")  # Verificar cada fila

#                 # Crear instancia del modelo Pais
#                 pais = Pais(
#                     c_Pais=row['c_Pais'],
#                     descripcion=row['Descripción'],
#                     formato_codigo_postal=row.get('Formato de código postal', None),
#                     formato_rfc=row.get('Formato de Registro de Identidad Tributaria', None),
#                     validacion_rfc=row.get('Validación del Registro de Identidad Tributaria', None),
#                     agrupaciones=row.get('Agrupaciones', None)
#                 )

#                 try:
#                     pais.save()
#                     print(f"Fila {index} guardada correctamente.")
#                 except Exception as e:
#                     print(f"Error al guardar la fila {index}: {e}")

#             # Mostrar mensaje de éxito
#             self.stdout.write(self.style.SUCCESS('Países cargados exitosamente.'))

#         except Exception as e:
#             print(f"Ocurrió un error: {e}")


# class Command(BaseCommand):
#     help = 'Cargar datos de UsoCFDI desde un archivo Excel a la base de datos'

#     def handle(self, *args, **kwargs):
#         file_path = r'C:\Users\admin\Documents\FAC\factupid\catCFDI.xls'

#         try:
#             # Leer la hoja 'c_UsoCFDI'
#             df_usocfdi = pd.read_excel(file_path, sheet_name='c_UsoCFDI', header=4)

#             # Verificar cuántas filas se cargaron
#             print(f"Filas cargadas: {len(df_usocfdi)}")

#             # Limpiar los nombres de las columnas
#             df_usocfdi.columns = df_usocfdi.columns.str.strip()

#             # Imprimir los nombres de las columnas para asegurar que sean correctos
#             print("Columnas:", df_usocfdi.columns)

#             # Procesar e insertar los datos de UsoCFDI
#             for index, row in df_usocfdi.iterrows():
#                 print(f"Procesando fila {index}: {row.to_dict()}")  # Verificar cada fila

#                 # Parsear las fechas
#                 fecha_inicio_vigencia = pd.to_datetime(row['Fecha inicio de vigencia'], errors='coerce')
#                 fecha_fin_vigencia = pd.to_datetime(row['Fecha fin de vigencia'], errors='coerce')

#                 # Crear la instancia del modelo UsoCFDI
#                 uso_cfdi = UsoCFDI(
#                     c_UsoCFDI=row['c_UsoCFDI'],
#                     descripcion=row['Descripción'],
#                     aplica_fisica=row['Física'] == 'Sí',
#                     aplica_moral=row['Moral'] == 'Sí',
#                     fecha_inicio_vigencia=fecha_inicio_vigencia,
#                     fecha_fin_vigencia=fecha_fin_vigencia if pd.notna(fecha_fin_vigencia) else None
#                 )

#                 try:
#                     uso_cfdi.save()  # Guardar el objeto primero
#                     print(f"Fila {index} guardada correctamente.")

#                     # Extraer los regímenes fiscales receptores mencionados en la fila
#                     regimenes = row['Régimen Fiscal Receptor']
#                     if pd.notna(regimenes):  # Verificar que no esté vacío
#                         regimenes_ids = [r.strip() for r in regimenes.split(',')]  # IDs separados por comas

#                         # Filtrar solo los regímenes fiscales que estén en el modelo
#                         regimenes_fiscales = RegimenFiscal.objects.filter(c_RegimenFiscal__in=regimenes_ids)

#                         # Filtrar según tipo de persona (física o moral)
#                         if uso_cfdi.aplica_fisica:
#                             # Solo se asignan si es física
#                             regimenes_fiscales = regimenes_fiscales.filter(fisica=True)  # Asegúrate de que el campo sea correcto
#                         if uso_cfdi.aplica_moral:
#                             # Solo se asignan si es moral
#                             regimenes_fiscales = regimenes_fiscales.filter(moral=True)  # Asegúrate de que el campo sea correcto

#                         # Solo establecer los regímenes fiscales si hay algunos válidos
#                         if regimenes_fiscales.exists():
#                             uso_cfdi.regimen_fiscal_receptor.set(regimenes_fiscales)  # Asignar los regímenes fiscales
#                             print(f"Regímenes fiscales asignados a la fila {index}.")
#                         else:
#                             print(f"No se encontraron regímenes fiscales válidos para la fila {index}.")
#                     else:
#                         print(f"No se especificaron regímenes fiscales para la fila {index}.")

#                 except Exception as e:
#                     print(f"Error al guardar la fila {index}: {e}")

#             # Mostrar mensaje de éxito
#             self.stdout.write(self.style.SUCCESS('UsosCFDI cargados exitosamente.'))

#         except Exception as e:
#             print(f"Ocurrió un error: {e}")


# class Command(BaseCommand):
#     help = 'Cargar datos de ClaveProdServ desde un archivo Excel a la base de datos'

#     def handle(self, *args, **kwargs):
#         file_path = r'C:\Users\admin\Documents\FAC\factupid\catCFDI.xls'

#         try:
#             # Leer la hoja 'c_ClaveProdServ'
#             df_clave_prod_serv = pd.read_excel(file_path, sheet_name='c_ClaveProdServ', header=4)

#             # Verificar cuántas filas se cargaron
#             print(f"Filas cargadas: {len(df_clave_prod_serv)}")

#             # Limpiar los nombres de las columnas
#             df_clave_prod_serv.columns = df_clave_prod_serv.columns.str.strip()

#             # Procesar e insertar los datos de ClaveProdServ
#             for index, row in df_clave_prod_serv.iterrows():
#                 print(f"Procesando fila {index}: {row.to_dict()}")  # Verificar cada fila

#                 # Parsear las fechas
#                 fecha_inicio_vigencia = pd.to_datetime(row['FechaInicioVigencia'], errors='coerce')
#                 fecha_fin_vigencia = pd.to_datetime(row['FechaFinVigencia'], errors='coerce')

#                 # Crear la instancia del modelo ClaveProdServ
#                 clave_prod_serv = ClaveProdServ(
#                     c_ClaveProdServ=row['c_ClaveProdServ'],
#                     descripcion=row['Descripción'],
#                     incluir_iva_trasladado=row['Incluir IVA trasladado'],
#                     incluir_ieps_trasladado=row['Incluir IEPS trasladado'],
#                     complemento_incluir=row['Complemento que debe incluir'],
#                     fecha_inicio_vigencia=fecha_inicio_vigencia,
#                     fecha_fin_vigencia=fecha_fin_vigencia if pd.notna(fecha_fin_vigencia) else None,
#                     estimulo_franja_fronteriza=row['Estímulo Franja Fronteriza'] == '1',
#                     palabras_similares=row['Palabras similares']
#                 )

#                 try:
#                     clave_prod_serv.save()
#                     print(f"Fila {index} guardada correctamente.")
#                 except Exception as e:
#                     print(f"Error al guardar la fila {index}: {e}")

#             # Mostrar mensaje de éxito
#             self.stdout.write(self.style.SUCCESS('Claves de Producto y Servicio cargadas exitosamente.'))

#         except Exception as e:
#             print(f"Ocurrió un error: {e}")



# class Command(BaseCommand):
#     help = 'Cargar datos de Unidades desde un archivo Excel a la base de datos'

#     def handle(self, *args, **kwargs):
#         file_path = r'C:\Users\admin\Documents\FAC\factupid\catCFDI.xls'  # Cambia la extensión si es necesario

#         try:
#             # Leer el archivo de Excel desde la hoja 'c_ClaveUnidad'
#             df_unidades = pd.read_excel(file_path, sheet_name='c_ClaveUnidad', header=5)  # Ajusta el número de encabezados según tu archivo

#             # Verificar cuántas filas se cargaron
#             print(f"Filas cargadas: {len(df_unidades)}")

#             # Limpiar los nombres de las columnas
#             df_unidades.columns = df_unidades.columns.str.strip()
#             print("Nombres de las columnas:", df_unidades.columns)  # Verificar nombres de columnas

#             # Verificar si las columnas requeridas están presentes
#             required_columns = ['c_ClaveUnidad', 'Nombre', 'Descripción', 'Nota', 'Fecha de inicio de vigencia', 'Fecha de fin de vigencia', 'Símbolo']
#             for column in required_columns:
#                 if column not in df_unidades.columns:
#                     print(f"La columna '{column}' no se encontró en el DataFrame.")
#                     return  # Terminar si falta alguna columna

#             # Procesar e insertar los datos de Unidad
#             for index, row in df_unidades.iterrows():
#                 print(f"Procesando fila {index}: {row.to_dict()}")  # Verificar cada fila

#                 # Parsear las fechas
#                 fecha_inicio_vigencia = pd.to_datetime(row['Fecha de inicio de vigencia'], errors='coerce')
#                 fecha_fin_vigencia = pd.to_datetime(row['Fecha de fin de vigencia'], errors='coerce')

#                 # Crear la instancia del modelo Unidad
#                 unidad = ClaveUnidad(  # Asegúrate de que este modelo es correcto
#                     c_ClaveUnidad=row['c_ClaveUnidad'],
#                     nombre=row['Nombre'],
#                     descripcion=row['Descripción'],
#                     nota=row['Nota'],
#                     fecha_inicio_vigencia=fecha_inicio_vigencia,
#                     fecha_fin_vigencia=fecha_fin_vigencia if pd.notna(fecha_fin_vigencia) else None,
#                     simbolo=row['Símbolo'],
#                 )

#                 try:
#                     unidad.save()
#                     print(f"Fila {index} guardada correctamente.")
#                 except Exception as e:
#                     print(f"Error al guardar la fila {index}: {e}")

#             # Mostrar mensaje de éxito
#             self.stdout.write(self.style.SUCCESS('Unidades cargadas exitosamente.'))

#         except Exception as e:
#             print(f"Ocurrió un error: {e}")



# class Command(BaseCommand):
#     help = 'Cargar datos de ObjetoImp desde un archivo Excel a la base de datos'

#     def handle(self, *args, **kwargs):
#         file_path = r'C:\Users\admin\Documents\FAC\factupid\catCFDI.xls'  # Cambia la ruta si es necesario

#         try:
#             # Leer la hoja 'c_ObjetoImp'
#             df_objeto_imp = pd.read_excel(file_path, sheet_name='c_ObjetoImp', header=4)  # Ajusta el número de encabezados según tu archivo

#             # Verificar cuántas filas se cargaron
#             print(f"Filas cargadas: {len(df_objeto_imp)}")

#             # Limpiar los nombres de las columnas
#             df_objeto_imp.columns = df_objeto_imp.columns.str.strip()

#             # Procesar e insertar los datos de ObjetoImp
#             for index, row in df_objeto_imp.iterrows():
#                 print(f"Procesando fila {index}: {row.to_dict()}")  # Verificar cada fila

#                 # Parsear las fechas
#                 fecha_inicio_vigencia = pd.to_datetime(row['Fecha inicio de vigencia'], errors='coerce')
#                 fecha_fin_vigencia = pd.to_datetime(row['Fecha fin de vigencia'], errors='coerce')

#                 # Crear la instancia del modelo ObjetoImp
#                 objeto_imp = ObjetoImp(
#                     c_ObjetoImp=row['c_ObjetoImp'],
#                     descripcion=row['Descripción'],
#                     fecha_inicio_vigencia=fecha_inicio_vigencia,
#                     fecha_fin_vigencia=fecha_fin_vigencia if pd.notna(fecha_fin_vigencia) else None,
#                 )

#                 try:
#                     objeto_imp.save()
#                     print(f"Fila {index} guardada correctamente.")
#                 except Exception as e:
#                     print(f"Error al guardar la fila {index}: {e}")

#             # Mostrar mensaje de éxito
#             self.stdout.write(self.style.SUCCESS('Objetos de Impuesto cargados exitosamente.'))

#         except Exception as e:
#             print(f"Ocurrió un error: {e}")



# class Command(BaseCommand):
#     help = 'Cargar datos de Impuesto desde un archivo Excel a la base de datos'

#     def handle(self, *args, **kwargs):
#         file_path = r'C:\Users\admin\Documents\FAC\factupid\catCFDI.xls'  # Cambia la ruta si es necesario

#         try:
#             # Leer la hoja 'c_Impuesto'
#             df_impuesto = pd.read_excel(file_path, sheet_name='c_Impuesto', header=4)  # Ajusta el número de encabezados según tu archivo

#             # Verificar cuántas filas se cargaron
#             print(f"Filas cargadas: {len(df_impuesto)}")

#             # Limpiar los nombres de las columnas
#             df_impuesto.columns = df_impuesto.columns.str.strip()

#             # Procesar e insertar los datos de Impuesto
#             for index, row in df_impuesto.iterrows():
#                 print(f"Procesando fila {index}: {row.to_dict()}")  # Verificar cada fila

#                 # Parsear las fechas
#                 fecha_inicio_vigencia = pd.to_datetime(row['Fecha inicio de vigencia'], errors='coerce')
#                 fecha_fin_vigencia = pd.to_datetime(row['Fecha fin de vigencia'], errors='coerce')

#                 # Crear la instancia del modelo Impuesto
#                 impuesto = Impuesto(
#                     c_Impuesto=row['c_Impuesto'],
#                     descripcion=row['Descripción'],
#                     traslado=row['Traslado'] == 'Si',
#                     local_o_federal=row['Local o federal'] == 'Federal',
#                     fecha_inicio_vigencia=fecha_inicio_vigencia,
#                     fecha_fin_vigencia=fecha_fin_vigencia if pd.notna(fecha_fin_vigencia) else None,
#                 )

#                 try:
#                     impuesto.save()
#                     print(f"Fila {index} guardada correctamente.")
#                 except Exception as e:
#                     print(f"Error al guardar la fila {index}: {e}")

#             # Mostrar mensaje de éxito
#             self.stdout.write(self.style.SUCCESS('Impuestos cargados exitosamente.'))

#         except Exception as e:
#             print(f"Ocurrió un error: {e}")




# class Command(BaseCommand):
#     help = 'Cargar datos de TipoFactor desde un archivo Excel a la base de datos'

#     def handle(self, *args, **kwargs):
#         file_path = r'C:\Users\admin\Documents\FAC\factupid\catCFDI.xls'  # Cambia la ruta si es necesario

#         try:
#             # Leer la hoja 'c_TipoFactor'
#             df_tipo_factor = pd.read_excel(file_path, sheet_name='c_TipoFactor', header=4)  # Ajusta el número de encabezados según tu archivo

#             # Verificar cuántas filas se cargaron
#             print(f"Filas cargadas: {len(df_tipo_factor)}")

#             # Limpiar los nombres de las columnas
#             df_tipo_factor.columns = df_tipo_factor.columns.str.strip()

#             # Procesar e insertar los datos de TipoFactor
#             for index, row in df_tipo_factor.iterrows():
#                 print(f"Procesando fila {index}: {row.to_dict()}")  # Verificar cada fila

#                 # Parsear las fechas
#                 fecha_inicio_vigencia = pd.to_datetime(row['Fecha inicio de vigencia'], errors='coerce')
#                 fecha_fin_vigencia = pd.to_datetime(row['Fecha fin de vigencia'], errors='coerce')

#                 # Crear la instancia del modelo TipoFactor
#                 tipo_factor = TipoFactor(
#                     c_TipoFactor=row['c_TipoFactor'],  # Asegúrate de que esta columna exista en tu Excel
#                     fecha_inicio_vigencia=fecha_inicio_vigencia,
#                     fecha_fin_vigencia=fecha_fin_vigencia if pd.notna(fecha_fin_vigencia) else None,
#                 )

#                 try:
#                     tipo_factor.save()
#                     print(f"Fila {index} guardada correctamente.")
#                 except Exception as e:
#                     print(f"Error al guardar la fila {index}: {e}")

#             # Mostrar mensaje de éxito
#             self.stdout.write(self.style.SUCCESS('Tipos de Factor cargados exitosamente.'))

#         except Exception as e:
#             print(f"Ocurrió un error: {e}")







# class Command(BaseCommand):
#     help = 'Cargar datos de TipoFactor desde un archivo Excel a la base de datos'

#     def handle(self, *args, **kwargs):
#         file_path = r'C:\Users\admin\Documents\FAC\factupid\catCFDI.xls'  # Cambia la ruta si es necesario

#         try:
#             # Leer la hoja 'c_TipoFactor'
#             df_tipo_aduana = pd.read_excel(file_path, sheet_name='c_Aduana', header=4)  # Ajusta el número de encabezados según tu archivo

#             # Verificar cuántas filas se cargaron
#             print(f"Filas cargadas: {len(df_tipo_aduana)}")

#             # Limpiar los nombres de las columnas
#             df_tipo_aduana.columns = df_tipo_aduana.columns.str.strip()

#             # Procesar e insertar los datos de TipoFactor
#             for index, row in df_tipo_aduana.iterrows():
#                 print(f"Procesando fila {index}: {row.to_dict()}")  # Verificar cada fila

#                 # Parsear las fechas
#                 fecha_inicio_vigencia = pd.to_datetime(row['Fecha inicio de vigencia'], errors='coerce')
#                 fecha_fin_vigencia = pd.to_datetime(row['Fecha fin de vigencia'], errors='coerce')

#                 # Crear la instancia del modelo TipoFactor
#                 tipo_aduana = Aduana(
#                     c_Aduana=row['c_Aduana'],  # Asegúrate de que esta columna exista en tu Excel
#                     descripcion=row['Descripción'],
#                     fecha_inicio_vigencia=fecha_inicio_vigencia,
#                     fecha_fin_vigencia=fecha_fin_vigencia if pd.notna(fecha_fin_vigencia) else None,
#                 )

#                 try:
#                     tipo_aduana.save()
#                     print(f"Fila {index} guardada correctamente.")
#                 except Exception as e:
#                     print(f"Error al guardar la fila {index}: {e}")

#             # Mostrar mensaje de éxito
#             self.stdout.write(self.style.SUCCESS('Tipos de aduana cargados exitosamente.'))

#         except Exception as e:
#             print(f"Ocurrió un error: {e}")



# class Command(BaseCommand):
#     help = 'Cargar datos de Número de Pedimento por Aduana desde un archivo Excel'

#     def handle(self, *args, **kwargs):
#         file_path = r'C:\Users\admin\Documents\FAC\factupid\catCFDI.xls'  # Cambia la ruta si es necesario

#         try:
#             # Leer la hoja correspondiente
#             df = pd.read_excel(file_path, sheet_name='c_NumPedimentoAduana', header=4)

#             print(f"Filas cargadas: {len(df)}")

#             # Limpiar los nombres de las columnas
#             df.columns = df.columns.str.strip()

#             # Procesar e insertar los datos
#             for index, row in df.iterrows():
#                 print(f"Procesando fila {index}: {row.to_dict()}")

#                 # Buscar la aduana correspondiente
#                 try:
#                     aduana = Aduana.objects.get(c_Aduana=row['c_Aduana'])
#                 except Aduana.DoesNotExist:
#                     print(f"Aduana con código {row['c_Aduana']} no encontrada.")
#                     continue

#                 # Parsear las fechas
#                 fecha_inicio_vigencia = pd.to_datetime(row['Fecha inicio de vigencia'], errors='coerce').date()
#                 fecha_fin_vigencia = (
#                     pd.to_datetime(row['Fecha fin de vigencia'], errors='coerce').date()
#                     if pd.notna(row['Fecha fin de vigencia']) else None
#                 )

#                 # Crear o actualizar la instancia
#                 pedimento, created = NumPedimentoAduana.objects.update_or_create(
#                     aduana=aduana,
#                     patente=row['Patente'],
#                     ejercicio=row['Ejercicio'],
#                     defaults={
#                         'cantidad': row['Cantidad'],
#                         'fecha_inicio_vigencia': fecha_inicio_vigencia,
#                         'fecha_fin_vigencia': fecha_fin_vigencia,
#                     }
#                 )

#                 if created:
#                     print(f"Fila {index} guardada como nueva entrada.")
#                 else:
#                     print(f"Fila {index} actualizada.")

#             self.stdout.write(self.style.SUCCESS('Datos de Número de Pedimento por Aduana cargados exitosamente.'))

#         except Exception as e:
#             print(f"Ocurrió un error: {e}")







# class Command(BaseCommand):
#     help = 'Cargar datos de NumPedimentoAduana desde un archivo Excel a la base de datos'

#     def handle(self, *args, **kwargs):
#         file_path = r'C:\Users\admin\Documents\FAC\factupid\catCFDI.xls'  # Cambia la ruta si es necesario

#         try:
#             # Leer la hoja 'c_NumPedimentoAduana'
#             df = pd.read_excel(file_path, sheet_name='c_PatenteAduanal', header=4)  # Ajusta el header según tu archivo

#             # Verificar cuántas filas se cargaron
#             print(f"Filas cargadas: {len(df)}")

#             # Limpiar los nombres de las columnas
#             df.columns = df.columns.str.strip()

#             # Procesar e insertar los datos
#             for index, row in df.iterrows():
#                 print(f"Procesando fila {index}: {row.to_dict()}")  # Verificar cada fila

#                 # Parsear las fechas
#                 fecha_inicio_vigencia = pd.to_datetime(row['Inicio de vigencia de la patente'], errors='coerce')
#                 fecha_fin_vigencia = pd.to_datetime(row['Fin de vigencia de la patente'], errors='coerce')

#                 # Obtener el objeto 'Aduana' relacionado (clave correcta: 'c_Aduana')
                

#                 # Crear la instancia del modelo
#                 num_PatenteAduanal = PatenteAduanal(
#                     c_PatenteAduanal=row['C_PatenteAduanal'],
#                     inicio_vigencia=fecha_inicio_vigencia,
#                     fin_vigencia=fecha_fin_vigencia if pd.notna(fecha_fin_vigencia) else None,
#                 )

#                 try:
#                     num_PatenteAduanal.save()
#                     print(f"Fila {index} guardada correctamente.")
#                 except Exception as e:
#                     print(f"Error al guardar la fila {index}: {e}")

#             # Mostrar mensaje de éxito
#             self.stdout.write(self.style.SUCCESS('Datos de patenteAduanal cargados exitosamente.'))

#         except Exception as e:
#             print(f"Ocurrió un error: {e}")



class Command(BaseCommand):
    help = 'Cargar datos de Colonia desde un archivo Excel a la base de datos'

    def handle(self, *args, **kwargs):
        file_path = r'C:\Users\admin\Documents\FAC\factupid\catCFDI.xls'  # Cambia la ruta si es necesario

        try:
            # Leer la hoja 'C_Colonia_1'
            df = pd.read_excel(file_path, sheet_name='C_Colonia_3', header=4)  # Ajusta el header según tu archivo

            print(f"Filas cargadas: {len(df)}")
            df.columns = df.columns.str.strip()  # Limpiar nombres de columnas

            for index, row in df.iterrows():
                print(f"Procesando fila {index}: {row.to_dict()}")

                # Asegúrate de que el código postal sea una cadena
                codigo_postal_str = str(int(row['c_CodigoPostal']))  # Convierte a entero y luego a cadena para manejar ceros

                # Usar filter para obtener todos los códigos postales coincidentes
                codigos_postales = CodigoPostal.objects.filter(c_CodigoPostal=codigo_postal_str)

                if not codigos_postales.exists():
                    print(f"Código postal {codigo_postal_str} no encontrado. Fila omitida.")
                    continue  # Omitir esta fila y pasar a la siguiente

                if codigos_postales.count() > 1:
                    print(f"Advertencia: Se encontraron múltiples códigos postales para {codigo_postal_str}. Usando el primero.")

                # Usar el primer código postal encontrado
                codigo_postal = codigos_postales.first()

                # Crear la instancia del modelo Colonia
                num_colonia = Colonia(
                    c_Colonia=row['c_Colonia'],
                    c_CodigoPostal=codigo_postal,
                    nombre_asentamiento=row.get('Nombre del asentamiento', '')  # Manejar nulos
                )

                try:
                    num_colonia.save()
                    print(f"Fila {index} guardada correctamente.")
                except Exception as e:
                    print(f"Error al guardar la fila {index}: {e}")

            self.stdout.write(self.style.SUCCESS('Datos de colonia cargados exitosamente.'))

        except Exception as e:
            print(f"Ocurrió un error: {e}")


#



# class Command(BaseCommand):
#     help = 'Cargar datos de Códigos Postales desde un archivo Excel a la base de datos'

#     def handle(self, *args, **kwargs):
#         file_path = r'C:\Users\admin\Documents\FAC\factupid\catCFDI.xls'

#         try:
#             # Leer el archivo Excel
#             df_codigos_postales = pd.read_excel(
#                 file_path, sheet_name='c_CodigoPostal_Parte_2', header=5
#             )
#             df_codigos_postales.columns = df_codigos_postales.columns.str.strip()

#             # Función para corregir fechas invertidas
#             def corregir_fecha(fecha):
#                 if pd.isnull(fecha):
#                     return None
#                 try:
#                     parsed_date = pd.to_datetime(fecha, dayfirst=True, errors='coerce')
#                     return parsed_date.date() if parsed_date is not None else None
#                 except Exception:
#                     return None

#             # Aplicar la corrección de fechas
#             df_codigos_postales['Fecha inicio de vigencia'] = df_codigos_postales['Fecha inicio de vigencia'].apply(corregir_fecha)
#             df_codigos_postales['Fecha fin de vigencia'] = df_codigos_postales['Fecha fin de vigencia'].apply(corregir_fecha)

#             # Función para convertir horas
#             def parse_time(value):
#                 try:
#                     return pd.to_datetime(value, format='%H:%M').time()
#                 except (ValueError, TypeError):
#                     return None

#             # Aplicar la conversión de horas
#             df_codigos_postales['Hora_Inicio_Horario_Verano'] = df_codigos_postales['Hora_Inicio_Horario_Verano'].apply(parse_time)
#             df_codigos_postales['Hora_Inicio_Horario_Invierno'] = df_codigos_postales['Hora_Inicio_Horario_Invierno'].apply(parse_time)

#             # Procesar y guardar los datos en la base de datos
#             for index, row in df_codigos_postales.iterrows():
#                 estado_codigo = row['c_Estado']
#                 estado = Estado.objects.filter(c_Estado=estado_codigo).first()

#                 # Usar un valor predeterminado (None) si no se encuentra el estado
#                 if not estado:
#                     estado = None

#                 # Convertir el municipio a int o usar None
#                 municipio_codigo = int(row['c_Municipio']) if pd.notna(row['c_Municipio']) else None
#                 municipio = Municipio.objects.filter(c_Estado=estado).filter(c_Municipio=municipio_codigo).first() if municipio_codigo else None

#                 # Convertir la localidad a int o usar None
#                 localidad_codigo = int(row['c_Localidad']) if pd.notna(row['c_Localidad']) else None
#                 localidad = Localidad.objects.filter(c_Estado=estado).filter(c_Localidad=localidad_codigo).first() if localidad_codigo else None

#                 estimulo = row['Estímulo Franja Fronteriza'] == 1 if pd.notna(row['Estímulo Franja Fronteriza']) else False

#                 codigo_postal = CodigoPostal(
#                     c_CodigoPostal=row.get('c_CodigoPostal', ''),
#                     c_Estado=estado,
#                     c_Municipio=municipio,
#                     c_Localidad=localidad,
#                     estimulo_franja_fronteriza=estimulo,
#                     fecha_inicio_vigencia=row['Fecha inicio de vigencia'],
#                     fecha_fin_vigencia=row['Fecha fin de vigencia'],
#                     descripcion_huso_horario=row.get('Descripción del Huso Horario', ''),
#                     mes_inicio_horario_verano=row.get('Mes_Inicio_Horario_Verano', ''),
#                     dia_inicio_horario_verano=row.get('Día_Inicio_Horario_Verano', ''),
#                     hora_inicio_verano=row['Hora_Inicio_Horario_Verano'],
#                     diferencia_horaria_verano=row['Diferencia_Horaria_Verano'] if pd.notna(row['Diferencia_Horaria_Verano']) else 0,
#                     mes_inicio_horario_invierno=row.get('Mes_Inicio_Horario_Invierno', ''),
#                     dia_inicio_horario_invierno=row.get('Día_Inicio_Horario_Invierno', ''),
#                     hora_inicio_invierno=row['Hora_Inicio_Horario_Invierno'],
#                     diferencia_horaria_invierno=row['Diferencia_Horaria_Invierno'] if pd.notna(row['Diferencia_Horaria_Invierno']) else 0,
#                 )

#                 codigo_postal.save()

#             self.stdout.write(self.style.SUCCESS(
#                 'Códigos postales cargados exitosamente desde Excel a la base de datos.'
#             ))

#         except Exception as e:
#             self.stderr.write(self.style.ERROR(f"Ocurrió un error: {e}"))