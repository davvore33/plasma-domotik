Feature: Device Management
  As a user
  I want to manage my TRÅDFRI devices
  So that I can control lights and plugs from Plasma

  Background:
    Given the Node Adapter is running on port 8765
    And the gateway is reachable at 192.168.1.116

  Scenario: Get list of devices
    Given I am connected to the gateway
    When I request the device list
    Then I should receive a JSON array
    And each device should have id, name, type, reachable, state

  Scenario: Device contains light
    Given a device with type "light"
    Then it should have lightList property

  Scenario: Device contains plug
    Given a device with type "plug"
    Then it should have plugList property

  Scenario: Device state includes on/off
    Given a device with on_off capability
    Then its state should contain "on" boolean

  Scenario: Device state includes brightness
    Given a device with brightness capability
    Then its state should contain "brightness" number

  Scenario: Device is reachable
    Given a reachable device
    When I query its status
    Then reachable should be true

  Scenario: Device is not reachable
    Given an unreachable device
    When I query its status
    Then reachable should be false