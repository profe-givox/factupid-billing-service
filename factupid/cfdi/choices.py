TIPO_DOCUMENTO_CHOICES = [
        ('borrador', 'Borrador'),
        ('plantilla', 'Plantilla'),
        ('timbrado', 'Timbrado'),
    ]

TIPO_ADDENDAS = [
    ('siemens_gamesa', 'SIEMENS GAMESA'),
    ('grupo_ado', 'Grupo ADO'),
    ('waldos', 'Waldos'),
    ('terra_multitransportes', 'Terra Multitransportes'),
]

SIEMENS_TIPO_DOCUMENTO = [
    ('factura','FACTURA'),
    ('nota_cargo', 'Nota de cargo'),
    ('nota_credito', 'Nota de crédito')
]


ADO_TIPO_ADDENDA = [
    ('pedido_capex', 'Pedido CAPEX'),
    ('refencia', 'Referencia'),
    ('pedido_jde', 'Pedido JDE'),
    ('nota_consumo', 'Nota de consumo')
]

MOTIVOS_CANCELACION = [
        ('01', 'Comprobante emitido con errores con relación'),
        ('02', 'Comprobante emitido con errores sin relación'),
        ('03', 'No se llevó a cabo la operación'),
        ('04', 'Operación nominativa relacionada en una factura global'),
    ]