"""
Automatic Group & Member Cleanup CLI Script.
Deletes groups older than TTL days (default: 90 days / 3 months).

Usage:
    python cleanup.py          # Deletes groups older than 90 days
    python cleanup.py --days 30 # Deletes groups older than 30 days
"""
import argparse
from datetime import datetime, timezone
from app import create_app
from app.models import cleanup_expired_groups

app = create_app('production')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Cleanup expired trip groups.")
    parser.add_argument('--days', type=int, default=90, help="TTL threshold in days (default: 90)")
    args = parser.parse_args()

    with app.app_context():
        deleted_count = cleanup_expired_groups(ttl_days=args.days)
        now_str = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        print(f"[{now_str}] Cleanup Completed: Purged {deleted_count} group(s) older than {args.days} days.")
