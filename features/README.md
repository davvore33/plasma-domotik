# Gherkin Feature Files

This directory contains BDD test scenarios written in Gherkin syntax.

## Format

Each `.feature` file corresponds to a feature area:
- `device_management.feature` - Device listing and properties
- `power_control.feature` - On/off control
- `gateway_connection.feature` - Gateway connection
- `plasmoid_ui.feature` - Plasma widget UI
- `brightness_control.feature` - Brightness adjustment

## Running Tests

These features can be run with `behave`:

```bash
pip install behave
behave features/
```

## Scenario Format

```gherkin
Feature: Feature title
  As a [role]
  I want to [action]
  So that [benefit]

  Background:
    Given [setup condition]

  Scenario: Scenario title
    Given [precondition]
    When [action]
    Then [expected result]
```

## Examples

See individual `.feature` files for complete scenarios.