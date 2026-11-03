import argparse
import json
import os
from datetime import date, timedelta
from decimal import Decimal

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "c7_django_settings")
django.setup()

from django.contrib.auth.models import User
from django.core.management import call_command

from cfdi.models import UsersCFDI, UserTimbreCount
from console.models import Plan, Service, Service_Plan, User_Service


def _seed():
    user_1 = User.objects.create_user(
        username="c7_user_1", email="c7_user_1@test.local", password="c7-test"
    )
    user_2 = User.objects.create_user(
        username="c7_user_2", email="c7_user_2@test.local", password="c7-test"
    )
    service = Service.objects.create(
        nombre="CFDI",
        descripcion="CFDI",
        tipo="app",
        url_servicio="/cfdi/",
    )
    pro = Plan.objects.create(
        nombre="PRO",
        descripcion="Pro",
        caracteristicas="",
        tipo="mensual",
        precio=Decimal("299.00"),
        limite_operaciones_dia=100,
        limite_operaciones_plan=1000,
        billing_code="CFDI_PRO",
    )
    free = Plan.objects.create(
        nombre="FREE",
        descripcion="Free",
        caracteristicas="",
        tipo="mensual",
        precio=Decimal("0.00"),
        limite_operaciones_dia=10,
        limite_operaciones_plan=100,
        billing_code="CFDI_FREE",
    )
    pro_service_plan = Service_Plan.objects.create(
        service=service,
        plan=pro,
        isActive=True,
        fechaVigenciaInicio=date.today(),
        fechaVigenciaFin=date.today() + timedelta(days=365),
    )
    free_service_plan = Service_Plan.objects.create(
        service=service,
        plan=free,
        isActive=True,
        fechaVigenciaInicio=date.today(),
        fechaVigenciaFin=date.today() + timedelta(days=365),
    )
    return {
        "user_ids": [user_1.id, user_2.id],
        "service_id": service.id,
        "pro_plan_id": pro.id,
        "free_plan_id": free.id,
        "pro_service_plan_id": pro_service_plan.id,
        "free_service_plan_id": free_service_plan.id,
    }


def _reset():
    call_command("flush", interactive=False, verbosity=0)
    return _seed()


def _seed_canceled(user_id):
    user = User.objects.get(id=user_id)
    service = Service.objects.get(nombre="CFDI")
    pro = Plan.objects.get(billing_code="CFDI_PRO")
    service_plan = Service_Plan.objects.get(service=service, plan=pro)
    user_service = User_Service.objects.create(
        idUser=user,
        idService=service,
        idPlan=pro,
        idServicePlan=service_plan,
        date_cutoff=date(2026, 1, 31),
        subscription_status="canceled",
        billing_subscription_id="sub_canceled_old",
        stripe_subscription_id="stripe_canceled_old",
    )
    cfdi_user = UsersCFDI.objects.create(
        idUserCFDI=user,
        idUserServicePlan_id=user_service,
    )
    count = UserTimbreCount.objects.create(
        user_cfdi=cfdi_user,
        periodo_inicio=date(2026, 1, 1),
        periodo_fin=date(2026, 1, 31),
        plan=pro,
        limite_timbres=1000,
        contador_actual=7,
        activo=True,
    )
    return {
        "user_service_id": user_service.id,
        "cfdi_user_id": cfdi_user.idUserCFDI_id,
        "count_id": count.id,
    }


def _snapshot(user_ids):
    result = {}
    for user_id in user_ids:
        user = User.objects.filter(id=user_id).first()
        if not user:
            result[str(user_id)] = None
            continue
        services = []
        for user_service in User_Service.objects.filter(idUser=user).order_by("id"):
            services.append(
                {
                    "id": user_service.id,
                    "service_id": user_service.idService_id,
                    "plan_id": user_service.idPlan_id,
                    "billing_code": (
                        user_service.idPlan.billing_code
                        if user_service.idPlan_id
                        else None
                    ),
                    "service_plan_id": user_service.idServicePlan_id,
                    "date_cutoff": (
                        user_service.date_cutoff.isoformat()
                        if user_service.date_cutoff
                        else None
                    ),
                    "subscription_status": user_service.subscription_status,
                    "cancel_at_period_end": user_service.cancel_at_period_end,
                    "billing_subscription_id": user_service.billing_subscription_id,
                    "stripe_subscription_id": user_service.stripe_subscription_id,
                    "last_billing_event_created_at": (
                        user_service.last_billing_event_created_at.isoformat()
                        if user_service.last_billing_event_created_at
                        else None
                    ),
                }
            )
        cfdi_users = []
        counts = []
        for cfdi_user in UsersCFDI.objects.filter(idUserCFDI_id=user_id):
            cfdi_users.append(
                {
                    "id": cfdi_user.idUserCFDI_id,
                    "user_service_id": cfdi_user.idUserServicePlan_id_id,
                    "has_token": bool(cfdi_user.token),
                }
            )
            for count in UserTimbreCount.objects.filter(user_cfdi=cfdi_user).order_by(
                "id"
            ):
                counts.append(
                    {
                        "id": count.id,
                        "periodo_inicio": count.periodo_inicio.isoformat(),
                        "periodo_fin": count.periodo_fin.isoformat(),
                        "contador_actual": count.contador_actual,
                        "limite_timbres": count.limite_timbres,
                        "activo": count.activo,
                        "plan_id": count.plan_id,
                        "plan_billing_code": (
                            count.plan.billing_code if count.plan_id else None
                        ),
                    }
                )
        result[str(user_id)] = {
            "user_id": user.id,
            "username": user.username,
            "groups": sorted(user.groups.values_list("name", flat=True)),
            "services": services,
            "cfdi_users": cfdi_users,
            "timbres": counts,
        }
    return result


def _set_counter(user_id, value):
    updated = UserTimbreCount.objects.filter(
        user_cfdi__idUserCFDI_id=user_id,
        activo=True,
    ).update(contador_actual=value)
    return {"updated": updated}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["reset", "snapshot", "seed_canceled", "set_counter"])
    parser.add_argument("--user-id", type=int)
    parser.add_argument("--value", type=int)
    args = parser.parse_args()

    if args.command == "reset":
        payload = _reset()
    elif args.command == "snapshot":
        user_ids = [args.user_id] if args.user_id else [1, 2]
        payload = _snapshot(user_ids)
    elif args.command == "seed_canceled":
        payload = _seed_canceled(args.user_id or 1)
    else:
        payload = _set_counter(args.user_id or 1, args.value or 0)

    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    main()
