Feature: Power Control
  As a user
  I want to turn devices on/off
  So that I can control lights and plugs

  Background:
    Given the Node Adapter is running on port 8765
    And I am connected to the gateway

  Scenario: Turn on a light
    Given a light device exists with id "65545"
    When I send power on command with state "true"
    Then the response should contain "success": true

  Scenario: Turn off a light
    Given a light device exists with id "65545"
    When I send power off command with state "false"
    Then the response should contain "success": true

  Scenario: Turn on a plug
    Given a plug device exists with id "65556"
    When I send power on command with state "true"
    Then the response should contain "success": true

  Scenario: Toggle updates device state
    Given a device is in "off" state
    When I toggle it to "on"
    And I refresh the device list
    Then the device should show "on": true

  Scenario: Command is always sent even when target state matches current state
    Given a reachable light device
    When I read its current power state
    And I send the same power state again
    Then the response should contain "success": true
    And after refresh the device power state should be unchanged

  Scenario: Toggle off a device that is on
    Given a reachable light device
    When I ensure the device is on
    And I send power off command with state "false"
    Then the response should contain "success": true
    And after waiting for state propagation the device should show "on": false

  Scenario: Toggle on a device that is off
    Given a reachable light device
    When I ensure the device is off
    And I send power on command with state "true"
    Then the response should contain "success": true
    And after waiting for state propagation the device should show "on": true

  Scenario: Device not found for power command
    Given a non-existent device with id "99999"
    When I send power command
    Then the response should contain error "Device not found"

  Scenario: Power command requires device id
    When I send power command without id
    Then the response should contain error "Missing id parameter"

  Scenario: Power command requires state
    Given a valid device id
    When I send power command without state
    Then the response should contain error "Missing state parameter"