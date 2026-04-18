"""
behave environment for Plasma Domotik tests
"""
import requests

BASE_URL = "http://localhost:8765"

def before_all(context):
    """Check if Node Adapter is running before tests"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=2)
        context.adapter_running = True
        print(f"\n✓ Node Adapter is running on {BASE_URL}")
    except:
        context.adapter_running = False
        print(f"\n✗ Node Adapter NOT running on {BASE_URL}")
        print("  Start with: systemctl --user start plasma-domotik-adapter")

def after_all(context):
    """Cleanup after tests"""
    pass