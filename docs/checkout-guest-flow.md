# Flujo de pago como invitado (Hugo -> Django -> Stripe)

Este documento describe el flujo de pago como invitado agregado en enero de 2026.

## Resumen

- El landing de Hugo ahora redirige a Django para iniciar el checkout.
- Django crea o reutiliza un usuario por email (modo invitado) y llama a la API de cobranza.
- La API de cobranza crea una sesión de Stripe Checkout y regresa `checkout_url`.
- Django redirige el navegador a Stripe Checkout.

## URLs públicas

- `GET /checkout/start/?plan=<plan_code>&mode=guest&email=<email>`
- `GET /checkout/success/`
- `GET /checkout/cancel/`

## Hugo (factupid-com)

Archivo: `factupid-com/content/_index.md`

- El cliente ya no hace POST directo a `api_cobranza`.
- Redirige a Django (`data-checkout-start`) con `plan`, `mode=guest` y `email` opcional.

Ejemplo:

```
https://app.factupid.com/checkout/start?plan=pro&mode=guest&email=correo@dominio.com
```

## Django (factupid)

Archivos:

- `factupid/console/views.py`
- `factupid/factupid/urls.py`

Comportamiento:

- `checkout_start` valida `plan`.
- Si hay sesión, usa `request.user`.
- Si es invitado:
  - Requiere `email`.
  - Busca usuario por email.
  - Crea usuario si no existe, con:
    - `username=email`
    - `email=email`
    - `is_active=False`
    - `set_unusable_password()`
  - Envía correo de activación (best-effort).
- Llama a la API de cobranza:
  - `POST {COBRANZA_API_BASE}/payments/init`
  - JSON: `{ "user_id": <id>, "plan_code": "<plan>" }`
- Redirige al `checkout_url` de la respuesta.

## Configuración

En settings de Django:

- `COBRANZA_API_BASE` (default: `http://192.168.54.71:8080`)

En settings de la API de cobranza:

- `STRIPE_SUCCESS_URL` -> `https://app.factupid.com/checkout/success/`
- `STRIPE_CANCEL_URL` -> `https://app.factupid.com/checkout/cancel/`

## Notas / Riesgos

- El pago queda asociado a un `user_id` real (no viene del cliente).
- Los usuarios invitados quedan inactivos hasta activar por correo.
- Si falla el correo de activación, el pago continúa igual.
