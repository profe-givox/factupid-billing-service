"""Tests para detección de estado "unpaid" y guardado de stripe_customer_id.

Cubre:
- handle_subscription_updated con status unpaid → status="unpaid" y notifica
  subscription_unpaid (sin cancelar ni notificar plan_changed/cancel_scheduled)
- guardado de stripe_customer_id en checkout, invoice, deleted y updated
"""

from unittest.mock import patch

import pytest
from sqlmodel import Session

from tests.conftest import test_engine
from app.models.plan import Plan
from app.models.subscription import Subscription
from app.routers.webhooks import (
    handle_subscription_updated,
    handle_checkout_completed,
    handle_subscription_payment,
    handle_subscription_deleted,
)


def _seed_active_sub(user_id=1, stripe_customer_id="cus_123"):
    """Crea un plan PRO y una suscripción activa con stripe_id."""
    with Session(test_engine) as db:
        plan = Plan(
            code="CFDI_PRO", name="PRO", price=50, currency="MXN",
            interval="month", billing_type="subscription",
            stripe_price_id="price_pro_test", stripe_product_id="prod_pro_test",
            is_active=True,
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)

        sub = Subscription(
            user_id=user_id,
            plan_id=plan.id,
            status="active",
            provider="stripe",
            stripe_subscription_id="sub_stripe_1",
            stripe_customer_id=stripe_customer_id,
        )
        db.add(sub)
        db.commit()
        db.refresh(sub)
        return sub.id


class TestSubscriptionUpdatedUnpaid:
    """T1-T4: customer.subscription.updated con status unpaid."""

    @pytest.fixture(autouse=True)
    def _patch_engine(self):
        with patch("app.routers.webhooks.engine", test_engine):
            yield

    def _update_data(self, *, status="unpaid", cancel_at_period_end=False, customer="cus_123", price_id="price_pro_test"):
        return {
            "id": "sub_stripe_1",
            "status": status,
            "customer": customer,
            "cancel_at_period_end": cancel_at_period_end,
            "items": {
                "data": [{"price": {"id": price_id}}],
            },
        }

    def test_unpaid_pone_status_y_notifica(self):
        sub_id = _seed_active_sub()

        with patch("app.routers.webhooks.notify_subscription_event") as mock_notify:
            handle_subscription_updated(self._update_data())

        with Session(test_engine) as db:
            sub = db.get(Subscription, sub_id)
            assert sub.status == "unpaid"

        mock_notify.assert_called_once()
        kwargs = mock_notify.call_args[1]
        assert kwargs["event_type"] == "subscription_unpaid"
        assert kwargs["user_id"] == 1
        assert kwargs["billing_code"] == "CFDI_PRO"
        assert kwargs["subscription_id"] == sub_id
        assert kwargs["plan_id"] is not None
        assert kwargs["stripe_subscription_id"] == "sub_stripe_1"

    def test_unpaid_guarda_stripe_customer_id(self):
        sub_id = _seed_active_sub(stripe_customer_id=None)

        with patch("app.routers.webhooks.notify_subscription_event"):
            handle_subscription_updated(self._update_data(customer="cus_nuevo"))

        with Session(test_engine) as db:
            sub = db.get(Subscription, sub_id)
            assert sub.stripe_customer_id == "cus_nuevo"

    def test_unpaid_no_notifica_cancel_scheduled(self):
        _seed_active_sub()

        # Si viene cancel_at_period_end=True, unpaid tiene prioridad: NO se
        # notifica subscription_cancel_scheduled ni plan_changed.
        with patch("app.routers.webhooks.notify_subscription_event") as mock_notify:
            handle_subscription_updated(self._update_data(cancel_at_period_end=True))

        mock_notify.assert_called_once()
        assert mock_notify.call_args[1]["event_type"] == "subscription_unpaid"

    def test_unpaid_no_notifica_plan_changed(self):
        _seed_active_sub()

        # Cambio de plan con status unpaid: la prioridad es unpaid, no plan_changed
        with patch("app.routers.webhooks.notify_subscription_event") as mock_notify:
            handle_subscription_updated(self._update_data(price_id="price_ent_test"))

        mock_notify.assert_called_once()
        assert mock_notify.call_args[1]["event_type"] == "subscription_unpaid"


class TestStripeCustomerIdGuardado:
    """T5-T8: stripe_customer_id se persiste desde cada webhook."""

    @pytest.fixture(autouse=True)
    def _patch_engine(self):
        with patch("app.routers.webhooks.engine", test_engine):
            yield

    def test_checkout_completed_guarda_customer(self):
        sub_id = _seed_active_sub(stripe_customer_id=None)

        session_data = {
            "id": "cs_test_guardado",
            "metadata": {"subscription_id": str(sub_id), "user_id": "1"},
            "payment_status": "paid",
            "status": "complete",
            "mode": "subscription",
            "subscription": "sub_stripe_1",
            "customer": "cus_checkout_1",
        }

        with patch("app.routers.webhooks.notify_main_app"):
            handle_checkout_completed(session_data)

        with Session(test_engine) as db:
            sub = db.get(Subscription, sub_id)
            assert sub.stripe_customer_id == "cus_checkout_1"

    def test_invoice_guarda_customer(self):
        sub_id = _seed_active_sub(stripe_customer_id=None)
        now_ts = 1750000000

        invoice = {
            "id": "in_customer_test",
            "billing_reason": "subscription_create",
            "customer": "cus_invoice_1",
            "amount_paid": 5000,
            "currency": "mxn",
            "status_transitions": {"paid_at": now_ts},
            "parent": {
                "subscription_details": {
                    "subscription": "sub_stripe_1",
                    "metadata": {"subscription_id": str(sub_id), "user_id": "1"},
                }
            },
            "lines": {
                "data": [
                    {
                        "period": {"start": now_ts, "end": now_ts + 30 * 86400},
                        "parent": {
                            "subscription_item_details": {
                                "subscription": "sub_stripe_1",
                            }
                        },
                    }
                ]
            },
        }

        with patch("app.routers.webhooks.notify_main_app"):
            handle_subscription_payment(invoice, {})

        with Session(test_engine) as db:
            sub = db.get(Subscription, sub_id)
            assert sub.stripe_customer_id == "cus_invoice_1"

    def test_deleted_guarda_customer(self):
        sub_id = _seed_active_sub(stripe_customer_id=None)

        with patch("app.routers.webhooks.notify_subscription_event"):
            handle_subscription_deleted({
                "id": "sub_stripe_1",
                "customer": "cus_deleted_1",
                "canceled_at": 1750000000,
            })

        with Session(test_engine) as db:
            sub = db.get(Subscription, sub_id)
            assert sub.stripe_customer_id == "cus_deleted_1"
            assert sub.status == "canceled"

    def test_customer_existente_no_se_pisa(self):
        # Si ya hay customer, el invoice no debe sobrescribirlo
        sub_id = _seed_active_sub(stripe_customer_id="cus_original")
        now_ts = 1750000000

        invoice = {
            "id": "in_customer_dup",
            "billing_reason": "subscription_cycle",
            "customer": "cus_distinto",
            "amount_paid": 5000,
            "currency": "mxn",
            "status_transitions": {"paid_at": now_ts},
            "parent": {
                "subscription_details": {
                    "subscription": "sub_stripe_1",
                    "metadata": {"subscription_id": str(sub_id), "user_id": "1"},
                }
            },
            "lines": {
                "data": [
                    {
                        "period": {"start": now_ts, "end": now_ts + 30 * 86400},
                        "parent": {
                            "subscription_item_details": {
                                "subscription": "sub_stripe_1",
                            }
                        },
                    }
                ]
            },
        }

        with patch("app.routers.webhooks.notify_subscription_event"):
            handle_subscription_payment(invoice, {})

        with Session(test_engine) as db:
            sub = db.get(Subscription, sub_id)
            assert sub.stripe_customer_id == "cus_original"
