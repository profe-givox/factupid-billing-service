import argparse
import json

from app.services.queue_processor import process_pending_notifications


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-items", type=int, default=20)
    args = parser.parse_args()
    stats = process_pending_notifications(max_items=args.max_items)
    print(json.dumps(stats, sort_keys=True))


if __name__ == "__main__":
    main()
