Feature: Multi-Agent Executive Orchestration
  Scenario: Security check blocks unauthorized viewer access
    Given the user has the role "Viewer"
    When they run an investigation with question "Why did revenue drop in May?"
    Then the security check blocks the request with reason "unauthorized_access"

  Scenario: Executive orchestrator executes parallel analysis
    Given the user has the role "Executive"
    When they run an investigation with question "Why did revenue drop in May?"
    Then the orchestrator runs parallel revenue, customer, and risk diagnostics
    And the report includes an evaluation score
