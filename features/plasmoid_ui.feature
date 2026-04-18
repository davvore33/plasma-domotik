Feature: Plasmoid UI
  As a Plasma user
  I want to see and control my devices in a widget
  So that I can manage them from the desktop

  Background:
    Given the Plasmoid is installed
    And the Node Adapter is running on port 8765

  Scenario: Plasmoid loads successfully
    When I add the "Plasma Domotik" widget to the panel
    Then it should display without errors

  Scenario: Plasmoid shows connection status
    Given I am connected to the gateway
    Then I should see "X devices" in status
    And the status should be green

  Scenario: Plasmoid shows devices
    Given devices exist
    When the widget loads
    Then I should see a list of devices

  Scenario: Device shows name and state
    Given a device "Bed side" exists
    When I view the device list
    Then I should see "Bed side" label

  Scenario: Device shows on/off state
    Given a device that is turned on
    When I view the device
    Then I should see "On" label

  Scenario: Device shows off state
    Given a device that is turned off
    When I view the device
    Then I should see "Off" label

  Scenario: Toggle switch for device
    Given a device is displayed
    When I click the toggle switch
    Then the power command should be sent

  Scenario: Toggle switch sends opposite state when device is on
    Given a reachable device that is currently on
    When the toggle is activated
    Then a power command with state "false" should be sent to the adapter
    And the response should contain "success": true

  Scenario: Toggle switch sends opposite state when device is off
    Given a reachable device that is currently off
    When the toggle is activated
    Then a power command with state "true" should be sent to the adapter
    And the response should contain "success": true

  Scenario: State refreshes correctly after external device change
    Given a reachable device that is currently on
    When an external source turns the device off
    And I refresh the device list
    Then the device should show "on": false

  Scenario: Device not reachable indicator
    Given an unreachable device
    When I view the device
    Then its icon should be dimmed (opacity 0.4)

  Scenario: Toggle disabled for unreachable device
    Given an unreachable device
    When I view the toggle switch
    Then the switch should be disabled

  Scenario: Refresh button works
    Given I click the refresh button
    Then the device list should be refreshed

  Scenario: Status shows loading during refresh
    When I click refresh
    Then status should show "Loading..."

  Scenario: Status shows gateway unreachable
    Given gateway is not connected
    When I view the widget
    Then status should show "Gateway unreachable"