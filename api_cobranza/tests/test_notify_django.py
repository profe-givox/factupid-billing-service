"""Tests para notify_main_app con diferentes escenarios de Django."""

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