
import math
import subprocess
import re
import json
from datetime import datetime
import os

def estimate_distance(signal_dbm, freq_mhz, path_loss_exp=3.0):
    try:
        return 10 ** ((27.55 - (20 * math.log10(freq_mhz)) + abs(signal_dbm)) / (10 * path_loss_exp))
    except Exception:
        return None

def parse_iwlist_output(output):
    cells = output.split("Cell ")
    results = []

    for cell in cells[1:]:
        result = {}

        address = re.search(r"Address: ([\w:]+)", cell)
        essid = re.search(r'ESSID:"([^"]*)"', cell)
        signal = re.search(r"Signal level=(-?\d+) dBm", cell)
        quality = re.search(r"Quality=([\d/]+)", cell)
        freq = re.search(r"Frequency:([\d\.]+) GHz", cell)
        channel = re.search(r"Channel:(\d+)", cell)
        encryption = re.search(r"Encryption key:(on|off)", cell)
        mode = re.search(r"Mode:(\w+)", cell)
        bitrates = re.findall(r"Bit Rates:(.+)", cell)

        result["timestamp"] = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
        result["bssid"] = address.group(1) if address else None
        result["ssid"] = essid.group(1) if essid else None
        result["signal"] = int(signal.group(1)) if signal else None
        result["quality"] = quality.group(1) if quality else None
        result["frequency"] = float(freq.group(1)) * 1000 if freq else None  # in MHz
        result["channel"] = int(channel.group(1)) if channel else None
        result["encryption"] = encryption.group(1) if encryption else None
        result["mode"] = mode.group(1) if mode else None

        if bitrates:
            rates = []
            for line in bitrates:
                rates.extend(rate.strip() for rate in line.split(";") if rate.strip())
            result["bit_rates"] = rates
        else:
            result["bit_rates"] = []

        if result["signal"] is not None and result["frequency"] is not None:
            result["estimated_distance_m"] = round(estimate_distance(result["signal"], result["frequency"]), 2)
        else:
            result["estimated_distance_m"] = None

        results.append(result)

    return results

def scan_wifi(interface="wlx00c0cab6949f"):
    try:
        result = subprocess.run(["iwlist", interface, "scan"], capture_output=True, text=True, timeout=15)
        if result.returncode != 0:
            raise RuntimeError(f"Scan failed: {result.stderr}")
        return parse_iwlist_output(result.stdout)
    except Exception as e:
        print(f"Error during scan: {e}")
        return []

def save_json(data, filename="wifi_scan_log.json"):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            existing = json.load(f)
    else:
        existing = []

    existing.extend(data)
    with open(filename, "w") as f:
        json.dump(existing, f, indent=2)
    print(f"Appended {len(data)} entries to {filename}")

if __name__ == "__main__":
    interface = "wlx00c0cab6949f"
    wifi_data = scan_wifi(interface)
    save_json(wifi_data)
