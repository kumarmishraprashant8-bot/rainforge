Feature: Quick Assessment
  As a user
  I want to run a quick RWH assessment
  So that I can get an estimate of rainwater harvesting potential

  Background:
    Given the RainForge API is running
    And I have a valid authentication token

  Scenario: Calculate annual yield for a concrete roof in Delhi
    Given I have the following assessment parameters:
      | parameter      | value      |
      | lat            | 28.6139    |
      | lng            | 77.2090    |
      | roof_area_sqm  | 250        |
      | roof_material  | concrete   |
      | city           | Delhi      |
      | state          | Delhi      |
      | people         | 5          |
    When I call POST /api/assessments/quick
    Then the response status code should be 200
    And the response should contain "annual_yield_l"
    # Annual yield = 250 sqm × 790.5 mm × 0.85 = 167,981 L (approx)
    And the annual_yield_l should be between 150000 and 200000

  Scenario: Quick assessment returns tank recommendation
    Given I have a roof area of 200 sqm with metal material
    And my location is Mumbai, Maharashtra
    When I run a quick assessment
    Then I should receive a tank recommendation in liters
    And the reliability percentage should be greater than 0

  Scenario: Quick assessment includes subsidy information
    Given I am in Karnataka state
    And I have a roof area of 300 sqm
    When I run a quick assessment
    Then the response should contain subsidy information
    And the subsidy_percent should be greater than 0

  Scenario: Quick assessment with polygon GeoJSON
    Given I have a polygon GeoJSON for my roof
    When I call POST /api/assessments/quick with the polygon
    Then the roof area should be calculated from the polygon
    And I should receive a valid assessment result


Feature: Complete Assessment (Async)
  As a government user
  I want to run a complete multi-scenario assessment
  So that I can compare different tank sizing options

  Scenario: Complete assessment returns job ID
    Given I have valid assessment parameters
    When I call POST /api/assessments/complete
    Then the response should contain a job_id
    And the job status should be "pending" or "processing"

  Scenario: Complete assessment generates PDF with BoM
    Given I have submitted a complete assessment
    And the job has completed successfully
    When I request the PDF report
    Then the PDF should contain a Bill of Materials table
    And the PDF should contain subsidy calculation for my state


Feature: Bulk Upload Processing
  As an administrator
  I want to upload a CSV with multiple sites
  So that I can process assessments for many locations at once

  Scenario: Upload sample_bulk.csv with 100 rows
    Given I have the sample_bulk.csv file with 100 rows
    When I call POST /api/bulk/upload with the CSV
    Then I should receive a job_id
    And the rows_total should be 100

  Scenario: Bulk processing validates and processes rows
    Given a bulk job is processing
    When the job completes
    Then rows_processed should be greater than 85
    And rows_failed should be less than 15
    # Expected failures: duplicates, invalid roof_area, missing required fields

  Scenario: Bulk processing produces output ZIP
    Given a bulk job has completed successfully
    When I request the output ZIP
    Then the ZIP should contain individual PDFs for successful rows
    And the ZIP should contain an error report for failed rows


Feature: Photo Verification
  As a verifier
  I want to verify installation photos with GPS and AI
  So that I can ensure installations are legitimate

  Background:
    Given a project exists at lat 28.6139 and lng 77.2090

  Scenario: Verification photo with correct GPS is auto-verified
    Given I have a photo with EXIF GPS at lat 28.6140 and lng 77.2091
    # GPS is within 50m of project location
    And the AI confidence for tank_present is 0.92
    When I submit the verification
    Then the verification status should be "verified"
    And the audit log should contain the photo hash signature

  Scenario: Verification photo with GPS mismatch is flagged
    Given I have a photo with EXIF GPS at lat 19.0760 and lng 72.8777
    # GPS is in Mumbai, not Delhi
    When I submit the verification for a Delhi project
    Then the verification status should be "flagged"
    And the reason should include "location mismatch"

  Scenario: Verification photo with low AI confidence needs review
    Given I have a photo with EXIF GPS within 50m of project
    But the AI confidence for tank_present is 0.65
    When I submit the verification
    Then the verification status should be "pending_review"

  Scenario: Verification creates immutable audit entry
    Given I submit a valid verification
    Then an audit_log entry should be created
    And the entry should contain data_hash
    And the entry should contain a signature
    And the signature should be verifiable with the server key


Feature: Sensor Monitoring
  As a system
  I want to ingest sensor data
  So that I can display tank levels and predict capture

  Scenario: Sensor simulator posts 24 hours of data
    Given the sensor simulator is configured for 24 hours
    And the interval is 5 minutes
    When I run the sensor simulator
    Then 288 data points should be posted to the API
    And each data point should contain level_percent

  Scenario: Monitoring dashboard updates with sensor data
    Given sensor data has been ingested for the last 24 hours
    When I view the monitoring dashboard
    Then I should see the 24-hour trend chart
    And the tank level should not show "NaN%"
    And the predicted days until empty should be calculated

  Scenario: Predictive capture uses weather forecast
    Given I have a project with location data
    When I request a 7-day capture prediction
    Then I should receive daily predictions
    And each prediction should include rainfall_mm and capture_l


Feature: Marketplace Allocation
  As an administrator
  I want to allocate installers to jobs
  So that I can optimize for price, SLA, and rating

  Scenario: Run allocation with default weights
    Given I have a job with 5 projects
    And there are 10 available installers
    When I call POST /api/marketplace/run-allocation with default weights
    Then I should receive ranked installers for each project
    And each installer should have a score breakdown

  Scenario: Custom weights affect allocation ranking
    Given I have a job with projects
    And the weights are:
      | weight   | value |
      | price    | 0.1   |
      | sla      | 0.5   |
      | distance | 0.1   |
      | rating   | 0.3   |
    When I run allocation
    Then installers with better SLA should rank higher
    And the score_breakdown should reflect the weights


Feature: API Security
  As a security auditor
  I want to verify API endpoints are secured
  So that only authorized users can access data

  Scenario: Unauthenticated request is rejected
    Given I do not have an authentication token
    When I call GET /api/project/1
    Then the response status code should be 401
    And the response should contain "Not authenticated"

  Scenario: Sensor endpoint requires API key
    Given I am posting sensor data
    But I do not have a valid API key
    When I call POST /api/monitoring/sensor
    Then the response status code should be 403

  Scenario: Rate limiting is enforced
    Given I am making requests to /api/assessments/quick
    When I make 100 requests in 1 minute
    Then some requests should return status code 429
    And the response should contain "Rate limit exceeded"
