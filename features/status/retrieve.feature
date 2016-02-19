Feature: Retrieving Status

  Scenario: Retrieve status without authentication
     Given we are anonymous
      when we get status
      then commissaire will deny access

  Scenario: Retrieve status with authentication
     Given we have a valid username and password
      when we get status
      then commissaire will allow access
      and commissaire will return status