# Class Diagrams

## 1. Main Components

```mermaid
classDiagram
    class PlasmoidItem {
        +property var devices[]
        +property bool loading
        +property bool connected
        +property string statusText
        +property string lastError
        +property string gatewayHost
        +property string securityCode
        +function httpGet(path, callback)
        +function refreshDevices()
        +function togglePower(deviceId, state)
    }
    
    class fullRepresentation {
        +property implicitWidth
        +property implicitHeight
    }
    
    class httpGet {
        +function XMLHttpRequest
    }
    
    PlasmoidItem --> fullRepresentation
    PlasmoidItem --> httpGet
```

```mermaid
classDiagram
    class NodeAdapter {
        +const PORT = 8765
        +let tradfri: TradfriClient
        +let connected: boolean
        +let devicesCache: Map
        +function loadConfig()
        +function mapDevice(device)
        +function ensureConnected()
        +function getCachedDevices()
        +function handleRequest(req, res)
    }
    
    class HTTPHandler {
        +function handleConnect()
        +function handleDevices()
        +function handlePower()
    }
    
    class TradfriClient {
        +function authenticate()
        +function operateLight()
        +function operatePlug()
    }
    
    NodeAdapter --> HTTPHandler
    NodeAdapter --> TradfriClient
    HTTPHandler --> NodeAdapter
```

---

## 2. Plasmoid Properties

```mermaid
classDiagram
    class PlasmoidItem {
        <<QML Component>>
        
        +property var devices: list of Device
        +property bool loading
        +property bool connected
        +property string statusText
        +property string lastError
        +property string gatewayHost
        +property string securityCode
    }
    
    class Device {
        +string id
        +string name
        +string type
        +boolean reachable
        +DeviceState state
    }
    
    class DeviceState {
        +boolean on
        +number brightness
        +string color
    }
    
    class fullRepresentation {
        <<Item>>
        
        +implicitWidth
        +implicitHeight
    }
    
    class ListView {
        +property model
        +property delegate
    }
    
    class Switch {
        +property checked
        +property enabled
        +signal onToggled
    }
    
    PlasmoidItem --> Device
    PlasmoidItem --> fullRepresentation
    fullRepresentation --> ListView
    ListView --> Switch
    Device --> DeviceState
```

---

## 3. Node Adapter State Machine

```mermaid
stateDiagram-v2
    [*] --> NotConnected
    NotConnected --> Connecting: ensureConnected()
    Connecting --> Connected: authenticate() success
    Connecting --> NotConnected: authenticate() fail
    
    Connected --> DeviceDiscovery: GET /devices
    DeviceDiscovery --> Connected: devices discovered
    
    Connected --> Operating: GET /power
    Operating --> Connected: operation complete
    
    Connected --> Disconnecting: service stop
    Disconnecting --> [*]
    
    Connected --> Reconnecting: connection lost
    Reconnecting --> Connecting: retry
```

---

## 4. Devices Cache

```mermaid
classDiagram
    class devicesCache {
        <<Map~string, DeviceWrapper>>
    }
    
    class DeviceWrapper {
        +number instanceId
        +string name
        +Light[] lightList
        +Plug[] plugList
        +Blind[] blindList
    }
    
    class Light {
        +number id
        +boolean isDimmable
        +boolean onOff
        +number brightness
        +number colorX
        +number colorY
    }
    
    class Plug {
        +number id
        +boolean onOff
    }
    
    devicesCache --> DeviceWrapper
    DeviceWrapper --> Light
    DeviceWrapper --> Plug
```

---

## 5. HTTP Request Flow

```mermaid
classDiagram
    class Request {
        +string method
        +URL url
    }
    
    class URL {
        +string pathname
        +SearchParams searchParams
    }
    
    class SearchParams {
        +function get(key)
    }
    
    class Router {
        +case '/connect': handleConnect
        +case '/devices': handleDevices
        +case '/power': handlePower
    }
    
    class Response {
        +function writeHead(status)
        +function end(data)
    }
    
    Request --> URL
    URL --> SearchParams
    Request --> Router
    Router --> Response
```

---

## 6. API Endpoints

```mermaid
classDiagram
    class NodeAdapter {
        +handleRequest(req, res)
    }
    
    class ConnectHandler {
        +host: string
        +securityCode: string
        +returns: {connected, identity, psk}
    }
    
    class DevicesHandler {
        +ensureConnected()
        +waitForInitialDiscovery()
        +getCachedDevices()
        +returns: Device[]
    }
    
    class PowerHandler {
        +deviceId: string
        +state: boolean
        +operateLight()/operatePlug()
        +returns: {success}
    }
    
    class BrightnessHandler {
        +deviceId: string
        +value: number
        +setBrightness()
        +returns: {success}
    }
    
    NodeAdapter --> ConnectHandler
    NodeAdapter --> DevicesHandler
    NodeAdapter --> PowerHandler
    NodeAdapter --> BrightnessHandler
```

---

## 7. Data Models

```mermaid
erDiagram
    PLASMOID ||--|| CONFIG : uses
    PLASMOID {
        string gatewayHost
        string securityCode
    }
    
    CONFIG {
        string host
        string identity
        string psk
    }
    
    NODE_ADAPTER ||--|| TRÅDFRI_CLIENT : connects
    NODE_ADAPTER {
        Map devicesCache
        boolean connected
    }
    
    TRÅDFRI_CLIENT {
        string host
        string identity
        string psk
    }
    
    DEVICES_CACHE ||--|| DEVICES : contains
    DEVICES {
        list devices
    }
    
    DEVICE_WRAPPER ||--|| LIGHT : has
    DEVICE_WRAPPER ||--|| PLUG : has
    
    DEVICE_WRAPPER {
        number instanceId
        string name
    }
    
    LIGHT {
        boolean onOff
        number brightness
    }
    
    PLUG {
        boolean onOff
    }
```

---

## 8. Relationships

```mermaid
flowchart LR
    A[Plasmoid<br/>main.qml] -->|creates| B[HTTP Request]
    B -->|sends to| C[localhost:8765]
    C -->|Node Adapter<br/>tradfri_node_adapter.mjs]
    C -->|creates| D[TradfriClient]
    D -->|connects to| E[TRÅDFRI Gateway]
    E -->|controls| F[Zigbee Devices]
    
    subgraph "Plasma Desktop"
    A
    B
    end
    
    subgraph "Node.js Runtime"
    C
    D
    end
    
    subgraph "Network"
    E
    F
    end
```