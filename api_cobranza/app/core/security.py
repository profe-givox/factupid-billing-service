import logging
from jose import jwt, JWTError
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings
from app.schemas.user import CurrentUser

logger = logging.getLogger(__name__)

reusable_bearer = HTTPBearer()


def verify_token(token: str) -> CurrentUser:
    try:
        public_key = settings.JWT_PUBLIC_KEY.replace("\\n", "\n").strip()

        payload = jwt.decode(
            token,
            public_key,
            algorithms=[settings.JWT_ALGORITHM],
            issuer=settings.JWT_ISSUER,
            audience=settings.JWT_AUDIENCE,
        )

        if payload.get("token_type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Se requiere un access token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not payload.get("sub"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalido: falta sub",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not payload.get("tenant"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalido: falta tenant",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return CurrentUser(**payload)

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token invalido o expirado: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    auth: HTTPAuthorizationCredentials = Depends(reusable_bearer),
) -> CurrentUser:
    logger.info("Validando token Bearer")
    return verify_token(auth.credentials)

def require_permission(permission: str):
    """
    Factory de dependencias para validar permisos de forma idiomática en FastAPI.

    Uso:
        @router.post("/")
        def my_endpoint(
            current_user: CurrentUser = Depends(require_permission(Permission.TICKET_CREATE)),
            db: Session = Depends(get_db),
        ):
            ...

    El objeto retornado ES el current_user ya validado, listo para usar en el endpoint.
    """
    def permission_checker(
        current_user: CurrentUser = Depends(get_current_user),
    ) -> CurrentUser:
        if permission not in current_user.perms:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permiso requerido: {permission}",
            )
        return current_user

    return permission_checker