# Plasma Domotik Documentation

## Overview

Plasma Domotik is a Plasma 6 widget (plasmoid) that provides control over TRÅDFRI Zigbee devices through the IKEA TRÅDFRI gateway.

## Components

| Component | Description |
|----------|------------|
| **Plasmoid** | Plasma 6 QML widget displayed in panel/desktop |
| **Node Adapter** | HTTP bridge between Plasmoid and TRÅDFRI gateway |
| **Gateway** | IKEA TRÅDFRI gateway (192.168.1.116) |

## Documentation

| File | Description |
|------|-------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | System architecture overview |
| [API.md](API.md) | Node Adapter REST API |
| [FLOWS.md](FLOWS.md) | Flow diagrams |
| [CLASSES.md](CLASSES.md) | Class diagrams |

## Installation

See [README.md](../README.md) in project root.

## Quick Reference

- **Node Adapter Port**: 8765
- **Gateway IP**: 192.168.1.116
- **Security Code**: <your security code from gateway>

## Devices

| ID | Name | Type |
|----|------|------|
| 65544 | Bathroom | light |
| 65545 | Bed side | light |
| 65553 | Main ceiling | light |
| 65555 | Bed ceiling | light |
| 65556 | Outlet1 | plug |
| 65557 | TRADFRI outlet 2 | plug |