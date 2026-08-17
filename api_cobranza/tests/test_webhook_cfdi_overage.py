"""Tests Fase 7B: facturas mixtas de Stripe (renovación + excedentes CFDI).

Cubre:
- Factura SOLO de excedentes: NO renueva suscripción.
- Factura mixta (renovación + excedente): SÍ renueva, usa period de línea de suscripción.
- Helpers: _is_cfdi_overage_line, _get_cfdi_overage_lines, _is_subscription_line, _get_subscription_line.
- Facturas normales (sin excedentes) siguen su flujo original.
- report-overage crea invoice item con metadata factupid_type.
"""

import time
from datetime import date, datetime, timezone

from unittest.mock import patch, MagicMock

import pytest

from sqlmodel import Session

from tests.conftest import test_engine, _make_invoice_event
from app.models.plan import Plan
from app.models.subscription import Subscription
from app.models.payment import Payment

WEBHOOK_URL = "/api/pagos/webhooks/stripe"
INVOICE_WEBHOOK_BODY = '{"type": "invoice.payment_succeeded"}'
WEBHOOK_HEADERS = {
    "stripe-signature": "t=123,v1=valida",
    "Content-Type": "application/json",
}
REPORT_OVERAGE_URL = "/api/pagos/subscriptions/report-overage"


def _seed_subscription(
    user_id=1,
    status="active",
    stripe_customer_id="cus_overage_1",
    start_date=None,
    end_date=None,
):
    """Crea un plan PRO y una suscripción en la BD de test."""
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
            status=status,
            provider="stripe",
            stripe_subscription_id="sub_stripe_overage_1",
            stripe_customer_id=stripe_customer_id,
            start_date=start_date or date(2026, 8, 1),
            end_date=end_date or date(2026, 8, 31),
        )
        db.add(sub)
        db.commit()
        db.refresh(sub)
        return sub.id


def _make_overage_invoice(
    sub_id,
    *,
    invoice_id=None,
    stripe_sub_id="sub_stripe_overage_1",
    billing_reason="subscription_cycle",
    placement="line",
):
    """Factura SOLO de excedentes CFDI (sin línea de suscripción).

    placement:
      - "line": metadata en invoice.lines.data[].metadata
      - "item_details": metadata dentro de invoice_item_details
    """
    now_ts = int(time.time())
    invoice_id = invoice_id or f"in_overage_{int(time.time() * 1000)}"

    line = {
        "period": {"start": now_ts, "end": now_ts + 30 * 86400},
        "parent": {
            "subscription_item_details": {"subscription": stripe_sub_id},
        },
    }

    if placement == "line":
        line["metadata"] = {"factupid_type": "cfdi_overage"}
    elif placement == "item_details":
        line["invoice_item_details"] = {
            "id": f"ii_overage_{int(time.time() * 1000)}",
            "metadata": {
                "factupid_type": "cfdi_overage",
                "overage_period_id": "77",
                "period_start": "2026-08-01",
                "period_end": "2026-08-31",
                "quantity": "3",
            },
        }

    obj = {
        "id": invoice_id,
        "billing_reason": billing_reason,
        "amount_paid": 150,
        "currency": "mxn",
        "status_transitions": {"paid_at": now_ts},
        "parent": {
            "subscription_details": {
                "subscription": stripe_sub_id,
                "metadata": {
                    "subscription_id": str(sub_id),
                    "user_id": "1",
                    "billing_code": "CFDI_PRO",
                },
            }
        },
        "lines": {"data": [line]},
    }

    return {
        "id": f"evt_{invoice_id}",
        "type": "invoice.payment_succeeded",
        "data": {"object": obj},
    }


def _make_mixed_invoice(
    sub_id,
    *,
    invoice_id=None,
    stripe_sub_id="sub_stripe_overage_1",
    billing_reason="subscription_cycle",
    overage_placement="line",
):
    """Factura MIXTA: línea de suscripción + línea de excedente CFDI.

    overage_placement:
      - "line": metadata en invoice.lines.data[].metadata
      - "item_details": metadata dentro de invoice_item_details
    """
    now_ts = int(time.time())
    invoice_id = invoice_id or f"in_mixed_{int(time.time() * 1000)}"

    # Línea de suscripción real (NO excedente)
    sub_period_start = now_ts
    sub_period_end = now_ts + 30 * 86400

    sub_line = {
        "period": {"start": sub_period_start, "end": sub_period_end},
        "parent": {
            "subscription_item_details": {"subscription": stripe_sub_id},
        },
    }

    # Línea de excedente CFDI
    overage_line = {
        "period": {"start": now_ts, "end": now_ts + 30 * 86400},
        "parent": {
            "subscription_item_details": {"subscription": stripe_sub_id},
        },
    }

    if overage_placement == "line":
        overage_line["metadata"] = {"factupid_type": "cfdi_overage"}
    elif overage_placement == "item_details":
        overage_line["invoice_item_details"] = {
            "id": f"ii_overage_mixed_{int(time.time() * 1000)}",
            "metadata": {
                "factupid_type": "cfdi_overage",
                "overage_period_id": "88",
                "period_start": "2026-08-01",
                "period_end": "2026-08-31",
                "quantity": "5",
            },
        }

    obj = {
        "id": invoice_id,
        "billing_reason": billing_reason,
        "amount_paid": 5150,  # $50 suscripción + $1.50 excedente
        "currency": "mxn",
        "status_transitions": {"paid_at": now_ts},
        "parent": {
            "subscription_details": {
                "subscription": stripe_sub_id,
                "metadata": {
                    "subscription_id": str(sub_id),
                    "user_id": "1",
                    "billing_code": "CFDI_PRO",
                },
            }
        },
        "lines": {"data": [sub_line, overage_line]},
    }

    return {
        "id": f"evt_{invoice_id}",
        "type": "invoice.payment_succeeded",
        "data": {"object": obj},
    }


def _post_invoice_webhook(client, event_dict):
    """Envía el evento invoice.payment_succeeded por el webhook real."""
    with patch("stripe.Webhook.construct_event", return_value=event_dict), \
            patch("app.routers.webhooks.engine", test_engine):
        return client.post(
            WEBHOOK_URL,
            content=INVOICE_WEBHOOK_BODY,
            headers=WEBHOOK_HEADERS,
        )


# ---------------------------------------------------------------------------
# 1. Factura SOLO de excedentes: NO renueva suscripción
# ---------------------------------------------------------------------------


class TestCfdiOverageInvoiceWebhook:
    """invoice.payment_succeeded de excedentes sin línea de suscripción
    NO renueva la suscripción."""

    def test_no_notifica_subscription_renewed(self, client):
        sub_id = _seed_subscription()
        event = _make_overage_invoice(sub_id)

        with patch("app.routers.webhooks.notify_subscription_event") as mock_notify_sub, \
                patch("app.routers.webhooks.notify_main_app") as mock_notify_main:
            response = _post_invoice_webhook(client, event)

        assert response.status_code == 200
        mock_notify_sub.assert_not_called()
        mock_notify_main.assert_not_called()

    def test_no_actualiza_start_date_ni_end_date(self, client):
        sub_id = _seed_subscription(
            start_date=date(2026, 8, 1),
            end_date=date(2026, 8, 31),
        )
        event = _make_overage_invoice(sub_id)

        _post_invoice_webhook(client, event)

        with Session(test_engine) as db:
            sub = db.get(Subscription, sub_id)
            assert sub.start_date == date(2026, 8, 1)
            assert sub.end_date == date(2026, 8, 31)

    def test_no_cambia_subscription_status(self, client):
        sub_id = _seed_subscription(status="active")
        event = _make_overage_invoice(sub_id)

        _post_invoice_webhook(client, event)

        with Session(test_engine) as db:
            sub = db.get(Subscription, sub_id)
            assert sub.status == "active"

    def test_no_notifica_main_app_y_registra_payment(self, client):
        sub_id = _seed_subscription()
        event = _make_overage_invoice(sub_id, invoice_id="in_overage_pay_1")

        with patch("app.routers.webhooks.notify_main_app") as mock_notify_main:
            _post_invoice_webhook(client, event)

        mock_notify_main.assert_not_called()

        # Se registra el pago (idempotente por invoice_id) sin renovación
        with Session(test_engine) as db:
            payment = db.exec(
                Payment.__table__.select().where(
                    Payment.provider_payment_id == "in_overage_pay_1"
                )
            ).first()
            assert payment is not None
            assert payment.subscription_id == sub_id
            assert payment.amount == 150
            assert payment.status == "succeeded"

    def test_detecta_metadata_en_invoice_item_details(self, client):
        sub_id = _seed_subscription()
        event = _make_overage_invoice(sub_id, placement="item_details")

        with patch("app.routers.webhooks.notify_subscription_event") as mock_notify_sub, \
                patch("app.routers.webhooks.notify_main_app") as mock_notify_main:
            response = _post_invoice_webhook(client, event)

        assert response.status_code == 200
        mock_notify_sub.assert_not_called()
        mock_notify_main.assert_not_called()

        with Session(test_engine) as db:
            sub = db.get(Subscription, sub_id)
            assert sub.status == "active"
            assert sub.start_date == date(2026, 8, 1)


# ---------------------------------------------------------------------------
# 2. Factura MIXTA (renovación + excedente): SÍ renueva suscripción
# ---------------------------------------------------------------------------


class TestMixedInvoiceSubscriptionRenewal:
    """Factura mixta con línea de suscripción + línea de excedente CFDI
    procesa la renovación normalmente."""

    def test_subscription_cycle_mixed_renovacion_sigue_notificando(self, client):
        """T2: subscription_cycle con excedente SÍ llama
        notify_subscription_event(subscription_renewed)."""
        sub_id = _seed_subscription()

        event = _make_mixed_invoice(
            sub_id,
            billing_reason="subscription_cycle",
            invoice_id="in_mixed_cycle_1",
        )

        with patch("app.routers.webhooks.notify_subscription_event") as mock_notify_sub:
            response = _post_invoice_webhook(client, event)

        assert response.status_code == 200
        mock_notify_sub.assert_called_once()
        assert mock_notify_sub.call_args.kwargs["event_type"] == "subscription_renewed"

    def test_subscription_create_mixed_activacion_sigue_notificando(self, client):
        """T5: subscription_create con excedente SÍ llama
        notify_main_app (checkout_complete)."""
        sub_id = _seed_subscription()

        event = _make_mixed_invoice(
            sub_id,
            billing_reason="subscription_create",
            invoice_id="in_mixed_create_1",
        )

        with patch("app.routers.webhooks.notify_main_app") as mock_notify_main:
            response = _post_invoice_webhook(client, event)

        assert response.status_code == 200
        mock_notify_main.assert_called_once()
        assert mock_notify_main.call_args.kwargs["subscription_id"] == sub_id

    def test_mixed_usa_period_de_suscripcion_no_de_excedente(self, client):
        """T3: La factura mixta usa el period de la línea de suscripción,
        NO el period de la línea de excedente para actualizar
        start_date/end_date."""
        sub_id = _seed_subscription(
            start_date=date(2026, 8, 1),
            end_date=date(2026, 8, 31),
        )

        now_ts = int(time.time())
        new_period_start = now_ts + 1000  # Futuro
        new_period_end = now_ts + 30 * 86400 + 1000

        # Crear factura mixta con period específico en la línea de suscripción
        sub_line = {
            "period": {"start": new_period_start, "end": new_period_end},
            "parent": {
                "subscription_item_details": {"subscription": "sub_stripe_overage_1"},
            },
        }
        overage_line = {
            "period": {"start": now_ts, "end": now_ts + 30 * 86400},
            "parent": {
                "subscription_item_details": {"subscription": "sub_stripe_overage_1"},
            },
            "metadata": {"factupid_type": "cfdi_overage"},
        }

        event = {
            "id": "evt_mixed_period_1",
            "type": "invoice.payment_succeeded",
            "data": {
                "object": {
                    "id": "in_mixed_period_1",
                    "billing_reason": "subscription_cycle",
                    "amount_paid": 5150,
                    "currency": "mxn",
                    "status_transitions": {"paid_at": now_ts},
                    "parent": {
                        "subscription_details": {
                            "subscription": "sub_stripe_overage_1",
                            "metadata": {
                                "subscription_id": str(sub_id),
                                "user_id": "1",
                                "billing_code": "CFDI_PRO",
                            },
                        }
                    },
                    "lines": {"data": [overage_line, sub_line]},
                }
            },
        }

        _post_invoice_webhook(client, event)

        with Session(test_engine) as db:
            sub = db.get(Subscription, sub_id)
            expected_start = datetime.fromtimestamp(
                new_period_start, tz=timezone.utc
            ).date()
            expected_end = datetime.fromtimestamp(
                new_period_end, tz=timezone.utc
            ).date()
            assert sub.start_date == expected_start
            assert sub.end_date == expected_end

    def test_mixed_no_hace_return_prematuro(self, client):
        """T4: La factura mixta NO hace return prematuro. La suscripción
        se actualiza y se registra el pago."""
        sub_id = _seed_subscription(
            start_date=date(2026, 8, 1),
            end_date=date(2026, 8, 31),
        )
        event = _make_mixed_invoice(
            sub_id,
            billing_reason="subscription_cycle",
            invoice_id="in_mixed_nopremature_1",
        )

        _post_invoice_webhook(client, event)

        with Session(test_engine) as db:
            # El pago se registró
            payment = db.exec(
                Payment.__table__.select().where(
                    Payment.provider_payment_id == "in_mixed_nopremature_1"
                )
            ).first()
            assert payment is not None
            assert payment.subscription_id == sub_id

            # start_date/end_date se actualizaron (ya no son las originales)
            sub = db.get(Subscription, sub_id)
            assert sub.start_date is not None
            assert sub.end_date is not None


# ---------------------------------------------------------------------------
# 3. Helpers: _is_cfdi_overage_line, _is_subscription_line
# ---------------------------------------------------------------------------


class TestHelpersDetection:
    """Tests de los helpers de detección de líneas."""

    def test_is_cfdi_overage_line_detecta_metadata_directa(self):
        """T6: _is_cfdi_overage_line detecta metadata en line.metadata."""
        from app.routers.webhooks import _is_cfdi_overage_line

        line = {
            "metadata": {"factupid_type": "cfdi_overage"},
            "parent": {},
        }
        assert _is_cfdi_overage_line(line) is True

    def test_is_cfdi_overage_line_detecta_parent_invoice_item_details(self):
        """T6: _is_cfdi_overage_line detecta metadata en
        parent.invoice_item_details.metadata."""
        from app.routers.webhooks import _is_cfdi_overage_line

        line = {
            "parent": {
                "invoice_item_details": {
                    "metadata": {"factupid_type": "cfdi_overage"},
                },
            },
        }
        assert _is_cfdi_overage_line(line) is True

    def test_is_cfdi_overage_line_detecta_line_invoice_item_details(self):
        """_is_cfdi_overage_line detecta metadata en
        line.invoice_item_details.metadata."""
        from app.routers.webhooks import _is_cfdi_overage_line

        line = {
            "invoice_item_details": {
                "metadata": {"factupid_type": "cfdi_overage"},
            },
            "parent": {},
        }
        assert _is_cfdi_overage_line(line) is True

    def test_is_cfdi_overage_line_no_detecta_linea_normal(self):
        """_is_cfdi_overage_line NO detecta una línea normal de suscripción."""
        from app.routers.webhooks import _is_cfdi_overage_line

        line = {
            "period": {"start": 1000, "end": 2000},
            "parent": {
                "subscription_item_details": {"subscription": "sub_123"},
            },
        }
        assert _is_cfdi_overage_line(line) is False

    def test_is_subscription_line_ignora_cfdi_overage(self):
        """T7: _is_subscription_line ignora líneas cfdi_overage."""
        from app.routers.webhooks import _is_subscription_line

        line = {
            "metadata": {"factupid_type": "cfdi_overage"},
            "parent": {
                "subscription_item_details": {"subscription": "sub_123"},
            },
        }
        assert _is_subscription_line(line) is False

    def test_is_subscription_line_detecta_linea_normal(self):
        """_is_subscription_line detecta una línea normal de suscripción."""
        from app.routers.webhooks import _is_subscription_line

        line = {
            "period": {"start": 1000, "end": 2000},
            "parent": {
                "subscription_item_details": {"subscription": "sub_123"},
            },
        }
        assert _is_subscription_line(line) is True

    def test_get_subscription_line_devuelve_primera_suscripcion(self):
        """_get_subscription_line retorna la primera línea de suscripción
        ignorando las de excedente."""
        from app.routers.webhooks import _get_subscription_line

        overage_line = {
            "metadata": {"factupid_type": "cfdi_overage"},
            "parent": {
                "subscription_item_details": {"subscription": "sub_123"},
            },
        }
        sub_line = {
            "period": {"start": 1000, "end": 2000},
            "parent": {
                "subscription_item_details": {"subscription": "sub_123"},
            },
        }

        invoice = {"lines": {"data": [overage_line, sub_line]}}
        result = _get_subscription_line(invoice)
        assert result is sub_line

    def test_get_subscription_line_devuelve_none_si_solo_overage(self):
        """_get_subscription_line retorna None si solo hay líneas de excedente."""
        from app.routers.webhooks import _get_subscription_line

        overage_line = {
            "metadata": {"factupid_type": "cfdi_overage"},
            "parent": {
                "subscription_item_details": {"subscription": "sub_123"},
            },
        }

        invoice = {"lines": {"data": [overage_line]}}
        result = _get_subscription_line(invoice)
        assert result is None


# ---------------------------------------------------------------------------
# 4. Facturas normales siguen su flujo original
# ---------------------------------------------------------------------------


class TestInvoiceNormalSigueNotificando:
    """Las facturas normales de suscripción (sin excedentes) siguen su
    flujo original."""

    def test_subscription_cycle_sigue_notificando_renewed(self, client):
        sub_id = _seed_subscription()

        event = _make_invoice_event(
            sub_id,
            billing_code="CFDI_PRO",
            stripe_sub_id="sub_stripe_overage_1",
            billing_reason="subscription_cycle",
            invoice_id="in_normal_cycle_1",
        )

        with patch("app.routers.webhooks.notify_subscription_event") as mock_notify_sub:
            response = _post_invoice_webhook(client, event)

        assert response.status_code == 200
        mock_notify_sub.assert_called_once()
        assert mock_notify_sub.call_args.kwargs["event_type"] == "subscription_renewed"

    def test_subscription_create_sigue_notificando_checkout_complete(self, client):
        sub_id = _seed_subscription()

        event = _make_invoice_event(
            sub_id,
            billing_code="CFDI_PRO",
            stripe_sub_id="sub_stripe_overage_1",
            billing_reason="subscription_create",
            invoice_id="in_normal_create_1",
        )

        with patch("app.routers.webhooks.notify_main_app") as mock_notify_main:
            response = _post_invoice_webhook(client, event)

        assert response.status_code == 200
        mock_notify_main.assert_called_once()
        assert mock_notify_main.call_args.kwargs["subscription_id"] == sub_id


# ---------------------------------------------------------------------------
# 5. report-overage crea invoice item con metadata
# ---------------------------------------------------------------------------


class TestReportOverageMetadata:
    """report-overage crea el invoice item con metadata factupid_type."""

    @pytest.fixture(autouse=True)
    def _patch_engine(self):
        with patch("app.routers.subscriptions.engine", test_engine):
            yield

    def test_invoice_item_metadata_incluye_factupid_type(self, client, auth_headers):
        sub_id = _seed_subscription()

        payload = {
            "subscription_id": sub_id,
            "user_id": 1,
            "overage_period_id": 77,
            "period_start": "2026-08-01",
            "period_end": "2026-08-31",
            "quantity": 3,
            "unit_price": 0.5,
            "total_amount": 1.5,
            "currency": "mxn",
        }

        item = MagicMock()
        item.id = "ii_overage_meta_1"

        with patch("stripe.InvoiceItem.create") as mock_invoice_item:
            mock_invoice_item.return_value = item

            response = client.post(REPORT_OVERAGE_URL, json=payload)

        assert response.status_code == 200
        mock_invoice_item.assert_called_once()
        metadata = mock_invoice_item.call_args.kwargs["metadata"]
        assert metadata["factupid_type"] == "cfdi_overage"
        assert metadata["overage_period_id"] == "77"
        assert metadata["subscription_id"] == str(sub_id)
        assert metadata["quantity"] == "3"
