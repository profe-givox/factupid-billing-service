"""Tests para notify_main_app con diferentes escenarios de Django."""

from datetime import date
from unittest.mock import patch, MagicMock

from app.routers.webhooks import notify_main_app


class TestNotifyMainAppExito:
    """notify_main_app retorna True cuando Django responde bien."""

    def test_exito_200(self):
        with patch("httpx.Client") as mock_httpx:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = '{"success": true}'
            mock_instance = MagicMock()
            mock_instance.post.return_value = mock_response
            mock_httpx.return_value.__enter__ = MagicMock(return_value=mock_instance)
            mock_httpx.return_value.__exit__ = MagicMock(return_value=False)

            result = notify_main_app(
                user_id=1, billing_code="CFDI_PRO", subscription_id=1,
            )
            assert result is True
            assert mock_instance.post.call_count == 1


class TestNotifyMainAppPeriodFields:
    """notify_main_app envía period_start, period_end, stripe_subscription_id en el payload."""

    def test_envia_period_fields_y_stripe_id(self):
        with patch("httpx.Client") as mock_httpx:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = '{"success": true}'
            mock_instance = MagicMock()
            mock_instance.post.return_value = mock_response
            mock_httpx.return_value.__enter__ = MagicMock(return_value=mock_instance)
            mock_httpx.return_value.__exit__ = MagicMock(return_value=False)

            result = notify_main_app(
                user_id=42,
                billing_code="CFDI_ENTERPRISE",
                subscription_id=10,
                period_start=date(2026, 8, 1),
                period_end=date(2026, 8, 31),
                stripe_subscription_id="sub_stripe_abc",
            )

            assert result is True

            # Verificar que el payload enviado contiene los campos
            call_args = mock_instance.post.call_args
            sent_payload = call_args[1].get("json") or call_args[0][1]
            assert sent_payload["period_start"] == "2026-08-01"
            assert sent_payload["period_end"] == "2026-08-31"
            assert sent_payload["stripe_subscription_id"] == "sub_stripe_abc"

    def test_no_envia_period_fields_si_son_none(self):
        with patch("httpx.Client") as mock_httpx:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = '{"success": true}'
            mock_instance = MagicMock()
            mock_instance.post.return_value = mock_response
            mock_httpx.return_value.__enter__ = MagicMock(return_value=mock_instance)
            mock_httpx.return_value.__exit__ = MagicMock(return_value=False)

            result = notify_main_app(
                user_id=1, billing_code="CFDI_PRO", subscription_id=1,
            )

            assert result is True
            call_args = mock_instance.post.call_args
            sent_payload = call_args[1].get("json") or call_args[0][1]
            assert "period_start" not in sent_payload
            assert "period_end" not in sent_payload
            assert "stripe_subscription_id" not in sent_payload


class TestNotifyMainAppConFallbackCola:
    """Cuando Django falla 3 veces, se guarda en cola."""

    def test_fallback_a_cola(self):
        with patch("httpx.Client") as mock_httpx:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_instance = MagicMock()
            mock_instance.post.return_value = mock_response
            mock_httpx.return_value.__enter__ = MagicMock(return_value=mock_instance)
            mock_httpx.return_value.__exit__ = MagicMock(return_value=False)

            with patch("app.routers.webhooks._save_failed_notification") as mock_save:
                with patch("app.routers.webhooks.time.sleep"):
                    result = notify_main_app(
                        user_id=1, billing_code="CFDI_PRO", subscription_id=1,
                    )

                    assert result is False
                    assert mock_instance.post.call_count == 3
                    mock_save.assert_called_once()