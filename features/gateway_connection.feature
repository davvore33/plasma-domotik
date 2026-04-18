Feature: Gateway Connection
  As a user
  I want to connect to the TRÅDFRI gateway
  So that I can manage my devices

  Background:
    Given the Node Adapter is running on port 8765

  Scenario: Connect to gateway with valid credentials
    Given gateway at 192.168.1.116
    And valid security code
    When I send connect request
    Then I should receive "connected": true
    And I should receive identity
    And I should receive psk

  Scenario: Connect with invalid security code
    Given gateway at 192.168.1.116
    And invalid security code "WRONG"
    When I send connect request
    Then I should receive "connected": false

  Scenario: Connect requires host parameter
    When I send connect request without host
    Then the response should contain error "Missing host parameter"

  Scenario: Connect requires security code
    Given gateway at 192.168.1.116
    When I send connect request without security code
    Then the response should contain error "Missing securityCode parameter"

  Scenario: Connection is cached
    Given I have successfully connected once
    When I request connect again
    Then it should use cached credentials

  Scenario: Connection loses gateway
    Given I was connected to gateway
    When gateway becomes unavailable
    Then connection status should be false