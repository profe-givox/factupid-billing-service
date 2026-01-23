from dataclasses import dataclass

@dataclass
class SupplierStamp:
    id = int 
    user = str 
    password = str 
    idsocio = str  #(snid de socio de plataforma de timbrado.), 
    urlSignManifest = str


