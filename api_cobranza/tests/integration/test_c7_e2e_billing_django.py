import hashlib
import hmac
import json
import os
import subprocess
import sys
import threading
import time
from datetime import date, datetime, timezone
from pathlib import Path

import httpx
import pytest
from sqlalchemy import text, update
from sqlalchemy.engine import make_url
from sqlmodel import Session, SQLModel, select

from app.db.session import engine
from app.models.payment import Payment, WebhookNotificationQueue
from app.models.plan import Plan
from app.models.subscription import Subscription

BASE_DIR = Path(__file__).resolve().parents[2]
INTEGRATION_DIR = Path(__file__).resolve().parent
DJANGO_ROOT = Path(
    os.environ.get("C7_DJANGO_ROOT", BASE_DIR.parent.parent / "factupid" / "factupid")
).resolve()
DJANGO_PYTHON = os.environ.get(
    "C7_DJANGO_PYTHON", str(DJANGO_ROOT.parent / "myenv" / "bin" / "python")
)
BILLING_URL = os.environ.get("C7_BILLING_URL", "http://127.0.0.1:18000").rstrip("/")
DJANGO_URL = os.environ.get("C7_DJANGO_URL", "http://127.0.0.1:18001").rstrip("/")
WEBHOOK_SECRET = os.environ.get("C7_WEBHOOK_SECRET", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_ENDPOINT_SECRET_C7", "")
DJANGO_DB_NAME = os.environ.get("C7_DJANGO_DB_NAME", "")
DELAY_FILE = Path(os.environ.get("C7_DELAY_FILE", "/tmp/opencode/c7/delay_seconds"))
REQUEST_LOG = Path(os.environ.get("C7_REQUEST_LOG", "/tmp/opencode/c7/requests.log"))
LOG_DIR = Path("/tmp/opencode/c7")

pytestmark = pytest.mark.skipif(
    os.environ.get("C7_E2E") != "1",
    reason="C7_E2E no configurado (integración E2E Billing/Django)",
)


class ServerManager:
    def __init__(self):
        self.billing = None
        self.django = None
        self.billing_log = None
        self.django_log = None

    def billing_env(self):
        env = os.environ.copy()
        env.update(
            {
                "DATABASE_URL": os.environ["DATABASE_URL"],
                "MAIN_APP_BASE": DJANGO_URL,
                "COBRANZA_WEBHOOK_SECRET": WEBHOOK_SECRET,
                "STRIPE_ENDPOINT_SECRET": STRIPE_WEBHOOK_SECRET,
                "STRIPE_SECRET_KEY": "sk_test_c7_only",
                "STRIPE_PUBLISHABLE_KEY": "pk_test_c7_only",
                "ENABLE_OVERAGE_REPORTING_SCHEDULER": "false",
                "DISCORD_ALERTS_ENABLED": "false",
            }
        )
        return env

    def django_env(self):
        env = os.environ.copy()
        env.update(
            {
                "PYTHONPATH": f"{INTEGRATION_DIR}:{DJANGO_ROOT}",
                "DJANGO_SETTINGS_MODULE": "c7_django_settings",
                "C7_DJANGO_DB_NAME": DJANGO_DB_NAME,
                "C7_WEBHOOK_SECRET": WEBHOOK_SECRET,
                "C7_DELAY_FILE": str(DELAY_FILE),
                "C7_REQUEST_LOG": str(REQUEST_LOG),
            }
        )
        return env

    def start_billing(self):
        if self.billing and self.billing.poll() is None:
            return
        self.billing_log = open(LOG_DIR / "billing-server.log", "ab")
        self.billing = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "app.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                "18000",
                "--lifespan",
                "off",
                "--log-level",
                "warning",
            ],
            cwd=BASE_DIR,
            env=self.billing_env(),
            stdout=self.billing_log,
            stderr=subprocess.STDOUT,
        )
        _wait_http(f"{BILLING_URL}/health", expected={200})

    def stop_billing(self):
        self.billing = _stop_process(self.billing)

    def start_django(self):
        if self.django and self.django.poll() is None:
            return
        self.django_log = open(LOG_DIR / "django-server.log", "ab")
        self.django = subprocess.Popen(
            [
                DJANGO_PYTHON,
                "manage.py",
                "runserver",
                "127.0.0.1:18001",
                "--noreload",
                "--verbosity",
                "0",
            ],
            cwd=DJANGO_ROOT,
            env=self.django_env(),
            stdout=self.django_log,
            stderr=subprocess.STDOUT,
        )
        _wait_http(f"{DJANGO_URL}/checkout/complete/", expected={405})

    def stop_django(self):
        self.django = _stop_process(self.django)

    def ensure_all(self):
        self.start_billing()
        self.start_django()

    def stop_all(self):
        self.stop_billing()
        self.stop_django()
        for log in (self.billing_log, self.django_log):
            if log:
                log.close()


def _stop_process(proc):
    if not proc:
        return None
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=8)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
    return None


def _wait_http(url, expected):
    deadline = time.time() + 25
    last_error = None
    while time.time() < deadline:
        try:
            response = httpx.get(url, timeout=2)
            if response.status_code in expected:
                return
        except Exception as exc:
            last_error = exc
        time.sleep(0.1)
    raise RuntimeError(f"Servidor no disponible en {url}: {last_error}")


def _assert_test_database():
    billing_name = make_url(os.environ["DATABASE_URL"]).database or ""
    if "test" not in billing_name.lower():
        raise RuntimeError(f"Base Billing no parece de pruebas: {billing_name}")
    if "test" not in DJANGO_DB_NAME.lower():
        raise RuntimeError(f"Base Django no parece de pruebas: {DJANGO_DB_NAME}")
    if not WEBHOOK_SECRET or not STRIPE_WEBHOOK_SECRET:
        raise RuntimeError("Faltan secretos de prueba C7")


def _django_cmd(*args):
    result = subprocess.run(
        [DJANGO_PYTHON, "c7_django_helper.py", *args],
        cwd=INTEGRATION_DIR,
        env=ServerManager().django_env(),
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Django helper falló: {result.returncode}\nSTDOUT={result.stdout}\nSTDERR={result.stderr}"
        )
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    return json.loads(lines[-1])


def _run_worker(max_items=20):
    env = ServerManager().billing_env()
    result = subprocess.run(
        [sys.executable, "-m", "tests.integration.c7_billing_worker", "--max-items", str(max_items)],
        cwd=BASE_DIR,
        env=env,
        capture_output=True,
        text=True,
        timeout=90,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Worker falló: {result.returncode}\nSTDOUT={result.stdout}\nSTDERR={result.stderr}"
        )
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    return json.loads(lines[-1])


def _reset_billing_data():
    with engine.begin() as connection:
        connection.execute(
            text(
                "TRUNCATE TABLE payment, webhooknotificationqueue, subscription, plan "
                "RESTART IDENTITY CASCADE"
            )
        )
    with Session(engine) as db:
        pro = Plan(
            code="CFDI_PRO",
            name="PRO",
            price=299,
            currency="MXN",
            interval="month",
            billing_type="subscription",
            stripe_price_id="price_c7_pro",
            stripe_product_id="prod_c7_pro",
            is_active=True,
        )
        free = Plan(
            code="CFDI_FREE",
            name="FREE",
            price=0,
            currency="MXN",
            interval=None,
            billing_type="one_time",
            is_active=True,
        )
        db.add(pro)
        db.add(free)
        db.commit()
        db.refresh(pro)
        db.refresh(free)
        sub_pro = Subscription(user_id=1, plan_id=pro.id, status="pending", provider="stripe")
        sub_repurchase = Subscription(
            user_id=1, plan_id=pro.id, status="pending", provider="stripe"
        )
        sub_free = Subscription(user_id=2, plan_id=free.id, status="pending", provider="stripe")
        db.add(sub_pro)
        db.add(sub_repurchase)
        db.add(sub_free)
        db.commit()
        db.refresh(sub_pro)
        db.refresh(sub_repurchase)
        db.refresh(sub_free)
        return {
            "pro_plan_id": pro.id,
            "free_plan_id": free.id,
            "sub_pro": sub_pro.id,
            "sub_repurchase": sub_repurchase.id,
            "sub_free": sub_free.id,
        }


def _queue_rows():
    with Session(engine) as db:
        items = db.exec(select(WebhookNotificationQueue).order_by(WebhookNotificationQueue.id)).all()
        return [
            {
                "id": item.id,
                "event_type": item.event_type,
                "status": item.status,
                "retry_count": item.retry_count,
                "max_retries": item.max_retries,
                "notification_key": item.notification_key,
                "source_event_id": item.source_event_id,
                "payload": item.payload,
                "next_retry_at": item.next_retry_at,
                "lease_expires_at": item.lease_expires_at,
                "last_error": item.last_error,
            }
            for item in items
        ]


def _queue_by_key(key):
    rows = [row for row in _queue_rows() if row["notification_key"] == key]
    assert len(rows) == 1, rows
    return rows[0]


def _force_retry(key):
    with Session(engine) as db:
        item = db.exec(
            select(WebhookNotificationQueue).where(
                WebhookNotificationQueue.notification_key == key
            )
        ).first()
        assert item is not None
        item.status = "pending"
        item.next_retry_at = datetime.now(timezone.utc) - timezone_resolution()
        item.lease_expires_at = None
        db.add(item)
        db.commit()


def timezone_resolution():
    from datetime import timedelta

    return timedelta(seconds=1)


def _signature(body: bytes):
    timestamp = int(time.time())
    signed = f"{timestamp}.".encode() + body
    digest = hmac.new(
        STRIPE_WEBHOOK_SECRET.encode(), signed, hashlib.sha256
    ).hexdigest()
    return f"t={timestamp},v1={digest}"


def _send_event(event_type, obj, event_id, created=None):
    event = {
        "id": event_id,
        "type": event_type,
        "created": int(created if created is not None else time.time()),
        "data": {"object": obj},
    }
    body = json.dumps(event, separators=(",", ":")).encode()
    response = httpx.post(
        f"{BILLING_URL}/webhooks/stripe",
        content=body,
        headers={
            "Content-Type": "application/json",
            "stripe-signature": _signature(body),
        },
        timeout=60,
    )
    assert response.status_code == 200, response.text
    return response


def _checkout_event(subscription_id, user_id, billing_code, stripe_sub_id, event_id=None):
    return _send_event(
        "checkout.session.completed",
        {
            "id": f"cs_{event_id or int(time.time() * 1000)}",
            "metadata": {
                "subscription_id": str(subscription_id),
                "user_id": str(user_id),
                "billing_code": billing_code,
            },
            "payment_status": "paid",
            "status": "complete",
            "mode": "subscription" if billing_code != "CFDI_FREE" else "payment",
            "subscription": stripe_sub_id,
            "customer": "cus_c7",
            "amount_total": 29900,
            "currency": "mxn",
        },
        event_id=event_id or f"evt_checkout_{time.time_ns()}",
    )


def _invoice_event(
    subscription_id,
    user_id,
    billing_code,
    invoice_id,
    period_start,
    period_end,
    stripe_sub_id,
    event_id=None,
    billing_reason="subscription_create",
    created=None,
):
    start = int(datetime.combine(period_start, datetime.min.time(), tzinfo=timezone.utc).timestamp())
    end = int(datetime.combine(period_end, datetime.min.time(), tzinfo=timezone.utc).timestamp())
    return _send_event(
        "invoice.payment_succeeded",
        {
            "id": invoice_id,
            "billing_reason": billing_reason,
            "amount_paid": 29900,
            "currency": "mxn",
            "customer": "cus_c7",
            "status_transitions": {"paid_at": int(time.time())},
            "parent": {
                "subscription_details": {
                    "subscription": stripe_sub_id,
                    "metadata": {
                        "subscription_id": str(subscription_id),
                        "user_id": str(user_id),
                        "billing_code": billing_code,
                    },
                }
            },
            "lines": {
                "data": [
                    {
                        "period": {"start": start, "end": end},
                        "parent": {
                            "subscription_item_details": {"subscription": stripe_sub_id}
                        },
                    }
                ]
            },
        },
        event_id=event_id or f"evt_invoice_{time.time_ns()}",
        created=created,
    )


def _request_count():
    if not REQUEST_LOG.exists():
        return 0
    return len([line for line in REQUEST_LOG.read_text(encoding="utf-8").splitlines() if line.strip()])


def _active_count(snapshot, user_id):
    rows = [row for row in snapshot[str(user_id)]["timbres"] if row["activo"]]
    assert len(rows) == 1, rows
    return rows[0]


@pytest.fixture(scope="session")
def servers():
    _assert_test_database()
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    migrate = subprocess.run(
        [DJANGO_PYTHON, "manage.py", "migrate", "--noinput", "--verbosity", "0"],
        cwd=DJANGO_ROOT,
        env=ServerManager().django_env(),
        capture_output=True,
        text=True,
        timeout=240,
    )
    if migrate.returncode != 0:
        raise RuntimeError(f"Migrate Django falló:\n{migrate.stdout}\n{migrate.stderr}")
    manager = ServerManager()
    manager.ensure_all()
    yield manager
    manager.stop_all()


@pytest.fixture
def state(servers):
    servers.ensure_all()
    seed = _reset_billing_data()
    _django_cmd("reset")
    REQUEST_LOG.parent.mkdir(parents=True, exist_ok=True)
    REQUEST_LOG.write_text("", encoding="utf-8")
    DELAY_FILE.unlink(missing_ok=True)
    yield seed
    DELAY_FILE.unlink(missing_ok=True)


def _key(subscription_id, start, end):
    return f"subscription:{subscription_id}:checkout_completed:{start.isoformat()}:{end.isoformat()}"


def test_c7_2_checkout_then_invoice(state):
    start = date(2026, 11, 1)
    end = date(2026, 12, 1)
    _checkout_event(state["sub_pro"], 1, "CFDI_PRO", "sub_c7_pro", "evt_c7_2_checkout")
    assert _queue_rows() == []

    _invoice_event(
        state["sub_pro"],
        1,
        "CFDI_PRO",
        "in_c7_2",
        start,
        end,
        "sub_c7_pro",
        event_id="evt_c7_2_invoice",
    )

    row = _queue_by_key(_key(state["sub_pro"], start, end))
    assert row["status"] == "completed"
    snapshot = _django_cmd("snapshot", "--user-id", "1")
    service = snapshot["1"]["services"][0]
    assert service["subscription_status"] == "active"
    assert service["date_cutoff"] == end.isoformat()
    count = _active_count(snapshot, 1)
    assert count["periodo_inicio"] == start.isoformat()
    assert count["periodo_fin"] == end.isoformat()
    assert count["contador_actual"] == 0
    assert _request_count() == 1


def test_c7_3_invoice_then_checkout(state):
    start = date(2026, 11, 1)
    end = date(2026, 12, 1)
    _invoice_event(
        state["sub_pro"],
        1,
        "CFDI_PRO",
        "in_c7_3",
        start,
        end,
        "sub_c7_pro",
        event_id="evt_c7_3_invoice",
    )
    before = _django_cmd("snapshot", "--user-id", "1")
    _checkout_event(
        state["sub_pro"],
        1,
        "CFDI_PRO",
        "sub_c7_pro",
        "evt_c7_3_checkout",
    )
    after = _django_cmd("snapshot", "--user-id", "1")
    assert before == after
    assert _request_count() == 1
    assert _queue_by_key(_key(state["sub_pro"], start, end))["status"] == "completed"


def test_c7_4_replay_checkout(state):
    start = date(2026, 11, 1)
    end = date(2026, 12, 1)
    _checkout_event(state["sub_pro"], 1, "CFDI_PRO", "sub_c7_pro", "evt_c7_4_checkout")
    _checkout_event(state["sub_pro"], 1, "CFDI_PRO", "sub_c7_pro", "evt_c7_4_checkout")
    _invoice_event(
        state["sub_pro"],
        1,
        "CFDI_PRO",
        "in_c7_4",
        start,
        end,
        "sub_c7_pro",
        event_id="evt_c7_4_invoice",
    )
    snapshot = _django_cmd("snapshot", "--user-id", "1")
    assert len(snapshot["1"]["services"]) == 1
    assert len(snapshot["1"]["timbres"]) == 1
    assert _request_count() == 1
    assert len(_queue_rows()) == 1


def test_c7_5_replay_invoice_same_and_different_event_id(state):
    start = date(2026, 11, 1)
    end = date(2026, 12, 1)
    _invoice_event(
        state["sub_pro"],
        1,
        "CFDI_PRO",
        "in_c7_5",
        start,
        end,
        "sub_c7_pro",
        event_id="evt_c7_5_invoice",
    )
    _invoice_event(
        state["sub_pro"],
        1,
        "CFDI_PRO",
        "in_c7_5",
        start,
        end,
        "sub_c7_pro",
        event_id="evt_c7_5_invoice",
    )
    _invoice_event(
        state["sub_pro"],
        1,
        "CFDI_PRO",
        "in_c7_5",
        start,
        end,
        "sub_c7_pro",
        event_id="evt_c7_5_invoice_new_id",
    )
    snapshot = _django_cmd("snapshot", "--user-id", "1")
    assert len(snapshot["1"]["timbres"]) == 1
    assert len(_queue_rows()) == 1
    assert _request_count() == 1


def test_c7_6_consumed_timbres_and_outbox_replay(state):
    start = date(2026, 11, 1)
    end = date(2026, 12, 1)
    _invoice_event(
        state["sub_pro"],
        1,
        "CFDI_PRO",
        "in_c7_6",
        start,
        end,
        "sub_c7_pro",
        event_id="evt_c7_6_invoice",
    )
    _django_cmd("set_counter", "--user-id", "1", "--value", "42")
    key = _key(state["sub_pro"], start, end)
    _force_retry(key)
    stats = _run_worker()
    assert stats["succeeded"] == 1
    snapshot = _django_cmd("snapshot", "--user-id", "1")
    count = _active_count(snapshot, 1)
    assert count["contador_actual"] == 42
    assert len(snapshot["1"]["timbres"]) == 1
    assert _queue_by_key(key)["status"] == "completed"


def test_c7_7_django_unavailable_then_recovery(state, servers):
    start = date(2026, 11, 1)
    end = date(2026, 12, 1)
    key = _key(state["sub_pro"], start, end)
    servers.stop_django()
    _invoice_event(
        state["sub_pro"],
        1,
        "CFDI_PRO",
        "in_c7_7",
        start,
        end,
        "sub_c7_pro",
        event_id="evt_c7_7_invoice",
    )
    pending = _queue_by_key(key)
    assert pending["status"] == "pending"
    assert pending["retry_count"] == 0
    assert _request_count() == 0

    _run_worker()
    retried = _queue_by_key(key)
    assert retried["status"] == "pending"
    assert retried["retry_count"] == 1
    assert retried["retry_count"] < retried["max_retries"]

    servers.start_django()
    _force_retry(key)
    stats = _run_worker()
    assert stats["succeeded"] == 1
    completed = _queue_by_key(key)
    assert completed["status"] == "completed"
    assert completed["retry_count"] == 2
    snapshot = _django_cmd("snapshot", "--user-id", "1")
    assert _active_count(snapshot, 1)["periodo_fin"] == end.isoformat()


def test_c7_8_billing_restart_preserves_outbox(state, servers):
    start = date(2026, 11, 2)
    end = date(2026, 12, 2)
    key = _key(state["sub_pro"], start, end)
    servers.stop_django()
    _invoice_event(
        state["sub_pro"],
        1,
        "CFDI_PRO",
        "in_c7_8",
        start,
        end,
        "sub_c7_pro",
        event_id="evt_c7_8_invoice",
    )
    assert _queue_by_key(key)["status"] == "pending"

    servers.stop_billing()
    assert _queue_by_key(key)["status"] == "pending"
    servers.start_billing()
    assert _queue_by_key(key)["status"] == "pending"

    servers.start_django()
    _force_retry(key)
    stats = _run_worker()
    assert stats["succeeded"] == 1
    assert _queue_by_key(key)["status"] == "completed"
    snapshot = _django_cmd("snapshot", "--user-id", "1")
    assert _active_count(snapshot, 1)["periodo_inicio"] == start.isoformat()


def test_c7_9_immediate_delivery_worker_race(state):
    start = date(2026, 11, 1)
    end = date(2026, 12, 1)
    key = _key(state["sub_pro"], start, end)
    DELAY_FILE.write_text("3", encoding="utf-8")
    result = {}

    def send():
        try:
            result["response"] = _invoice_event(
                state["sub_pro"],
                1,
                "CFDI_PRO",
                "in_c7_9",
                start,
                end,
                "sub_c7_pro",
                event_id="evt_c7_9_invoice",
            )
        except Exception as exc:
            result["error"] = exc

    thread = threading.Thread(target=send)
    thread.start()
    deadline = time.time() + 10
    while time.time() < deadline:
        rows = _queue_rows()
        if rows:
            break
        time.sleep(0.05)
    assert _queue_rows(), "El evento no llegó al Outbox"
    worker_stats = _run_worker()
    thread.join(timeout=30)
    assert not thread.is_alive()
    assert "error" not in result, result.get("error")
    assert result["response"].status_code == 200
    assert worker_stats["processed"] == 1
    assert worker_stats["succeeded"] == 0
    assert worker_stats["skipped"] == 1
    assert worker_stats["failed"] == 0
    assert worker_stats["expired"] == 0
    queue_row = _queue_by_key(key)
    assert queue_row["status"] == "completed"
    assert queue_row["lease_expires_at"] is None
    assert _request_count() >= 2, _request_count()
    snapshot = _django_cmd("snapshot", "--user-id", "1")
    assert len(snapshot["1"]["services"]) == 1
    assert len(snapshot["1"]["timbres"]) == 1
    assert _active_count(snapshot, 1)["contador_actual"] == 0


def test_c7_10_repurchase_after_cancellation(state):
    _django_cmd("seed_canceled", "--user-id", "1")
    start = date(2026, 12, 1)
    end = date(2027, 1, 1)
    _checkout_event(
        state["sub_repurchase"],
        1,
        "CFDI_PRO",
        "sub_c7_repurchase",
        "evt_c7_10_checkout",
    )
    _invoice_event(
        state["sub_repurchase"],
        1,
        "CFDI_PRO",
        "in_c7_10",
        start,
        end,
        "sub_c7_repurchase",
        event_id="evt_c7_10_invoice",
    )
    snapshot = _django_cmd("snapshot", "--user-id", "1")
    assert len(snapshot["1"]["services"]) == 1
    service = snapshot["1"]["services"][0]
    assert service["subscription_status"] == "active"
    assert service["billing_subscription_id"] == str(state["sub_repurchase"])
    assert service["stripe_subscription_id"] == "sub_c7_repurchase"
    assert service["date_cutoff"] == end.isoformat()
    assert len(snapshot["1"]["timbres"]) == 2
    old = [row for row in snapshot["1"]["timbres"] if not row["activo"]]
    assert len(old) == 1 and old[0]["contador_actual"] == 7
    active = _active_count(snapshot, 1)
    assert active["periodo_inicio"] == start.isoformat()
    assert active["contador_actual"] == 0


def test_c7_11_cfdi_free(state):
    _checkout_event(
        state["sub_free"],
        2,
        "CFDI_FREE",
        "sub_c7_free",
        "evt_c7_11_checkout",
    )
    row = _queue_by_key(f"evt_c7_11_checkout:checkout_completed")
    assert row["status"] == "pending"
    stats = _run_worker()
    assert stats["succeeded"] == 1
    snapshot = _django_cmd("snapshot", "--user-id", "2")
    service = snapshot["2"]["services"][0]
    assert service["billing_code"] == "CFDI_FREE"
    assert snapshot["2"]["timbres"] == []
    assert not row["payload"].get("period_start")
    assert not row["payload"].get("period_end")


def test_c7_12_period_invariant(state):
    start = date(2026, 12, 15)
    end = date(2027, 1, 15)
    _invoice_event(
        state["sub_pro"],
        1,
        "CFDI_PRO",
        "in_c7_12",
        start,
        end,
        "sub_c7_pro",
        event_id="evt_c7_12_invoice",
    )
    snapshot = _django_cmd("snapshot", "--user-id", "1")
    service = snapshot["1"]["services"][0]
    count = _active_count(snapshot, 1)
    assert service["date_cutoff"] == end.isoformat()
    assert count["periodo_fin"] == end.isoformat()
    assert count["periodo_inicio"] == start.isoformat()
    assert service["date_cutoff"] == count["periodo_fin"]


def test_c7_13_payment_exists_without_outbox(state):
    start = date(2026, 11, 1)
    end = date(2026, 12, 1)
    with Session(engine) as db:
        db.add(
            Payment(
                subscription_id=state["sub_pro"],
                provider="stripe",
                provider_payment_id="in_c7_13",
                amount=29900,
                currency="mxn",
                status="succeeded",
                paid_at=datetime.now(timezone.utc),
            )
        )
        db.commit()
    assert _queue_rows() == []
    _invoice_event(
        state["sub_pro"],
        1,
        "CFDI_PRO",
        "in_c7_13",
        start,
        end,
        "sub_c7_pro",
        event_id="evt_c7_13_invoice",
    )
    row = _queue_by_key(_key(state["sub_pro"], start, end))
    assert row["status"] == "completed"
    snapshot = _django_cmd("snapshot", "--user-id", "1")
    assert _active_count(snapshot, 1)["periodo_fin"] == end.isoformat()
    with Session(engine) as db:
        payments = db.exec(
            select(Payment).where(Payment.provider_payment_id == "in_c7_13")
        ).all()
        assert len(payments) == 1


def test_c7_14_payment_and_completed_outbox_replay(state):
    start = date(2026, 11, 1)
    end = date(2026, 12, 1)
    _invoice_event(
        state["sub_pro"],
        1,
        "CFDI_PRO",
        "in_c7_14",
        start,
        end,
        "sub_c7_pro",
        event_id="evt_c7_14_invoice",
    )
    _django_cmd("set_counter", "--user-id", "1", "--value", "42")
    before = _django_cmd("snapshot", "--user-id", "1")
    before_requests = _request_count()
    _invoice_event(
        state["sub_pro"],
        1,
        "CFDI_PRO",
        "in_c7_14",
        start,
        end,
        "sub_c7_pro",
        event_id="evt_c7_14_invoice_new_id",
    )
    after = _django_cmd("snapshot", "--user-id", "1")
    row = _queue_by_key(_key(state["sub_pro"], start, end))
    assert row["status"] == "completed"
    assert len(_queue_rows()) == 1
    assert _request_count() == before_requests
    assert before == after
    assert _active_count(after, 1)["contador_actual"] == 42


def test_c7_15_max_retries_tenth_failure_unchanged(state, servers):
    start = date(2026, 11, 1)
    end = date(2026, 12, 1)
    key = _key(state["sub_pro"], start, end)
    servers.stop_django()
    _invoice_event(
        state["sub_pro"],
        1,
        "CFDI_PRO",
        "in_c7_15",
        start,
        end,
        "sub_c7_pro",
        event_id="evt_c7_15_invoice",
    )
    assert _queue_by_key(key)["status"] == "pending"
    for attempt in range(1, 11):
        _force_retry(key)
        _run_worker()
        row = _queue_by_key(key)
        assert row["retry_count"] == attempt
    final = _queue_by_key(key)
    assert final["status"] == "failed"
    assert final["retry_count"] == 10
    assert final["max_retries"] == 10
    assert final["next_retry_at"] is None
    assert final["lease_expires_at"] is None
    assert _run_worker()["processed"] == 0
    assert _queue_by_key(key)["status"] == "failed"
