#!/usr/bin/env python3

import sqlite3
import json
import hashlib
import os
import sys
import random
from copy import deepcopy

# ================= USER SETTINGS =================
# Edit this to point to your file and point to where the anonymized list should be saved.
INPUT_DB = r"path_to_your_.kismet_file"
OUTPUT_DB = r"path_to_new_anonymized.kismet"
# =================================================

# ---- Fake manufacturers to substitute for the real manufacturers from the scan  ----
FAKE_MANUFACTURERS = [
    "TechSavvy Systems",
    "Fictional Wireless Ltd.",
    "ABCD Connectivity",
    "Best Wireless Inc.",
    "DemoTech Corp"
]

# ---- Salt must be set as environment variable ----
HASH_SALT = os.getenv("KISMET_HASH_SALT")

if not HASH_SALT:
    print("[!] ERROR: Environment variable KISMET_HASH_SALT is not set")
    print("    Example (PowerShell):")
    print('    setx KISMET_HASH_SALT "use-a-long-random-string-here"')
    sys.exit(1)


def hash_value(value: str) -> str:
    """Hash a value using SHA-256 with salt"""
    if not value:
        return None
    h = hashlib.sha256()
    h.update((HASH_SALT + value).encode("utf-8"))
    return h.hexdigest()


def round_coord(coord):
    """Round GPS coordinate to 3 decimal places"""
    try:
        return round(float(coord), 3)
    except Exception:
        return coord


def anonymize_device_blob(device_blob: str) -> str:
    """Anonymize fields inside the JSON device blob"""
    try:
        dev = json.loads(device_blob)
    except Exception:
        return device_blob

    dev = deepcopy(dev)

    # ---- Hash SSID ----
    ssid_key = "kismet.device.base.name"
    if ssid_key in dev and dev[ssid_key]:
        dev[ssid_key] = hash_value(dev[ssid_key])

    # ---- Remove real manufacturer & insert fake ----
    manuf_key = "kismet.device.base.manuf"
    dev[manuf_key] = random.choice(FAKE_MANUFACTURERS)

    # ---- Remove signal strength if present ----
    signal_keys = [
        "kismet.device.base.signal",
        "kismet.device.base.signal_dbm",
        "kismet.device.base.strongest_signal"
    ]
    for key in signal_keys:
        if key in dev:
            dev[key] = None

    return json.dumps(dev)


def main():
    print("[*] Opening source database...")
    src = sqlite3.connect(INPUT_DB)
    src.row_factory = sqlite3.Row

    print("[*] Creating anonymized database...")
    dst = sqlite3.connect(OUTPUT_DB)

    src_cur = src.cursor()
    dst_cur = dst.cursor()

    print("[*] Copying database schema...")
    src_cur.execute("SELECT sql FROM sqlite_master WHERE type='table'")
    for row in src_cur.fetchall():
        if row["sql"]:
            dst_cur.execute(row["sql"])

    print("[*] Processing devices table...")
    src_cur.execute("SELECT * FROM devices")
    columns = [desc[0] for desc in src_cur.description]

    placeholders = ",".join(["?"] * len(columns))
    insert_sql = f"INSERT INTO devices ({','.join(columns)}) VALUES ({placeholders})"

    for row in src_cur.fetchall():
        row = dict(row)

        # ---- Hash BSSID (devmac) ----
        if row.get("devmac"):
            row["devmac"] = hash_value(row["devmac"])

        # ---- Remove timestamps ----
        if "first_time" in row:
            row["first_time"] = None
        if "last_time" in row:
            row["last_time"] = None

        # ---- Round GPS coordinates ----
        if row.get("avg_lat") is not None:
            row["avg_lat"] = round_coord(row["avg_lat"])
        if row.get("avg_lon") is not None:
            row["avg_lon"] = round_coord(row["avg_lon"])

        # ---- Remove signal strength column if exists ----
        if "strongest_signal" in row:
            row["strongest_signal"] = None

        # ---- Anonymize JSON device blob ----
        if row.get("device"):
            row["device"] = anonymize_device_blob(row["device"])

        dst_cur.execute(insert_sql, list(row.values()))

    dst.commit()
    src.close()
    dst.close()

    print("[+] Anonymized database created at:")
    print(f"    {OUTPUT_DB}")


if __name__ == "__main__":
    main()
