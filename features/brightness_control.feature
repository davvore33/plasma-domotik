Feature: Brightness Control
  As a user
  I want to adjust device brightness
  So that I can dim lights

  Background:
    Given the Node Adapter is running on port 8765
    And I am connected to the gateway
    And a dimmable light exists with id "65545"

  Scenario: Set brightness to 50%
    Given the device supports brightness
    When I set brightness to 50
    Then the response should contain "success": true

  Scenario: Set brightness to 0%
    Given the device supports brightness
    When I set brightness to 0
    Then the light should turn off

  Scenario: Set brightness to 100%
    Given the device supports brightness
    When I set brightness to 100
    Then the light should be at full brightness

  Scenario: Brightness requires device id
    When I send brightness command without id
    Then the response should contain error "Missing id parameter"

  Scenario: Brightness requires value
    Given a valid device id
    When I send brightness command without value
    Then the response should contain error "Missing value parameter"

  Scenario: Brightness value must be number
    Given a valid device id
    When I set brightness to "fifty"
    Then the response should contain error

  Scenario: Brightness updates device state
    Given brightness is set to 75
    When I refresh the device list
    Then the device state should show brightness 75