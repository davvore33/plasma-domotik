# Flow Diagrams

## 1. Application Startup

```mermaid
sequenceDiagram
    participant User
    participant Plasmoid
    participant NodeAdapter
    participant Gateway
    
    Note over Plasmoid: Component.onCompleted
    
    Plasmoid->>Plasmoid: refreshDevices()
    
    Plasmoid->>NodeAdapter: GET /connect?host=192.168.1.116&securityCode=...
    NodeAdapter->>Gateway: Authenticate(host, securityCode)
    Gateway-->>NodeAdapter: {identity, psk}
    NodeAdapter-->>Plasmoid: {connected: true}
    
    Plasmoid->>NodeAdapter: GET /devices
    Note over NodeAdapter: Wait for device discovery
    NodeAdapter-->>Plasmoid: [{devices...}]
    
    Plasmoid->>Plasmoid: Update UI with device list
    Note over Plasmoid: Display devices with switches
```

## 2. Toggle Device Power

```mermaid
sequenceDiagram
    participant User
    participant Plasmoid
    participant NodeAdapter
    participant Gateway
    participant Device
    
    User->>Plasmoid: Click toggle switch
    
    Plasmoid->>Plasmoid: onToggled(deviceId, checked)
    
    Plasmoid->>NodeAdapter: GET /power?id=65545&state=true
    Note over NodeAdapter: Lookup device in cache
    
    NodeAdapter->>Gateway: operateLight(device, {onOff: true})
    Gateway->>Device: Zigbee command (on)
    
    Note over Device: Physical device turns on
    
    Device-->>Gateway: ACK
    Gateway-->>NodeAdapter: success
    
    Note over NodeAdapter: Device observation updates state
    
    NodeAdapter-->>Plasmoid: {success: true}
    
    Plasmoid->>Plasmoid: refreshDevices()
    Plasmoid->>NodeAdapter: GET /devices
    NodeAdapter-->>Plasmoid: Updated device list
    
    Plasmoid->>Plasmoid: Update switch state
```

## 3. HTTP Request Flow

```mermaid
sequenceDiagram
    participant Plasmoid
    participant NodeAdapter
    participant Cache
    
    Plasmoid->>NodeAdapter: XMLHttpRequest GET /path
    
    Note over NodeAdapter: Parse URL and path
    
    alt /connect
        NodeAdapter->>NodeAdapter: ensureConnected()
        NodeAdapter->>Cache: Check cached credentials
        Cache-->>NodeAdapter: config or null
        Note over NodeAdapter: Create TradfriClient
        NodeAdapter->>NodeAdapter: Authenticate
    else /devices
        NodeAdapter->>NodeAdapter: ensureConnected()
        NodeAdapter->>NodeAdapter: waitForInitialDiscovery()
        Note over NodeAdapter: Device observation in progress
        NodeAdapter->>Cache: Get cached devices
        Cache-->>NodeAdapter: devices array
    else /power
        NodeAdapter->>NodeAdapter: Lookup device by ID
        NodeAdapter->>Cache: devicesCache.get(id)
        Note over NodeAdapter: Check lightList/plugList
        NodeAdapter->>NodeAdapter: operateLight() or operatePlug()
    end
    
    NodeAdapter-->>Plasmoid: JSON response
```

## 4. Device List Update Timer

```mermaid
sequenceDiagram
    participant Timer
    participant Plasmoid
    participant NodeAdapter
    
    Note over Timer: Fires every 10 seconds
    
    Timer->>Plasmoid: onTriggered
    
    Plasmoid->>NodeAdapter: GET /connect?host=...
    NodeAdapter-->>Plasmoid: {connected: true}
    Note over Plasmoid: Check connection status
    
    Plasmoid->>NodeAdapter: GET /devices
    NodeAdapter-->>Plasmoid: [{devices...}]
    Note over Plasmoid: Update device list and UI
    
    Note over Timer: Repeats every 10 seconds
```

## 5. System Flow Diagram

```mermaid
flowchart TD
    A[User clicks switch] --> B[onToggled event]
    
    B --> C[XMLHttpRequest]
    C --> D[localhost:8765]
    
    D --> E{Device in cache?}
    E -->|Yes| F[operateLight/operatePlug]
    E -->|No| G[Return 404]
    
    F --> H[CoAP to Gateway]
    H --> I[Zigbee to Device]
    I --> J[Device responds]
    J --> K[ACK to Gateway]
    K --> F
    
    F --> L[{success: true}]
    L --> M[refreshDevices]
    
    M --> N[GET /devices]
    N --> O[Update UI]
    
    style A fill:#f9f,stroke:#333
    style I fill:#ff9,stroke:#333
    style O fill:#9f9,stroke:#333
```

## 6. Connection Flow

```mermaid
flowchart TD
    A[Plasmoid loads] --> B[Component.onCompleted]
    
    B --> C[refreshDevices]
    
    C --> D[HTTP GET /connect]
    D --> E[Node Adapter]
    
    E --> F{Credentials cached?}
    F -->|Yes| G[Use cached identity/psk]
    F -->|No| H[Authenticate with Gateway]
    H --> I[Save to config file]
    G --> J[Create TradfriClient]
    
    J --> K[Connect to Gateway]
    K --> L{Connected?}
    L -->|Yes| M[Return connected: true]
    L -->|No| N[Return connected: false]
    
    M --> O[GET /devices]
    O --> P[Wait for discovery]
    P --> Q[Return device list]
    Q --> R[Update UI]
    
    style H fill:#ff9,stroke:#333
    style R fill:#9f9,stroke:#333
```