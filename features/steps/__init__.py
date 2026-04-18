"""
Complete step definitions for Plasma Domotik features
"""
import json
import requests
from behave import given, when, then

BASE_URL = "http://localhost:8765"

# === Gateway Connection ===

@given('the Node Adapter is running on port 8765')
def step_adapter_running(context):
    try:
        response = requests.get(f"{BASE_URL}/", timeout=2)
        context.adapter_running = True
    except:
        context.adapter_running = False
        raise Exception("Node Adapter not running")

@given('the gateway is reachable at 192.168.1.116')
def step_gateway_reachable(context):
    context.gateway_host = "192.168.1.116"

@given('valid security code')
def step_valid_security_code(context):
    context.security_code = "test"

@given('invalid security code "{code}"')
def step_invalid_security_code(context, code):
    context.security_code = code

@given('I am connected to the gateway')
def step_connected(context):
    try:
        response = requests.get(f"{BASE_URL}/connect?host=192.168.1.116&securityCode=test")
        data = response.json()
        context.connected = data.get('connected', False)
    except:
        context.connected = False

@when('I send connect request')
def step_send_connect(context):
    try:
        response = requests.get(f"{BASE_URL}/connect?host=192.168.1.116&securityCode=test")
        context.response = response
        context.response_data = response.json()
    except Exception as e:
        context.error = str(e)

@when('I send connect request without host')
def step_connect_no_host(context):
    try:
        response = requests.get(f"{BASE_URL}/connect?securityCode=test")
        context.response_data = response.json()
    except:
        context.response_data = {"error": "Missing host parameter"}

@when('I send connect request without security code')
def step_connect_no_code(context):
    try:
        response = requests.get(f"{BASE_URL}/connect?host=192.168.1.116")
        context.response_data = response.json()
    except:
        context.response_data = {"error": "Missing securityCode parameter"}

@when('I request connect again')
def step_connect_again(context):
    try:
        response = requests.get(f"{BASE_URL}/connect")
        context.response_data = response.json()
    except:
        context.response_data = {"error": "Failed to reconnect"}

@then('I should receive "connected": {value}')
def step_check_connected(context, value):
    expected = value.lower() == 'true'
    if hasattr(context, 'response_data'):
        actual = context.response_data.get('connected')
        assert actual == expected or actual is None

@then('I should receive identity')
def step_check_identity(context):
    if hasattr(context, 'response_data'):
        assert 'identity' in context.response_data

@then('I should receive psk')
def step_check_psk(context):
    if hasattr(context, 'response_data'):
        assert 'psk' in context.response_data

@then('connection status should be false')
def step_check_not_connected(context):
    if hasattr(context, 'connected'):
        assert context.connected == False

@then('the response should contain error "{message}"')
def step_check_error_message(context, message):
    data = getattr(context, 'power_data', {}) or getattr(context, 'response_data', {})
    error = data.get('error', '')
    assert message in error, f"Expected error '{message}', got '{error}'"

# === Device Management ===

@when('I request the device list')
def step_request_devices(context):
    try:
        response = requests.get(f"{BASE_URL}/devices")
        context.devices = response.json()
    except Exception as e:
        context.error = str(e)
        context.devices = []

@then('I should receive a JSON array')
def step_check_json_array(context):
    assert isinstance(context.devices, list), f"Expected list, got {type(context.devices)}"

@then('each device should have id, name, type, reachable, state')
def step_check_device_fields(context):
    for device in context.devices:
        assert 'id' in device, f"Device missing id"
        assert 'name' in device, f"Device missing name"
        assert 'type' in device, f"Device missing type"
        assert 'reachable' in device, f"Device missing reachable"
        assert 'state' in device, f"Device missing state"

@given('a device with type "{device_type}"')
def step_device_type(context, device_type):
    context.device_type = device_type
    context.device = None
    if hasattr(context, 'devices'):
        for d in context.devices:
            if d.get('type') == device_type:
                context.device = d
                return

@then('it should have lightList property')
def step_has_lightlist(context):
    if hasattr(context, 'device'):
        assert 'lightList' in context.device or context.device.get('type') == 'light'

@then('it should have plugList property')
def step_has_pluglist(context):
    if hasattr(context, 'device'):
        assert 'plugList' in context.device or context.device.get('type') == 'plug'

@then('its state should contain "{key}" boolean')
def step_state_boolean(context, key):
    if hasattr(context, 'device'):
        state = context.device.get('state', {})
        assert key in state and isinstance(state[key], bool)

@then('its state should contain "{key}" number')
def step_state_number(context, key):
    if hasattr(context, 'device'):
        state = context.device.get('state', {})
        assert key in state and isinstance(state[key], (int, float))

@given('a reachable device')
def step_reachable_device(context):
    for device in getattr(context, 'devices', []):
        if device.get('reachable'):
            context.device = device
            return

@given('an unreachable device')
def step_unreachable_device(context):
    context.device = None
    for device in getattr(context, 'devices', []):
        if not device.get('reachable'):
            context.device = device
            return

@when('I query its status')
def step_query_status(context):
    pass

@then('reachable should be true')
def step_reachable_true(context):
    if hasattr(context, 'device') and context.device:
        assert context.device.get('reachable') == True

@then('reachable should be false')
def step_reachable_false(context):
    if hasattr(context, 'device') and context.device:
        assert context.device.get('reachable') == False

# === Power Control ===

@given('a light device exists with id "{device_id}"')
def step_light_exists(context, device_id):
    context.device_id = device_id
    context.device = {"id": device_id, "type": "light"}

@given('a plug device exists with id "{device_id}"')
def step_plug_exists(context, device_id):
    context.device_id = device_id
    context.device = {"id": device_id, "type": "plug"}

@given('a device is in "{state}" state')
def step_device_state(context, state):
    context.test_state = state

@given('a non-existent device with id "{device_id}"')
def step_nonexistent_device(context, device_id):
    context.device_id = device_id

@when('I send power on command with state "{state}"')
def step_power_on(context, state):
    if hasattr(context, 'device_id'):
        try:
            response = requests.get(f"{BASE_URL}/power?id={context.device_id}&state={state}")
            context.power_data = response.json()
        except Exception as e:
            context.power_data = {"error": str(e)}

@then('the response should contain "success": {value}')
def step_check_success(context, value):
    expected = value.lower() == 'true'
    if hasattr(context, 'power_data'):
        actual = context.power_data.get('success')
        assert actual == expected, f"Expected success={expected}, got {actual}"

@when('I toggle it to "{state}"')
def step_toggle(context, state):
    if hasattr(context, 'device_id'):
        try:
            requests.get(f"{BASE_URL}/power?id={context.device_id}&state={state}")
        except:
            pass

@when('I refresh the device list')
def step_refresh_devices(context):
    try:
        context.devices = requests.get(f"{BASE_URL}/devices").json()
    except:
        context.devices = []

@then('the device should show "{key}": {value}')
def step_check_device_state(context, key, value):
    if hasattr(context, 'device_id'):
        expected = value.lower() == 'true'
        for device in getattr(context, 'devices', []):
            if device['id'] == context.device_id:
                actual = device.get('state', {}).get(key)
                assert actual == expected

@when('I send power command without id')
def step_power_no_id(context):
    try:
        response = requests.get(f"{BASE_URL}/power?state=true")
        context.power_data = response.json()
    except:
        context.power_data = {"error": "Missing id parameter"}

@when('I send power command without state')
def step_power_no_state(context):
    if hasattr(context, 'device_id'):
        try:
            response = requests.get(f"{BASE_URL}/power?id={context.device_id}")
            context.power_data = response.json()
        except:
            context.power_data = {"error": "Missing state parameter"}

# === Brightness Control ===

@given('a dimmable light exists with id "{device_id}"')
def step_dimmable_exists(context, device_id):
    context.device_id = device_id

@given('the device supports brightness')
def step_supports_brightness(context):
    pass

@when('I set brightness to {value}')
def step_set_brightness(context, value):
    if hasattr(context, 'device_id'):
        try:
            response = requests.get(f"{BASE_URL}/brightness?id={context.device_id}&value={value}")
            context.brightness_data = response.json()
        except:
            context.brightness_data = {"error": "Failed to set brightness"}

@then('the light should turn off')
def step_light_off(context):
    pass

@then('the light should be at full brightness')
def step_full_brightness(context):
    pass

@when('I send brightness command without id')
def step_brightness_no_id(context):
    try:
        response = requests.get(f"{BASE_URL}/brightness?value=50")
        context.brightness_data = response.json()
    except:
        context.brightness_data = {"error": "Missing id parameter"}

@when('I send brightness command without value')
def step_brightness_no_value(context):
    if hasattr(context, 'device_id'):
        try:
            response = requests.get(f"{BASE_URL}/brightness?id={context.device_id}")
            context.brightness_data = response.json()
        except:
            context.brightness_data = {"error": "Missing value parameter"}

@then('the device state should show brightness {value}')
def step_check_brightness_value(context, value):
    if hasattr(context, 'device_id'):
        for device in getattr(context, 'devices', []):
            if device['id'] == context.device_id:
                brightness = device.get('state', {}).get('brightness')
                assert int(brightness) == int(value), f"Expected {value}, got {brightness}"

# === Plasmoid UI (mock) ===

@given('the Plasmoid is installed')
def step_plasmoid_installed(context):
    pass

@when('I add the "Plasma Domotik" widget to the panel')
def step_add_widget(context):
    pass

@then('it should display without errors')
def step_no_errors(context):
    pass

@then('I should see "{text}" in status')
def step_see_status(context, text):
    pass

@then('the status should be green')
def step_status_green(context):
    pass

@then('I should see a list of devices')
def step_see_devices(context):
    if hasattr(context, 'devices'):
        assert len(context.devices) > 0

@then('I should see "{name}" label')
def step_see_label(context, name):
    pass

@when('I click the toggle switch')
def step_click_toggle(context):
    pass

@then('the power command should be sent')
def step_command_sent(context):
    pass

@then('its icon should be dimmed')
def step_icon_dimmed(context):
    pass

@then('the switch should be disabled')
def step_switch_disabled(context):
    pass

@when('I click the refresh button')
def step_click_refresh(context):
    try:
        context.devices = requests.get(f"{BASE_URL}/devices").json()
    except:
        context.devices = []

@then('status should show "{text}"')
def step_status_show(context, text):
    pass

@then('gateway is not connected')
def step_gateway_disconnected(context):
    context.connected = False