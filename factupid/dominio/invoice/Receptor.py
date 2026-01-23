from dataclasses import dataclass

@dataclass
class Receptor(object):
    """description of class"""
    taxpayer_id = str
    type_user = str
    cer = str
    key = str
    passphrase = str
