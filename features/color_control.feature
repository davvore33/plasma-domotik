Feature: Color and Color Temperature Control
  As a user
  I want to adjust the color and color temperature of my lights
  So that I can set the right ambiance

  Background:
    Given the Node Adapter is running on port 8765
    And I am connected to the gateway

  # --- Color Temperature ---

  Scenario: Set color temperature to warm
    Given a white-spectrum light exists with id "65545"
    And the device supports color_temp
    When I set color temperature to 100
    Then the response should contain "success": true

  Scenario: Set color temperature to cool
    Given a white-spectrum light exists with id "65545"
    And the device supports color_temp
    When I set color temperature to 0
    Then the response should contain "success": true

  Scenario: Color temperature is clamped to valid range
    Given a white-spectrum light exists with id "65545"
    And the device supports color_temp
    When I set color temperature to 150
    Then the response should contain "success": true
    And the applied value should be 100

  Scenario: Color temperature requires device id
    When I send color_temp command without id
    Then the response should contain error "Missing id or value parameter"

  Scenario: Color temperature requires value
    Given a valid device id
    When I send color_temp command without value
    Then the response should contain error "Missing id or value parameter"

  Scenario: White-spectrum bulb exposes color_temp capability but not color
    Given a white-spectrum light exists
    When I request the device list
    Then the device capabilities should include "color_temp"
    And the device capabilities should not include "color"

  # --- Hue / Color ---

  Scenario: Set hue to red
    Given a color light exists with id "65546"
    And the device supports color
    When I set color hue to 0 with saturation 100
    Then the response should contain "success": true

  Scenario: Set hue to green
    Given a color light exists with id "65546"
    And the device supports color
    When I set color hue to 120 with saturation 100
    Then the response should contain "success": true

  Scenario: Hue is clamped to 0-360
    Given a color light exists with id "65546"
    And the device supports color
    When I set color hue to 400 with saturation 100
    Then the response should contain "success": true
    And the applied hue should be 360

  Scenario: Color requires device id
    When I send color command without id
    Then the response should contain error "Missing id or hue parameter"

  Scenario: Color requires hue
    Given a valid device id
    When I send color command without hue
    Then the response should contain error "Missing id or hue parameter"

  Scenario: Color bulb exposes color capability but not color_temp
    Given a color light exists
    When I request the device list
    Then the device capabilities should include "color"
    And the device capabilities should not include "color_temp"

  Scenario: Color state includes hue and saturation
    Given a color light exists with id "65546"
    And I set color hue to 180 with saturation 100
    When I request the device list
    Then the device state should include hue 180
    And the device state should include saturation 100
