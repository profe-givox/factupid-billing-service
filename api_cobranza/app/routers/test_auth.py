from fastapi import APIRouter, Depends
from app.core.security import get_current_user, require_permission
from app.core.permissions import Permission
from app.schemas.user import CurrentUser

router = APIRouter(prefix="/auth-test", tags=["auth-test"])


@router.get("/me")
def read_me(current_user: CurrentUser = Depends(get_current_user)):
    return {
        "ok": True,
        "message": "Token valido",
        "user_id": current_user.user_id,
        "sub": current_user.sub,
        "username": current_user.username,
        "email": current_user.email,
        "groups": current_user.groups,
        'perms': current_user.perms,
        "tenant": current_user.tenant,
        'token_type': current_user.token_type,
        'aud': current_user.aud,
        'iss': current_user.iss,
    }
    
@router.get("/can-view-payments")
def can_view_payments(
    current_user: CurrentUser = Depends(
        require_permission(Permission.VIEW_PAYMENTS)
    )
):
    return {
        "ok": True,
        "message": "Tienes permiso para ver pagos",
        "user_id": current_user.user_id,
        "username": current_user.username,
        "permiso_validado": Permission.VIEW_PAYMENTS,
    }
    
@router.get("/can-CREATE_CHECKOUT")
def can_view_payments(
    current_user: CurrentUser = Depends(
        require_permission(Permission.CREATE_CHECKOUT)
    )
):
    return {
        "ok": True,
        "message": "Tienes permiso para crear checkout",
        "user_id": current_user.user_id,
        "username": current_user.username,
        "permiso_validado": Permission.CREATE_CHECKOUT,
    }