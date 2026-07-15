"""Reprocesar la cola de notificaciones pendientes.

Uso:
    python -m app.cli.reprocess_queue
    python -m app.cli.reprocess_queue --max-items 50
"""

import argparse
from app.services.queue_processor import process_pending_notifications


def main():
    parser = argparse.ArgumentParser(description="Reprocesar cola de notificaciones")
    parser.add_argument("--max-items", type=int, default=10)
    args = parser.parse_args()

    stats = process_pending_notifications(max_items=args.max_items)
    print(f"Procesadas: {stats['processed']}")
    print(f"Exitosas:   {stats['succeeded']}")
    print(f"Fallidas:   {stats['failed']}")
    print(f"Expiradas:  {stats['expired']}")


if __name__ == "__main__":
    main()