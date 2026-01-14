#!/usr/bin/env python3

import sqlite3
import json
import csv
from collections import Counter

# ================= USER SETTINGS =================
KISMET_DB = r"path_to_your_anonymized_or_original_.kismet_file"
OUTPUT_CSV = "wifi_security_summary.csv"
# =================================================


# Security ranking: higher = stronger
SECURITY_ORDER = [
    "WPA3",
    "WPA2",
    "WPA",
    "WEP",
    "Open",
    "Other",
    "Unknown"
]


def parse_security(crypt_list):
    if not crypt_list:
        return "Unknown"

    crypt = " ".join(crypt_list).upper()

    if "OPEN" in crypt:
        return "Open"
    if "WPA3" in crypt:
        return "WPA3"
    if "WPA2" in crypt and "WPA3" in crypt:
        return "WPA2"
    if "WPA2" in crypt:
        return "WPA2"
    if "WPA" in crypt:
        return "WPA"
    if "WEP" in crypt:
        return "WEP"

    return "Other"


def main():
    conn = sqlite3.connect(KISMET_DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT device
        FROM devices
        WHERE type = 'Wi-Fi AP'
    """)

    rows = cur.fetchall()
    if not rows:
        print("[!] No Wi-Fi AP data found.")
        return

    counts = Counter()

    for row in rows:
        try:
            dev = json.loads(row["device"])
        except Exception:
            dev = {}

        crypto = []
        for key in [
            "kismet.device.base.crypt",
            "kismet.device.base.wifi.crypt",
            "kismet.device.base.wireless.crypt"
        ]:
            if key in dev and dev[key]:
                val = dev[key]
                if isinstance(val, dict):
                    crypto.extend([k for k, v in val.items() if v])
                elif isinstance(val, list):
                    crypto.extend(val)
                else:
                    crypto.append(str(val))
                break

        if not crypto and "kismet.device.base.basic_crypt_set" in dev:
            basic_map = {
                0: "Open",
                1: "WEP",
                2: "WPA",
                3: "WPA2",
                4: "WPA3"
            }
            crypto.append(
                basic_map.get(dev["kismet.device.base.basic_crypt_set"], "Other")
            )

        security = parse_security(crypto)
        counts[security] += 1

    total = sum(counts.values())

    # ---- Sort by security strength ----
    sorted_results = [
        (sec, counts.get(sec, 0))
        for sec in SECURITY_ORDER
        if counts.get(sec, 0) > 0
    ]

    # ---- Print summary ----
    print("\nWi-Fi Security Summary")
    print("----------------------")
    for sec, count in sorted_results:
        percent = (count / total) * 100
        print(f"{sec:6} : {count:5}  ({percent:5.1f}%)")

    # ---- Write CSV ----
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Security_Type", "Count", "Percentage"])
        for sec, count in sorted_results:
            percent = (count / total) * 100
            writer.writerow([sec, count, f"{percent:.2f}"])

    print(f"\n[+] Summary written to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
