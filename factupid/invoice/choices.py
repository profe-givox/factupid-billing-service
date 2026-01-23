estatus_timbre = (
    ('A', 'Activado'),
    ('S', 'Suspendido'),
)

tipo_Cliente = (
        ('O','OnDemant'),
        ('P','Prepago'),
    )

tipo_Receptor = (
        ('moral','Persona Moral'),
        ('fisica','Persona Fisica'),
        ('extranjero','Extranjero'),
    )

estatus = (
    ('A', 'Activar'),
    ('S', 'Suspender')
)

estatus_token = (
    ('true', 'Activo'),
    ('false', 'Suspendido')
)

ESTADO_FIRMA = (
    ('true', 'FIRMADO'),
    ('false', 'SIN_FIRMAR')
)

STATUS_CHOICES = [
        ('firmada', 'Firmada'),
        ('timbrada', 'Timbrada'),
        ('firmada_timbrada', 'Firmada y Timbrada'),
        ('sin_timbrar', 'Sin Timbrar'),
    ]

OPERATION_CHOICES = [
        ('stamp', 'Stamp'),
        ('cancel', 'Cancel'),
        ('sign_stamp', 'Sign and Stamp'),
    ]

REGIMENES_FISCAL = (
        ("601", "General de Ley Personas Morales"),
        ("603", "Personas Morales con Fines no Lucrativos"),
        ("605", "Sueldos y Salarios e Ingresos Asimilados a Salarios"),
        ("606", "Arrendamiento"),
        ("607", "Régimen de Enajenación o Adquisición de Bienes"),
        ("608", "Demás ingresos"),
        ("609", "Consolidación"),
        ("610", "Residentes en el Extranjero sin Establecimiento Permanente en Máxico"),
        ("611", "Ingresos por Dividendos (socios y accionistas)"),
        ("612", "Personas Físicas con Actividades Empresariales y Profesionales"),
        ("614", "Ingresos por intereses"),
        ("615", "Régimen de los ingresos por obtención de premios"),
        ("616", "Sin obligaciones fiscales"),
        ("620", "Sociedades Cooperativas de Producción que optan por diferir sus ingresos"),
        ("621", "Incorporación Fiscal"),
        ("622", "Actividades Agrícolas, Ganaderas, Silvícolas y Pesqueras"),
        ("623", "Opcional para Grupos de Sociedades"),
        ("624", "Coordinados"),
        ("625", "Régimen de las Actividades Empresariales con ingresos a través de Plataformas Tecnológicas"),
        ("626", "Régimen Simplificado de Confianza"),
        ("628", "Hidrocarburos"),
        ("629", "De los Regímenes Fiscales Preferentes y de las Empresas Multinacionales"),
        ("630", "Enajenación de acciones en bolsa de valores"),
)
