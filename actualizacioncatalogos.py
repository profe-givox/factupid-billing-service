#################### NOMINA #########################
import glob
import os
import pandas as pd
import requests
from sqlalchemy import create_engine, text, MetaData, Table
from sqlalchemy.dialects.postgresql import insert
from decouple import config

# ===== Diccionario de mapeos columna Excel -> columna DB =====
MAPPINGS = {
    'cfdi_banco': {
        'c_Banco': 'c_Banco',
        'Descripción': 'descripcion',
        'Nombre o razón social': 'razon_social',
        'Fecha inicio de vigencia': 'fecha_inicio_vigencia',
        'Fecha fin de vigencia': 'fecha_fin_vigencia',
    },
    'cfdi_origenrecurso': {
        'c_OrigenRecurso': 'c_OrigenRecurso',
        'Descripción': 'descripcion',
    },
    'cfdi_periodicidadpago': {
        'c_PeriodicidadPago': 'c_PeriodicidadPago',
        'Descripción': 'descripcion',
        'Fecha inicio de vigencia': 'fecha_inicio_vigencia',
        'Fecha fin de vigencia': 'fecha_fin_vigencia',
    },
    'cfdi_riesgopuesto': {
        'c_RiesgoPuesto': 'c_RiesgoPuesto',
        'Descripción': 'descripcion',
        'Fecha inicio de vigencia': 'fecha_inicio_vigencia',
        'Fecha fin de vigencia': 'fecha_fin_vigencia',
    },
    'cfdi_tipocontrato': {
        'c_TipoContrato': 'c_TipoContrato',
        'Descripción': 'descripcion',
    },
    'cfdi_tipodeduccion': {
        'c_TipoDeduccion': 'c_TipoDeduccion',
        'Descripción': 'descripcion',
        'Fecha inicio de vigencia': 'fecha_inicio_vigencia',
        'Fecha fin de vigencia': 'fecha_fin_vigencia',
    },
    'cfdi_tipohoras': {
        'c_TipoHoras': 'c_TipoHoras',
        'Descripción': 'descripcion',
    },
    'cfdi_tipoincapacidad': {
        'c_TipoIncapacidad': 'c_TipoIncapacidad',
        'Descripción': 'descripcion',
    },
    'cfdi_tipojornada': {
        'c_TipoJornada': 'c_TipoJornada',
        'Descripción': 'descripcion',
    },
    'cfdi_tiponomina': {
        'c_TipoNomina': 'c_TipoNomina',
        'Descripción': 'opcion',
    },
    'cfdi_tipootropago': {
        'c_TipoOtroPago': 'c_TipoOtroPago',
        'Descripción': 'descripcion',
        'Fecha inicio de vigencia': 'fecha_inicio_vigencia',
        'Fecha fin de vigencia': 'fecha_fin_vigencia',
    },
    'cfdi_tipopercepcion': {
        'c_TipoPercepcion': 'c_TipoPercepcion',
        'Descripción': 'descripcion',
        'Fecha inicio de vigencia': 'fecha_inicio_vigencia',
        'Fecha fin de vigencia': 'fecha_fin_vigencia',
    },
    'cfdi_tiporegimen': {
        'c_TipoRegimen': 'c_TipoRegimen',
        'Descripción': 'descripcion',
        'Fecha inicio de vigencia': 'fecha_inicio_vigencia',
        'Fecha fin de vigencia': 'fecha_fin_vigencia',
    },
}

# Diccionario: tabla -> (columna, longitud_deseada)
LPAD_QUERIES = {
    "cfdi_periodicidadpago":    [("c_PeriodicidadPago", 2)],
    "cfdi_tipocontrato":        [("c_TipoContrato", 2)],
    "cfdi_tipohoras":           [("c_TipoHoras", 2)],
    "cfdi_tipoincapacidad":     [("c_TipoIncapacidad", 2)],
    "cfdi_tipojornada":         [("c_TipoJornada", 2)],
    "cfdi_tipodeduccion":       [("c_TipoDeduccion", 3)],
    "cfdi_tipootropago":        [("c_TipoOtroPago", 3)],
    "cfdi_tipopercepcion":      [("c_TipoPercepcion", 3)],
    "cfdi_tiporegimen":         [("c_TipoRegimen", 2)],
}

# ===== CONEXIÓN A BASE =====
db_config = {
    "ENGINE": "django.db.backends.postgresql_psycopg2",
    "NAME": config('DB_NAME_SCRIPT'),
    "USER": config('DB_USER'),
    "PASSWORD": config('DB_PASSWORD'),
    "HOST": config('DB_HOST'),
    "PORT": config('DB_PORT'),
}

conn_str = (
    f"postgresql+psycopg2://{db_config['USER']}:{db_config['PASSWORD']}"
    f"@{db_config['HOST']}:{db_config['PORT']}/{db_config['NAME']}"
)
engine = create_engine(conn_str)

# ===== DESCARGA EL ARCHIVO XLS DE NOMINA =====
try:
    url = "http://omawww.sat.gob.mx/tramitesyservicios/Paginas/documentos/catNomina.xls"
    response = requests.get(url)
    with open("catNomina.xls", "wb") as f:
        f.write(response.content)
except Exception as e:
    print(f"Error al descargar el archivo XLS: {e}")
    exit(1)

try:
    xls = pd.ExcelFile("catNomina.xls", engine="xlrd")
    sheets = xls.sheet_names
except Exception as e:
    print(f"Error al abrir el archivo XLS: {e}")
    exit(1)

# ===== PROCESAR CADA HOJA =====
for sheet in sheets:
    try:
        preview = pd.read_excel(xls, sheet_name=sheet, nrows=10, header=None)
        header_row = None
        for i, row in preview.iterrows():
            row_str = [str(cell).strip() for cell in row]
            if any(c.startswith("c_") for c in row_str):
                header_row = i
                break
        if header_row is None:
            header_row = 4

        print(f"Hoja '{sheet}': usando header en la fila {header_row + 1}")

        df = pd.read_excel(xls, sheet_name=sheet, header=header_row)
        df.columns = [str(c).strip() for c in df.columns]
        df = df.loc[:, ~df.columns.str.startswith("Unnamed")]

        # === MAPEADO DE COLUMNAS ===
        safe_sheet = sheet.replace(" ", "_").replace("/", "_")
        if safe_sheet.lower().startswith("c_"):
            safe_sheet = "cfdi_" + safe_sheet[2:]
        safe_sheet = safe_sheet.lower()

        mapping = MAPPINGS.get(safe_sheet)
        if mapping:
            df = df.rename(columns=mapping)
            print(f"Columnas tras mapeo para {safe_sheet}: {df.columns.tolist()}")
        else:
            print(f"Advertencia: no hay mapeo para {safe_sheet}, se usan nombres originales.")

        table_name = safe_sheet

        # === UPSERT (INSERT OR UPDATE) ===
        if mapping:
            pk_col = list(mapping.values())[0]  # primera columna clave (ej: c_TipoDeduccion)
        else:
            pk_col = df.columns[0]

        print(f"Actualizando tabla '{table_name}' con UPSERT basado en '{pk_col}'...")

        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=engine)

        with engine.begin() as connection:
            for _, row in df.iterrows():
                row_data = {c: None if pd.isna(row[c]) else row[c] for c in df.columns}
                stmt = insert(table).values(**row_data)
                update_cols = {c: row_data[c] for c in df.columns if c != pk_col}
                stmt = stmt.on_conflict_do_update(
                    index_elements=[pk_col],
                    set_=update_cols
                )
                connection.execute(stmt)

        print(f"✅ Tabla '{table_name}' actualizada correctamente con UPSERT.\n")

        # === AJUSTE DE CEROS A LA IZQUIERDA ===
        for col_lpad in LPAD_QUERIES.get(table_name, []):
            col, width = col_lpad
            sql = f'''
                UPDATE {table_name}
                SET "{col}" = LPAD("{col}"::text, {width}, '0')
                WHERE "{col}" IS NOT NULL AND LENGTH("{col}"::text) < {width}
            '''
            try:
                with engine.begin() as connection:
                    connection.execute(text(sql))
                    print(f"Ajuste de ceros a la izquierda en {table_name}.{col} ({width} dígitos)")
            except Exception as e:
                print(f"Error ajustando ceros a la izquierda en {table_name}.{col}: {e}")

    except Exception as e:
        print(f"❌ Error procesando hoja '{sheet}': {e}\n")

# ==== ELIMINAR TODOS LOS CSV GENERADOS AL FINAL ====
csv_files = glob.glob("cfdi_*.csv")
for csv_file in csv_files:
    try:
        os.remove(csv_file)
        print(f"Archivo CSV eliminado: {csv_file}")
    except Exception as e:
        print(f"Error al eliminar {csv_file}: {e}")

print("✅ ¡Actualización de catálogos completada sin violar claves foráneas!")






# import glob
# import os
# import pandas as pd
# import requests
# from sqlalchemy import create_engine, text
# import pathlib
# import glob
# import os
# import pandas as pd
# import requests
# from sqlalchemy import create_engine, text
# import pathlib

# # ===== CONEXIÓN A BASE (SQLite local) =====

# db_config = {
#    "ENGINE": "django.db.backends.postgresql_psycopg2",
#     "NAME": "factupiddatabase",
#     "USER": "factupid",
#     "PASSWORD": "raspbian",
#     "HOST": "6.tcp.us-cal-1.ngrok.io",
#     "PORT": "19148",
# }

# conn_str = (
#     f"postgresql+psycopg2://{db_config['USER']}:{db_config['PASSWORD']}"
#     f"@{db_config['HOST']}:{db_config['PORT']}/{db_config['NAME']}"
# )
# engine = create_engine(conn_str)


# # ===== FUNCIÓN GENÉRICA PARA CREAR/ACTUALIZAR TABLAS =====
# def upsert_table(df, table_name):
#     """Si la tabla existe, elimina registros y los reemplaza. Si no existe, la crea."""
#     try:
#         with engine.begin() as connection:
#             connection.execute(text(f"DELETE FROM {table_name}"))
#             print(f"Datos de la tabla '{table_name}' eliminados correctamente.")
#     except Exception:
#         print(f"La tabla '{table_name}' no existe todavía. Se creará al insertar datos.")

#     df.to_sql(table_name, engine, if_exists='append', index=False)
#     print(f"Tabla '{table_name}' actualizada exitosamente.\n")





# # ===== ANEXO 20: Forma de Pago =====
# try:
#     url_anexo20 = "http://omawww.sat.gob.mx/tramitesyservicios/Paginas/documentos/catCFDI_V_4_20250917.xls"
#     response = requests.get(url_anexo20, timeout=60)
#     with open("catCFDI_V_4_20250917.xls", "wb") as f:
#         f.write(response.content)
#     print("Descargado: catCFDI_V_4_20250917.xls")

#     xls_a20 = pd.ExcelFile("catCFDI_V_4_20250917.xls", engine="xlrd")
#     sheets_a20 = xls_a20.sheet_names

#     hoja_forma_pago = None
#     for s in sheets_a20:
#         if "formapago" in s.lower():
#             hoja_forma_pago = s
#             break

#     preview = pd.read_excel(xls_a20, sheet_name=hoja_forma_pago, nrows=10, header=None)
#     header_row = None
#     for i, row in preview.iterrows():
#         row_str = [str(cell).strip() for cell in row]
#         if any(c.startswith("c_") for c in row_str):
#             header_row = i
#             break
#     if header_row is None:
#         header_row = 4

#     print(f"Hoja '{hoja_forma_pago}': usando header en la fila {header_row + 1}")

#     df_fp = pd.read_excel(xls_a20, sheet_name=hoja_forma_pago, header=header_row)
#     df_fp.columns = [str(c).strip() for c in df_fp.columns]
#     df_fp = df_fp.loc[:, ~df_fp.columns.str.startswith("Unnamed")]

#     forma_pago_mapping = {
#         'c_FormaPago': 'c_FormaPago',
#         'Descripción': 'descripcion',
#         'Bancarizado': 'bancarizado',
#         'Número de operación': 'num_operacion',
#         'RFC del Emisor de la cuenta ordenante': 'rfc_emisor_cta_ord',
#         'Cuenta Ordenante': 'cuenta_ordenante',
#         'Patrón para cuenta ordenante': 'patron_cta_ordenante',
#         'RFC del Emisor Cuenta de Beneficiario': 'rfc_emisor_cta_benef',
#         'Cuenta de Benenficiario': 'cuenta_beneficiario',
#         'Cuenta de Beneficiario': 'cuenta_beneficiario',
#         'Patrón para cuenta Beneficiaria': 'patron_cta_beneficiaria',
#         'Tipo Cadena Pago': 'tipo_cadena_pago',
#         'Nombre del Banco emisor de la cuenta ordenante en caso de extranjero': 'banco_extranjero',
#         'Fecha inicio de vigencia': 'fecha_inicio_vigencia',
#         'Fecha fin de vigencia': 'fecha_fin_vigencia',
#     }
#     df_fp = df_fp.rename(columns={c: forma_pago_mapping[c] for c in forma_pago_mapping if c in df_fp.columns})

#     if 'bancarizado' in df_fp.columns:
#         df_fp['bancarizado'] = df_fp['bancarizado'].map(
#             lambda x: 1 if str(x).strip().lower() in ["sí", "si"] else (0 if str(x).strip().lower() == "no" else x)
#         )

#     if 'c_FormaPago' in df_fp.columns:
#         df_fp['c_FormaPago'] = df_fp['c_FormaPago'].astype(str).str.replace(r'\.0$', '', regex=True).str.zfill(2)

#     # Crear/actualizar tabla
#     upsert_table(df_fp, "cfdi_formapago")

# except Exception as e:
#     print(f"❌ Error procesando Anexo 20 (Forma de Pago): {e}")


# # ==== LIMPIEZA ====
# for f in ["catNomina.xls", "catCFDI_V_4_20250917.xls"]:
#     try:
#         os.remove(f)
#         print(f"Archivo XLS eliminado: {f}")
#     except Exception:
#         pass

# print("¡Conversión e importación completas en SQLite!")



# #MONEDA

# try:
#     xls_a20 = pd.ExcelFile("catCFDI_V_4_20250917.xls", engine="xlrd")
#     sheets_a20 = xls_a20.sheet_names

#     hoja_moneda = None
#     for s in sheets_a20:
#         if "moneda" in s.lower():
#             hoja_moneda = s
#             break

#     if hoja_moneda is None:
#         raise ValueError("No se encontró hoja de Moneda en el Anexo 20")

#     preview = pd.read_excel(xls_a20, sheet_name=hoja_moneda, nrows=10, header=None)
#     header_row = None
#     for i, row in preview.iterrows():
#         row_str = [str(cell).strip() for cell in row]
#         if any(c.startswith("c_") for c in row_str):
#             header_row = i
#             break
#     if header_row is None:
#         header_row = 4

#     print(f"Hoja '{hoja_moneda}': usando header en la fila {header_row + 1}")

#     df_mon = pd.read_excel(xls_a20, sheet_name=hoja_moneda, header=header_row)
#     df_mon.columns = [str(c).strip() for c in df_mon.columns]
#     df_mon = df_mon.loc[:, ~df_mon.columns.str.startswith("Unnamed")]

#     moneda_mapping = {
#         'c_Moneda': 'c_Moneda',
#         'Descripción': 'descripcion',
#         'Decimales': 'decimales',
#         'Porcentaje variación': 'porcentaje_variacion',
#         'Fecha inicio de vigencia': 'fecha_inicio_vigencia',
#         'Fecha fin de vigencia': 'fecha_fin_vigencia',
#     }
#     df_mon = df_mon.rename(columns={c: moneda_mapping[c] for c in moneda_mapping if c in df_mon.columns})

#     # --- Limpieza ---
#     if 'variacion' in df_mon.columns:
#         df_mon['variacion'] = (
#             df_mon['variacion']
#             .astype(str)
#             .str.replace('%', '', regex=False)
#             .replace("nan", "0")
#         )
#         df_mon['variacion'] = pd.to_numeric(df_mon['variacion'], errors='coerce').fillna(0).astype(int)

#     if 'decimales' in df_mon.columns:
#         df_mon['decimales'] = pd.to_numeric(df_mon['decimales'], errors='coerce').fillna(0).astype(int)

#     # Crear/actualizar tabla
#     upsert_table(df_mon, "cfdi_moneda")

# except Exception as e:
#     print(f"❌ Error procesando Anexo 20 (Moneda): {e}")



# # ===== ANEXO 20: Tipo de Comprobante =====
# try:
#     xls_a20 = pd.ExcelFile("catCFDI_V_4_20250917.xls", engine="xlrd")
#     sheets_a20 = xls_a20.sheet_names

#     hoja_tc = None
#     for s in sheets_a20:
#         if "tipodecomprobante" in s.lower():
#             hoja_tc = s
#             break

#     if hoja_tc is None:
#         raise ValueError("No se encontró hoja de Tipo de Comprobante en el Anexo 20")

#     preview = pd.read_excel(xls_a20, sheet_name=hoja_tc, nrows=10, header=None)
#     header_row = None
#     for i, row in preview.iterrows():
#         row_str = [str(cell).strip() for cell in row]
#         if any(c.startswith("c_") for c in row_str):
#             header_row = i
#             break
#     if header_row is None:
#         header_row = 4

#     print(f"Hoja '{hoja_tc}': usando header en la fila {header_row + 1}")

#     # Leemos con encabezado detectado
#     df_tc = pd.read_excel(xls_a20, sheet_name=hoja_tc, header=header_row)
#     df_tc.columns = [str(c).strip() for c in df_tc.columns]
#     df_tc = df_tc.loc[:, ~df_tc.columns.str.startswith("Unnamed")]

#     # Mapping
#     tc_mapping = {
#         'c_TipoDeComprobante': 'c_TipoDeComprobante',
#         'Descripción': 'descripcion',
#         'Valor máximo': 'valor_maximo',
#         'NS': 'ns',
#         'NdS': 'nds',
#         'Fecha inicio de vigencia': 'fecha_inicio_vigencia',
#         'Fecha fin de vigencia': 'fecha_fin_vigencia',
#     }
#     df_tc = df_tc.rename(columns={c: tc_mapping[c] for c in tc_mapping if c in df_tc.columns})

#     # --- Normalización especial para Nómina ---
#     filas_nomina = df_tc[df_tc['c_TipoComprobante'].astype(str).str.strip() == 'N']
#     if not filas_nomina.empty:
#         idx_nomina = filas_nomina.index[0]
#         if idx_nomina + 1 in df_tc.index:
#             # Insertamos manualmente los valores en la fila "N"
#             df_tc.loc[idx_nomina, 'ns'] = 0
#             df_tc.loc[idx_nomina, 'valor_maximo'] = str(df_tc.loc[idx_nomina + 1, 'Valor máximo']) if 'Valor máximo' in df_tc.columns else None
#             df_tc.loc[idx_nomina, 'nds'] = str(df_tc.loc[idx_nomina + 1, 'NdS']) if 'NdS' in df_tc.columns else None
#             # Eliminamos la fila extra
#             df_tc = df_tc.drop(idx_nomina + 1)

#     # Limpiamos valores nulos/NaN
#     for col in ['valor_maximo', 'ns', 'nds']:
#         if col in df_tc.columns:
#             df_tc[col] = df_tc[col].astype(str).replace("nan", "")

#     # Crear/actualizar tabla en cfdi_tipocomprobante
#     upsert_table(df_tc, "cfdi_tipocomprobante")

# except Exception as e:
#     print(f"❌ Error procesando Anexo 20 (Tipo de Comprobante): {e}")



# # ==== Exportacion ====

# # ===== ANEXO 20: Exportación =====
# try:
#     xls_a20 = pd.ExcelFile("catCFDI_V_4_20250917.xls", engine="xlrd")
#     sheets_a20 = xls_a20.sheet_names

#     hoja_export = None
#     for s in sheets_a20:
#         if "exportacion" in s.lower():
#             hoja_export = s
#             break

#     if hoja_export is None:
#         raise ValueError("No se encontró hoja de Exportación en el Anexo 20")

#     preview = pd.read_excel(xls_a20, sheet_name=hoja_export, nrows=10, header=None)
#     header_row = None
#     for i, row in preview.iterrows():
#         row_str = [str(cell).strip() for cell in row]
#         if any(c.startswith("c_") for c in row_str):
#             header_row = i
#             break
#     if header_row is None:
#         header_row = 4

#     print(f"Hoja '{hoja_export}': usando header en la fila {header_row + 1}")

#     df_exp = pd.read_excel(xls_a20, sheet_name=hoja_export, header=header_row)
#     df_exp.columns = [str(c).strip() for c in df_exp.columns]
#     df_exp = df_exp.loc[:, ~df_exp.columns.str.startswith("Unnamed")]

#     export_mapping = {
#         'c_Exportacion': 'c_Exportacion',
#         'Descripción': 'descripcion',
#         'Fecha inicio de vigencia': 'fecha_inicio_vigencia',
#         'Fecha fin de vigencia': 'fecha_fin_vigencia',
#     }
#     df_exp = df_exp.rename(columns={c: export_mapping[c] for c in export_mapping if c in df_exp.columns})

#     # Normalizar c_Exportacion a 2 dígitos
#     if 'c_Exportacion' in df_exp.columns:
#         df_exp['c_Exportacion'] = df_exp['c_Exportacion'].astype(str).str.replace(r'\.0$', '', regex=True).str.zfill(2)

#     # Crear/actualizar tabla
#     upsert_table(df_exp, "cfdi_exportacion")

# except Exception as e:
#     print(f"❌ Error procesando Anexo 20 (Exportación): {e}")


# # ===== ANEXO 20: Método de Pago =====
# try:
#     xls_a20 = pd.ExcelFile("catCFDI_V_4_20250917.xls", engine="xlrd")
#     sheets_a20 = xls_a20.sheet_names

#     hoja_metodo = None
#     for s in sheets_a20:
#         if "metodopago" in s.lower():
#             hoja_metodo = s
#             break

#     if hoja_metodo is None:
#         raise ValueError("No se encontró hoja de Método de Pago en el Anexo 20")

#     preview = pd.read_excel(xls_a20, sheet_name=hoja_metodo, nrows=10, header=None)
#     header_row = None
#     for i, row in preview.iterrows():
#         row_str = [str(cell).strip() for cell in row]
#         if any(c.startswith("c_") for c in row_str):
#             header_row = i
#             break
#     if header_row is None:
#         header_row = 4

#     print(f"Hoja '{hoja_metodo}': usando header en la fila {header_row + 1}")

#     df_mp = pd.read_excel(xls_a20, sheet_name=hoja_metodo, header=header_row)
#     df_mp.columns = [str(c).strip() for c in df_mp.columns]
#     df_mp = df_mp.loc[:, ~df_mp.columns.str.startswith("Unnamed")]

#     metodo_mapping = {
#         'c_MetodoPago': 'c_MetodoPago',
#         'Descripción': 'descripcion',
#         'Fecha inicio de vigencia': 'fecha_inicio_vigencia',
#         'Fecha fin de vigencia': 'fecha_fin_vigencia',
#     }
#     df_mp = df_mp.rename(columns={c: metodo_mapping[c] for c in metodo_mapping if c in df_mp.columns})

#     # Normalizar fechas a formato YYYY-MM-DD
#     for col in ['fecha_inicio_vigencia', 'fecha_fin_vigencia']:
#         if col in df_mp.columns:
#             df_mp[col] = pd.to_datetime(df_mp[col], errors='coerce').dt.strftime('%Y-%m-%d')

#     # Crear/actualizar tabla
#     upsert_table(df_mp, "cfdi_metodopago")

# except Exception as e:
#     print(f"❌ Error procesando Anexo 20 (Método de Pago): {e}")


# # ==== codigo postal ====

# # ===== ANEXO 20: Código Postal =====
# try:
#     xls_a20 = pd.ExcelFile("catCFDI_V_4_20250917.xls", engine="xlrd")
#     sheets_a20 = xls_a20.sheet_names

#     hoja_cp = None
#     for s in sheets_a20:
#         if "codigopostal" in s.lower():
#             hoja_cp = s
#             break

#     if hoja_cp is None:
#         raise ValueError("No se encontró hoja de Código Postal en el Anexo 20")

#     preview = pd.read_excel(xls_a20, sheet_name=hoja_cp, nrows=10, header=None)
#     header_row = None
#     for i, row in preview.iterrows():
#         row_str = [str(cell).strip() for cell in row]
#         if any(c.startswith("c_") for c in row_str):
#             header_row = i
#             break
#     if header_row is None:
#         header_row = 4

#     print(f"Hoja '{hoja_cp}': usando header en la fila {header_row + 1}")

#     df_cp = pd.read_excel(xls_a20, sheet_name=hoja_cp, header=header_row)
#     df_cp.columns = [str(c).strip() for c in df_cp.columns]
#     df_cp = df_cp.loc[:, ~df_cp.columns.str.startswith("Unnamed")]

#     cp_mapping = {
#         'c_CodigoPostal': 'c_CodigoPostal',
#         'c_Estado': 'c_Estado_id',
#         'c_Municipio': 'c_Municipio_id',
#         'c_Localidad': 'c_Localidad_id',
#         'Estímulo Franja Fronteriza': 'estimulo_franja_fronteriza',
#         'Fecha inicio de vigencia': 'fecha_inicio_vigencia',
#         'Fecha fin de vigencia': 'fecha_fin_vigencia',
#         'Descripción del Huso Horario': 'descripcion_huso_horario',
#         'Mes_Inicio_Horario_Verano': 'mes_inicio_verano',
#         'Día_Inicio_Horario_Verano': 'dia_inicio_verano',
#         'Hora_Inicio_Horario_Verano': 'hora_inicio_verano',
#         'Diferencia_Horaria_Verano': 'diferencia_verano',
#         'Mes_Inicio_Horario_Invierno': 'mes_inicio_invierno',
#         'Día_Inicio_Horario_Invierno': 'dia_inicio_invierno',
#         'Hora_Inicio_Horario_Invierno': 'hora_inicio_invierno',
#         'Diferencia_Horaria_Invierno': 'diferencia_invierno',
#     }
#     df_cp = df_cp.rename(columns={c: cp_mapping[c] for c in cp_mapping if c in df_cp.columns})

#     # Normalizar estímulo (0/1 en vez de NaN)
#     if 'franja_fronteriza' in df_cp.columns:
#         df_cp['franja_fronteriza'] = df_cp['franja_fronteriza'].fillna(0).astype(int)

#     # Normalizar fechas a formato YYYY-MM-DD
#     for col in ['fecha_inicio_vigencia', 'fecha_fin_vigencia']:
#         if col in df_cp.columns:
#             df_cp[col] = pd.to_datetime(df_cp[col], errors='coerce').dt.strftime('%Y-%m-%d')

#     # Normalizar CP (rellenar con ceros si es necesario)
#     if 'c_CodigoPostal' in df_cp.columns:
#         df_cp['c_CodigoPostal'] = df_cp['c_CodigoPostal'].astype(str).str.replace(r'\.0$', '', regex=True).str.zfill(5)

#     # Crear/actualizar tabla
#     upsert_table(df_cp, "cfdi_codigopostal")

# except Exception as e:
#     print(f"❌ Error procesando Anexo 20 (Código Postal): {e}")



# # ==== periodicidad ====
# # ===== ANEXO 20: Periodicidad =====
# try:
#     xls_a20 = pd.ExcelFile("catCFDI_V_4_20250917.xls", engine="xlrd")
#     sheets_a20 = xls_a20.sheet_names

#     hoja_periodicidad = None
#     for s in sheets_a20:
#         if "periodicidad" in s.lower():
#             hoja_periodicidad = s
#             break

#     if hoja_periodicidad is None:
#         raise ValueError("No se encontró hoja de Periodicidad en el Anexo 20")

#     preview = pd.read_excel(xls_a20, sheet_name=hoja_periodicidad, nrows=10, header=None)
#     header_row = None
#     for i, row in preview.iterrows():
#         row_str = [str(cell).strip() for cell in row]
#         if any(c.startswith("c_") for c in row_str):
#             header_row = i
#             break
#     if header_row is None:
#         header_row = 4

#     print(f"Hoja '{hoja_periodicidad}': usando header en la fila {header_row + 1}")

#     df_per = pd.read_excel(xls_a20, sheet_name=hoja_periodicidad, header=header_row)
#     df_per.columns = [str(c).strip() for c in df_per.columns]
#     df_per = df_per.loc[:, ~df_per.columns.str.startswith("Unnamed")]

#     periodicidad_mapping = {
#         'c_Periodicidad': 'c_Periodicidad',
#         'Descripción': 'descripcion',
#         'Fecha inicio de vigencia': 'fecha_inicio_vigencia',
#         'Fecha fin de vigencia': 'fecha_fin_vigencia',
#     }
#     df_per = df_per.rename(columns={c: periodicidad_mapping[c] for c in periodicidad_mapping if c in df_per.columns})

#     # Normalizar c_Periodicidad a 2 dígitos
#     if 'c_Periodicidad' in df_per.columns:
#         df_per['c_Periodicidad'] = df_per['c_Periodicidad'].astype(str).str.replace(r'\.0$', '', regex=True).str.zfill(2)

#     # Normalizar fechas
#     for col in ['fecha_inicio_vigencia', 'fecha_fin_vigencia']:
#         if col in df_per.columns:
#             df_per[col] = pd.to_datetime(df_per[col], errors='coerce').dt.strftime('%Y-%m-%d')

#     # Crear/actualizar tabla
#     upsert_table(df_per, "cfdi_periodicidad")

# except Exception as e:
#     print(f"❌ Error procesando Anexo 20 (Periodicidad): {e}")

# # ===== ANEXO 20: Meses =====
# try:
#     xls_a20 = pd.ExcelFile("catCFDI_V_4_20250917.xls", engine="xlrd")
#     sheets_a20 = xls_a20.sheet_names

#     hoja_meses = None
#     for s in sheets_a20:
#         if "meses" in s.lower():
#             hoja_meses = s
#             break

#     if hoja_meses is None:
#         raise ValueError("No se encontró hoja de Meses en el Anexo 20")

#     preview = pd.read_excel(xls_a20, sheet_name=hoja_meses, nrows=10, header=None)
#     header_row = None
#     for i, row in preview.iterrows():
#         row_str = [str(cell).strip() for cell in row]
#         if any(c.startswith("c_") for c in row_str):
#             header_row = i
#             break
#     if header_row is None:
#         header_row = 4

#     print(f"Hoja '{hoja_meses}': usando header en la fila {header_row + 1}")

#     df_mes = pd.read_excel(xls_a20, sheet_name=hoja_meses, header=header_row)
#     df_mes.columns = [str(c).strip() for c in df_mes.columns]
#     df_mes = df_mes.loc[:, ~df_mes.columns.str.startswith("Unnamed")]

#     meses_mapping = {
#         'c_Meses': 'c_Meses',
#         'Descripción': 'descripcion',
#         'Fecha inicio de vigencia': 'fecha_inicio_vigencia',
#         'Fecha fin de vigencia': 'fecha_fin_vigencia',
#     }
#     df_mes = df_mes.rename(columns={c: meses_mapping[c] for c in meses_mapping if c in df_mes.columns})

#     # Normalizar c_Meses a 2 dígitos
#     if 'c_Meses' in df_mes.columns:
#         df_mes['c_Meses'] = df_mes['c_Meses'].astype(str).str.replace(r'\.0$', '', regex=True).str.zfill(2)

#     # Normalizar fechas
#     for col in ['fecha_inicio_vigencia', 'fecha_fin_vigencia']:
#         if col in df_mes.columns:
#             df_mes[col] = pd.to_datetime(df_mes[col], errors='coerce').dt.strftime('%Y-%m-%d')

#     # Crear/actualizar tabla
#     upsert_table(df_mes, "cfdi_meses")

# except Exception as e:
#     print(f"❌ Error procesando Anexo 20 (Meses): {e}")


# # ===== ANEXO 20: Tipo de Relación =====
# try:
#     xls_a20 = pd.ExcelFile("catCFDI_V_4_20250917.xls", engine="xlrd")
#     sheets_a20 = xls_a20.sheet_names

#     hoja_relacion = None
#     for s in sheets_a20:
#         if "tiporelacion" in s.lower():
#             hoja_relacion = s
#             break

#     if hoja_relacion is None:
#         raise ValueError("No se encontró hoja de Tipo de Relación en el Anexo 20")

#     preview = pd.read_excel(xls_a20, sheet_name=hoja_relacion, nrows=10, header=None)
#     header_row = None
#     for i, row in preview.iterrows():
#         row_str = [str(cell).strip() for cell in row]
#         if any(c.startswith("c_") for c in row_str):
#             header_row = i
#             break
#     if header_row is None:
#         header_row = 4

#     print(f"Hoja '{hoja_relacion}': usando header en la fila {header_row + 1}")

#     df_rel = pd.read_excel(xls_a20, sheet_name=hoja_relacion, header=header_row)
#     df_rel.columns = [str(c).strip() for c in df_rel.columns]
#     df_rel = df_rel.loc[:, ~df_rel.columns.str.startswith("Unnamed")]

#     relacion_mapping = {
#         'c_TipoRelacion': 'c_TipoRelacion',
#         'Descripción': 'descripcion',
#         'Fecha inicio de vigencia': 'fecha_inicio_vigencia',
#         'Fecha fin de vigencia': 'fecha_fin_vigencia',
#     }
#     df_rel = df_rel.rename(columns={c: relacion_mapping[c] for c in relacion_mapping if c in df_rel.columns})

#     # Normalizar c_TipoRelacion a 2 dígitos
#     if 'c_TipoRelacion' in df_rel.columns:
#         df_rel['c_TipoRelacion'] = df_rel['c_TipoRelacion'].astype(str).str.replace(r'\.0$', '', regex=True).str.zfill(2)

#     # Normalizar fechas
#     for col in ['fecha_inicio_vigencia', 'fecha_fin_vigencia']:
#         if col in df_rel.columns:
#             df_rel[col] = pd.to_datetime(df_rel[col], errors='coerce').dt.strftime('%Y-%m-%d')

#     # Crear/actualizar tabla
#     upsert_table(df_rel, "cfdi_tiporelacion")

# except Exception as e:
#     print(f"❌ Error procesando Anexo 20 (Tipo de Relación): {e}")


# # ===== ANEXO 20: regimen fiscal =====

# # ===== ANEXO 20: Régimen Fiscal =====
# try:
#     xls_a20 = pd.ExcelFile("catCFDI_V_4_20250917.xls", engine="xlrd")
#     sheets_a20 = xls_a20.sheet_names

#     hoja_regimen = None
#     for s in sheets_a20:
#         if "regimenfiscal" in s.lower():
#             hoja_regimen = s
#             break

#     if hoja_regimen is None:
#         raise ValueError("No se encontró hoja de Régimen Fiscal en el Anexo 20")

#     preview = pd.read_excel(xls_a20, sheet_name=hoja_regimen, nrows=10, header=None)
#     header_row = None
#     for i, row in preview.iterrows():
#         row_str = [str(cell).strip() for cell in row]
#         if any(c.startswith("c_") for c in row_str):
#             header_row = i
#             break
#     if header_row is None:
#         header_row = 4

#     print(f"Hoja '{hoja_regimen}': usando header en la fila {header_row + 1}")

#     df_reg = pd.read_excel(xls_a20, sheet_name=hoja_regimen, header=header_row)
#     df_reg.columns = [str(c).strip() for c in df_reg.columns]
#     df_reg = df_reg.loc[:, ~df_reg.columns.str.startswith("Unnamed")]

#     regimen_mapping = {
#         'c_RegimenFiscal': 'c_RegimenFiscal',
#         'Descripción': 'descripcion',
#         'Física': 'fisica',
#         'Moral': 'moral',
#         'Fecha de inicio de vigencia': 'fecha_inicio_vigencia',
#         'Fecha de fin de vigencia': 'fecha_fin_vigencia',
#     }
#     df_reg = df_reg.rename(columns={c: regimen_mapping[c] for c in regimen_mapping if c in df_reg.columns})

#     # Convertir Física/Moral de Sí/No a 1/0
#     for col in ['fisica', 'moral']:
#         if col in df_reg.columns:
#             df_reg[col] = df_reg[col].map(
#                 lambda x: 1 if str(x).strip().lower() in ["sí", "si"] else (0 if str(x).strip().lower() == "no" else x)
#             )

#     # Normalizar fechas
#     for col in ['fecha_inicio_vigencia', 'fecha_fin_vigencia']:
#         if col in df_reg.columns:
#             df_reg[col] = pd.to_datetime(df_reg[col], errors='coerce').dt.strftime('%Y-%m-%d')

#     # Crear/actualizar tabla
#     upsert_table(df_reg, "cfdi_regimenfiscal")

# except Exception as e:
#     print(f"❌ Error procesando Anexo 20 (Régimen Fiscal): {e}")

# # ==== pais ====

# # ===== ANEXO 20: País =====
# try:
#     xls_a20 = pd.ExcelFile("catCFDI_V_4_20250917.xls", engine="xlrd")
#     sheets_a20 = xls_a20.sheet_names

#     hoja_pais = None
#     for s in sheets_a20:
#         if "pais" in s.lower():
#             hoja_pais = s
#             break

#     if hoja_pais is None:
#         raise ValueError("No se encontró hoja de País en el Anexo 20")

#     preview = pd.read_excel(xls_a20, sheet_name=hoja_pais, nrows=10, header=None)
#     header_row = None
#     for i, row in preview.iterrows():
#         row_str = [str(cell).strip() for cell in row]
#         if any(c.startswith("c_") for c in row_str):
#             header_row = i
#             break
#     if header_row is None:
#         header_row = 4

#     print(f"Hoja '{hoja_pais}': usando header en la fila {header_row + 1}")

#     df_pais = pd.read_excel(xls_a20, sheet_name=hoja_pais, header=header_row)
#     df_pais.columns = [str(c).strip() for c in df_pais.columns]
#     df_pais = df_pais.loc[:, ~df_pais.columns.str.startswith("Unnamed")]

#     pais_mapping = {
#         'c_Pais': 'c_Pais',
#         'Descripción': 'descripcion',
#         'Formato de código postal': 'formato_codigo_postal',
#         'Formato de Registro de Identidad Tributaria': 'formato_rfc',
#         'Validación del Registro de Identidad Tributaria': 'validacion_rfc',
#         'Agrupaciones': 'agrupaciones',
#     }
#     df_pais = df_pais.rename(columns={c: pais_mapping[c] for c in pais_mapping if c in df_pais.columns})

#     # Reemplazar NaN vacíos con None para compatibilidad
#     df_pais = df_pais.where(pd.notnull(df_pais), None)

#     # Crear/actualizar tabla
#     upsert_table(df_pais, "cfdi_pais")

# except Exception as e:
#     print(f"❌ Error procesando Anexo 20 (País): {e}")


# # # ==== usocfdi ====
# # ===== ANEXO 20: Uso CFDI =====
# try:
#     xls_a20 = pd.ExcelFile("catCFDI_V_4_20250917.xls", engine="xlrd")
#     sheets_a20 = xls_a20.sheet_names

#     hoja_uso = None
#     for s in sheets_a20:
#         if "usocfdi" in s.lower():
#             hoja_uso = s
#             break

#     if hoja_uso is None:
#         raise ValueError("No se encontró hoja de UsoCFDI en el Anexo 20")

#     preview = pd.read_excel(xls_a20, sheet_name=hoja_uso, nrows=10, header=None)
#     header_row = None
#     for i, row in preview.iterrows():
#         row_str = [str(cell).strip() for cell in row]
#         if any(c.startswith("c_") for c in row_str):
#             header_row = i
#             break
#     if header_row is None:
#         header_row = 4

#     print(f"Hoja '{hoja_uso}': usando header en la fila {header_row + 1}")

#     df_uso = pd.read_excel(xls_a20, sheet_name=hoja_uso, header=header_row)
#     df_uso.columns = [str(c).strip() for c in df_uso.columns]
#     df_uso = df_uso.loc[:, ~df_uso.columns.str.startswith("Unnamed")]

#     uso_mapping = {
#         'c_UsoCFDI': 'c_UsoCFDI',
#         'Descripción': 'descripcion',
#         'Física': 'aplica_fisica',
#         'Moral': 'aplica_moral',
#         'Fecha inicio de vigencia': 'fecha_inicio_vigencia',
#         'Fecha fin de vigencia': 'fecha_fin_vigencia',
#         #'Régimen Fiscal Receptor': 'regimenes',
#     }
#     df_uso = df_uso.rename(columns={c: uso_mapping[c] for c in uso_mapping if c in df_uso.columns})

#     # Convertir Física/Moral de Sí/No a 1/0
#     for col in ['fisica', 'moral']:
#         if col in df_uso.columns:
#             df_uso[col] = df_uso[col].map(
#                 lambda x: 1 if str(x).strip().lower() in ["sí", "si"] else (0 if str(x).strip().lower() == "no" else x)
#             )

#     # Normalizar fechas
#     for col in ['fecha_inicio_vigencia', 'fecha_fin_vigencia']:
#         if col in df_uso.columns:
#             df_uso[col] = pd.to_datetime(df_uso[col], errors='coerce').dt.strftime('%Y-%m-%d')

#     # Crear/actualizar tabla
#     upsert_table(df_uso, "cfdi_usocfdi")

# except Exception as e:
#     print(f"❌ Error procesando Anexo 20 (Uso CFDI): {e}")


# # ===== ANEXO 20: ClaveProdServ =====
# try:
#     xls_a20 = pd.ExcelFile("catCFDI_V_4_20250917.xls", engine="xlrd")
#     sheets_a20 = xls_a20.sheet_names

#     hoja_clave = None
#     for s in sheets_a20:
#         if "claveprodserv" in s.lower():
#             hoja_clave = s
#             break

#     if hoja_clave is None:
#         raise ValueError("No se encontró hoja de ClaveProdServ en el Anexo 20")

#     preview = pd.read_excel(xls_a20, sheet_name=hoja_clave, nrows=10, header=None)
#     header_row = None
#     for i, row in preview.iterrows():
#         row_str = [str(cell).strip() for cell in row]
#         if any(c.startswith("c_") for c in row_str):
#             header_row = i
#             break
#     if header_row is None:
#         header_row = 4

#     print(f"Hoja '{hoja_clave}': usando header en la fila {header_row + 1}")

#     df_clave = pd.read_excel(xls_a20, sheet_name=hoja_clave, header=header_row)
#     df_clave.columns = [str(c).strip() for c in df_clave.columns]
#     df_clave = df_clave.loc[:, ~df_clave.columns.str.startswith("Unnamed")]

#     clave_mapping = {
#         'c_ClaveProdServ': 'c_ClaveProdServ',
#         'Descripción': 'descripcion',
#         'Incluir IVA trasladado': 'incluir_iva_trasladado',
#         'Incluir IEPS trasladado': 'incluir_ieps_trasladado',
#         'Complemento que debe incluir': 'complemento_incluir',
#         'FechaInicioVigencia': 'fecha_inicio_vigencia',
#         'FechaFinVigencia': 'fecha_fin_vigencia',
#         'Estímulo Franja Fronteriza': 'estimulo_franja_fronteriza',
#         'Palabras similares': 'palabras_similares',
#     }
#     df_clave = df_clave.rename(columns={c: clave_mapping[c] for c in clave_mapping if c in df_clave.columns})

#     # Normalizar fechas
#     for col in ['fecha_inicio_vigencia', 'fecha_fin_vigencia']:
#         if col in df_clave.columns:
#             df_clave[col] = pd.to_datetime(df_clave[col], errors='coerce').dt.strftime('%Y-%m-%d')

#     # Reemplazar NaN por None
#     df_clave = df_clave.where(pd.notnull(df_clave), None)

#     # Convertir estímulo de texto/número a entero 0/1
#     if 'estimulo_frontera' in df_clave.columns:
#         df_clave['estimulo_frontera'] = df_clave['estimulo_frontera'].fillna(0).astype(int)

#     # Crear/actualizar tabla
#     upsert_table(df_clave, "cfdi_claveprodserv")

# except Exception as e:
#     print(f"❌ Error procesando Anexo 20 (ClaveProdServ): {e}")


# # ===== ANEXO 20: ClaveUnidad =====
# try:
#     xls_a20 = pd.ExcelFile("catCFDI_V_4_20250917.xls", engine="xlrd")
#     sheets_a20 = xls_a20.sheet_names

#     hoja_unidad = None
#     for s in sheets_a20:
#         if "claveunidad" in s.lower():
#             hoja_unidad = s
#             break

#     if hoja_unidad is None:
#         raise ValueError("No se encontró hoja de ClaveUnidad en el Anexo 20")

#     preview = pd.read_excel(xls_a20, sheet_name=hoja_unidad, nrows=10, header=None)
#     header_row = None
#     for i, row in preview.iterrows():
#         row_str = [str(cell).strip() for cell in row]
#         if any(c.startswith("c_") for c in row_str):
#             header_row = i
#             break
#     if header_row is None:
#         header_row = 4

#     print(f"Hoja '{hoja_unidad}': usando header en la fila {header_row + 1}")

#     df_unidad = pd.read_excel(xls_a20, sheet_name=hoja_unidad, header=header_row)
#     df_unidad.columns = [str(c).strip() for c in df_unidad.columns]
#     df_unidad = df_unidad.loc[:, ~df_unidad.columns.str.startswith("Unnamed")]

#     unidad_mapping = {
#         'c_ClaveUnidad': 'c_ClaveUnidad',
#         'Nombre': 'nombre',
#         'Descripción': 'descripcion',
#         'Nota': 'nota',
#         'FechaInicioVigencia': 'fecha_inicio_vigencia',
#         'FechaFinVigencia': 'fecha_fin_vigencia',
#         'Símbolo': 'simbolo'
#     }
#     df_unidad = df_unidad.rename(columns={c: unidad_mapping[c] for c in unidad_mapping if c in df_unidad.columns})

#     # Normalizar fechas
#     for col in ['fecha_inicio_vigencia', 'fecha_fin_vigencia']:
#         if col in df_unidad.columns:
#             df_unidad[col] = pd.to_datetime(df_unidad[col], errors='coerce').dt.strftime('%Y-%m-%d')

#     # Reemplazar NaN por None
#     df_unidad = df_unidad.where(pd.notnull(df_unidad), None)

#     # Crear/actualizar tabla
#     upsert_table(df_unidad, "cfdi_claveunidad")

# except Exception as e:
#     print(f"❌ Error procesando Anexo 20 (ClaveUnidad): {e}")



# # ===== ANEXO 20: ObjetoImp =====
# try:
#     xls_a20 = pd.ExcelFile("catCFDI_V_4_20250917.xls", engine="xlrd")
#     sheets_a20 = xls_a20.sheet_names

#     hoja_objeto = None
#     for s in sheets_a20:
#         if "objetoimp" in s.lower():
#             hoja_objeto = s
#             break

#     if hoja_objeto is None:
#         raise ValueError("No se encontró hoja de ObjetoImp en el Anexo 20")

#     preview = pd.read_excel(xls_a20, sheet_name=hoja_objeto, nrows=10, header=None)
#     header_row = None
#     for i, row in preview.iterrows():
#         row_str = [str(cell).strip() for cell in row]
#         if any(c.startswith("c_") for c in row_str):
#             header_row = i
#             break
#     if header_row is None:
#         header_row = 4

#     print(f"Hoja '{hoja_objeto}': usando header en la fila {header_row + 1}")

#     df_objeto = pd.read_excel(xls_a20, sheet_name=hoja_objeto, header=header_row)
#     df_objeto.columns = [str(c).strip() for c in df_objeto.columns]
#     df_objeto = df_objeto.loc[:, ~df_objeto.columns.str.startswith("Unnamed")]

#     objeto_mapping = {
#         'c_ObjetoImp': 'c_ObjetoImp',
#         'Descripción': 'descripcion',
#         'Fecha inicio de vigencia': 'fecha_inicio_vigencia',
#         'Fecha fin de vigencia': 'fecha_fin_vigencia'
#     }
#     df_objeto = df_objeto.rename(columns={c: objeto_mapping[c] for c in objeto_mapping if c in df_objeto.columns})

#     # Normalizar fechas
#     for col in ['fecha_inicio_vigencia', 'fecha_fin_vigencia']:
#         if col in df_objeto.columns:
#             df_objeto[col] = pd.to_datetime(df_objeto[col], errors='coerce').dt.strftime('%Y-%m-%d')

#     # Reemplazar NaN por None
#     df_objeto = df_objeto.where(pd.notnull(df_objeto), None)

#     # Crear/actualizar tabla
#     upsert_table(df_objeto, "cfdi_objetoimp")

# except Exception as e:
#     print(f"❌ Error procesando Anexo 20 (ObjetoImp): {e}")


# # ===== ANEXO 20: Impuesto =====
# try:
#     xls_a20 = pd.ExcelFile("catCFDI_V_4_20250917.xls", engine="xlrd")
#     sheets_a20 = xls_a20.sheet_names

#     hoja_impuesto = None
#     for s in sheets_a20:
#         if "impuesto" in s.lower():
#             hoja_impuesto = s
#             break

#     if hoja_impuesto is None:
#         raise ValueError("No se encontró hoja de Impuesto en el Anexo 20")

#     preview = pd.read_excel(xls_a20, sheet_name=hoja_impuesto, nrows=10, header=None)
#     header_row = None
#     for i, row in preview.iterrows():
#         row_str = [str(cell).strip() for cell in row]
#         if any(c.startswith("c_") for c in row_str):
#             header_row = i
#             break
#     if header_row is None:
#         header_row = 4

#     print(f"Hoja '{hoja_impuesto}': usando header en la fila {header_row + 1}")

#     df_impuesto = pd.read_excel(xls_a20, sheet_name=hoja_impuesto, header=header_row)
#     df_impuesto.columns = [str(c).strip() for c in df_impuesto.columns]
#     df_impuesto = df_impuesto.loc[:, ~df_impuesto.columns.str.startswith("Unnamed")]

#     impuesto_mapping = {
#         'c_Impuesto': 'c_Impuesto',
#         'Descripción': 'descripcion',
#         'Retención': 'retencion',
#         'Traslado': 'traslado',
#         'Local o federal': 'local_o_federal',
#         'Fecha inicio de vigencia': 'fecha_inicio_vigencia',
#         'Fecha fin de vigencia': 'fecha_fin_vigencia'
#     }
#     df_impuesto = df_impuesto.rename(columns={c: impuesto_mapping[c] for c in impuesto_mapping if c in df_impuesto.columns})

#     # Normalizar valores de Retención, Traslado y Ámbito
#     for col in ['retencion', 'traslado', 'ambito']:
#         if col in df_impuesto.columns:
#             df_impuesto[col] = df_impuesto[col].astype(str).str.upper().replace({
#                 'SI': 'SI', 'SÍ': 'SI', 'NO': 'NO', 'FEDERAL': 'FEDERAL', 'LOCAL': 'LOCAL'
#             })

#     # Normalizar fechas
#     for col in ['fecha_inicio_vigencia', 'fecha_fin_vigencia']:
#         if col in df_impuesto.columns:
#             df_impuesto[col] = pd.to_datetime(df_impuesto[col], errors='coerce').dt.strftime('%Y-%m-%d')

#     # Reemplazar NaN por None
#     df_impuesto = df_impuesto.where(pd.notnull(df_impuesto), None)

#     # Crear/actualizar tabla
#     upsert_table(df_impuesto, "cfdi_impuesto")

# except Exception as e:
#     print(f"❌ Error procesando Anexo 20 (Impuesto): {e}")

# # ===== ANEXO 20: TipoFactor =====
# try:
#     xls_a20 = pd.ExcelFile("catCFDI_V_4_20250917.xls", engine="xlrd")
#     sheets_a20 = xls_a20.sheet_names

#     hoja_tipofactor = None
#     for s in sheets_a20:
#         if "tipofactor" in s.lower():
#             hoja_tipofactor = s
#             break

#     if hoja_tipofactor is None:
#         raise ValueError("No se encontró hoja de TipoFactor en el Anexo 20")

#     preview = pd.read_excel(xls_a20, sheet_name=hoja_tipofactor, nrows=10, header=None)
#     header_row = None
#     for i, row in preview.iterrows():
#         row_str = [str(cell).strip() for cell in row]
#         if any(c.lower().startswith("c_tipofactor") or "tipo" in c.lower() for c in row_str):
#             header_row = i
#             break
#     if header_row is None:
#         header_row = 0

#     print(f"Hoja '{hoja_tipofactor}': usando header en la fila {header_row + 1}")

#     df_tipofactor = pd.read_excel(xls_a20, sheet_name=hoja_tipofactor, header=header_row)
#     df_tipofactor.columns = [str(c).strip() for c in df_tipofactor.columns]
#     df_tipofactor = df_tipofactor.loc[:, ~df_tipofactor.columns.str.startswith("Unnamed")]

#     tipofactor_mapping = {
#         'c_TipoFactor': 'c_TipoFactor',
#         'Fecha inicio de vigencia': 'fecha_inicio_vigencia',
#         'Fecha fin de vigencia': 'fecha_fin_vigencia'
#     }
#     df_tipofactor = df_tipofactor.rename(columns={c: tipofactor_mapping[c] for c in tipofactor_mapping if c in df_tipofactor.columns})

#     # Normalizar fechas
#     for col in ['fecha_inicio_vigencia', 'fecha_fin_vigencia']:
#         if col in df_tipofactor.columns:
#             df_tipofactor[col] = pd.to_datetime(df_tipofactor[col], errors='coerce').dt.strftime('%Y-%m-%d')

#     # Reemplazar NaN por None
#     df_tipofactor = df_tipofactor.where(pd.notnull(df_tipofactor), None)

#     # Crear/actualizar tabla
#     upsert_table(df_tipofactor, "cfdi_tipofactor")

# except Exception as e:
#     print(f"❌ Error procesando Anexo 20 (TipoFactor): {e}")


# # ===== ANEXO 20: Tasa o Cuota FALTA MODIFICARN =====
# try:
#     xls_a20 = pd.ExcelFile("catCFDI_V_4_20250917.xls", engine="xlrd")
#     sheets_a20 = xls_a20.sheet_names

#     hoja_tasa = None
#     for s in sheets_a20:
#         if "tasa" in s.lower() or "cuota" in s.lower():
#             hoja_tasa = s
#             break

#     if hoja_tasa is None:
#         raise ValueError("No se encontró hoja de Tasa o Cuota en el Anexo 20")

#     preview = pd.read_excel(xls_a20, sheet_name=hoja_tasa, nrows=10, header=None)
#     header_row = None
#     for i, row in preview.iterrows():
#         row_str = [str(cell).strip() for cell in row]
#         if "c_TasaOCuota" in row_str or "Rango o Fijo" in row_str:
#             header_row = i
#             break
#     if header_row is None:
#         header_row = 0

#     print(f"Hoja '{hoja_tasa}': usando header en la fila {header_row + 1}")

#     df_tasa = pd.read_excel(xls_a20, sheet_name=hoja_tasa, header=header_row)
#     df_tasa.columns = [str(c).strip() for c in df_tasa.columns]
#     df_tasa = df_tasa.loc[:, ~df_tasa.columns.str.startswith("Unnamed")]

#     tasa_mapping = {
#         'Rango o Fijo': 'rango_o_fijo',
#         'Valor mínimo': 'valor_minimo',
#         'Valor máximo': 'valor_maximo',
#         'c_TasaOCuota': 'c_TasaOCuota',
#         'Impuesto': 'impuesto',
#         'Factor': 'factor',
#         'Traslado': 'traslado',
#         'Retención': 'retencion',
#         'Fecha inicio de vigencia': 'fecha_inicio_vigencia',
#         'Fecha fin de vigencia': 'fecha_fin_vigencia'
#     }
#     df_tasa = df_tasa.rename(columns={c: tasa_mapping[c] for c in tasa_mapping if c in df_tasa.columns})

#     # Normalizar impuesto: mapear nombres a claves SAT
#     impuesto_map = {'IVA': '002', 'ISR': '001', 'IEPS': '003'}
#     if 'impuesto' in df_tasa.columns:
#         df_tasa['impuesto'] = df_tasa['impuesto'].replace(impuesto_map)

#     # Convertir Sí/No a 1/0
#     for col in ['traslado', 'retencion']:
#         if col in df_tasa.columns:
#             df_tasa[col] = df_tasa[col].astype(str).str.upper().map({'SI': 1, 'NO': 0}).fillna(0)

#     # Normalizar fechas
#     for col in ['fecha_inicio_vigencia', 'fecha_fin_vigencia']:
#         if col in df_tasa.columns:
#             df_tasa[col] = pd.to_datetime(df_tasa[col], errors='coerce').dt.strftime('%Y-%m-%d')

#     # Reemplazar NaN por None
#     df_tasa = df_tasa.where(pd.notnull(df_tasa), None)

#     # Crear/actualizar tabla
#     upsert_table(df_tasa, "cfdi_tasaocuota")

# except Exception as e:
#     print(f"❌ Error procesando Anexo 20 (Tasa o Cuota): {e}")



# # ===== ANEXO 20: Aduana =====
# try:
#     xls_a20 = pd.ExcelFile("catCFDI_V_4_20250917.xls", engine="xlrd")
#     sheets_a20 = xls_a20.sheet_names

#     hoja_aduana = None
#     for s in sheets_a20:
#         if "aduana" in s.lower():
#             hoja_aduana = s
#             break

#     if hoja_aduana is None:
#         raise ValueError("No se encontró hoja de Aduana en el Anexo 20")

#     preview = pd.read_excel(xls_a20, sheet_name=hoja_aduana, nrows=10, header=None)
#     header_row = None
#     for i, row in preview.iterrows():
#         row_str = [str(cell).strip() for cell in row]
#         if "c_Aduana" in row_str:
#             header_row = i
#             break
#     if header_row is None:
#         header_row = 0

#     print(f"Hoja '{hoja_aduana}': usando header en la fila {header_row + 1}")

#     df_aduana = pd.read_excel(xls_a20, sheet_name=hoja_aduana, header=header_row)
#     df_aduana.columns = [str(c).strip() for c in df_aduana.columns]
#     df_aduana = df_aduana.loc[:, ~df_aduana.columns.str.startswith("Unnamed")]

#     aduana_mapping = {
#         'c_Aduana': 'c_Aduana',
#         'Descripción': 'descripcion',
#         'Fecha inicio de vigencia': 'fecha_inicio_vigencia',
#         'Fecha fin de vigencia': 'fecha_fin_vigencia'
#     }
#     df_aduana = df_aduana.rename(columns={c: aduana_mapping[c] for c in aduana_mapping if c in df_aduana.columns})

#     # Normalizar fechas
#     for col in ['fecha_inicio_vigencia', 'fecha_fin_vigencia']:
#         if col in df_aduana.columns:
#             df_aduana[col] = pd.to_datetime(df_aduana[col], errors='coerce').dt.strftime('%Y-%m-%d')

#     # Reemplazar NaN por None
#     df_aduana = df_aduana.where(pd.notnull(df_aduana), None)

#     # Crear/actualizar tabla
#     upsert_table(df_aduana, "cfdi_aduana")

# except Exception as e:
#     print(f"❌ Error procesando Anexo 20 (Aduana): {e}")


# # ===== ANEXO 20: NumPedimentoAduana =====
# try:
#     xls_a20 = pd.ExcelFile("catCFDI_V_4_20250917.xls", engine="xlrd")
#     sheets_a20 = xls_a20.sheet_names

#     hoja_numped = None
#     for s in sheets_a20:
#         if "pedimento" in s.lower():
#             hoja_numped = s
#             break

#     if hoja_numped is None:
#         raise ValueError("No se encontró hoja de NumPedimentoAduana en el Anexo 20")

#     preview = pd.read_excel(xls_a20, sheet_name=hoja_numped, nrows=10, header=None)
#     header_row = None
#     for i, row in preview.iterrows():
#         row_str = [str(cell).strip() for cell in row]
#         if "c_Aduana" in row_str:
#             header_row = i
#             break
#     if header_row is None:
#         header_row = 0

#     print(f"Hoja '{hoja_numped}': usando header en la fila {header_row + 1}")

#     df_ped = pd.read_excel(xls_a20, sheet_name=hoja_numped, header=header_row)
#     df_ped.columns = [str(c).strip() for c in df_ped.columns]
#     df_ped = df_ped.loc[:, ~df_ped.columns.str.startswith("Unnamed")]

#     ped_mapping = {
#         'c_Aduana': 'c_Aduana',
#         'Patente': 'patente',
#         'Ejercicio': 'ejercicio',
#         'Cantidad': 'numero',
#         'Fecha inicio de vigencia': 'fecha_inicio_vigencia',
#         'Fecha fin de vigencia': 'fecha_fin_vigencia'
#     }
#     df_ped = df_ped.rename(columns={c: ped_mapping[c] for c in ped_mapping if c in df_ped.columns})

#     # Normalizar fechas
#     for col in ['fecha_inicio_vigencia', 'fecha_fin_vigencia']:
#         if col in df_ped.columns:
#             df_ped[col] = pd.to_datetime(df_ped[col], errors='coerce').dt.strftime('%Y-%m-%d')

#     # Reemplazar NaN por None
#     df_ped = df_ped.where(pd.notnull(df_ped), None)

#     # === Resolver llaves foráneas (aduana_id y patente_id) ===
#     with engine.begin() as conn:
#         # Mapeo aduana
#         aduanas = pd.read_sql("SELECT id, c_Aduana FROM cfdi_aduana", conn)
#         patentes = pd.read_sql("SELECT id, codigo AS patente FROM cfdi_patente", conn)

#     df_ped = df_ped.merge(aduanas, on="c_Aduana", how="left").rename(columns={"id": "aduana_id"})
#     df_ped = df_ped.merge(patentes, on="patente", how="left").rename(columns={"id": "patente_id"})

#     # Seleccionar solo columnas para la BD
#     df_ped = df_ped[["ejercicio", "numero", "aduana_id", "patente_id", "fecha_inicio_vigencia", "fecha_fin_vigencia"]]

#     # Crear/actualizar tabla
#     upsert_table(df_ped, "cfdi_pedimentocfdi")

# except Exception as e:
#     print(f"❌ Error procesando Anexo 20 (NumPedimentoAduana): {e}")




# # ===== ANEXO 20: Patente Aduanal =====
# try:
#     xls_a20 = pd.ExcelFile("catCFDI_V_4_20250917.xls", engine="xlrd")
#     sheets_a20 = xls_a20.sheet_names

#     hoja_patente = None
#     for s in sheets_a20:
#         if "patente" in s.lower():
#             hoja_patente = s
#             break

#     if hoja_patente is None:
#         raise ValueError("No se encontró hoja de Patente Aduanal en el Anexo 20")

#     preview = pd.read_excel(xls_a20, sheet_name=hoja_patente, nrows=10, header=None)
#     header_row = None
#     for i, row in preview.iterrows():
#         row_str = [str(cell).strip() for cell in row]
#         if "c_PatenteAduanal" in row_str or "C_PatenteAduanal" in row_str:
#             header_row = i
#             break
#     if header_row is None:
#         header_row = 0

#     print(f"Hoja '{hoja_patente}': usando header en la fila {header_row + 1}")

#     df_patente = pd.read_excel(xls_a20, sheet_name=hoja_patente, header=header_row)
#     df_patente.columns = [str(c).strip() for c in df_patente.columns]
#     df_patente = df_patente.loc[:, ~df_patente.columns.str.startswith("Unnamed")]

#     patente_mapping = {
#         'c_PatenteAduanal': 'c_PatenteAduanal',
#         'C_PatenteAduanal': 'c_PatenteAduanal',  # por si viene en mayúscula
#         'Inicio de vigencia de la patente': 'inicio_vigencia',
#         'Fin de vigencia de la patente': 'fin_vigencia'
#     }
#     df_patente = df_patente.rename(columns={c: patente_mapping[c] for c in patente_mapping if c in df_patente.columns})

#     # Normalizar fechas
#     for col in ['inicio_vigencia', 'fin_vigencia']:
#         if col in df_patente.columns:
#             df_patente[col] = pd.to_datetime(df_patente[col], errors='coerce').dt.strftime('%Y-%m-%d')

#     # Reemplazar NaN por None
#     df_patente = df_patente.where(pd.notnull(df_patente), None)

#     # Crear/actualizar tabla
#     upsert_table(df_patente, "cfdi_patente")

# except Exception as e:
#     print(f"❌ Error procesando Anexo 20 (Patente Aduanal): {e}")



# # ===== ANEXO 20: Colonia =====
# try:
#     xls_a20 = pd.ExcelFile("catCFDI_V_4_20250917.xls", engine="xlrd")
#     sheets_a20 = xls_a20.sheet_names

#     hoja_colonia = None
#     for s in sheets_a20:
#         if "colonia" in s.lower():
#             hoja_colonia = s
#             break

#     if hoja_colonia is None:
#         raise ValueError("No se encontró hoja de Colonia en el Anexo 20")

#     preview = pd.read_excel(xls_a20, sheet_name=hoja_colonia, nrows=10, header=None)
#     header_row = None
#     for i, row in preview.iterrows():
#         row_str = [str(cell).strip() for cell in row]
#         if "c_Colonia" in row_str and "c_CodigoPostal" in row_str:
#             header_row = i
#             break
#     if header_row is None:
#         header_row = 0

#     print(f"Hoja '{hoja_colonia}': usando header en la fila {header_row + 1}")

#     df_colonia = pd.read_excel(xls_a20, sheet_name=hoja_colonia, header=header_row)
#     df_colonia.columns = [str(c).strip() for c in df_colonia.columns]
#     df_colonia = df_colonia.loc[:, ~df_colonia.columns.str.startswith("Unnamed")]

#     colonia_mapping = {
#         'c_Colonia': 'c_Colonia',
#         'c_CodigoPostal': 'c_CodigoPostal_id',
#         'Nombre del asentamiento': 'nombre_asentamiento'
#     }
#     df_colonia = df_colonia.rename(columns={c: colonia_mapping[c] for c in colonia_mapping if c in df_colonia.columns})

#     # Convertir a enteros los códigos si aplica
#     df_colonia['c_Colonia'] = df_colonia['c_Colonia'].astype(str).str.zfill(4)
#     df_colonia['c_CodigoPostal_id'] = df_colonia['c_CodigoPostal_id'].astype(str).str.zfill(5)

#     # Reemplazar NaN por None
#     df_colonia = df_colonia.where(pd.notnull(df_colonia), None)

#     # Crear/actualizar tabla
#     upsert_table(df_colonia, "cfdi_colonia")

# except Exception as e:
#     print(f"❌ Error procesando Anexo 20 (Colonia): {e}")


# # ===== ANEXO 20: Estado =====
# try:
#     xls_a20 = pd.ExcelFile("catCFDI_V_4_20250917.xls", engine="xlrd")
#     sheets_a20 = xls_a20.sheet_names

#     hoja_estado = None
#     for s in sheets_a20:
#         if "estado" in s.lower():
#             hoja_estado = s
#             break

#     if hoja_estado is None:
#         raise ValueError("No se encontró hoja de Estado en el Anexo 20")

#     # Detectar fila header
#     preview = pd.read_excel(xls_a20, sheet_name=hoja_estado, nrows=10, header=None)
#     header_row = None
#     for i, row in preview.iterrows():
#         row_str = [str(cell).strip() for cell in row]
#         if "c_Estado" in row_str and "c_Pais" in row_str:
#             header_row = i
#             break
#     if header_row is None:
#         header_row = 0

#     print(f"Hoja '{hoja_estado}': usando header en la fila {header_row + 1}")

#     df_estado = pd.read_excel(xls_a20, sheet_name=hoja_estado, header=header_row)
#     df_estado.columns = [str(c).strip() for c in df_estado.columns]
#     df_estado = df_estado.loc[:, ~df_estado.columns.str.startswith("Unnamed")]

#     estado_mapping = {
#         'c_Estado': 'c_Estado',
#         'c_Pais': 'c_Pais_id',
#         'Nombre del estado': 'nombre',
#         'Fecha inicio de vigencia': 'fecha_inicio_vigencia',
#         'Fecha fin de vigencia': 'fecha_fin_vigencia'
#     }
#     df_estado = df_estado.rename(columns={c: estado_mapping[c] for c in estado_mapping if c in df_estado.columns})

#     # Normalizar códigos
#     df_estado['c_Estado'] = df_estado['c_Estado'].astype(str).str.strip()
#     df_estado['c_Pais_id'] = df_estado['c_Pais_id'].astype(str).str.strip()

#     # Reemplazar NaN por None
#     df_estado = df_estado.where(pd.notnull(df_estado), None)

#     # Crear/actualizar tabla
#     upsert_table(df_estado, "cfdi_estado")

# except Exception as e:
#     print(f"❌ Error procesando Anexo 20 (Estado): {e}")


# # ===== ANEXO 20: Localidad =====
# try:
#     xls_a20 = pd.ExcelFile("catCFDI_V_4_20250917.xls", engine="xlrd")
#     sheets_a20 = xls_a20.sheet_names

#     hoja_localidad = None
#     for s in sheets_a20:
#         if "localidad" in s.lower():
#             hoja_localidad = s
#             break

#     if hoja_localidad is None:
#         raise ValueError("No se encontró hoja de Localidad en el Anexo 20")

#     # Detectar fila header
#     preview = pd.read_excel(xls_a20, sheet_name=hoja_localidad, nrows=10, header=None)
#     header_row = None
#     for i, row in preview.iterrows():
#         row_str = [str(cell).strip() for cell in row]
#         if "c_Localidad" in row_str and "c_Estado" in row_str:
#             header_row = i
#             break
#     if header_row is None:
#         header_row = 0

#     print(f"Hoja '{hoja_localidad}': usando header en la fila {header_row + 1}")

#     df_localidad = pd.read_excel(xls_a20, sheet_name=hoja_localidad, header=header_row)
#     df_localidad.columns = [str(c).strip() for c in df_localidad.columns]
#     df_localidad = df_localidad.loc[:, ~df_localidad.columns.str.startswith("Unnamed")]

#     localidad_mapping = {
#         'c_Localidad': 'c_Localidad',
#         'c_Estado': 'c_Estado_id',
#         'Descripción': 'descripcion',
#         'Fecha de inicio de vigencia': 'fecha_inicio_vigencia',
#         'Fecha de fin de vigencia': 'fecha_fin_vigencia'
#     }
#     df_localidad = df_localidad.rename(columns={c: localidad_mapping[c] for c in localidad_mapping if c in df_localidad.columns})

#     # Normalizar códigos
#     df_localidad['c_Localidad'] = df_localidad['c_Localidad'].astype(str).str.strip()
#     df_localidad['c_Estado_id'] = df_localidad['c_Estado_id'].astype(str).str.strip()

#     # Reemplazar NaN por None
#     df_localidad = df_localidad.where(pd.notnull(df_localidad), None)

#     # Crear/actualizar tabla
#     upsert_table(df_localidad, "cfdi_localidad")

# except Exception as e:
#     print(f"❌ Error procesando Anexo 20 (Localidad): {e}")


# # ===== ANEXO 20: Municipio =====
# try:
#     xls_a20 = pd.ExcelFile("catCFDI_V_4_20250917.xls", engine="xlrd")
#     sheets_a20 = xls_a20.sheet_names

#     hoja_municipio = None
#     for s in sheets_a20:
#         if "municipio" in s.lower():
#             hoja_municipio = s
#             break

#     if hoja_municipio is None:
#         raise ValueError("No se encontró hoja de Municipio en el Anexo 20")

#     # Detectar fila header
#     preview = pd.read_excel(xls_a20, sheet_name=hoja_municipio, nrows=10, header=None)
#     header_row = None
#     for i, row in preview.iterrows():
#         row_str = [str(cell).strip() for cell in row]
#         if "c_Municipio" in row_str and "c_Estado" in row_str:
#             header_row = i
#             break
#     if header_row is None:
#         header_row = 0

#     print(f"Hoja '{hoja_municipio}': usando header en la fila {header_row + 1}")

#     df_municipio = pd.read_excel(xls_a20, sheet_name=hoja_municipio, header=header_row)
#     df_municipio.columns = [str(c).strip() for c in df_municipio.columns]
#     df_municipio = df_municipio.loc[:, ~df_municipio.columns.str.startswith("Unnamed")]

#     municipio_mapping = {
#         'c_Municipio': 'c_Municipio',
#         'c_Estado': 'c_Estado_id',
#         'Descripción': 'descripcion',
#         'Fecha de inicio de vigencia': 'fecha_inicio_vigencia',
#         'Fecha de fin de vigencia': 'fecha_fin_vigencia'
#     }
#     df_municipio = df_municipio.rename(columns={c: municipio_mapping[c] for c in municipio_mapping if c in df_municipio.columns})

#     # Normalizar
#     df_municipio['c_Municipio'] = df_municipio['c_Municipio'].astype(str).str.strip()
#     df_municipio['c_Estado_id'] = df_municipio['c_Estado_id'].astype(str).str.strip()

#     # Reemplazar NaN por None
#     df_municipio = df_municipio.where(pd.notnull(df_municipio), None)

#     # Crear/actualizar tabla
#     upsert_table(df_municipio, "cfdi_municipio")

# except Exception as e:
#     print(f"❌ Error procesando Anexo 20 (Municipio): {e}")

# actualizacion_catalogos_cfdi.py
# actualizacion_catalogos_cfdi.py
# actualizacion_catalogos_cfdi.py

#========================== anexos 20 ==========================ANEXO

import os
import re
import sys
import json
import time
import glob
import traceback
import requests
import pandas as pd
from typing import Dict, Callable, List, Optional

from sqlalchemy import create_engine, text, MetaData, Table
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import ProgrammingError, OperationalError, SQLAlchemyError

# =========================
# CONFIGURACIÓN DB (confirmada)
# =========================
DB_CONFIG = {
    "ENGINE": "django.db.backends.postgresql_psycopg2",
    "NAME": config('DB_NAME_SCRIPT'),
    "USER": config('DB_USER'),
    "PASSWORD": config('DB_PASSWORD'),
    "HOST": config('DB_HOST'),
    "PORT": config('DB_PORT'),
}
CONN_STR = (
    f"postgresql+psycopg2://{DB_CONFIG['USER']}:{DB_CONFIG['PASSWORD']}"
    f"@{DB_CONFIG['HOST']}:{DB_CONFIG['PORT']}/{DB_CONFIG['NAME']}"
)
engine = create_engine(CONN_STR)

# =========================================
# DESCARGA DEL XLS MÁS RECIENTE DEL SAT
# =========================================
SAT_BASE = "http://omawww.sat.gob.mx/tramitesyservicios/Paginas/documentos/"
FALLBACK_FILE = "catCFDI_V_4_20250917.xls"  # fallback sólido
LOCAL_FILE = None

def find_latest_catcfdi_url() -> str:
    """
    Busca en la página de 'documentos' los links catCFDI_V_4_*.xls y elige el más nuevo por fecha en el filename.
    Si falla, regresa el fallback fijo.
    """
    index_url = SAT_BASE
    pat = re.compile(r'href="([^"]*catCFDI_V_4_(\d{8})\.xls)"', re.IGNORECASE)
    try:
        r = requests.get(index_url, timeout=30)
        r.raise_for_status()
        candidates = []
        for m in pat.finditer(r.text):
            href, ymd = m.group(1), m.group(2)
            # Normaliza URL relativa/absoluta
            url = href if href.lower().startswith("http") else SAT_BASE + href.split("/")[-1]
            candidates.append((ymd, url))
        if not candidates:
            # si no encontró en el índice, intenta algunas versiones recientes por patrón (heurística)
            raise RuntimeError("No se localizaron vínculos catCFDI_V_4_*.xls; se usará fallback.")
        # ordenar por fecha desc
        candidates.sort(key=lambda t: t[0], reverse=True)
        return candidates[0][1]
    except Exception:
        return SAT_BASE + FALLBACK_FILE

def download_latest_catcfdi() -> str:
    """
    Descarga el último archivo del SAT detectado automáticamente.
    Retorna el nombre local del archivo.
    """
    url = find_latest_catcfdi_url()
    fname = url.split("/")[-1]
    try:
        print(f"Descargando: {url}")
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        with open(fname, "wb") as f:
            f.write(r.content)
        print(f"Descargado: {fname}")
        return fname
    except Exception as e:
        # Fallback duro
        fb = FALLBACK_FILE
        try:
            url_fb = SAT_BASE + fb
            print(f"Fallo descarga del más reciente ({e}). Intentando fallback: {url_fb}")
            r = requests.get(url_fb, timeout=60)
            r.raise_for_status()
            with open(fb, "wb") as f:
                f.write(r.content)
            print(f"Descargado fallback: {fb}")
            return fb
        except Exception as e2:
            print(f"❌ Error descargando fallback: {e2}")
            raise

# =========================================
# HELPERS GENERALES
# =========================================
def detect_header_row(xls, sheet_name: str, default: int = 4) -> int:
    """
    Busca una fila que contenga alguna columna comenzando por 'c_' para usarla como header.
    Si no encuentra, devuelve 'default'.
    """
    preview = pd.read_excel(xls, sheet_name=sheet_name, nrows=12, header=None)
    header_row = None
    for i, row in preview.iterrows():
        row_str = [str(cell).strip() for cell in row]
        if any(c.strip().lower().startswith("c_") for c in row_str):
            header_row = i
            break
    return header_row if header_row is not None else default

def yesno_to_bit(val):
    s = str(val).strip().lower()
    if s in ("si", "sí", "yes", "y", "1", "requerido", "obligatorio"):
        return True
    if s in ("no", "n", "0", "no aplica"):
        return False
    if s in ("opcional", "condicional"):
        return False
    # cualquier otro caso o NaN -> False por seguridad
    return False


def parse_date_col(df: pd.DataFrame, cols: List[str]):
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%Y-%m-%d")

def zfill_col(df: pd.DataFrame, col: str, width: int):
    if col in df.columns:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(r"\.0$", "", regex=True)
            .str.replace(r"\.00$", "", regex=True)
            .str.strip()
            .replace({"nan": ""})
            .str.zfill(width)
        )

def normalize_upper(df: pd.DataFrame, col: str, mapping: Dict[str, str] = None):
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip().str.upper()
        if mapping:
            df[col] = df[col].replace(mapping)

# === NUEVA FUNCIÓN AQUÍ ===
def coerce_to_bool(df: pd.DataFrame, cols: List[str]):
    """
    Convierte a booleanos estrictos (True/False) las columnas indicadas.
    Acepta 1/0, 'si/no', 'true/false', 'x', numéricos o texto.
    """
    def _to_bool(x):
        if pd.isna(x):
            return False
        if isinstance(x, bool):
            return x
        s = str(x).strip().lower()
        return s in ("1", "si", "sí", "true", "x", "s", "y")
    for c in cols:
        if c in df.columns:
            df[c] = df[c].map(_to_bool)

def ensure_unique_index(conn, table_name: str, pk_col: str):
    """
    Crea UNÍQUE INDEX si no existe para la columna pk_col.
    Esto permite usar ON CONFLICT(index_elements=[pk_col]).
    """
    idx_name = f"ux_{table_name}_{pk_col}".lower()
    sql = f'CREATE UNIQUE INDEX IF NOT EXISTS "{idx_name}" ON "{table_name}"("{pk_col}");'
    conn.execute(text(sql))

def upsert_dataframe(df: pd.DataFrame, table_name: str, pk_col: str):
    """
    UPSERT general (fila por fila) usando SQLAlchemy Core + ON CONFLICT DO UPDATE.
    Requiere índice único en pk_col (se crea si no existe).
    """
    if df.empty:
        print(f"(saltado) DataFrame vacío para {table_name}")
        return

    metadata = MetaData()
    table = Table(table_name, metadata, autoload_with=engine)

    with engine.begin() as conn:
        # Garantiza índice único
        ensure_unique_index(conn, table_name, pk_col)

        cols = [c for c in df.columns if c in table.c.keys()]
        if pk_col not in cols:
            raise RuntimeError(f"Columna PK '{pk_col}' no está presente en DataFrame para {table_name}.")

        for _, row in df[cols].iterrows():
            row_data = {c: (None if pd.isna(row[c]) else row[c]) for c in cols}
            stmt = insert(table).values(**row_data)
            update_cols = {c: row_data[c] for c in cols if c != pk_col}
            stmt = stmt.on_conflict_do_update(
                index_elements=[pk_col],
                set_=update_cols
            )
            conn.execute(stmt)

    print(f"✅ UPSERT completado: {table_name} ({len(df)} filas)")

# =========================================
# CONFIGURACIÓN DE CATÁLOGOS (Anexo 20)
# Cada entrada define:
#  - match: subcadena para encontrar hoja
#  - table: nombre tabla BD
#  - pk: columna PK/UNIQUE
#  - mapping: dict Excel->BD
#  - prepare(df): callable opcional para normalizar
# =========================================
Catalog = Dict[str, object]

def make_prepare(*steps: Callable[[pd.DataFrame], None]) -> Callable[[pd.DataFrame], pd.DataFrame]:
    def _prep(df: pd.DataFrame) -> pd.DataFrame:
        for st in steps:
            st(df)
        return df
    return _prep

def prep_dates(cols: List[str]) -> Callable[[pd.DataFrame], None]:
    return lambda df: parse_date_col(df, cols)

def prep_zfill(col: str, width: int) -> Callable[[pd.DataFrame], None]:
    return lambda df: zfill_col(df, col, width)

def prep_yesno(cols: List[str]) -> Callable[[pd.DataFrame], None]:
    def _f(df):
        for c in cols:
            if c in df.columns:
                df[c] = df[c].map(yesno_to_bit)
    return _f

def prep_upper(col: str, mapping: Dict[str, str] = None) -> Callable[[pd.DataFrame], None]:
    return lambda df: normalize_upper(df, col, mapping)

CATALOGS: List[Catalog] = [
    {   # Forma de Pago
        "match": "formapago",
        "table": "cfdi_formapago",
        "pk": "c_FormaPago",
        "mapping": {
            "c_FormaPago": "c_FormaPago",
            "Descripción": "descripcion",
            "Bancarizado": "bancarizado",
            "Número de operación": "num_operacion",
            "RFC del Emisor de la cuenta ordenante": "rfc_emisor_cta_ord",
            "Cuenta Ordenante": "cuenta_ordenante",
            "Patrón para cuenta ordenante": "patron_cta_ordenante",
            "RFC del Emisor Cuenta de Beneficiario": "rfc_emisor_cta_benef",
            "Cuenta de Benenficiario": "cuenta_beneficiario",
            "Cuenta de Beneficiario": "cuenta_beneficiario",
            "Patrón para cuenta Beneficiaria": "patron_cta_beneficiaria",
            "Tipo Cadena Pago": "tipo_cadena_pago",
            "Nombre del Banco emisor de la cuenta ordenante en caso de extranjero": "banco_extranjero",
            "Fecha inicio de vigencia": "fecha_inicio_vigencia",
            "Fecha fin de vigencia": "fecha_fin_vigencia",
        },
        "prepare": make_prepare(
            prep_yesno(["bancarizado"]),
            prep_zfill("c_FormaPago", 2),
            prep_dates(["fecha_inicio_vigencia", "fecha_fin_vigencia"]),
        )
    },
    {   # Moneda
        "match": "moneda",
        "table": "cfdi_moneda",
        "pk": "c_Moneda",
        "mapping": {
            "c_Moneda": "c_Moneda",
            "Descripción": "descripcion",
            "Decimales": "decimales",
            "Porcentaje variación": "porcentaje_variacion",
            "Fecha inicio de vigencia": "fecha_inicio_vigencia",
            "Fecha fin de vigencia": "fecha_fin_vigencia",
        },
        "prepare": make_prepare(
            lambda df: df.__setitem__("decimales", pd.to_numeric(df.get("decimales"), errors="coerce").fillna(0).astype("Int64")) if "Decimales" else None,
            lambda df: df.__setitem__("porcentaje_variacion", pd.to_numeric(df.get("porcentaje_variacion"), errors="coerce")) if "porcentaje_variacion" in df.columns else None,
            prep_dates(["fecha_inicio_vigencia", "fecha_fin_vigencia"]),
        )
    },
    {   # Método de Pago
        "match": "metodopago",
        "table": "cfdi_metodopago",
        "pk": "c_MetodoPago",
        "mapping": {
            "c_MetodoPago": "c_MetodoPago",
            "Descripción": "descripcion",
            "Fecha inicio de vigencia": "fecha_inicio_vigencia",
            "Fecha fin de vigencia": "fecha_fin_vigencia",
        },
        "prepare": make_prepare(
            prep_dates(["fecha_inicio_vigencia", "fecha_fin_vigencia"]),
        )
    },
    {   # Tipo de Comprobante
        "match": "tipodecomprobante",
        "table": "cfdi_tipocomprobante",
        "pk": "c_TipoDeComprobante",
        "mapping": {
            "c_TipoDeComprobante": "c_TipoDeComprobante",
            "Descripción": "descripcion",
            "Valor máximo": "valor_maximo",
            "NS": "ns",
            "NdS": "nds",
            "Fecha inicio de vigencia": "fecha_inicio_vigencia",
            "Fecha fin de vigencia": "fecha_fin_vigencia",
        },
        "prepare": make_prepare(
            prep_dates(["fecha_inicio_vigencia", "fecha_fin_vigencia"]),
        )
    },
    {   # Exportación
        "match": "exportacion",
        "table": "cfdi_exportacion",
        "pk": "c_Exportacion",
        "mapping": {
            "c_Exportacion": "c_Exportacion",
            "Descripción": "descripcion",
            "Fecha inicio de vigencia": "fecha_inicio_vigencia",
            "Fecha fin de vigencia": "fecha_fin_vigencia",
        },
        "prepare": make_prepare(
            prep_zfill("c_Exportacion", 2),
            prep_dates(["fecha_inicio_vigencia", "fecha_fin_vigencia"]),
        )
    },
    # {   # Código Postal
    #     "match": "codigopostal",
    #     "table": "cfdi_codigopostal",
    #     "pk": "c_CodigoPostal",
    #     "mapping": {
    #         "c_CodigoPostal": "c_CodigoPostal",
    #         "c_Estado": "c_Estado_id",
    #         "c_Municipio": "c_Municipio_id",
    #         "c_Localidad": "c_Localidad_id",
    #         "Estímulo Franja Fronteriza": "estimulo_franja_fronteriza",
    #         "Fecha inicio de vigencia": "fecha_inicio_vigencia",
    #         "Fecha fin de vigencia": "fecha_fin_vigencia",
    #         "Descripción del Huso Horario": "descripcion_huso_horario",
    #         "Mes_Inicio_Horario_Verano": "mes_inicio_verano",
    #         "Día_Inicio_Horario_Verano": "dia_inicio_verano",
    #         "Hora_Inicio_Horario_Verano": "hora_inicio_verano",
    #         "Diferencia_Horaria_Verano": "diferencia_verano",
    #         "Mes_Inicio_Horario_Invierno": "mes_inicio_invierno",
    #         "Día_Inicio_Horario_Invierno": "dia_inicio_invierno",
    #         "Hora_Inicio_Horario_Invierno": "hora_inicio_invierno",
    #         "Diferencia_Horaria_Invierno": "diferencia_invierno",
    #     },
    #     "prepare": make_prepare(
    #         prep_zfill("c_CodigoPostal", 5),
    #         prep_dates(["fecha_inicio_vigencia", "fecha_fin_vigencia"]),
    #     )
    # },

    {   # Código Postal
        "match": "codigopostal",
        "table": "cfdi_codigopostal",
        "pk": "c_CodigoPostal",
        "mapping": {
            "c_CodigoPostal": "c_CodigoPostal",
            "c_Estado": "c_Estado_id",
            "c_Municipio": "c_Municipio_id",
            "c_Localidad": "c_Localidad_id",
            "Estímulo Franja Fronteriza": "estimulo_franja_fronteriza",
            "Fecha inicio de vigencia": "fecha_inicio_vigencia",
            "Fecha fin de vigencia": "fecha_fin_vigencia",
            "Descripción del Huso Horario": "descripcion_huso_horario",
            "Mes_Inicio_Horario_Verano": "mes_inicio_verano",
            "Día_Inicio_Horario_Verano": "dia_inicio_verano",
            "Hora_Inicio_Horario_Verano": "hora_inicio_verano",
            "Diferencia_Horaria_Verano": "diferencia_verano",
            "Mes_Inicio_Horario_Invierno": "mes_inicio_invierno",
            "Día_Inicio_Horario_Invierno": "dia_inicio_invierno",
            "Hora_Inicio_Horario_Invierno": "hora_inicio_invierno",
            "Diferencia_Horaria_Invierno": "diferencia_invierno",
        },
        "prepare": make_prepare(
            prep_zfill("c_CodigoPostal", 5),
            prep_dates(["fecha_inicio_vigencia", "fecha_fin_vigencia"]),
            lambda df: coerce_to_bool(df, ["estimulo_franja_fronteriza"]),
            lambda df: df.where(pd.notnull(df), None),
        )
    },
    {   # Periodicidad (genérica de Anexo 20, no nómina)
        "match": "periodicidad",
        "table": "cfdi_periodicidad",
        "pk": "c_Periodicidad",
        "mapping": {
            "c_Periodicidad": "c_Periodicidad",
            "Descripción": "descripcion",
            "Fecha inicio de vigencia": "fecha_inicio_vigencia",
            "Fecha fin de vigencia": "fecha_fin_vigencia",
        },
        "prepare": make_prepare(
            prep_zfill("c_Periodicidad", 2),
            prep_dates(["fecha_inicio_vigencia", "fecha_fin_vigencia"]),
        )
    },
    {   # Meses
        "match": "meses",
        "table": "cfdi_meses",
        "pk": "c_Meses",
        "mapping": {
            "c_Meses": "c_Meses",
            "Descripción": "descripcion",
            "Fecha inicio de vigencia": "fecha_inicio_vigencia",
            "Fecha fin de vigencia": "fecha_fin_vigencia",
        },
        "prepare": make_prepare(
            prep_zfill("c_Meses", 2),
            prep_dates(["fecha_inicio_vigencia", "fecha_fin_vigencia"]),
        )
    },
    {   # TipoRelación
        "match": "tiporelacion",
        "table": "cfdi_tiporelacion",
        "pk": "c_TipoRelacion",
        "mapping": {
            "c_TipoRelacion": "c_TipoRelacion",
            "Descripción": "descripcion",
            "Fecha inicio de vigencia": "fecha_inicio_vigencia",
            "Fecha fin de vigencia": "fecha_fin_vigencia",
        },
        "prepare": make_prepare(
            prep_zfill("c_TipoRelacion", 2),
            prep_dates(["fecha_inicio_vigencia", "fecha_fin_vigencia"]),
        )
    },
    {   # Régimen Fiscal
        "match": "regimenfiscal",
        "table": "cfdi_regimenfiscal",
        "pk": "c_RegimenFiscal",
        "mapping": {
            "c_RegimenFiscal": "c_RegimenFiscal",
            "Descripción": "descripcion",
            "Física": "fisica",
            "Moral": "moral",
            "Fecha de inicio de vigencia": "fecha_inicio_vigencia",
            "Fecha de fin de vigencia": "fecha_fin_vigencia",
        },
        "prepare": make_prepare(
            prep_yesno(["fisica", "moral"]),
            prep_dates(["fecha_inicio_vigencia", "fecha_fin_vigencia"]),
        )
    },
    {   # País
        "match": "pais",
        "table": "cfdi_pais",
        "pk": "c_Pais",
        "mapping": {
            "c_Pais": "c_Pais",
            "Descripción": "descripcion",
            "Formato de código postal": "formato_codigo_postal",
            "Formato de Registro de Identidad Tributaria": "formato_rfc",
            "Validación del Registro de Identidad Tributaria": "validacion_rfc",
            "Agrupaciones": "agrupaciones",
        },
        "prepare": make_prepare(
            lambda df: df.where(pd.notnull(df), None)
        )
    },
    {   # UsoCFDI
        "match": "usocfdi",
        "table": "cfdi_usocfdi",
        "pk": "c_UsoCFDI",
        "mapping": {
            "c_UsoCFDI": "c_UsoCFDI",
            "Descripción": "descripcion",
            "Física": "aplica_fisica",
            "Moral": "aplica_moral",
            "Fecha inicio de vigencia": "fecha_inicio_vigencia",
            "Fecha fin de vigencia": "fecha_fin_vigencia",
        },
        "prepare": make_prepare(
            prep_yesno(["aplica_fisica", "aplica_moral"]),
            prep_dates(["fecha_inicio_vigencia", "fecha_fin_vigencia"]),
        )
    },
    {   # ClaveProdServ
        "match": "claveprodserv",
        "table": "cfdi_claveprodserv",
        "pk": "c_ClaveProdServ",
        "mapping": {
            "c_ClaveProdServ": "c_ClaveProdServ",
            "Descripción": "descripcion",
            "Incluir IVA trasladado": "incluir_iva_trasladado",
            "Incluir IEPS trasladado": "incluir_ieps_trasladado",
            "Complemento que debe incluir": "complemento_incluir",
            "FechaInicioVigencia": "fecha_inicio_vigencia",
            "FechaFinVigencia": "fecha_fin_vigencia",
            "Estímulo Franja Fronteriza": "estimulo_franja_fronteriza",
            "Palabras similares": "palabras_similares",
        },
        "prepare": make_prepare(
            prep_dates(["fecha_inicio_vigencia", "fecha_fin_vigencia"]),
            lambda df: df.where(pd.notnull(df), None)
        )
    },
    {   # ClaveUnidad
        "match": "claveunidad",
        "table": "cfdi_claveunidad",
        "pk": "c_ClaveUnidad",
        "mapping": {
            "c_ClaveUnidad": "c_ClaveUnidad",
            "Nombre": "nombre",
            "Descripción": "descripcion",
            "Nota": "nota",
            "FechaInicioVigencia": "fecha_inicio_vigencia",
            "FechaFinVigencia": "fecha_fin_vigencia",
            "Símbolo": "simbolo",
        },
        "prepare": make_prepare(
            prep_dates(["fecha_inicio_vigencia", "fecha_fin_vigencia"]),
            lambda df: df.where(pd.notnull(df), None)
        )
    },
    {   # ObjetoImp
        "match": "objetoimp",
        "table": "cfdi_objetoimp",
        "pk": "c_ObjetoImp",
        "mapping": {
            "c_ObjetoImp": "c_ObjetoImp",
            "Descripción": "descripcion",
            "Fecha inicio de vigencia": "fecha_inicio_vigencia",
            "Fecha fin de vigencia": "fecha_fin_vigencia",
        },
        "prepare": make_prepare(
            prep_dates(["fecha_inicio_vigencia", "fecha_fin_vigencia"]),
            lambda df: df.where(pd.notnull(df), None)
        )
    },
    {   # Impuesto
        "match": "impuesto",
        "table": "cfdi_impuesto",
        "pk": "c_Impuesto",
        "mapping": {
            "c_Impuesto": "c_Impuesto",
            "Descripción": "descripcion",
            "Retención": "retencion",
            "Traslado": "traslado",
            "Local o federal": "local_o_federal",
            "Fecha inicio de vigencia": "fecha_inicio_vigencia",
            "Fecha fin de vigencia": "fecha_fin_vigencia",
        },
        "prepare": make_prepare(
            prep_upper("retencion", {"SÍ": "SI"}),
            prep_upper("traslado", {"SÍ": "SI"}),
            prep_upper("local_o_federal"),
            prep_dates(["fecha_inicio_vigencia", "fecha_fin_vigencia"]),
            lambda df: df.where(pd.notnull(df), None)
        )
    },
    {   # TipoFactor
        "match": "tipofactor",
        "table": "cfdi_tipofactor",
        "pk": "c_TipoFactor",
        "mapping": {
            "c_TipoFactor": "c_TipoFactor",
            "Fecha inicio de vigencia": "fecha_inicio_vigencia",
            "Fecha fin de vigencia": "fecha_fin_vigencia",
        },
        "prepare": make_prepare(
            prep_dates(["fecha_inicio_vigencia", "fecha_fin_vigencia"]),
            lambda df: df.where(pd.notnull(df), None)
        )
    },
    {   # Tasa o Cuota
        "match": "tasa",  # (a veces aparece como TasaOCuota)
        "table": "cfdi_tasaocuota",
        "pk": "c_TasaOCuota",
        "mapping": {
            "Rango o Fijo": "rango_o_fijo",
            "Valor mínimo": "valor_minimo",
            "Valor máximo": "valor_maximo",
            "c_TasaOCuota": "c_TasaOCuota",
            "Impuesto": "impuesto",
            "Factor": "factor",
            "Traslado": "traslado",
            "Retención": "retencion",
            "Fecha inicio de vigencia": "fecha_inicio_vigencia",
            "Fecha fin de vigencia": "fecha_fin_vigencia",
        },
        "prepare": make_prepare(
            lambda df: df.__setitem__("impuesto", df.get("impuesto").replace({"IVA": "002", "ISR": "001", "IEPS": "003"})) if "impuesto" in df.columns else None,
            lambda df: df.__setitem__("traslado", df.get("traslado").astype(str).str.upper().map({"SI": 1, "NO": 0}).fillna(0)) if "traslado" in df.columns else None,
            lambda df: df.__setitem__("retencion", df.get("retencion").astype(str).str.upper().map({"SI": 1, "NO": 0}).fillna(0)) if "retencion" in df.columns else None,
            prep_dates(["fecha_inicio_vigencia", "fecha_fin_vigencia"]),
            lambda df: df.where(pd.notnull(df), None),
        )
    },
    {   # Aduana
        "match": "aduana",
        "table": "cfdi_aduana",
        "pk": "c_Aduana",
        "mapping": {
            "c_Aduana": "c_Aduana",
            "Descripción": "descripcion",
            "Fecha inicio de vigencia": "fecha_inicio_vigencia",
            "Fecha fin de vigencia": "fecha_fin_vigencia",
        },
        "prepare": make_prepare(
            prep_dates(["fecha_inicio_vigencia", "fecha_fin_vigencia"]),
            lambda df: df.where(pd.notnull(df), None)
        )
    },
    {   # Patente Aduanal
        "match": "patente",
        "table": "cfdi_patente",
        "pk": "c_PatenteAduanal",
        "mapping": {
            "c_PatenteAduanal": "c_PatenteAduanal",
            "C_PatenteAduanal": "c_PatenteAduanal",
            "Inicio de vigencia de la patente": "inicio_vigencia",
            "Fin de vigencia de la patente": "fin_vigencia",
        },
        "prepare": make_prepare(
            prep_dates(["inicio_vigencia", "fin_vigencia"]),
            lambda df: df.where(pd.notnull(df), None)
        )
    },
    {   # NumPedimentoAduana (requiere llaves foráneas si las manejas; aquí solo prepara tabla cruda)
        "match": "pedimento",
        "table": "cfdi_pedimentocfdi",
        "pk": "c_Aduana",  # NOTA: si tu tabla final usa id foráneos, ajusta a tu PK real (ej. (c_Aduana, patente, ejercicio, numero))
        "mapping": {
            "c_Aduana": "c_Aduana",
            "Patente": "patente",
            "Ejercicio": "ejercicio",
            "Cantidad": "numero",
            "Fecha inicio de vigencia": "fecha_inicio_vigencia",
            "Fecha fin de vigencia": "fecha_fin_vigencia",
        },
        "prepare": make_prepare(
            prep_dates(["fecha_inicio_vigencia", "fecha_fin_vigencia"]),
            lambda df: df.where(pd.notnull(df), None)
        )
    },
    {   # Colonia
        "match": "colonia",
        "table": "cfdi_colonia",
        "pk": "c_Colonia",
        "mapping": {
            "c_Colonia": "c_Colonia",
            "c_CodigoPostal": "c_CodigoPostal_id",
            "Nombre del asentamiento": "nombre_asentamiento",
        },
        "prepare": make_prepare(
            prep_zfill("c_Colonia", 4),
            prep_zfill("c_CodigoPostal_id", 5),
            lambda df: df.where(pd.notnull(df), None)
        )
    },
    {   # Estado
        "match": "estado",
        "table": "cfdi_estado",
        "pk": "c_Estado",
        "mapping": {
            "c_Estado": "c_Estado",
            "c_Pais": "c_Pais_id",
            "Nombre del estado": "nombre",
            "Fecha inicio de vigencia": "fecha_inicio_vigencia",
            "Fecha fin de vigencia": "fecha_fin_vigencia",
        },
        "prepare": make_prepare(
            lambda df: df.__setitem__("c_Estado", df.get("c_Estado").astype(str).str.strip()) if "c_Estado" in df.columns else None,
            lambda df: df.__setitem__("c_Pais_id", df.get("c_Pais_id").astype(str).str.strip()) if "c_Pais_id" in df.columns else None,
            prep_dates(["fecha_inicio_vigencia", "fecha_fin_vigencia"]),
            lambda df: df.where(pd.notnull(df), None)
        )
    },
    {   # Localidad
        "match": "localidad",
        "table": "cfdi_localidad",
        "pk": "c_Localidad",
        "mapping": {
            "c_Localidad": "c_Localidad",
            "c_Estado": "c_Estado_id",
            "Descripción": "descripcion",
            "Fecha de inicio de vigencia": "fecha_inicio_vigencia",
            "Fecha de fin de vigencia": "fecha_fin_vigencia",
        },
        "prepare": make_prepare(
            lambda df: df.__setitem__("c_Localidad", df.get("c_Localidad").astype(str).str.strip()) if "c_Localidad" in df.columns else None,
            lambda df: df.__setitem__("c_Estado_id", df.get("c_Estado_id").astype(str).str.strip()) if "c_Estado_id" in df.columns else None,
            prep_dates(["fecha_inicio_vigencia", "fecha_fin_vigencia"]),
            lambda df: df.where(pd.notnull(df), None)
        )
    },
    {   # Municipio
        "match": "municipio",
        "table": "cfdi_municipio",
        "pk": "c_Municipio",
        "mapping": {
            "c_Municipio": "c_Municipio",
            "c_Estado": "c_Estado_id",
            "Descripción": "descripcion",
            "Fecha de inicio de vigencia": "fecha_inicio_vigencia",
            "Fecha de fin de vigencia": "fecha_fin_vigencia",
        },
        "prepare": make_prepare(
            lambda df: df.__setitem__("c_Municipio", df.get("c_Municipio").astype(str).str.strip()) if "c_Municipio" in df.columns else None,
            lambda df: df.__setitem__("c_Estado_id", df.get("c_Estado_id").astype(str).str.strip()) if "c_Estado_id" in df.columns else None,
            prep_dates(["fecha_inicio_vigencia", "fecha_fin_vigencia"]),
            prep_yesno(["estimulo_franja_fronteriza"]),
            lambda df: df.where(pd.notnull(df), None)
        )
    },
]

# =========================================
# PROCESADOR GENÉRICO DE CATÁLOGOS
# =========================================
def read_sheet(xls, sheets: List[str], match: str) -> Optional[str]:
    """
    Encuentra la hoja cuyo nombre contiene 'match' (case-insensitive).
    Retorna el nombre de la hoja o None si no se encuentra.
    """
    m = match.lower()
    for s in sheets:
        if m in s.lower():
            return s
    return None

def process_catalog(xls, sheets: List[str], cfg: Catalog):
    sheet = read_sheet(xls, sheets, cfg["match"])

    if not sheet:
        print(f"⚠️  No se encontró hoja para '{cfg['match']}'. Catálogo: {cfg['table']}")
        return

    header_row = detect_header_row(xls, sheet, default=4)
    print(f"Hoja '{sheet}': usando header en la fila {header_row + 1}")

    df = pd.read_excel(xls, sheet_name=sheet, header=header_row)
    df.columns = [str(c).strip() for c in df.columns]
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]

    # mapping
    mapping: Dict[str, str] = cfg["mapping"]
    cols_in = [c for c in mapping.keys() if c in df.columns]
    if not cols_in:
        print(f"⚠️  Ninguna columna esperada está en la hoja '{sheet}'. Saltando {cfg['table']}.")
        return

    rename_dict = {c: mapping[c] for c in cols_in}
    df = df.rename(columns=rename_dict)
    df = df.dropna(subset=[cfg["pk"]], how="any")  # elimina filas sin PK


    # preparar / normalizar
    if "prepare" in cfg and callable(cfg["prepare"]):
        df = cfg["prepare"](df)

    # UPSERT
    table = cfg["table"]
    pk = cfg["pk"]
    try:
        upsert_dataframe(df, table, pk)
    except Exception as e:
        print(f"❌ Error UPSERT {table}: {e}")
        traceback.print_exc()

# =========================================
# MAIN
# =========================================
def main():
    global LOCAL_FILE
    try:
        LOCAL_FILE = download_latest_catcfdi()
        xls = pd.ExcelFile(LOCAL_FILE, engine="xlrd")
        sheets = xls.sheet_names
        print(f"Se detectaron hojas: {sheets}")

        for cfg in CATALOGS:
            process_catalog(xls, sheets, cfg)

    except Exception as e:
        print(f"❌ Error general: {e}")
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Limpieza de archivos temporales
        try:
            if LOCAL_FILE and os.path.exists(LOCAL_FILE):
                os.remove(LOCAL_FILE)
                print(f"Archivo XLS eliminado: {LOCAL_FILE}")
        except Exception:
            pass
    print("✅ ¡Actualización de catálogos Anexo 20 completada sin violar claves foráneas!")

if __name__ == "__main__":
    main()







# """Herramienta para actualizar los catálogos CFDI directamente desde SAT.

# El script descarga el archivo XLS publicado por el SAT, interpreta cada hoja y
# actualiza las tablas de catálogo dentro de la base de datos PostgreSQL definida
# en ``db_config``.  El proceso es el siguiente:

# 1. Descarga (o reutiliza) el archivo ``.xls`` de catálogos CFDI.
# 2. Lee cada hoja del archivo, detectando de forma automática la fila que
#    contiene los encabezados (la primera fila donde aparece una columna que
#    inicia con ``c_``).
# 3. Normaliza los nombres de columnas y los alinea con los nombres existentes en
#    la base de datos (utilizando metadatos obtenidos vía SQLAlchemy).
# 4. Limpia las tablas objetivo mediante ``DELETE`` y posteriormente inserta los
#    registros actualizados usando ``pandas.DataFrame.to_sql``.

# Se intenta ser lo más genérico posible para evitar depender de cambios en los
# nombres de columnas del archivo publicado por el SAT.  Si se detecta una hoja o
# columna que no puede mapearse automáticamente, el script lo indicará en consola
# sin detener la ejecución.

# Requisitos:
#     * pandas
#     * xlrd (>=1.2) para poder abrir archivos ``.xls``
#     * SQLAlchemy
#     * psycopg2-binary

# Instalación de dependencias de ejemplo::

#     pip install pandas "xlrd>=1.2" SQLAlchemy psycopg2-binary

# Uso básico::

#     python actualizacion_catalogos_cfdi.py \
#         --url "http://omawww.sat.gob.mx/.../catCFDI_V_4_20251002.xls"

# También es posible omitir la descarga si ya se cuenta con el archivo::

#     python actualizacion_catalogos_cfdi.py --skip-download --workbook local.xls

El script se puede ejecutar en modo ``--dry-run`` para validar el procesamiento
sin modificar la base de datos.
"""


import argparse
import logging
import os
import pathlib
import re
import sys
import unicodedata
from dataclasses import dataclass
from typing import Dict, Iterator, List, Optional, Sequence

import pandas as pd
import requests
from psycopg2 import errorcodes
from sqlalchemy.sql import sqltypes

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Integer,
    MetaData,
    Numeric,
    Table,
    Time,
    create_engine,
    inspect,
    text,
)
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.engine import Engine
from sqlalchemy.exc import DBAPIError


# ---------------------------------------------------------------------------
# Configuración de conexión a la base de datos (editar según sea necesario)
# ---------------------------------------------------------------------------
BASE_DIR = pathlib.Path(__file__).resolve().parent
DB_CONFIG = {
    "ENGINE": "postgresql",
    "NAME": "scriptmigracion",
    "USER": "factupiddev",
    "PASSWORD": "raspbian",
    "HOST": "192.168.54.61",
    "PORT": "5432",
}


# # ---------------------------------------------------------------------------
# # Configuración general del script
# # ---------------------------------------------------------------------------
# DEFAULT_URL = "http://omawww.sat.gob.mx/tramitesyservicios/Paginas/documentos/catCFDI_V_4_20251002.xls"
# DEFAULT_FILENAME = "catCFDI_V_4_20251002.xls"

# # Algunas hojas del Excel contienen partes del mismo catálogo (por ejemplo,el
# # catálogo de códigos postales viene dividido en dos partes).  En esos casos se
# # consolidan todas las hojas que apunten a la misma tabla.
# # Lista explícita de tablas conocidas en la base de datos para validar mapeos
# KNOWN_TABLES = {
#     "cfdi_versioncfdi",
#     "cfdi_usocfdi_regimen_fiscal_receptor",
#     "cfdi_formapago",
#     "cfdi_aduana",
#     "cfdi_claveprodserv",
#     "cfdi_claveunidad",
#     "cfdi_codigopostal",
#     "cfdi_colonia",
#     "cfdi_estado",
#     "cfdi_exportacion",
#     "cfdi_impuesto",
#     "cfdi_localidad",
#     "cfdi_meses",
#     "cfdi_metodopago",
#     "cfdi_moneda",
#     "cfdi_municipio",
#     "cfdi_numpedimentoaduana",
#     "cfdi_objetoimp",
#     "cfdi_pais",
#     "cfdi_patenteaduanal",
#     "cfdi_periodicidad",
#     "cfdi_regimenfiscal",
#     "cfdi_tasaocuota",
#     "cfdi_tipofactor",
#     "cfdi_tiporelacion",
#     "cfdi_usocfdi",
#     "cfdi_informacionfiscal_regimen_fiscal",
#     "cfdi_informacionfiscal",
#     "cfdi_receptor",
#     "cfdi_receptor_regimen_fiscal",
#     "cfdi_facturaelectronicaborrador",
#     "cfdi_certificadosellodigital",
#     "cfdi_comprobanteemitido",
#     "cfdi_comprobantesrelacionados",
#     "cfdi_emisor",
#     "cfdi_informacionglobal",
#     "cfdi_informacionpago",
#     "cfdi_leyendasfiscales",
#     "cfdi_tipocomprobante",
#     "cfdi_facturaelectronica",
#     "cfdi_archivo",
#     "cfdi_concepto",
# }

# SHEET_TABLE_MAP: Dict[str, str] = {
#     "versiones": "cfdi_versioncfdi",
#     "version_cfdi": "cfdi_versioncfdi",
#     "c_formapago": "cfdi_formapago",
#     "c_metodopago": "cfdi_metodopago",
#     "c_moneda": "cfdi_moneda",
#     "c_tipodecomprobante": "cfdi_tipocomprobante",
#     "c_tipocomprobante": "cfdi_tipocomprobante",
#     "c_exportacion": "cfdi_exportacion",
#     "c_periodicidad": "cfdi_periodicidad",
#     "c_meses": "cfdi_meses",
#     "c_tiporelacion": "cfdi_tiporelacion",
#     "c_usocfdi": "cfdi_usocfdi",
#     "c_usocfdi_regimenfiscalreceptor": "cfdi_usocfdi_regimen_fiscal_receptor",
#     "usocfdi_regimenfiscal": "cfdi_usocfdi_regimen_fiscal_receptor",
#     "c_aduana": "cfdi_aduana",
#     "c_claveprodserv": "cfdi_claveprodserv",
#     "c_claveunidad": "cfdi_claveunidad",
#     "c_codigopostal": "cfdi_codigopostal",
#     "c_codigopostal_parte_1": "cfdi_codigopostal",
#     "c_codigopostal_parte_2": "cfdi_codigopostal",
#     "c_colonia": "cfdi_colonia",
#     "c_estado": "cfdi_estado",
#     "c_exportacion_": "cfdi_exportacion",
#     "c_impuesto": "cfdi_impuesto",
#     "c_localidad": "cfdi_localidad",
#     "c_municipio": "cfdi_municipio",
#     "c_numpedimentoaduana": "cfdi_numpedimentoaduana",
#     "c_objetoimp": "cfdi_objetoimp",
#     "c_pais": "cfdi_pais",
#     "c_patenteaduanal": "cfdi_patenteaduanal",
#     "c_regimenfiscal": "cfdi_regimenfiscal",
#     "c_tasaocuota": "cfdi_tasaocuota",
#     "c_tipofactor": "cfdi_tipofactor",
# }

STOPWORDS = {"de", "del", "la", "el", "los", "las", "para", "por", "con", "en"}
BOOLEAN_TRUE = {"1", "s", "si", "sí", "true", "verdadero", "x"}
BOOLEAN_FALSE = {"0", "n", "no", "false", "falso"}


# @dataclass
# class SheetPayload:
#     """Representa el contenido procesado de una hoja del Excel."""

#     sheet_name: str
#     normalized_name: str
#     dataframe: pd.DataFrame


# def configure_logging(verbose: bool) -> None:
#     level = logging.DEBUG if verbose else logging.INFO
#     logging.basicConfig(
#         level=level,
#         format="%(asctime)s [%(levelname)s] %(message)s",
#         datefmt="%Y-%m-%d %H:%M:%S",
#     )


# def normalize_text(value: str) -> str:
#     """Normaliza texto removiendo acentos y caracteres especiales."""

#     value = unicodedata.normalize("NFKD", value)
#     value = "".join(ch for ch in value if not unicodedata.combining(ch))
#     value = value.lower()
#     value = value.replace("%", "_porcentaje")
#     value = re.sub(r"[^0-9a-zA-Z_]+", "_", value)
#     value = re.sub(r"_+", "_", value)
#     return value.strip("_")


# def canonical_key(value: str) -> str:
#     """Genera una clave sin stopwords ni separadores para facilitar comparaciones."""

#     tokens = [token for token in re.split(r"[_\s]+", normalize_text(value)) if token]
#     filtered = [token for token in tokens if token not in STOPWORDS]
#     return "".join(filtered)


# def download_workbook(url: str, destination: str, overwrite: bool = True) -> str:
#     """Descarga el archivo Excel que contiene los catálogos CFDI."""

#     if not overwrite and os.path.exists(destination):
#         logging.info("Se reutiliza el archivo existente: %s", destination)
#         return destination

#     logging.info("Descargando catálogo CFDI desde %s", url)
#     response = requests.get(url, timeout=120)
#     response.raise_for_status()

#     with open(destination, "wb") as handler:
#         handler.write(response.content)

#     logging.info("Archivo guardado en %s", destination)
#     return destination


# def detect_header_row(sample: pd.DataFrame) -> int:
#     """Detecta la fila que contiene el encabezado buscando c_ en alguna celda."""

    for idx, (_, row) in enumerate(sample.iterrows()):
        for cell in row:
            if isinstance(cell, str) and cell.strip().lower().startswith("c_"):
                return idx
    return 4


def read_sheet(xls: pd.ExcelFile, sheet: str) -> SheetPayload:
    logging.debug("Leyendo hoja '%s'", sheet)
    preview = pd.read_excel(xls, sheet_name=sheet, nrows=15, header=None, dtype=str)
    header_row = detect_header_row(preview)

#     df = pd.read_excel(xls, sheet_name=sheet, header=header_row, dtype=object)
#     df.columns = [str(col).strip() for col in df.columns]
#     unnamed_mask = df.columns.map(str).str.startswith("Unnamed")
#     if unnamed_mask.any():
#         df = df.loc[:, ~unnamed_mask]
#     df = df.dropna(how="all")

#     normalized_sheet = normalize_text(sheet)
#     logging.debug(
#         "Hoja '%s' normalizada como '%s' con %d columnas y %d filas",
#         sheet,
#         normalized_sheet,
#         len(df.columns),
#         len(df),
#     )

#     return SheetPayload(sheet_name=sheet, normalized_name=normalized_sheet, dataframe=df)


def resolve_table_name(sheet_name: str) -> Optional[str]:
    normalized = normalize_text(sheet_name)

#     candidates = [normalized]

#     without_parte = re.sub(r"_parte_\d+$", "", normalized)
#     if without_parte not in candidates:
#         candidates.append(without_parte)

#     without_numeric_suffix = re.sub(r"_\d+$", "", normalized)
#     if without_numeric_suffix not in candidates:
#         candidates.append(without_numeric_suffix)

#     for candidate in candidates:
#         if candidate in SHEET_TABLE_MAP:
#             return SHEET_TABLE_MAP[candidate]

#     if "usocfdi" in normalized and "regimen" in normalized:
#         return "cfdi_usocfdi_regimen_fiscal_receptor"

#     for candidate in candidates:
#         if candidate.startswith("c_"):
#             base = candidate[2:]
#             base = re.sub(r"_parte_\d+$", "", base)
#             base = re.sub(r"_\d+$", "", base)
#             target = f"cfdi_{base}"
#             if target in KNOWN_TABLES:
#                 return target

#     return None


def consolidate_tables(sheets: Sequence[SheetPayload]) -> Dict[str, pd.DataFrame]:
    grouped: Dict[str, List[pd.DataFrame]] = {}
    for payload in sheets:
        table = resolve_table_name(payload.normalized_name)
        if not table:
            logging.warning("No se encontró tabla destino para la hoja '%s'", payload.sheet_name)
            continue
        grouped.setdefault(table, []).append(payload.dataframe)

#     combined: Dict[str, pd.DataFrame] = {}
#     for table, frames in grouped.items():
#         combined[table] = pd.concat(frames, ignore_index=True)
#         logging.info("Tabla destino '%s' recibirá %d filas", table, len(combined[table]))

#     return combined


def normalize_dataframe_columns(df: pd.DataFrame, db_columns: Sequence[str]) -> pd.DataFrame:
    db_canonical_map: Dict[str, str] = {}
    for column in db_columns:
        canonical = canonical_key(column)
        db_canonical_map.setdefault(canonical, column)

    for column in db_columns:
        if column.lower().endswith("_id"):
            alias = canonical_key(column[:-3])
            db_canonical_map.setdefault(alias, column)

#     renamed_columns: Dict[str, str] = {}
#     for column in df.columns:
#         canonical = canonical_key(str(column))
#         target = db_canonical_map.get(canonical)
#         if target:
#             renamed_columns[column] = target
#         else:
#             logging.debug("Columna '%s' no tiene mapeo automático", column)

#     df = df.rename(columns=renamed_columns)

    intersection = [col for col in df.columns if col in db_columns]
    dropped = set(df.columns) - set(intersection)
    if dropped:
        logging.debug("Columnas descartadas por no existir en BD: %s", ", ".join(sorted(dropped)))
    df = df[intersection]

    for column in db_columns:
        if column not in df.columns:
            df[column] = None

    df = df[db_columns]
    return df


# def parse_boolean(value: object) -> Optional[bool]:
#     if value is None:
#         return None
#     if isinstance(value, bool):
#         return value

#     text = str(value).strip().lower()
#     if not text:
#         return None
#     if text in BOOLEAN_TRUE:
#         return True
#     if text in BOOLEAN_FALSE:
#         return False
#     return None


def convert_dataframe_types(df: pd.DataFrame, columns_info: Sequence[Dict[str, object]]) -> pd.DataFrame:
    for column in columns_info:
        name = column["name"]
        if name not in df.columns:
            continue
        col_type = column["type"]

#         try:
#             if isinstance(col_type, Boolean):
#                 df[name] = df[name].apply(parse_boolean)
#                 if not column.get("nullable", True):
#                     missing_mask = df[name].isna()
#                     if missing_mask.any():
#                         logging.debug(
#                             "Columna booleana '%s' sin datos. Se reemplazan %d valores vacíos por False",
#                             name,
#                             int(missing_mask.sum()),
#                         )
#                         df.loc[missing_mask, name] = False
#                     df[name] = df[name].astype(bool)
#             elif isinstance(col_type, Date):
#                 date_series = pd.to_datetime(df[name], errors="coerce").dt.date
#                 df[name] = date_series.apply(lambda value: value if pd.notnull(value) else None)
#             elif isinstance(col_type, Time):
#                 time_series = pd.to_datetime(df[name], errors="coerce").dt.time
#                 df[name] = time_series.apply(lambda value: value if pd.notnull(value) else None)
#             elif isinstance(col_type, DateTime):
#                 datetime_series = pd.to_datetime(df[name], errors="coerce")
#                 df[name] = datetime_series.apply(
#                     lambda value: value.to_pydatetime() if pd.notnull(value) else None
#                 )
#             elif isinstance(col_type, Integer):
#                 df[name] = pd.to_numeric(df[name], errors="coerce").astype("Int64")
#             elif isinstance(col_type, Numeric):
#                 df[name] = pd.to_numeric(df[name], errors="coerce")
#             elif isinstance(col_type, sqltypes.String):
#                 def _coerce_string(value: object) -> Optional[str]:
#                     if value is None:
#                         return None
#                     if isinstance(value, str):
#                         text_value = value.strip()
#                         return text_value or None
#                     if isinstance(value, float):
#                         if pd.isna(value):
#                             return None
#                         if value.is_integer():
#                             return str(int(value))
#                         return format(value, ".15g")
#                     if isinstance(value, (int,)):
#                         return str(value)
#                     return str(value).strip() or None

#                 df[name] = df[name].apply(_coerce_string)

                max_length = getattr(col_type, "length", None)
                if max_length:
                    too_long_mask = df[name].apply(lambda x: isinstance(x, str) and len(x) > max_length)
                    if too_long_mask.any():
                        truncated_count = int(too_long_mask.sum())
                        logging.warning(
                            "Se truncaron %d valores en la columna '%s' para respetar el límite de %d caracteres",
                            truncated_count,
                            name,
                            max_length,
                        )
                        df.loc[too_long_mask, name] = df.loc[too_long_mask, name].apply(
                            lambda value: value[:max_length] if isinstance(value, str) else value
                        )
            else:
                df[name] = df[name].apply(lambda x: x.strip() if isinstance(x, str) else x)
        except Exception as exc:
            logging.warning("No fue posible convertir la columna '%s': %s", name, exc)

    df = df.where(pd.notnull(df), None)
    return df


def drop_rows_with_missing_required_fields(
    df: pd.DataFrame,
    columns_info: Sequence[Dict[str, object]],
    table: str,
    primary_keys: Optional[Sequence[str]] = None,
) -> pd.DataFrame:
    pk_columns = list(primary_keys or [])

#     required_columns = [
#         column["name"]
#         for column in columns_info
#         if (not column.get("nullable", True) or column.get("primary_key"))
#     ]

    required_columns.extend(pk_columns)
    seen = set()
    deduped_required: List[str] = []
    for column in required_columns:
        if column in seen:
            continue
        seen.add(column)
        deduped_required.append(column)
    required_columns = deduped_required

#     if not required_columns:
#         return df

#     missing_required = [column for column in required_columns if column not in df.columns]
#     if missing_required:
#         logging.error(
#             "No se encontraron columnas obligatorias %s en la tabla '%s'; se omite la carga.",
#             ", ".join(missing_required),
#             table,
#         )
#         return pd.DataFrame(columns=df.columns)

#     required_columns = [column for column in required_columns if column in df.columns]

#     def has_value(value: object) -> bool:
#         if pd.isna(value) or value is None:
#             return False
#         if isinstance(value, str):
#             return bool(value.strip())
#         return True

#     mask = pd.Series(True, index=df.index)
#     for column in required_columns:
#         mask &= df[column].apply(has_value)

#     removed_rows = len(df) - int(mask.sum())
#     if removed_rows:
#         logging.warning(
#             "Se descartaron %d filas con valores obligatorios nulos en '%s' (%s)",
#             removed_rows,
#             table,
#             ", ".join(required_columns),
#         )

#     return df.loc[mask].copy()


def chunk_records(records: List[Dict[str, object]], chunk_size: int = 1000) -> Iterator[List[Dict[str, object]]]:
    for start in range(0, len(records), chunk_size):
        yield records[start : start + chunk_size]


def append_dataframe_to_table(
    engine: Engine,
    table_name: str,
    dataframe: pd.DataFrame,
    table_obj: Optional[Table] = None,
    chunk_size: int = 1000,
) -> None:
    if dataframe.empty:
        return

    if table_obj is None:
        try:
            table_obj = Table(table_name, MetaData(), autoload_with=engine)
        except Exception as exc:
            logging.warning("No fue posible reflejar la tabla '%s': %s", table_name, exc)
            return

    insert_stmt = table_obj.insert()
    records = dataframe.to_dict(orient="records")

    with engine.begin() as connection:
        for chunk in chunk_records(records, chunk_size):
            if not chunk:
                continue
            connection.execute(insert_stmt, chunk)


def upsert_dataframe(
    connection,
    table_obj: Table,
    dataframe: pd.DataFrame,
    chunk_size: int = 1000,
) -> None:
    pk_columns = [column.name for column in table_obj.primary_key.columns]
    if not pk_columns:
        logging.warning(
            "La tabla '%s' no tiene clave primaria definida; se insertarán filas sin control de duplicados.",
            table_obj.name,
        )
        insert_stmt = table_obj.insert()
        records = dataframe.to_dict(orient="records")
        for chunk in chunk_records(records, chunk_size):
            if not chunk:
                continue
            connection.execute(insert_stmt, chunk)
        return

#     insert_stmt = pg_insert(table_obj)
#     update_columns = {
#         column.name: insert_stmt.excluded[column.name]
#         for column in table_obj.columns
#         if column.name not in pk_columns
#     }

#     records = dataframe.to_dict(orient="records")
#     for chunk in chunk_records(records, chunk_size):
#         if not chunk:
#             continue
#         stmt = insert_stmt.values(chunk)
#         if update_columns:
#             stmt = stmt.on_conflict_do_update(index_elements=pk_columns, set_=update_columns)
#         else:
#             stmt = stmt.on_conflict_do_nothing(index_elements=pk_columns)
#         connection.execute(stmt)


def load_catalogs_to_database(
    engine: Engine,
    tables: Dict[str, pd.DataFrame],
    truncate_before_insert: bool = True,
    dry_run: bool = False,
) -> None:
    inspector = inspect(engine)

#     metadata = MetaData()
#     table_cache: Dict[str, Table] = {}

#     for table, dataframe in tables.items():
#         if dataframe.empty:
#             logging.info("La tabla '%s' no contiene registros para actualizar.", table)
#             continue

#         try:
#             columns_info = inspector.get_columns(table)
#         except Exception as exc:
#             logging.warning("No fue posible obtener columnas de '%s': %s", table, exc)
#             continue

#         try:
#             pk_info = inspector.get_pk_constraint(table)
#             pk_columns = (pk_info or {}).get("constrained_columns") or []
#         except Exception as exc:
#             logging.debug("No fue posible obtener la llave primaria de '%s': %s", table, exc)
#             pk_columns = []

#         db_columns = [column["name"] for column in columns_info]
#         if not db_columns:
#             logging.warning("La tabla '%s' no tiene columnas visibles; se omite.", table)
#             continue

#         df_aligned = normalize_dataframe_columns(dataframe, db_columns)
#         df_aligned = convert_dataframe_types(df_aligned, columns_info)
#         df_aligned = drop_rows_with_missing_required_fields(
#             df_aligned,
#             columns_info,
#             table,
#             primary_keys=pk_columns,
#         )

#         logging.info("Preparando la carga de %d filas en '%s'", len(df_aligned), table)

#         if dry_run:
#             logging.info("Modo dry-run activo; no se modificará la tabla '%s'", table)
#             continue

#         delete_failed = False
#         if truncate_before_insert:
#             logging.debug("Eliminando datos previos de '%s'", table)
#             try:
#                 with engine.begin() as connection:
#                     connection.execute(text(f"DELETE FROM {table}"))
#             except DBAPIError as exc:
#                 if getattr(getattr(exc, "orig", None), "pgcode", "") == errorcodes.FOREIGN_KEY_VIOLATION:
#                     logging.warning(
#                         "No se pudo eliminar el contenido de '%s' por restricciones de integridad. "
#                         "Se realizará una sincronización incremental.",
#                         table,
#                     )
#                     delete_failed = True
#                 else:
#                     raise

        table_obj = table_cache.get(table)
        if table_obj is None:
            try:
                table_obj = Table(table, metadata, autoload_with=engine)
            except Exception as exc:
                logging.warning("No fue posible reflejar la tabla '%s': %s", table, exc)
                table_obj = None
            else:
                table_cache[table] = table_obj

        if truncate_before_insert and not delete_failed:
            if table_obj is None:
                logging.warning(
                    "No se cuenta con metadatos de '%s'; se omite la inserción después del borrado.",
                    table,
                )
                continue
            append_dataframe_to_table(engine, table, df_aligned, table_obj=table_obj)
        else:
            if table_obj is not None:
                with engine.begin() as connection:
                    upsert_dataframe(connection, table_obj, df_aligned)
            else:
                logging.warning(
                    "No se cuenta con metadatos de '%s'; no se pudo sincronizar la información.",
                    table,
                )
                continue

        logging.info("✅ Tabla '%s' actualizada correctamente", table)


# def build_engine() -> Engine:
#     conn_str = (
#         f"postgresql+psycopg2://{DB_CONFIG['USER']}:{DB_CONFIG['PASSWORD']}"
#         f"@{DB_CONFIG['HOST']}:{DB_CONFIG['PORT']}/{DB_CONFIG['NAME']}"
#     )
#     return create_engine(conn_str)


# def parse_arguments(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
#     parser = argparse.ArgumentParser(description="Actualiza los catálogos CFDI desde el archivo del SAT")
#     parser.add_argument("--url", default=DEFAULT_URL, help="URL del archivo XLS a descargar")
#     parser.add_argument(
#         "--workbook",
#         default=DEFAULT_FILENAME,
#         help="Ruta donde se almacenará el archivo descargado o archivo existente si se usa --skip-download",
#     )
#     parser.add_argument("--skip-download", action="store_true", help="No descargar el archivo si ya existe")
#     parser.add_argument("--keep-file", action="store_true", help="No eliminar el archivo XLS al finalizar")
#     parser.add_argument("--no-truncate", action="store_true", help="No eliminar datos previos antes de insertar (append)")
#     parser.add_argument("--dry-run", action="store_true", help="Procesa el archivo sin modificar la base de datos")
#     parser.add_argument("--verbose", action="store_true", help="Muestra información detallada de depuración")
#     return parser.parse_args(argv)


# def main(argv: Optional[Sequence[str]] = None) -> int:
#     args = parse_arguments(argv)
#     configure_logging(args.verbose)

#     try:
#         workbook_path = download_workbook(args.url, args.workbook, overwrite=not args.skip_download)
#     except Exception as exc:
#         logging.error("No fue posible descargar el archivo: %s", exc)
#         return 1

#     sheet_payloads: List[SheetPayload] = []
#     try:
#         with pd.ExcelFile(workbook_path, engine="xlrd") as xls:
#             for sheet_name in xls.sheet_names:
#                 try:
#                     sheet_payloads.append(read_sheet(xls, sheet_name))
#                 except Exception as exc:
#                     logging.warning("No fue posible procesar la hoja '%s': %s", sheet_name, exc)
#     except Exception as exc:
#         logging.error("Error al abrir el archivo XLS: %s", exc)
#         return 1

#     tables = consolidate_tables(sheet_payloads)

#     if not tables:
#         logging.error("No se generó información de catálogos para actualizar.")
#         return 1

#     try:
#         engine = build_engine()
#     except Exception as exc:
#         logging.error("No fue posible crear el engine de base de datos: %s", exc)
#         return 1

#     try:
#         load_catalogs_to_database(
#             engine,
#             tables,
#             truncate_before_insert=not args.no_truncate,
#             dry_run=args.dry_run,
#         )
#     except Exception as exc:
#         logging.error("Se produjo un error al actualizar los catálogos: %s", exc)
#         return 1
#     finally:
#         if not args.keep_file and os.path.exists(workbook_path):
#             try:
#                 os.remove(workbook_path)
#                 logging.debug("Archivo temporal eliminado: %s", workbook_path)
#             except OSError as exc:
#                 logging.warning("No se pudo eliminar el archivo %s: %s", workbook_path, exc)

    logging.info("✅ Proceso completado correctamente")
    return 0


if __name__ == "__main__":  # pragma: no cover - punto de entrada principal
    sys.exit(main())
