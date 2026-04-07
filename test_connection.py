#!/usr/bin/env python3
"""Quick test script to verify Tradfri connection.

Credentials are read from environment variables to avoid committing secrets.
Set TRADFRI_HOST, TRADFRI_SECURITY_CODE (or TRADFRI_IDENTITY + TRADFRI_PSK).
"""

import logging
import os
from backend.service.tradfri_adapter import TradfriAdapter

logging.basicConfig(level=logging.INFO)

def main():
    host = os.environ.get("TRADFRI_HOST", "192.168.1.100")
    security_code = os.environ.get("TRADFRI_SECURITY_CODE")
    identity = os.environ.get("TRADFRI_IDENTITY")
    psk = os.environ.get("TRADFRI_PSK")

    print(f"Attempting to connect to Tradfri gateway at {host}...")
    print()

    adapter = TradfriAdapter(
        host=host,
        identity=identity,
        psk=psk,
        security_code=security_code,
    )

    if adapter.connect():
        print("Successfully connected to gateway!")
        print(f"Identity: {adapter.identity}")
        print(f"PSK: {adapter.psk}")
        print()

        print("Discovering devices...")
        devices = list(adapter.discover_devices())
        print(f"Found {len(devices)} device(s):")
        for device in devices:
            print(f"  - {device['name']} (ID: {device['id']}, Type: {device['type']}, Reachable: {device['reachable']})")
            if device['state']:
                print(f"    State: {device['state']}")

        adapter.disconnect()
    else:
        print("Failed to connect to gateway")
        print("Please check:")
        print("  1. The gateway IP address is correct")
        print("  2. The security code is correct (found on bottom of gateway)")
        print("  3. The gateway is powered on and reachable on the network")
        print("  4. pytradfri is installed: pip install pytradfri")

if __name__ == "__main__":
    main()
