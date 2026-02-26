#!/usr/bin/env python3
"""Backup and migrate the local SQLite RSVP database to the latest Alembic schema.

Flow:
1) create timestamped backup
2) stamp baseline Alembic revision if DB predates Alembic tracking
3) run `alembic upgrade head`
4) verify expected columns exist
"""

from __future__ import annotations

import argparse
import shutil
import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path


BASELINE_REVISION = "001"
EXPECTED_GUEST_COLUMNS = {
    "attendance_choice",
    "attend_ceremony",
    "attend_lunch",
    "allergens",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--backend-dir",
        default=Path(__file__).resolve().parents[1],
        type=Path,
        help="Path to backend directory containing alembic.ini and wedding.db",
    )
    parser.add_argument(
        "--db-path",
        default=None,
        type=Path,
        help="Override SQLite DB path (default: <backend-dir>/wedding.db)",
    )
    parser.add_argument(
        "--backup-dir",
        default=None,
        type=Path,
        help="Where to write backup files (default: <backend-dir>/backups)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned actions without executing migration",
    )
    parser.add_argument(
        "--no-restore-on-failure",
        action="store_true",
        help="Do not restore DB from backup if migration fails",
    )
    return parser.parse_args()


def sqlite_table_names(db_path: Path) -> set[str]:
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    return {row[0] for row in rows}


def sqlite_column_names(db_path: Path, table_name: str) -> set[str]:
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    return {row[1] for row in rows}


def create_sqlite_backup(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(source) as src_conn, sqlite3.connect(destination) as dst_conn:
        src_conn.backup(dst_conn)


def sqlite_url_for_path(db_path: Path, backend_dir: Path) -> str:
    try:
        relative = db_path.relative_to(backend_dir)
        return f"sqlite:///./{relative.as_posix()}"
    except ValueError:
        return f"sqlite:///{db_path}"


def prepare_alembic_ini(backend_dir: Path, db_path: Path) -> tuple[Path, Path | None]:
    """Return alembic ini path to use and optional temp ini path to cleanup."""
    default_db = (backend_dir / "wedding.db").resolve()
    default_ini = backend_dir / "alembic.ini"
    if db_path == default_db:
        return default_ini, None

    temp_ini = backend_dir / ".alembic.migrate.tmp.ini"
    content = default_ini.read_text(encoding="utf-8")
    target_line_prefix = "sqlalchemy.url = "
    new_lines = []
    replaced = False
    for line in content.splitlines():
        if line.startswith(target_line_prefix):
            new_lines.append(f"{target_line_prefix}{sqlite_url_for_path(db_path, backend_dir)}")
            replaced = True
        else:
            new_lines.append(line)
    if not replaced:
        raise RuntimeError("Could not find sqlalchemy.url in alembic.ini")
    temp_ini.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    return temp_ini, temp_ini


def run_alembic(backend_dir: Path, alembic_ini_path: Path, *args: str) -> None:
    cmd = [sys.executable, "-m", "alembic", "-c", str(alembic_ini_path), *args]
    subprocess.run(cmd, cwd=backend_dir, check=True)


def infer_needs_stamp(db_path: Path) -> bool:
    tables = sqlite_table_names(db_path)
    if "alembic_version" in tables:
        return False
    # Existing app DBs may have schema but no alembic metadata.
    return "families" in tables and "guests" in tables


def verify_migration(db_path: Path) -> None:
    cols = sqlite_column_names(db_path, "guests")
    missing = EXPECTED_GUEST_COLUMNS - cols
    if missing:
        raise RuntimeError(f"Migration verification failed, missing columns: {sorted(missing)}")


def main() -> int:
    args = parse_args()
    backend_dir = args.backend_dir.resolve()
    db_path = (args.db_path or (backend_dir / "wedding.db")).resolve()
    backup_dir = (args.backup_dir or (backend_dir / "backups")).resolve()

    if not (backend_dir / "alembic.ini").exists():
        print(f"ERROR: alembic.ini not found in {backend_dir}", file=sys.stderr)
        return 2
    if not db_path.exists():
        print(f"ERROR: database not found: {db_path}", file=sys.stderr)
        return 2

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = backup_dir / f"{db_path.stem}-{timestamp}.sqlite3"

    print(f"Backend dir: {backend_dir}")
    print(f"Database:    {db_path}")
    print(f"Backup:      {backup_path}")

    if args.dry_run:
        if infer_needs_stamp(db_path):
            print(f"[dry-run] Would run: alembic stamp {BASELINE_REVISION}")
        print("[dry-run] Would run: alembic upgrade head")
        print("[dry-run] Would verify guest columns:", ", ".join(sorted(EXPECTED_GUEST_COLUMNS)))
        return 0

    create_sqlite_backup(db_path, backup_path)
    print("Backup created.")

    restore_on_failure = not args.no_restore_on_failure
    alembic_ini_path, temp_ini_path = prepare_alembic_ini(backend_dir, db_path)

    try:
        if infer_needs_stamp(db_path):
            print(f"No alembic history found. Stamping existing DB as revision {BASELINE_REVISION}...")
            run_alembic(backend_dir, alembic_ini_path, "stamp", BASELINE_REVISION)

        print("Running alembic upgrade head...")
        run_alembic(backend_dir, alembic_ini_path, "upgrade", "head")

        print("Verifying migrated schema...")
        verify_migration(db_path)
        print("Migration completed successfully.")
        return 0
    except Exception as exc:
        print(f"ERROR: migration failed: {exc}", file=sys.stderr)
        if restore_on_failure:
            print("Restoring database from backup...")
            shutil.copy2(backup_path, db_path)
            print("Database restored from backup.", file=sys.stderr)
        else:
            print("Backup preserved; restore manually if needed.", file=sys.stderr)
        return 1
    finally:
        if temp_ini_path and temp_ini_path.exists():
            temp_ini_path.unlink()


if __name__ == "__main__":
    raise SystemExit(main())
