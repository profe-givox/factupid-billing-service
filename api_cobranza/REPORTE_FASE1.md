# Reporte de Cambios — Fase 1: Seguridad y Confiabilidad del Checkout

> **Proyecto:** Factupid Billing Service (FastAPI)
> **Fecha:** 2026-06-16
> **Tests:** 22/22 pasando

---

## 1. Objetivo de los cambios

Corregir problemas críticos de seguridad e integridad detectados en la auditoría:

1. **Endpoints públicos sin autenticación** — Cualquier persona podía crear/cancelar suscripciones y modificar planes.
2. **Activación sin verificación de pago** — `handle_checkout_completed` activaba la suscripción sin confirmar que Stripe hubiera recibido el pago (`payment_status`).
3. **Sin reintentos en notificación a Django** — Si Django fallaba al recibir el webhook, el pago quedaba huérfano (activo en billing API pero `User_Service` nunca creado).
4. **`/payments/confirm` inexistente** — Django lo llamaba pero no existía el endpoint.
5. **Sin cola de reintentos** — No había forma de recuperar notificaciones fallidas.

---

## 2. Archivos modificados

| Archivo | Tipo de cambio | Líneas |
|---|---|---|
| `app/models/payment.py` | Agregado modelo `WebhookNotificationQueue` | +21 |
| `app/models/subscription.py` | Actualizado docstring de `status` | 1 |
| `app/db/base.py` | Agregado import de `WebhookNotificationQueue` | 1 |
| `app/routers/payments.py` | JWT en 2 endpoints + 2 endpoints nuevos + imports | +110 |
| `app/routers/subscriptions.py` | JWT en 3 endpoints | +9 |
| `app/routers/plans.py` | JWT en 3 endpoints + imports | +10 |
| `app/routers/webhooks.py` | Validación `payment_status`, reintentos, cola, imports | +90 |
| `requirements.txt` | Agregado pytest | +3 |

### Archivos creados

| Archivo | Propósito |
|---|---|
| `tests/__init__.py` | Paquete de tests |
| `tests/conftest.py` | Fixtures compartidos, override de DB y auth |
| `tests/test_auth.py` | 9 tests de autenticación |
| `tests/test_payments.py` | 7 tests de `/payments/confirm` y `/payments/status` |
| `tests/test_webhooks.py` | 6 tests de webhooks Stripe |

---

## 3. Endpoints modificados

### 3.1 Endpoints que ahora requieren JWT

| Endpoint | Método | Permiso requerido | Cambio |
|---|---|---|---|
| `/payments/init` | POST | `billing.create_checkout` | Se agregó `require_permission` |
| `/payments/subscriptions/{id}/cancel` | POST | `billing.cancel_subscription` | Se agregó `require_permission` |
| `/subscriptions/change-plan` | POST | `billing.change_subscription_plan` | Se agregó `require_permission` |
| `/subscriptions/preview-plan-change` | POST | `billing.change_subscription_plan` | Se agregó `require_permission` |
| `/subscriptions/test-access/{user_id}` | GET | `billing.view_subscription` | Se agregó `require_permission` |
| `/plans/create-stripe` | POST | `billing.register_subscription` | Se agregó `require_permission` |
| `/plans/register` | POST | `billing.register_subscription` | Se agregó `require_permission` |
| `/plans/{plan_code}` | PATCH | `billing.register_subscription` | Se agregó `require_permission` |

### 3.2 Endpoints nuevos

| Endpoint | Método | Permiso | Propósito |
|---|---|---|---|
| `/payments/confirm` | POST | `billing.view_payments` | Consulta estado real de sesión Stripe (solo lectura) |
| `/payments/status/{subscription_id}` | GET | `billing.view_subscription` | Consulta estado local de suscripción (solo lectura) |

### 3.3 Endpoints NO modificados

| Endpoint | Método | Razón |
|---|---|---|
| `/webhooks/stripe` | POST | Usa firma Stripe, NO JWT |
| `/plans/` | GET | Lectura pública de planes activos |
| `/subscriptions/checkout` | POST | Ya tenía JWT desde antes |
| `/health`, `/` | GET | Públicos |

---

## 4. Funciones modificadas

| Función | Archivo | Cambio |
|---|---|---|
| `init_subscription` | `routers/payments.py:30` | Agregado `require_permission(Permission.CREATE_CHECKOUT)` |
| `cancel_subscription` | `routers/payments.py:92` | Agregado `require_permission(Permission.CANCEL_SUBSCRIPTION)` |
| `change_plan` | `routers/subscriptions.py:174` | Agregado `require_permission(Permission.CHANGE_SUBSCRIPTION_PLAN)` |
| `preview_plan_change` | `routers/subscriptions.py:341` | Agregado `require_permission(Permission.CHANGE_SUBSCRIPTION_PLAN)` |
| `test_access` | `routers/subscriptions.py:447` | Agregado `require_permission(Permission.VIEW_SUBSCRIPTION)` |
| `create_plan_stripe` | `routers/plans.py:41` | Agregado `require_permission(Permission.REGISTER_SUBSCRIPTION)` |
| `register_plan` | `routers/plans.py:82` | Agregado `require_permission(Permission.REGISTER_SUBSCRIPTION)` |
| `update_plan_local` | `routers/plans.py:117` | Agregado `require_permission(Permission.REGISTER_SUBSCRIPTION)` |
| `handle_checkout_completed` | `routers/webhooks.py:212` | Validación `payment_status == "paid"` y `session_status == "complete"` |
| `notify_main_app` | `routers/webhooks.py:105` | Reintentos (3) con backoff, cola de fallidos, validación `MAIN_APP_BASE` |
| `_save_failed_notification` | `routers/webhooks.py:62` | **Nueva** — guarda en `WebhookNotificationQueue` |
| `confirm_payment` | `routers/payments.py:141` | **Nueva** — consulta estado de sesión Stripe |
| `subscription_status` | `routers/payments.py:211` | **Nueva** — consulta estado local |

---

## 5. Qué problema corregía cada cambio

| Cambio | Problema | Síntoma |
|---|---|---|
| JWT en `/payments/init` | Cualquiera podía crear suscripciones y sesiones Stripe | Ataque de creación masiva |
| JWT en `/payments/subscriptions/{id}/cancel` | Cualquiera podía cancelar suscripciones ajenas | Sabotaje de suscripciones |
| JWT en `/subscriptions/change-plan` | Cualquiera podía cambiar planes | Fraude de upgrade |
| JWT en `/subscriptions/preview-plan-change` | Cualquiera podía consultar datos financieros | Fuga de información |
| JWT en `/plans/create-stripe`, `/register`, `/{code}` | Cualquiera podía crear/modificar planes | Manipulación de precios |
| `payment_status != "paid"` → no activar | Stripe envía `checkout.session.completed` incluso si el pago no se completa | Activación falsa de suscripciones |
| `session_status != "complete"` → no activar | Sesión puede completarse sin pago exitoso | Mismo riesgo |
| Reintentos en `notify_main_app` | Si Django falla, la notificación se pierde | Suscripciones huérfanas (activas en billing, no en Django) |
| Cola `WebhookNotificationQueue` | No había forma de recuperar notificaciones fallidas | Pérdida permanente del evento |
| `/payments/confirm` | Django llamaba a un endpoint que no existía (404) | Error en pantalla de éxito |
| `/payments/status/{id}` | No había forma de consultar estado sin Stripe | Dependencia excesiva de Stripe API |

---

## 6. Qué comportamiento debería tener ahora la API

### 6.1 `POST /payments/init`

**Antes:** Cualquiera podía crear suscripciones y sesiones Stripe.
**Después:** Requiere JWT con permiso `billing.create_checkout`. Sin token → `403 Forbidden`.

### 6.2 `POST /payments/confirm` (NUEVO)

- Consulta el estado real de la sesión en Stripe vía `stripe.checkout.Session.retrieve(session_id)`
- **NO modifica la base de datos** — solo lectura
- Si la sesión tiene `mode=subscription` y `subscription`, también consulta el estado de la suscripción en Stripe
- Retorna uno de: `paid`, `active`, `unpaid`, `pending`, `expired`, `not_found`
- Requiere JWT con permiso `billing.view_payments`

### 6.3 `GET /payments/status/{subscription_id}` (NUEVO)

- Consulta el estado local de la suscripción en la BD del billing service
- **NO consulta Stripe**
- Retorna: `id`, `user_id`, `plan_code`, `status`, fechas, `cancel_at_period_end`
- Requiere JWT con permiso `billing.view_subscription`

### 6.4 `POST /subscriptions/checkout`

Sin cambios en la lógica de negocio. Ya requería JWT desde antes. Ahora los imports de seguridad están consolidados.

### 6.5 `POST /webhooks/stripe`

- La validación de firma (`stripe.Webhook.construct_event`) ya existía y no se modificó
- **Nuevo:** `handle_checkout_completed` verifica `payment_status == "paid"` y `status == "complete"` antes de activar
- **Nuevo:** `notify_main_app` reintenta 3 veces con backoff y guarda en cola si falla
- Los demás eventos (`invoice.payment_succeeded`, `customer.subscription.deleted`, etc.) no cambiaron su lógica

### 6.6 Creación de Stripe Checkout Session

Sin cambios. Se usa `mode="payment"` para `/payments/init` y `mode="subscription"` para `/subscriptions/checkout`. Las URLs `success_url` y `cancel_url` vienen de variables de entorno (`STRIPE_SUCCESS_URL`, `STRIPE_CANCEL_URL`).

### 6.7 Stripe Customer

No se crea ni modifica Stripe Customer explícitamente. Stripe lo maneja automáticamente.

### 6.8 Stripe Subscription

- Se asigna `stripe_subscription_id` en `handle_checkout_completed` cuando `mode="subscription"`
- Se sincroniza en `handle_subscription_updated`

### 6.9 `success_url` y `cancel_url`

No se modificaron. Vienen de las variables de entorno `STRIPE_SUCCESS_URL` y `STRIPE_CANCEL_URL`. No hay hardcode de `http://127.0.0.1:8001` en el código.

### 6.10 Validación de `Stripe-Signature`

No se modificó. Usa `stripe.Webhook.construct_event()` con el secreto de `STRIPE_ENDPOINT_SECRET`.

### 6.11 `notify_main_app`

**Antes:**
- Sin retorno
- Sin reintentos
- Sin validación de `MAIN_APP_BASE`
- Sin cola de fallidos
- Loggeaba error y terminaba

**Después:**
- Retorna `bool` (True si éxito, False si falló)
- 3 reintentos con backoff exponencial (2s, 4s, 8s)
- Timeout 10s por intento
- Valida que `MAIN_APP_BASE` esté configurado
- Si todos fallan, guarda en `WebhookNotificationQueue`
- Log sin datos sensibles

### 6.12 Llamada a Django `/checkout/complete/`

Sin cambios en la URL ni en el payload. Se envía `X-Webhook-Token` si `COBRANZA_WEBHOOK_SECRET` está configurado.

### 6.13 `X-Webhook-Token`

Sin cambios en su construcción. Se envía en header `X-Webhook-Token` cuando `settings.COBRANZA_WEBHOOK_SECRET` no es `None`. Se agregó un warning log si no está configurado.

### 6.14 Autenticación JWT

Se agregó `require_permission()` a 8 endpoints adicionales. El webhook Stripe sigue siendo el único endpoint mutante sin JWT (usa firma Stripe).

### 6.15 `payment_status`

**Antes:** No se verificaba.
**Después:** `handle_checkout_completed` verifica `payment_status == "paid"` y `status == "complete"`. Si no cumple, no activa ni notifica.

### 6.16 `checkout.session.completed`

**Antes:** Activaba subscription y notificaba a Django siempre.
**Después:** Solo activa y notifica si `payment_status == "paid"` y `status == "complete"`.

### 6.17 `invoice.paid`, `invoice.payment_failed`, `customer.subscription.updated`, `customer.subscription.deleted`

Sin cambios en la lógica de negocio. Solo se eliminaron imports locales redundantes de `engine` para que usen el import del módulo.

---

## 7. Flujos que deberían probarse manualmente

### 7.1 Django solicita iniciar checkout

1. Django hace `POST /api/pagos/subscriptions/checkout?user_id=1&plan_code=CFDI_PRO` con JWT
2. API responde `{checkout_url, subscription_id, reused: false}`
3. Django redirige al usuario a Stripe

**Esperado:** Suscripción creada en estado `pending`, sesión Stripe creada.

### 7.2 API crea sesión Stripe

1. `stripe.checkout.Session.create()` con `mode="subscription"`
2. Metadata incluye `subscription_id`, `user_id`
3. `success_url` y `cancel_url` de variables de entorno

**Esperado:** Sesión Stripe creada con metadata correcta.

### 7.3 Usuario paga correctamente

1. Usuario completa pago en Stripe Checkout
2. Stripe redirige a `success_url` (Django)
3. Stripe envía `checkout.session.completed` con `payment_status=paid`

**Esperado:** Webhook recibido, suscripción activada, Django notificado.

### 7.4 Stripe envía webhook `checkout.session.completed`

1. Stripe hace `POST /api/pagos/webhooks/stripe` con firma
2. API valida firma → `stripe.Webhook.construct_event()`
3. API verifica `payment_status == "paid"` y `status == "complete"`
4. API: `subscription.status = "active"`, asigna `stripe_subscription_id`
5. API: `notify_main_app()` → POST a Django `/checkout/complete/`

**Esperado:** Suscripción activa, notificación enviada.

### 7.5 API valida firma Stripe

1. Sin `stripe-signature` header → 400 "Missing Stripe signature"
2. Firma inválida → 400 "Invalid signature"
3. Firma válida → procesa evento

**Esperado:** Solo eventos con firma válida se procesan.

### 7.6 API notifica a Django `/checkout/complete/`

1. Payload: `{user_id, billing_code, plan_code, subscription_id, plan_id}`
2. Header: `X-Webhook-Token: <COBRANZA_WEBHOOK_SECRET>`
3. Reintentos: 3 intentos con backoff (2s, 4s, 8s)
4. Timeout: 10s por intento

**Esperado:** Django recibe notificación. Si responde OK, se completa el flujo.

### 7.7 Django no responde o responde error

1. `notify_main_app` reintenta 3 veces
2. Si todos fallan, guarda en `WebhookNotificationQueue`
3. La suscripción en billing API queda `active`
4. `User_Service` en Django **no se crea** hasta que se reprocese la cola

**Esperado:** No se pierde el evento, queda encolado para reprocesamiento.

### 7.8 Usuario cancela checkout

1. Stripe redirige a `cancel_url` (Django)
2. Stripe NO envía webhook de cancelación
3. La suscripción en billing API queda `pending`

**Esperado:** Suscripción `pending` no se activa. Sin cambios.

### 7.9 Usuario llega a `success_url`

1. Django recibe GET con `session_id`
2. Django renderiza página de éxito
3. Django hace `POST /api/pagos/payments/confirm` con JWT
4. API consulta Stripe, retorna estado actual

**Esperado:** Usuario ve pantalla de éxito.

### 7.10 Django consulta `/payments/confirm` o estado del pago

1. `POST /api/pagos/payments/confirm` con `{session_id}`
2. API llama a `stripe.checkout.Session.retrieve(session_id)`
3. Retorna estado sin modificar BD
4. Estados posibles: `paid`, `active`, `unpaid`, `pending`, `expired`, `not_found`

**Esperado:** Consulta de solo lectura, no activa nada.

### 7.11 Pago recurrente falla

1. Stripe envía `invoice.payment_failed` con `billing_reason=subscription_cycle`
2. API loggea el fallo (sin cambios en este handler)
3. Stripe envía `customer.subscription.updated` con `status=past_due`
4. API actualiza `subscription.status = "past_due"`

**Esperado:** Status actualizado en BD, Stripe reintenta automáticamente.

### 7.12 Suscripción queda `past_due`

1. `puede_acceder()` retorna `True` para `past_due` (Stripe está reintentando)
2. Si Stripe no logra cobrar en ~14 días, envía `customer.subscription.deleted`
3. API actualiza `subscription.status = "canceled"`

**Esperado:** Acceso permitido durante período de gracia.

### 7.13 Suscripción se cancela

1. Stripe envía `customer.subscription.deleted`
2. API actualiza `subscription.status = "canceled"`
3. API actualiza `subscription.canceled_at`

**Esperado:** Suscripción marcada como cancelada en BD.

---

## 8. Pruebas automatizadas agregadas

### 8.1 `tests/test_auth.py` (9 tests)

| Test | Verifica |
|---|---|
| `test_payments_init_sin_jwt_rechazado` | `/payments/init` sin JWT → 403 |
| `test_payments_init_con_jwt_aceptado` | `/payments/init` con JWT → 200/201/404 |
| `test_cancel_subscription_sin_jwt_rechazado` | `/payments/subscriptions/{id}/cancel` sin JWT → 403 |
| `test_change_plan_sin_jwt_rechazado` | `/subscriptions/change-plan` sin JWT → 403 |
| `test_preview_plan_change_sin_jwt_rechazado` | `/subscriptions/preview-plan-change` sin JWT → 403 |
| `test_plans_create_stripe_sin_jwt_rechazado` | `/plans/create-stripe` sin JWT → 403 |
| `test_plans_register_sin_jwt_rechazado` | `/plans/register` sin JWT → 403 |
| `test_plans_update_sin_jwt_rechazado` | `/plans/{code}` PATCH sin JWT → 403 |
| `test_webhook_stripe_no_requiere_jwt` | `/webhooks/stripe` sin JWT → 400 (signature), no 403 |

### 8.2 `tests/test_payments.py` (7 tests)

| Test | Verifica |
|---|---|
| `test_confirm_payment_session_pagado` | `/payments/confirm` con session paid → `status: paid` |
| `test_confirm_payment_session_no_pagado` | `/payments/confirm` con session unpaid → `status: unpaid` |
| `test_confirm_payment_session_no_existe` | `/payments/confirm` con session inexistente → `status: not_found` |
| `test_confirm_payment_sin_session_id` | `/payments/confirm` sin session_id → 400 |
| `test_confirm_payment_sin_jwt_rechazado` | `/payments/confirm` sin JWT → 403 |
| `test_confirm_no_activa_planes` | `/payments/confirm` **no** modifica BD ni activa |
| `test_subscription_status_retorna_estado` | `/payments/status/{id}` funciona |

### 8.3 `tests/test_webhooks.py` (6 tests)

| Test | Verifica |
|---|---|
| `test_webhook_stripe_sin_firma` | Webhook sin firma → 400 |
| `test_webhook_stripe_firma_invalida` | Webhook con firma inválida → 400 |
| `test_webhook_checkout_completed_no_pagado_no_activa` | `payment_status=unpaid` → no activa, no notifica |
| `test_webhook_checkout_completed_pagado_si_notifica` | `payment_status=paid` → activa y notifica |
| `test_webhook_payload_malformado` | Payload inválido → 400 |
| `test_notify_main_app_reintenta_si_falla` | `notify_main_app` hace 3 intentos si Django falla |

---

## 9. Riesgos que siguen pendientes

| Riesgo | Impacto | Notas |
|---|---|---|
| **Django no envía JWT a `/payments/init`** | 🔴 Ruptura de flujo de one-time payments | Si Django no envía JWT, este endpoint devolverá 403. Hay que verificar que Django envíe JWT también para pagos únicos. |
| **`notify_main_app` solo se llama en checkout** | 🟡 Renovaciones, cancelaciones, past_due no notifican a Django | Django no se entera de cambios post-checkout. Para Fase 2. |
| **Sin job de reconciliación** | 🟡 La cola `WebhookNotificationQueue` se llena sin procesar | No hay scheduler que reprocese los fallidos. Para Fase 2. |
| **`handle_invoice_payment_failed` no actualiza status** | 🟡 No se marca `past_due` inmediatamente | Stripe lo resuelve con `customer.subscription.updated`, pero hay ventana de inconsistencia. |
| **`COBRANZA_WEBHOOK_SECRET` truncado en `.env`** | 🟡 El secreto termina en `>`, posiblemente inválido | Django rechazaría la notificación. Hay que corregir el valor manualmente. |
| **Sin verificación de `stripe_customer_id`** | 🟡 No se persiste el Customer ID de Stripe | Dificulta diagnosis de problemas en Stripe. |
| **Sin idempotencia por `checkout_session_id`** | 🟡 Múltiples eventos `checkout.session.completed` podrían activar múltiples veces | Stripe garantiza entrega, pero no deduplicación. |

---

## 10. Qué NO se corrigió todavía

| Tema | Razón | Pendiente para |
|---|---|---|
| Notificar a Django en renovaciones, cancelaciones, cambios de plan | Scope limitado a Fase 1 | Fase 2 |
| Job de reconciliación para `WebhookNotificationQueue` | Requiere scheduler externo | Fase 2 |
| `handle_invoice_payment_failed` → status `past_due` | Scope limitado a checkout | Fase 2 |
| Migración Alembic para `WebhookNotificationQueue` | Se usa `create_all()` por ahora | Fase 2 |
| Validar `stripe_customer_id` | No impacta checkout inmediato | Fase 3 |
| Idempotencia por `checkout_session_id` | Stripe raramente duplica eventos | Fase 3 |
| Endpoints protegidos con rate limiting | No existía antes | Fase 4 |
| Logging estructurado (JSON) | No impacta seguridad inmediata | Fase 4 |

---

## 11. Comandos recomendados para probar

```bash
# Activar venv
cd api_cobranza
source .venv/bin/activate

# Instalar dependencias (si no está hecho)
pip install -r requirements.txt

# Ejecutar tests unitarios
python -m pytest tests/ -v

# Ejecutar tests con cobertura
python -m pytest tests/ --cov=app -v

# Iniciar servidor en desarrollo
uvicorn app.main:app --reload --port 8080

# Probar health check
curl http://localhost:8080/api/pagos/health

# Probar endpoint sin JWT (debe fallar con 403)
curl -X POST http://localhost:8080/api/pagos/payments/init \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "plan_code": "CFDI_PRO"}'

# Probar endpoint con JWT simulado (requiere JWT real de Django)
curl -X POST http://localhost:8080/api/pagos/payments/init \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT>" \
  -d '{"user_id": 1, "plan_code": "CFDI_PRO"}'

# Probar /payments/confirm
curl -X POST http://localhost:8080/api/pagos/payments/confirm \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT>" \
  -d '{"session_id": "cs_test_abc123"}'

# Simular webhook Stripe (requiere Stripe CLI)
stripe trigger checkout.session.completed

# Ver cola de notificaciones fallidas (SQLite directo)
sqlite3 billing.db "SELECT * FROM webhooknotificationqueue;"
```

---

## 12. Variables de entorno necesarias

### Requeridas (sin cambios)

| Variable | Ejemplo | Propósito |
|---|---|---|
| `STRIPE_SECRET_KEY` | `sk_test_...` | API key secret de Stripe |
| `STRIPE_PUBLISHABLE_KEY` | `pk_test_...` | API key pública de Stripe |
| `STRIPE_ENDPOINT_SECRET` | `whsec_...` | Secreto para validar webhooks Stripe |
| `STRIPE_SUCCESS_URL` | `http://127.0.0.1:8001/checkout/success/?session_id={CHECKOUT_SESSION_ID}` | URL post-pago exitoso |
| `STRIPE_CANCEL_URL` | `http://127.0.0.1:8001/checkout/cancel/` | URL post-cancelación |
| `DATABASE_URL` | `postgresql+psycopg://user:pass@host:5432/db` | Conexión a BD |
| `JWT_PUBLIC_KEY` | `-----BEGIN PUBLIC KEY-----\n...` | RSA public key para validar JWT |
| `JWT_ALGORITHM` | `RS256` | Algoritmo JWT |
| `JWT_ISSUER` | `https://app.factupid.com` | Issuer del JWT |
| `JWT_AUDIENCE` | `billing-api` | Audience del JWT |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | Expiración del token |

### Opcionales (sin cambios funcionales, pero ahora con warning si faltan)

| Variable | Ejemplo | Propósito |
|---|---|---|
| `MAIN_APP_BASE` | `http://127.0.0.1:8001` | URL base de Django. `notify_main_app` falla gracefulmente si no está configurado. |
| `COBRANZA_WEBHOOK_SECRET` | `63af5d...` | Secreto compartido con Django. Ahora emite warning si no está configurado. |

### ⚠️ Problema conocido en `.env`

`COBRANZA_WEBHOOK_SECRET` aparece truncado con `>` al final:
```
COBRANZA_WEBHOOK_SECRET="63af5dde9a404a791b6179a826d42ee9659769cac649368e9705bc>"
```
El secreto real debería ser un hash hexadecimal sin `>` final. Este valor debe corregirse manualmente para que la comunicación con Django funcione.

---

## Tabla de cambios por flujo

| Flujo | Antes | Después | Endpoint | Función | Resultado esperado | Cómo probarlo | Riesgo pendiente |
|---|---|---|---|---|---|---|---|
| **Iniciar checkout (pago único)** | Sin auth | Requiere JWT `billing.create_checkout` | `POST /payments/init` | `init_subscription` | 201 con checkout_url si hay JWT; 403 si no | Llamar sin JWT → 403; con JWT → 201 | Django debe enviar JWT (verificar) |
| **Iniciar checkout (suscripción)** | Ya tenía JWT | Sin cambios | `POST /subscriptions/checkout` | `start_subscription` | 201 con checkout_url | Usar JWT de Django | — |
| **Activar por webhook** | Activaba siempre | Solo si `payment_status=paid` y `status=complete` | `POST /webhooks/stripe` | `handle_checkout_completed` | Solo activa si realmente pagó | Stripe CLI con evento unpaid | — |
| **Notificar a Django** | Sin reintentos | 3 reintentos (2s,4s,8s) + cola | — | `notify_main_app` | Reintenta, encola si falla | Apagar Django y hacer checkout | Falta job de reprocesamiento |
| **Consultar estado post-pago** | 404 | Endpoint nuevo de solo lectura | `POST /payments/confirm` | `confirm_payment` | Retorna estado real sin activar | Llamar con session_id | — |
| **Consultar estado local** | No existía | Endpoint nuevo | `GET /payments/status/{id}` | `subscription_status` | Retorna estado local | Llamar con subscription_id | — |
| **Cancelar suscripción** | Sin auth | Requiere JWT `billing.cancel_subscription` | `POST /payments/subscriptions/{id}/cancel` | `cancel_subscription` | 403 sin JWT | Llamar sin JWT | — |
| **Cambiar plan** | Sin auth | Requiere JWT `billing.change_subscription_plan` | `POST /subscriptions/change-plan` | `change_plan` | 403 sin JWT | Llamar sin JWT | — |
| **Vista previa cambio plan** | Sin auth | Requiere JWT `billing.change_subscription_plan` | `POST /subscriptions/preview-plan-change` | `preview_plan_change` | 403 sin JWT | Llamar sin JWT | — |
| **Crear plan en Stripe** | Sin auth | Requiere JWT `billing.register_subscription` | `POST /plans/create-stripe` | `create_plan_stripe` | 403 sin JWT | Llamar sin JWT | — |
| **Registrar plan existente** | Sin auth | Requiere JWT `billing.register_subscription` | `POST /plans/register` | `register_plan` | 403 sin JWT | Llamar sin JWT | — |
| **Actualizar plan** | Sin auth | Requiere JWT `billing.register_subscription` | `PATCH /plans/{code}` | `update_plan_local` | 403 sin JWT | Llamar sin JWT | — |
| **Test de acceso** | Sin auth | Requiere JWT `billing.view_subscription` | `GET /subscriptions/test-access/{user_id}` | `test_access` | 403 sin JWT | Llamar sin JWT | — |
