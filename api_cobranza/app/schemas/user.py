from pydantic import BaseModel
from typing import List, Optional

class CurrentUser(BaseModel):
    """
    Modelo que representa al usuario autenticado extraído del JWT.
    Mapea los claims personalizados inyectados por Django.
    """
    sub: str
    user_id: int
    username: str
    email: Optional[str] = None
    is_staff: bool = False
    is_superuser: bool = False
    groups: List[str] = []
    perms: List[str] = []
    tenant: int
    token_type: str
    aud: str
    iss: str