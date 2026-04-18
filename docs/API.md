# Node Adapter API

## Base URL

```
http://localhost:8765
```

## Endpoints

### 1. Connect to Gateway

**Endpoint**: `/connect`

**Method**: GET

**Parameters**:

| Parameter | Type | Required | Description |
|----------|------|----------|-------------|
| host | string | Yes | Gateway IP address |
| securityCode | string | Yes | Gateway security code |

**Example**:

```bash
curl "http://127.0.0.1:8765/connect?host=192.168.1.116&securityCode=YOUR_SECURITY_CODE"
```

**Response** (success):

```json
{
  "connected": true,
  "identity": "tradfri_123456789",
  "psk": "abc123..."
}
```

**Response** (error):

```json
{
  "connected": false,
  "error": "Authentication failed"
}
```

---

### 2. Get Devices

**Endpoint**: `/devices`

**Method**: GET

**Example**:

```bash
curl "http://127.0.0.1:8765/devices"
```

**Response**:

```json
[
  {
    "id": "65544",
    "name": "Bathroom",
    "type": "light",
    "reachable": false,
    "state": {
      "on": false,
      "brightness": 0,
      "color": "f1e0b5"
    },
    "capabilities": ["on_off", "brightness"]
  },
  {
    "id": "65545", 
    "name": "Bed side",
    "type": "light",
    "reachable": true,
    "state": {
      "on": true,
      "brightness": 31,
      "color": "e78834"
    },
    "capabilities": ["on_off", "brightness", "color"]
  }
]
```

**Device Fields**:

| Field | Type | Description |
|-------|------|-------------|
| id | string | Device instance ID |
| name | string | Device name |
| type | string | "light" or "plug" |
| reachable | boolean | Device reachable status |
| state.on | boolean | Power state |
| state.brightness | number | Brightness 0-100 |
| state.color | string | RGB hex color |
| capabilities | string[] | Available features |

---

### 3. Set Power

**Endpoint**: `/power`

**Method**: GET

**Parameters**:

| Parameter | Type | Required | Description |
|----------|------|----------|-------------|
| id | string | Yes | Device instance ID |
| state | string | Yes | "true" or "false" |

**Example**:

```bash
# Turn on
curl "http://127.0.0.1:8765/power?id=65545&state=true"

# Turn off  
curl "http://127.0.0.1:8765/power?id=65545&state=false"
```

**Response** (success):

```json
{
  "success": true
}
```

**Response** (error):

```json
{
  "success": false,
  "error": "Device not found"
}
```

---

### 4. Set Brightness

**Endpoint**: `/brightness`

**Method**: GET

**Parameters**:

| Parameter | Type | Required | Description |
|----------|------|----------|-------------|
| id | string | Yes | Device instance ID |
| value | number | Yes | Brightness 0-100 |

**Example**:

```bash
curl "http://127.0.0.1:8765/brightness?id=65545&value=50"
```

---

## HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request (missing parameters) |
| 404 | Device not found |
| 503 | Not connected to gateway |

## Error Responses

```json
{
  "error": "Error message"
}
```

or

```json
{
  "success": false,
  "error": "Error message"
}
```