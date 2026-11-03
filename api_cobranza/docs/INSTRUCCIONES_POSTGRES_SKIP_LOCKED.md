# Cómo ejecutar la prueba PostgreSQL real (SKIP LOCKED)

## Requisitos
- PostgreSQL accesible (NO producción)
- Base dedicada de pruebas (ej. `billing_test`)
- Usuario con permisos para crear/drop tablas

## Configuración
Usar `TEST_POSTGRES_URL` con `postgresql+psycopg`:
```bash
export TEST_POSTGRES_URL=postgresql+psycopg://user:pass@host:5432/billing_test
```

## Ejecutar
```bash
cd api_cobranza
.venv/bin/python -m pytest tests/integration/test_queue_processor_postgres_skip_locked.py -v
```

## Qué valida
- Fila bloqueada por otra transacción con `SELECT ... FOR UPDATE` no es reclamada por `claim_pending_notifications` (SKIP LOCKED)
- Fila libre SÍ es reclamada

## Notas
- SQLite NO demuestra SKIP LOCKED
- El test crea tablas con `SQLModel.metadata.create_all`
- Se usa transacción bloqueante en el test para simular worker A
- Si falla por permisos/conexión, revisar URL y firewall
