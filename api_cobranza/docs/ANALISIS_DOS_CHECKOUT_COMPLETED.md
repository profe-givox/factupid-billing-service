# Análisis: Dos `checkout_completed` durante una suscripción

> **NO MODIFICAR** en esta fase. Solo análisis.

## 1) ¿Qué Stripe event genera cada uno?

| Fila | Evento Stripe | Handler | Momento típico |
|---|---|---|---|
| A | `checkout.session.completed` | `handle_checkout_completed(session_data, event)` | Al finalizar sesión de Checkout. |
| B | `invoice.payment_succeeded` con `billing_reason = "subscription_create"` | `handle_subscription_payment(invoice, event)` | Al pagarse la factura inicial de la suscripción. |

## 2) ¿Qué handler crea cada fila?

- A: crea `WebhookNotificationQueue` con `event_type="checkout_completed"`, `notification_key="{stripe_event_id_checkout}:checkout_completed"`. Si faltan fechas en la Subscription, puede omitir `period_start/period_end/date_cutoff` y **no notifica inmediatamente**.
- B: tras crear `Payment`, actualizar fechas desde `subscription_line.period`, crea `WebhookNotificationQueue` con `event_type="checkout_completed"`, `notification_key="{stripe_event_id_invoice}:checkout_completed"`. Encola con fechas reales y notifica a Django.

## 3) ¿Por qué uno puede contener fechas y el otro no?

- A: lee la Subscription tal como está en BD en ese momento. Frecuentemente las fechas aún no están fijadas.
- B: toma fechas **reales** de la factura (`subscription_line.period.start/end`) y las asigna a la Subscription.

## 4) ¿Misma transición o eventos distintos?

Son **eventos distintos** de Stripe. Representan la misma transición de negocio, pero con **momentos, fuentes de verdad y `stripe_event_id` diferentes**. Por tanto tienen `notification_key` distintos.

## 5) Consecuencias de consolidarlos

- **Riesgo:** romper idempotencia/orden, perder la fuente fiable (factura) para fechas, afectar lógica de reparación.
- **Beneficio:** evitar duplicado semántico.
- **Recomendación:** **NO consolidar ahora**. Ya se verificó que no dañan `date_cutoff` ni estado final. Documentado como deuda técnica.

## Archivos involucrados
- `app/routers/webhooks.py`: `handle_checkout_completed`, `handle_subscription_payment`
- `app/routers/webhooks.py`: `_build_notification_key`, `enqueue_notification`
