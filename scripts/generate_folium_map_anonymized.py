#!/usr/bin/env python3

import sqlite3
import json
import folium
from folium.plugins import MarkerCluster

# ================= USER SETTINGS =================
# Edit the path to point to the .kismet file you anonymized with  the anonymize_kismet_data.py script before.
KISMET_DB = r"path_to_your_anonymized_.kismet_file"
OUTPUT_MAP = "wifi_security_map.html"
DEFAULT_LOCATION = [0, 0]
# =================================================


def parse_security(crypt_list):
    if not crypt_list:
        return "Unknown"

    crypt = " ".join(crypt_list).upper()

    if "OPEN" in crypt:
        return "Open"
    if "WPA3" in crypt:
        return "WPA3"
    if "WPA2" in crypt and "WPA3" in crypt:
        return "WPA2/WPA3"
    if "WPA2" in crypt:
        return "WPA2"
    if "WPA" in crypt:
        return "WPA"
    if "WEP" in crypt:
        return "WEP"

    return crypt


def main():
    conn = sqlite3.connect(KISMET_DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    query = """
        SELECT
            devmac,
            avg_lat,
            avg_lon,
            device,
            strongest_signal
        FROM devices
        WHERE type = 'Wi-Fi AP'
          AND avg_lat IS NOT NULL
          AND avg_lon IS NOT NULL
    """
    cur.execute(query)
    rows = cur.fetchall()

    if not rows:
        print("[!] No Wi-Fi APs with GPS data found.")
        return

    wifi_map = folium.Map(
        location=[rows[0]["avg_lat"], rows[0]["avg_lon"]],
        zoom_start=14,
        tiles="OpenStreetMap"
    )

    cluster = MarkerCluster().add_to(wifi_map)

    for row in rows:
        try:
            dev = json.loads(row["device"])
        except Exception:
            dev = {}

        ssid_hash = dev.get("kismet.device.base.name", "<hidden>")
        channel = dev.get("kismet.device.base.channel", "N/A")
        manuf = dev.get("kismet.device.base.manuf", "Unknown")

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
                basic_map.get(dev["kismet.device.base.basic_crypt_set"], "Unknown")
            )

        security = parse_security(crypto)

        popup_html = (
            f"<b>SSID Hash:</b> {ssid_hash}<br>"
            f"<b>BSSID Hash:</b> {row['devmac']}<br>"
            f"<b>Security:</b> {security}<br>"
            f"<b>Channel:</b> {channel}<br>"
            f"<b>Manufacturer:</b> {manuf}<br>"
            f"<b>Signal:</b> {row['strongest_signal']}"
        )

        color = (
            "red" if security == "Open"
            else "green" if "WPA3" in security
            else "blue" if "WPA2" in security
            else "orange"
        )

        folium.CircleMarker(
            location=[row["avg_lat"], row["avg_lon"]],
            radius=6,
            popup=popup_html,
            color=color,
            fill=True,
            fill_opacity=0.8
        ).add_to(cluster)

    wifi_map.save(OUTPUT_MAP)
    print(f"[+] Map generated: {OUTPUT_MAP}")


if __name__ == "__main__":
    main()
